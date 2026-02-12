"""
run_calibration_FI.py
Usage: python scripts/run_calibration_FI.py
"""
import pandas as pd
import os
import shutil
import sys
from pathlib import Path

# --- CONFIGURATION ---
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.append(str(WORKSPACE_ROOT))

try:
    from esmc import Esmc
except ImportError:
    print("CRITICAL: content of esmc module could not be imported. Check PYTHONPATH.")
    sys.exit(1)

# File Paths
YEAR = 2017
REGION = 'FI'
DATA_DIR = WORKSPACE_ROOT / "Data" / str(YEAR) / REGION
TECH_FILE = DATA_DIR / "Technologies.csv"
RES_FILE = DATA_DIR / "Resources.csv"
BACKUP_TECH = DATA_DIR / "Technologies_REF.csv"
BACKUP_RES = DATA_DIR / "Resources_REF.csv"

def restore_backup_if_exists(original: Path, backup: Path):
    if backup.exists():
        print(f"Restoring clean backup from {backup.name}...")
        shutil.copy(backup, original)
    else:
        print(f"Creating backup {backup.name}...")
        shutil.copy(original, backup)

def get_constraints():
    tech_constraints = {
        'CAR_BEV': {'f_max': 0},
        'CAR_PHEV': {'f_max': 0},
        'CAR_FUEL_CELL': {'f_max': 0}, 
        'CAR_METHANOL': {'f_max': 0},
        'BUS_COACH_FC_HYBRIDH2': {'f_max': 0},
        'TRUCK_FUEL_CELL': {'f_max': 0},
        'TRUCK_ELEC': {'f_max': 0},
        'CCGT_AMMONIA': {'f_max': 0},
        'COAL_IGCC': {'f_max': 0},
        'SMR': {'f_max': 0},
        'DEC_ADVCOGEN_GAS': {'f_max': 0},
        'DEC_ADVCOGEN_H2': {'f_max': 0},
        'DEC_THHP_GAS': {'f_max': 0},
        'DEC_THHP_GAS_COLD': {'f_max': 0},
        'DEC_ELEC_COLD': {'f_max': 0},
        'CAR_HEV': {'f_max': 100000.0},
        'TRUCK_NG': {'f_max': 100000.0},
        'INDUSTRY_CCS': {'f_max': 0},
        'ATM_CCS': {'f_max': 0},
        'NUCLEAR': {'f_min': 2.7, 'f_max': 2.835},
        'WIND_ONSHORE': {'f_min': 2.0, 'f_max': 2.1},
        'WIND_OFFSHORE': {'f_max': 0.1},
        'HYDRO_DAM': {'f_max': 2.2},
        'HYDRO_RIVER': {'f_min': 1.0, 'f_max': 1.0},
        'COAL_US': {'f_min': 0.5, 'f_max': 2.0}, 
        'IND_COGEN_WOOD': {'f_min': 2.0, 'f_max': 50.0},
        'DHN_COGEN_WOOD': {'f_min': 1.0, 'f_max': 50.0},
        'BIOMASS_TO_POWER': {'f_min': 0.2, 'f_max': 50.0}, 
        'IND_BOILER_WOOD': {'f_min': 6.0, 'f_max': 50.0},
        'DHN_BOILER_WOOD': {'f_min': 3.0, 'f_max': 50.0},
        'IND_BOILER_GAS': {'f_max': 4.0},
        'IND_COGEN_GAS': {'f_max': 1.0},
        'DHN_BOILER_GAS': {'f_max': 2.0},
        'DHN_COGEN_GAS': {'f_max': 2.5},
        'DEC_BOILER_GAS': {'f_max': 0.5},
        'DEC_BOILER_BIOWASTE': {'f_max': 1.0},
        'IND_BOILER_BIOWASTE': {'f_max': 1.0},
        'IND_BOILER_OIL': {'f_max': 1.0},
        'DHN_BOILER_OIL': {'f_max': 1.0},
        'IND_BOILER_COAL': {'f_min': 4.0, 'f_max': 50.0, 'fmin_perc': 0.30}, 
        'DHN_COGEN_COAL': {'f_min': 2.5, 'f_max': 50.0, 'fmin_perc': 0.20},  
        'DHN_BOILER_COAL': {'f_min': 0.0}, 
        'HVAC_LINE': {'f_max': 3.5},
        'HVDC_SUBSEA': {'f_max': 1.5},
    }

    res_constraints = {
        'GAS':      {'avail_local': 0.0, 'c_op_local': 0.20, 'avail_exterior': 25000.0}, 
        'COAL':     {'avail_local': 0.0, 'c_op_local': 0.015, 'avail_exterior': 60000.0}, 
        'OIL':      {'avail_local': 0.0, 'c_op_local': 0.05,  'avail_exterior': 50000.0}, 
        'GASOLINE': {'avail_local': 0.0, 'c_op_local': 0.06,  'avail_exterior': 30000.0}, 
        'DIESEL':   {'avail_local': 0.0, 'c_op_local': 0.05,  'avail_exterior': 40000.0}, 
        'LFO':      {'avail_local': 0.0, 'c_op_local': 0.05,  'avail_exterior': 50000.0},
        'JET_FUEL': {'avail_local': 0.0, 'c_op_local': 0.05,  'avail_exterior': 15000.0}, 
        'WOOD':     {'avail_local': 110805.66, 'c_op_local': 0.022, 'avail_exterior': 10000.0},
        'URANIUM':  {'avail_local': 0.0, 'c_op_local': 0.005, 'avail_exterior': 1000000.0}, 
        'GAS_RE': {'avail_local': 0.0, 'c_op_local': 0.0, 'avail_exterior': 0.001},
        'LFO_RE': {'avail_local': 0.0, 'c_op_local': 0.0, 'avail_exterior': 0.001},
        'DIESEL_RE': {'avail_local': 0.0, 'c_op_local': 0.0, 'avail_exterior': 0.001},
        'GASOLINE_RE': {'avail_local': 0.0, 'c_op_local': 0.0, 'avail_exterior': 0.001},
        'JET_FUEL_RE': {'avail_local': 0.0, 'c_op_local': 0.0, 'avail_exterior': 0.001},
        'H2_RE': {'avail_local': 0.0, 'c_op_local': 0.0, 'avail_exterior': 0.001},
        'AMMONIA_RE': {'avail_local': 0.0, 'c_op_local': 0.0, 'avail_exterior': 0.001},
        'METHANOL_RE': {'avail_local': 0.0, 'c_op_local': 0.0, 'avail_exterior': 0.001},
    }
    return tech_constraints, res_constraints

