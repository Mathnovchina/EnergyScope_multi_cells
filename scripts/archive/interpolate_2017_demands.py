
import pandas as pd
import os
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIONS_DATA = os.path.join(BASE_DIR, 'Data', 'exogenous_data', 'regions', 'Demands.csv')
DEST_FILE = os.path.join(BASE_DIR, 'Data', '2017', 'FI', 'Demands.csv')

def interpolate_demands():
    print("Loading Regional Data...")
    # Load source data (no header in file usually, based on previous exploration)
    # The file has: ,,,HOUSEHOLDS,SERVICES,INDUSTRY,TRANSPORTATION (line 0)
    # Then data lines
    df_regions = pd.read_csv(REGIONS_DATA)
    # Rename columns to match expected structure if needed, but read_csv with header=0 likely picks up keys
    # Keys should be: Unnamed: 0 (Year), Unnamed: 1 (Region), Unnamed: 2 (Parameter), then HOUSEHOLDS...
    
    # Let's clean up column names
    df_regions.columns.values[0] = 'Year'
    df_regions.columns.values[1] = 'Region'
    df_regions.columns.values[2] = 'Parameter'
    
    # Filter for FI
    df_fi = df_regions[df_regions['Region'] == 'FI'].copy()
    
    # Get 2015 and 2020
    df_2015 = df_fi[df_fi['Year'] == 2015].set_index('Parameter')
    df_2020 = df_fi[df_fi['Year'] == 2020].set_index('Parameter')
    
    # Prepare interpolation
    # Formula: Val_2017 = Val_2015 + (Val_2020 - Val_2015) * (2/5)
    ratio = 2.0 / 5.0
    
    # Load destination file
    print(f"Loading destination file: {DEST_FILE}")
    df_dest = pd.read_csv(DEST_FILE)
    
    updated_count = 0
    
    for idx, row in df_dest.iterrows():
        param = row['parameter name']
        if param in df_2015.index and param in df_2020.index:
            # Columns to interpolate
            cols = ['HOUSEHOLDS', 'SERVICES', 'INDUSTRY', 'TRANSPORTATION']
            
            for col in cols:
                val_15 = df_2015.loc[param, col]
                val_20 = df_2020.loc[param, col]
                
                # Simple linear interpolation
                val_17 = val_15 + (val_20 - val_15) * ratio
                
                # Update destination dataframe
                df_dest.at[idx, col] = val_17
            
            updated_count += 1
            # print(f"Interpolated {param}")

    print(f"Updated {updated_count} parameters with interpolated 2017 values.")
    
    # Save
    df_dest.to_csv(DEST_FILE, index=False)
    print("Saved updated Demands.csv")

if __name__ == "__main__":
    interpolate_demands()
