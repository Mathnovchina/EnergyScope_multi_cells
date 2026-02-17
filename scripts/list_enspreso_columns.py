import pandas as pd
import os

# Path to ENSPRESO file
enspreso_path = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\exogenous_data\ENSPRESO\ENSPRESO_BIOMASS.xlsx'

try:
    df = pd.read_excel(enspreso_path, sheet_name='ENER - NUTS0 EnergyCom')
    print("Columns:", df.columns.tolist())
    
    # Print first row
    print(df.head(1).T)
except Exception as e:
    print(f"Error: {e}")
