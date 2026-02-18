
import pandas as pd
import os
import re

# Define paths
base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
v8_dir = os.path.join(base_path, "case_studies", "FI", "calib_2017_finland_v8_no_coal_us")
v9_dir = os.path.join(base_path, "case_studies", "FI", "calib_2017_finland_v9")

print(f"Comparing:")
print(f"v8: {v8_dir}")
print(f"v9: {v9_dir}")

def parse_ampl_dat_simple(filepath, keys):
    """
    Simple parser for AMPL .dat files that look like:
    param : k1 k2 k3 := 
    Region Item val1 val2 val3
    Could fail on complex structures.
    """
    data = {}
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return {}

    with open(filepath, "r") as f:
        lines = f.readlines()
    
    parsing = False
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"): continue
        
        if ":=" in line:
            parsing = True
            continue
        if ";" in line:
            parsing = False
            continue
        
        if parsing:
            parts = line.split()
            # Expecting: Region Item val1 val2 ...
            # Length should be at least 2 + len(keys) usually
            if len(parts) >= 2:
                region = parts[0]
                item = parts[1]
                values = parts[2:]
                
                # Basic float conversion attempt
                parsed_vals = {}
                for i, k in enumerate(keys):
                    if i < len(values):
                        try:
                            parsed_vals[k] = float(values[i])
                        except:
                            parsed_vals[k] = values[i]
                data[item] = parsed_vals

    return data

# Resources
print("\n--- Resources (v8 vs v9) ---")
res_keys = ["avail_local", "avail_exterior", "gwp_op_local", "c_op_local"]
res_v8 = parse_ampl_dat_simple(os.path.join(v8_dir, "reg_resources.dat"), res_keys)
res_v9 = parse_ampl_dat_simple(os.path.join(v9_dir, "reg_resources.dat"), res_keys)

all_res = set(res_v8.keys()) | set(res_v9.keys())
for r in all_res:
    if r not in res_v8: print(f"{r}: New in v9"); continue
    if r not in res_v9: print(f"{r}: Removed in v9"); continue
    
    diff = []
    for k in res_keys:
        v8 = res_v8[r].get(k)
        v9 = res_v9[r].get(k)
        if v8 != v9:
            diff.append(f"{k}: {v8}->{v9}")
    if diff:
        print(f"{r}: {', '.join(diff)}")

# Technologies (bounds)
print("\n--- Technologies Bounds (v8 vs v9) ---")
tech_keys = ["c_inv", "c_maint", "gwp_constr", "lifetime", "c_p", "fmin_perc", "fmax_perc", "f_min", "f_max"]
tech_v8 = parse_ampl_dat_simple(os.path.join(v8_dir, "reg_technologies.dat"), tech_keys)
tech_v9 = parse_ampl_dat_simple(os.path.join(v9_dir, "reg_technologies.dat"), tech_keys)

all_tech = set(tech_v8.keys()) | set(tech_v9.keys())
for t in all_tech:
    if t not in tech_v8: continue
    if t not in tech_v9: continue
    
    diff = []
    for k in ["fmin_perc", "fmax_perc", "f_min", "f_max"]:
        v8 = tech_v8[t].get(k)
        v9 = tech_v9[t].get(k)

        # Handle infinity string if present in simple parsing
        if str(v8) == "Infinity": v8 = float('inf')
        if str(v9) == "Infinity": v9 = float('inf')

        # Compare floats
        if isinstance(v8, (int, float)) and isinstance(v9, (int, float)):
             if abs(v8 - v9) > 1e-6:
                 diff.append(f"{k}: {v8}->{v9}")
        elif v8 != v9:
             diff.append(f"{k}: {v8}->{v9}")

    if diff:
        print(f"{t}: {', '.join(diff)}")

# Consumption
print("\n--- Year Balance Consumption (Negative Values) ---")
def load_bal(d):
    p = os.path.join(d, "outputs", "Year_balance.csv")
    if os.path.exists(p): return pd.read_csv(p, index_col=0)
    return None

df8 = load_bal(v8_dir)
df9 = load_bal(v9_dir)

if df8 is not None and df9 is not None:
    resources = ["GASOLINE", "DIESEL", "LFO", "JET_FUEL", "WOOD", "WET_BIOMASS", "Co2_LFO", "Co2_Diesel"]
    # Add any column present in either
    cols = set(df8.columns) | set(df9.columns)
    
    check_list = [c for c in cols if any(x in c for x in ["GASOLINE", "DIESEL", "LFO", "WOOD", "BIO", "OIL"])]
    
    print(f"{'Resource':<20} {'v8 Cons':<15} {'v9 Cons':<15} {'Diff':<15}")
    for res in sorted(check_list):
        c8 = 0
        c9 = 0
        if res in df8.columns:
            # Sum negative values
            c8 = df8[res][df8[res] < -0.1].sum()
        if res in df9.columns:
            c9 = df9[res][df9[res] < -0.1].sum()
        
        if abs(c8 - c9) > 1:
             print(f"{res:<20} {c8:<15.1f} {c9:<15.1f} {c9-c8:<15.1f}")

    print("\n--- Detailed Tech Consumption Changes ---")
    # Identify Techs causing the drop in LFO/WOOD/DIESEL
    target_res = ["LFO", "WOOD", "DIESEL", "GASOLINE"]
    for r in target_res:
        if r not in df8.columns or r not in df9.columns: continue
        
        print(f"\nResource: {r}")
        # Get techs consuming in v8
        s8 = df8[r][df8[r] < -1]
        s9 = df9[r][df9[r] < -1]
        
        all_t = set(s8.index) | set(s9.index)
        for t in all_t:
            v8_val = s8.get(t, 0)
            v9_val = s9.get(t, 0)
            if abs(v9_val - v8_val) > 10:
                print(f"  {t:<30} v8: {v8_val:.1f}  v9: {v9_val:.1f}  Diff: {v9_val - v8_val:.1f}")

else:
    print("Could not load Year_balance.csv for one or both versions.")
