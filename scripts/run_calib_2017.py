import pandas as pd
import os
import shutil
from pathlib import Path
import sys

# Paths
workspace_root = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")
tech_file = workspace_root / "Data/2017/FI/Technologies.csv"
backup_file = workspace_root / "Data/2017/FI/Technologies_REF.csv"

# Add project root to path for Esmc
sys.path.append(str(workspace_root))
from esmc import Esmc

def run_calib():
    # 1. Helper to update constraints
    print(f"Reading {tech_file}")
    
    # Read existing (3-column format expected: Technologies param, f_min, f_max)
    df = pd.read_csv(tech_file, index_col=0)
    
    # Backup if not exists
    if not os.path.exists(backup_file):
        print(f"Backing up to {backup_file}")
        shutil.copy(tech_file, backup_file)
    else:
        # If backup exists, RESTORE it first to ensure clean slate?
        # Yes, good practice to avoid accumulating constraints.
        print(f"Restoring clean REF from {backup_file}")
        shutil.copy(backup_file, tech_file)
        df = pd.read_csv(tech_file, index_col=0)
    
    # Ensure index is clean
    df.index = df.index.str.strip()

    # 2. Define Constraints (The "Limpens" Method)
    # Units: GW (Power/Heat), Mpkm/h (Transport), Mtonkm/h (Freight)
    
    constraints = {
        # --- UNBLOCK TRANSPORT (ICE Proxies) ---
        'CAR_HEV': {'f_max': 100000.0},
        'CAR_PHEV': {'f_max': 100000.0},
        'TRUCK_NG': {'f_max': 100000.0},
        'TRUCK_METHANOL': {'f_max': 100000.0}, # Allow alternatives if NG limited

        # --- PHASE OUT FUTURE TECHS (f_max=0) ---
        'CAR_BEV': {'f_max': 0},
        # 'CAR_PHEV': {'f_max': 0},
        # 'CAR_HEV': {'f_max': 0}, # Unblock HEV to allow ICE proxy
        'CAR_FUEL_CELL': {'f_max': 0}, 
        'CAR_METHANOL': {'f_max': 0},
        'BUS_COACH_FC_HYBRIDH2': {'f_max': 0},
        'TRUCK_FUEL_CELL': {'f_max': 0},
        'TRUCK_ELEC': {'f_max': 0},
        # 'TRUCK_METHANOL': {'f_max': 0},
        # 'TRUCK_NG': {'f_max': 0}, # Unblock NG Truck to allow transport (ICE Proxy)
        
        # --- SYNTHETIC FUELS / HYDROGEN (Relaxed to allow transport if ICE missing) ---
        # 'H2_ELECTROLYSIS': {'f_max': 0},
        # 'H2_NG': {'f_max': 0}, 
        # 'H2_BIOMASS': {'f_max': 0},
        # 'POWER_TO_GASOLINE': {'f_max': 0},
        # 'POWER_TO_DIESEL': {'f_max': 0},
        # 'BIOMASS_TO_GASOLINE': {'f_max': 0},
        # 'BIOMASS_TO_DIESEL': {'f_max': 0},
        
        # --- FORCE HISTORICAL CAPACITIES (f_min, f_max) ---
        'NUCLEAR': {'f_min': 2.7, 'f_max': 2.8},
        'WIND_ONSHORE': {'f_min': 2.0, 'f_max': 2.1},
        'WIND_OFFSHORE': {'f_max': 0.1},
        'HYDRO_RIVER': {'f_min': 1.9, 'f_max': 2.1},
        'HYDRO_DAM': {'f_min': 1.1, 'f_max': 1.3}, 
        
        # --- FORCE BIOMASS USE ---
        # Real 2017 Biomass: ~105 TWh total.
        # Ind: 40 TWh -> ~5 GW
        # DHN: 20 TWh -> ~2.5 GW
        # Increase mins to force model usage
        'IND_BOILER_WOOD': {'f_min': 5.0}, 
        'DHN_COGEN_WOOD': {'f_min': 2.5},
        'IND_COGEN_WOOD': {'f_min': 1.0}, # Add Cogen wood min

        # --- LIMIT FOSSIL IMPORTS ---
        # Force GAS to max 25 TWh (approx 2.8 GW avg, set 3.5 GW capacity max)
        # Note: Esmc treats GAS as resource 'avail_exterior' if not in Techs.
        # But we must ensure the Technologies consumming gas are limited too.
        'GAS': {'f_max': 3.5},
        'IND_BOILER_GAS': {'f_max': 2.0}, # Constrain Ind Gas Boiler
        
        # --- ENABLE ELECTRICITY IMPORTS ---
        # Real 2017: ~5 GW capacity (Sweden, Estonia, Russia)
        'HVAC_LINE': {'f_max': 3.5},  # Interconnection Sweden/Norway
        'HVDC_SUBSEA': {'f_max': 1.5}, # Estonia/Russia
    }
    
    # 3. Apply Constraints
    print("Applying calibration constraints...")
    for tech, bounds in constraints.items():
        if tech not in df.index:
            # We must assume the tech exists in the Global definitions.
            # Esmc uses this file to OVERRIDE. So we can add any valid tech name.
            # Default values (0, 100000) or similar (NaN?)
            # The CSV has f_min, f_max columns.
            pass
            
        if 'f_min' in bounds:
            if tech not in df.index: df.loc[tech] = [0.0, 100000.0]
            df.loc[tech, 'f_min'] = bounds['f_min']
            
        if 'f_max' in bounds:
            if tech not in df.index: df.loc[tech] = [0.0, 100000.0]
            df.loc[tech, 'f_max'] = bounds['f_max']

    # Save
    print(f"Saving calibrated Tech file to {tech_file}")
    df.to_csv(tech_file)
    
    # 4. Run Model
    case_study = 'calib_2017_finland'
    print(f"Running Case: {case_study}")

    config = {
        'case_study': case_study,
        'comment': 'Finland 2017 Calibration with f_min/f_max constraints',
        'regions_names': ['FI'],
        'gwp_limit_overall': None,
        're_share_primary': None,
        'f_perc': False,
        'year': 2017
    }

    try:
        my_model = Esmc(config, nbr_td=12)
        my_model.read_data_indep()
        my_model.init_regions()
        my_model.init_ta(algo='read') 
        my_model.print_td_data()
        my_model.print_data(indep=True)
        
        print("Solving constrained model...")
        my_model.set_esom()
        try:
            my_model.solve_esom()
        except Exception as e:
            print(f"AMPL Execution Warning/Error: {e}")
            print("Attempting to proceed with result extraction (assuming optimal)...")
        
        my_model.get_year_results(save_hourly=['Resources', 'Exchanges', 'Assets', 'Storage', 'Curt'])
        print("Saving results to CSV...")
        my_model.prints_esom(solve_info=True)
        print(f"Run complete. Check {my_model.cs_dir}")
        
    except Exception as e:
        print(f"Run failed: {e}")
        # Restore backup? Maybe better to leave it for debugging
        # shutil.copy(backup_file, tech_file)

if __name__ == "__main__":
    run_calib()
