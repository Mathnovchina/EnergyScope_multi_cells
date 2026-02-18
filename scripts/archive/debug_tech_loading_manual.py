import pandas as pd
from pathlib import Path

path_ref = Path("Data/2017/02_REF_REGION/Technologies.csv")
path_fi = Path("Data/2017/FI/Technologies.csv")

# 1. Load Ref
print("Loading Ref...")
try:
    # Mimic Region.read_tech for ref_region
    df_ref = pd.read_csv(path_ref, sep=',', header=[0], index_col=[3], skiprows=[1]).drop(columns=['Comment'], errors='ignore')
    # clean_indices
    df_ref.index = df_ref.index.str.strip()
    df_ref.columns = df_ref.columns.str.strip()
    
    if 'SYN_METHANATION' in df_ref.index:
        print(f"Ref['SYN_METHANATION'] f_max: {df_ref.loc['SYN_METHANATION', 'f_max']}")
    else:
        print("Ref['SYN_METHANATION'] NOT FOUND!")
        # Print indices close to SYN_METHANATION
        print([i for i in df_ref.index if 'METH' in str(i)])

except Exception as e:
    print(f"Error loading Ref: {e}")

# 2. Load FI
print("\nLoading FI...")
try:
    # Mimic Region.read_tech for non-ref
    df_fi = pd.read_csv(path_fi, sep=',', header=[0], index_col=[0]).dropna(how='all', axis=1)
    df_fi.index = df_fi.index.str.strip()
    df_fi.columns = df_fi.columns.str.strip()

    if 'SYN_METHANATION' in df_fi.index:
        print(f"FI['SYN_METHANATION'] f_max: {df_fi.loc['SYN_METHANATION', 'f_max']}")
    else:
        print("FI['SYN_METHANATION'] NOT FOUND!")

except Exception as e:
    print(f"Error loading FI: {e}")

# 3. Update
print("\nUpdating...")
try:
    # Copy Ref
    df_merged = df_ref.copy()
    # Update
    df_merged.update(df_fi)
    
    val = df_merged.loc['SYN_METHANATION', 'f_max']
    print(f"Resulting f_max: {val}")
    
    if val == 0:
        print("UPDATE SUCCESSFUL in standalone test.")
    else:
        print("UPDATE FAILED in standalone test.")

except Exception as e:
    print(f"Error updating: {e}")
