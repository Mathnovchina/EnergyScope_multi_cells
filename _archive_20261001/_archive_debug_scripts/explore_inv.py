import pandas as pd
import os

def check_resources_duplication(path1, path2):
    print(f"Checking duplication between {path1} and {path2}")
    try:
        df1 = pd.read_csv(path1, index_col=0, comment='#')
        df2 = pd.read_csv(path2, index_col=0, comment='#')
    except Exception as e:
        print(f"Error reading CSVs: {e}")
        return

    # Check if 'avail' exists in both
    col1 = None
    if 'avail' in df1.columns: col1 = 'avail'
    if 'avail_local' in df1.columns: col1 = 'avail_local'
    
    col2 = None
    if 'avail' in df2.columns: col2 = 'avail'
    if 'avail_local' in df2.columns: col2 = 'avail_local'
    
    if not col1 or not col2:
        print("Could not find 'avail' or 'avail_local' column in one of the files.")
        print(f"Columns in {path1}: {df1.columns}")
        print(f"Columns in {path2}: {df2.columns}")
        return

    common_resources = df1.index.intersection(df2.index)
    print(f"Common resources: {list(common_resources)}")
    
    diffs = []
    tol = 1e-4
    for res in common_resources:
        val1 = df1.loc[res, col1]
        val2 = df2.loc[res, col2]
        
        # Check if values are close enough (if float)
        try:
            diff = abs(float(val1) - float(val2))
            is_close = diff < tol
        except:
            is_close = str(val1) == str(val2)
            
        if not is_close:
            diffs.append((res, val1, val2))
            
    if not diffs:
        print("Identical values (within tolerance) for common resources.")
    else:
        print("Differences found:")
        for res, v1, v2 in diffs:
            print(f"{res}: {v1} (2017) vs {v2} (2035)")

def explore_enspreso(path):
    print(f"\nExploring ENSPRESO data: {path}")
    try:
        xl = pd.ExcelFile(path)
        relevant_sheets = [s for s in xl.sheet_names if 'NUTS0' in s]
        print(f"NUTS0 related sheets: {relevant_sheets}")
        
        for sheet in relevant_sheets:
            print(f"\n--- Reading sheet: {sheet} ---")
            df = pd.read_excel(path, sheet_name=sheet, nrows=20)
            print("First 5 rows:")
            print(df.head())
            print(f"Columns: {list(df.columns)}")
            
            # Check for FI
            cols_str = [str(c) for c in df.columns]
            if 'FI' in cols_str:
                print("'FI' found in columns.")
            
            # check rows for FI or Finland
            msg = "FI not found in 20 first rows"
            found_fi = False
            for col in df.columns:
                if df[col].astype(str).str.contains('FI').any():
                     print(f"'FI' found in column '{col}' values.")
                     found_fi = True
                     msg = ""
                if df[col].astype(str).str.contains('Finland').any():
                     print(f"'Finland' found in column '{col}' values.")
                     found_fi = True
                     msg = ""
            if not found_fi:
                print(msg)

            # Check for years (2010 .. 2050)
            years_found = [y for y in [2010, 2020, 2030, 2040, 2050] if any(str(y) in str(c) for c in cols_str)]
            if years_found:
                print(f"Years found in columns: {years_found}")
            else:
                print("Years NOT found in columns.")
                # Maybe they are in a 'Year' column
                if 'Year' in cols_str or 'year' in cols_str:
                    print("Year column found.")


    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    check_resources_duplication('Data/2017/FI/Resources.csv', 'Data/2035/FI/Resources.csv')
    
    enspreso_path = 'Data/exogenous_data/ENSPRESO/ENSPRESO_BIOMASS.xlsx'
    if os.path.exists(enspreso_path):
        explore_enspreso(enspreso_path)
