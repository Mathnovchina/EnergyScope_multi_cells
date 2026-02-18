import pandas as pd
import os
import re

# Define paths
base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
v9_input_tech = os.path.join(base_path, "Data", "2017", "FI", "Technologies.csv")
v9_input_res = os.path.join(base_path, "Data", "2017", "FI", "Resources.csv")
v9_output_yb = os.path.join(base_path, "case_studies", "FI", "calib_2017_finland_v9", "outputs", "Year_balance.csv")

v8_input_tech_dat = os.path.join(base_path, "case_studies", "FI", "calib_2017_finland_v8_no_coal_us", "reg_technologies.dat")
v8_input_res_dat = os.path.join(base_path, "case_studies", "FI", "calib_2017_finland_v8_no_coal_us", "reg_resources.dat")
v8_output_yb = os.path.join(base_path, "case_studies", "FI", "calib_2017_finland_v8_no_coal_us", "outputs", "Year_balance.csv")

def parse_ampl_dat_technologies(filepath):
    """
    Parses reg_technologies.dat to extract f_min, f_max, fmin_perc, fmax_perc.
    Format:
    param : 	c_inv	c_maint	gwp_constr	lifetime	c_p	fmin_perc	fmax_perc	f_min	f_max := 
    FI	NUCLEAR	6000.0	120.0	707.88	60	0.849	0.0	1.0	2.7	2.8
    """
    data = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    start_parsing = False
    headers = []
    for line in lines:
        line = line.strip()
        if line.startswith("param :"):
            # Extract headers
            # param : 	c_inv	c_maint	gwp_constr	lifetime	c_p	fmin_perc	fmax_perc	f_min	f_max := 
            parts = line.replace("param :", "").replace(":=", "").strip().split()
            headers = parts
            start_parsing = True
            continue
        
        if start_parsing and line.startswith("FI"): # Assuming region is FI
            parts = line.split()
            # parts[0] is Region, parts[1] is Tech
            if len(parts) >= len(headers) + 2:
                row = {}
                row['Technologies'] = parts[1]
                # Map values to headers
                # parts[2] corresponds to headers[0]
                for i, header in enumerate(headers):
                    try:
                        row[header] = float(parts[2+i])
                    except ValueError:
                         if parts[2+i] == 'Infinity':
                             row[header] = float('inf')
                         else:
                             row[header] = parts[2+i]
                data.append(row)
        elif start_parsing and line.startswith(";"):
            break
            
    return pd.DataFrame(data)

def parse_ampl_dat_resources(filepath):
    """
    Parses reg_resources.dat to extract avail_exterior.
    Format:
    param : 	avail_local	avail_exterior	gwp_op_local	c_op_local := 
    FI	ELECTRICITY	0.0	25000.0	0.21	0.05
    """
    data = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    start_parsing = False
    headers = []
    for line in lines:
        line = line.strip()
        if line.startswith("param :"):
            parts = line.replace("param :", "").replace(":=", "").strip().split()
            headers = parts
            start_parsing = True
            continue
            
        if start_parsing and line.startswith("FI"):
            parts = line.split()
            if len(parts) >= len(headers) + 2:
                row = {}
                row['Resources'] = parts[1]
                for i, header in enumerate(headers):
                    try:
                        row[header] = float(parts[2+i])
                    except ValueError:
                         if parts[2+i] == 'Infinity':
                             row[header] = float('inf')
                         else:
                             row[header] = parts[2+i]
                data.append(row)
        elif start_parsing and line.startswith(";"):
            break
    return pd.DataFrame(data)

print("-" * 50)
print("Comparing Inputs (Technologies)")
print("-" * 50)

# Load v9 Tech
if os.path.exists(v9_input_tech):
    df_v9_tech = pd.read_csv(v9_input_tech, index_col=0) # Assuming first col is Technologies param or similar
    # It might be named "Technologies param" or just "Technologies"
    # Inspect columns to be safe
    if 'Technologies param' in df_v9_tech.columns: 
        # Actually standard CSV structure usually has headers on first row
        pass
    # If first column is index, usually it is name of tech.
else:
    print(f"Error: v9 Tech file not found at {v9_input_tech}")
    df_v9_tech = pd.DataFrame()

# Load v8 Tech
if os.path.exists(v8_input_tech_dat):
    df_v8_tech = parse_ampl_dat_technologies(v8_input_tech_dat)
    if not df_v8_tech.empty:
        df_v8_tech.set_index('Technologies', inplace=True)
