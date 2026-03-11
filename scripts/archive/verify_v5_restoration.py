"""Verify restored v5_fperc inputs: replicate pipeline merge and compare against v5 .dat ground truth."""
import os
import pandas as pd
import numpy as np

base = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
ref_dir = os.path.join(base, 'Data', '2017', '02_REF_REGION')
fi_dir = os.path.join(base, 'Data', '2017', 'FI')
cs_dir = os.path.join(base, 'case_studies', 'FI', 'calib_2017_finland_v5_fperc')

def clean_idx(df):
    df.index = df.index.astype(str).str.strip()
    return df

# ── Step 1: Replicate pipeline merge for Technologies ──
# REF: header=[0], index_col=[3], skiprows=[1]
ref_tech = pd.read_csv(os.path.join(ref_dir, 'Technologies.csv'),
                        skiprows=[1], header=[0], index_col=3)
ref_tech = clean_idx(ref_tech)

# FI: header=[0], index_col=[0]  
fi_tech = pd.read_csv(os.path.join(fi_dir, 'Technologies.csv'),
                       header=[0], index_col=0)
fi_tech = clean_idx(fi_tech)

# Apply update (as pipeline does)
merged_tech = ref_tech.copy()
merged_tech.update(fi_tech)

# ── Step 2: Parse v5 .dat ground truth ──
with open(os.path.join(cs_dir, 'reg_technologies.dat'), 'r') as f:
    lines = f.readlines()
header = lines[0].strip().replace('param :', '').replace(':=', '').strip().split()
dat_techs = {}
for line in lines[1:]:
    line = line.strip()
    if not line or line == ';':
        continue
    parts = line.split('\t')
    if parts[0] == 'FI':
        tech = parts[1].strip()
        vals = {}
        for j, col in enumerate(header):
            v = parts[j + 2]
            vals[col] = 1e15 if v == 'Infinity' else float(v)
        dat_techs[tech] = vals

# ── Step 3: Compare ──
print("=" * 70)
print("TECHNOLOGIES: pipeline merge vs v5 .dat (f_min/f_max/fmin_perc/fmax_perc)")
print("=" * 70)
tech_mismatches = 0
for tech, dat_vals in sorted(dat_techs.items()):
    for col in ['f_min', 'f_max', 'fmin_perc', 'fmax_perc']:
        dat_v = dat_vals[col]
        if dat_v > 1e14:
            dat_v = 1e15

        if tech in merged_tech.index and col in merged_tech.columns:
            pipe_v = merged_tech.loc[tech, col]
            if pd.isna(pipe_v):
                pipe_v = 0.0
            if pipe_v > 1e14:
                pipe_v = 1e15
            if abs(dat_v - pipe_v) > 1e-4:
                print("  MISMATCH %s.%s: dat=%.6g pipeline=%.6g" % (tech, col, dat_v, pipe_v))
                tech_mismatches += 1

if tech_mismatches == 0:
    print("  ALL %d techs MATCH" % len(dat_techs))
else:
    print("  %d mismatches" % tech_mismatches)

# ── Step 4: Replicate pipeline merge for Resources ──
# REF: header=[2], index_col=[2]
ref_res = pd.read_csv(os.path.join(ref_dir, 'Resources.csv'),
                       header=[2], index_col=[2]).dropna(axis=1, how='all')
ref_res = clean_idx(ref_res)

# FI: header=[0], index_col=[0]
fi_res = pd.read_csv(os.path.join(fi_dir, 'Resources.csv'),
                      header=[0], index_col=[0]).dropna(axis=1, how='all')
fi_res = clean_idx(fi_res)

merged_res = ref_res.copy()
merged_res.update(fi_res)

# ── Step 5: Parse v5 resources .dat ──
with open(os.path.join(cs_dir, 'reg_resources.dat'), 'r') as f:
    rlines = f.readlines()
rheader = rlines[0].strip().replace('param :', '').replace(':=', '').strip().split()
dat_res = {}
for line in rlines[1:]:
    line = line.strip()
    if not line or line == ';':
        continue
    parts = line.split('\t')
    if parts[0] == 'FI':
        res = parts[1].strip()
        vals = {}
        for j, col in enumerate(rheader):
            v = parts[j + 2]
            vals[col] = 1e15 if v == 'Infinity' else float(v)
        dat_res[res] = vals

# ── Step 6: Compare ──
print("\n" + "=" * 70)
print("RESOURCES: pipeline merge vs v5 .dat (avail_local/c_op_local/avail_exterior)")
print("=" * 70)
res_mismatches = 0
for res, dat_vals in sorted(dat_res.items()):
    for col in ['avail_local', 'c_op_local', 'avail_exterior']:
        dat_v = dat_vals[col]
        if dat_v > 1e14:
            dat_v = 1e15

        if res in merged_res.index and col in merged_res.columns:
            pipe_v = merged_res.loc[res, col]
            if pd.isna(pipe_v):
                pipe_v = 0.0
            if pipe_v > 1e14:
                pipe_v = 1e15
            if abs(dat_v - pipe_v) > 1e-4:
                print("  MISMATCH %s.%s: dat=%.6g pipeline=%.6g" % (res, col, dat_v, pipe_v))
                res_mismatches += 1
        else:
            print("  MISSING %s.%s" % (res, col))
            res_mismatches += 1

if res_mismatches == 0:
    print("  ALL %d resources MATCH" % len(dat_res))
else:
    print("  %d mismatches" % res_mismatches)

# ── Verdict ──
total = tech_mismatches + res_mismatches
print("\n" + "=" * 70)
if total == 0:
    print("VERDICT: PERFECT MATCH — restored CSVs reproduce v5_fperc .dat values")
else:
    print("VERDICT: %d total mismatches" % total)
