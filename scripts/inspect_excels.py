import pandas as pd
from pathlib import Path

def inspect_excel(path):
    print(f"--- Inspecting {path.name} ---")
    try:
        xl = pd.ExcelFile(path)
        print("Sheet names:", xl.sheet_names)
        # Try to glimpse into a likely sheet
        for trigger in ['Technologies', 'Resources', 'Demand', 'Tech']:
            matches = [s for s in xl.sheet_names if trigger in s]
            if matches:
                print(f"Found potential data sheet: {matches[0]}")
                df = pd.read_excel(path, sheet_name=matches[0], nrows=5)
                print(df.columns.tolist())
    except Exception as e:
        print(f"Error reading {path.name}: {e}")

base_path = Path(r"c:/Users/borde/OneDrive/Bureau/model/EnergyScope_multi_cells/Data/exogenous_data")
inspect_excel(base_path / "EnergyScope_Finland_calibration_template_v4.xlsx")
inspect_excel(base_path / "Finland_MASTER_Calibration.xlsx")
