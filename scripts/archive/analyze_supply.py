
import pandas as pd
import os

base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
# Explicit paths to ensure correctness
v8_path = os.path.join(base_path, "case_studies", "FI", "calib_2017_finland_v10_oil_constr") # Use v10 as baseline
v9_path = os.path.join(base_path, "case_studies", "FI", "calib_2017_finland_v11_heat_fix")  # Use v11 as new

print(f"DEBUG: v8_path resolved to: {v8_path}")
print(f"DEBUG: v9_path resolved to: {v9_path}")


def get_supply(folder):
    path = os.path.join(folder, "outputs", "Year_balance.csv")
    if not os.path.exists(path): return None
    try:
        return pd.read_csv(path, index_col=0)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

df8 = get_supply(v8_path)
df9 = get_supply(v9_path)

targets = [
    "SHIPPING", "MOB_FREIGHT_ROAD", "MOB_FREIGHT_RAIL", "MOB_FREIGHT_BOAT",
    "MOB_PRIVATE", "MOB_PUBLIC",
    "HEAT_LOW_T_DECEN", "HEAT_LOW_T_DHN", "HEAT_HIGH_T",
    "ELECTRICITY",
    "MOBILITY_PASSENGER", "MOBILITY_FREIGHT"
]

all_cols = set()
if df8 is not None: all_cols.update(df8.columns)
if df9 is not None: all_cols.update(df9.columns)

for target in targets:
    if target not in all_cols:
        continue

    print(f"\n--- Supplying {target} ---")
    print(f"{'Tech':<30} {'v8':<15} {'v9':<15} {'Diff':<15}")
    
    techs = set()
    if df8 is not None and target in df8.columns:
        s = df8[target]
        techs.update(s[s > 1.0].index)
    if df9 is not None and target in df9.columns:
        s = df9[target]
        techs.update(s[s > 1.0].index)
        
    v8_sum = 0
    v9_sum = 0
    
    for t in sorted(techs):
        v8_val = df8[target].get(t, 0) if (df8 is not None and target in df8.columns) else 0
        v9_val = df9[target].get(t, 0) if (df9 is not None and target in df9.columns) else 0
        
        if v8_val > 1.0 or v9_val > 1.0:
            print(f"{t:<30} {v8_val:<15.1f} {v9_val:<15.1f} {v9_val-v8_val:<15.1f}")
        
        if v8_val > 0: v8_sum += v8_val
        if v9_val > 0: v9_sum += v9_val
    
    print(f"{'TOTAL':<30} {v8_sum:<15.1f} {v9_sum:<15.1f} {v9_sum-v8_sum:<15.1f}")
