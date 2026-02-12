import pandas as pd
import openpyxl
import os

base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
file_path = os.path.join(base_path, "Data", "exogenous_data", "DEA_Elec_Heat.xlsx")
sheet_name = "alldata_flat"

print("Loading DEA Data...")
df = pd.read_excel(file_path, sheet_name=sheet_name)

print("\n--- Unique Technologies ---")
print(df['Technology'].unique())

print("\n--- Unique Parameters (par) ---")
# Filter for typical cost keywords to avoid listing 100s of technical params
cost_params = [p for p in df['par'].unique() if 'cost' in str(p).lower() or 'investment' in str(p).lower() or 'o&m' in str(p).lower()]
print(cost_params[:20]) # Print first 20 matches

print("\n--- Check for Nuclear ---")
nuclear_matches = df[df['Technology'].str.contains("Nuclear", case=False, na=False)]
if not nuclear_matches.empty:
    print("Nuclear found!")
    print(nuclear_matches['Technology'].unique())
else:
    print("No Nuclear technology found in this catalogue.")

print("\n--- Available Years ---")
print(sorted(df['year'].unique()))
