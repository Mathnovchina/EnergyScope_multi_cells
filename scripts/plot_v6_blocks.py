"""
Generate charts for Finland 2017 v6 calibration block-by-block results.
Saves PNGs to plots/v6_blocks/ and updates the markdown report with image links.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

ROOT = Path(__file__).resolve().parent.parent
PLOT_DIR = ROOT / 'plots' / 'v6_blocks'
PLOT_DIR.mkdir(parents=True, exist_ok=True)

BLOCKS = {
    'v5_fperc': 'calib_2017_finland_v5_fperc',
    'Block 0\nDegeneracy': 'calib_2017_finland_v6_block0_degeneracy',
    'Block 1\nOil': 'calib_2017_finland_v6_block1_oil',
    'Block 2\nBiomass': 'calib_2017_finland_v6_block2_biomass',
    'Block 3\nNuclear': 'calib_2017_finland_v6_block3_nuclear',
    'Block 4\nSolar': 'calib_2017_finland_v6_block4_solar',
    'Block 5\nCoal': 'calib_2017_finland_v6_block5_coal',
    'Block 6\nElecMix': 'calib_2017_finland_v6_block6_elecmix',
}

# Short labels for tables
SHORT_LABELS = {
    'v5_fperc': 'v5',
    'Block 0\nDegeneracy': 'B0',
    'Block 1\nOil': 'B1',
    'Block 2\nBiomass': 'B2',
    'Block 3\nNuclear': 'B3',
    'Block 4\nSolar': 'B4',
    'Block 5\nCoal': 'B5',
    'Block 6\nElecMix': 'B6',
}

REALITY_TARGETS = {
    'WOOD': 105000,
    'LFO': 40000,
    'DIESEL': 25000,
    'GASOLINE': 16000,
    'JET_FUEL': 5000,
    'GAS': 25000,
    'COAL': 50000,
    'URANIUM': 65000,
    'RES_WIND': 5000,
    'RES_HYDRO': 15000,
    'TOTAL_OIL': 96000,
    'TOTAL_BIOMASS': 105000,
}

# Color palette
BLOCK_COLORS = sns.color_palette('tab10', n_colors=8)
REALITY_COLOR = '#E63946'  # red
sns.set_theme(style='whitegrid', font_scale=1.05)


def collect_data():
    """Collect resources and assets from all block outputs."""
    all_resources = {}
    all_assets = {}
    all_objectives = {}

    for label, case in BLOCKS.items():
        out_dir = ROOT / 'case_studies' / 'FI' / case / 'outputs'
        if not out_dir.exists():
            print(f"  SKIP {label}: {out_dir} not found")
            continue

        # Resources
        res = pd.read_csv(out_dir / 'Resources.csv')
        res_dict = {}
        for _, row in res.iterrows():
            name = row['Resources']
            res_dict[name] = row['R_year_local'] + row['R_year_exterior']
        # Derived totals
        res_dict['TOTAL_OIL'] = sum(res_dict.get(r, 0) for r in
                                     ['LFO', 'DIESEL', 'GASOLINE', 'JET_FUEL'])
        res_dict['TOTAL_BIOMASS'] = sum(res_dict.get(r, 0) for r in
                                         ['WOOD', 'ENERGY_CROPS_2', 'BIOWASTE',
                                          'BIOMASS_RESIDUES', 'WET_BIOMASS'])
        all_resources[label] = res_dict

        # Assets
        assets = pd.read_csv(out_dir / 'Assets.csv')
        assets_dict = {}
        for _, row in assets.iterrows():
            tech = row['Technologies']
            assets_dict[tech] = {
                'F': row['F'], 'f_min': row['f_min'], 'f_max': row['f_max'],
                'F_year': row['F_year']
            }
        all_assets[label] = assets_dict

        # Objective
        obj = pd.read_csv(out_dir / 'Objective.csv')
        all_objectives[label] = obj.iloc[0, 1]

    return all_resources, all_assets, all_objectives


# ─── PLOT 1: Objective Function Progression ────────────────────────────────────
def plot_objective(all_objectives):
    labels = list(all_objectives.keys())
    values = list(all_objectives.values())

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(labels)), [v / 1e6 for v in values],
                  color=BLOCK_COLORS, edgecolor='white', linewidth=0.8)

    # Annotate values
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f'{v / 1e6:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel('Objective (M€)')
    ax.set_title('Objective Function Progression Across Blocks', fontsize=13, fontweight='bold')
    ax.set_ylim(0, max(v / 1e6 for v in values) * 1.2)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    fig.savefig(PLOT_DIR / '01_objective_progression.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    print('  [1/7] Objective progression')


# ─── PLOT 2: Key Resources Evolution (stacked area / multi-line) ──────────────
def plot_resource_evolution(all_resources):
    resources_to_plot = ['WOOD', 'LFO', 'GAS', 'COAL', 'URANIUM', 'TOTAL_OIL']
    labels = list(all_resources.keys())
    x = range(len(labels))

    fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharey=False)
    axes = axes.flatten()

    for i, res in enumerate(resources_to_plot):
        ax = axes[i]
        vals = [all_resources[lbl].get(res, 0) / 1000 for lbl in labels]
        ax.plot(x, vals, 'o-', color=BLOCK_COLORS[0], linewidth=2, markersize=6)
        ax.fill_between(x, vals, alpha=0.15, color=BLOCK_COLORS[0])

        # Reality target line
        if res in REALITY_TARGETS:
            target = REALITY_TARGETS[res] / 1000
            ax.axhline(target, color=REALITY_COLOR, linewidth=1.8, linestyle='--',
                       label=f'Reality ({target:.0f} TWh)')
            ax.legend(fontsize=8, loc='best')

        ax.set_xticks(list(x))
        ax.set_xticklabels([SHORT_LABELS[l] for l in labels], fontsize=8)
        ax.set_title(res.replace('_', ' '), fontsize=11, fontweight='bold')
        ax.set_ylabel('TWh')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}'))

    sns.despine(left=True, bottom=True)
    fig.suptitle('Key Resource Usage Evolution Across Blocks', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(PLOT_DIR / '02_resource_evolution.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    print('  [2/7] Resource evolution')


# ─── PLOT 3: Assessment vs Reality (final Block 6) ───────────────────────────
def plot_vs_reality(all_resources):
    metrics = [
        ('WOOD', 'Wood'),
        ('TOTAL_OIL', 'Total Oil'),
        ('GAS', 'Gas'),
        ('COAL', 'Coal'),
        ('URANIUM', 'Uranium'),
        ('RES_WIND', 'Wind'),
        ('RES_HYDRO', 'Hydro'),
    ]

    b6_label = 'Block 6\nElecMix'
    v5_label = 'v5_fperc'

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(metrics))
    width = 0.25

    reality_vals = [REALITY_TARGETS.get(m[0], np.nan) / 1000 for m in metrics]
    v5_vals = [all_resources[v5_label].get(m[0], 0) / 1000 for m in metrics]
    b6_vals = [all_resources[b6_label].get(m[0], 0) / 1000 for m in metrics]
    labels_display = [m[1] for m in metrics]

    bars1 = ax.bar(x - width, reality_vals, width, label='Reality', color=REALITY_COLOR,
                   edgecolor='white', linewidth=0.8, alpha=0.85)
    bars2 = ax.bar(x, v5_vals, width, label='v5_fperc (baseline)', color=BLOCK_COLORS[0],
                   edgecolor='white', linewidth=0.8, alpha=0.85)
    bars3 = ax.bar(x + width, b6_vals, width, label='Block 6 (final)', color=BLOCK_COLORS[7],
                   edgecolor='white', linewidth=0.8, alpha=0.85)

    # Value annotations
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            if np.isfinite(h) and h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 1.5,
                        f'{h:.0f}', ha='center', va='bottom', fontsize=7.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels_display, fontsize=10)
    ax.set_ylabel('TWh')
    ax.set_title('Block 6 vs Reality vs Baseline', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    fig.savefig(PLOT_DIR / '03_vs_reality.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    print('  [3/7] Assessment vs reality')


# ─── PLOT 4: F > f_max Violations (Block 6) ──────────────────────────────────
def plot_violations(all_assets):
    b6_label = 'Block 6\nElecMix'
    if b6_label not in all_assets:
        return

    techs, f_vals, fmax_vals, pct_overs = [], [], [], []
    for tech, data in all_assets[b6_label].items():
        f = data['F']
        fmax = data['f_max']
        if f > fmax + 0.001 and fmax > 0:
            techs.append(tech)
            f_vals.append(f)
            fmax_vals.append(fmax)
            pct_overs.append((f - fmax) / fmax * 100)

    if not techs:
        print('  [4/7] No violations to plot')
        return

    # Sort by pct_over descending
    order = np.argsort(pct_overs)[::-1]
    techs = [techs[i] for i in order]
    f_vals = [f_vals[i] for i in order]
    fmax_vals = [fmax_vals[i] for i in order]
    pct_overs = [pct_overs[i] for i in order]

    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(techs))
    width = 0.35

    ax.bar(x - width / 2, fmax_vals, width, label='f_max (cap)', color=BLOCK_COLORS[2],
           edgecolor='white', alpha=0.85)
    ax.bar(x + width / 2, f_vals, width, label='F (actual)', color=BLOCK_COLORS[3],
           edgecolor='white', alpha=0.85)

    # % over annotations
    for i, pct in enumerate(pct_overs):
        ax.text(x[i] + width / 2, f_vals[i] + 0.05, f'+{pct:.0f}%',
                ha='center', va='bottom', fontsize=8, color=REALITY_COLOR, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(techs, fontsize=8, rotation=35, ha='right')
    ax.set_ylabel('Installed Capacity (GW)')
    ax.set_title('F > f_max Violations — Block 6 (Barrier Solver Tolerance)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    fig.savefig(PLOT_DIR / '04_violations.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    print('  [4/7] F > f_max violations')


# ─── PLOT 5: Electricity Generation Mix (Block 6 vs v5_fperc) ────────────────
def plot_elec_mix(all_assets):
    """Show electricity generation technologies F_year for v5 vs Block 6."""
    elec_techs = ['NUCLEAR', 'CCGT', 'COAL_US', 'WIND_ONSHORE', 'WIND_OFFSHORE',
                  'HYDRO_DAM', 'HYDRO_RIVER', 'PV_ROOFTOP', 'PV_UTILITY',
                  'GEOTHERMAL']

    b6_label = 'Block 6\nElecMix'
    v5_label = 'v5_fperc'

    v5_data = {}
    b6_data = {}
    for tech in elec_techs:
        v5_data[tech] = all_assets.get(v5_label, {}).get(tech, {}).get('F_year', 0) / 1000
        b6_data[tech] = all_assets.get(b6_label, {}).get(tech, {}).get('F_year', 0) / 1000

    # Only show techs with >0.01 in either
    show_techs = [t for t in elec_techs if v5_data[t] > 0.01 or b6_data[t] > 0.01]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(show_techs))
    width = 0.35

    v5_vals = [v5_data[t] for t in show_techs]
    b6_vals = [b6_data[t] for t in show_techs]

    ax.bar(x - width / 2, v5_vals, width, label='v5_fperc (baseline)', color=BLOCK_COLORS[0],
           edgecolor='white', alpha=0.85)
    ax.bar(x + width / 2, b6_vals, width, label='Block 6 (final)', color=BLOCK_COLORS[7],
           edgecolor='white', alpha=0.85)

    for i in range(len(show_techs)):
        for val, xoff in [(v5_vals[i], -width / 2), (b6_vals[i], width / 2)]:
            if val > 0.5:
                ax.text(x[i] + xoff, val + 0.3, f'{val:.1f}', ha='center',
                        va='bottom', fontsize=7.5)

    ax.set_xticks(x)
    ax.set_xticklabels([t.replace('_', '\n') for t in show_techs], fontsize=8)
    ax.set_ylabel('Annual Generation (TWh)')
    ax.set_title('Electricity Generation Mix: v5 Baseline vs Block 6', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    fig.savefig(PLOT_DIR / '05_electricity_mix.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    print('  [5/7] Electricity mix')


# ─── PLOT 6: Heating Technology Comparison ────────────────────────────────────
def plot_heat_mix(all_assets):
    """Show heating technologies F_year for v5 vs Block 6."""
    heat_techs = [
        'DHN_COGEN_WOOD', 'DHN_COGEN_GAS', 'DHN_COGEN_COAL', 'DHN_HP_ELEC',
        'DHN_BOILER_GAS', 'DHN_BOILER_WOOD', 'DHN_BOILER_OIL',
        'IND_BOILER_WOOD', 'IND_BOILER_GAS', 'IND_BOILER_COAL', 'IND_BOILER_OIL',
        'IND_COGEN_WOOD', 'IND_COGEN_GAS',
        'DEC_BOILER_WOOD', 'DEC_BOILER_GAS', 'DEC_BOILER_OIL', 'DEC_HP_ELEC',
    ]

    b6_label = 'Block 6\nElecMix'
    v5_label = 'v5_fperc'

    v5_heat, b6_heat = {}, {}
    for tech in heat_techs:
        v5_heat[tech] = all_assets.get(v5_label, {}).get(tech, {}).get('F_year', 0) / 1000
        b6_heat[tech] = all_assets.get(b6_label, {}).get(tech, {}).get('F_year', 0) / 1000

    show = [t for t in heat_techs if v5_heat[t] > 0.01 or b6_heat[t] > 0.01]

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(show))
    width = 0.35

    v5_vals = [v5_heat[t] for t in show]
    b6_vals = [b6_heat[t] for t in show]

    ax.bar(x - width / 2, v5_vals, width, label='v5_fperc', color=BLOCK_COLORS[0],
           edgecolor='white', alpha=0.85)
    ax.bar(x + width / 2, b6_vals, width, label='Block 6', color=BLOCK_COLORS[7],
           edgecolor='white', alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels([t.replace('_', '\n') for t in show], fontsize=7, rotation=45, ha='right')
    ax.set_ylabel('Annual Output (TWh)')
    ax.set_title('Heating & Industrial Technologies: v5 vs Block 6', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    fig.savefig(PLOT_DIR / '06_heating_mix.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    print('  [6/7] Heating mix')


# ─── PLOT 7: Resource Gap Waterfall (Block 6 vs Reality) ─────────────────────
def plot_gap_waterfall(all_resources):
    """Show the gap (%) between Block 6 final and reality targets."""
    items = [
        ('WOOD', 'Wood'),
        ('TOTAL_OIL', 'Total Oil'),
        ('GAS', 'Gas'),
        ('COAL', 'Coal'),
        ('URANIUM', 'Uranium'),
        ('RES_WIND', 'Wind'),
        ('RES_HYDRO', 'Hydro'),
    ]

    b6_label = 'Block 6\nElecMix'
    names, gaps = [], []
    for key, display in items:
        target = REALITY_TARGETS.get(key)
        actual = all_resources[b6_label].get(key, 0)
        if target and target > 0:
            gap_pct = (actual - target) / target * 100
            names.append(display)
            gaps.append(gap_pct)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = [BLOCK_COLORS[2] if g <= 0 else REALITY_COLOR for g in gaps]
    bars = ax.barh(range(len(names)), gaps, color=colors, edgecolor='white', alpha=0.85)

    # Annotate
    for i, (bar, g) in enumerate(zip(bars, gaps)):
        xpos = g + (2 if g >= 0 else -2)
        ha = 'left' if g >= 0 else 'right'
        ax.text(xpos, i, f'{g:+.0f}%', va='center', ha=ha, fontsize=10, fontweight='bold')

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=11)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel('Gap vs Reality (%)')
    ax.set_title('Block 6 Final — Gap to Reality Targets', fontsize=13, fontweight='bold')
    ax.invert_yaxis()
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    fig.savefig(PLOT_DIR / '07_gap_waterfall.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    print('  [7/7] Gap waterfall')


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print('Collecting data from block outputs...')
    all_resources, all_assets, all_objectives = collect_data()
    print(f'  Found {len(all_resources)} blocks with outputs\n')

    print('Generating plots...')
    plot_objective(all_objectives)
    plot_resource_evolution(all_resources)
    plot_vs_reality(all_resources)
    plot_violations(all_assets)
    plot_elec_mix(all_assets)
    plot_heat_mix(all_assets)
    plot_gap_waterfall(all_resources)

    print(f'\nAll plots saved to {PLOT_DIR}/')
    for f in sorted(PLOT_DIR.glob('*.png')):
        print(f'  {f.name}')


if __name__ == '__main__':
    main()
