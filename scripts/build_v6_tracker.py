"""
Create comprehensive v6 calibration tracking workbook.
Collects results from all block runs and generates Excel + markdown summary.
"""
import pandas as pd
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BLOCKS = {
    'v5_fperc': 'calib_2017_finland_v5_fperc',
    'Block0_degeneracy': 'calib_2017_finland_v6_block0_degeneracy',
    'Block1_oil': 'calib_2017_finland_v6_block1_oil',
    'Block2_biomass': 'calib_2017_finland_v6_block2_biomass',
    'Block3_nuclear': 'calib_2017_finland_v6_block3_nuclear',
    'Block4_solar': 'calib_2017_finland_v6_block4_solar',
    'Block5_coal': 'calib_2017_finland_v6_block5_coal',
    'Block6_elecmix': 'calib_2017_finland_v6_block6_elecmix',
}

# Reality targets (TWh unless noted)
REALITY = {
    'WOOD': 105.0,
    'LFO': 40.0,  # approx LFO portion of 96 TWh total oil
    'DIESEL': 25.0,
    'GASOLINE': 16.0,
    'JET_FUEL': 5.0,
    'GAS': 25.0,
    'COAL': 50.0,  # coal + peat
    'URANIUM': 65.0,  # primary nuclear
    'WASTE': 8.0,
    'ELECTRICITY_import': 20.0,
    'Total_Oil': 96.0,
    'Total_Biomass': 105.0,
}

KEY_RESOURCES = ['ELECTRICITY','GASOLINE','DIESEL','LFO','JET_FUEL','GAS',
                 'WOOD','ENERGY_CROPS_2','BIOWASTE','BIOMASS_RESIDUES',
                 'COAL','URANIUM','WASTE','WET_BIOMASS',
                 'RES_WIND','RES_SOLAR','RES_HYDRO','RES_GEO']

KEY_TECHNOLOGIES = ['NUCLEAR','CCGT','COAL_US','WIND_ONSHORE','WIND_OFFSHORE',
                     'HYDRO_DAM','HYDRO_RIVER','PV_ROOFTOP','PV_UTILITY',
                     'IND_BOILER_WOOD','IND_COGEN_WOOD','DHN_COGEN_WOOD',
                     'DHN_COGEN_COAL','IND_BOILER_COAL',
                     'DEC_BOILER_WOOD','DEC_HP_ELEC',
                     'CARGO_LFO','TRUCK_DIESEL','CAR_PHEV','CAR_GASOLINE',
                     'OIL_TO_HVC','TRAIN_FREIGHT']


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
            res_dict[f"{name}_local"] = row['R_year_local']
            res_dict[f"{name}_exterior"] = row['R_year_exterior']
            res_dict[f"{name}_total"] = row['R_year_local'] + row['R_year_exterior']
        all_resources[label] = res_dict
        
        # Assets
        assets = pd.read_csv(out_dir / 'Assets.csv')
        assets_dict = {}
        for _, row in assets.iterrows():
            tech = row['Technologies']
            assets_dict[f"{tech}_F"] = row['F']
            assets_dict[f"{tech}_f_min"] = row['f_min']
            assets_dict[f"{tech}_f_max"] = row['f_max']
        all_assets[label] = assets_dict
        
        # Objective
        obj = pd.read_csv(out_dir / 'Objective.csv')
        all_objectives[label] = obj.iloc[0, 1]
    
    return all_resources, all_assets, all_objectives


def build_resource_table(all_resources):
    """Build resource comparison table across blocks."""
    rows = []
    for res_name in KEY_RESOURCES:
        row = {'Resource': res_name}
        for label in BLOCKS.keys():
            if label in all_resources:
                key = f"{res_name}_total"
                val = all_resources[label].get(key, 0)
                row[label] = round(val, 0)
        rows.append(row)
    
    # Add derived metrics
    for label in BLOCKS.keys():
        if label in all_resources:
            oil_total = sum(all_resources[label].get(f"{r}_total", 0) 
                          for r in ['LFO','DIESEL','GASOLINE','JET_FUEL'])
            bio_total = sum(all_resources[label].get(f"{r}_total", 0)
                          for r in ['WOOD','ENERGY_CROPS_2','BIOWASTE','BIOMASS_RESIDUES','WET_BIOMASS'])
            for row in rows:
                pass
            rows.append({'Resource': 'TOTAL_OIL', **{l: '' for l in BLOCKS.keys()}})
            rows[-1][label] = round(oil_total, 0)
            rows.append({'Resource': 'TOTAL_BIOMASS', **{l: '' for l in BLOCKS.keys()}})
            rows[-1][label] = round(bio_total, 0)
    
    # Rebuild derived rows properly
    derived = {}
    for label in BLOCKS.keys():
        if label in all_resources:
            derived.setdefault('TOTAL_OIL', {})[label] = round(sum(
                all_resources[label].get(f"{r}_total", 0) 
                for r in ['LFO','DIESEL','GASOLINE','JET_FUEL']), 0)
            derived.setdefault('TOTAL_BIOMASS', {})[label] = round(sum(
                all_resources[label].get(f"{r}_total", 0)
                for r in ['WOOD','ENERGY_CROPS_2','BIOWASTE','BIOMASS_RESIDUES','WET_BIOMASS']), 0)
    
    # Remove badly built rows and add properly
    rows = [r for r in rows if r['Resource'] not in ('TOTAL_OIL', 'TOTAL_BIOMASS')]
    for metric, vals in derived.items():
        row = {'Resource': metric}
        row.update(vals)
        rows.append(row)
    
    return pd.DataFrame(rows)


