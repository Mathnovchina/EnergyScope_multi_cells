# ** DEPRECATED — Use validate_run.py instead. **
# This script is superseded by scripts/validate_run.py which provides:
#   - Corrected Statistics Finland 2017 electricity values
#   - CHP + condensation fuel-breakdown diagnostic plots
#   - Batch mode for all baselines (--batch)
# Run:  python validate_run.py --batch

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
import os

# Set up paths
SECTION = 'FI'
CASE_STUDY = 'calib_2017_finland'
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'case_studies' / SECTION / CASE_STUDY / 'outputs'
PLOTS_DIR = PROJECT_ROOT / 'plots' / 'validation_2017'

# Ensure plots directory exists and is empty (erase old)
import shutil
if os.path.exists(PLOTS_DIR):
    shutil.rmtree(PLOTS_DIR)
os.makedirs(PLOTS_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# REALITY DATA (2017 Finland - Approximate Targets)
# Source: Logic from conversation & Statistics Finland general knowledge
# -----------------------------------------------------------------------------
REALITY = {
    'Primary Energy': {
        'WOOD': 105.0, # Wood & Bio combined
        'OIL': 96.0,   # Refined Oil Products
        'NUCLEAR': 65.0, # Thermal input
        'COAL_PEAT': 50.0, # Coal 35 + Peat 15
        'GAS': 25.0,
        'HYDRO': 15.0,
        'WIND': 5.0,
        'AMMONIA': 0.0
    },
    'Electricity Generation': {
        'Nuclear': 21.6,
        'Hydro': 14.6,
        'Biomass': 11.0, 
        'Coal': 9.0, # Coal + Peat approx
        'Wind': 4.8,
        'Gas': 3.7,
        'Solar': 0.04,
        'Geothermal': 0.0,
        'CHP Oil': 0.0, # Included elsewhere in stats
        'Ammonia': 0.0  # Should not exist in 2017
    },
    'CO2 Emissions': 42.0 # MtCO2 (approx Energy Sector)
}

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def load_csv(filename):
    path = OUTPUT_DIR / filename
    if not path.exists():
        print(f"Warning: {path} not found.")
        return pd.DataFrame()
    # Try different separators
    try:
        df = pd.read_csv(path)
    except:
         df = pd.read_csv(path, sep=';')
         
    # Standardize first column name to 'item'
    df.rename(columns={df.columns[0]: 'item'}, inplace=True)
    
    # Calculate 'Yearly' for Resources.csv
    if filename == 'Resources.csv':
         # Consumption = Local + Exterior + Import - Export
         # Adjust based on available columns
         res_consump = 0
         if 'R_year_local' in df.columns: res_consump += df['R_year_local']
         if 'R_year_exterior' in df.columns: res_consump += df['R_year_exterior']
         if 'R_year_import' in df.columns: res_consump += df['R_year_import']
         # exclude exports if necessary, but usually negligible for primary
         
         df['Yearly'] = res_consump

    return df

# -----------------------------------------------------------------------------
# ANALYSIS & PLOTTING
# -----------------------------------------------------------------------------
def analyze_primary_energy():
    print("Analyzing Primary Energy...")
    resources = load_csv('Resources.csv')
    if resources.empty: return
    
    # Convert from GWh to TWh (Divide by 1000)
    SCALER = 1/1000.0

    # Map Model Resources to Reality Categories
    model_sum = {}
    
    # Wood Group
    wood_cols = ['WOOD', 'WET_BIOMASS', 'ENERGY_CROPS_2', 'BIOMASS_RESIDUES', 'BIOWASTE']
    model_val = resources[resources['item'].isin(wood_cols)]['Yearly'].sum() * SCALER
    model_sum['WOOD'] = model_val
    
    # Oil Group
    oil_cols = ['DIESEL', 'GASOLINE', 'LFO', 'JET_FUEL', 'OIL', 'DIESEL_RE', 'GASOLINE_RE', 'LFO_RE', 'JET_FUEL_RE', 'HFO', 'HFO_RE']
    found_oil = resources[resources['item'].isin(oil_cols)]
    oil_sum = found_oil['Yearly'].sum() * SCALER
    print(f"DEBUG: Found Oil items: {found_oil['item'].unique()} Sum: {oil_sum}")
    model_sum['OIL'] = oil_sum
    
    # Nuclear
    model_sum['NUCLEAR'] = resources[resources['item'] == 'URANIUM']['Yearly'].sum() * SCALER
    
    # Coal & Peat
    # Sum COAL (which in model currently acts as Coal+Peat proxy or just Coal)
    # If PEAT exists, add it.
    model_sum['COAL_PEAT'] = resources[resources['item'].isin(['COAL', 'PEAT'])]['Yearly'].sum() * SCALER
    
    # Gas
    model_sum['GAS'] = resources[resources['item'].isin(['GAS', 'GAS_RE'])]['Yearly'].sum() * SCALER
    
    # Hydro
    model_sum['HYDRO'] = resources[resources['item'] == 'RES_HYDRO']['Yearly'].sum() * SCALER
    
    # Wind
    model_sum['WIND'] = resources[resources['item'] == 'RES_WIND']['Yearly'].sum() * SCALER

    # Ammonia (The Anomaly!)
    model_sum['AMMONIA'] = resources[resources['item'].isin(['AMMONIA', 'AMMONIA_RE'])]['Yearly'].sum() * SCALER

    # Create DataFrame
    df = pd.DataFrame({
        'Model': model_sum,
        'Reality (Target)': REALITY['Primary Energy']
    }).fillna(0)
    
    # Calculate Totals (TPES)
    tpes_model = df['Model'].sum()
    tpes_real = df['Reality (Target)'].sum() # Should be approx 360 TWh (100+80+65+35+25+15+5) -> 325 + Peat?
    
    # Print Table
    print("\nPrimary Energy (TWh):")
    print(df)
    
    print("\n--- Total Primary Energy Supply (TPES) ---")
    print(f"Model:   {tpes_model:.1f} TWh")
    print(f"Reality: {tpes_real:.1f} TWh")
    print(f"Diff:    {tpes_model - tpes_real:.1f} TWh ({(tpes_model/tpes_real - 1)*100:+.1f}%)")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#4c72b0', '#55a868'] # Blue vs Green
    df.plot(kind='bar', ax=ax, width=0.8, color=colors)
    ax.set_title(f'Primary Energy Consumption (TWh) - {CASE_STUDY}')
    ax.set_ylabel('TWh')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add labels
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f')
        
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'primary_energy_comparison.png')
    print("Saved primary_energy_comparison.png")

