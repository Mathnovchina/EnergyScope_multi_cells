
import pandas as pd
import os

# Paths
BASE_DIR = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
TECH_FILE = os.path.join(BASE_DIR, 'Data', '2017', 'FI', 'Technologies.csv')
RES_FILE = os.path.join(BASE_DIR, 'Data', '2017', 'FI', 'Resources.csv')

def apply_constraints():
    print(f"Loading Technologies from {TECH_FILE}")
    df_tech = pd.read_csv(TECH_FILE, index_col=0)
    # Clean index
    df_tech.index = df_tech.index.str.strip()

    # 1. Constrain GAS Import (Pipeline capacity proxy)
    # Real 2017: ~22 TWh/yr => ~2.5 GW avg. 
    # Current model used 113 TWh. 
    # Set limit to 6 GW (allows ~52 TWh max, enough buffer but kills 113 TWh)
    if 'GAS' in df_tech.index:
        df_tech.loc['GAS', 'f_max'] = 6.0
        print("Updated GAS f_max -> 6.0 GW")

    # 2. Constrain COAL Import
    # Real 2017: ~32 TWh/yr => ~3.6 GW avg.
    # Set limit to 6 GW
    if 'COAL' in df_tech.index:
        df_tech.loc['COAL', 'f_max'] = 6.0
        print("Updated COAL f_max -> 6.0 GW")

    # 3. Disable Future H2 Technologies
    h2_techs = ['H2_NG', 'H2_ELECTROLYSIS', 'H2_BIOMASS', 
                'H2_TO_GASOLINE', 'H2_TO_DIESEL', 'H2_TO_JET_FUEL', 
                'H2_TO_LFO', 'AMMONIA_TO_H2']
    for tech in h2_techs:
        if tech in df_tech.index:
            df_tech.loc[tech, 'f_max'] = 0.0
            df_tech.loc[tech, 'f_min'] = 0.0
            print(f"Disabled {tech}")

    # 4. Constrain Hydro (Overestimated in model)
    # Real 2017: 14.6 TWh. Model: 26.7 TWh.
    # Reduce capacities.
    if 'HYDRO_DAM' in df_tech.index:
        # Was 1.8. Reduce to 1.1
        df_tech.loc['HYDRO_DAM', 'f_max'] = 1.1
        print("Updated HYDRO_DAM f_max -> 1.1 GW")
        
    if 'HYDRO_RIVER' in df_tech.index:
        # Was 2.5. Reduce to 1.6
        df_tech.loc['HYDRO_RIVER', 'f_max'] = 1.6
        print("Updated HYDRO_RIVER f_max -> 1.6 GW")

    # 5. Constrain Wind Onshore (Overbuilt)
    # Real 2017: ~2.0 GW Capacity. Model built > 4 GW equivalent output?
    # Set max to 2.2 GW.
    if 'WIND_ONSHORE' in df_tech.index:
        df_tech.loc['WIND_ONSHORE', 'f_max'] = 2.2
        # Ensure f_min is not higher
        if df_tech.loc['WIND_ONSHORE', 'f_min'] > 2.2:
             df_tech.loc['WIND_ONSHORE', 'f_min'] = 2.2
        print("Updated WIND_ONSHORE f_max -> 2.2 GW")

    # Save
    df_tech.to_csv(TECH_FILE)
    print("Technologies.csv updated successfully.")

if __name__ == "__main__":
    apply_constraints()
