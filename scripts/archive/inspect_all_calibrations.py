import pandas as pd
import os

# Read all existing calibration files
print("Reading all Finland calibration files...")

files = {
    'UPDATES': 'Data/exogenous_data/Finland_Calibration_UPDATES.xlsx',
    'MASTER_2017': 'Finland_Calibration_MASTER_2017.xlsx',
    'EXHAUSTIVE': 'Data/exogenous_data/Finland_Calibration_Exhaustive_2017.xlsx'
}

for name, path in files.items():
    if os.path.exists(path):
        print(f"\n=== {name} ({path}) ===")
        xls = pd.ExcelFile(path)
        print(f"Sheets: {xls.sheet_names}")
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet)
            print(f"\n  Sheet '{sheet}': {df.shape[0]} rows x {df.shape[1]} cols")
    else:
        print(f"{name}: File not found")
