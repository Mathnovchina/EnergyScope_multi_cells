import pandas as pd
from pathlib import Path
import sys

# Define paths
workspace_root = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")
case_study_path = workspace_root / "case_studies/FI/calib_2017_finland_v9"
output_path = case_study_path / "outputs"
assets_path = output_path / "Assets.csv"
year_balance_path = output_path / "Year_balance.csv"
technologies_path = workspace_root / "Data/2017/FI/Technologies.csv"
run_script_path = workspace_root / "scripts/run_calib_case.py"

def check_f_perc():
    print("--- 1. Checking f_perc status ---")
    if not run_script_path.exists():
        print(f"Error: {run_script_path} not found.")
        return False
    
    with open(run_script_path, 'r') as f:
        content = f.read()
        if "'f_perc': True" in content:
            print("  [OK] 'f_perc': True found in run_calib_case.py")
            return True
        elif "'f_perc': False" in content:
            print("  [WARNING] 'f_perc': False found in run_calib_case.py")
            return False
        else:
            print("  [?] Could not determine f_perc status from simple text search.")
            return None

def analyze_assets_consumption():
    print("\n--- 2. Analyzing Assets and Consumption ---")
    
    # Load Assets
    if not assets_path.exists():
        print(f"Error: {assets_path} not found.")
        return
    
    assets_df = pd.read_csv(assets_path, index_col=0)
    # Filter for Finland region if necessary, but usually index is Tech
    # The format might be Tech, [metrics...] or something. Let's inspect columns if needed.
    # Assuming standard EnergyScope output: Index=Tech, Columns=[F, f_min, f_max, ...]
    
    # Load Year Balance to see consumption (optional, but requested)
    if year_balance_path.exists():
        yb_df = pd.read_csv(year_balance_path, index_col=0)
        # Identify top consumers?
        # Year_balance usually has columns like 'Electricity', 'Heat', etc.
        pass

    # Load Technologies input to compare constraints
    tech_input_df = pd.read_csv(technologies_path, index_col=0)
    
    # Define groups to check
    # Cars
    cars = ['CAR_GASOLINE', 'CAR_DIESEL', 'CAR_BEV', 'CAR_PHEV', 'CAR_HEV', 'CAR_FUEL_CELL', 'CAR_METHANOL']
    # Trucks
    trucks = ['TRUCK_DIESEL', 'TRUCK_NG', 'TRUCK_ELEC', 'TRUCK_FUEL_CELL']
    # Industry
    ind_heat = ['IND_BOILER_WOOD', 'IND_COGEN_WOOD', 'IND_BOILER_COAL', 'IND_BOILER_GAS', 'IND_BOILER_OIL', 'IND_BOILER_WASTE']
    # DHN
    dhn_heat = ['DHN_BOILER_WOOD', 'DHN_COGEN_WOOD', 'DHN_BOILER_COAL', 'DHN_COGEN_COAL', 'DHN_BOILER_GAS', 'DHN_COGEN_GAS', 'DHN_BOILER_OIL']

    groups = {
        'Cars': cars,
        'Trucks': trucks,
        'Industry Heat': ind_heat,
        'District Heating': dhn_heat
    }

    for group_name, techs in groups.items():
        print(f"\n--- Analysis: {group_name} ---")
        
        # Get actual capacities (F)
        actual_F = {}
        total_F = 0
        for t in techs:
            if t in assets_df.index:
                val = assets_df.loc[t, 'F']
                actual_F[t] = val
                total_F += val
            else:
                actual_F[t] = 0.0
        
        # Print shares
        print(f"Total Capacity (GW): {total_F:.4f}")
        for t in techs:
            share = actual_F[t] / total_F if total_F > 0 else 0
            
            # Get constraint info
            input_fmin_perc = "N/A"
            input_fmax_perc = "N/A"
            
            if t in tech_input_df.index:
                if 'fmin_perc' in tech_input_df.columns:
                    val = tech_input_df.loc[t, 'fmin_perc']
                    if not pd.isna(val): input_fmin_perc = f"{val:.4f}"
                if 'fmax_perc' in tech_input_df.columns:
                    val = tech_input_df.loc[t, 'fmax_perc']
                    if not pd.isna(val): input_fmax_perc = f"{val:.4f}"

            print(f"  {t:<20} | F: {actual_F[t]:.4f} | Share: {share:.2%} | Limit: [{input_fmin_perc}, {input_fmax_perc}]")
            
            # Alert if 0 but constraint exists
            if actual_F[t] < 1e-4 and input_fmin_perc != "N/A" and float(input_fmin_perc) > 0:
                 print(f"    [ALERT] {t} is 0 but fmin_perc is {input_fmin_perc}!")


if __name__ == "__main__":
    check_f_perc()
    analyze_assets_consumption()
