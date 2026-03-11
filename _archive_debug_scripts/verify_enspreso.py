import pandas as pd
import numpy as np
import os

# Mappings
# Trying different combinations to match target ~110,805 for WOOD
groupings = {
    'Attempt_Factor1000': {
        'WOOD': ['MINBIOWOO', 'MINBIOWOOa', 'MINBIOFRSR1', 'MINBIOFRSR1a', 'MINBIOWOOW1', 'MINBIOWOOW1a'], 
        'WET_BIOMASS': ['MINBIOSLU1', 'MINBIOMUN1'], 
        'BIOMASS_RESIDUES': ['MINBIOAGRW1'],
        'BIOWASTE': ['MINBIOMUN1'],
        'ENERGY_CROPS_2': ['MINBIOCRP11', 'MINBIOCRP21', 'MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a'],
        'Factor': 1000
    },
    'Attempt_Factor277_TJ_to_GWh': {
        'WOOD': ['MINBIOWOO', 'MINBIOWOOa', 'MINBIOFRSR1', 'MINBIOFRSR1a', 'MINBIOWOOW1', 'MINBIOWOOW1a'], 
        'WET_BIOMASS': ['MINBIOSLU1', 'MINBIOMUN1'], 
        'BIOMASS_RESIDUES': ['MINBIOAGRW1'],
        'BIOWASTE': ['MINBIOMUN1'],
        'ENERGY_CROPS_2': ['MINBIOCRP11', 'MINBIOCRP21', 'MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a'],
        'Factor': 277.77 # If ENSPRESO is PJ * 1000 = TJ. TJ -> GWh is / 3.6 = * 0.277
    },
     'Attempt_Factor_1': {
        'WOOD': ['MINBIOWOO', 'MINBIOWOOa', 'MINBIOFRSR1', 'MINBIOFRSR1a', 'MINBIOWOOW1', 'MINBIOWOOW1a'], 
        'WET_BIOMASS': ['MINBIOSLU1', 'MINBIOMUN1'], 
        'BIOMASS_RESIDUES': ['MINBIOAGRW1'],
        'BIOWASTE': ['MINBIOMUN1'],
        'ENERGY_CROPS_2': ['MINBIOCRP11', 'MINBIOCRP21', 'MINBIOCRP31', 'MINBIOCRP41', 'MINBIOCRP41a'],
        'Factor': 1
    }
}

target_file = 'Data/2035/FI/Resources.csv'
enspreso_file = 'Data/exogenous_data/ENSPRESO/ENSPRESO_BIOMASS.xlsx'

def main():
    print("--- Reading Target ---")
    if not os.path.exists(target_file):
        print(f"Target file missing: {target_file}")
        return
        
    try:
        # Try tab
        df_t = pd.read_csv(target_file, sep='\t', comment='#', index_col=0)
        if 'avail_local' not in df_t.columns:
             # Try semicolon
             df_t = pd.read_csv(target_file, sep=';', comment='#', index_col=0)
        
        if 'avail_local' not in df_t.columns:
             print("avail_local column not found")
             return
    except Exception as e:
        print(f"Error reading target: {e}")
        return

    df_t.index = df_t.index.str.strip()
    
    targets = {}
    for r in ['WOOD', 'WET_BIOMASS', 'BIOMASS_RESIDUES', 'BIOWASTE', 'ENERGY_CROPS_2']:
        if r in df_t.index:
            targets[r] = df_t.loc[r]['avail_local']
        else:
            targets[r] = 0
            
    print("Targets:")
    for k, v in targets.items():
        print(f"  {k}: {v:.2f}")

    print("\n--- Reading ENSPRESO ---")
    if not os.path.exists(enspreso_file):
        print(f"ENSPRESO file missing: {enspreso_file}")
        return
    
    try:
        xl = pd.ExcelFile(enspreso_file)
        sheet = 'ENER - NUTS0 EnergyCom'
        if sheet not in xl.sheet_names:
            sheet = xl.sheet_names[0]
        df_ens = pd.read_excel(enspreso_file, sheet_name=sheet)
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return
        
    # Filter FI
    df_fi = df_ens[df_ens['NUTS0'] == 'FI']
    
    # Check Units if available
    if 'units' in df_ens.columns:
        print(f"Units in ENSPRESO: {df_ens['units'].unique()}")
    
    # Pivot
    df_piv = df_fi[df_fi['Year'].isin([2030, 2040])].pivot_table(
        index=['Scenario', 'Energy Commodity'], columns='Year', values='Value', aggfunc='sum'
    )
    
    if 2030 not in df_piv.columns or 2040 not in df_piv.columns:
        print(f"Missing years. Cols: {df_piv.columns}")
        return
        
    df_piv['2035'] = (df_piv[2030] + df_piv[2040]) / 2
    
    print("\n--- Raw Values 2035 (Average 2030/2040) ---")
    raw_sums = df_piv['2035'].groupby('Energy Commodity').sum()
    print(raw_sums)

    print("\n--- Calculation & Comparison ---")
    
    scenarios = df_piv.index.get_level_values(0).unique()
    
    results = []
    
    for scen in scenarios:
        try:
            scen_data = df_piv.xs(scen, level=0)
        except:
            continue
            
        for map_name, maps in groupings.items():
            row_vals = {'Scenario': scen, 'Mapping': map_name}
            factor = maps.get('Factor', 1)
            
            for res_name in ['WOOD', 'WET_BIOMASS', 'BIOMASS_RESIDUES', 'BIOWASTE', 'ENERGY_CROPS_2']:
                codes = maps.get(res_name, [])
                val = 0
                for c in codes:
                    if c in scen_data.index:
                        val += scen_data.loc[c, '2035']
                row_vals[res_name] = val * factor
            
            # Error calc
            err = 0
            count = 0
            for k in ['WOOD', 'WET_BIOMASS', 'BIOMASS_RESIDUES']:
                t = targets.get(k, 0)
                c = row_vals.get(k, 0)
                if t > 100:
                    err += abs((c-t)/t)
                    count += 1
            avg_err = err/count if count else 0
            row_vals['Avg_Error'] = avg_err
            
            results.append(row_vals)

    # Sort results
    results.sort(key=lambda x: x['Avg_Error'])
    
    for res in results[:5]: # Top 5
        print(f"\nScenario: {res['Scenario']}, Mapping: {res['Mapping']}")
        print(f"Avg Error: {res['Avg_Error']:.2%}")
        for k in ['WOOD', 'WET_BIOMASS', 'BIOMASS_RESIDUES', 'BIOWASTE', 'ENERGY_CROPS_2']:
            t = targets.get(k, 0)
            c = res.get(k, 0)
            diff = (c-t)/t*100 if t>0 else 0
            print(f"  {k}: Target={t:.0f}, Calc={c:.0f}, Diff={diff:.1f}%")

if __name__ == "__main__":
    main()
