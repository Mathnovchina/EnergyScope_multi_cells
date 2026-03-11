
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Define root
workspace_root = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")

CSV_SEPARATOR = ','

# Paths
ref_path = workspace_root / "Data/2017/02_REF_REGION/Technologies.csv"
fi_path = workspace_root / "Data/2017/FI/Technologies.csv"

def clean_indices(df):
    """
    Cleans the index of the dataframe. If index is MultiIndex, levels are stripped.
    If index is single index, it is stripped.
    """
    if isinstance(df.index, pd.MultiIndex):
        # Using set_levels to clean MultiIndex levels
        cleaned_levels = [level.astype(str).str.strip() for level in df.index.levels]
        df.index = df.index.set_levels(cleaned_levels, level=np.arange(len(df.index.levels)))
    else:
        df.index = df.index.astype(str).str.strip()
    return df

print(f"Reading ref from {ref_path}")
try:
    # Mimicking esmc logic for Ref Region
    # Note: ref_region read uses skiprows=[1] which skips unit row usually
    df_ref = pd.read_csv(ref_path, sep=CSV_SEPARATOR, header=[0], index_col=[3], skiprows=[1],
                     dtype={'fmin_perc': np.float64, 'f_min': np.float64}).drop(
                    columns=['Comment']
                    , errors='ignore')
    df_ref = clean_indices(df_ref)
    
    if 'SYN_METHANATION' in df_ref.index:
        print(f"Found SYN_METHANATION in Ref Region.")
        print('Before Update:')
        print(df_ref.loc['SYN_METHANATION', ['f_min', 'f_max']])
    else:
        print("SYN_METHANATION NOT FOUND in Ref Region.")

except Exception as e:
    print(f"Error reading Ref Region: {e}")
    sys.exit(1)

print(f"Reading fi from {fi_path}")
try:
    # Mimicking esmc logic for Local Region
    df_fi = pd.read_csv(fi_path, sep=CSV_SEPARATOR, header=[0], index_col=[0]).dropna(how='all', axis=1)
    df_fi = clean_indices(df_fi)

    if 'SYN_METHANATION' in df_fi.index:
        print(f"Found SYN_METHANATION in FI.")
        print('FI Value:')
        print(df_fi.loc['SYN_METHANATION', ['f_min', 'f_max']])
    else:
        print("SYN_METHANATION NOT FOUND in FI.")
    
    # Update logic
    if 'SYN_METHANATION' in df_ref.index and 'SYN_METHANATION' in df_fi.index:
        print("Applying update...")
        # Check alignment of columns
        print("Columns in Ref:", df_ref.columns)
        print("Columns in FI:", df_fi.columns)
        
        df_ref.update(df_fi)
        print("Updated SYN_METHANATION in Ref Region:")
        print(df_ref.loc['SYN_METHANATION', ['f_min', 'f_max']])
    else:
        print("Skipping update due to missing index.")

except Exception as e:
    print(f"Error reading FI: {e}")
