"""
Quick sanity check: verify that the restored 937940b inputs can be read
and processed through the pipeline without errors (no AMPL solve).
"""
import sys
from pathlib import Path

workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

import pandas as pd
from esmc import Esmc

config = {
    'case_study': 'calib_2017_finland_sanity',
    'comment': 'Sanity check for restored inputs',
    'regions_names': ['FI'],
    'gwp_limit_overall': None,
    'f_perc': True,
    'year': 2017,
    're_share_primary': None,
}

print("=== Sanity Check: 937940b Inputs ===\n")

# Step 1: Verify CSV reading
print("[1] Reading FI/Technologies.csv...")
tech = pd.read_csv(workspace_root / 'Data/2017/FI/Technologies.csv', sep=',', header=[0], index_col=[0])
print(f"    Shape: {tech.shape}")
print(f"    Columns: {list(tech.columns)}")
print(f"    Dtypes:\n{tech.dtypes}")
print(f"    Index unique: {tech.index.is_unique}")
print(f"    Sample (first 5):\n{tech.head()}\n")

print("[2] Reading FI/Resources.csv...")
res = pd.read_csv(workspace_root / 'Data/2017/FI/Resources.csv', sep=',', header=[0], index_col=[0])
print(f"    Shape: {res.shape}")
print(f"    Columns: {list(res.columns)}")
print(f"    Index unique: {res.index.is_unique}")
print(f"    Sample (first 5):\n{res.head()}\n")

# Step 2: Full pipeline up to print_data
print("[3] Initializing Esmc...")
my_model = Esmc(config, nbr_td=12)

print("[4] read_data_indep()...")
my_model.read_data_indep()

print("[5] init_regions()...")
my_model.init_regions()

# Verify the merged Technologies
tech_merged = my_model.regions['FI'].data['Technologies']
print(f"\n[6] Merged Technologies shape: {tech_merged.shape}")
print(f"    f_min dtype: {tech_merged['f_min'].dtype}")
print(f"    f_max dtype: {tech_merged['f_max'].dtype}")
print(f"    fmin_perc dtype: {tech_merged['fmin_perc'].dtype}")
print(f"    fmax_perc dtype: {tech_merged['fmax_perc'].dtype}")

# Check for string contamination
for col in ['f_min', 'f_max', 'fmin_perc', 'fmax_perc']:
    non_numeric = tech_merged[col].apply(lambda x: not isinstance(x, (int, float)))
    if non_numeric.any():
        print(f"    WARNING: {col} has non-numeric values: {tech_merged[col][non_numeric]}")
    else:
        print(f"    ✓ {col} all numeric")

# Verify Resources
res_merged = my_model.regions['FI'].data['Resources']
print(f"\n[7] Merged Resources shape: {res_merged.shape}")
for col in ['avail_local', 'avail_exterior', 'c_op_local']:
    if col in res_merged.columns:
        print(f"    {col} dtype: {res_merged[col].dtype}, max: {res_merged[col].max():.2f}")

print("\n[8] init_ta (kmedoid)...")
my_model.init_ta(algo='kmedoid')

print("[9] print_td_data()...")
my_model.print_td_data()

print("[10] print_data(indep=True)...")
my_model.print_data(indep=True)

# Verify generated .dat files
cs_dir = my_model.cs_dir
print(f"\n[11] Case study dir: {cs_dir}")
for f in sorted(cs_dir.glob('*.dat')):
    print(f"    {f.name}: {f.stat().st_size} bytes")

# Quick check of reg_technologies.dat for NUCLEAR
reg_tech_dat = cs_dir / 'reg_technologies.dat'
if reg_tech_dat.exists():
    content = reg_tech_dat.read_text()
    # Find NUCLEAR line
    for line in content.split('\n'):
        if 'NUCLEAR' in line and 'SMR' not in line:
            print(f"\n[12] NUCLEAR in reg_technologies.dat: {line.strip()}")
            break

print("\n=== Sanity check complete ===")