def build_tech_table(all_assets):
    """Build technology F-value comparison table."""
    rows = []
    for tech in KEY_TECHNOLOGIES:
        row = {'Technology': tech}
        for label in BLOCKS.keys():
            if label in all_assets:
                f_val = all_assets[label].get(f"{tech}_F", 0)
                f_max = all_assets[label].get(f"{tech}_f_max", None)
                row[f"{label}_F"] = round(f_val, 3)
                if f_max is not None:
                    row[f"{label}_f_max"] = round(f_max, 3)
        rows.append(row)
    return pd.DataFrame(rows)


def build_violations_table(all_assets):
    """Build table of F > f_max violations."""
    rows = []
    # Get all technologies from Block6
    if 'Block6_elecmix' in all_assets:
        techs = set()
        for key in all_assets['Block6_elecmix'].keys():
            if key.endswith('_F'):
                techs.add(key[:-2])
        
        for label in BLOCKS.keys():
            if label in all_assets:
                for tech in sorted(techs):
                    f = all_assets[label].get(f"{tech}_F", 0)
                    fmax = all_assets[label].get(f"{tech}_f_max", 1e15)
                    if f > fmax + 0.001:
                        rows.append({
                            'Block': label,
                            'Technology': tech,
                            'F': round(f, 3),
                            'f_max': round(fmax, 3),
                            'Excess': round(f - fmax, 3),
                            'Pct_over': round((f - fmax) / fmax * 100, 1),
                        })
    return pd.DataFrame(rows)


def build_objective_table(all_objectives):
    """Build objective function comparison."""
    rows = [{'Block': label, 'Objective': val} for label, val in all_objectives.items()]
    return pd.DataFrame(rows)


