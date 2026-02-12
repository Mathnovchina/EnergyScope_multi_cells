import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Paths
workspace_root = r"c:/Users/borde/OneDrive/Bureau/model/EnergyScope_multi_cells"
ref_dir = os.path.join(workspace_root, "case_studies/FI/ref_2017_finland/outputs")
calib_dir = os.path.join(workspace_root, "case_studies/FI/calib_2017_finland/outputs")

# Real Data 2017 (TWh)
real_2017 = {
    'Nuclear': 21.6,
    'Hydro': 14.6,
    'Wind': 4.8,
    'Biomass': 11.0, # Elec
    'Coal': 6.0,     # Elec
    'Gas': 4.0,      # Elec
    'Wood_PE': 105.0 # Primary Energy
}

def get_vals(output_dir):
    yb_path = os.path.join(output_dir, "Year_balance.csv")
    res_path = os.path.join(output_dir, "Resources.csv")
    
    vals = {}
    if not os.path.exists(yb_path):
        return None
        
    yb = pd.read_csv(yb_path, index_col=0)
    GWh_to_TWh = 1/1000.0
    
    # Elec Gen
    if 'ELECTRICITY' in yb.columns:
        elec_col = yb['ELECTRICITY']
        vals['Nuclear'] = (elec_col.get('NUCLEAR', 0) + elec_col.get('NUCLEAR_SMR', 0)) * GWh_to_TWh
        vals['Wind'] = (elec_col.get('WIND_ONSHORE', 0) + elec_col.get('WIND_OFFSHORE', 0)) * GWh_to_TWh
        vals['Hydro'] = (elec_col.get('HYDRO_RIVER', 0) + elec_col.get('HYDRO_DAM', 0)) * GWh_to_TWh
        vals['Gas'] = sum([elec_col.get(t, 0) for t in ['CCGT', 'IND_COGEN_GAS', 'DHN_COGEN_GAS']]) * GWh_to_TWh
        vals['Biomass'] = sum([elec_col.get(t, 0) for t in ['IND_COGEN_WOOD', 'DHN_COGEN_WOOD', 'BIOMASS_TO_POWER']]) * GWh_to_TWh
        vals['Coal'] = sum([elec_col.get(t, 0) for t in ['COAL_US', 'DHN_COGEN_COAL']]) * GWh_to_TWh

    # Primary Energy
    if os.path.exists(res_path):
        res = pd.read_csv(res_path, index_col=0)
        def get_res(name):
             if name in res.index:
                 return (res.loc[name, 'R_year_local'] + res.loc[name, 'R_year_exterior'] + res.loc[name, 'R_year_import'] - res.loc[name, 'R_year_export']) * GWh_to_TWh
             return 0.0
        vals['Wood_PE'] = get_res('WOOD') + get_res('WET_BIOMASS') + get_res('BIOWASTE')
        
    return vals

def analyze():
    print("Analyzing Calibration vs Reference...")
    ref_vals = get_vals(ref_dir)
    calib_vals = get_vals(calib_dir)
    
    if not ref_vals:
        print("Reference results missing.")
    if not calib_vals:
        print("Calibration results missing (Run likely failed or running).")
        return

    # Comparison Table
    keys = ['Nuclear', 'Wind', 'Hydro', 'Gas', 'Biomass', 'Wood_PE']
    
    print(f"{'Metric':<15} | {'Real 2017':<10} | {'Ref (Unconst)':<15} | {'Calib (Const)':<15} | {'Diff Ref%':<10} | {'Diff Cal%':<10}")
    print("-" * 90)
    
    for k in keys:
        real = real_2017.get(k, 0)
        ref = ref_vals.get(k, 0)
        cal = calib_vals.get(k, 0)
        
        diff_ref = ((ref - real)/real * 100) if real else 0
        diff_cal = ((cal - real)/real * 100) if real else 0
        
        print(f"{k:<15} | {real:<10.1f} | {ref:<15.1f} | {cal:<15.1f} | {diff_ref:+.1f}%    | {diff_cal:+.1f}%")

    # Plot
    df = pd.DataFrame({
        'Real 2017': [real_2017[k] for k in keys],
        'Reference': [ref_vals.get(k, 0) for k in keys],
        'Calibrated': [calib_vals.get(k, 0) for k in keys]
    }, index=keys)
    
    df.plot(kind='bar', figsize=(10, 6))
    plt.title("Finland 2017: Model Calibration Results")
    plt.ylabel("TWh")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig("calibration_result_plot.png")
    print("\nPlot saved to calibration_result_plot.png")

if __name__ == "__main__":
    analyze()
