"""Analyze unconstrained technologies and calibration gaps."""
import pandas as pd
import numpy as np

ref = pd.read_csv('Data/2017/02_REF_REGION/Technologies.csv')
fi = pd.read_csv('Data/2017/FI/Technologies.csv')
fi_techs = fi['Technologies param'].tolist()

# Convert f_max to numeric
ref['f_max'] = pd.to_numeric(ref['f_max'], errors='coerce')
ref['f_min'] = pd.to_numeric(ref['f_min'], errors='coerce')

# Techs with huge f_max and no FI override  
huge = ref[(ref['f_max'] >= 1e14) & (~ref['Technologies param'].isin(fi_techs))]
print(f'=== Techs with f_max >= 1e14 and NO FI override: {len(huge)} ===')
for r in huge['Technologies param'].tolist():
    print(f'  {r}')

# Assets from rerun showing absurd values
assets = pd.read_csv('case_studies/FI/calib_2017_finland_v5_fperc_repro/outputs/Assets.csv')
assets.rename(columns={assets.columns[0]: 'item'}, inplace=True)
cap_col = assets.columns[1]

absurd = assets[assets[cap_col] > 100]  # > 100 GW is clearly wrong for Finland
print(f'\n=== Technologies deployed at > 100 GW (absurd): {len(absurd)} ===')
for _, r in absurd.iterrows():
    print(f'  {r["item"]:35s} {r[cap_col]:.2e} GW')

# Show what the demands are
print('\n=== Key demands (GWh or Mpkm/Mtkm) ===')
d = pd.read_csv('Data/2017/FI/Demands.csv')
for _, row in d.iterrows():
    total = 0
    for c in ['HOUSEHOLDS','SERVICES','INDUSTRY','TRANSPORTATION']:
        if c in d.columns:
            try:
                total += float(row[c])
            except:
                pass
    print(f'  {row["parameter name"]:25s} {total:12.1f}')

print('\n=== FI-overridden techs with their bounds ===')
for _, r in fi.iterrows():
    print(f'  {r["Technologies param"]:25s} f_min={r["f_min"]:<10} f_max={r["f_max"]:<12} fmin_perc={r["fmin_perc"]:<6} fmax_perc={r["fmax_perc"]:<6}')
