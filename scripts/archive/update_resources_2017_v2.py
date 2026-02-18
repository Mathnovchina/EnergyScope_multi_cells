import pandas as pd
import os
import shutil
import numpy as np

# Paths
BASE_DIR = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
ENSPRESO_PATH = os.path.join(BASE_DIR, 'Data', 'exogenous_data', 'ENSPRESO', 'ENSPRESO_BIOMASS.xlsx')
TARGET_2017_PATH = os.path.join(BASE_DIR, 'Data', '2017', 'FI', 'Resources.csv')

# Conversions
PJ_TO_GWH = 277.778 

# Mappings (Scenario: ENS_Med)
# Note: Using set for faster lookup, but list is fine for small count
MAPPINGS = {
    'WOOD': ['MINBIOWOO', 'MINBIOFRSR1', 'MINBIOWOOW1'],
    'WET_BIOMASS': ['MINBIOGAS1', 'MINBIOSLU1'],
    'ENERGY_CROPS_2': ['MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a'],
    'BIOWASTE': ['MINBIOMUN1'],
    'BIOMASS_RESIDUES': ['MINBIORPS1', 'MINBIOAGRW1'],
}

def load_resources_csv(filepath):
    try:
        # Try comma first
        try:
             df = pd.read_csv(filepath, sep=',', index_col=0)
             if 'avail_local' in df.columns: return df
        except: pass
        
        # Try semicolon
        try:
             df = pd.read_csv(filepath, sep=';', index_col=0)
             if 'avail_local' in df.columns: return df
             if 'avail' in df.columns: return df
        except: pass
        
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def main():
    print("--- Loading ENSPRESO Data ---")
    try:
        # Check if file starts with 'MIN' as used in the mapping, or if there is a prefix issue. 
        # Previous script implies codes are like 'MINBIOWOO'.
        df_ens = pd.read_excel(ENSPRESO_PATH, sheet_name='ENER - NUTS0 EnergyCom')
    except Exception as e:
        print(f"Error loading ENSPRESO Excel: {e}")
        return

    # Filter for Finland and Scenario ENS_Med
    df_fi = df_ens[(df_ens['NUTS0'] == 'FI') & (df_ens['Scenario'] == 'ENS_Med')].copy()

    # Get years 2010 and 2020 for 2017 interpolation
    years_needed = [2010, 2020]
    df_fi = df_fi[df_fi['Year'].isin(years_needed)]
    
    if df_fi.empty:
        print("No data found for FI in ENS_Med for years 2010, 2020.")
        return

    # Pivot
    df_pivoted = df_fi.pivot_table(index='Energy Commodity', columns='Year', values='Value', aggfunc='sum')

    # Check if we have both years
    if 2010 not in df_pivoted.columns or 2020 not in df_pivoted.columns:
        print("Missing 2010 or 2020 data for interpolation.")
        print(df_pivoted.columns)
        return

    # Interpolate 2017
    # Linear interpolation: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    # 2017 is 70% of the way from 2010 to 2020
    fraction = (2017 - 2010) / (2020 - 2010)
    df_pivoted['2017_val'] = df_pivoted[2010] + (df_pivoted[2020] - df_pivoted[2010]) * fraction
    
    # Calculate new values
    new_values = {}
    print("\n--- Calculated Values for 2017 (ENS_Med) ---")
    
    for resource, codes in MAPPINGS.items():
        # Sum the values for the codes in the list
        # We need to be careful if a code is missing in the dataframe (treat as 0)
        valid_codes = [c for c in codes if c in df_pivoted.index]
        missing_codes = [c for c in codes if c not in df_pivoted.index]
        
        if missing_codes:
            print(f"Warning: Missing codes for {resource}: {missing_codes}")
            
        val_pj = df_pivoted.loc[valid_codes, '2017_val'].sum()
        val_gwh = val_pj * PJ_TO_GWH
        new_values[resource] = val_gwh
        
        print(f"{resource}: {val_gwh:.2f} GWh (Codes: {valid_codes})")

    # Update Resources.csv
    print("\n--- Updating Resources.csv ---")
    df_target = load_resources_csv(TARGET_2017_PATH)
    if df_target is None:
        print("Could not load target Resources.csv")
        return

    # Create backup
    backup_path = TARGET_2017_PATH + ".bak_v2"
    shutil.copy(TARGET_2017_PATH, backup_path)
    print(f"Backup created at {backup_path}")

    # Determine column name
    col_name = 'avail_local' if 'avail_local' in df_target.columns else 'avail'
    
    changes_log = []

    for resource, new_val in new_values.items():
        if resource in df_target.index:
            old_val = df_target.loc[resource, col_name]
            df_target.loc[resource, col_name] = new_val
            changes_log.append(f"Updated {resource}: {old_val:.2f} -> {new_val:.2f}")
        else:
            print(f"Warning: Resource {resource} not found in Resources.csv. Skipping.")

    # Save
    # We need to preserve the format (separator)
    # The load function handles both, but let's see which one it was.
    # Usually it's semicolon for EnergyScope but CSV implies comma. 
    # Let's check the first line of the file to be sure, or just use the one that worked.
    # Since I don't want to re-read, I'll assume semicolon if that's the standard, 
    # but the previous script tried comma first.
    # Let's try to infer from the file content.
    
    with open(TARGET_2017_PATH, 'r') as f:
        first_line = f.readline()
        sep = ';' if ';' in first_line else ','

    df_target.to_csv(TARGET_2017_PATH, sep=sep)
    print("File saved.")
    
    print("\n--- Summary of Changes ---")
    for log in changes_log:
        print(log)
    print("Crucial addition: Included MINBIOAGRW1 in BIOMASS_RESIDUES.")

if __name__ == "__main__":
    main()