def analyze_emissions():
    print("Analyzing CO2 Emissions...")
    yb = load_csv('Year_balance.csv')
    resources = load_csv('Resources.csv')
    
    if yb.empty or resources.empty: return
    
    # EMISSION FACTORS (Approximate from Resources_indep.csv)
    # Unit: ktCO2/GWh (Model uses kt and GWh) -> MtCO2 / TWh is equivalent (1/1000 * 1000)
    # So factor 0.4 kt/GWh = 0.4 Mt/TWh
    factors = {
        'COAL': 0.40,  # Resources_indep says 0.4014
        'OIL': 0.31,   # Diesel/LFO ~0.31
        'GAS': 0.26,   # Gas ~0.26
        'Peat': 0.38,  # Similar to coal
        'Waste': 0.15  # Non-renewable part
    }
    
    SCALER = 1/1000.0 # GWh -> TWh
    
    # Calculate Emissions Manually based on Primary Energy Consumption
    # This avoids issues if the model's CO2_ATM tracking is weird
    calculated_emissions = 0.0
    
    # Coal
    coal_val = resources[resources['item'] == 'COAL']['Yearly'].sum() * SCALER
    calculated_emissions += coal_val * factors['COAL']
    
    # Oil
    oil_cols = ['DIESEL', 'GASOLINE', 'LFO', 'JET_FUEL', 'OIL', 'HFO']
    oil_val = resources[resources['item'].isin(oil_cols)]['Yearly'].sum() * SCALER
    calculated_emissions += oil_val * factors['OIL']
    
    # Gas
    gas_val = resources[resources['item'] == 'GAS']['Yearly'].sum() * SCALER
    calculated_emissions += gas_val * factors['GAS']
    
    # Waste
    waste_val = resources[resources['item'] == 'WASTE']['Yearly'].sum() * SCALER
    calculated_emissions += waste_val * factors['Waste']
    
    print("\nCO2 Emissions Analysis:")
    print(f"Calculated from Primary Energy (Manual): {calculated_emissions:.2f} MtCO2")
    print(f"Reality: {REALITY['CO2 Emissions']} MtCO2")
    
    # Simple Bar Plot
    df = pd.DataFrame({
        'Emissions': [calculated_emissions, REALITY['CO2 Emissions']]
    }, index=['Model (Calc)', 'Reality'])
    
    fig, ax = plt.subplots(figsize=(6, 6))
    df.plot(kind='bar', ax=ax, color=['#d62728', '#7f7f7f'], legend=False)
    ax.set_title('CO2 Emissions (MtCO2)')
    ax.set_ylabel('MtCO2')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f')
        
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'co2_emissions_comparison.png')
    print("Saved co2_emissions_comparison.png")


