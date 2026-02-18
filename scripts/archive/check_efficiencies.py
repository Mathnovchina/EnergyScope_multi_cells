import pandas as pd
import os

# Paths
current_layers_path = r'Data/2017/00_INDEP/Layers_in_out.csv'
# v8_path = r'case_studies/FI/calib_2017_finland_v8_no_coal_us/inputs/Layers_in_out.csv' # Assuming inputs folder exists? Based on prompt "Usually case_studies/.../inputs/Layers_in_out.csv exists"

# Standard values as per user
standards = {
    'CAR_GASOLINE': {'input': 'GASOLINE', 'output': 'MOB_PRIVATE', 'expected_eff': 0.25}, # 0.2-0.3
    'TRUCK_DIESEL': {'input': 'DIESEL', 'output': 'MOB_FREIGHT_ROAD', 'expected_eff': 0.75}, # 0.5-1.0
    'IND_BOILER_WOOD': {'input': 'WOOD', 'output': 'HEAT_HIGH_T', 'expected_eff': 0.85} # 0.8-0.9
}

def check_efficiency(df, tech, input_res, output_res):
    try:
        # Check if tech exists
        if tech not in df.index:
            return f"Tech {tech} not found in index."
        
        # Get input and output values
        # Input is usually negative, output positive? 
        # In Layers_in_out.csv:
        # CAR_GASOLINE: GASOLINE should be -1 (or negative), MOB_PRIVATE should be 1?
        # Let's check the convention.
        # Usually: Input is 1 if it uses 1 unit of input to produce eff units of output?
        # Or: Input is -1/eff, output is 1?
        
        # Let's read the row for CAR_GASOLINE to see convention
        row = df.loc[tech]
        
        inp_val = row.get(input_res, 0)
        out_val = row.get(output_res, 0)

        # Convention in EnergyScope:
        # Often defined as consumption per unit of production.
        # If output (e.g. MOB_PRIVATE) is 1.
        # Input (e.g. GASOLINE) is the amount consumed.
        # So Efficiency = Output / Input (abs)
        
        return {
            'input_res': input_res,
            'input_val': inp_val,
            'output_res': output_res,
            'output_val': out_val
        }

    except Exception as e:
        return str(e)

def load_layers(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return None
    
    # The file has "param layers_in_out:," at the start of the header, which is weird for CSV.
    # It seems to be a mix of AMPL and CSV.
    # Let's try reading with pandas, skipping the "param layers_in_out:," part if necessary.
    
    try:
        # First read the header to see what it looks like
        with open(path, 'r') as f:
            header = f.readline().strip()
            
        # The header starts with "param layers_in_out:,". We can probably just read it as CSV but the first column name is messy.
        df = pd.read_csv(path)
        
        # Rename the first column to 'Technology' if it looks like "param layers_in_out:"
        if 'param layers_in_out:' in df.columns[0]:
            df.rename(columns={df.columns[0]: 'Technology'}, inplace=True)
            
        df.set_index('Technology', inplace=True)
        return df
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

def main():
    print("Checking current Layers_in_out.csv...")
    df_current = load_layers(current_layers_path)
    
    if df_current is not None:
        for tech, std in standards.items():
            print(f"\n--- Checking {tech} ---")
            res = check_efficiency(df_current, tech, std['input'], std['output'])
            print(res)
            
            if isinstance(res, dict):
                in_val = float(res['input_val'])
                out_val = float(res['output_val'])
                
                # Calculating efficiency
                # Assuming standard EnergyScope: positive is output, negative is input.
                # If both are positive, maybe one is input and one is output defined differently?
                # User says: "CAR_GASOLINE: GASOLINE input, MOB_PRIVATE output"
                
                # Check signs
                if out_val != 0 and in_val != 0:
                     # Usually one is 1 (the main output or input).
                     # Efficiency = Output / Input
                     efficiency = abs(out_val / in_val)
                     print(f"Calculated Efficiency: {efficiency:.4f}")
                     print(f"Expected Efficiency: ~{std['expected_eff']}")
                else:
                    print("Could not calculate efficiency (one value is 0)")

    # Check for v8 backup
    # Based on user content "Usually case_studies/.../inputs/Layers_in_out.csv exists"
    # User mentioned v8 path: case_studies/FI/calib_2017_finland_v8_no_coal_us/
    v8_possible_path = r'case_studies/FI/calib_2017_finland_v8_no_coal_us/inputs/Layers_in_out.csv' # Guessing 'inputs'
    if not os.path.exists(v8_possible_path):
         # Try looking for any csv in that folder or subfolders?
         # Or just skip
         print(f"\nBackup file not found at {v8_possible_path}")
    else:
        print(f"\nChecking backup {v8_possible_path}...")
        df_v8 = load_layers(v8_possible_path)
        if df_v8 is not None:
             for tech, std in standards.items():
                print(f"\n--- Checking {tech} (v8) ---")
                res = check_efficiency(df_v8, tech, std['input'], std['output'])
                print(res)

if __name__ == "__main__":
    main()