def main():
    print(f"--- STARTING 2017 FINLAND CALIBRATION RUN [{YEAR}] ---")
    
    restore_backup_if_exists(TECH_FILE, BACKUP_TECH)
    restore_backup_if_exists(RES_FILE, BACKUP_RES)
    
    try:
        df_tech = pd.read_csv(TECH_FILE, index_col=0)
        df_tech.index = df_tech.index.str.strip()
        df_res = pd.read_csv(RES_FILE, index_col=0)
    except FileNotFoundError as e:
        print(f"CRITICAL: Input file not found. {e}")
        return

    tech_bounds, res_updates = get_constraints()
    
    if "fmin_perc" not in df_tech.columns:
        print(" Adding 'fmin_perc' column to Technologies...")
        df_tech['fmin_perc'] = 0.0

    print(" Applying Technology Constraints...")
    for tech, bounds in tech_bounds.items():
        if tech not in df_tech.index:
            print(f"  Warning: Tech {tech} not found in CSV. Adding it.")
            df_tech.loc[tech] = [0.0] * len(df_tech.columns)
            
        for param, value in bounds.items():
            if param in df_tech.columns:
                if param == 'f_max' and value > 3000.0:
                     value = 50.0
                df_tech.loc[tech, param] = value
                
    if 'f_max' in df_tech.columns:
        df_tech.loc[df_tech['f_max'] > 50.0, 'f_max'] = 50.0
        
    if 'f_max' in df_tech.columns and 'f_min' in df_tech.columns:
        mask_min = (df_tech['f_min'] > 0)
        required_max_all = df_tech['f_min'] * 1.05
        mask_tight = mask_min & (df_tech['f_max'] < required_max_all)
        
        if mask_tight.any():
            print(f"  Adjusting {mask_tight.sum()} technology bounds to ensure >5% gap...")
            df_tech.loc[mask_tight, 'f_max'] = required_max_all[mask_tight].round(4)
            
        for tech, bounds in tech_bounds.items():
             if tech in df_tech.index and 'f_max' in bounds and bounds['f_max'] <= 0.0001:
                 df_tech.loc[tech, 'f_max'] = 0.0

    print(" Applying Resource Constraints...")
    for res, data in res_updates.items():
        if res not in df_res.index:
             print(f"  Adding missing Resource {res}...")
             df_res.loc[res] = [data['avail_local'], data['c_op_local'], data['avail_exterior']]
        else:
             df_res.loc[res, 'avail_exterior'] = data['avail_exterior']
             df_res.loc[res, 'c_op_local'] = data['c_op_local']
    
    df_tech.to_csv(TECH_FILE)
    df_res.to_csv(RES_FILE)
    print(" Input CSVs updated successfully.")

    case_study = f'calib_{YEAR}_finland'
    config = {
        'case_study': case_study,
        'comment': 'Finland 2017 Calibration',
        'regions_names': [REGION],
        'gwp_limit_overall': None,
        're_share_primary': None,  # ADDED BACK
        'f_perc': False,
        'year': YEAR
    }

    try:
        print(" Initializing ESMC Model...")
        my_model = Esmc(config, nbr_td=12)
        my_model.read_data_indep()
        
        res_key = 'Resources_indep'
        if res_key in my_model.data_indep:
             if 'GAS' in my_model.data_indep[res_key].index:
                  my_model.data_indep[res_key].loc['GAS', 'c_op_exterior'] = 0.20
             if 'COAL' in my_model.data_indep[res_key].index:
                  my_model.data_indep[res_key].loc['COAL', 'c_op_exterior'] = 0.03

        techs_to_degrade = [
             ('IND_BOILER_WOOD', 'WOOD', 1.15),
             ('DHN_COGEN_WOOD', 'WOOD', 1.20), 
             ('IND_COGEN_WOOD', 'WOOD', 1.20),
             ('IND_BOILER_COAL', 'COAL', 1.15),
             ('DHN_COGEN_COAL', 'COAL', 1.20),
             ('IND_BOILER_GAS', 'GAS', 1.10),
             ('DHN_COGEN_GAS', 'GAS', 1.10)
        ]
        
        if 'Layers_in_out' in my_model.data_indep:
             for tech, res, factor in techs_to_degrade:
                 if tech in my_model.data_indep['Layers_in_out'].index:
                     current_val = my_model.data_indep['Layers_in_out'].loc[tech, res]
                     my_model.data_indep['Layers_in_out'].loc[tech, res] = current_val * factor
        
        my_model.init_regions()
        my_model.init_ta(algo='read') 
        
        print(" Patching Region Data (In-Memory)...")
        for r_name, region in my_model.regions.items():
            if 'Technologies' in region.data:
                df_t = region.data['Technologies']
                if 'f_max' in df_t.columns:
                    mask_huge = df_t['f_max'] > 5000.0
                    df_t.loc[mask_huge, 'f_max'] = 50.0
                
                if 'f_max' in df_t.columns and 'f_min' in df_t.columns:
                     mask_min = (df_t['f_min'] > 0)
                     req_max = df_t['f_min'] * 1.05
                     mask_tight = mask_min & (df_t['f_max'] < req_max)
                     if mask_tight.any():
                         df_t.loc[mask_tight, 'f_max'] = req_max[mask_tight].round(4)
                         
                     for tech, bounds in tech_bounds.items():
                         if tech in df_t.index and 'f_max' in bounds and bounds['f_max'] <= 0.0001:
                             df_t.loc[tech, 'f_max'] = 0.0

        my_model.print_td_data()
        my_model.print_data(indep=True)
        my_model.set_esom()
        my_model.solve_esom()
        
        print(" Saving Results...")
        my_model.get_year_results(save_hourly=['Resources', 'Exchanges', 'Assets', 'Storage', 'Curt'])
        my_model.prints_esom(solve_info=True)
        print(" Calibration Run Complete.")
        
    except Exception as e:
        print(f"CRITICAL ERROR during execution: {e}")

if __name__ == "__main__":
    main()
