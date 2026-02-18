
import os
import pandas as pd
import re

# Absolute paths
base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
v8_path = os.path.join(base_path, r"case_studies\FI\calib_2017_finland_v8_no_coal_us")
v9_path = os.path.join(base_path, r"case_studies\FI\calib_2017_finland_v9")
data_path = os.path.join(base_path, r"Data\2017\FI\Demands.csv")

def parse_reg_demands(filepath):
    """
    Parses reg_demands.dat to extract demand parameters.
    Format:
    param end_uses_demand_year : 	HOUSEHOLDS	SERVICES	INDUSTRY	TRANSPORTATION := 
    FI	ELECTRICITY	8760.1	10822.3	23424.8	0.0
    ...
    ;
    """
    demands = {}
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return demands

    with open(filepath, 'r') as f:
        content = f.read()
    
    # Simple parsing logic
    # Find the block related to end_uses_demand_year
    # It might be spread across multiple lines
    
    lines = content.split('\n')
    parsing = False
    for line in lines:
        if "param end_uses_demand_year" in line:
            parsing = True
            continue
        if parsing and ";" in line:
            parsing = False
            break
        
        if parsing and line.strip().startswith('FI'):
            # Split by whitespace
            parts = line.strip().split()
            # FI Is usually first
            # The structure is: Region Category Val1 Val2 Val3 Val4
            # Or Category Val1..Val4?
            # Based on previous read: "FI	ELECTRICITY	8760... 10822... 23424... 0.0"
            if len(parts) >= 6:
                category = parts[1]
                try:
                    vals = [float(x) for x in parts[2:]]
                    demands[category] = sum(vals)
                except ValueError:
                    pass
            
    return demands

def get_consumption(filepath):
    """
    Parses Year_balance.csv to get consumption of oil products.
    Returns dictionary of fuel -> TWh (positive value for consumption)
    """
    res = {}
    fuels = ['GASOLINE', 'DIESEL', 'LFO', 'JET_FUEL', 'GAS', 'COAL', 'WOOD', 'WET_BIOMASS']
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return res

    try:
        df = pd.read_csv(filepath)
        # Consumption is negative in Year_balance.csv
        for f in fuels:
            if f in df.columns:
                # Sum only negative values
                val = df.loc[df[f] < 0, f].sum()
                res[f] = abs(val) 
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        
    return res

print(f"Comparing v8: {v8_path}")
print(f"       vs v9: {v9_path}")

# 1. Compare input demands (reg_demands.dat)
print("\n--- 1. DEMAND PARAMETERS (GWh or Mpkm/Mtkm) ---")
d8 = parse_reg_demands(os.path.join(v8_path, "reg_demands.dat"))
d9 = parse_reg_demands(os.path.join(v9_path, "reg_demands.dat"))

all_cats = sorted(list(set(d8.keys()) | set(d9.keys())))
print(f"{'Category':<25} {'v8':>15} {'v9':>15} {'Diff':>15}")
for c in all_cats:
    val8 = d8.get(c, 0)
    val9 = d9.get(c, 0)
    print(f"{c:<25} {val8:15.2f} {val9:15.2f} {val8-val9:15.2f}")

# 2. Compare output consumption (Year_balance.csv)
print("\n--- 2. FUEL CONSUMPTION (TWh) ---")
c8 = get_consumption(os.path.join(v8_path, "outputs", "Year_balance.csv"))
c9 = get_consumption(os.path.join(v9_path, "outputs", "Year_balance.csv"))

all_fuels = sorted(list(set(c8.keys()) | set(c9.keys())))
print(f"{'Fuel':<25} {'v8':>15} {'v9':>15} {'Ratio':>15}")
for f in all_fuels:
    val8 = c8.get(f, 0)
    val9 = c9.get(f, 0)
    ratio = val8/val9 if val9 > 1e-3 else 0.0
    print(f"{f:<25} {val8:15.2f} {val9:15.2f} {ratio:15.2f}")

# 3. Check for Demands.csv existence
print("\n--- 3. CHECKING CSV SOURCE FILES ---")
def check_csv(path):
    f1 = os.path.join(path, "Demands.csv")
    f2 = os.path.join(path, "00_td_dat", "Demands.csv")
    if os.path.exists(f1): return f1
    if os.path.exists(f2): return f2
    return None

f8 = check_csv(v8_path)
f9 = check_csv(v9_path)

if f8:
    print(f"v8 Demands.csv found at: {f8}")
    # Read and print first few lines of parameter 'MOBILITY_PASSENGER' if possible
    try:
        df = pd.read_csv(f8, sep=';', comment='#') # separator often ;
        # Assuming format: Parameter;Details;Unit;Value
        # Let's peek
        print(df.head())
    except:
        pass
else:
    print("v8 Demands.csv NOT found in case study folder.")

if f9:
    print(f"v9 Demands.csv found at: {f9}")
else:
    print("v9 Demands.csv NOT found in case study folder.")

