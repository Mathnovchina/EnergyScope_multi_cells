import pandas as pd
import os
import sys

# Paths
BASE_DIR = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
ENSPRESO_PATH = os.path.join(BASE_DIR, 'Data', 'exogenous_data', 'ENSPRESO', 'ENSPRESO_BIOMASS.xlsx')
TARGET_2035_PATH = os.path.join(BASE_DIR, 'Data', '2035', 'FI', 'Resources.csv')

def load_resources_csv(filepath):
    try:
        # Try comma first
        try:
             df = pd.read_csv(filepath, sep=',', index_col=0)
             if 'avail_local' in df.columns: return df['avail_local'].to_dict()
        except: pass
        
        # Try semicolon
        try:
             df = pd.read_csv(filepath, sep=';', index_col=0)
             if 'avail_local' in df.columns: return df['avail_local'].to_dict()
             if 'avail' in df.columns: return df['avail'].to_dict()
        except: pass
        
        return {}
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return {}

def main():
    print("--- Loading Target Data (2035) ---")
    target_data_2035 = load_resources_csv(TARGET_2035_PATH)
    if not target_data_2035:
        print("Could not load target 2035 data. Exiting.")
        return

    # Relevant categories
    categories = {
        'ENERGY_CROPS_2': target_data_2035.get('ENERGY_CROPS_2', 0),
        'WOOD': target_data_2035.get('WOOD', 0),
        'WET_BIOMASS': target_data_2035.get('WET_BIOMASS', 0),
        'BIOWASTE': target_data_2035.get('BIOWASTE', 0),
        'BIOMASS_RESIDUES': target_data_2035.get('BIOMASS_RESIDUES', 0)
    }
    
    print("Target values (2035) from Resources.csv:")
    for cat, val in categories.items():
        print(f"  {cat}: {val:.2f} GWh")

    print("\n--- Loading ENSPRESO Data ---")
    try:
        df_ens = pd.read_excel(ENSPRESO_PATH, sheet_name='ENER - NUTS0 EnergyCom')
    except Exception as e:
        print(f"Error loading ENSPRESO Excel: {e}")
        return

    # Filter for Finland
    # Note: Column is NUTS0
    df_fi = df_ens[df_ens['NUTS0'] == 'FI'].copy()

    # Get years 2030 and 2040 for 2035 interpolation
    df_fi = df_fi[df_fi['Year'].isin([2030, 2040])]
    
    # Pivot to get years as columns: index=[Scenario, Energy Commodity], columns=Year, values=Value
    if df_fi.empty:
        print("No data found for FI in years 2030, 2040.")
        return
        
    df_pivoted = df_fi.pivot_table(index=['Scenario', 'Energy Commodity'], columns='Year', values='Value', aggfunc='sum')
    
    # Interpolate 2035
    if 2030 in df_pivoted.columns and 2040 in df_pivoted.columns:
        df_pivoted['2035_val'] = df_pivoted[2030] + (df_pivoted[2040] - df_pivoted[2030]) * 0.5
    else:
        print("Years 2030 or 2040 missing in pivot.")
        print(df_pivoted.columns)
        return

    # Reset index to make filtering easier
    df_calc = df_pivoted.reset_index()

    # Conversion factor: PJ -> GWh
    conversion_factor = 277.778 

    # Hypotheses definitions
    # Note: Using set for faster lookup, but list is fine for small count
    hypotheses = {
        'ENERGY_CROPS_2': {
            'All Crops': ['MINBIOCRP11', 'MINBIOCRP21', 'MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a'],
            '2nd Gen (31+41+41a)': ['MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a'],
            'Strict 2nd Gen (31+41)': ['MINBIOCRP31', 'MINBIOCRP41'],
            'Only Grassy (41+41a)': ['MINBIOCRP41', 'MINBIOCRP41a'],
            'Only Ligno (31)': ['MINBIOCRP31'],
            'Only 1st Gen (11+21)': ['MINBIOCRP11', 'MINBIOCRP21'],
        },
        'WOOD': {
            'All Wood (Woo+Frsr+Woow)': ['MINBIOWOO', 'MINBIOWOOa', 'MINBIOFRSR1', 'MINBIOFRSR1a', 'MINBIOWOOW1', 'MINBIOWOOW1a'], 
            'Core Wood (Woo+Frsr)': ['MINBIOWOO', 'MINBIOWOOa', 'MINBIOFRSR1', 'MINBIOFRSR1a'],
        },
        'WET_BIOMASS': {
            'Sludge + Manure': ['MINBIOSLU1', 'MINBIOGAS1'],
            'Just Manure': ['MINBIOGAS1'],
        },
        'BIOWASTE': {
            'Municipal (Mun)': ['MINBIOMUN1'],
        },
        'BIOMASS_RESIDUES': {
            'Agri Res (Rps)': ['MINBIORPS1'],
            'Agri Res (Rps + Agrw)': ['MINBIORPS1', 'MINBIOAGRW1'],
        }
    }

    unique_scenarios = df_calc['Scenario'].unique()
    print(f"\nScenarios found: {unique_scenarios}")

    print("\n--- Testing Hypotheses ---")

    for res, strategies in hypotheses.items():
        target_val = categories.get(res, 0)
        print(f"\nResource: {res} (Target: {target_val:.2f})")
        
        for strat_name, codes in strategies.items():
            codes_in_this_strategy = codes # Just renaming for clarity
            
            # Scenario loop
            for scen in unique_scenarios:
                mask_scen = df_calc['Scenario'] == scen
                mask_codes = df_calc['Energy Commodity'].isin(codes_in_this_strategy)
                
                # Check which codes are actually found
                found_codes = df_calc[mask_scen & mask_codes]['Energy Commodity'].unique()
                
                val = df_calc[mask_codes & mask_scen]['2035_val'].sum() * conversion_factor
                
                # Check for match (within 1% or fixed amount)
                diff = abs(val - target_val)
                match_str = ""
                if diff < 1.0: match_str = " <--- EXACT MATCH"
                elif diff < 100.0: match_str = " <--- CLOSE MATCH"
                elif target_val > 0 and diff/target_val < 0.01: match_str = " <--- 1% MATCH"
                
                print(f"  [{strat_name}] ({scen}): {val:.2f}{match_str}")
        
    print("\nDone.")

if __name__ == "__main__":
    main()
