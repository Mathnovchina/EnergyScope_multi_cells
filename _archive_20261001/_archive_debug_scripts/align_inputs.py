import pandas as pd
import os
from datetime import datetime
import numpy as np

# Paths
base_dir = r"C:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
tech_file_2017 = os.path.join(base_dir, "Data", "2017", "FI", "Technologies.csv")
tech_file_ref = os.path.join(base_dir, "Data", "2017", "02_REF_REGION", "Technologies.csv")
res_file_2017 = os.path.join(base_dir, "Data", "2017", "FI", "Resources.csv")
res_file_2035 = os.path.join(base_dir, "Data", "2035", "FI", "Resources.csv")
exog_file = os.path.join(base_dir, "Data", "exogenous_data", "Finland_MASTER_Calibration.xlsx")

# 1. Log Source & Values
print(f"Updating log file: {exog_file}")
try:
    if os.path.exists(exog_file):
        # Read Excel
        df_log = pd.read_excel(exog_file)
        
        # New entry
        new_row = {
            "Date": datetime.now(),
            "Description": "Update Onshore/Offshore Wind and Large Heat Pumps costs",
            "Notes": "Source: Estimated historical 2015 values (DEA 2015 data unavailable online). Onshore Inv: 1.3 M€/MW, Offshore Inv: 3.5 M€/MW, HP Inv: 0.8 M€/MW."
        }
        
        # Append
        df_log = pd.concat([df_log, pd.DataFrame([new_row])], ignore_index=True)
        
        # Write back
        df_log.to_excel(exog_file, index=False)
        print("Log updated successfully.")
    else:
        print(f"Warning: Log file not found: {exog_file}")
except Exception as e:
    print(f"Error updating Excel log: {e}")

# 2. Update Technologies.csv
print(f"Updating Technologies: {tech_file_2017}")
if os.path.exists(tech_file_2017):
    # Read existing FI technologies
    df_tech = pd.read_csv(tech_file_2017, index_col=0)
    
    # Ensure columns exist
    for col in ['c_inv', 'c_maint']:
        if col not in df_tech.columns:
            df_tech[col] = np.nan
            
    # Define updates (Units: User input M€/MW -> Convert to M€/GW by * 1000)
    updates = {
        'WIND_ONSHORE': {'c_inv': 1.3 * 1000, 'c_maint': 0.021 * 1000},
        'WIND_OFFSHORE': {'c_inv': 3.5 * 1000, 'c_maint': 0.10 * 1000},
    }
    
    # Handle "Large Heat Pumps" (HEAT_HIGH_T)
    # Check if HEAT_HIGH_T exists as a technology name
    if 'HEAT_HIGH_T' in df_tech.index:
        target_hp = 'HEAT_HIGH_T'
    else:
        # Check REF file to see if user meant DHN_HP_ELEC
        # We assume DHN_HP_ELEC corresponds to "Large Heat Pumps"
        target_hp = 'DHN_HP_ELEC'
        print(f"Note: 'HEAT_HIGH_T' not found. Applying large heat pump update to '{target_hp}'.")
        
        # If DHN_HP_ELEC is not in FI file, we might need to add it?
        if target_hp not in df_tech.index:
             # In EnergyScope, if a technology is not in the regional file, it uses REF.
             # To Override REF, we must add it to the regional file.
             print(f"Adding '{target_hp}' override to {tech_file_2017}")
             # Create a new row with NaNs, then update
             df_tech.loc[target_hp] = np.nan
    
    # Add HP update
    updates[target_hp] = {'c_inv': 0.8 * 1000, 'c_maint': 0.002 * 1000}
    
    # Apply updates
    for tech, vals in updates.items():
        if tech in df_tech.index:
            df_tech.loc[tech, 'c_inv'] = vals['c_inv']
            df_tech.loc[tech, 'c_maint'] = vals['c_maint']
            print(f"Updated {tech}: c_inv={vals['c_inv']}, c_maint={vals['c_maint']}")
        else:
            print(f"Error: {tech} could not be updated/added.")
            
    # Save
    df_tech.to_csv(tech_file_2017)
    print("Technologies.csv updated.")
else:
    print(f"Error: {tech_file_2017} not found.")

# 3. Align Resources.csv
print(f"Aligning Resources: {res_file_2017} to {res_file_2035}")
if os.path.exists(res_file_2017) and os.path.exists(res_file_2035):
    # Read files
    df_res_2017 = pd.read_csv(res_file_2017, index_col=0)
    df_res_2035 = pd.read_csv(res_file_2035, index_col=0)
    
    print("2017 Original Index:", df_res_2017.index.tolist())
    print("2035 Target Index:", df_res_2035.index.tolist())
    
    # Create new aligned dataframe
    # We want 2017 values but 2035 structure
    df_aligned = pd.DataFrame(index=df_res_2035.index, columns=df_res_2035.columns)
    
    for res in df_res_2035.index:
        if res in df_res_2017.index:
            # Copy values if columns match
            for col in df_aligned.columns:
                if col in df_res_2017.columns:
                    df_aligned.loc[res, col] = df_res_2017.loc[res, col]
        else:
             print(f"Warning: Resource {res} missing in 2017 source. Using 2035 values or NaN.")
             # Fallback to 2035 values if available?
             # Or check if it's a sum of others (e.g. WOOD)?
             # But aligning structure implies we accept incomplete data if 2017 didn't have it.
             # But if 2035 has it, we probably want it.
             df_aligned.loc[res] = df_res_2035.loc[res]

    # Handle known aggregates if necessary
    # (e.g. if 2017 had "ENERGY_CROPS_2" and 2035 has "Slurry" or something else?)
    # Assuming simple alignment based on names.
    
    # Save
    df_aligned.to_csv(res_file_2017)
    print("Resources.csv aligned and saved.")
else:
    print("Error: Resource files missing.")
