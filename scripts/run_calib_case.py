import sys
import pandas as pd
from pathlib import Path

# Add project root to sys.path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc

def run_finland_calibration():
    # Configuration for Finland 2017 Calibration
    
    config = {
        'case_study': 'calib_2017_finland_v9', # Using v9 as agreed
        'comment': 'Calibration for Finland 2017 with specific technology constraints',
        'regions_names': ['FI'],
        'gwp_limit_overall': None, 
        'f_perc': True, 
        'year': 2017,
        're_share_primary': None
    }
    
    print("Initializing ESMC model for Finland 2017...")
    # Initialize the model with 12 Typical Days (standard)
    my_model = Esmc(config, nbr_td=12)
    
    print("Reading independent data...")
    my_model.read_data_indep()
    
    print("Initializing regions...")
    my_model.init_regions()
    
    # Corrected method for temporal aggregation initialization
    print("Initializing temporal aggregation...")
    my_model.init_ta(algo='kmedoid') 
    
    print("Printing data files...")
    my_model.print_td_data()
    my_model.print_data(indep=True) # THIS WAS MISSING OR WRONG ORDER

    print("Setting up AMPL problem...")
    # Points to the .mod file and prepares the run
    # Requires ampl executable in path or specified
    my_model.set_esom(solver='cplex') 
    
    print("Solving...")
    try:
        # 1. Run the optimization
        my_model.solve_esom()
        
        # 2. Retrieve results from AMPL output
        # Based on esmc.py, we might need to manually extract results or call a method
        print("Extracting results...")
        
        # This will populate my_model.results
        my_model.get_year_results()
        
        # 3. Save to CSVs
        print("Saving outputs...")
        my_model.prints_esom(inputs=True, outputs=True, solve_info=True)
        
        print(f"Run completed successfully.")
        print(f"Results located in: {my_model.cs_dir / 'outputs'}")
        
    except Exception as e:
        print(f"Solver failed or AMPL error: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    run_finland_calibration()
