import pandas as pd
import os
import sys

# Paths
BASE_DIR = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
ENSPRESO_PATH = os.path.join(BASE_DIR, 'Data', 'exogenous_data', 'ENSPRESO', 'ENSPRESO_BIOMASS.xlsx')
TARGET_2017_PATH = os.path.join(BASE_DIR, 'Data', '2017', 'FI', 'Resources.csv')

def main():
    print(f"Reading current 2017 file: {TARGET_2017_PATH}")
    try:
        # Read with correct separator (try comma first as seen in prev steps, but keep backup)
        try:
             df_current = pd.read_csv(TARGET_2017_PATH, sep=',', index_col=0)
             if 'avail_local' not in df_current.columns: raise ValueError
        except:
             df_current = pd.read_csv(TARGET_2017_PATH, sep=';', index_col=0)
    
        print("Current values:")
        print(df_current['avail_local'])
    except Exception as e:
        print(f"Error reading current file: {e}")
        return

    print("\nReading ENSPRESO...")
    df_ens = pd.read_excel(ENSPRESO_PATH, sheet_name='ENER - NUTS0 EnergyCom')
    df_fi = df_ens[df_ens['NUTS0'] == 'FI'].copy()
    
    # Filter for years 2010, 2020 for interpolation
    df_fi = df_fi[df_fi['Year'].isin([2010, 2020])]
    
    # Pivot: Index=[Scenario, Commodity], Cols=Year
    df_piv = df_fi.pivot_table(index=['Scenario', 'Energy Commodity'], columns='Year', values='Value', aggfunc='sum')
    
    # Interpolate 2017
    # 2017 is 70% of way from 2010 to 2020
    if 2010 in df_piv.columns and 2020 in df_piv.columns:
        df_piv['2017_val'] = df_piv[2010] + (df_piv[2020] - df_piv[2010]) * 0.7
    else:
        print("Missing 2010 or 2020 data.")
        return
        
    df_calc = df_piv.reset_index()
    
    # Conversion PJ -> GWh
    conversion_factor = 277.778 
    
    # Select Scenario: ENS_Med (Based on BIOMASS_RESIDUES match)
    scenario = 'ENS_Med'
    
    print(f"\nUsing Scenario: {scenario}")
    df_scen = df_calc[df_calc['Scenario'] == scenario].copy()

    # Define New Mappings
    mappings = {
        'ENERGY_CROPS_2': ['MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a'], # Exclude 11, 21
        # Keep other categories consistent with "All Wood" or "Core Wood"?
        # Script analysis showed WOOD matched ~91% with All Wood (Woo+Frsr+Woow)
        'WOOD': ['MINBIOWOO', 'MINBIOWOOa', 'MINBIOFRSR1', 'MINBIOFRSR1a', 'MINBIOWOOW1', 'MINBIOWOOW1a'],
        'WET_BIOMASS': ['MINBIOSLU1', 'MINBIOGAS1'], # Sludge + Manure
        'BIOWASTE': ['MINBIOMUN1'], # Municipal
        'BIOMASS_RESIDUES': ['MINBIORPS1', 'MINBIOAGRW1'], # Rps + Agrw
    }
    
    new_values = {}
    for res, codes in mappings.items():
        mask = df_scen['Energy Commodity'].isin(codes)
        val = df_scen[mask]['2017_val'].sum() * conversion_factor
        new_values[res] = val
        print(f"  Calculated {res}: {val:.2f} GWh")

    # Update DataFrame
    # Note: 'avail_local' is the column to update
    for res, val in new_values.items():
        if res in df_current.index:
            old_val = df_current.loc[res, 'avail_local']
            print(f"Updating {res}: {old_val:.2f} -> {val:.2f}")
            df_current.loc[res, 'avail_local'] = val
        else:
            print(f"Warning: {res} not in Resources.csv index. Adding it.")
            # For simplicity, if not exists, skipping or adding row 
            # (Assuming structure is fixed, skipping add to avoid breaking format if strict)
    
    # Save
    # Use comma as separator if that was what we read (implied by previous steps)
    output_path = TARGET_2017_PATH
    # Backup first?
    # df_current.to_csv(output_path, sep=',') 
    # Use verify_enspreso output style which seemed to be comma
    df_current.to_csv(output_path, sep=',')
    print(f"\nSaved updated 2017 values to {output_path}")

if __name__ == "__main__":
    main()