else:
    print(f"Error: v8 Tech .dat file not found at {v8_input_tech_dat}")
    df_v8_tech = pd.DataFrame()

# Compare specific techs
techs_to_check = ['TRUCK_DIESEL', 'CAR_GASOLINE', 'IND_BOILER_WOOD', 'DHN_BOILER_WOOD']
cols_to_check = ['f_min', 'f_max', 'fmin_perc', 'fmax_perc']

for tech in techs_to_check:
    print(f"\nTechnology: {tech}")
    if tech in df_v9_tech.index:
        v9_vals = df_v9_tech.loc[tech, cols_to_check] if all(c in df_v9_tech.columns for c in cols_to_check) else "Cols missing"
        print(f"  v9: {v9_vals.to_dict() if isinstance(v9_vals, pd.Series) else v9_vals}")
    else:
        print(f"  v9: Not found")
        
    if tech in df_v8_tech.index:
        v8_vals = df_v8_tech.loc[tech, cols_to_check] if all(c in df_v8_tech.columns for c in cols_to_check) else "Cols missing"
        print(f"  v8: {v8_vals.to_dict() if isinstance(v8_vals, pd.Series) else v8_vals}")
    else:
        print(f"  v8: Not found")

print("\n" + "-" * 50)
print("Comparing Inputs (Resources)")
print("-" * 50)

if os.path.exists(v9_input_res):
    df_v9_res = pd.read_csv(v9_input_res, index_col=0)
else:
    print(f"Error: v9 Resources not found")
    df_v9_res = pd.DataFrame()

if os.path.exists(v8_input_res_dat):
    df_v8_res = parse_ampl_dat_resources(v8_input_res_dat)
    if not df_v8_res.empty:
        df_v8_res.set_index('Resources', inplace=True)
else:
    print(f"Error: v8 Resources .dat not found")
    df_v8_res = pd.DataFrame()

res_to_check = ['GASOLINE', 'DIESEL', 'OIL', 'LFO', 'WOOD']
# Check avail_exterior
for res in res_to_check:
    print(f"\nResource: {res}")
    if res in df_v9_res.index:
        print(f"  v9 avail_exterior: {df_v9_res.loc[res, 'avail_exterior']}")
    else:
        print(f"  v9: Not found")
        
    if res in df_v8_res.index:
        print(f"  v8 avail_exterior: {df_v8_res.loc[res, 'avail_exterior']}")
    else:
        print(f"  v8: Not found")


print("\n" + "-" * 50)
print("Comparing Outputs (Year_balance consumption)")
print("-" * 50)

def get_consumption(filepath, resource_name):
    if not os.path.exists(filepath):
        return "File not found"
    df = pd.read_csv(filepath, index_col=0)
    # Rows are Technologies, Columns are Elements (Resources)
    if resource_name not in df.columns:
        return "Resource not in columns"
    
    # Consumption is usually negative values in the Resources column for technologies that consume it
    # Or positive? In EnergyScope, usually positive = production, negative = consumption in balance?
    # Actually Year_balance usually shows flux.
    # Total consumption = sum of negative values? Or specific rows?
    # Let's just print the sum of column.
    
    return df[resource_name].sum()

def get_tech_consumption(filepath, tech_name, resource_name):
    if not os.path.exists(filepath):
        return "File not found"
    df = pd.read_csv(filepath, index_col=0)
    if resource_name not in df.columns:
        return "Resource column missing"
    if tech_name not in df.index:
        return "Tech row missing"
    return df.loc[tech_name, resource_name]

resources_output = ['GASOLINE', 'DIESEL', 'OIL', 'WOOD', 'LFO']

print(f"{'Resource':<15} | {'v9 Total':<15} | {'v8 Total':<15}")
for res in resources_output:
    v9_val = get_consumption(v9_output_yb, res)
    v8_val = get_consumption(v8_output_yb, res)
    print(f"{res:<15} | {v9_val:<15} | {v8_val:<15}")

print("\nSpecific Tech consumptions (WOOD):")
for tech in ['IND_BOILER_WOOD', 'DHN_BOILER_WOOD']:
    v9_val = get_tech_consumption(v9_output_yb, tech, 'WOOD')
    v8_val = get_tech_consumption(v8_output_yb, tech, 'WOOD')
    print(f"{tech}: v9={v9_val}, v8={v8_val}")

