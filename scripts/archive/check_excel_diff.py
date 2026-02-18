import pandas as pd
import os

base_dir = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
old_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_old.xlsx')
new_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_old_UPDATED.xlsx')

def check_differences():
    print("Checking differences between OLD and NEW files...")
    
    if not os.path.exists(old_file):
        print("OLD file does not exist. NEW file is the only one.")
        return

    try:
        xls_old = pd.ExcelFile(old_file)
        sheets_old = set(xls_old.sheet_names)
        xls_old.close()
    except Exception as e:
        print(f"Error reading OLD file: {e}")
        sheets_old = set()

    try:
        xls_new = pd.ExcelFile(new_file)
        sheets_new = set(xls_new.sheet_names)
        xls_new.close()
    except Exception as e:
        print(f"Error reading NEW file: {e}")
        sheets_new = set()

    print(f"Sheets in OLD: {len(sheets_old)}")
    print(f"Sheets in NEW: {len(sheets_new)}")

    missing_in_new = sheets_old - sheets_new
    if missing_in_new:
        print(f"The following sheets are in OLD but missing in NEW: {missing_in_new}")
        print("We should probably merge them.")
    else:
        print("NEW file contains all sheets from OLD (or OLD is empty/error).")
        print("You can safely use NEW file.")

if __name__ == "__main__":
    check_differences()
