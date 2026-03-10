import pandas as pd
lio = pd.read_csv('Data/2017/00_INDEP/Layers_in_out.csv', index_col=0)
lio.columns = lio.columns.str.strip()
lio.index = lio.index.str.strip()

# CHP techs (produce both electricity and DHN heat)
chp = lio[(lio['ELECTRICITY'] > 0) & (lio['HEAT_LOW_T_DHN'] > 0)]
print('CHP techs (elec + DHN heat):')
for t in chp.index:
    e = chp.loc[t, 'ELECTRICITY']
    h = chp.loc[t, 'HEAT_LOW_T_DHN']
    print(f'  {t}: ELEC={e:.3f}, DHN={h:.3f}')

print()

# Industrial heat techs
hht = lio[lio['HEAT_HIGH_T'] > 0]
print('Industrial heat techs:')
for t in hht.index:
    h = hht.loc[t, 'HEAT_HIGH_T']
    e = lio.loc[t, 'ELECTRICITY']
    print(f'  {t}: HHT={h:.3f}, ELEC={e:.3f}')
