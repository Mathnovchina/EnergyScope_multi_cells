"""
Run v7 Block A calibration
===========================
After disabling 69 future technologies (f_max=0), run model to see impact.
"""
import sys
from pathlib import Path

# Add project root to sys.path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc

def run_v7_blockA():
    config = {
        'case_study': 'calib_2017_finland_v7_blockA',
        'comment': 'v7 Block A: Disable 69 future technologies (f_max=0)',
        'regions_names': ['FI'],
        'gwp_limit_overall': None, 
        'f_perc': True, 
        'year': 2017,
        're_share_primary': None
    }
    
    print("="*60)
    print("v7 BLOCK A: Disable Future Technologies")
    print("="*60)
    print("\nInitializing ESMC model for Finland 2017...")
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
    
    print("\nSolving...")
    try:
        my_model.solve_esom()
        print("Extracting results...")
        my_model.get_year_results()
        print("Saving outputs...")
        my_model.prints_esom(inputs=True, outputs=True, solve_info=True)
        
        print("\n" + "="*60)
        print("v7 BLOCK A RUN COMPLETED")
        print("="*60)
        print(f"Results: {my_model.cs_dir / 'outputs'}")
        
    except Exception as e:
        print(f"Solver failed: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    run_v7_blockA()
