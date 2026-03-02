"""Compare v5 demands with current Demands.csv"""
import pandas as pd

# v5 demands from .dat
dat_lines = open('case_studies/FI/calib_2017_finland_v5_fperc/reg_demands.dat').readlines()
demands_v5 = {}
for line in dat_lines:
    s = line.strip()
    if s.startswith('FI'):
        parts = s.replace(';','').split()
        if len(parts) >= 6:
            demands_v5[parts[1]] = sum(float(x) for x in parts[2:6])

# Current demands
dem_cur = pd.read_csv('Data/2017/FI/Demands.csv')
param_col = [c for c in dem_cur.columns if 'parameter' in c.lower()]
if param_col:
    dem_cur_idx = dem_cur.set_index(param_col[0])
else:
    dem_cur_idx = dem_cur.set_index(dem_cur.columns[2])

num_cols = ['HOUSEHOLDS','SERVICES','INDUSTRY','TRANSPORTATION']
for col in num_cols:
    dem_cur_idx[col] = pd.to_numeric(dem_cur_idx[col], errors='coerce').fillna(0)
dem_cur_idx['Total'] = dem_cur_idx[num_cols].sum(axis=1)

print("Demands comparison (v5 .dat vs current CSV):")
print(f"{'End-use':<25} {'v5 total':>12} {'cur total':>12} {'match':>10}")
print("-" * 65)
all_match = True
for eu, v5_t in sorted(demands_v5.items()):
    eu_strip = eu.strip()
    if eu_strip in dem_cur_idx.index:
        cur_t = dem_cur_idx.loc[eu_strip, 'Total']
        diff_pct = abs(v5_t - cur_t) / max(cur_t, 0.1) * 100
        match = "OK" if diff_pct < 0.1 else f"DIFF {diff_pct:.2f}%"
        if diff_pct >= 0.1:
            all_match = False
        print(f"{eu_strip:<25} {v5_t:>12.1f} {cur_t:>12.1f} {match:>10}")
    else:
        all_match = False
        print(f"{eu_strip:<25} {v5_t:>12.1f} {'N/A':>12} NOT FOUND")

print()
print("VERDICT: Demands MATCH" if all_match else "VERDICT: Demands DIFFER")

# Also check storage_power_to_energy
print()
print("=== Storage Power to Energy ===")
sto_dat = open('case_studies/FI/calib_2017_finland_v5_fperc/reg_storage_power_to_energy.dat').read()
print("v5 .dat content (FI lines):")
for line in sto_dat.splitlines():
    if 'FI' in line:
        print(f"  {line.strip()}")

sto_csv = pd.read_csv('Data/2017/FI/Storage_power_to_energy.csv', index_col=0)
print()
print("Current CSV:")
print(sto_csv.to_string())
