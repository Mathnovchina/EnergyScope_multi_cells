"""
Compare v6 block outputs against v5_fperc baseline and reality.

Usage:
  python scripts/compare_v6_blocks.py --block 0
  python scripts/compare_v6_blocks.py --block 0 1 2  (compare multiple)
  python scripts/compare_v6_blocks.py --all           (compare all completed)

Produces:
  - Console summary table
  - plots/calibration_v6/block{N}_comparison.png
  - plots/calibration_v6/block{N}_summary.csv
"""
import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# ── Reality targets (Finland 2017) ────────────────────────────────
REALITY = {
    'primary_energy': {
        'WOOD': 105, 'OIL': 96, 'NUCLEAR': 65, 'COAL_PEAT': 50,
        'GAS': 25, 'HYDRO': 15, 'WIND': 5
    },
    'electricity': {
        'Nuclear': 21.6, 'Hydro': 14.6, 'Biomass': 11.0,
        'Coal': 9.0, 'Wind': 4.8, 'Gas': 3.7, 'Solar': 0.1
    },
    'co2': 42.0  # MtCO2
}

# ── Case study folder mapping ────────────────────────────────────
CASE_DIRS = {
    'baseline': 'calib_2017_finland_v5_fperc_repro',
    0: 'calib_2017_finland_v6_block0_degeneracy',
    1: 'calib_2017_finland_v6_block1_oil',
    2: 'calib_2017_finland_v6_block2_biomass',
    3: 'calib_2017_finland_v6_block3_nuclear',
    4: 'calib_2017_finland_v6_block4_solar',
    5: 'calib_2017_finland_v6_block5_coal',
    6: 'calib_2017_finland_v6_block6_elecmix',
}


def load_outputs(case_name):
    """Load key outputs from a case study."""
    out_dir = ROOT / 'case_studies' / 'FI' / case_name / 'outputs'
    if not out_dir.exists():
        return None

    result = {}

    # Solve info
    solve_info = out_dir / 'Solve_info.csv'
    if solve_info.exists():
        si = pd.read_csv(solve_info, index_col=0)
        result['solve_result_num'] = float(si.loc['solve_result_num', 'Value'])
        result['solve_time'] = float(si.loc['solve_elapsed_time', 'Value'])
        result['objective'] = float(si.loc['objective', 'Value'])

    # Assets
    assets_file = out_dir / 'Assets.csv'
    if assets_file.exists():
        result['assets'] = pd.read_csv(assets_file)

    # Resources
    res_file = out_dir / 'Resources.csv'
    if res_file.exists():
        result['resources'] = pd.read_csv(res_file)

    # Year balance
    yb_file = out_dir / 'Year_balance.csv'
    if yb_file.exists():
        result['year_balance'] = pd.read_csv(yb_file)

    # GWP
    gwp_file = out_dir / 'Gwp_breakdown.csv'
    if gwp_file.exists():
        result['gwp'] = pd.read_csv(gwp_file)

    # Cost breakdown
    cost_file = out_dir / 'Cost_breakdown.csv'
    if cost_file.exists():
        result['cost'] = pd.read_csv(cost_file)

    # Log file for tolerance warnings
    log_file = ROOT / 'case_studies' / 'FI' / case_name / 'log.txt'
    if log_file.exists():
        with open(log_file, 'r') as f:
            log_text = f.read()
        result['has_tolerance_warning'] = 'Tolerance violations' in log_text
        result['has_numeric_issue'] = 'numeric issue' in log_text
    
    return result


def extract_primary_energy(data):
    """Extract primary energy consumption from resources."""
    if 'resources' not in data:
        return {}
    res = data['resources']
    # Sum local + exterior usage
    pe = {}
    
    # Map resource names to categories
    resource_map = {
        'WOOD': ['WOOD'],
        'OIL': ['LFO', 'DIESEL', 'GASOLINE', 'JET_FUEL'],
        'NUCLEAR': ['URANIUM'],
        'GAS': ['GAS'],
        'HYDRO': [],  # from year_balance
        'WIND': [],   # from year_balance
        'COAL_PEAT': ['COAL'],
        'BIOMASS_OTHER': ['BIOMASS_RESIDUES', 'BIOWASTE', 'ENERGY_CROPS_2', 'WET_BIOMASS', 'WASTE'],
    }
    
    for cat, resources in resource_map.items():
        total = 0
        for r in resources:
            mask = res.iloc[:, 0] == r
            if mask.any():
                row = res[mask].iloc[0]
                # Resources.csv has columns like: Resource, Used_local, Used_exterior
                # Need to check actual column names
                for col in res.columns[1:]:
                    if 'used' in col.lower() or 'local' in col.lower() or 'exterior' in col.lower():
                        val = row[col]
                        if pd.notna(val) and isinstance(val, (int, float)):
                            total += abs(val)
        pe[cat] = total / 1000  # GWh → TWh

    return pe


