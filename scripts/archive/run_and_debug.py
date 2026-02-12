
import pandas as pd
import os
import sys
import traceback
from pathlib import Path

# Paths
workspace_root = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")
sys.path.append(str(workspace_root))

from esmc import Esmc

def main():
    try:
        case_study = 'calib_2017_finland'
        print(f"Running Case: {case_study} (Debug Mode)")

        config = {
            'case_study': case_study,
            'comment': 'Finland 2017 Calibration',
            'regions_names': ['FI'],
            'gwp_limit_overall': None,
            're_share_primary': None,
            'f_perc': False,
            'year': 2017
        }
        
        # Initialize
        print("Initializing Esmc...")
        my_model = Esmc(config, nbr_td=12)
        print("Reading Data Indep...")
        my_model.read_data_indep()
        print("Init Regions...")
        my_model.init_regions()
        print("Init TA...")
        my_model.init_ta(algo='read')
        print("Printing Data...")
        my_model.print_td_data()
        my_model.print_data(indep=True)
        
        # Run
        print("Setting ESOM...")
        my_model.set_esom()
        print("Solving ESOM...")
        my_model.solve_esom()
        
        print("Getting Results...")
        my_model.get_year_results(save_hourly=['Resources', 'Exchanges', 'Assets', 'Storage', 'Curt'])
        
        print("Run finished successfully.")
        
    except Exception as e:
        print("CRITICAL ERROR FOUND:")
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
