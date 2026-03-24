import pandas as pd
import os

out = os.path.join('case_studies', 'FI', 'manual_runs', '20260319_164846__v28d_coal_gentle', 'outputs')
yb = pd.read_csv(os.path.join(out, 'year_balance.csv'), index_col=0)
assets = pd.read_csv(os.path.join(out, 'assets.csv'), index_col=0)

# ---- Current metrics scorecard ----
metrics = {
    'CO2':               (39.33, 41.2),
    'ELEC_CHP':          (20.69, 20.7),
    'ELEC_CONDENSATION': (3.00,  3.28),
    'ELEC_HYDRO':        (14.60, 14.6),
    'ELEC_NUCLEAR':      (22.31, 21.6),
    'ELEC_SOLAR':        (0.02,  0.0),
    'ELEC_WIND':         (4.79,  4.8),
    'PE_BIOMASS':        (98.97, 100.0),
    'PE_COAL':           (35.00, 35.0),
    'PE_GAS':            (20.00, 20.0),
    'PE_HYDRO':          (14.60, 15.0),
    'PE_NUCLEAR':        (69.72, 65.0),
    'PE_OIL':            (74.02, 82.0),
    'PE_WIND':           (4.79,  5.0),
}

print(f'{"Metric":<22} {"Model":>8} {"Target":>8} {"AbsErr":>8} {"RelErr%":>9} {"Notes"}')
print('-' * 80)
for m, (model, target) in sorted(metrics.items(), key=lambda x: -abs(x[1][0]-x[1][1])/max(x[1][1],0.01)):
    abs_err = abs(model - target)
    rel_err = abs_err / max(target, 0.01) * 100
    direction = 'HIGH' if model > target else 'LOW '
    print(f'{m:<22} {model:>8.2f} {target:>8.2f} {abs_err:>8.2f} {rel_err:>8.1f}%  {direction}')

# ---- PE_OIL: what uses oil? ----
print('\n=== OIL-consuming technologies (year_balance) ===')
oil_carriers = ['LFO', 'GASOLINE', 'DIESEL', 'JET_FUEL']
for carrier in oil_carriers:
    if carrier in yb.columns:
        col = yb[carrier]
        nz = col[col > 0.5]  # technologies CONSUMING this carrier
        if not nz.empty:
            print(f'\n{carrier} consumers:')
            for tech, val in nz.sort_values(ascending=False).items():
                print(f'  {tech:30s} {val:10.1f} GWh')

# ---- PE_NUCLEAR: what uses uranium? ----
print('\n=== URANIUM consumption ===')
if 'URANIUM' in yb.columns:
    ur = yb['URANIUM']
    nz = ur[ur > 0.5]
    for tech, val in nz.sort_values(ascending=False).items():
        print(f'  {tech:30s} {val:10.1f} GWh')
    total_ur = nz.sum()
    # PE_NUCLEAR = URANIUM / efficiency, or direct GWh?
    # In EnergyScope, PE_NUCLEAR usually = URANIUM consumed (GWh thermal)
    print(f'\nTotal URANIUM consumed: {total_ur:.1f} GWh = {total_ur/1000:.2f} TWh')
    print(f'NUCLEAR electricity: {yb.loc["NUCLEAR","ELECTRICITY"]:.1f} GWh')
    nuc_eff = yb.loc["NUCLEAR","ELECTRICITY"] / total_ur
    print(f'Implied efficiency: {nuc_eff:.3f}')

# ---- Oil total ----
print('\n=== Total oil-products consumed ===')
total_oil = 0
for carrier in oil_carriers:
    if carrier in yb.columns:
        consumed = yb[carrier][yb[carrier] > 0.5].sum()
        print(f'  {carrier:15s} {consumed:10.1f} GWh')
        total_oil += consumed
print(f'  {"TOTAL":15s} {total_oil:10.1f} GWh = {total_oil/1000:.2f} TWh (target 82 TWh)')

# ---- What drives OIL imports? ----
print('\n=== RES (resource rows) consumption check ===')
for res_row in ['LFO', 'GASOLINE', 'DIESEL', 'JET_FUEL']:
    if res_row in yb.index:
        val = yb.loc[res_row, res_row] if res_row in yb.columns else 0
        print(f'  {res_row} resource supply: {val:.1f} GWh')
