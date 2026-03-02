import pandas as pd
import os
import shutil
from pathlib import Path
import sys

# Paths
# Adjust the path to match your environment
workspace_root = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")
tech_file_path = workspace_root / "Data/2017/FI/Technologies.csv"
backup_file_path = workspace_root / "Data/2017/FI/Technologies_REF.csv"
ref_indep_file = workspace_root / "Data/2017/02_REF_REGION/Technologies.csv" # Additional source if needed

def run_calib():
    print(f"Target file: {tech_file_path}")
    
    # 1. Ensure backup exists (Golden Copy)
    # Check if backup exists and is valid (not minimal/corrupted)
    backup_valid = False
    if backup_file_path.exists():
        if backup_file_path.stat().st_size > 2000: # Assuming minimal file is < 2KB
            backup_valid = True
        else:
            print("Backup file seems minimal or corrupted. Re-creating from reference.")
    
    if not backup_valid:
        print(f"Creating backup at {backup_file_path} from {ref_indep_file}")
        if ref_indep_file.exists():
             shutil.copy(ref_indep_file, backup_file_path)
        else:
             print("Error: Reference Technologies.csv not found to backup!")
             return
    else:
        # If backup exists, use it to restore clean state
        # This prevents accumulating constraints if you run script multiple times
        print("Restoring clean state from backup...")
        shutil.copy(backup_file_path, tech_file_path)

    # 2. Load the data
    # Fix: Use 'Technologies param' as index, not implicit column 0 (Category)
    # If the file has 'Category' as first column, index_col=0 would make it the index.
    # We want 'Technologies param' (usually 3rd or 4th column) as index.
    print("Reading CSV...")
    try:
        # Try reading with 'Technologies param' as index
        df = pd.read_csv(tech_file_path, index_col='Technologies param')
        # Clean index whitespace immediately
        df.index = df.index.str.strip()
        
        # Remove metadata/unit row if present
        if 'Name (in model and documents)' in df.index:
            df.drop('Name (in model and documents)', inplace=True)
            
        # Force numeric columns to be float
        cols_to_ignore = ['Category', 'Subcategory', 'Technologies name', 'Comment']
        for col in df.columns:
            if col not in cols_to_ignore:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    except ValueError:
        # Fallback if 'Technologies param' column is not found (e.g. slight name diff)
        print("Warning: 'Technologies param' not found as index. Trying default read.")
        df = pd.read_csv(tech_file_path)
        if 'Technologies param' in df.columns:
            df.set_index('Technologies param', inplace=True)
        elif 'Technologies name' in df.columns:
            df.set_index('Technologies name', inplace=True)
            print("Warning: Using 'Technologies name' as index.")
        else:
             # Last resort: use column 0 but warn
             print("Warning: Could not identify index column. Using first column.")
             df = pd.read_csv(tech_file_path, index_col=0)
    
    # NEW: Strip whitespace from index and columns to prevent duplicates
    # This fixes issues where 'CCGT_AMMONIA ' != 'CCGT_AMMONIA'
    if df.index.dtype == 'object':
         df.index = df.index.str.strip()
    df.columns = df.columns.str.strip()
    
    print(f"Loaded {len(df)} technologies.")

    # 2b. Ensure necessary columns exist
    # The model supports these params, but the CSV might be minimal.
    required_cols = ['f_min', 'f_max', 'fmin_perc', 'fmax_perc', 'c_inv', 'c_maint', 'lifetime']
    for col in required_cols:
        if col not in df.columns:
            print(f"  [+] Adding missing column: {col}")
            df[col] = 0.0
            if 'perc' in col:
                df[col] = 1.0 # Default max percentage is 100%
            elif 'max' in col:
                df[col] = 100000.0 # Default max capacity is high
        else:
             # Force float if int to avoid dtypes warnings
             if pd.api.types.is_integer_dtype(df[col]):
                 df[col] = df[col].astype(float)

    # 3. Define Constraints map
    # Using fmin_perc/fmax_perc effectively forces market shares
    # Using f_max=0 blocks future technologies
    
    constraints = {
        # --- ELECTRICITY GENERATION ---
        'NUCLEAR':      {'f_min': 2.5, 'f_max': 2.8, 'fmin_perc': 0.0, 'fmax_perc': 1.0},
        'WIND_ONSHORE': {'f_min': 2.0, 'f_max': 2.1},
        'HYDRO_DAM':    {'f_min': 1.1, 'f_max': 1.3}, 
        'HYDRO_RIVER':  {'f_min': 1.9, 'f_max': 2.1},
        'COAL_US':      {'f_min': 3.5, 'f_max': 4.5}, # Coal condensation
        'PV_ROOFTOP':   {'f_min': 0.02, 'f_max': 2.0}, # Very small in 2017
        'PV_UTILITY':   {'f_max': 1.0},
        
        # --- HEAT GENERATION ---
        # 2017 was dominated by Wood/Biomass and Coal/Peat, with some Gas/Oil.
        # Switch District Heating (DHN) to fmin_perc (Market Share) to force production.
        'DHN_COGEN_WOOD':  {'fmin_perc': 0.02}, 
        'DHN_BOILER_WOOD': {'fmin_perc': 0.02}, 
        'DHN_COGEN_COAL':  {'fmin_perc': 0.02}, 
        'DHN_BOILER_OIL':  {'fmin_perc': 0.02}, 

        # Industry: Mix of Capacity and Share
        'IND_COGEN_WOOD':  {'fmin_perc': 0.1, 'fmax_perc': 1.0}, 
        'IND_BOILER_WOOD': {'fmin_perc': 0.1}, 
        'IND_BOILER_OIL':  {'fmin_perc': 0.1}, 
        'IND_BOILER_COAL': {'fmin_perc': 0.1}, 
        'IND_DIRECT_ELEC': {'fmax_perc': 0.1}, 
        
        # Limit Gas to historical low shares
        'IND_BOILER_GAS':  {'fmax_perc': 0.2}, 
        'DHN_COGEN_GAS':   {'fmax_perc': 0.2},

        # --- TRANSPORT: PASSENGER CARS ---
        # User request: Force CAR_GASOLINE + CAR_DIESEL to near 100%
        # CAR_GASOLINE: fmin_perc = 0.58
        # CAR_DIESEL: fmin_perc = 0.38
        'CAR_GASOLINE':  {'fmin_perc': 0.58, 'fmax_perc': 0.65},
        'CAR_DIESEL':    {'fmin_perc': 0.38, 'fmax_perc': 0.40},
        'CAR_BEV':       {'fmax_perc': 0.01}, 
        'CAR_PHEV':      {'fmax_perc': 0.01},
        'CAR_HEV':       {'fmax_perc': 0.05},
        'CAR_FUEL_CELL': {'f_max': 0, 'fmax_perc': 0.0},
        'CAR_METHANOL':  {'f_max': 0},
        
        # --- TRANSPORT: TRUCKS ---
        # User request: Force TRUCK_DIESEL to 0.95
        'TRUCK_DIESEL': {'fmin_perc': 0.95, 'fmax_perc': 1.0},
        'TRUCK_NG':     {'fmax_perc': 0.05},
        'TRUCK_ELEC':   {'f_max': 0,'fmin_perc': 0.95},
        'TRUCK_FUEL_CELL': {'f_max': 0,'fmin_perc': 0.95},
        
        # --- TRANSPORT: BUSES ---
        # User request: Force BUS_COACH_DIESEL to 0.95
        'BUS_COACH_DIESEL': {'fmin_perc': 0.5},
        'BUS_COACH_FC_HYBRIDH2': {'f_max': 0},

        # --- SYNTHETIC FUELS (PtL) ---
        # In 2017, synthetic fuels were negligible. Force them to 0 to ensure Fossil Oil is used.
        'H2_TO_GASOLINE': {'f_max': 0},
        'H2_TO_DIESEL':   {'f_max': 0},
        'H2_TO_LFO':      {'f_max': 0},
        'H2_TO_JET_FUEL': {'f_max': 0},
        'POWER_TO_GASOLINE': {'f_max': 0},
        'POWER_TO_DIESEL':   {'f_max': 0},
        'POWER_TO_LFO':      {'f_max': 0},
        'POWER_TO_JET_FUEL': {'f_max': 0},
        'BIOMASS_TO_GASOLINE': {'f_max': 0}, # If exists
        'BIOMASS_TO_DIESEL':   {'f_max': 0}, # If exists
        'SYN_METHANATION':     {'f_max': 0}, # Force Methanation to 0


        # Prevent Ammonia/H2 power cycles from exploding
        'CCGT_AMMONIA': {'f_max': 0},
        'AMMONIA_TO_H2': {'f_max': 0},
        'DEC_ADVCOGEN_H2': {'f_max': 0},
        'DEC_ADVCOGEN_GAS': {'f_max': 0}, 

        # --- TRANSPORT: SHIPPING (INTERNATIONAL) ---
        # Demand ~149,000 Mtkm -> ~17 GW equivalent capacity
        # Force Diesel/HFO (Oil)
        'CARGO_LFO': {'f_min': 15.0, 'fmin_perc': 0.95}, 
        'CARGO_LNG': {'fmax_perc': 0.05},
        'CARGO_METHANOL': {'f_max': 0},
        'CARGO_AMMONIA':  {'f_max': 0},
        
        # --- TRANSPORT: DOMESTIC BOAT ---
        'BOAT_FREIGHT_DIESEL': {'fmin_perc': 0.6},
        'BOAT_FREIGHT_NG':     {'fmax_perc': 0.05},
        'BOAT_FREIGHT_METHANOL': {'f_max': 0},
        
        # --- STORAGE ---
        # Constrain DAM_STORAGE because HYDRO_DAM is constrained (avoids Infinity in linear interpolation)
        'DAM_STORAGE': {'f_max': 20000},
        'PT_COLLECTOR': {'f_max': 0},
        'ST_COLLECTOR': {'f_max': 0},
    }

    # 4. Apply Constraints
    print(f"Applying constraints for {len(constraints)} technologies...")
    
    # We need to know the columns to add new rows properly
    cols = df.columns.tolist()
    
    for tech, params in constraints.items():
        # A. Check existence
        if tech not in df.index:
            print(f"  [+] Adding/Overriding missing tech: {tech}")
            # Add with wide open defaults first
            new_row = {c: (0.0 if 'min' in c else 1 if 'perc' in c else 100000.0) for c in cols}
            if 'fmax_perc' in new_row: new_row['fmax_perc'] = 1.0
                
            df.loc[tech] = pd.Series(new_row)
            
        # B. Update values
        for param, value in params.items():
            if param in df.columns:
                df.at[tech, param] = value
            else:
                print(f"  [!] Column '{param}' missing. Cannot set for {tech}")

    # 5. Save
    print(f"Saving modified file to {tech_file_path}")
    df.to_csv(tech_file_path)
    print("Calibration setup complete.")

if __name__ == "__main__":
    run_calib()
