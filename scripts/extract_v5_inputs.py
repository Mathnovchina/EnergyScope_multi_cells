"""
Extract v5_fperc inputs from .dat files by comparing against REF_REGION defaults.
Produces the FI override CSVs that were used for the v5_fperc run.
"""
import pandas as pd
import json
from pathlib import Path

ws = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")
v5_dir = ws / "case_studies/FI/calib_2017_finland_v5_fperc"

# ============================================================
# 1) Parse reg_technologies.dat
# ============================================================
dat_path = v5_dir / "reg_technologies.dat"
lines = open(dat_path).readlines()

tech_cols = ['c_inv', 'c_maint', 'gwp_constr', 'lifetime', 'c_p',
             'fmin_perc', 'fmax_perc', 'f_min', 'f_max']
techs = {}
for line in lines:
    line = line.strip()
    if line.startswith('FI'):
        parts = line.split()
        if len(parts) >= 11:
            tech = parts[1]
            vals = parts[2:]
            row = {}
            for i, col in enumerate(tech_cols):
                v = vals[i] if i < len(vals) else '0'
                row[col] = float(v) if v != 'Infinity' else 1e15
            techs[tech] = row

dat_tech = pd.DataFrame(techs).T
dat_tech.index.name = 'Technology'

# ============================================================
# 2) Parse REF Technologies
# ============================================================
ref = pd.read_csv(ws / 'Data/2017/02_REF_REGION/Technologies.csv',
                  skiprows=[1], header=[0], index_col=3)
ref.index = ref.index.str.strip()
for c in tech_cols:
    if c in ref.columns:
        ref[c] = pd.to_numeric(ref[c], errors='coerce')

# ============================================================
# 3) Find FI overrides for Technologies
# ============================================================
override_cols = ['f_min', 'f_max', 'fmin_perc', 'fmax_perc']
tech_overrides = {}

for tech in dat_tech.index:
    if tech in ref.index:
        diffs = {}
        for col in override_cols:
            dat_val = dat_tech.at[tech, col]
            ref_val = ref.at[tech, col] if col in ref.columns else (0.0 if 'min' in col else 1.0)
            if pd.isna(ref_val):
                ref_val = 0.0 if 'min' in col else 1.0
            ref_val = float(ref_val)
            if abs(dat_val - ref_val) > 0.0001:
                diffs[col] = dat_val
        if diffs:
            tech_overrides[tech] = {c: dat_tech.at[tech, c] for c in override_cols}
            tech_overrides[tech]['_changed'] = list(diffs.keys())

print("=" * 90)
print(f"TECHNOLOGIES: {len(dat_tech)} total in .dat, {len(tech_overrides)} FI overrides")
print("=" * 90)
hdr = f"{'Technology':<30} {'f_min':>10} {'f_max':>12} {'fmin_perc':>10} {'fmax_perc':>10}  changed"
print(hdr)
print("-" * 90)
for tech in sorted(tech_overrides.keys()):
    vals = tech_overrides[tech]
    fmax = vals['f_max']
    fmax_s = f"{fmax:.4f}" if fmax < 1e14 else "Inf"
    changed = vals['_changed']
    print(f"{tech:<30} {vals['f_min']:>10.4f} {fmax_s:>12} {vals['fmin_perc']:>10.4f} {vals['fmax_perc']:>10.4f}  {changed}")

# ============================================================
# 4) Parse reg_resources.dat
# ============================================================
res_path = v5_dir / "reg_resources.dat"
res_lines = open(res_path).readlines()

res_cols = ['avail_local', 'avail_exterior', 'gwp_op_local', 'c_op_local']
resources = {}
for line in res_lines:
    line = line.strip()
    if line.startswith('FI'):
        parts = line.split()
        if len(parts) >= 6:
            res_name = parts[1]
            vals = parts[2:]
            row = {}
            for i, col in enumerate(res_cols):
                v = vals[i] if i < len(vals) else '0'
                row[col] = float(v) if v != 'Infinity' else 1e15
            resources[res_name] = row

dat_res = pd.DataFrame(resources).T
dat_res.index.name = 'Resource'

# Parse REF Resources
ref_res_raw = pd.read_csv(ws / 'Data/2017/02_REF_REGION/Resources.csv', skiprows=[1], header=[0])
# Columns: Category, Subcategory, parameter name, avail_local, avail_exterior, gwp_op_local, c_op_local, Comment
ref_res = ref_res_raw.copy()
ref_res.columns = ['Category', 'Subcategory', 'param_name', 'avail_local', 'avail_exterior', 'gwp_op_local', 'c_op_local', 'Comment'][:len(ref_res.columns)]
ref_res = ref_res.set_index('param_name')
ref_res.index = ref_res.index.str.strip()
for c in res_cols:
    if c in ref_res.columns:
        ref_res[c] = pd.to_numeric(ref_res[c], errors='coerce')

# Find FI resource overrides
res_override_cols = ['avail_local', 'c_op_local', 'avail_exterior']
res_overrides = {}
for res_name in dat_res.index:
    if res_name in ref_res.index:
        diffs = {}
        for col in res_override_cols:
            dat_val = dat_res.at[res_name, col]
            ref_val = ref_res.at[res_name, col] if col in ref_res.columns else 0.0
            if pd.isna(ref_val):
                ref_val = 0.0
            ref_val = float(ref_val)
            if abs(dat_val - ref_val) > 0.0001:
                diffs[col] = dat_val
        if diffs:
            res_overrides[res_name] = {c: dat_res.at[res_name, c] for c in res_override_cols}
            res_overrides[res_name]['_changed'] = list(diffs.keys())
    else:
        # Resource in .dat but not in REF — might be from FI override
        pass

