"""
Run v6 calibration blocks for Finland 2017.

Usage:
  python scripts/run_v6_block.py --block 0
  python scripts/run_v6_block.py --block 1
  ...etc

Each block uses a different case_study name so outputs don't overwrite each other.
The FI input files (Technologies.csv, Resources.csv) MUST be updated
before running each block:
  - Block 0: scripts/build_v6_block0.py (already applied)
  - Block 1+: scripts/apply_v6_blocks.py --through N
"""
import sys
import argparse
from pathlib import Path

workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc

BLOCK_NAMES = {
    0: 'calib_2017_finland_v6_block0_degeneracy',
    1: 'calib_2017_finland_v6_block1_oil',
    2: 'calib_2017_finland_v6_block2_biomass',
    3: 'calib_2017_finland_v6_block3_nuclear',
    4: 'calib_2017_finland_v6_block4_solar',
    5: 'calib_2017_finland_v6_block5_coal',
    6: 'calib_2017_finland_v6_block6_elecmix',
}

BLOCK_COMMENTS = {
    0: 'Block 0: Degeneracy fix - 130 technology bounds constrained',
    1: 'Block 0+1: + Oil overconsumption fix (LFO/JET_FUEL caps)',
    2: 'Block 0+1+2: + Biomass forcing (fmin_perc on wood techs)',
    3: 'Block 0+1+2+3: + Nuclear tightening (URANIUM cap)',
    4: 'Block 0-4: + Solar cap reduction',
    5: 'Block 0-5: + Coal/peat rebalancing',
    6: 'Block 0-6: + Electricity mix fine-tuning',
}


def run_block(block_num):
    case_study = BLOCK_NAMES[block_num]
    comment = BLOCK_COMMENTS[block_num]

    config = {
        'case_study': case_study,
        'comment': comment,
        'regions_names': ['FI'],
        'gwp_limit_overall': None,
        'f_perc': True,
        'year': 2017,
        're_share_primary': None,
    }

    print("=" * 60)
    print(f"V6 CALIBRATION — BLOCK {block_num}")
    print(f"Case study: {case_study}")
    print(f"Comment: {comment}")
    print("=" * 60)

    print("\n[1/6] Initializing ESMC model (12 TDs)...")
    my_model = Esmc(config, nbr_td=12)

    print("\n[2/6] Reading independent data...")
    my_model.read_data_indep()

    print("\n[3/6] Initializing regions (REF → FI overrides)...")
    my_model.init_regions()

    print("\n[4/6] Initializing temporal aggregation (k-medoid)...")
    my_model.init_ta(algo='kmedoid')

    print("\n[5/6] Printing data files...")
    my_model.print_td_data()
    my_model.print_data(indep=True)

    print("\n[6/6] Setting up AMPL + solving...")
    # Barrier solver (crossover doesn't work on this model — CPLEX barrier
    # consistently produces 0 simplex iterations regardless of crossover setting)
    cplex_opts = ['baropt',
                  'predual=-1',
                  'barstart=4',
                  'comptol=1e-5',
                  'crossover=0',
                  'timelimit 172800',
                  'bardisplay=1',
                  'display=2']
    ampl_options = {'show_stats': 3,
                    'log_file': str(my_model.cs_dir / 'log.txt'),
                    'presolve': 200,
                    'times': 1,
                    'gentimes': 1,
                    'cplex_options': ' '.join(cplex_opts)}
    my_model.set_esom(solver='cplex', ampl_options=ampl_options)

    try:
        my_model.solve_esom()
        print("\nExtracting results...")
        my_model.get_year_results()
        print("Saving outputs...")
        my_model.prints_esom(inputs=True, outputs=True, solve_info=True)
        print(f"\nBlock {block_num} completed successfully.")
        print(f"Results: {my_model.cs_dir / 'outputs'}")
    except Exception as e:
        print(f"\nBlock {block_num} FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run v6 calibration block')
    parser.add_argument('--block', type=int, required=True,
                        choices=list(BLOCK_NAMES.keys()),
                        help='Block number (0-6)')
    args = parser.parse_args()
    run_block(args.block)
