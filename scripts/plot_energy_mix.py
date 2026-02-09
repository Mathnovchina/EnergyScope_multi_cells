import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def plot_energy_mix(space_id, case_study):
    output_dir = os.path.join("case_studies", space_id, case_study, "outputs")
    file_path = os.path.join(output_dir, "Year_balance.csv")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Read CSV
    try:
        df = pd.read_csv(file_path, index_col=0, sep=",")
    except:
        df = pd.read_csv(file_path, index_col=0, sep=";")

    # Primary Energy Resources
    # We look for columns that represent primary resources
    resources = [
        "GASOLINE", "DIESEL", "LFO", "JET_FUEL", "GAS", 
        "WOOD", "WET_BIOMASS", "BIOWASTE", "COAL", "URANIUM", "WASTE", 
        "RES_WIND", "RES_SOLAR", "RES_HYDRO", "RES_GEO",
        "COAL_US", "COAL_IGCC" # If these are resources? No, likely techs.
    ]
    
    # Filter columns that exist
    resources = [c for c in resources if c in df.columns]

    # Calculate Total Consumption (Input > 0) per resource
    # Sum over all rows where value > 0
    mix = {}
    for r in resources:
        # Sum positive values (Inputs to the system/techs)
        # However, for RES (Wind/Solar), the flow is Output from Resource?
        # In Year_balance:
        # PV_UTILITY: ELECTRICITY -105, RES_SOLAR +105.
        # So Input is Positive.
        # So Sum(Positive values) is correct for consumption of that resource.
        val = df[r][df[r] > 0].sum()
        mix[r] = val / 1000.0 # Convert to TWh (assuming GWh input)

    mix_series = pd.Series(mix)
    mix_series = mix_series[mix_series > 0.1] # Filter small

    plt.figure(figsize=(10, 6))
    mix_series.plot(kind='bar', color='skyblue')
    plt.title(f"Primary Energy Mix (TWh) - {case_study}")
    plt.ylabel("TWh")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img_path = os.path.join(output_dir, "Primary_Energy_Mix.png")
    plt.savefig(img_path)
    print(f"Plot saved to {img_path}")

if __name__ == "__main__":
    plot_energy_mix("FI", "ref_2017_finland")
