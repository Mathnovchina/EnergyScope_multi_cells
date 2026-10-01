import pandas as pd
import os

# Paths
ref_tech_path = r'Data/2017/02_REF_REGION/Technologies.csv'
fi_tech_path = r'Data/2017/FI/Technologies.csv'

# Load reference technologies
# Based on the file content, header is at row 0 (1-based line 1)
# And the index column seems to be 'Technologies param'
try:
    df_ref = pd.read_csv(ref_tech_path, sep=',', comment='#') # Assuming comma and comments
    print(f"Loaded {ref_tech_path} with shape {df_ref.shape}")
    print(f"Columns: {df_ref.columns.tolist()}")
    
    # Check if 'Technologies param' exists
    if 'Technologies param' in df_ref.columns:
        df_ref.set_index('Technologies param', inplace=True)
        print("Set index to 'Technologies param'")
    else:
        print("Column 'Technologies param' not found in ref file")

    # Check for duplicates in index
    if df_ref.index.duplicated().any():
        print("Duplicates found in index:")
        print(df_ref.index[df_ref.index.duplicated()].tolist())
    else:
        print("No duplicates in index of ref file")

    # Check for SYN_METHANATION
    if 'SYN_METHANATION' in df_ref.index:
        print("SYN_METHANATION is in ref index")
    else:
        print("SYN_METHANATION is NOT in ref index")
        # Check if there are similar strings (whitespace issues)
        similar = [i for i in df_ref.index if 'SYN_METHANATION' in str(i)]
        print(f"Entries containing 'SYN_METHANATION': {similar}")

except Exception as e:
    print(f"Error loading ref file: {e}")

# Load FI technologies
try:
    df_fi = pd.read_csv(fi_tech_path, sep=',')
    print(f"Loaded {fi_tech_path} with shape {df_fi.shape}")
    
    if 'Technologies param' in df_fi.columns:
        df_fi.set_index('Technologies param', inplace=True)
        print("Set index to 'Technologies param' for FI file")
    
    # attempt update
    if 'SYN_METHANATION' in df_fi.index: 
         print(f"SYN_METHANATION in FI file: {df_fi.loc['SYN_METHANATION']}")
    
    # Update logic (simulated)
    # The actual update logic depends on the code, but let's try standard pandas update
    df_ref.update(df_fi)
    
    if 'SYN_METHANATION' in df_ref.index:
        print("After update, SYN_METHANATION in ref:")
        print(df_ref.loc['SYN_METHANATION'])
        
except Exception as e:
    print(f"Error loading FI file: {e}")
