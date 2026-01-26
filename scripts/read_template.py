import pandas as pd

print("="*80)
print("READING TEMPLATE FILE")
print("="*80)

xls = pd.ExcelFile('Data/exogenous_data/EnergyScope_Finland_calibration_template_v4.xlsx')

for sheet in xls.sheet_names:
    print(f"\n{'='*80}")
    print(f"Sheet: {sheet}")
    print(f"{'='*80}")
    df = pd.read_excel(xls, sheet)
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst 10 rows:")
    print(df.head(10))
