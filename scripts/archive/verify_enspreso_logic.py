import pandas as pd
import numpy as np
import os
import sys

# Define mapping using CODES
# Based on commodity codes seen:
# ['MINBIOAGRW1', 'MINBIOCRP11', 'MINBIOCRP21', 'MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a', 
#  'MINBIOFRSR1', 'MINBIOFRSR1a', 'MINBIOGAS1', 'MINBIOMUN1', 'MINBIORPS1', 'MINBIOSLU1', 
#  'MINBIOWOO', 'MINBIOWOOa', 'MINBIOWOOW1', 'MINBIOWOOW1a']

groupings = {
    'Attempt_1': {
        'WOOD': ['MINBIOWOO', 'MINBIOWOOa', 'MINBIOFRSR1', 'MINBIOFRSR1a', 'MINBIOWOOW1', 'MINBIOWOOW1a'], 
        'WET_BIOMASS': ['MINBIOMUN1', 'MINBIOSLU1', 'MINBIOGAS1'], # Maybe not GAS? Maybe Manure is missing?
        'BIOMASS_RESIDUES': ['MINBIOAGRW1'], 
        'BIOWASTE': ['MINBIOMUN1', 'MINBIOSLU1'], # Overlap with WET?
        'ENERGY_CROPS_2': ['MINBIOCRP11', 'MINBIOCRP21', 'MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a']
    },
    'Attempt_2_NoGas': {
        'WOOD': ['MINBIOWOO', 'MINBIOWOOa', 'MINBIOFRSR1', 'MINBIOFRSR1a', 'MINBIOWOOW1', 'MINBIOWOOW1a'], 
        'WET_BIOMASS': ['MINBIOSLU1'], # Maybe Manure? Where is Manure? MINBIORPS1?
        'BIOMASS_RESIDUES': ['MINBIOAGRW1'],
        'BIOWASTE': ['MINBIOMUN1'],
        'ENERGY_CROPS_2': ['MINBIOCRP11', 'MINBIOCRP21', 'MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a']
    },
    'Attempt_3_OnlyWoo': {
        'WOOD': ['MINBIOWOO', 'MINBIOWOOa'], 
        'WET_BIOMASS': ['MINBIOSLU1', 'MINBIOMUN1'],
        'BIOMASS_RESIDUES': ['MINBIOFRSR1', 'MINBIOFRSR1a'], # Maybe residues are forestry?
        'BIOWASTE': [],
        'ENERGY_CROPS_2': []
    }
}
# MINBIORPS1 -> Maybe "Rapeseed"? Or "Residues Primary Solid"?
# MINBIOGAS1 -> Biogas?

# Paths
base_dir = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
target_file = os.path.join(base_dir, 'Data', '2035', 'FI', 'Resources.csv')
enspreso_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'ENSPRESO', 'ENSPRESO_BIOMASS.xlsx')

def read_target_values():
    if not os.path.exists(target_file):
        print(f"Target file not found: {target_file}")
        return None, None
    try:
        df = pd.read_csv(target_file, sep=';', comment='#', index_col=0)
        if 'avail_local' not in df.columns:
             df = pd.read_csv(target_file, sep='\t', comment='#', index_col=0)
    except Exception as e:
        print(f"Error reading target file: {e}")
        return None, None

    df.index = df.index.str.strip()
    target_resources = ['WOOD', 'WET_BIOMASS', 'ENERGY_CROPS_2', 'BIOWASTE', 'BIOMASS_RESIDUES']
    values = {}
    for res in target_resources:
        if res in df.index:
            values[res] = df.loc[res].get('avail_local', 0)
        else:
            values[res] = 0
            
    return values, df

def calculate_enspreso_values():
    if not os.path.exists(enspreso_file):
        print(f"ENSPRESO file not found")
        return pd.DataFrame()
        
    print(f"Reading {enspreso_file}...")
    try:
        df_ens = pd.read_excel(enspreso_file, sheet_name='ENER - NUTS0 EnergyCom')
    except Exception as e:
        print(f"Error reading ENSPRESO file: {e}")
        return pd.DataFrame()

    df_fi = df_ens[df_ens['NUTS0'] == 'FI'].copy()
    
    # Filter for years 2030 and 2040
    df_fi = df_fi[df_fi['Year'].isin([2030, 2040])]
    
    # Pivot
    pivot = df_fi.pivot_table(index=['Scenario', 'Energy Commodity'], columns='Year', values='Value', aggfunc='sum')
    
    if 2030 not in pivot.columns or 2040 not in pivot.columns:
        print("Missing 2030 or 2040")
        return pd.DataFrame()
        
    pivot['Value_2035'] = (pivot[2030] + pivot[2040]) / 2
    
    results = []
    
    for scenario in pivot.index.get_level_values('Scenario').unique():
        scen_data = pivot.xs(scenario, level='Scenario')
        
        # Also print raw values for each commodity to see what adds up
        print(f"\nScenario: {scenario}")
        print(scen_data['Value_2035'].head())
        
        for map_name, maps in groupings.items():
            row = {'Scenario': scenario, 'Mapping': map_name}
            
            for res_name, codes in maps.items():
                val = 0
                for code in codes:
                    if code in scen_data.index:
                        val += scen_data.loc[code, 'Value_2035']
                
                # Try Factor 1000
                row[res_name] = val * 1000
            
            results.append(row)
            
    return pd.DataFrame(results)

def main():
    print("--- Reading Target Values (2035/FI) ---")
    target_vals, _ = read_target_values()
    if target_vals:
         for k, v in target_vals.items():
             print(f"{k}: {v}")

    print("\n--- Calculating ENSPRESO Interpolated Values (2035) ---")
    df_calc = calculate_enspreso_values()
    
    if df_calc.empty:
        print("No calculations produced.")
        return

    print("\n--- Comparison ---")
    metrics = []
    
    for idx, row in df_calc.iterrows():
        errs = []
        for res in ['WOOD', 'WET_BIOMASS', 'BIOMASS_RESIDUES']:
            t = target_vals.get(res, 0)
            c = row.get(res, 0)
            if t > 100:
                errs.append(abs((c - t)/t))
        
        avg_err = sum(errs)/len(errs) if errs else float('inf')
        
        res_row = {
            'Scenario': row['Scenario'],
            'Mapping': row['Mapping'],
            'Avg_Error_%': round(avg_err * 100, 2)
        }
        
        for res in ['WOOD', 'WET_BIOMASS', 'BIOMASS_RESIDUES', 'BIOWASTE', 'ENERGY_CROPS_2']:
             t = target_vals.get(res, 0)
             c = row.get(res, 0)
             res_row[f'{res}_Diff%'] = round((c - t)/t * 100, 2) if t > 10 else 0
             res_row[f'{res}_C'] = round(c, 0)
             res_row[f'{res}_T'] = round(t, 0)

        metrics.append(res_row)

    df_metrics = pd.DataFrame(metrics)
    df_metrics = df_metrics.sort_values(by='Avg_Error_%')
    
    print("\nBest Match Details:")
    if not df_metrics.empty:
        print(df_metrics.iloc[0])
        
    print("\nAll Scenarios Summary:")
    print(df_metrics[['Scenario', 'Mapping', 'Avg_Error_%', 'WOOD_Diff%', 'WET_BIOMASS_Diff%', 'BIOMASS_RESIDUES_Diff%']].head(10))

if __name__ == "__main__":
    main()
