"""
Reverse-engineer FI Resources.csv from calib_2017_finland/reg_resources.dat
by comparing against 02_REF_REGION/Resources.csv defaults.
"""
import pandas as pd
from pathlib import Path

ws = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")

# 1. Read REF_REGION Resources
ref = pd.read_csv(ws / 'Data/2017/02_REF_REGION/Resources.csv',
                   sep=',', header=[2], index_col=[2]).dropna(axis=1, how='all')
ref.index = ref.index.str.strip()
ref.columns = ref.columns.str.strip()
print("REF columns:", list(ref.columns))
print("REF shape:", ref.shape)

# 2. Parse reg_resources.dat
dat_path = ws / 'case_studies/FI/calib_2017_finland/reg_resources.dat'
dat_lines = dat_path.read_text().splitlines()

# Header: avail_local avail_exterior gwp_op_local c_op_local
dat_cols = ['avail_local', 'avail_exterior', 'gwp_op_local', 'c_op_local']
dat_rows = {}
for line in dat_lines:
    line = line.strip()
    if line.startswith('FI'):
        parts = line.rstrip(';').split()
        res = parts[1]
        vals = parts[2:]
        if len(vals) >= 4:
            row = {}
            for i, col in enumerate(dat_cols):
                v = vals[i]
                if v == 'Infinity':
                    row[col] = 1e15
                else:
                    row[col] = float(v)
            dat_rows[res] = row

dat_df = pd.DataFrame(dat_rows).T

# 3. Compare against REF and find overrides
# FI override has columns: avail_local, c_op_local, avail_exterior
fi_cols = ['avail_local', 'c_op_local', 'avail_exterior']
overrides = {}

print("\n" + "=" * 100)
print(f"{'Resource':<25} {'col':<20} {'DAT':>15} {'REF':>15} {'Override?':>10}")
print("-" * 100)

for res in dat_df.index:
    if res in ref.index:
        diffs = {}
        for col in fi_cols:
            dat_val = dat_df.at[res, col]
            ref_val = float(ref.at[res, col])
            if abs(dat_val - ref_val) > 0.0001:
                diffs[col] = dat_val
                print(f"{res:<25} {col:<20} {dat_val:>15.4f} {ref_val:>15.4f} {'YES':>10}")
        if diffs:
            overrides[res] = diffs
    else:
        print(f"{res:<25} NOT IN REF")

# 4. Generate FI Resources.csv
print("\n\n" + "=" * 80)
print("Reconstructed FI Resources.csv:")
print("=" * 80)
csv_lines = [",avail_local,c_op_local,avail_exterior"]
for res, diffs in sorted(overrides.items()):
    avl = diffs.get('avail_local', float(ref.at[res, 'avail_local']) if res in ref.index else 0.0)
    col = diffs.get('c_op_local', float(ref.at[res, 'c_op_local']) if res in ref.index else 0.0)
    ave = diffs.get('avail_exterior', float(ref.at[res, 'avail_exterior']) if res in ref.index else 0.0)
    csv_lines.append(f"{res},{avl},{col},{ave}")

print("\n".join(csv_lines))
