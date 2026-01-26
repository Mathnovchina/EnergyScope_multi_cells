
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
    # nbr_td=16 is used in run_esmc.py.
    my_model = Esmc(config, nbr_td=16)

    # Read data
    my_model.read_data_indep()
    my_model.init_regions()

    # NOTE: The original run_esmc.py contained code to FORCE nuclear to 0. 
    # We DO NOT include that here, so it respects the f_min from Technologies.csv.
    
    # Initialize Temporal Aggregation (clustering)
    # Using 'kmedoid' for the first run to generate the days
    ampl_path = None # Assumes AMPL is in PATH
    my_model.init_ta(algo='kmedoid', ampl_path=ampl_path)

    # Print data for AMPL
    my_model.print_td_data()
    my_model.print_data(indep=True)

    # Set up AMPL problem
    my_model.set_esom(ampl_path=ampl_path)

    # Solve
    print("Solving...")
    my_model.solve_esom()

    # Process results
    my_model.get_year_results(save_hourly=['Resources', 'Exchanges', 'Assets', 'Storage', 'Curt'])
    print("Run complete. Results in: ", my_model.cs_dir)

if __name__ == '__main__':
    run_finland_model()
