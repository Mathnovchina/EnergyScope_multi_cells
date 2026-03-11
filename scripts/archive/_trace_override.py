"""Trace the FI override chain for NUCLEAR to understand what values reach the .dat."""
import sys, os
sys.path.insert(0, os.getcwd())

import pandas as pd
import numpy as np
from esmc.utils.region import clean_indices

CSV_SEPARATOR = ','

# Step 1: Read REF_REGION exactly as region.py does for ref_region=True
ref_path = 'Data/2017/02_REF_REGION/Technologies.csv'
df_ref = pd.read_csv(ref_path, sep=CSV_SEPARATOR, header=[0], index_col=[3], skiprows=[1],
                     dtype={'fmin_perc': np.float64, 'f_min': np.float64}).drop(columns=['Comment'], errors='ignore')
df_ref = clean_indices(df_ref)
print("=== STEP 1: REF_REGION (after read + clean) ===")
print(f"NUCLEAR: f_min={df_ref.loc['NUCLEAR','f_min']}, f_max={df_ref.loc['NUCLEAR','f_max']}, fmin_perc={df_ref.loc['NUCLEAR','fmin_perc']}, fmax_perc={df_ref.loc['NUCLEAR','fmax_perc']}")
print(f"  f_min dtype: {type(df_ref.loc['NUCLEAR','f_min'])}")
print(f"  f_max dtype: {type(df_ref.loc['NUCLEAR','f_max'])}")

# Step 2: Read FI Technologies.csv exactly as region.py does for ref_region=False
fi_path = 'Data/2017/FI/Technologies.csv'
df_fi = pd.read_csv(fi_path, sep=CSV_SEPARATOR, header=[0], index_col=[0]).dropna(how='all', axis=1)
df_fi = clean_indices(df_fi)
print("\n=== STEP 2: FI Technologies.csv (after read + clean) ===")
print(f"Columns: {list(df_fi.columns)}")
print(f"Index: {list(df_fi.index)}")
print(f"NUCLEAR row:\n{df_fi.loc['NUCLEAR']}")
print(f"  f_min dtype: {type(df_fi.loc['NUCLEAR','f_min'])}")
print(f"  f_max dtype: {type(df_fi.loc['NUCLEAR','f_max'])}")

# Step 3: Simulate update
print("\n=== STEP 3: After df_ref.update(df_fi) ===")
df_ref_copy = df_ref.copy()
df_ref_copy.update(df_fi)
print(f"NUCLEAR: f_min={df_ref_copy.loc['NUCLEAR','f_min']}, f_max={df_ref_copy.loc['NUCLEAR','f_max']}, fmin_perc={df_ref_copy.loc['NUCLEAR','fmin_perc']}, fmax_perc={df_ref_copy.loc['NUCLEAR','fmax_perc']}")

# Check if there are duplicate NUCLEAR entries in REF_REGION
print(f"\nNUCLEAR appears {(df_ref.index == 'NUCLEAR').sum()} time(s) in REF_REGION index")
print(f"NUCLEAR appears {(df_fi.index == 'NUCLEAR').sum()} time(s) in FI index")

# Also check what columns overlap
print(f"\nREF_REGION columns: {list(df_ref.columns)}")
print(f"FI columns: {list(df_fi.columns)}")
print(f"Overlap: {list(set(df_ref.columns) & set(df_fi.columns))}")
