
import pandas as pd
import os

# Paths
BASE_DIR = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
CALIB_FILE = os.path.join(BASE_DIR, 'Data', 'exogenous_data', 'Finland_Calibration_MASTER.xlsx')

def main():
    print("Updating Nuclear and Wind restrictions for 2035/2050 based on Calibration File...")
    
    try:
        tech_caps_df = pd.read_excel(CALIB_FILE, sheet_name='6_Technology_Capacities')
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # Years to update
    years = [2035, 2050]
    
    for year in years:
        tech_path = os.path.join(BASE_DIR, 'Data', str(year), 'FI', 'Technologies.csv')
        if not os.path.exists(tech_path):
            print(f"File not found: {tech_path}")
            continue
            
        print(f"Processing {year}...")
        curr_tech = pd.read_csv(tech_path, index_col=0) # index is Technologies param
        curr_tech.index = curr_tech.index.str.strip()
        
        for _, row in tech_caps_df.iterrows():
            tech_name = str(row['Technology']).strip()
            
            # Identify columns in Excel: Year_2035, f_max_2035, etc.
            cap_col = f'Year_{year}'
            fmax_col = f'f_max_{year}'
            
            cap_val = row[cap_col] if cap_col in row else None
            fmax_val = row[fmax_col] if fmax_col in row else None
            
            if tech_name in curr_tech.index:
                # Update f_min with expected capacity (Year_XXXX)
                if pd.notnull(cap_val):
                    curr_tech.loc[tech_name, 'f_min'] = cap_val
                    
                # Update f_max if provided
                if pd.notnull(fmax_val):
                    curr_tech.loc[tech_name, 'f_max'] = fmax_val
                
                # Validation
                f_min = curr_tech.loc[tech_name, 'f_min']
                f_max = curr_tech.loc[tech_name, 'f_max']
                
                if f_min > f_max:
                    # Depending on policy: usually relax f_max to f_min if f_min is the "known reality"
                    # specially for Nuclear or existing Wind
                    print(f"  Warning: {tech_name} f_min ({f_min}) > f_max ({f_max}). Setting f_max = f_min.")
                    curr_tech.loc[tech_name, 'f_max'] = f_min
        
        curr_tech.to_csv(tech_path)
        print(f"Updated {tech_path}")

if __name__ == "__main__":
    main()
