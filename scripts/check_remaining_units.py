"""Check unit issues for waste CHP, electric boilers, heat pumps."""
import pandas as pd
dea = pd.read_excel('Data/exogenous_data/DEA_Elec_Heat.xlsx', sheet_name='alldata_flat')

# Waste CHP investment
print("=== Waste CHP investment ===")
waste = dea[(dea['Technology'].str.contains('Waste CHP', na=False)) & 
            (dea['par'].str.contains('Nominal investment.*total', na=False))]
for _, r in waste[waste['year']==2015].iterrows():
    t = r['Technology']
    p = r['par']
    v = r['val']
    print(f"  {t}")
    print(f"    {p}  val={v}")

# Electric boiler
print("\n=== Electric boiler investment ===")
eb = dea[(dea['Technology'].str.contains('Electric boiler', na=False)) & 
         (dea['par'].str.contains('Nominal investment.*total', na=False))]
for _, r in eb[eb['year'].isin([2015,2020])].iterrows():
    t = r['Technology']
    yr = r['year']
    p = r['par']
    v = r['val']
    print(f"  {t}  yr={yr}  {p}  val={v}")

# Heat pump small - check what unit
print("\n=== Heat pump small (air source) ===")
hp = dea[(dea['Technology']=='Heat pump, air source - heat pump - electricity - small') & 
         (dea['par'].str.contains('Nominal investment.*total', na=False))]
for _, r in hp.iterrows():
    yr = r['year']
    p = r['par']
    v = r['val']
    print(f"  yr={yr}  {p}  val={v}")

# What is ESM DEC_HP_ELEC capacity measured in? Check Layers_in_out
print("\n=== ESM DEC_HP_ELEC in Layers_in_out ===")
try:
    lio = pd.read_csv('Data/2017/00_INDEP/Layers_in_out.csv')
    hp_rows = lio[lio.iloc[:,0].str.contains('DEC_HP', na=False)]
    print(hp_rows.to_string())
except Exception as e:
    print(f"Error: {e}")
