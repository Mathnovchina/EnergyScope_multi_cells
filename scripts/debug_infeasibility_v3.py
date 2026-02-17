
import sys
import pandas as pd
from pathlib import Path
import logging

# Add project root to sys.path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc

def run_debug_infeasibility():
    # Configuration for Finland 2017 Calibration
    # Using v9 as it's the one failing
    config = {
        'case_study': 'calib_2017_finland_v9',
        'comment': 'Debug Infeasibility for Finland 2017 v9',
        'regions_names': ['FI'],
        'gwp_limit_overall': None, 
        'f_perc': True,
        'year': 2017,
        're_share_primary': None
    }
    
    print("Initializing ESMC model for Finland 2017 (Debug Mode)...")
    logging.getLogger().setLevel(logging.INFO) # Enable logging if ESMC uses it
    
    # Initialize the model with 12 Typical Days (standard)
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
    # Use cplex
    my_model.set_esom(solver='cplex') 
    
    # Access the AMPL object directly
    # 'my_model.esom' is an OptiProbl instance
    # 'my_model.esom.ampl' is the amplpy.AMPL object
    ampl = my_model.esom.ampl
    
    # Set useful debugging options
    print("Setting debug options for AMPL/CPLEX...")
    ampl.setOption('solver_msg', 1) # Enable solver messages
    
    # Force some cplex options for stability?
    # ampl.setOption('cplex_options', 'display=2 bargap=1e-6 barobj=1e-6') 
    # Use default
    
    print("Solving with detailed output...")
    try:
        # We manually call solve instead of my_model.solve_esom() so we can catch exceptions
        # and print raw output before post-processing fails
        
        # 1. Update version (optional, mimics solve_esom)
        my_model.update_version()
        
        # 2. Print initial info
        ampl.eval('print "gwp_limit_overall [ktCO2eq/y]", gwp_limit_overall;')
        ampl.eval('print "Number of TDs", last(TYPICAL_DAYS);')
        
        # 3. Solve
        ampl.solve()
        
        solve_result = ampl.getValue("solve_result")
        solve_result_num = ampl.getValue("solve_result_num")
        print(f"Solve Result String: {solve_result}")
        print(f"Solve Result Num: {solve_result_num}")
        
        # Check specific status codes for CPLEX
        # solve_result variable in AMPL:
        # "solved" -> optimal
        # "infeasible" -> infeasible
        # "limit" -> iteration limit
        # "failure" -> failure
        
        print("Evaluating Cost Breakdown...")
        # These are scalar values (sum over regions)
        try:
             # Using eval to print directly to stdout (captured by python normally)
             # But let's get values to print them explicitly
             total_cost = ampl.getObjective("obj").value()
             print(f"Objective 'obj' value: {total_cost}")
        except Exception as e:
            print(f"Could not print objective: {e}")

        try:
             # Evaluate expressions
             # Note: correct syntax for eval is 'display ...;' or just an expression
             # ampl.eval('display sum{c in REGIONS} (TotalCost[c]);')
             # Let's get them as values
             total_gwp = ampl.getData('sum{c in REGIONS} (TotalGWP[c])').iloc[0,0] # Assuming scalar returns 1x1 dataframe or similar
             total_cost_calc = ampl.getData('sum{c in REGIONS} (TotalCost[c])').iloc[0,0]
             
             print(f"TotalCost (calculated): {total_cost_calc}")
             print(f"TotalGWP (calculated): {total_gwp}")
             
        except Exception as e:
             print(f"Could not eval expressions: {e}")
             # Fallback to display
             ampl.eval('display sum{c in REGIONS} TotalCost[c];')
             ampl.eval('display sum{c in REGIONS} TotalGWP[c];')

    except Exception as e:
        print(f"Solve failed with Python exception: {e}")
        # Try to get status anyway
        try:
            print(f"Solve Result Num: {ampl.getValue('solve_result_num')}")
            print(f"Solve Result: {ampl.getValue('solve_result')}")
        except:
             pass

if __name__ == "__main__":
    run_debug_infeasibility()
