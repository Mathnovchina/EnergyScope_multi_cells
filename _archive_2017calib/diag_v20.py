import pandas as pd, pathlib

run = pathlib.Path('case_studies/FI/manual_runs/20260316_130543__v20_disable_biomass_hvc')
yb  = pd.read_csv(run / 'outputs' / 'Year_balance.csv', index_col=0)
res = pd.read_csv(run / 'outputs' / 'Resources.csv', index_col=0)
ass = pd.read_csv(run / 'outputs' / 'Assets.csv', index_col=0)

res['total'] = res['R_year_local'] + res['R_year_exterior']

# ---- SCORECARD ----
REALITY = {
    'PE_BIOMASS':        (100.0, 1.5),
    'PE_OIL':            (82.0,  1.5),
    'PE_GAS':            (20.0,  1.0),
    'PE_COAL':           (35.0,  1.5),
    'PE_NUCLEAR':        (65.0,  1.0),
    'PE_HYDRO':          (15.0,  0.8),
    'PE_WIND':           (5.0,   0.8),
    'ELEC_NUCLEAR':      (21.6,  1.5),
    'ELEC_HYDRO':        (14.6,  1.2),
    'ELEC_WIND':         (4.8,   1.0),
    'ELEC_CHP':          (20.735, 1.2),
    'ELEC_CONDENSATION': (3.284, 0.8),
    'ELEC_SOLAR':        (0.044, 0.3),
    'CO2':               (41.2,  2.0),
}

def elec_from(techs):
    s = 0
    for t in techs:
        if t in yb.index and 'ELECTRICITY' in yb.columns:
            v = yb.loc[t, 'ELECTRICITY']
            if v > 0: s += v
    return s / 1000

def pe(resources):
    s = 0
    for r in resources:
        if r in res.index:
            s += res.loc[r, 'total']
    return s / 1000

m = {}
m['PE_BIOMASS']        = pe(['WOOD','WET_BIOMASS','BIOWASTE','ENERGY_CROPS_2','BIOMASS_RESIDUES'])
m['PE_OIL']            = pe(['LFO','DIESEL','GASOLINE','JET_FUEL'])
m['PE_GAS']            = pe(['GAS','GAS_RE'])
m['PE_COAL']           = pe(['COAL'])
m['PE_NUCLEAR']        = pe(['URANIUM'])
m['PE_HYDRO']          = pe(['HYDRO'])
m['PE_WIND']           = pe(['WIND'])
m['ELEC_NUCLEAR']      = elec_from(['NUCLEAR'])
m['ELEC_HYDRO']        = elec_from(['HYDRO_RIVER','HYDRO_DAM'])
m['ELEC_WIND']         = elec_from(['WIND_ONSHORE','WIND_OFFSHORE'])
m['ELEC_CHP']          = elec_from([t for t in yb.index if 'COGEN' in t])
m['ELEC_CONDENSATION'] = elec_from(['CCGT','OCGT','COAL_US','COAL_IGCC','CCGT_AMMONIA','BIOMASS_TO_POWER'])
m['ELEC_SOLAR']        = elec_from(['PV_ROOFTOP','PV_UTILITY'])

co2_candidates = [c for c in yb.columns if 'CO2' in c and 'ATM' not in c and 'CAPTURED' not in c]
if co2_candidates and 'GHG_EMISSIONS' in yb.index:
    m['CO2'] = abs(yb.loc['GHG_EMISSIONS', co2_candidates[0]]) / 1000
else:
    m['CO2'] = 0.0

print('=' * 70)
print('SCORECARD v20')
print('=' * 70)
header = f"{'Metric':<22} {'Model':>8} {'Target':>8} {'Error%':>8} {'W':>4}  {'WxErr':>8}"
print(header)
print('-' * 70)

rows = []
for k, (tgt, w) in REALITY.items():
    mv = m.get(k, 0.0)
    err = abs(mv - tgt) / tgt * 100
    rows.append((k, mv, tgt, err, w, err * w))

