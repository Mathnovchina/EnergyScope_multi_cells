"""Check DEA data for technologies with mapping discrepancies."""
import pandas as pd
dea = pd.read_excel('Data/exogenous_data/DEA_Elec_Heat.xlsx', sheet_name='alldata_flat')

# Check all Offshore Wind entries
print('=== All Offshore/Nearshore Wind c_inv entries ===')
off = dea[dea['Technology'].str.contains('shore Wind|shore wind', case=False, na=False)]
inv_off = off[off['par'].str.contains('Nominal investment.*total.*MEUR', na=False)]
for _, row in inv_off.sort_values(['Technology','year']).iterrows():
    tech = row['Technology']
    yr = row['year']
    par = row['par']
    val = row['val']
    print(f'  {tech:60s} yr={yr}  {par:40s}  val={val}')

# Check Biomass CHP variants
print('\n=== All Biomass CHP c_inv entries (MEUR/MW_e) ===')
bio_chp = dea[(dea['Technology'].str.contains('Biomass CHP', case=False, na=False)) & 
              (dea['par'].str.contains('Nominal investment.*total.*MEUR/MW_e', na=False))]
for _, row in bio_chp.sort_values(['Technology','year']).iterrows():
    tech = row['Technology']
    yr = row['year']
    val = row['val']
    print(f'  {tech:65s} yr={yr}  val={val}')

# Check Heat pump variants
print('\n=== All Heat pump c_inv entries (MEUR/MW_h) ===')
hp = dea[(dea['Technology'].str.contains('Heat pump', case=False, na=False)) & 
         (dea['par'].str.contains('Nominal investment.*total.*MEUR/MW_h', na=False))]
for _, row in hp.sort_values(['Technology','year']).iterrows():
    tech = row['Technology']
    yr = row['year']
    val = row['val']
    print(f'  {tech:65s} yr={yr}  val={val}')

# Check Gas boiler
print('\n=== Gas boiler c_inv entries ===')
gb = dea[(dea['Technology'].str.contains('Gas boiler', case=False, na=False)) & 
         (dea['par'].str.contains('Nominal investment.*total', na=False))]
for _, row in gb.sort_values(['Technology','year']).iterrows():
    tech = row['Technology']
    yr = row['year']
    par = row['par']
    val = row['val']
    print(f'  {tech:65s} yr={yr}  {par:40s}  val={val}')

# Check Biomass boiler variants  
print('\n=== Biomass boiler c_inv entries (MEUR/MW_h) ===')
bb = dea[(dea['Technology'].str.contains('Biomass boiler', case=False, na=False)) & 
         (dea['par'].str.contains('Nominal investment.*total.*MEUR/MW_h', na=False))]
for _, row in bb.sort_values(['Technology','year']).iterrows():
    tech = row['Technology']
    yr = row['year']
    val = row['val']
    print(f'  {tech:65s} yr={yr}  val={val}')
