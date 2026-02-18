"""
Verify that the reconstructed FI inputs produce .dat files matching
the original calib_2017_finland case study.
"""
import sys
from pathlib import Path

workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc

config = {
    'case_study': 'calib_2017_finland_verify',
    'comment': 'Verification of reconstructed Feb14 inputs',
    'regions_names': ['FI'],
    'gwp_limit_overall': None,
    'f_perc': True,
    'year': 2017,
    're_share_primary': None,
}

print("=== Verification: Reconstructed Inputs ===\n")

my_model = Esmc(config, nbr_td=12)
my_model.read_data_indep()
my_model.init_regions()
my_model.init_ta(algo='kmedoid')
my_model.print_td_data()
my_model.print_data(indep=True)

cs_dir = my_model.cs_dir
orig_dir = workspace_root / 'case_studies/FI/calib_2017_finland'

# Compare reg_technologies.dat
print("\n=== Comparing reg_technologies.dat ===")
orig_tech = (orig_dir / 'reg_technologies.dat').read_text().splitlines()
new_tech = (cs_dir / 'reg_technologies.dat').read_text().splitlines()

tech_diffs = 0
for i, (o, n) in enumerate(zip(orig_tech, new_tech)):
    if o.strip() != n.strip():
        tech_diffs += 1
        if tech_diffs <= 10:
            print(f"Line {i+1}:")
            print(f"  ORIG: {o.strip()}")
            print(f"  NEW:  {n.strip()}")
if tech_diffs == 0:
    print("PERFECT MATCH!")
else:
    print(f"\n{tech_diffs} lines differ")

# Compare reg_resources.dat
print("\n=== Comparing reg_resources.dat ===")
orig_res = (orig_dir / 'reg_resources.dat').read_text().splitlines()
new_res = (cs_dir / 'reg_resources.dat').read_text().splitlines()

res_diffs = 0
for i, (o, n) in enumerate(zip(orig_res, new_res)):
    if o.strip() != n.strip():
        res_diffs += 1
        if res_diffs <= 10:
            print(f"Line {i+1}:")
            print(f"  ORIG: {o.strip()}")
            print(f"  NEW:  {n.strip()}")
if res_diffs == 0:
    print("PERFECT MATCH!")
else:
    print(f"\n{res_diffs} lines differ")

print("\n=== Verification complete ===")
