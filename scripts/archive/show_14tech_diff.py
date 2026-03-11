"""Show full comparison of 14 key technologies: original 2017 vs current 2035."""
import pandas as pd

orig = pd.read_csv('Data/2017/02_REF_REGION/Technologies.csv.bak_20260308_pre2035', skiprows=[1])
orig.columns = orig.columns.str.strip()
orig = orig.set_index('Technologies param')

cur = pd.read_csv('Data/2017/02_REF_REGION/Technologies.csv', skiprows=[1])
cur.columns = cur.columns.str.strip()
cur = cur.set_index('Technologies param')

key14 = ['NUCLEAR','WIND_ONSHORE','WIND_OFFSHORE','PV_ROOFTOP','PV_UTILITY',
         'COAL_US','CCGT','DHN_COGEN_GAS','DHN_HP_ELEC','DHN_BOILER_GAS',
         'DHN_BOILER_WOOD','DHN_SOLAR','IND_BOILER_GAS','IND_BOILER_WOOD']

header = f"{'Tech':<25} {'orig_cinv':>10} {'35_cinv':>10} {'d%':>7} {'orig_cmt':>10} {'35_cmt':>10} {'d%':>7} {'o_lt':>5} {'3_lt':>5}"
print(header)
print("-" * len(header))

for t in key14:
    oi = float(orig.loc[t, 'c_inv'])
    ci = float(cur.loc[t, 'c_inv'])
    om = float(orig.loc[t, 'c_maint'])
    cm = float(cur.loc[t, 'c_maint'])
    ol = float(orig.loc[t, 'lifetime'])
    cl = float(cur.loc[t, 'lifetime'])
    di = (ci - oi) / oi * 100 if oi != 0 else 0
    dm = (cm - om) / om * 100 if om != 0 else 0
    print(f"{t:<25} {oi:>10.1f} {ci:>10.1f} {di:>+6.1f}% {om:>10.2f} {cm:>10.2f} {dm:>+6.1f}% {ol:>5.0f} {cl:>5.0f}")
