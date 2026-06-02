import pandas as pd
from pathlib import Path

FOREST_DIR = Path('case_studies/FI/forest_scenarios_2035')

def find_run(scenario, ghg):
    dirs = sorted(FOREST_DIR.glob(f'*__{scenario}__{ghg}'))
    for d in reversed(dirs):
        if (d / 'outputs' / 'TotalCost.csv').exists():
            return d
    return None

MOB_LAYERS = ['DIESEL','LFO','JET_FUEL','MOB_FREIGHT_ROAD','MOB_FREIGHT_RAIL',
              'MOB_FREIGHT_BOAT','MOB_PRIVATE','MOB_PUBLIC','AVIATION_LONG_HAUL',
              'AVIATION_SHORT_HAUL','SHIPPING','GASOLINE']

target = find_run('S3_BDS', 'ghg_95pct_nonuke')
print(f'Run: {target.name}')
yb = pd.read_csv(target/'outputs'/'Year_balance.csv', index_col=0)
print(f'Year_balance shape: {yb.shape}')
print('Columns (layers):', yb.columns.tolist()[:20])
print()

# Show all technologies that produce or consume mobility-related layers
for layer in MOB_LAYERS:
    if layer in yb.columns:
        col = yb[layer]
        producers = col[col > 0.1].sort_values(ascending=False).head(8)
        consumers = col[col < -0.1].sort_values().head(5)
        if len(producers) > 0:
            print(f'--- {layer} producers (GWh/yr) ---')
            print(producers.to_string())
        if len(consumers) > 0:
            print(f'--- {layer} consumers (GWh/yr) ---')
            print(consumers.to_string())
        print()
