import pandas as pd
import os

base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
dea_path = os.path.join(base_path, "Data", "exogenous_data", "DEA_Elec_Heat.xlsx")

df = pd.read_excel(dea_path, sheet_name="alldata_flat")

print("Checking Offshore Wind Data:")
owp = df[df['Technology'].str.contains("Offshore Wind", na=False)]
print(owp[['Technology', 'par', 'year', 'val']].head(20))

print("\nChecking Nuclear Cost in CSV:")
tech_csv = pd.read_csv(os.path.join(base_path, "Data", "2017", "02_REF_REGION", "Technologies.csv"), header=0, skiprows=[1], index_col=3)
print(tech_csv.loc['NUCLEAR', ['c_inv', 'c_maint']])
