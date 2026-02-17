import pandas as pd
import os
from pathlib import Path

# Paths
workspace_root = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")
excel_path = workspace_root / "Data/exogenous_data/Finland_MASTER_Calibration.xlsx"
res_path = workspace_root / "case_studies/FI/calib_2017_finland_v4_fixed/outputs/Resources.csv"

# Historical Data (Approx 2017)
history_data = {
    'ELECTRICITY': 20.0,  # Net Input
    'GAS': 25.0,
    'COAL': 35.0,
    'WOOD': 95.0,
    'OIL_PRODUCTS': 100.0,
    'NUCLEAR': 65.0,      # Generation ~21 TWh, Fuel Input much higher ~65
    'HYDRO': 14.0,        # Generation
    'WIND': 5.0           # Generation
}

def get_resource_val(df, res_name):
    if res_name in df['Resources'].values:
        row = df[df['Resources'] == res_name]
        return row['R_year_local'].values[0] + row['R_year_exterior'].values[0]
    return 0.0

try:
    print(f"Reading results from {res_path}...")
    res_df = pd.read_csv(res_path)
    
    # Calculate Model Results (Convert GWh to TWh)
    model_res = {}
    model_res['ELECTRICITY'] = get_resource_val(res_df, 'ELECTRICITY') / 1000.0
    model_res['GAS'] = get_resource_val(res_df, 'GAS') / 1000.0
    model_res['COAL'] = get_resource_val(res_df, 'COAL') / 1000.0
    model_res['WOOD'] = (get_resource_val(res_df, 'WOOD') + get_resource_val(res_df, 'BIOMASS_RESIDUES') + get_resource_val(res_df, 'WET_BIOMASS')) / 1000.0
    
    oil_list = ['GASOLINE', 'DIESEL', 'LFO', 'JET_FUEL']
    model_res['OIL_PRODUCTS'] = sum([get_resource_val(res_df, r) for r in oil_list]) / 1000.0
    
    model_res['NUCLEAR'] = get_resource_val(res_df, 'URANIUM') / 1000.0
    model_res['HYDRO'] = get_resource_val(res_df, 'RES_HYDRO') / 1000.0
    model_res['WIND'] = get_resource_val(res_df, 'RES_WIND') / 1000.0
    
    # Create DataFrame
    summary_df = pd.DataFrame([history_data, model_res], index=['History 2017 (Ref)', 'Model Run v4'])
    summary_df = summary_df.T
    summary_df['Diff'] = summary_df['Model Run v4'] - summary_df['History 2017 (Ref)']
    summary_df['Diff %'] = (summary_df['Diff'] / summary_df['History 2017 (Ref)']) * 100
    
    print("\nCalibration Summary:")
    print(summary_df)
    
    # Append to Excel
    print(f"\nUpdating Excel: {excel_path}")
    if os.path.exists(excel_path):
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            summary_df.to_excel(writer, sheet_name='Run_Feb16_AutoCalib')
        print("Update Successful.")
    else:
        print("Excel file not found!")
        
except Exception as e:
    print(f"Error: {e}")
