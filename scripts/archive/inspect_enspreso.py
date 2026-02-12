import pandas as pd
import os
import sys

def search_in_excel(file_path):
    print(f"Searching in {file_path}")
    try:
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            print(f"  Scanning sheet: {sheet_name}")
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                # Search in headers
                if any("peat" in str(col).lower() for col in df.columns):
                    print(f"    FOUND 'Peat' in header of {sheet_name}")
                    for col in df.columns:
                        if "peat" in str(col).lower():
                            print(f"      Header: {col}")

                # Search in values (first non-empty column usually contains category)
                # Convert whole dataframe to string and search might be slow but effective
                
                mask = df.map(lambda x: "peat" in str(x).lower() if pd.notnull(x) else False)
                if mask.any().any():
                    print(f"    FOUND 'Peat' in values of {sheet_name}")
                    # Print first few rows where it is found
                    rows_with_peat = df[mask.any(axis=1)]
                    print(rows_with_peat.head(2).to_markdown())
            except Exception as e:
                print(f"    Error reading sheet {sheet_name}: {e}")
    except Exception as e:
        print(f"Error opening {file_path}: {e}")

def main():
    enspreso_dir = os.path.join("Data", "exogenous_data", "ENSPRESO")
    
    files_to_check = [
        "ENSPRESO_BIOMASS.xlsx",
        "ENSPRESO_SOLAR_PV_CSP.XLSX",
        "ENSPRESO_WIND_ONSHORE_OFFSHORE.XLSX"
    ]
    
    for fname in files_to_check:
        fpath = os.path.join(enspreso_dir, fname)
        if os.path.exists(fpath):
            search_in_excel(fpath)
        else:
            print(f"File not found: {fpath}")

if __name__ == "__main__":
    main()
