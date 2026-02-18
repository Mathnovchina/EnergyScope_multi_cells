
import sys
import pandas as pd
from pathlib import Path
import logging

# Add project root to sys.path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc

def run_debug_iis():
    # Configuration for Finland 2017 Calibration - v9
    config = {
        'case_study': 'calib_2017_finland_v9',
        'comment': 'Debug Infeasibility IIS for Finland 2017 v9',
        'regions_names': ['FI'],
        'gwp_limit_overall': None, 
        'f_perc': True,
        'year': 2017,
        're_share_primary': None
    }
    
    print("Initializing ESMC model for Finland 2017 (IIS Debug Mode)...")
    logging.getLogger().setLevel(logging.INFO)
    
    # Initialize the model with 12 Typical Days
    my_model = Esmc(config, nbr_td=12)
    
    print("Reading independent data...")
    my_model.read_data_indep()
    
    print("Initializing regions...")
    my_model.init_regions()
    
    print("Initializing temporal aggregation...")
    my_model.init_ta(algo='kmedoid') 
    
    print("Printing data files...")
    my_model.print_td_data()
    my_model.print_data(indep=True)

    print("Setting up AMPL problem...")
    my_model.set_esom(solver='cplex') 
    
    # Set CPLEX option to find IIS
    # iisfind=1 : Find a minimal conflict
    print("Setting cplex_options...")
    try:
        # Access the AMPL object directly through esom
        ampl = my_model.esom.ampl
        # Remove iisfind, focus on getting a solution even if bad
        ampl.setOption('cplex_options', 'mipdisplay=2') 
        ampl.setOption('show_stats', 1)
        ampl.setOption('presolve', 0) 
    except Exception as e:
        print(f"Error setting AMPL options: {e}")
        return

    print("Solving model...")
    try:
        my_model.solve_esom()
    except Exception as e:
        print(f"Solve returned error: {e}")

    print("\n--- Cost Analysis (Debugging Numeric Issue) ---")
    
    # Check identifying high cost components
    try:
        # Export high cost items to CSV
        cost_cmd = """
        printf "Type,Name,Cost,Capacity_F,Unit_Cost_cinv\\n" > cost_debug.csv;
        
        # Check Investment Costs
        for {c in REGIONS, j in TECHNOLOGIES} {
            if C_inv[c,j] > 1e12 then {
                 printf "C_inv,%s.%s,%g,%g,%g\\n", c, j, C_inv[c,j], F[c,j], c_inv[c,j] >> cost_debug.csv;
            }
        }
        """
        ampl.eval(cost_cmd)
        
        if Path("cost_debug.csv").exists():
            print("\nReading Cost Analysis report...")
            df_cost = pd.read_csv("cost_debug.csv")
            df_cost = df_cost.sort_values(by="Cost", ascending=False)
            
            print("\nTop 20 Highest Costs:")
            print(df_cost.head(20).to_string(index=False))
            
        else:
             print("No cost report generated.")

    except Exception as e:
        print(f"Error analyzing costs: {e}")

    print("Done.")

    print("Done.")

if __name__ == "__main__":
    run_debug_iis()