def analyze_electricity():
    print("Analyzing Electricity Generation...")
    yb = load_csv('Year_balance.csv')
    if yb.empty: return
    
    SCALER = 1/1000.0

    # Filter for Electricity Techs
    groups = {
        'Nuclear': ['NUCLEAR'],
        'Hydro': ['HYDRO_DAM', 'HYDRO_RIVER'],
        'Biomass': ['IND_BOILER_WOOD', 'DEC_BOILER_WOOD', 'DHN_COGEN_WOOD', 'IND_COGEN_WOOD'], 
        'Coal': ['IND_BOILER_COAL', 'DHN_COGEN_COAL', 'COAL_US', 'COAL_IGCC'],
        'Wind': ['WIND_ONSHORE', 'WIND_OFFSHORE'],
        'Gas': ['CCGT', 'OCGT', 'IND_COGEN_GAS', 'DHN_COGEN_GAS', 'DEC_COGEN_GAS', 'DEC_ADVCOGEN_GAS'],
        'Solar': ['PV_ROOFTOP', 'PV_UTILITY'],
        'Geothermal': ['GEOTHERMAL'],
        'CHP Oil': ['DEC_COGEN_OIL'],
        'Ammonia': ['CCGT_AMMONIA'] # Catching the anomaly
    }
    
    model_vals = {k: 0.0 for k in groups.keys()}
    
    # Identify Electricity Column
    elec_col = 'ELECTRICITY'
    if elec_col not in yb.columns:
        print(f"Error: ELECTRICITY column not found in Year_balance. Available: {yb.columns}")
        return

    # Sum up
    for group, techs in groups.items():
        for tech in techs:
            # Flexible matching (contains)
            matches = [t for t in yb['item'] if tech in t]
            for m in matches:
                # Only if positive (Generation)
                val = yb.loc[yb['item'] == m, elec_col].values[0]
                if val > 0:
                    model_vals[group] += val * SCALER
    
    # Create DataFrame
    df = pd.DataFrame({
        'Model': model_vals,
        'Reality (Target)': REALITY['Electricity Generation']
    }).fillna(0)
    
    print("\nElectricity Generation (TWh):")
    print(df)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(kind='bar', ax=ax, width=0.8, color=['#1f77b4', '#ff7f0e'])
    ax.set_title(f'Electricity Generation (TWh) - {CASE_STUDY}')
    ax.set_ylabel('TWh')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f')
        
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'electricity_mix_comparison.png')
    print("Saved electricity_mix_comparison.png")

# -----------------------------------------------------------------------------
# SANKEY WRAPPER
# -----------------------------------------------------------------------------
def generate_sankey():
    print("Generating Sankey Diagram...")
    sys.path.append(str(PROJECT_ROOT))
    
    try:
        from esmc.postprocessing.draw_sankey.output_to_sankey_csv import write_sankey_file
        from esmc.postprocessing.draw_sankey.ESSankey import drawSankey
        
        # 1. Generate CSVs
        # Note: write_sankey_file expects space_id and case_study
        write_sankey_file(SECTION, CASE_STUDY)
        
        # 2. Draw HTML
        drawSankey(
            path=OUTPUT_DIR,
            outputfile='validation_sankey.html',
            I2S_File="input2sankey_Total.csv",
            auto_open=False
        )
        # Move to plots dir
        src = OUTPUT_DIR / 'validation_sankey.html'
        dst = PLOTS_DIR / 'validation_sankey.html'
        if src.exists():
            import shutil
            shutil.copy(src, dst)
            print(f"Sankey saved to {dst}")
            
    except ImportError:
        print("Could not import ESMC Sankey tools. Skipping.")
    except Exception as e:
        print(f"Error generating Sankey: {e}")

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Comparing Model ({CASE_STUDY}) to Reality...")
    analyze_primary_energy()
    analyze_electricity()
    analyze_emissions()
    # execute sankey if possible
    generate_sankey()  
    print(f"\nDone. Check {PLOTS_DIR} folder.")