def generate_markdown(res_table, tech_table, obj_table, viol_table):
    """Generate markdown summary report."""
    lines = []
    lines.append("# Finland 2017 v6 Calibration — Block-by-Block Results\n")
    lines.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    lines.append("## Solver Note\n")
    lines.append("All runs use CPLEX 22.1.2 barrier solver (crossover disabled — consistently")
    lines.append("produces 0 simplex iterations regardless of settings). The barrier interior-point")
    lines.append("solution does NOT exactly satisfy variable bounds or linear constraints.")
    lines.append("Tolerance violations (MaxAbs up to ~10^2 on bounds, ~10^5 on constraints) mean")
    lines.append("that f_max caps and resource availability limits are only **approximately** enforced.")
    lines.append("solve_result_num = -1 for all runs (feasible with numerical issues).\n")
    
    lines.append("## Objective Function Progression\n")
    lines.append("| Block | Objective (MEUR) |")
    lines.append("|-------|-----------------|")
    for _, row in obj_table.iterrows():
        lines.append(f"| {row['Block']} | {row['Objective']:.2e} |")
    lines.append("")
    
    lines.append("## Key Resource Usage (GWh)\n")
    lines.append("Reality targets: WOOD=105K, Total Oil=96K, GAS=25K, COAL+PEAT=50K, NUCLEAR=65K\n")
    cols = ['Resource'] + [c for c in res_table.columns if c != 'Resource']
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    lines.append(header)
    lines.append(sep)
    for _, row in res_table.iterrows():
        vals = [str(row.get(c, '')) for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    lines.append("")
    
    lines.append("## F > f_max Violations (Block 6 final)\n")
    b6_viols = viol_table[viol_table['Block'] == 'Block6_elecmix']
    if len(b6_viols) > 0:
        lines.append("| Technology | F (GW) | f_max (GW) | Excess | % Over |")
        lines.append("|-----------|--------|-----------|--------|--------|")
        for _, row in b6_viols.iterrows():
            lines.append(f"| {row['Technology']} | {row['F']:.3f} | {row['f_max']:.3f} | {row['Excess']:.3f} | {row['Pct_over']:.1f}% |")
    lines.append("")
    
    lines.append("## Block Descriptions\n")
    lines.append("- **Block 0 (Degeneracy)**: Cap 120 previously-unconstrained techs (f_max 1e15 → 5-100K)")
    lines.append("- **Block 1 (Oil)**: LFO 150K→80K, JET_FUEL 15K→5K [historical realism]")
    lines.append("- **Block 2 (Biomass)**: Wood tech fmin_perc forcing, GAS 28K→22K, COAL 50K→35K [calibration forcing]")
    lines.append("- **Block 3 (Nuclear)**: URANIUM 100K→62K, NUCLEAR f_min=2.76 [historical realism]")
    lines.append("- **Block 4 (Solar)**: PV_ROOFTOP 2→0.05, PV_UTILITY 1→0.02 [historical realism]")
    lines.append("- **Block 5 (Coal)**: IND_BOILER_COAL fmin_perc 0.15, DHN_COGEN_COAL fmin_perc 0.20 [calibration forcing]")
    lines.append("- **Block 6 (ElecMix)**: CCGT f_max 1.5→1.2, WIND_ONSHORE f_max 2.1→1.7 / f_min 1.5, WIND_OFFSHORE f_max 0.1→0.03 [mixed]")
    lines.append("")
    
    lines.append("## Assessment vs Reality\n")
    lines.append("| Metric | Reality (TWh) | v5_fperc | Block 6 | Direction |")
    lines.append("|--------|-------------|---------|---------|-----------|")
    
    # Get v5 and b6 values
    v5_col = 'v5_fperc' if 'v5_fperc' in res_table.columns else None
    b6_col = 'Block6_elecmix' if 'Block6_elecmix' in res_table.columns else None
    
    assessments = [
        ('WOOD', 105000, 'WOOD'),
        ('Total Oil', 96000, 'TOTAL_OIL'),
        ('GAS', 25000, 'GAS'),
        ('COAL', 50000, 'COAL'),
        ('URANIUM', 65000, 'URANIUM'),
    ]
    for name, target, res_key in assessments:
        v5_val = ''
        b6_val = ''
        direction = ''
        r = res_table[res_table['Resource'] == res_key]
        if len(r) > 0 and v5_col:
            v5_raw = r.iloc[0].get(v5_col, '')
            b6_raw = r.iloc[0].get(b6_col, '')
            if v5_raw != '' and b6_raw != '':
                v5_val = f"{float(v5_raw)/1000:.1f}K"
                b6_val = f"{float(b6_raw)/1000:.1f}K"
                diff = float(b6_raw) - float(v5_raw)
                if abs(diff) > 100:
                    toward_target = (abs(float(b6_raw) - target) < abs(float(v5_raw) - target))
                    direction = "IMPROVED" if toward_target else "WORSE"
        lines.append(f"| {name} | {target/1000:.0f}K | {v5_val} | {b6_val} | {direction} |")
    
    return "\n".join(lines)


def main():
    print("Collecting data from all block outputs...")
    all_resources, all_assets, all_objectives = collect_data()
    
    print("Building tables...")
    res_table = build_resource_table(all_resources)
    tech_table = build_tech_table(all_assets)
    viol_table = build_violations_table(all_assets)
    obj_table = build_objective_table(all_objectives)
    
    # Save to Excel
    excel_path = ROOT / 'Data' / 'exogenous_data' / 'Finland_2017_v6_calibration_tracker.xlsx'
    print(f"Writing Excel to {excel_path}...")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        res_table.to_excel(writer, sheet_name='Resources', index=False)
        tech_table.to_excel(writer, sheet_name='Technologies', index=False)
        obj_table.to_excel(writer, sheet_name='Objective', index=False)
        viol_table.to_excel(writer, sheet_name='Violations', index=False)
    
    # Generate markdown report
    md = generate_markdown(res_table, tech_table, obj_table, viol_table)
    md_path = ROOT / 'Docs' / 'finland_2017_v6_block_results.md'
    print(f"Writing markdown to {md_path}...")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print("\nDone!")
    print(f"  Excel: {excel_path}")
    print(f"  Markdown: {md_path}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY: Resource progression (GWh)")
    print("="*70)
    print(res_table.to_string(index=False))


if __name__ == '__main__':
    main()
