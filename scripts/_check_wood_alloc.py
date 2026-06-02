import pandas as pd
from pathlib import Path

FOREST_DIR = Path('case_studies/FI/forest_scenarios_2035')

def find_run(scenario, ghg):
    dirs = sorted(FOREST_DIR.glob(f'*__{scenario}__{ghg}'))
    for d in reversed(dirs):
        if (d / 'outputs' / 'TotalCost.csv').exists():
            return d
    return None

WOOD_RESOURCES = ['WOOD_FI1','WOOD_FI2','WOOD_FI3','WOOD_FI4','WOOD_FI5']

scenarios = ['S1_BES', 'S2_NFS', 'S3_BDS']
ghgs = ['unconstrained', 'ghg_95pct', 'ghg_95pct_nonuke']

print('Wood resource use (GWh/yr) — summed across all regions\n')
header = f'{"Scenario":12s}  {"GHG config":25s}  {"FI1 TWh":>8} {"FI2 TWh":>8} {"FI3 TWh":>8} {"FI4 TWh":>8} {"FI5 TWh":>8}  {"TOTAL TWh":>10}'
print(header)
print('-'*len(header))

for s in scenarios:
    for g in ghgs:
        d = find_run(s, g)
        if not d:
            print(f'{s:12s}  {g:25s}  NOT FOUND')
            continue
        res = pd.read_csv(d / 'outputs' / 'Resources.csv', index_col=0)
        # Use R_year_local column (actual consumption, not availability cap)
        row = {}
        for fi in WOOD_RESOURCES:
            matched = [idx for idx in res.index if fi in str(idx)]
            if matched and 'R_year_local' in res.columns:
                row[fi] = float(res.loc[matched, 'R_year_local'].sum())
            else:
                row[fi] = 0.0
        total = sum(row.values())
        vals = '  '.join(f'{row.get(f"WOOD_FI{i}",0)/1000:>8.1f}' for i in range(1,6))
        print(f'{s:12s}  {g:25s}  {vals}  {total/1000:>10.1f}')

print()
print('NOTE: FI5 is RoW import backstop (70 €/MWh, avail_exterior=1e6 GWh)')
