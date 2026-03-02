"""
Reproduce the exact case study that generated plots/calibration_methodical_Feb14.
Uses Data/2017/FI/ files restored to commit 937940b state.
Case study output: case_studies/FI/calib_2017_finland_repro/
"""
import sys
from pathlib import Path

workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc

def run():
    config = {
        'case_study': 'calib_2017_finland_repro',
        'comment': 'Reproduction of Feb14 calibration (937940b inputs)',
        'regions_names': ['FI'],
        'gwp_limit_overall': None,
        'f_perc': True,
        'year': 2017,
        're_share_primary': None,
    }

    print("=== Feb14 Reproduction Run ===")
    print(f"Input commit: 937940b (Feb 12)")
    print(f"Case study:   {config['case_study']}")
    print()

    my_model = Esmc(config, nbr_td=12)

    print("[1/6] Reading independent data...")
    my_model.read_data_indep()

    print("[2/6] Initializing regions...")
    my_model.init_regions()

    print("[3/6] Temporal aggregation (kmedoid, 12 TD)...")
    my_model.init_ta(algo='kmedoid')

    print("[4/6] Printing data files...")
    my_model.print_td_data()
    my_model.print_data(indep=True)

    print("[5/6] Setting up AMPL + CPLEX...")
    my_model.set_esom(solver='cplex')

    print("[6/6] Solving...")
    try:
        my_model.solve_esom()
        my_model.get_year_results()
        my_model.prints_esom(inputs=True, outputs=True, solve_info=True)
        print(f"\n✓ Run completed. Results in: {my_model.cs_dir / 'outputs'}")
    except Exception as e:
        print(f"\n✗ Solver error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()
