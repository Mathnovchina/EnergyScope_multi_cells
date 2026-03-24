import pandas as pd
import os

out = os.path.join('case_studies', 'FI', 'manual_runs', '20260319_164846__v28d_coal_gentle', 'outputs')
yb = pd.read_csv(os.path.join(out, 'year_balance.csv'), index_col=0)
assets = pd.read_csv(os.path.join(out, 'assets.csv'), index_col=0)

e = yb['ELECTRICITY']
nz = e[e.abs() > 0.5].sort_values(ascending=False)
print('=== v28d ELECTRICITY balance (GWh) ===')
for tech, val in nz.items():
    print(f'  {tech:30s} {val:10.1f}')

cond = ['COAL_US', 'COAL_IGCC', 'CCGT', 'CCGT_AMMONIA']
total_cond = sum(max(0, e.get(t, 0)) for t in cond)
total_positive = e[e > 0].sum()
imports = e.get('ELECTRICITY', 0)

print(f'\nCondensation total: {total_cond:.1f} GWh (target 3284)')
print(f'Total positive: {total_positive:.1f} GWh')
print(f'Imports: {imports:.1f} GWh (target 20426)')
print(f'COAL_US: {e.get("COAL_US", 0):.1f} GWh')
print(f'COAL_US F: {assets.loc["COAL_US", "F"]:.2f} GW')
print(f'COAL_US F_year: {assets.loc["COAL_US", "F_year"]:.1f} GWh')
print(f'COAL_US effective ratio: {e.get("COAL_US", 0) / total_positive:.4f}')

# Check key changes vs v28
out_prev = os.path.join('case_studies', 'FI', 'manual_runs', '20260319_155308__v28_coal_cap', 'outputs')
yb_p = pd.read_csv(os.path.join(out_prev, 'year_balance.csv'), index_col=0)
e_p = yb_p['ELECTRICITY']

print('\n=== Key changes v28 -> v28d ===')
for tech in ['COAL_US', 'COAL_IGCC', 'CCGT', 'ELECTRICITY', 'DHN_COGEN_COAL', 'DEC_HP_ELEC', 'DHN_HP_ELEC']:
    v28 = e_p.get(tech, 0)
    v28d = e.get(tech, 0)
    diff = v28d - v28
    if abs(diff) > 5:
        print(f'  {tech:30s}  {v28:10.1f} -> {v28d:10.1f}  ({diff:+.1f})')
