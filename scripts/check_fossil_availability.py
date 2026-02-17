import pandas as pd
import os

def check_file(path, label):
    print(f"--- Checking {label}: {path} ---")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    # Try reading with comma, then semicolon
    try:
        # Check if it's the INDEP file which has a special structure
        if "indep" in path.lower():
             # Try header=2 (3rd line) which contains 'parameter name'
             df = pd.read_csv(path, sep=',', header=2, index_col=2)
        else:
             df = pd.read_csv(path, sep=',', index_col=0)
             
        if df.shape[1] < 1: # Empty or wrong sep
            raise ValueError
    except:
        try:
            if "indep" in path.lower():
                 df = pd.read_csv(path, sep=';', header=2, index_col=2)
            else:
                 df = pd.read_csv(path, sep=';', index_col=0)
        except Exception as e:
            print(f"Error reading file check delimiters: {e}")
            return
            
    print(f"Columns found: {df.columns.tolist()}")
    
    resources_to_check = ['GASOLINE', 'DIESEL', 'LFO', 'JET_FUEL', 'GAS', 'COAL']
    
    # Map for column names if they differ slightly (e.g. avail_local vs avail_exterior)
    cols_to_print = []
    
    # Try to find relevant columns
    possible_avail = [col for col in df.columns if 'avail' in col.lower()]
    possible_cop = [col for col in df.columns if 'c_op' in col.lower() or 'cost' in col.lower()] # catched c_op_local or c_op_exterior
    
    cols_to_print.extend(possible_avail)
    cols_to_print.extend(possible_cop)
    
    if not cols_to_print:
        print("No columns containing 'avail' or 'c_op' found.")
        print(f"Columns found: {df.columns.tolist()}")

    found_any = False
    for res in resources_to_check:
        if res in df.index:
            found_any = True
            print(f"\nResource: {res}")
            for col in cols_to_print:
                try:
                    val = df.loc[res, col]
                    print(f"  {col}: {val}")
                except:
                    pass
        else:
            # print(f"Resource {res} not found in file.")
            pass
            
    if not found_any:
        print("\nNone of the specified fossil resources were found in this file.")
        if "indep" not in path.lower():
            print(f"Resources found in file: {df.index.tolist()}")


if __name__ == "__main__":
    base_dir = os.getcwd()
    
    # Check User Specified Files
    file_2017 = os.path.join(base_dir, 'Data', '2017', 'FI', 'Resources.csv')
    file_2035 = os.path.join(base_dir, 'Data', '2035', 'FI', 'Resources.csv')
    
    print("=== Checking User Specified Files ===")
    check_file(file_2017, "2017 (Data/2017/FI/Resources.csv)")
    print("\n")
    check_file(file_2035, "2035 (Data/2035/FI/Resources.csv)")
    
    # Check INDEP files as extra helpful info if resources were missing in FI files
    print("\n=== Checking INDEP Files (where fossils usually reside) ===")
    file_indep_2017 = os.path.join(base_dir, 'Data', '2017', '00_INDEP', 'Resources_indep.csv')
    check_file(file_indep_2017, "2017 INDEP (Data/2017/00_INDEP/Resources_indep.csv)")

