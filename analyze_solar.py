import pandas as pd
import os

out = os.path.join('case_studies', 'FI', 'manual_runs', '20260319_164846__v28d_coal_gentle', 'outputs')
yb = pd.read_csv(os.path.join(out, 'year_balance.csv'), index_col=0)
assets = pd.read_csv(os.path.join(out, 'assets.csv'), index_col=0)

# --- 1. Solar tech rows ---
solar_techs = [t for t in yb.index if 'SOLAR' in t.upper() or 'PV' in t.upper() or 'PT_' in t.upper() or 'ST_' in t.upper()]
print('=== Solar-related technology rows ===')
for t in solar_techs:
    row = yb.loc[t]
    nz = row[row.abs() > 0.01]
    print(f'\n{t}:')
    for col, val in nz.items():
        print(f'  {col:30s} {val:10.3f}')

# --- 2. RES_SOLAR row (resource) ---
solar_res = [r for r in yb.index if 'RES_SOLAR' in str(r).upper() or r == 'SOLAR']
print(f'\n=== Solar resource rows: {solar_res} ===')
for r in solar_res:
    row = yb.loc[r]
    nz = row[row.abs() > 0.01]
    print(f'\n{r}:')
    for col, val in nz.items():
        print(f'  {col:30s} {val:10.3f}')

# --- 3. All columns in year_balance ---
print(f'\n=== All energy carriers (columns of year_balance) ===')
print(list(yb.columns))

# --- 4. Assets for solar techs ---
print('\n=== Solar tech installed capacities ===')
for t in solar_techs:
    if t in assets.index:
        cols = ['F', 'F_year'] + [c for c in ['c_p_max', 'f_min', 'f_max'] if c in assets.columns]
        print(f'{t}: {assets.loc[t][["F","F_year"]].to_dict()}')

# --- 5. What's in "primary energy" resources rows ---
# In EnergyScope, primary energy resources are things like WOOD, COAL, GAS, URANIUM, SOLAR, WIND, etc.
# Find all rows that could be resources
print('\n=== Resource rows (likely PE contributors) ===')
resource_like = [r for r in yb.index if r in list(yb.columns)]  # resources == carriers
print(resource_like[:30])
