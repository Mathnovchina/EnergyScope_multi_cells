
import pandas as pd
from pathlib import Path
import os

# Config
BASE_DIR = Path(os.getcwd())
EXCEL_PATH = BASE_DIR / "Data/exogenous_data/Finland_MASTER_Calibration.xlsx"

def check_tech_caps():
    print(f"Reading {EXCEL_PATH}...")
    try:
        # Try reading the sheet used by update_data_2017.py
        # Note: the script update_data_2017.py used '6_Technology_Capacities', let's try that.
        sheet_name = '6_Technology_Capacities'
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
        print(f"Sheet '{sheet_name}' columns:", df.columns.tolist())
        
        # Look for technology names
        # Assuming column 'Technology' or similar
        print(df.head())

        # Filter for relevant fossil keywords
        keywords = ['COAL', 'GAS', 'OIL', 'PEAT', 'CCGT', 'Nuclear', 'Hydro', 'Wind']
        
        # Find column that holds tech name
        tech_col = None
        for col in df.columns:
            if 'Tech' in col or 'Parameter' in col:
                tech_col = col
                break
        
        if tech_col:
            print(f"Found tech column: {tech_col}")
            df[tech_col] = df[tech_col].astype(str)
            
            mask = df[tech_col].apply(lambda x: any(k.upper() in x.upper() for k in keywords))
            relevant_df = df[mask]
            print("Relevant Data:")
            print(relevant_df.to_string())
        else:
            print("Could not identify technology name column.")
            print(df)

    except Exception as e:
        print(f"Error: {e}")
        # Fallback: list sheet names
        try:
            xl = pd.ExcelFile(EXCEL_PATH)
            print("Sheet names:", xl.sheet_names)
        except Exception as e2:
            print(f"Error listing sheets: {e2}")

if __name__ == "__main__":
    check_tech_caps()
