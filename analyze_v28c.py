import pandas as pd
import os

out = os.path.join('case_studies', 'FI', 'manual_runs', '20260319_163357__v28c_coal_no_igcc', 'outputs')
yb = pd.read_csv(os.path.join(out, 'year_balance.csv'), index_col=0)
assets = pd.read_csv(os.path.join(out, 'assets.csv'), index_col=0)

e = yb['ELECTRICITY']
nz = e[e.abs() > 0.5].sort_values(ascending=False)
print('=== v28c ELECTRICITY balance (GWh) ===')
for tech, val in nz.items():
    print(f'  {tech:30s} {val:10.1f}')

cond = ['COAL_US', 'COAL_IGCC', 'CCGT', 'CCGT_AMMONIA']
total_cond = sum(max(0, e.get(t, 0)) for t in cond)
total_positive = e[e > 0].sum()
coal_us_out = e.get('COAL_US', 0)

print(f'\nCondensation total: {total_cond:.1f} GWh')
print(f'Total positive (all gen + imports): {total_positive:.1f} GWh')
print(f'COAL_US output: {coal_us_out:.1f} GWh')
print(f'COAL_US effective ratio: {coal_us_out / total_positive:.4f}')
print(f'COAL_US F: {assets.loc["COAL_US", "F"]:.2f} GW')
print(f'COAL_US F_year: {assets.loc["COAL_US", "F_year"]:.1f} GWh')

# Compare with v28 (no fmax_perc, no IGCC issue)
out_prev = os.path.join('case_studies', 'FI', 'manual_runs', '20260319_155308__v28_coal_cap', 'outputs')
yb_p = pd.read_csv(os.path.join(out_prev, 'year_balance.csv'), index_col=0)
e_p = yb_p['ELECTRICITY']
total_pos_prev = e_p[e_p > 0].sum()
coal_prev = e_p.get('COAL_US', 0)

print(f'\n=== v28 (prev, no fmax_perc) ===')
print(f'COAL_US output: {coal_prev:.1f} GWh')
print(f'Total positive: {total_pos_prev:.1f} GWh')
print(f'COAL_US effective ratio: {coal_prev / total_pos_prev:.4f}')

# Calculate target fmax_perc
# Target condensation = 3284 GWh, CCGT ~60 = COAL_US ~3224
# fmax_perc * total_sector = target_coal_output
# But total_sector changes with fmax_perc... use current total as estimate
target_coal = 3224
est_total = (total_positive + total_pos_prev) / 2  # approximate
target_fmaxperc = target_coal / est_total
print(f'\nTarget COAL_US output: {target_coal} GWh')
print(f'Estimated total sector: {est_total:.0f} GWh')
print(f'Target fmax_perc: {target_fmaxperc:.4f}')
print(f'Also try slightly higher: {target_fmaxperc * 1.05:.4f}')
