import pandas as pd
from collections import defaultdict

runs = [
    ('2017', 'case_studies/FI/manual_runs/20260323_173930__2017_baseline/outputs/input2sankey_FI.csv'),
    ('2050', 'case_studies/FI/manual_runs/20260324_142019__national_plan_2050/outputs/input2sankey_FI.csv')
]

for label, path in runs:
    df = pd.read_csv(path)
    print(f'\n{"="*70}')
    print(f'{label} Sankey: {len(df)} links, {df.realValue.sum():.1f} TWh total flow')
    print(f'{"="*70}')
    
    # Node balance check
    balances = defaultdict(float)
    for _, r in df.iterrows():
        balances[r.source] -= r.realValue  # outflow
        balances[r.target] += r.realValue  # inflow
    
    # Show nodes with significant imbalance (>1 TWh)
    print(f'\nNodes with imbalance > 1 TWh:')
    for node, bal in sorted(balances.items(), key=lambda x: abs(x[1]), reverse=True):
        if abs(bal) > 1:
            kind = "SOURCE" if bal < -1 else "SINK"
            print(f'  {node:30s}: {bal:+8.1f} TWh ({kind})')
    
    # Show all links sorted by value
    print(f'\nAll links:')
    for _, r in df.sort_values('realValue', ascending=False).iterrows():
        print(f'  {r.source:25s} -> {r.target:25s}: {r.realValue:8.2f} TWh ({r.layerID})')
