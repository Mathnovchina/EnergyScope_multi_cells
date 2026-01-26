
import pandas as pd
import os
import json
import ast

# Paths
BASE_DIR = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
DATA_2017_DIR = os.path.join(BASE_DIR, 'Data', '2017')
CALIB_FILE = os.path.join(BASE_DIR, 'Data', 'exogenous_data', 'Finland_Calibration_MASTER.xlsx')

def main():
    print(f"Reading calibration file: {CALIB_FILE}")
    try:
        # Load sheets
        demands_df = pd.read_excel(CALIB_FILE, sheet_name='5_Finland_Demands_2015')
        resources_df = pd.read_excel(CALIB_FILE, sheet_name='4_Finland_Resources')
        tech_caps_df = pd.read_excel(CALIB_FILE, sheet_name='6_Technology_Capacities')
        misc_params_df = pd.read_excel(CALIB_FILE, sheet_name='7_Misc_Parameters')
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # 1. Update Demands
    demands_csv_path = os.path.join(DATA_2017_DIR, 'FI', 'Demands.csv')
    if os.path.exists(demands_csv_path):
        # ... (Same as before)
        curr_demands = pd.read_csv(demands_csv_path)
        for _, row in demands_df.iterrows():
            cat = row['Category']
            subcat = row['Subcategory']
            mask = (curr_demands['Category'] == cat) & (curr_demands['Subcategory'] == subcat)
            if mask.any():
                if 'HOUSEHOLDS_GWh' in row: curr_demands.loc[mask, 'HOUSEHOLDS'] = row['HOUSEHOLDS_GWh']
                if 'SERVICES_GWh' in row: curr_demands.loc[mask, 'SERVICES'] = row['SERVICES_GWh']
                if 'INDUSTRY_GWh' in row: curr_demands.loc[mask, 'INDUSTRY'] = row['INDUSTRY_GWh']
                if 'TRANSPORTATION_GWh' in row: curr_demands.loc[mask, 'TRANSPORTATION'] = row['TRANSPORTATION_GWh']
        curr_demands.to_csv(demands_csv_path, index=False)
        print("Demands updated.")

    # 2. Update Resources
    resources_csv_path = os.path.join(DATA_2017_DIR, 'FI', 'Resources.csv')
    if os.path.exists(resources_csv_path):
        # ...
        curr_resources = pd.read_csv(resources_csv_path, index_col=0)
        for _, row in resources_df.iterrows():
            res_name = str(row['Resource']).strip()
            if res_name in curr_resources.index:
                curr_resources.loc[res_name, 'avail_local'] = row['Availability_GWh']
                cost = row['Cost_EUR_per_GWh']
                if pd.notnull(cost):
                   if cost > 100: cost = cost / 1e6
                   curr_resources.loc[res_name, 'c_op_local'] = cost
        curr_resources.to_csv(resources_csv_path)
        print("Resources updated.")

    # 3. Update Technologies (f_max AND f_min)
    technologies_csv_path = os.path.join(DATA_2017_DIR, 'FI', 'Technologies.csv')
    if os.path.exists(technologies_csv_path):
        print(f"Updating {technologies_csv_path}...")
        curr_tech = pd.read_csv(technologies_csv_path, index_col=0) # index is 'Technologies param'
        # Clean index whitespace
        curr_tech.index = curr_tech.index.str.strip()
        
        for _, row in tech_caps_df.iterrows():
            tech_name = str(row['Technology']).strip()
            year_2017_cap = row['Year_2017']
            f_max_2017 = row['f_max_2017']
            
            if tech_name == "WIND_ONSHORE":
                print(f"DEBUG: WIND_ONSHORE - Year_2017: {year_2017_cap}, f_max: {f_max_2017}, Present? {tech_name in curr_tech.index}")
            
            if tech_name in curr_tech.index:
                 # Update f_max
                 if pd.notnull(f_max_2017):
                     curr_tech.loc[tech_name, 'f_max'] = f_max_2017
                 
                 # Update f_min
                 if pd.notnull(year_2017_cap):
                     # Ensure it's a number
                     try:
                         val = float(year_2017_cap)
                         curr_tech.loc[tech_name, 'f_min'] = val
                         if tech_name == "WIND_ONSHORE": print(f"DEBUG: Set f_min to {val}")
                     except:
                         pass
                 
                 # Ensure f_min <= f_max
                 f_min_val = curr_tech.loc[tech_name, 'f_min']
                 f_max_val = curr_tech.loc[tech_name, 'f_max']
                 
                 if f_min_val > f_max_val:
                     print(f"WARNING: {tech_name} f_min ({f_min_val}) > f_max ({f_max_val}). Adjusting f_min = f_max.")
                     curr_tech.loc[tech_name, 'f_min'] = f_max_val
        
        curr_tech.to_csv(technologies_csv_path)
        print("Technologies updated.")

    # 4. Update Misc Parameters (Misc.json and Misc_indep.json)
    # ... (Same as before)
    # Load target JSONs
    fi_misc_path = os.path.join(DATA_2017_DIR, 'FI', 'Misc.json')
    indep_misc_path = os.path.join(DATA_2017_DIR, '00_INDEP', 'Misc_indep.json')
    
    if os.path.exists(fi_misc_path) and os.path.exists(indep_misc_path):
        with open(fi_misc_path, 'r') as f: fi_misc = json.load(f)
        with open(indep_misc_path, 'r') as f: indep_misc = json.load(f)
        indep_keys = list(indep_misc.keys())
        
        for _, row in misc_params_df.iterrows():
            param = str(row['Parameter']).strip()
            val = row['2017_value']
            
            if pd.isna(val): continue
                
            if isinstance(val, str) and (val.strip().startswith('{') or val.strip().startswith('[')):
                try:
                    val_parsed = ast.literal_eval(val)
                    val = val_parsed
                except: pass

            if param in indep_keys:
                indep_misc[param] = val
            else:
                fi_misc[param] = val
                
        with open(fi_misc_path, 'w') as f: json.dump(fi_misc, f, indent=4)
        with open(indep_misc_path, 'w') as f: json.dump(indep_misc, f, indent=4)
        print("Misc parameters updated.")

if __name__ == "__main__":
    main()
