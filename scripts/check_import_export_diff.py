import pandas as pd
import numpy as np
import os

base_dir = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data"

def compare_csv(rel_path, index_col=0):
    path_17 = os.path.join(base_dir, "2017", rel_path)
    path_35 = os.path.join(base_dir, "2035", rel_path)
    
    try:
        df17 = pd.read_csv(path_17, index_col=index_col, comment='#', skipinitialspace=True)
        df35 = pd.read_csv(path_35, index_col=index_col, comment='#', skipinitialspace=True)
        
        # Resources.csv checks
        if "Resources.csv" in rel_path:
             print(f"\n--- Checking {rel_path} ---")
             # Row 3 (index 2) is the header "Category, Subcategory, parameter name..."
             df17 = pd.read_csv(path_17, header=2, index_col='parameter name', skipinitialspace=True)
             df35 = pd.read_csv(path_35, header=2, index_col='parameter name', skipinitialspace=True)
             
             cols = ['c_op_local', 'avail_exterior'] 
             
             # Resources to check
             resources = ['ELECTRICITY', 'GASOLINE', 'DIESEL', 'LFO', 'COAL', 'GAS', 'WOOD', 'NG']
             
             for res in resources:
                 if res in df17.index and res in df35.index:
                     v17 = df17.loc[res][cols]
                     v35 = df35.loc[res][cols]
                     
                     print(f"{res} (2017 vs 2035):")
                     print(f"  2017 cost: {v17.get('c_op_local', 'N/A')}")
                     print(f"  2035 cost: {v35.get('c_op_local', 'N/A')}")
                     
                     if np.isclose(float(v17['c_op_local']), float(v35['c_op_local'])):
                         print("  -> PRICE IDENTICAL")
                     else:
                         print("  -> PRICE DIFFERS")
                         
        # Network exchanges
        elif "Network_exchanges.csv" in rel_path:
             print(f"\n--- Checking {rel_path} ---")
             # Just strict equality of the whole dataframe
             if df17.equals(df35):
                 print("Entire file is IDENTICAL to 2035.")
             else:
                 print("File differs.")
                 
    except Exception as e:
        print(f"Error comparing {rel_path}: {e}")

compare_csv(r"02_REF_REGION\Resources.csv", index_col=2) # Index is 'Resources name' usually col 2
print("\n")
compare_csv(r"01_EXCH\Network_exchanges.csv", index_col=0) # Index usually first col
