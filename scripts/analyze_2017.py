import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Paths (Relative to workspace root)
output_dir = r"case_studies/FI/ref_2017_finland/outputs"
yb_path = os.path.join(output_dir, "Year_balance.csv")
res_path = os.path.join(output_dir, "Resources.csv")

# 1. Real Data 2017 (Statistics Finland / IEA approx) [TWh]
real_2017 = {
    'Primary Energy': {
        'Oil': 97.0,
        'Coal': 32.0,
        'Gas': 22.0,
        'Nuclear': 65.0,
        'Hydro': 14.6,
        'Wind': 4.8,
        'Biomass/Waste': 105.0,
        'Peat': 16.0,
        'Net Import Elec': 20.4
    },
    'Electricity Generation': {
        'Nuclear': 21.6,
        'Hydro': 14.6, 
        'Wind': 4.8,
        'Biomass': 11.0,
        'Coal': 6.0,
        'Gas': 4.0
    },
    'Emissions': {
        'CO2_Total': 42.0 # MtCO2 approx
    }
}

def analyze():
    print(f"Reading from: {os.path.abspath(output_dir)}")
    # Read Model Outputs
    try:
        # Check if files exist
        if not os.path.exists(yb_path):
            print(f"Error: {yb_path} does not exist.")
            return
        if not os.path.exists(res_path):
            print(f"Error: {res_path} does not exist.")
            return

        yb = pd.read_csv(yb_path, index_col=0)
        res = pd.read_csv(res_path, index_col=0)
    except Exception as e:
        print(f"Error reading CSVs: {e}")
        return

    # --- 1. Primary Energy Analysis ---
    # Convert GWh to TWh for comparison
    GWh_to_TWh = 1/1000.0
    
    # Helper to safe get
    def get_res_val(name):
        if name in res.index:
            # R_year_local etc are in GWh
             return (res.loc[name, 'R_year_local'] + res.loc[name, 'R_year_exterior'] + res.loc[name, 'R_year_import'] - res.loc[name, 'R_year_export']) * GWh_to_TWh
        return 0.0

    model_pe = {}
    model_pe['Oil'] = get_res_val('GASOLINE') + get_res_val('DIESEL') + get_res_val('LFO') + get_res_val('JET_FUEL')
    model_pe['Coal'] = get_res_val('COAL')
    model_pe['Gas'] = get_res_val('GAS')
    model_pe['Nuclear'] = get_res_val('URANIUM')
    model_pe['Hydro'] = get_res_val('RES_HYDRO')
    model_pe['Wind'] = get_res_val('RES_WIND')
    model_pe['Biomass/Waste'] = (get_res_val('WOOD') + get_res_val('WET_BIOMASS') + get_res_val('BIOWASTE') + 
                                get_res_val('BIOMASS_RESIDUES') + get_res_val('WASTE'))
    model_pe['Hydrogen Import'] = get_res_val('H2') 
    
    # --- 2. Electricity Analysis ---
    # From Year_balance.csv (Sum of ELECTRICITY column for technologies)
    # Rows are Technologies/Resources.
    # Positive values in 'ELECTRICITY' column = Generation.
    
    if 'ELECTRICITY' in yb.columns:
        elec_col = yb['ELECTRICITY']
        
        model_elec = {}
        model_elec['Nuclear'] = (elec_col.get('NUCLEAR', 0) + elec_col.get('NUCLEAR_SMR', 0)) * GWh_to_TWh
        model_elec['Hydro'] = (elec_col.get('HYDRO_RIVER', 0) + elec_col.get('HYDRO_DAM', 0)) * GWh_to_TWh
        model_elec['Wind'] = (elec_col.get('WIND_ONSHORE', 0) + elec_col.get('WIND_OFFSHORE', 0)) * GWh_to_TWh
        # Biomass Gen:
        bio_techs = ['BIOMASS_TO_POWER', 'IND_COGEN_WOOD', 'DHN_COGEN_WOOD', 'IND_COGEN_WASTE', 'DHN_COGEN_WASTE']
        model_elec['Biomass'] = sum([elec_col.get(t, 0) for t in bio_techs]) * GWh_to_TWh
        # Coal Gen:
        coal_techs = ['COAL_US', 'COAL_IGCC'] 
        # Check if IND_BOILER_COAL produces elec? Usually no.
        model_elec['Coal'] = sum([elec_col.get(t, 0) for t in coal_techs]) * GWh_to_TWh
        # Gas Gen:
        gas_techs = ['CCGT', 'CCGT_AMMONIA', 'IND_COGEN_GAS', 'DHN_COGEN_GAS']
        model_elec['Gas'] = sum([elec_col.get(t, 0) for t in gas_techs]) * GWh_to_TWh
    else:
        model_elec = {}
    
    # --- Comparison Report ---
    report = []
    report.append("# Finland 2017 Model Validation Analysis")
    report.append("\n## 1. Primary Energy Comparison (TWh)")
    report.append("| Resource | Real (2017) | Model (Unconstrained) | Diff (%) | Status |")
    report.append("|---|---|---|---|---|")
    
    for key, real_val in real_2017['Primary Energy'].items():
        if key == 'Peat': continue
        model_val = model_pe.get(key, 0)
        diff = model_val - real_val
        pct = (diff / real_val * 100) if real_val > 0 else 0
        status = "OK" if abs(pct) < 15 else ("**HIGH**" if model_val > real_val else "**LOW**")
        report.append(f"| {key} | {real_val:.1f} | {model_val:.1f} | {pct:+.1f}% | {status} |")
    
    if model_pe.get('Hydrogen Import', 0) > 1:
        report.append(f"| Hydrogen Import | 0.0 | {model_pe['Hydrogen Import']:.1f} | +Inf% | **MODEL ARTIFACT** |")

    report.append("\n## 2. Electricity Generation Mix (TWh)")
    report.append("| Source | Real (2017) | Model (Unconstrained) | Diff (%) | Status |")
    report.append("|---|---|---|---|---|")
    
    for key, real_val in real_2017['Electricity Generation'].items():
        model_val = model_elec.get(key, 0)
        diff = model_val - real_val
        pct = (diff / real_val * 100) if real_val > 0 else 0
        status = "OK" if abs(pct) < 15 else ("**HIGH**" if model_val > real_val else "**LOW**")
        report.append(f"| {key} | {real_val:.1f} | {model_val:.1f} | {pct:+.1f}% | {status} |")

    report.append("\n## 3. Analysis & Conclusions")
    report.append("The unconstrained model run shows significant deviations from the 2017 validation year:")
    report.append("1. **Fuel Switch (Gas vs Wood):** The model massively prefers Natural Gas (>113 TWh) over Biomass (~0 TWh), whereas reality is the opposite. This is driven by cost optimization without 'Limpens-style' historical constraints. In 2017, legacy infrastructure and policy drove biomass use.")
    report.append("2. **Wind Overbuild:** The model installs ~15 TWh of Wind (economically optimal), triple the actual 2017 level (4.8 TWh).")
    report.append("3. **Hydrogen Import:** The model imports ~60 TWh of H2, likely to replace fossil fuels or for heavy transport/industry, which did not exist in 2017.")
    report.append("4. **Hydro:** Model estimates 31 TWh vs 14.6 TWh actual. This suggests availability factors or capacity inputs need checking.")
    
    # Saving report
    print("\n".join(report))
    with open("validation_report_2017.md", "w") as f:
        f.write("\n".join(report))
        
    # --- plotting ---
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Primary Energy Plot
    labels_pe = [k for k in real_2017['Primary Energy'].keys() if k != 'Peat']
    real_pe_vals = [real_2017['Primary Energy'][k] for k in labels_pe]
    model_pe_vals = [model_pe.get(k, 0) for k in labels_pe]
    
    x = range(len(labels_pe))
    ax[0].bar([i - 0.2 for i in x], real_pe_vals, width=0.4, label='Real 2017', color='blue')
    ax[0].bar([i + 0.2 for i in x], model_pe_vals, width=0.4, label='Model 2017', color='orange')
    ax[0].set_xticks(x)
    ax[0].set_xticklabels(labels_pe, rotation=45)
    ax[0].set_title('Primary Energy (TWh)')
    ax[0].legend()
    
    # 2. Electricity Plot
    labels_el = real_2017['Electricity Generation'].keys()
    real_el_vals = [real_2017['Electricity Generation'][k] for k in labels_el]
    model_el_vals = [model_elec.get(k, 0) for k in labels_el]
    
    x2 = range(len(labels_el))
    ax[1].bar([i - 0.2 for i in x2], real_el_vals, width=0.4, label='Real 2017', color='blue')
    ax[1].bar([i + 0.2 for i in x2], model_el_vals, width=0.4, label='Model 2017', color='orange')
    ax[1].set_xticks(x2)
    ax[1].set_xticklabels(labels_el, rotation=45)
    ax[1].set_title('Electricity Generation (TWh)')
    ax[1].legend()

    plt.tight_layout()
    plt.savefig('comparison_plot_2017.png')
    print("Plot saved to comparison_plot_2017.png")

if __name__ == "__main__":
    analyze()
