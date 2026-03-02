"""
Reverse-engineer the FI Technologies.csv override that produced
calib_2017_finland/reg_technologies.dat by comparing .dat values
against 02_REF_REGION/Technologies.csv defaults.
"""
import pandas as pd
from pathlib import Path

ws = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")

# 1. Read REF_REGION defaults
ref = pd.read_csv(ws / 'Data/2017/02_REF_REGION/Technologies.csv',
                   sep=',', header=[0], index_col=[3], skiprows=[1])
ref.index = ref.index.str.strip()
ref.columns = ref.columns.str.strip()

# 2. Parse reg_technologies.dat
dat_path = ws / 'case_studies/FI/calib_2017_finland/reg_technologies.dat'
dat_lines = dat_path.read_text().splitlines()

# Columns in .dat: c_inv c_maint gwp_constr lifetime c_p fmin_perc fmax_perc f_min f_max
dat_cols = ['c_inv', 'c_maint', 'gwp_constr', 'lifetime', 'c_p', 'fmin_perc', 'fmax_perc', 'f_min', 'f_max']
dat_rows = {}
for line in dat_lines:
    line = line.strip()
    if line.startswith('FI'):
        parts = line.split()
        tech = parts[1]
        vals = parts[2:]
        if len(vals) >= 9:
            row = {}
            for i, col in enumerate(dat_cols):
                v = vals[i]
                if v == 'Infinity':
                    row[col] = 1e15
                else:
                    row[col] = float(v)
            dat_rows[tech] = row

dat_df = pd.DataFrame(dat_rows).T
dat_df.index.name = 'Technologies param'

# 3. Compare f_min, f_max, fmin_perc, fmax_perc against REF defaults
override_cols = ['f_min', 'f_max', 'fmin_perc', 'fmax_perc']
overrides = {}

for tech in dat_df.index:
    if tech in ref.index:
        diffs = {}
        for col in override_cols:
            dat_val = dat_df.at[tech, col]
            ref_val = float(ref.at[tech, col]) if col in ref.columns else (0.0 if 'min' in col else 1.0)
            # REF f_max is 1e15 for most techs, stored as "1.00E+15"
            try:
                ref_val = float(ref_val)
            except:
                ref_val = 1e15
            
            if abs(dat_val - ref_val) > 0.001:
                diffs[col] = dat_val
        
        if diffs:
            overrides[tech] = diffs
    else:
        print(f"WARNING: {tech} not in REF (storage or other)")

# 4. Print what must be in the FI override
print("=" * 80)
print("Technologies that need FI override (differ from REF_REGION defaults)")
print("=" * 80)
print(f"\n{'Technology':<30} {'f_min':>8} {'f_max':>12} {'fmin_perc':>10} {'fmax_perc':>10}")
print("-" * 72)

for tech, diffs in sorted(overrides.items()):
    parts = [f"{tech:<30}"]
    for col in override_cols:
        if col in diffs:
            v = diffs[col]
            if v >= 1e14:
                parts.append(f"{'Inf':>12}" if 'max' in col and 'perc' not in col else f"{v:>10.4f}")
            else:
                parts.append(f"{v:>12.4f}" if 'max' in col and 'perc' not in col else f"{v:>10.4f}")
        else:
            parts.append(f"{'(ref)':>12}" if ('max' in col and 'perc' not in col) else f"{'(ref)':>10}")
    print(" ".join(parts))

# 5. Generate the reconstructed FI Technologies.csv
print("\n\n" + "=" * 80)
print("Reconstructed FI Technologies.csv content:")
print("=" * 80)
csv_lines = ["Technologies param,f_min,f_max,fmin_perc"]
for tech in dat_df.index:
    if tech in ref.index:
        diffs = {}
        for col in override_cols:
            dat_val = dat_df.at[tech, col]
            try:
                ref_val = float(ref.at[tech, col])
            except:
                ref_val = 1e15 if 'max' in col and 'perc' not in col else (0.0 if 'min' in col else 1.0)
            if abs(dat_val - ref_val) > 0.001:
                diffs[col] = dat_val
        
        if diffs:
            f_min = dat_df.at[tech, 'f_min']
            f_max = dat_df.at[tech, 'f_max']
            fmin_perc = dat_df.at[tech, 'fmin_perc']
            # Convert Infinity back
            if f_max >= 1e14:
                f_max_str = str(f_max)  
            else:
                f_max_str = str(f_max)
            csv_lines.append(f"{tech},{f_min},{f_max_str},{fmin_perc}")

print("\n".join(csv_lines))
