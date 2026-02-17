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
    if not backup_file_path.exists():
        print(f"Creating backup at {backup_file_path}")
        if tech_file_path.exists():
             shutil.copy(tech_file_path, backup_file_path)
        else:
             print("Error: Original Technologies.csv not found to backup!")
             return
    else:
        # If backup exists, use it to restore clean state
        # This prevents accumulating constraints if you run script multiple times
        print("Restoring clean state from backup...")
        shutil.copy(backup_file_path, tech_file_path)

    # 2. Load the data
    df = pd.read_csv(tech_file_path, index_col=0)
    print(f"Loaded {len(df)} technologies.")

    # 2b. Ensure necessary columns exist (this was the missing piece!)
    # The model supports these params, but the CSV might be minimal.
    required_cols = ['f_min', 'f_max', 'fmin_perc', 'fmax_perc']
    for col in required_cols:
        if col not in df.columns:
            print(f"  [+] Adding missing column: {col}")
            # Initialize with non-constraining default values
            if 'min' in col:
                df[col] = 0.0
            elif 'max' in col and 'perc' in col:
                df[col] = 1.0 # Default max percentage is 100%
            elif 'max' in col:
                df[col] = 100000.0 # Default max capacity is high

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
        # Force Wood/Biomass
        'IND_BOILER_WOOD': {'f_min': 5.0, 'fmin_perc': 0.4},
        'DHN_COGEN_WOOD':  {'f_min': 2.5, 'fmin_perc': 0.3},
        # Force Coal
        'DHN_COGEN_COAL':  {'f_min': 0.5, 'fmin_perc': 0.3},
        'DHN_BOILER_COAL': {'f_min': 0.5, 'fmin_perc': 0.1},
        'IND_BOILER_COAL': {'f_min': 0.5, 'fmin_perc': 0.1},
        # Limit Gas/Oil to historical low shares
        'IND_BOILER_GAS':  {'fmax_perc': 0.2}, 
        'DHN_COGEN_GAS':   {'fmax_perc': 0.2},
        'DHN_BOILER_OIL':  {'fmax_perc': 0.1},
        'IND_BOILER_OIL':  {'f_min': 0.0},

        # --- TRANSPORT: PASSENGER CARS ---
        # Share: ~55% Gasoline, ~40% Diesel, <1% EV/Hybrid
        'CAR_GASOLINE':  {'fmin_perc': 0.55, 'fmax_perc': 0.65},
        'CAR_DIESEL':    {'fmin_perc': 0.30, 'fmax_perc': 0.40},
        'CAR_BEV':       {'fmax_perc': 0.01}, 
        'CAR_PHEV':      {'fmax_perc': 0.01},
        'CAR_HEV':       {'fmax_perc': 0.05},
        'CAR_FUEL_CELL': {'f_max': 0, 'fmax_perc': 0.0},
        'CAR_METHANOL':  {'f_max': 0},
        
        # --- TRANSPORT: TRUCKS ---
        # Share: >90% Diesel
        'TRUCK_DIESEL': {'fmin_perc': 0.90, 'fmax_perc': 1.0},
        'TRUCK_NG':     {'fmax_perc': 0.05},
        'TRUCK_ELEC':   {'f_max': 0},
        'TRUCK_FUEL_CELL': {'f_max': 0},
        
        # --- TRANSPORT: BUSES ---
        # Share: >90% Diesel
        'BUS_COACH_DIESEL': {'fmin_perc': 0.90},
        'BUS_COACH_FC_HYBRIDH2': {'f_max': 0},

        # --- TRANSPORT: SHIPPING (INTERNATIONAL) ---
        # Demand ~149,000 Mtkm -> ~17 GW equivalent capacity
        # Force Diesel/HFO (Oil)
        'CARGO_LFO': {'f_min': 15.0, 'fmin_perc': 0.95}, 
        'CARGO_LNG': {'fmax_perc': 0.05},
        'CARGO_METHANOL': {'f_max': 0},
        'CARGO_AMMONIA':  {'f_max': 0},
        
        # --- TRANSPORT: DOMESTIC BOAT ---
        'BOAT_FREIGHT_DIESEL': {'fmin_perc': 0.95},
        'BOAT_FREIGHT_NG':     {'fmax_perc': 0.05},
        'BOAT_FREIGHT_METHANOL': {'f_max': 0},
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
