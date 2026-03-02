"""
Generate validation plots for v5_fperc_repro rerun.
Compares rerun outputs against both:
  - Original v5_fperc outputs
  - Finland 2017 Reality targets

Produces: primary_energy_comparison.png, electricity_mix_comparison.png,
          co2_emissions_comparison.png, asset_capacity_comparison.png
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os, shutil

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECTION = 'FI'

RERUN_CASE  = 'calib_2017_finland_v5_fperc_repro'
ORIG_CASE   = 'calib_2017_finland_v5_fperc'

RERUN_DIR = PROJECT_ROOT / 'case_studies' / SECTION / RERUN_CASE / 'outputs'
ORIG_DIR  = PROJECT_ROOT / 'case_studies' / SECTION / ORIG_CASE / 'outputs'

PLOTS_DIR = PROJECT_ROOT / 'plots' / 'calibration_v5_fperc_rerun'
if os.path.exists(PLOTS_DIR):
    shutil.rmtree(PLOTS_DIR)
os.makedirs(PLOTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# REALITY TARGETS – Finland 2017
# ---------------------------------------------------------------------------
REALITY = {
    'Primary Energy': {
        'WOOD': 105.0,
        'OIL': 96.0,
        'NUCLEAR': 65.0,
        'COAL_PEAT': 50.0,
        'GAS': 25.0,
        'HYDRO': 15.0,
        'WIND': 5.0,
    },
    'Electricity Generation': {
        'Nuclear': 21.6,
        'Hydro': 14.6,
        'Biomass': 11.0,
        'Coal': 9.0,
        'Wind': 4.8,
        'Gas': 3.7,
        'Solar': 0.1,
    },
    'CO2 Emissions': 42.0  # MtCO2
}

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def load_csv(filename, output_dir):
    path = output_dir / filename
    if not path.exists():
        print(f"  Warning: {path} not found.")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df.rename(columns={df.columns[0]: 'item'}, inplace=True)

    if filename == 'Resources.csv':
        consump = 0
        for c in ['R_year_local', 'R_year_exterior', 'R_year_import']:
            if c in df.columns:
                consump = consump + df[c]
        df['Yearly'] = consump
    return df

# ---------------------------------------------------------------------------
# PRIMARY ENERGY CATEGORIES
# ---------------------------------------------------------------------------
def _primary_energy(resources):
    SCALER = 1/1000.0
    m = {}
    wood_cols = ['WOOD', 'WET_BIOMASS', 'ENERGY_CROPS_2', 'BIOMASS_RESIDUES', 'BIOWASTE']
    m['WOOD'] = resources[resources['item'].isin(wood_cols)]['Yearly'].sum() * SCALER

    oil_cols = ['DIESEL', 'GASOLINE', 'LFO', 'JET_FUEL', 'OIL',
                'DIESEL_RE', 'GASOLINE_RE', 'LFO_RE', 'JET_FUEL_RE', 'HFO', 'HFO_RE']
    m['OIL'] = resources[resources['item'].isin(oil_cols)]['Yearly'].sum() * SCALER

    m['NUCLEAR']   = resources[resources['item'] == 'URANIUM']['Yearly'].sum() * SCALER
    m['COAL_PEAT'] = resources[resources['item'].isin(['COAL', 'PEAT'])]['Yearly'].sum() * SCALER
    m['GAS']       = resources[resources['item'].isin(['GAS', 'GAS_RE'])]['Yearly'].sum() * SCALER
    m['HYDRO']     = resources[resources['item'] == 'RES_HYDRO']['Yearly'].sum() * SCALER
    m['WIND']      = resources[resources['item'] == 'RES_WIND']['Yearly'].sum() * SCALER
    return m

def analyze_primary_energy():
    print("=== Primary Energy Comparison ===")
    res_rerun = load_csv('Resources.csv', RERUN_DIR)
    res_orig  = load_csv('Resources.csv', ORIG_DIR)

    pe_rerun = _primary_energy(res_rerun) if not res_rerun.empty else {}
    pe_orig  = _primary_energy(res_orig)  if not res_orig.empty  else {}

    df = pd.DataFrame({
        'Original v5': pe_orig,
        'Rerun': pe_rerun,
        'Reality': REALITY['Primary Energy']
    }).fillna(0)

    print(df.round(1))
    print(f"\nTPES  Original: {df['Original v5'].sum():.1f}  Rerun: {df['Rerun'].sum():.1f}  Reality: {df['Reality'].sum():.1f} TWh\n")

    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(df))
    w = 0.25
    bars1 = ax.bar(x - w, df['Original v5'], w, label='Original v5', color='#4c72b0')
    bars2 = ax.bar(x,     df['Rerun'],       w, label='Rerun',       color='#dd8452')
    bars3 = ax.bar(x + w, df['Reality'],     w, label='Reality',     color='#55a868')

    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=30, ha='right')
    ax.set_ylabel('TWh')
    ax.set_title('Primary Energy Consumption (TWh) – v5_fperc')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    for bars in [bars1, bars2, bars3]:
        ax.bar_label(bars, fmt='%.0f', fontsize=7, padding=2)

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'primary_energy_comparison.png', dpi=150)
    print("Saved primary_energy_comparison.png")

# ---------------------------------------------------------------------------
# ELECTRICITY
# ---------------------------------------------------------------------------
def _electricity(yb):
    SCALER = 1/1000.0
    groups = {
        'Nuclear': ['NUCLEAR'],
        'Hydro':   ['HYDRO_DAM', 'HYDRO_RIVER'],
        'Biomass': ['IND_BOILER_WOOD', 'DEC_BOILER_WOOD', 'DHN_COGEN_WOOD', 'IND_COGEN_WOOD'],
        'Coal':    ['IND_BOILER_COAL', 'DHN_COGEN_COAL', 'COAL_US', 'IND_COGEN_COAL'],
        'Wind':    ['WIND_ONSHORE', 'WIND_OFFSHORE'],
        'Gas':     ['CCGT', 'OCGT', 'IND_COGEN_GAS', 'DHN_COGEN_GAS', 'DEC_COGEN_GAS'],
        'Solar':   ['PV_ROOFTOP', 'PV_UTILITY'],
    }
    elec_col = 'ELECTRICITY'
    vals = {k: 0.0 for k in groups}
    if elec_col not in yb.columns:
        print("  ELECTRICITY column missing in Year_balance!")
        return vals
    for grp, techs in groups.items():
        for tech in techs:
            matches = yb[yb['item'].str.contains(tech, na=False)]
            for _, row in matches.iterrows():
                v = row[elec_col]
                if v > 0:
                    vals[grp] += v * SCALER
    return vals

def analyze_electricity():
    print("=== Electricity Generation Comparison ===")
    yb_rerun = load_csv('Year_balance.csv', RERUN_DIR)
    yb_orig  = load_csv('Year_balance.csv', ORIG_DIR)

    e_rerun = _electricity(yb_rerun) if not yb_rerun.empty else {}
    e_orig  = _electricity(yb_orig)  if not yb_orig.empty  else {}

    df = pd.DataFrame({
        'Original v5': e_orig,
        'Rerun': e_rerun,
        'Reality': REALITY['Electricity Generation']
    }).fillna(0)

    print(df.round(1))
    print(f"\nTotal  Original: {df['Original v5'].sum():.1f}  Rerun: {df['Rerun'].sum():.1f}  Reality: {df['Reality'].sum():.1f} TWh\n")

    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(df))
    w = 0.25
    bars1 = ax.bar(x - w, df['Original v5'], w, label='Original v5', color='#4c72b0')
    bars2 = ax.bar(x,     df['Rerun'],       w, label='Rerun',       color='#dd8452')
    bars3 = ax.bar(x + w, df['Reality'],     w, label='Reality',     color='#55a868')

    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=30, ha='right')
    ax.set_ylabel('TWh')
    ax.set_title('Electricity Generation (TWh) – v5_fperc')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    for bars in [bars1, bars2, bars3]:
        ax.bar_label(bars, fmt='%.1f', fontsize=7, padding=2)

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'electricity_mix_comparison.png', dpi=150)
    print("Saved electricity_mix_comparison.png")

# ---------------------------------------------------------------------------
# CO2 EMISSIONS
# ---------------------------------------------------------------------------
def _calc_emissions(resources):
    SCALER = 1/1000.0
    factors = {'COAL': 0.40, 'OIL': 0.31, 'GAS': 0.26, 'Waste': 0.15}
    em = 0.0
    em += resources[resources['item'] == 'COAL']['Yearly'].sum() * SCALER * factors['COAL']
    oil_cols = ['DIESEL', 'GASOLINE', 'LFO', 'JET_FUEL', 'OIL', 'HFO']
    em += resources[resources['item'].isin(oil_cols)]['Yearly'].sum() * SCALER * factors['OIL']
    em += resources[resources['item'] == 'GAS']['Yearly'].sum() * SCALER * factors['GAS']
    em += resources[resources['item'] == 'WASTE']['Yearly'].sum() * SCALER * factors['Waste']
    return em

def analyze_emissions():
    print("=== CO2 Emissions Comparison ===")
    res_rerun = load_csv('Resources.csv', RERUN_DIR)
    res_orig  = load_csv('Resources.csv', ORIG_DIR)

    em_rerun = _calc_emissions(res_rerun) if not res_rerun.empty else 0.0
    em_orig  = _calc_emissions(res_orig)  if not res_orig.empty  else 0.0
    em_real  = REALITY['CO2 Emissions']

    print(f"  Original v5: {em_orig:.1f} MtCO2")
    print(f"  Rerun:       {em_rerun:.1f} MtCO2")
    print(f"  Reality:     {em_real:.1f} MtCO2\n")

    fig, ax = plt.subplots(figsize=(6, 6))
    cats = ['Original v5', 'Rerun', 'Reality']
    vals = [em_orig, em_rerun, em_real]
    colors = ['#4c72b0', '#dd8452', '#55a868']
    bars = ax.bar(cats, vals, color=colors)
    ax.set_ylabel('MtCO2')
    ax.set_title('CO2 Emissions – v5_fperc')
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.bar_label(bars, fmt='%.1f', padding=3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'co2_emissions_comparison.png', dpi=150)
    print("Saved co2_emissions_comparison.png")

# ---------------------------------------------------------------------------
# ASSET CAPACITIES (selected core techs)
# ---------------------------------------------------------------------------
def analyze_assets():
    print("=== Asset Capacity Comparison ===")
    a_rerun = load_csv('Assets.csv', RERUN_DIR)
    a_orig  = load_csv('Assets.csv', ORIG_DIR)
    if a_rerun.empty:
        print("  No rerun Assets.csv")
        return

    # Identify the capacity column (F or similar)
    cap_col = [c for c in a_rerun.columns if c.lower().startswith('f') and c != 'item']
    if not cap_col:
        cap_col = [a_rerun.columns[1]]
    cap_col = cap_col[0]

    core_techs = [
        'NUCLEAR', 'CCGT', 'COAL_US', 'WIND_ONSHORE', 'PV_ROOFTOP',
        'HYDRO_DAM', 'HYDRO_RIVER', 'GEOTHERMAL',
        'DHN_COGEN_GAS', 'DHN_COGEN_WOOD', 'DHN_COGEN_COAL',
        'IND_COGEN_GAS', 'IND_COGEN_WOOD',
        'DEC_BOILER_OIL', 'DEC_BOILER_GAS', 'DEC_BOILER_WOOD',
        'CAR_GASOLINE', 'CAR_DIESEL', 'TRUCK_DIESEL',
        'BOAT_FREIGHT_DIESEL', 'CARGO_LFO',
    ]

    rows = []
    for t in core_techs:
        orig_v = a_orig[a_orig['item'] == t][cap_col].values[0] if not a_orig.empty and t in a_orig['item'].values else 0.0
        rerun_v = a_rerun[a_rerun['item'] == t][cap_col].values[0] if t in a_rerun['item'].values else 0.0
        rows.append({'Tech': t, 'Original v5': orig_v, 'Rerun': rerun_v})
    df = pd.DataFrame(rows).set_index('Tech')

    # Filter to non-zero in at least one
    df = df[(df['Original v5'] > 0) | (df['Rerun'] > 0)]
    print(df.round(3))

    fig, ax = plt.subplots(figsize=(13, 7))
    x = np.arange(len(df))
    w = 0.35
    bars1 = ax.bar(x - w/2, df['Original v5'], w, label='Original v5', color='#4c72b0')
    bars2 = ax.bar(x + w/2, df['Rerun'],       w, label='Rerun',       color='#dd8452')

    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('GW (installed)')
    ax.set_title('Core Asset Capacities (GW) – v5_fperc')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    for bars in [bars1, bars2]:
        ax.bar_label(bars, fmt='%.2f', fontsize=6, padding=2)

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'asset_capacity_comparison.png', dpi=150)
    print("Saved asset_capacity_comparison.png")

# ---------------------------------------------------------------------------
# SUMMARY TABLE (saved as CSV)
# ---------------------------------------------------------------------------
def save_summary():
    """Write a CSV with key metrics for quick reference."""
    res_rerun = load_csv('Resources.csv', RERUN_DIR)
    res_orig  = load_csv('Resources.csv', ORIG_DIR)
    obj_rerun = load_csv('Objective.csv', RERUN_DIR)
    obj_orig  = load_csv('Objective.csv', ORIG_DIR)
    tc_rerun  = load_csv('TotalCost.csv', RERUN_DIR)
    tc_orig   = load_csv('TotalCost.csv', ORIG_DIR)

    pe_rerun = _primary_energy(res_rerun) if not res_rerun.empty else {}
    pe_orig  = _primary_energy(res_orig)  if not res_orig.empty  else {}

    rows = []
    rows.append({'Metric': 'Objective (M€)', 'Original v5': obj_orig.iloc[0,1] if not obj_orig.empty else '', 'Rerun': obj_rerun.iloc[0,1] if not obj_rerun.empty else ''})
    rows.append({'Metric': 'TotalCost (M€)', 'Original v5': tc_orig.iloc[0,1] if not tc_orig.empty else '', 'Rerun': tc_rerun.iloc[0,1] if not tc_rerun.empty else ''})
    for k in REALITY['Primary Energy']:
        rows.append({'Metric': f'PE {k} (TWh)', 'Original v5': pe_orig.get(k, 0), 'Rerun': pe_rerun.get(k, 0), 'Reality': REALITY['Primary Energy'][k]})
    rows.append({'Metric': 'CO2 (MtCO2)',
                 'Original v5': _calc_emissions(res_orig) if not res_orig.empty else '',
                 'Rerun': _calc_emissions(res_rerun) if not res_rerun.empty else '',
                 'Reality': REALITY['CO2 Emissions']})

    pd.DataFrame(rows).to_csv(PLOTS_DIR / 'comparison_summary.csv', index=False)
    print("Saved comparison_summary.csv")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print(f"Rerun dir : {RERUN_DIR}")
    print(f"Original  : {ORIG_DIR}")
    print(f"Plots dir : {PLOTS_DIR}\n")
    analyze_primary_energy()
    analyze_electricity()
    analyze_emissions()
    analyze_assets()
    save_summary()
    print(f"\nAll plots saved to {PLOTS_DIR}")
