import pandas as pd
from pathlib import Path
import numpy as np

# Config
BASE_DIR = Path(r"c:/Users/borde/OneDrive/Bureau/model/EnergyScope_multi_cells")
EXCEL_PATH = BASE_DIR / "Data/exogenous_data/Finland_MASTER_Calibration.xlsx"
CSV_DIR = BASE_DIR / "Data/2017/FI"
TECH_CSV_PATH = CSV_DIR / "Technologies.csv"
RES_CSV_PATH = CSV_DIR / "Resources.csv"

def compare_data(excel_df, csv_df, name, index_col):
    print(f"\n--- Comparing {name} ---")
    
    # Clean indices
    excel_df = excel_df.set_index(index_col)
    excel_df.index = excel_df.index.astype(str).str.strip()
    
    csv_df.index = csv_df.index.astype(str).str.strip()
    
    # Find common indices
    common_indices = excel_df.index.intersection(csv_df.index)
    # print(f"Common indices: {len(common_indices)}")
    
    if "DIESEL_TO_JET_FUEL" in excel_df.index:
         print(f"DIESEL_TO_JET_FUEL found in Excel. f_max: {excel_df.loc['DIESEL_TO_JET_FUEL', 'f_max']}")
    else:
         print("DIESEL_TO_JET_FUEL NOT found in Excel.")

    if len(common_indices) == 0:
        print("No match found. Indices might be named differently.")
        print("Excel Sample:", excel_df.index[:5].tolist())
        print("CSV Sample:", csv_df.index[:5].tolist())
        return

    # Find common columns
    # Excel might have spaces or units in names, CSV usually simplified
    # Lets try direct match first
    common_cols = excel_df.columns.intersection(csv_df.columns)
    
    # If few matches, try cleaning Excel columns (strip spaces)
    if len(common_cols) < 2:
        excel_df.columns = excel_df.columns.str.strip()
        common_cols = excel_df.columns.intersection(csv_df.columns)
        
    print(f"Common columns to compare: {common_cols.tolist()}")
    
    diff_count = 0
    for col in common_cols:
        # Check if numeric
        if not pd.api.types.is_numeric_dtype(csv_df[col]) or not pd.api.types.is_numeric_dtype(excel_df[col]):
            continue
            
        # Compare
        # Align data
        s_excel = excel_df.loc[common_indices, col]
        s_csv = csv_df.loc[common_indices, col]
        
        # Handle formatting differences (thousands, etc) if any
        
        # Diff
        diff = s_csv - s_excel
        
        # Filter significant diffs
        significant = diff[diff.abs() > 1e-5]
        
        if not significant.empty:
            diff_count += len(significant)
            print(f"\nMismatch in column '{col}': {len(significant)} entries differ.")
            print(significant.head(5))
            print("CSV values:")
            print(s_csv.loc[significant.index[:5]])
            print("Excel values:")
            print(s_excel.loc[significant.index[:5]])
        else:
            # print(f"Column '{col}': OK")
            pass
            
    if diff_count == 0:
        print(">> ALL CHECKED DATA MATCHES! (Calibration integrated)")
    else:
        print(f">> FOUND {diff_count} MISMATCHES. (Calibration might NOT be fully integrated)")

def main():
    if not EXCEL_PATH.exists():
        print(f"Excel not found: {EXCEL_PATH}")
        return

    # 1. Technologies
    print("Reading Excel Technologies...")
    try:
        df_tech_xl = pd.read_excel(EXCEL_PATH, sheet_name="4_Technologies", skiprows=0)
        # Drop rows where 'Technologies param' is null (often empty rows)
        df_tech_xl = df_tech_xl.dropna(subset=['Technologies param'])
        
        print("Reading CSV Technologies...")
        # ES CSVs are typically ';' separated, comments '#'
        # Update: It appears to be comma separated in this dataset
        df_tech_csv = pd.read_csv(TECH_CSV_PATH, sep=',', comment='#', index_col=0)
        # Fix: sometimes the first column is the index but pandas reads it differently if header is complex
        # Assuming standard format
        
        compare_data(df_tech_xl, df_tech_csv, "Technologies", "Technologies param")
        
    except Exception as e:
        print(f"Error checking Technologies: {e}")

    # 2. Resources
    print("\nReading Excel Resources...")
    try:
        df_res_xl = pd.read_excel(EXCEL_PATH, sheet_name="5_Resources")
        # Assuming first column is valid index, inspect column 0 name
        idx_col = df_res_xl.columns[0] # 'Unnamed: 0' usually if not named
        df_res_xl = df_res_xl.dropna(subset=[idx_col])
        
        print("Reading CSV Resources...")
        df_res_csv = pd.read_csv(RES_CSV_PATH, sep=',', comment='#', index_col=0)
        
        compare_data(df_res_xl, df_res_csv, "Resources", idx_col)
        
    except Exception as e:
        print(f"Error checking Resources: {e}")

if __name__ == "__main__":
    main()
