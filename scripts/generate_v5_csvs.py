"""Generate exact v5_fperc FI override CSVs from .dat files (combined param format)."""
import os
import pandas as pd
import math

base = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
cs_dir = os.path.join(base, 'case_studies', 'FI', 'calib_2017_finland_v5_fperc')
ref_dir = os.path.join(base, 'Data', '2017', '02_REF_REGION')
fi_dir = os.path.join(base, 'Data', '2017', 'FI')

# ── Parse Technologies from reg_technologies.dat ──
with open(os.path.join(cs_dir, 'reg_technologies.dat'), 'r') as f:
    lines = f.readlines()

# Header: param :  c_inv  c_maint  gwp_constr  lifetime  c_p  fmin_perc  fmax_perc  f_min  f_max :=
header = lines[0].strip()
# Extract column names between "param :" and ":="
cols_str = header.replace('param :', '').replace(':=', '').strip()
cols = cols_str.split()
print("Tech columns: {}".format(cols))

dat_techs = {}
for line in lines[1:]:
    line = line.strip()
    if not line or line == ';':
        continue
    parts = line.split('\t')
    if len(parts) < 4:
        parts = line.split()
    if parts[0] == 'FI' and len(parts) >= len(cols) + 2:
        tech = parts[1]
        vals = {}
        for j, col in enumerate(cols):
            v = parts[j + 2]
            if v == 'Infinity':
                vals[col] = 1e15
            else:
                vals[col] = float(v)
        dat_techs[tech] = vals

print("Parsed {} FI techs from .dat".format(len(dat_techs)))

# REF data
ref = pd.read_csv(os.path.join(ref_dir, 'Technologies.csv'),
                   skiprows=[1], header=[0], index_col=3)
# Clean index
ref.index = ref.index.str.strip()
print("REF has {} techs".format(len(ref)))

# Find overrides (techs where FI differs from REF)
OVERRIDE_COLS = ['f_min', 'f_max', 'fmin_perc', 'fmax_perc']
overrides = {}
for tech in sorted(dat_techs.keys()):
    vals = dat_techs[tech]
    tech_clean = tech.strip()
    if tech_clean not in ref.index:
        print("  WARNING: {} not in REF, including as override".format(tech_clean))
        overrides[tech_clean] = {c: vals[c] for c in OVERRIDE_COLS}
        continue
    
    diff = False
    for col in OVERRIDE_COLS:
        fi_v = vals.get(col, 0.0)
        ref_v = ref.loc[tech_clean, col] if col in ref.columns else 0.0
        if pd.isna(ref_v):
            ref_v = 0.0
        # Normalize both: Infinity -> 1e15
        if ref_v > 1e14:
            ref_v = 1e15
        if fi_v > 1e14:
            fi_v = 1e15
        if abs(fi_v - ref_v) > 1e-6:
            diff = True
            break
    
    if diff:
        overrides[tech_clean] = {c: vals[c] for c in OVERRIDE_COLS}

print("\n=== Technologies.csv ({} overrides) ===".format(len(overrides)))
tech_lines = ['Technologies param,f_min,f_max,fmin_perc,fmax_perc']
for tech in overrides:
    vals = overrides[tech]
    f_min = vals['f_min']
    f_max = vals['f_max'] if vals['f_max'] < 1e14 else 100000.0
    fmin_p = vals['fmin_perc']
    fmax_p = vals['fmax_perc']
    row = "{},{},{},{},{}".format(tech, f_min, f_max, fmin_p, fmax_p)
    tech_lines.append(row)
    print("  " + row)

# ── Parse Resources from reg_resources.dat ──
with open(os.path.join(cs_dir, 'reg_resources.dat'), 'r') as f:
    rlines = f.readlines()

# Find the param line  
rheader = rlines[0].strip()
rcols_str = rheader.replace('param :', '').replace(':=', '').strip()
rcols = rcols_str.split()
print("\nResource columns: {}".format(rcols))

dat_res = {}
for line in rlines[1:]:
    line = line.strip()
    if not line or line == ';':
        continue
    parts = line.split('\t')
    if len(parts) < 4:
        parts = line.split()
    if parts[0] == 'FI' and len(parts) >= len(rcols) + 2:
        res = parts[1]
        vals = {}
        for j, col in enumerate(rcols):
            v = parts[j + 2]
            if v == 'Infinity':
                vals[col] = 1e15
            else:
                vals[col] = float(v)
        dat_res[res] = vals

print("Parsed {} FI resources from .dat".format(len(dat_res)))

ref_r = pd.read_csv(os.path.join(ref_dir, 'Resources.csv'), header=[2], index_col=[2]).dropna(axis=1, how='all')
ref_r.index = ref_r.index.str.strip()

RES_COLS = ['avail_local', 'c_op_local', 'avail_exterior']
res_overrides = {}
for res in sorted(dat_res.keys()):
    vals = dat_res[res]
    res_clean = res.strip()
    if res_clean not in ref_r.index:
        print("  WARNING: {} not in REF, including as override".format(res_clean))
        res_overrides[res_clean] = {c: vals.get(c, 0.0) for c in RES_COLS}
        continue
    
    diff = False
    for col in RES_COLS:
        fi_v = vals.get(col, 0.0)
        ref_v = ref_r.loc[res_clean, col] if col in ref_r.columns else 0.0
        if pd.isna(ref_v):
            ref_v = 0.0
        if ref_v > 1e14:
            ref_v = 1e15
        if fi_v > 1e14:
            fi_v = 1e15
        if abs(fi_v - ref_v) > 1e-6:
            diff = True
            break
    
    if diff:
        res_overrides[res_clean] = {c: vals.get(c, 0.0) for c in RES_COLS}

print("\n=== Resources.csv ({} overrides) ===".format(len(res_overrides)))
res_lines = [',avail_local,c_op_local,avail_exterior']
for res in res_overrides:
    vals = res_overrides[res]
    al = vals['avail_local']
    cop = vals['c_op_local']
    ae = vals['avail_exterior']
    row = "{},{},{},{}".format(res, al, cop, ae)
    res_lines.append(row)
    print("  " + row)

# ── Write files ──
tech_csv = '\n'.join(tech_lines) + '\n'
res_csv = '\n'.join(res_lines) + '\n'

with open(os.path.join(fi_dir, 'Technologies.csv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(tech_csv)
print("\nWrote Technologies.csv ({} rows)".format(len(overrides)))

with open(os.path.join(fi_dir, 'Resources.csv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(res_csv)
print("Wrote Resources.csv ({} rows)".format(len(res_overrides)))
