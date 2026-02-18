import pandas as pd
import numpy as np
import os
import re

# Define paths
DATA_PATH = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\2017\FI\Demands.csv'
V8_DAT_PATH = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\case_studies\FI\calib_2017_finland_v8_no_coal_us\reg_demands.dat'

def parse_dat_file(filepath):
    if not os.path.exists(filepath):
        print(f'File not found: {filepath}')
        return pd.DataFrame()

    with open(filepath, 'r') as f:
        content = f.read()
    
    match = re.search(r':=\s*(.*?)\s*;', content, re.DOTALL)
    if not match:
        print('Could not find data block in .dat file')
        return pd.DataFrame()
        
    lines = match.group(1).strip().split('\n')
    
    rows = []
    
    for line in lines:
        parts = line.strip().split() 
        if len(parts) >= 6:
            category = parts[1]
            try:
                h = float(parts[2])
                s = float(parts[3])
                i = float(parts[4])
                t = float(parts[5])
                
                rows.append({
                    'parameter name': category,
                    'HOUSEHOLDS': h,
                    'SERVICES': s,
                    'INDUSTRY': i,
                    'TRANSPORTATION': t,
                    'Units': '[GWh]' 
                })
            except ValueError:
                continue

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    for idx, row in df.iterrows():
        cat = row['parameter name']
        if 'MOBILITY' in cat or 'AVIATION' in cat or 'SHIPPING' in cat:
             if 'PASSENGER' in cat or 'AVIATION' in cat:
                 df.at[idx, 'Units'] = '[Mpkm]'
             else:
                 df.at[idx, 'Units'] = '[Mtkm]'
                 
    return df

def analyze_demands(df, label):
    print(f'\nAnalyzing Demands for: {label}')
    if df is None or df.empty:
        print('DataFrame is empty.')
        return 0

    sector_cols = ['HOUSEHOLDS', 'SERVICES', 'INDUSTRY', 'TRANSPORTATION']
    
    print(f'{"Category":<25} {"Sum (Units)":<15} {"Unit":<8} {"Appx TWh (Final)":<20}')
    print('-' * 75)
    
    total_twh = 0
    
    for idx, row in df.iterrows():
        param = row['parameter name']
        val = sum(row[col] for col in sector_cols if col in df.columns and pd.notnull(row[col]))
        unit = row['Units'] if pd.notnull(row['Units']) else '[GWh]'
        
        twh_val = 0
        
        # Simple Logic for Conversion
        if '[GWh]' in unit:
            twh_val = val / 1000.0
        elif 'MOBILITY_PASSENGER' in param:
            # Mpkm -> TWh final energy (Appx 0.35 kWh/pkm check)
            twh_val = val * 0.35 / 1000.0
        elif 'MOBILITY_FREIGHT' in param:
            # Mtkm -> TWh final energy (Appx 0.8 kWh/tkm check)
            twh_val = val * 0.8 / 1000.0
        elif 'AVIATION' in param:
             # Appx 0.4 kWh/pkm
             twh_val = val * 0.4 / 1000.0
        elif 'SHIPPING' in param:
             # Appx 0.1 kWh/tkm
             twh_val = val * 0.1 / 1000.0
        
        print(f'{param:<25} {val:10.2f} {unit:<8} {twh_val:10.2f} TWh')
        total_twh += twh_val

    print('-' * 75)
    print(f'Total Approx Final Energy: {total_twh:.2f} TWh')
    return total_twh

print('--- Current Data (Data/2017/FI/Demands.csv) ---')
try:
    df_current = pd.read_csv(DATA_PATH)
    analyze_demands(df_current, 'Current')
except Exception as e:
    print(f'Error reading current demands: {e}')

print('\n--- v8 Data (case_studies/.../reg_demands.dat) ---')
try:
    df_v8 = parse_dat_file(V8_DAT_PATH)
    analyze_demands(df_v8, 'v8 Old')
except Exception as e:
    print(f'Error reading v8 demands: {e}')

