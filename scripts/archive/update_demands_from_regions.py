import pandas as pd
import os

def update_demands():
    # Paths
    source_path = os.path.join('Data', 'exogenous_data', 'regions', 'Demands.csv')
    target_path = os.path.join('Data', '2017', 'FI', 'Demands.csv')
    
    # Read source
    print(f"Reading source from {source_path}")
    # The source file has no headers in the first line strictly speaking? 
    # Let's check the format again. 
    # "2015,AL,ELECTRICITY,..."
    # The first few lines of the file I read earlier showed:
    # ,,,HOUSEHOLDS,SERVICES,INDUSTRY,TRANSPORTATION
    # 2015,AL,ELECTRICITY,...
    # So line 0 is empty-ish headers? No, line 0 is ",,,HOUSEHOLDS..."
    
    df_source = pd.read_csv(source_path, header=0)
    # The header is likely: Unnamed: 0, Unnamed: 1, Unnamed: 2, HOUSEHOLDS, SERVICES, INDUSTRY, TRANSPORTATION
    # Let's inspect columns or just hardcode if it's tricky.
    # But based on `read_file` output:
    # ,,,HOUSEHOLDS,SERVICES,INDUSTRY,TRANSPORTATION
    # So the columns are likely: "Unnamed: 0", "Unnamed: 1", "Unnamed: 2", "HOUSEHOLDS", ...
    # Unnamed: 0 is Year, Unnamed: 1 is Region, Unnamed: 2 is Parameter
    
    df_source.rename(columns={'Unnamed: 0': 'Year', 'Unnamed: 1': 'Region', 'Unnamed: 2': 'Parameter'}, inplace=True)
    
    # Filter for FI 2015
    df_fi_2015 = df_source[(df_source['Year'] == 2015) & (df_source['Region'] == 'FI')]
    
    if df_fi_2015.empty:
        print("No data found for FI 2015 in source file!")
        return

    print("Found FI 2015 data:")
    print(df_fi_2015)

    # Read target
    print(f"Reading target from {target_path}")
    df_target = pd.read_csv(target_path)
    # Target columns: Category,Subcategory,parameter name,HOUSEHOLDS,SERVICES,INDUSTRY,TRANSPORTATION,Units
    
    # Update target
    for index, row in df_target.iterrows():
        param = row['parameter name']
        
        # Find corresponding row in source
        source_row = df_fi_2015[df_fi_2015['Parameter'] == param]
        
        if not source_row.empty:
            # Update values
            df_target.at[index, 'HOUSEHOLDS'] = source_row.iloc[0]['HOUSEHOLDS']
            df_target.at[index, 'SERVICES'] = source_row.iloc[0]['SERVICES']
            df_target.at[index, 'INDUSTRY'] = source_row.iloc[0]['INDUSTRY']
            df_target.at[index, 'TRANSPORTATION'] = source_row.iloc[0]['TRANSPORTATION']
            print(f"Updated {param}")
        else:
            print(f"Warning: Parameter {param} not found in source data.")

    # Save
    print(f"Saving updated demands to {target_path}")
    df_target.to_csv(target_path, index=False)
    print("Done.")

if __name__ == "__main__":
    update_demands()