for (k, mv, tgt, err, w, we) in sorted(rows, key=lambda x: -x[3]):
    flag = ' <<<' if err > 15 else (' ok' if err < 6 else '')
    print(f"{k:<22} {mv:>8.2f} {tgt:>8.1f} {err:>7.1f}% {w:>4.1f}  {we:>8.2f}{flag}")

total_we = sum(r[5] for r in rows)
total_w  = sum(r[4] for r in rows)
print('-' * 70)
print(f"{'SCORE':<22} {'':>8} {'':>8} {total_we/total_w:>7.1f}% {total_w:>4.1f}")

# ---- CHP DETAIL ----
print()
print('=' * 70)
print('CHP ELECTRICITY DETAIL (target: 20.74 TWh)')
print('=' * 70)
chp_techs = [t for t in yb.index if 'COGEN' in t]
total_chp = 0
for t in sorted(chp_techs):
    if 'ELECTRICITY' in yb.columns:
        v = yb.loc[t, 'ELECTRICITY']
        if abs(v) > 1:
            cap = ass.loc[t, 'F'] if t in ass.index and 'F' in ass.columns else float('nan')
            print(f"  {t:<35} {v/1000:+.3f} TWh   cap={cap:.3f} GW")
            if v > 0: total_chp += v
print(f"  {'TOTAL CHP':<35} {total_chp/1000:+.3f} TWh")

# ---- CHP HEAT (to understand utilization) ----
print()
print('DHN HEAT SUPPLY BREAKDOWN (target: ~52 TWh total DHN)')
for col in [c for c in yb.columns if 'HEAT_LOW_T_DHN' in c]:
    s = yb[col]
    nz = s[s.abs() > 100].sort_values(ascending=False)
    for idx, v in nz.items():
        if v > 0 and 'END_USES' not in idx:
            print(f"  {idx:<35} {v/1000:+.3f} TWh")

# ---- WIND ----
print()
print('=' * 70)
print('WIND DETAIL (target: 4.8 TWh)')
print('=' * 70)
for t in ['WIND_ONSHORE', 'WIND_OFFSHORE']:
    cap = ass.loc[t, 'F'] if t in ass.index and 'F' in ass.columns else float('nan')
    if 'ELECTRICITY' in yb.columns and t in yb.index:
        gen = yb.loc[t, 'ELECTRICITY'] / 1000
    else:
        gen = 0
    print(f"  {t:<30} F={cap:.3f} GW   gen={gen:.3f} TWh   cp={gen/(cap*8.76)*100 if cap>0 else 0:.1f}%")
print(f"  Wind target = 4.8 TWh. fmax_v9=2.1 GW => at cp=34% => 6.23 TWh (over by 1.5 TWh)")

# ---- OIL DETAIL ----
print()
print('=' * 70)
print('OIL PE DETAIL (target: 82.0 TWh)')
print('=' * 70)
for r in ['LFO','DIESEL','GASOLINE','JET_FUEL']:
    if r in res.index:
        tot = res.loc[r, 'total']
        loc = res.loc[r, 'R_year_local']
        ext = res.loc[r, 'R_year_exterior']
        if abs(tot) > 1:
            print(f"  {r:<20} {tot/1000:7.2f} TWh  (local={loc/1000:.2f}, import={ext/1000:.2f})")
total_oil = pe(['LFO','DIESEL','GASOLINE','JET_FUEL'])
print(f"  TOTAL: {total_oil:.2f} TWh  (gap to target: {82.0-total_oil:.2f} TWh)")

# ---- OIL CONSUMERS ----
print()
print('LFO consumers (Year_balance):')
if 'LFO' in yb.columns:
    lfo = yb['LFO']
    nz = lfo[lfo.abs() > 10].sort_values()
    for idx, v in nz.items():
        print(f"  {idx:<35} {v/1000:+.3f} TWh")

# ---- GAS ----
print()
print('=' * 70)
print('GAS PE DETAIL (target: 20.0 TWh, model: ~22 TWh)')
print('=' * 70)
if 'GAS' in yb.columns:
    gas = yb['GAS']
    nz = gas[gas.abs() > 10].sort_values()
    for idx, v in nz.items():
        print(f"  {idx:<35} {v/1000:+.3f} TWh")