def extract_electricity(data):
    """Extract electricity generation from year_balance."""
    if 'year_balance' not in data:
        return {}
    yb = data['year_balance']
    
    elec = {}
    # Map tech groups to electricity categories
    elec_map = {
        'Nuclear': ['NUCLEAR'],
        'Hydro': ['HYDRO_DAM', 'HYDRO_RIVER'],
        'Wind': ['WIND_ONSHORE', 'WIND_OFFSHORE'],
        'Solar': ['PV_ROOFTOP', 'PV_UTILITY'],
        'Gas': ['CCGT', 'DHN_COGEN_GAS', 'DEC_COGEN_GAS'],
        'Coal': ['COAL_US', 'COAL_IGCC', 'IND_COGEN_COAL', 'DHN_COGEN_COAL'],
        'Biomass': ['IND_COGEN_WOOD', 'DHN_COGEN_WOOD', 'DEC_COGEN_WOOD',
                     'BIOMASS_TO_POWER', 'IND_COGEN_WASTE', 'DHN_COGEN_WASTE'],
    }
    
    # Find ELECTRICITY column/row
    # Year_balance structure varies - check columns
    cols = yb.columns.tolist()
    
    for cat, techs in elec_map.items():
        total = 0
        for tech in techs:
            # Check if tech is in the data
            mask = yb.iloc[:, 0] == tech
            if mask.any():
                row = yb[mask].iloc[0]
                # Look for ELECTRICITY column
                for col in cols:
                    if 'ELECTRICITY' in str(col).upper() or 'ELEC' in str(col).upper():
                        val = row[col]
                        if pd.notna(val) and isinstance(val, (int, float)):
                            if val > 0:  # production is positive
                                total += val
        elec[cat] = total / 1000  # GWh → TWh
    
    return elec


def extract_co2(data):
    """Extract total CO2 emissions."""
    if 'gwp' not in data:
        return None
    gwp = data['gwp']
    # Sum all GWP contributions
    total = 0
    for col in gwp.columns[1:]:
        vals = pd.to_numeric(gwp[col], errors='coerce')
        total += vals.sum()
    return total / 1e6  # kton → Mt (check units)


def check_bound_violations(data):
    """Check for F > f_max or F < f_min violations."""
    if 'assets' not in data:
        return []
    assets = data['assets']
    violations = []
    for _, row in assets.iterrows():
        tech = row.iloc[0]
        F = row.get('F', 0)
        f_min = row.get('f_min', 0)
        f_max = row.get('f_max', 1e15)
        if pd.notna(F) and pd.notna(f_max):
            if F > f_max * 1.001:  # 0.1% tolerance
                violations.append({
                    'tech': tech,
                    'F': F,
                    'f_max': f_max,
                    'violation_pct': (F - f_max) / f_max * 100 if f_max > 0 else float('inf')
                })
            if pd.notna(f_min) and f_min > 0 and F < f_min * 0.999:
                violations.append({
                    'tech': tech,
                    'F': F,
                    'f_min': f_min,
                    'violation_pct': (f_min - F) / f_min * 100
                })
    return violations


def print_comparison(blocks_data):
    """Print comparison table."""
    print("\n" + "=" * 80)
    print("V6 CALIBRATION COMPARISON")
    print("=" * 80)

    # Solver info
    print("\n--- Solver Info ---")
    header = f"{'Case':<30} {'Result':>8} {'Time(s)':>8} {'Objective':>15} {'Tol.Warn':>9}")
    print(header)
    print("-" * len(header))
    for name, data in blocks_data.items():
        if data:
            rn = data.get('solve_result_num', '?')
            st = data.get('solve_time', '?')
            obj = data.get('objective', '?')
            tw = 'YES' if data.get('has_tolerance_warning', False) else 'no'
            ni = ' (NI)' if data.get('has_numeric_issue', False) else ''
            print(f"{name:<30} {rn:>8.0f} {st:>8.1f} {obj:>15.3e} {tw:>9}{ni}")

    # Bound violations
    print("\n--- Bound Violations (F > f_max) ---")
    for name, data in blocks_data.items():
        if data:
            viols = check_bound_violations(data)
            if viols:
                print(f"\n  {name}:")
                for v in sorted(viols, key=lambda x: -x.get('violation_pct', 0)):
                    if 'f_max' in v:
                        print(f"    {v['tech']}: F={v['F']:.3f} > f_max={v['f_max']:.3f} "
                              f"(+{v['violation_pct']:.1f}%)")
            else:
                print(f"  {name}: NONE ✅")

    # Absurd deployments (F > 100 GW)
    print("\n--- Absurd Deployments (F > 100 GW) ---")
    for name, data in blocks_data.items():
        if data and 'assets' in data:
            assets = data['assets']
            absurd = assets[assets['F'] > 100]
            if len(absurd) > 0:
                print(f"  {name}: {len(absurd)} techs > 100 GW")
                for _, row in absurd.nlargest(5, 'F').iterrows():
                    print(f"    {row.iloc[0]}: F={row['F']:.1f} GW")
            else:
                print(f"  {name}: NONE ✅")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--block', type=int, nargs='+', help='Block numbers to compare')
    parser.add_argument('--all', action='store_true', help='Compare all available blocks')
    args = parser.parse_args()

    if args.all:
        blocks = list(range(7))  # 0-6
    elif args.block:
        blocks = args.block
    else:
        blocks = [0]

    # Always include baseline
    blocks_data = {}
    
    baseline = load_outputs(CASE_DIRS['baseline'])
    if baseline:
        blocks_data['v5_fperc (baseline)'] = baseline
    else:
        print("WARNING: Baseline outputs not found")

    for b in blocks:
        case = CASE_DIRS.get(b)
        if case:
            data = load_outputs(case)
            if data:
                blocks_data[f'Block {b}'] = data
            else:
                print(f"Block {b} outputs not found: {case}")

    if blocks_data:
        print_comparison(blocks_data)
    else:
        print("No data found to compare.")


if __name__ == '__main__':
    main()
