"""
Rerun script for v5_fperc calibration state reproduction.

This script runs the Finland 2017 calibration using the restored v5_fperc inputs
in Data/2017/FI/ (Technologies.csv + Resources.csv restored on 2026-02-26).

New case study output will be written to:
  case_studies/FI/calib_2017_finland_v5_fperc_repro/

Config mirrors the original v5_fperc run:
  - f_perc: True (market share constraints active)
  - nbr_td: 12 (typical days)
  - year: 2017
  - regions_names: ['FI']
  - solver: cplex (barrier)

Usage:
  python scripts/run_v5_fperc_repro.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc


def run_v5_fperc_repro():
    config = {
        'case_study': 'calib_2017_finland_v5_fperc_repro',
        'comment': 'Reproduction of v5_fperc calibration (restored 2026-02-26)',
        'regions_names': ['FI'],
        'gwp_limit_overall': None,
        'f_perc': True,
        'year': 2017,
        're_share_primary': None,
    }

    print("=" * 60)
    print("v5_fperc REPRODUCTION RUN")
    print("=" * 60)

    print("\n[1/6] Initializing ESMC model (12 TDs)...")
    my_model = Esmc(config, nbr_td=12)

    print("\n[2/6] Reading independent data...")
    my_model.read_data_indep()

    print("\n[3/6] Initializing regions (REF -> FI overrides)...")
    my_model.init_regions()

    print("\n[4/6] Initializing temporal aggregation (k-medoid)...")
    my_model.init_ta(algo='kmedoid')

    print("\n[5/6] Printing data files...")
    my_model.print_td_data()
    my_model.print_data(indep=True)

    print("\n[6/6] Setting up AMPL + solving...")
    my_model.set_esom(solver='cplex')

    try:
        my_model.solve_esom()
        print("\nExtracting results...")
        my_model.get_year_results()
        print("Saving outputs...")
        my_model.prints_esom(inputs=True, outputs=True, solve_info=True)
        print("\nRun completed successfully.")
        print("Results: %s" % (my_model.cs_dir / 'outputs'))
    except Exception as e:
        print("\nSolver failed: %s" % e)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_v5_fperc_repro()
