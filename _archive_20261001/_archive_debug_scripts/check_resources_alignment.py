import pandas as pd
import os

def check_and_align_resources():
    path_2017 = os.path.join('Data', '2017', 'FI', 'Resources.csv')
    path_2035 = os.path.join('Data', '2035', 'FI', 'Resources.csv')

    # Read 2035 first as reference
    try:
        # Try finding delimiter
        with open(path_2035, 'r') as f:
            header_2035 = f.readline()
        
        delim_2035 = ';' if ';' in header_2035 else ','
        print(f"Reading 2035 with delimiter '{delim_2035}'")
        
        df_2035 = pd.read_csv(path_2035, sep=delim_2035, index_col=0, comment='#')
        resources_2035 = df_2035.index.tolist()
        print(f"2035 Resources ({len(resources_2035)}): {resources_2035}")
        
    except Exception as e:
        print(f"Error reading 2035 file: {e}")
        return

    # Read 2017
    try:
        with open(path_2017, 'r') as f:
            header_2017 = f.readline()
        
        delim_2017 = ';' if ';' in header_2017 else ','
        print(f"Reading 2017 with delimiter '{delim_2017}'")

        df_2017 = pd.read_csv(path_2017, sep=delim_2017, index_col=0, comment='#')
        resources_2017 = df_2017.index.tolist()
        print(f"2017 Resources ({len(resources_2017)}): {resources_2017}")

    except Exception as e:
        print(f"Error reading 2017 file: {e}")
        return

    # Compare
    if resources_2017 == resources_2035 and len(df_2017.columns) == len(df_2035.columns):
        print("Resources match perfectly.")
    else:
        print("Resources do NOT match. Aligning 2017 to 2035...")
        
        # Align 2017 to 2035 structure
        # Reindex checks for matching index, filling missing with NA (which we can fill with 0 or defaults)
        # We also need to match columns
        
        # Create a new DataFrame with 2035 index and columns
        df_aligned = pd.DataFrame(index=df_2035.index, columns=df_2035.columns)
        
        # Fill with data from df_2017 where indices and columns match
        # We first check common indices
        common_indices = df_2017.index.intersection(df_2035.index)
        common_cols = df_2017.columns.intersection(df_2035.columns)
        
        print(f"Common indices: {len(common_indices)}")
        print(f"Common columns: {len(common_cols)}")

        # Copy data
        for idx in common_indices:
            for col in common_cols:
                df_aligned.at[idx, col] = df_2017.at[idx, col]
        
        # Fill NaN with default values from 2035 or 0? 
        # User said "potentially zeroing out values if unsure"
        # Since it's resources, missing values often mean not available or 0 cost if not used.
        # However, for cost parameters like c_op, 0 might be wrong.
        # Let's try to fill missing values for a resource with values from 2035 if the resource is new?
        # Or just fill 0. 
        # Let's fill 0 for now as requested "zeroing out values if unsure".
        
        df_aligned = df_aligned.fillna(0)
        
        # Save back to 2017 file
        # Ensure we use the same format as 2035 (likely semicolon if that's standard, but user said 2017 was comma)
        # Let's stick to the delimiter of 2035 to be consistent across years if we are aligning.
        
        print(f"Saving aligned 2017 resources to {path_2017}")
        df_aligned.to_csv(path_2017, sep=delim_2035)
        print("Done.")

        # Verify
        df_check = pd.read_csv(path_2017, sep=delim_2035, index_col=0, comment='#')
        print(f"New 2017 Resources ({len(df_check.index)}): {df_check.index.tolist()}")
        if df_check.index.tolist() == resources_2035:
            print("Verification successful: Indices match.")

if __name__ == "__main__":
    check_and_align_resources()