print()
print("=" * 90)
print(f"RESOURCES: {len(dat_res)} total in .dat, {len(res_overrides)} FI overrides")
print("=" * 90)
hdr = f"{'Resource':<20} {'avail_local':>15} {'c_op_local':>12} {'avail_ext':>15}  changed"
print(hdr)
print("-" * 80)
for res_name in sorted(res_overrides.keys()):
    vals = res_overrides[res_name]
    avail_ext = vals['avail_exterior']
    avail_ext_s = f"{avail_ext:.2f}" if avail_ext < 1e14 else "Inf"
    avail_loc = vals['avail_local']
    avail_loc_s = f"{avail_loc:.2f}" if avail_loc < 1e14 else "Inf"
    changed = vals['_changed']
    print(f"{res_name:<20} {avail_loc_s:>15} {vals['c_op_local']:>12.6f} {avail_ext_s:>15}  {changed}")

# ============================================================
# 5) Parse reg_misc.dat for FI-specific misc params
# ============================================================
misc_path = v5_dir / "reg_misc.dat"
misc_lines = open(misc_path).readlines()

print()
print("=" * 90)
print("MISC PARAMS (reg_misc.dat — FI region)")
print("=" * 90)

# Look for key parameters
in_param = False
current_param = ""
misc_params = {}
for line in misc_lines:
    stripped = line.strip()
    if stripped.startswith("param "):
        # e.g. "param share_heat_dhn_min :="
        parts = stripped.split()
        if len(parts) >= 2:
            current_param = parts[1]
            in_param = True
    elif in_param and stripped.startswith("FI"):
        parts = stripped.replace(";", "").split()
        if len(parts) >= 2:
            val = parts[1]
            misc_params[current_param] = val
            in_param = False
    elif stripped == ";":
        in_param = False

for k, v in sorted(misc_params.items()):
    print(f"  {k:<40} = {v}")

# ============================================================
# 6) Parse reg_demands.dat
# ============================================================
demands_path = v5_dir / "reg_demands.dat"
dem_lines = open(demands_path).readlines()

print()
print("=" * 90)
print("DEMANDS (reg_demands.dat)")
print("=" * 90)

demands = {}
for line in dem_lines:
    stripped = line.strip()
    if stripped.startswith("FI"):
        parts = stripped.replace(";", "").split()
        if len(parts) >= 6:
            end_use = parts[1]
            # sectors: households, services, industry, transportation
            vals = parts[2:]
            demands[end_use] = [float(v) for v in vals[:4]]

if demands:
    dem_df = pd.DataFrame(demands, index=['Households', 'Services', 'Industry', 'Transportation']).T
    dem_df['Total'] = dem_df.sum(axis=1)
    print(dem_df.to_string())

# ============================================================
# 7) Write reconstructed FI Technologies.csv
# ============================================================
print()
print("=" * 90)
print("RECONSTRUCTED FI/Technologies.csv")
print("=" * 90)
csv_lines = ["Technologies param,f_min,f_max,fmin_perc,fmax_perc"]
for tech in sorted(tech_overrides.keys()):
    vals = tech_overrides[tech]
    fmin = vals['f_min']
    fmax = vals['f_max']
    fminp = vals['fmin_perc']
    fmaxp = vals['fmax_perc']
    csv_lines.append(f"{tech},{fmin},{fmax},{fminp},{fmaxp}")

for line in csv_lines:
    print(line)

# ============================================================
# 8) Write reconstructed FI Resources.csv
# ============================================================
print()
print("=" * 90)
print("RECONSTRUCTED FI/Resources.csv")
print("=" * 90)
res_csv_lines = [",avail_local,c_op_local,avail_exterior"]
for res_name in sorted(res_overrides.keys()):
    vals = res_overrides[res_name]
    avail_loc = vals['avail_local']
    c_op = vals['c_op_local']
    avail_ext = vals['avail_exterior']
    res_csv_lines.append(f"{res_name},{avail_loc},{c_op},{avail_ext}")

for line in res_csv_lines:
    print(line)

# ============================================================
# 9) Check outputs
# ============================================================
print()
print("=" * 90)
print("V5 OUTPUTS SUMMARY")
print("=" * 90)
out_dir = v5_dir / "outputs"
tc = pd.read_csv(out_dir / "TotalCost.csv", index_col=0)
print(f"Total cost: {tc.iloc[0,0]:,.0f} M€/y")
obj = pd.read_csv(out_dir / "Objective.csv", index_col=0)
print(f"Objective:  {obj.iloc[0,0]:,.0f} M€/y")

# Key resources
res_out = pd.read_csv(out_dir / "Resources.csv", index_col=0)
used = res_out[(res_out['R_year_local'].abs() > 1) | (res_out['R_year_exterior'].abs() > 1)]
print("\nResources consumed:")
for idx in used.index:
    loc = used.at[idx, 'R_year_local']
    ext = used.at[idx, 'R_year_exterior']
    total = loc + ext
    print(f"  {idx:<20} local={loc:>12.1f}  exterior={ext:>12.1f}  total={total:>12.1f}")

# Key assets
assets = pd.read_csv(out_dir / "Assets.csv", index_col=0)
nz = assets[assets['F'].abs() > 0.001]
print(f"\nNon-zero assets: {len(nz)}")
for idx in nz.index:
    f = nz.at[idx, 'F']
    print(f"  {idx:<30} F={f:>10.4f} GW")
