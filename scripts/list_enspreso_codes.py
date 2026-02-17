import pandas as pd
import os

# Path to ENSPRESO file
enspreso_path = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\exogenous_data\ENSPRESO\ENSPRESO_BIOMASS.xlsx'

try:
    # Read the specific sheet
    # Note: 'ENER - NUTS0 EnergyCom' seems to be the sheet mentioned by user.
    # The previous script used 'ENER - NUTS0 EnergyCom'.
    df = pd.read_excel(enspreso_path, sheet_name='ENER - NUTS0 EnergyCom')
    
    # Get unique values for Energy Commodity
    if 'Energy Commodity' in df.columns:
        unique_codes = df['Energy Commodity'].unique()
        print("Unique Energy Commodity Codes:")
        for code in unique_codes:
            print(f" - {code}")
            
    if 'Sector' in df.columns:
        print("\nUnique Sectors:") 
        print(df['Sector'].unique())
        
    print("\nSample rows for context:")
    cols_to_print = [c for c in ['Energy Commodity', 'Sector', 'Reference', 'Unit'] if c in df.columns]
    print(df[cols_to_print].head().to_string())

except Exception as e:
    print(f"Error reading Excel file: {e}")
