
import pandas as pd
import os

# Define paths
DATA_DIR = os.path.join('Data', '2017', 'FI')
RESOURCES_FILE = os.path.join(DATA_DIR, 'Resources.csv')
DEMANDS_FILE = os.path.join(DATA_DIR, 'Demands.csv')
TIME_SERIES_FILE = os.path.join(DATA_DIR, 'Time_series.csv')
TECHNOLOGIES_FILE = os.path.join(DATA_DIR, 'Technologies.csv')

def check_resources_vs_demands():
    print("\n--- 1. Resources vs Demands ---")
    
    # Resources
    if os.path.exists(RESOURCES_FILE):
        try:
            res_df = pd.read_csv(RESOURCES_FILE, index_col=0)
            # Assuming avail_local is in GWh. User asked to convert to TWh.
            # Usually the file has no unit in header but it IS typically GWh in ESMC.
            total_avail_gwh = res_df['avail_local'].sum()
            total_avail_twh = total_avail_gwh / 1000
            print(f"Total Resources avail_local: {total_avail_gwh:.2f} GWh = {total_avail_twh:.2f} TWh")
            print("Top 5 Resources by availability:")
            print(res_df['avail_local'].sort_values(ascending=False).head(5) / 1000)
        except Exception as e:
            print(f"Error reading Resources: {e}")
    else:
        print(f"File not found: {RESOURCES_FILE}")

    # Demands
    if os.path.exists(DEMANDS_FILE):
        try:
            dem_df = pd.read_csv(DEMANDS_FILE)
            # Sum demand columns
            demand_cols = ['HOUSEHOLDS', 'SERVICES', 'INDUSTRY', 'TRANSPORTATION']
            # Filter non-numeric just in case (though read_csv should handle)
            dem_df['Total_GWh'] = dem_df[demand_cols].sum(axis=1)
            
            print("\nDemands by Category (TWh):")
            for index, row in dem_df.iterrows():
                cat = row['parameter name']
                val_twh = row['Total_GWh'] / 1000
                print(f"  {cat}: {val_twh:.2f} TWh")
                
            total_demand_twh = dem_df['Total_GWh'].sum() / 1000
            print(f"Total Demand: {total_demand_twh:.2f} TWh")
            
        except Exception as e:
            print(f"Error reading Demands: {e}")
    else:
        print(f"File not found: {DEMANDS_FILE}")

def check_wind_cp():
    print("\n--- 2. Wind Capacity Factor (c_p) ---")
    if os.path.exists(TIME_SERIES_FILE):
        try:
            ts_df = pd.read_csv(TIME_SERIES_FILE)
            if 'WIND_ONSHORE' in ts_df.columns:
                wind_cp = ts_df['WIND_ONSHORE']
                print(f"WIND_ONSHORE Stats:")
                print(f"  Min: {wind_cp.min()}")
                print(f"  Max: {wind_cp.max()}")
                print(f"  Mean: {wind_cp.mean()}")
                zeros = (wind_cp == 0).sum()
                print(f"  Hours with 0 generation: {zeros}")
                
                # Check for other columns just in case
                if 'NUCLEAR' in ts_df.columns:
                     nuc_cp = ts_df['NUCLEAR']
                     print(f"NUCLEAR in Time_series Stats:")
                     print(f"  Min: {nuc_cp.min()}")
                     print(f"  Max: {nuc_cp.max()}")
                else:
                    print("NUCLEAR not in Time_series (Expected if c_p is constant)")
            else:
                print("WIND_ONSHORE not found in Time_series.csv")
        except Exception as e:
            print(f"Error reading Time_series: {e}")
    else:
        print(f"File not found: {TIME_SERIES_FILE}")

def check_technologies_and_storage():
    print("\n--- 3 & 4. Technologies & Storage ---")
    if os.path.exists(TECHNOLOGIES_FILE):
        try:
            tech_df = pd.read_csv(TECHNOLOGIES_FILE, index_col=0)
            
            # Check Nuclear
            if 'NUCLEAR' in tech_df.index:
                print(f"NUCLEAR parameters:")
                print(tech_df.loc['NUCLEAR', ['f_min', 'f_max']])
            else:
                print("NUCLEAR not found in Technologies.csv")
            
            # Check Storage
            # Keywords for storage
            storage_keywords = ['STORAGE', 'BATT', 'PHS', 'TS_', 'DAM']
            found_storage = []
            for tech in tech_df.index:
                if any(k in tech for k in storage_keywords):
                    found_storage.append(tech)
            
            print("\nPotential Storage Technologies found:")
            if found_storage:
                for tech in found_storage:
                    # Accessing using .loc[tech] might return a Series if tech is unique, but let's be safe
                    # Actually if tech is unique index, .loc[tech] is a Series.
                    # If there are duplicates, it's a DataFrame. Assuming unique index.
                    try:
                        f_min = tech_df.loc[tech, 'f_min']
                        f_max = tech_df.loc[tech, 'f_max']
                        print(f"  {tech}")
                        print(f"    f_min: {f_min}")
                        print(f"    f_max: {f_max}")
                    except:
                        pass
            else:
                print("  NO STORAGE TECHNOLOGIES FOUND based on keywords [STORAGE, BATT, PHS, TS_, DAM]")

            # Check for specific missing technologies and add them
            missing_techs = []
            target_techs = ['BATT_LI', 'TS_DEC_TH', 'TS_DHN_TH']
            for t in target_techs:
                if t not in tech_df.index:
                    missing_techs.append(t)
            
            if missing_techs:
                print(f"\nMissing technologies: {missing_techs}")
                print("Adding missing technologies to Technologies.csv...")
                
                with open(TECHNOLOGIES_FILE, 'a') as f:
                    for tech in missing_techs:
                        # Format: Technologies param,f_min,f_max,fmin_perc,fmax_perc
                        # Using 0.0, 100000.0 (unlimited), 0.0, 1.0
                        line = f"\n{tech},0.0,100000.0,0.0,1.0"
                        f.write(line)
                        print(f"Added {tech}")
            else:
                print("\nAll target storage technologies are present.")

        except Exception as e:
            print(f"Error reading/modifying Technologies: {e}")
    else:
        print(f"File not found: {TECHNOLOGIES_FILE}")

if __name__ == "__main__":
    check_resources_vs_demands()
    check_wind_cp()
    check_technologies_and_storage()
