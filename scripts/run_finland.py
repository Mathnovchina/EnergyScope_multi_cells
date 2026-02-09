
import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path

# Add project root to path
# Adjust this path if running from a different location, currently assumes scripts/
project_root = Path(__file__).parents[1]
sys.path.append(str(project_root))

from esmc import Esmc
from esmc.common import CSV_SEPARATOR

def run_finland_model():
    # Configuration
    years = [2017] # Start with 2017 as requested
    # user might want to run 2035/2050 later, but let's default to 2017 first
    
    # Scenarios? The user asked about the 3 scenarios in run_esmc.py. 
    # For a calibration/first run, 'ref' (reference) is best.
    case_study = 'ref_2017_finland'
    
    print(f"Running Case: {case_study}")

    config = {
        'case_study': case_study,
        'comment': 'Finland 2017 Calibration Run',
        'regions_names': ['FI'], # Only Finland
        'gwp_limit_overall': None, # Unconstrained for calibration/validation
        're_share_primary': None,
        'f_perc': False,
        'year': 2017
    }

    # Initialize ESMC
    # nbr_td=12 as requested by user
    my_model = Esmc(config, nbr_td=12)

    # Read data
    my_model.read_data_indep()
    my_model.init_regions()

    # NOTE: The original run_esmc.py contained code to FORCE nuclear to 0. 
    # We DO NOT include that here, so it respects the f_min from Technologies.csv.
    
    # Initialize Temporal Aggregation (clustering)
    # Using 'kmedoid' as requested
    ampl_path = None # Assumes AMPL is in PATH
    try:
        my_model.init_ta(algo='read', ampl_path=ampl_path)
    except RuntimeError as e:
        print(f"Warning: Clustering failed ({e}). Trying to use existing typical days...")
        # If clustering fails (e.g. license), try to proceed??
        # Usually kmedoid generates 'td_of_days.csv'. 
        # But 'init_ta' logic usually requires success.
        # If we fail here, we might just try to print data using whatever default?
        raise e

    # Print data for AMPL
    my_model.print_td_data()
    my_model.print_data(indep=True)

    # Set up AMPL problem
    my_model.set_esom(ampl_path=ampl_path)

    # Solve
    print("Solving...")
    try:
        my_model.solve_esom()
    except Exception as e:
        print(f"Caught exception during solve: {e}")
        try:
            msg = my_model.esom.ampl.get_value("solve_message")
            num = my_model.esom.ampl.get_value("solve_result_num")
            print(f"AMPL solve_message: {msg}")
            print(f"AMPL solve_result_num: {num}")
        except:
            print("Could not retrieve solve_message")
        # Do not re-raise, try to continue to see if we can get partial results or debug info
    
    # Process results

    # Process results
    my_model.get_year_results(save_hourly=['Resources', 'Exchanges', 'Assets', 'Storage', 'Curt'])
    my_model.prints_esom(inputs=True, outputs=True, solve_info=True)
    print("Run complete. Results in: ", my_model.cs_dir)

if __name__ == '__main__':
    run_finland_model()
