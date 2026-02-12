import pandas as pd
import os

workspace_root = r"c:/Users/borde/OneDrive/Bureau/model/EnergyScope_multi_cells"
output_dir = os.path.join(workspace_root, "case_studies/FI/calib_2017_finland/outputs")
assets_path = os.path.join(output_dir, "Assets.csv")

if not os.path.exists(assets_path):
    print("Assets.csv not found.")
else:
    df = pd.read_csv(assets_path, index_col=0)
    # Check key columns. Usually "f" is capacity.
    # Adjust column name if needed.
    # Looking for 'f' or similar.
    # print(df.head())
    
    techs = [
        "NUCLEAR", "WIND_ONSHORE", "HYDRO_RIVER", 
        "IND_BOILER_WOOD", "DHN_COGEN_WOOD", "DEC_BOILER_WOOD",
        "IND_COGEN_GAS", "DEC_ADVCOGEN_GAS", "DEC_THHP_GAS",
        "CCGT", "DHN_COGEN_GAS", "IND_BOILER_GAS", "DEC_BOILER_GAS",
        "IND_BOILER_COAL"
    ]
    
    print("\n--- Key Capacities (f) [GW] ---")
    # Using 'f' column.
    for t in techs:
        if t in df.index:
            # Check if 'f' exists
            if 'f' in df.columns:
                 print(f"{t}: {df.loc[t, 'f']:.4f}")
            else:
                 print(f"{t}: 'f' col missing")
        else:
            print(f"{t}: Not Installed (Not in Assets)")
