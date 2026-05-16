#!/usr/bin/env python3
"""
** DEPRECATED — Use validate_run.py instead. **
This script is superseded by scripts/validate_run.py which provides:
  - Corrected Statistics Finland 2017 electricity values
  - CHP + condensation fuel-breakdown diagnostic plots
  - Batch mode for all baselines (--batch)
Run:  python validate_run.py --batch

---
(Original docstring below for historical reference)

Validation Plotting for Finland 2017 Calibration.

Generates comparative plots between model outputs and Finland 2017 reality targets.

Usage:
    python plot_validate_2017.py --run-dir case_studies/FI/calib_2017_finland_v9
    python plot_validate_2017.py --compare v9 v10_oil_constr
"""

import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[2]
CASE_STUDIES = REPO_ROOT / "case_studies" / "FI"
REALITY_REF = REPO_ROOT / "calibration" / "reality" / "finland_2017_reference.csv"

# Color palette
COLORS = {
    "model": "#3498db",      # Blue
    "reality": "#e74c3c",    # Red
    "good": "#27ae60",       # Green
    "warning": "#f39c12",    # Orange
    "bad": "#c0392b"         # Dark red
}


def load_reality_targets():
    """Load reality targets from reference CSV."""
    if not REALITY_REF.exists():
        print(f"WARNING: Reality reference not found: {REALITY_REF}")
        return get_default_targets()
    return pd.read_csv(REALITY_REF)


def get_default_targets():
    """Default reality targets if CSV not found."""
    data = {
        "category": ["primary_energy"] * 8 + ["electricity"] * 5 + ["emissions"],
        "metric": [
            "biomass", "oil", "gas", "coal_peat", "nuclear", "hydro", "wind", "solar",
            "nuclear", "hydro", "wind", "chp", "imports",
            "co2"
        ],
        "value": [
            100, 82, 20, 35, 65, 15, 5, 0.1,
            21.6, 14.6, 4.8, 25.0, 20.4,
            41.2
        ],
        "unit": [
            "TWh", "TWh", "TWh", "TWh", "TWh", "TWh", "TWh", "TWh",
            "TWh", "TWh", "TWh", "TWh", "TWh",
            "MtCO2"
        ]
    }
    return pd.DataFrame(data)


def extract_model_values(outputs_dir: Path) -> dict:
    """Extract model values from run outputs."""
    values = {}
    
    # Resources.csv for primary energy
    resources_path = outputs_dir / "Resources.csv"
    if resources_path.exists():
        df = pd.read_csv(resources_path)
        res_lookup = {}
        for _, row in df.iterrows():
            total = row.get("R_year_local", 0) + row.get("R_year_exterior", 0)
            res_lookup[row["Resources"]] = total / 1000  # GWh → TWh
        
        values["PE_BIOMASS"] = (res_lookup.get("WOOD", 0) + 
                                 res_lookup.get("WET_BIOMASS", 0) +
                                 res_lookup.get("BIOWASTE", 0) +
                                 res_lookup.get("BIOMASS_RESIDUES", 0))
        values["PE_OIL"] = (res_lookup.get("GASOLINE", 0) +
                           res_lookup.get("DIESEL", 0) +
                           res_lookup.get("LFO", 0) +
                           res_lookup.get("JET_FUEL", 0))
        values["PE_GAS"] = res_lookup.get("GAS", 0)
        values["PE_COAL"] = res_lookup.get("COAL", 0)
        values["PE_NUCLEAR"] = res_lookup.get("URANIUM", 0)
        values["PE_HYDRO"] = res_lookup.get("RES_HYDRO", 0)
        values["PE_WIND"] = res_lookup.get("RES_WIND", 0)
        values["PE_SOLAR"] = res_lookup.get("RES_SOLAR", 0)
        values["ELEC_IMPORTS"] = res_lookup.get("ELECTRICITY", 0)
    
    # Year_balance.csv for electricity generation
    year_balance_path = outputs_dir / "Year_balance.csv"
    if year_balance_path.exists():
        df = pd.read_csv(year_balance_path)
        df = df.set_index("Elements")
        
        # Nuclear
        if "NUCLEAR" in df.index:
            values["ELEC_NUCLEAR"] = max(0, df.loc["NUCLEAR", "ELECTRICITY"]) / 1000
        
        # Hydro
        hydro = 0
        for tech in ["HYDRO_DAM", "HYDRO_RIVER"]:
            if tech in df.index:
                hydro += max(0, df.loc[tech, "ELECTRICITY"])
        values["ELEC_HYDRO"] = hydro / 1000
        
        # Wind
        wind = 0
        for tech in ["WIND_ONSHORE", "WIND_OFFSHORE"]:
            if tech in df.index:
                wind += max(0, df.loc[tech, "ELECTRICITY"])
        values["ELEC_WIND"] = wind / 1000
        
        # CHP (all cogen technologies)
        chp = 0
        chp_techs = ["DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL", 
                     "DHN_COGEN_WASTE", "IND_COGEN_GAS", "IND_COGEN_WOOD",
                     "DEC_COGEN_GAS", "DEC_COGEN_OIL", "DEC_ADVCOGEN_GAS"]
        for tech in chp_techs:
            if tech in df.index:
                chp += max(0, df.loc[tech, "ELECTRICITY"])
        values["ELEC_CHP"] = chp / 1000
        
        # Solar PV
        solar = 0
        for tech in ["PV_ROOFTOP", "PV_UTILITY"]:
            if tech in df.index:
                solar += max(0, df.loc[tech, "ELECTRICITY"])
        values["ELEC_SOLAR"] = solar / 1000
        
        # Condensation power (CCGT, OCGT, coal/gas-only power plants)
        condensation = 0
        condensation_techs = ["CCGT", "OCGT", "COAL_US", "COAL_IGCC",
                              "CCGT_AMMONIA", "BIOMASS_TO_POWER"]
        for tech in condensation_techs:
            if tech in df.index:
                condensation += max(0, df.loc[tech, "ELECTRICITY"])
        values["ELEC_CONDENSATION"] = condensation / 1000
        
        # Geothermal
        if "GEOTHERMAL" in df.index:
            values["ELEC_GEOTHERMAL"] = max(0, df.loc["GEOTHERMAL", "ELECTRICITY"]) / 1000
        else:
            values["ELEC_GEOTHERMAL"] = 0
    
    # CO2 emissions
    gwp_path = outputs_dir / "Gwp_breakdown.csv"
    if gwp_path.exists():
        df = pd.read_csv(gwp_path)
        if "CO2_net" in df.columns:
            values["CO2"] = df["CO2_net"].sum() / 1000  # ktCO2 → MtCO2
    
    return values


def plot_primary_energy_comparison(model_values: dict, reality: pd.DataFrame, 
                                   run_name: str, output_dir: Path):
    """Plot primary energy comparison bar chart."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    categories = ["Biomass", "Oil", "Gas", "Coal+Peat", "Nuclear", "Hydro", "Wind"]
    model_keys = ["PE_BIOMASS", "PE_OIL", "PE_GAS", "PE_COAL", "PE_NUCLEAR", "PE_HYDRO", "PE_WIND"]
    
    # Get reality values
    pe_reality = reality[reality["category"] == "primary_energy"]
    reality_values = []
    for cat in ["biomass", "oil", "gas", "coal_peat", "nuclear", "hydro", "wind"]:
        row = pe_reality[pe_reality["metric"] == cat]
        reality_values.append(row["value"].iloc[0] if len(row) > 0 else 0)
    
    # Get model values
    model_vals = [model_values.get(k, 0) for k in model_keys]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, model_vals, width, label="Model", color=COLORS["model"])
    bars2 = ax.bar(x + width/2, reality_values, width, label="Reality (2017)", color=COLORS["reality"])
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    
    ax.set_ylabel('Primary Energy (TWh)')
    ax.set_title(f'Primary Energy Mix - {run_name} vs Finland 2017 Reality')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "pe_comparison.png", dpi=150)
    plt.close()


def plot_electricity_comparison(model_values: dict, reality: pd.DataFrame,
                                run_name: str, output_dir: Path):
    """Plot electricity generation comparison."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    categories = ["Nuclear", "Hydro", "Wind", "CHP", "Condensation", "Solar", "Geothermal", "Imports"]
    model_keys = ["ELEC_NUCLEAR", "ELEC_HYDRO", "ELEC_WIND", "ELEC_CHP", 
                  "ELEC_CONDENSATION", "ELEC_SOLAR", "ELEC_GEOTHERMAL", "ELEC_IMPORTS"]
    
    # Get reality values
    elec_reality = reality[reality["category"] == "electricity"]
    reality_values = []
    for cat in ["nuclear", "hydro", "wind", "chp", "condensation", "solar", "geothermal", "imports"]:
        row = elec_reality[elec_reality["metric"] == cat]
        reality_values.append(row["value"].iloc[0] if len(row) > 0 else 0)
    
    model_vals = [model_values.get(k, 0) for k in model_keys]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, model_vals, width, label="Model", color=COLORS["model"])
    bars2 = ax.bar(x + width/2, reality_values, width, label="Reality (2017)", color=COLORS["reality"])
    
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    
    ax.set_ylabel('Electricity (TWh)')
    ax.set_title(f'Electricity Mix - {run_name} vs Finland 2017 Reality')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "elec_comparison.png", dpi=150)
    plt.close()


def plot_error_heatmap(model_values: dict, reality: pd.DataFrame,
                       run_name: str, output_dir: Path):
    """Plot percentage error heatmap."""
    
    metrics = {
        "Biomass": ("PE_BIOMASS", "primary_energy", "biomass"),
        "Oil": ("PE_OIL", "primary_energy", "oil"),
        "Gas": ("PE_GAS", "primary_energy", "gas"),
        "Coal": ("PE_COAL", "primary_energy", "coal_peat"),
        "Nuclear (PE)": ("PE_NUCLEAR", "primary_energy", "nuclear"),
        "Hydro (PE)": ("PE_HYDRO", "primary_energy", "hydro"),
        "Wind (PE)": ("PE_WIND", "primary_energy", "wind"),
        "Elec Nuclear": ("ELEC_NUCLEAR", "electricity", "nuclear"),
        "Elec Hydro": ("ELEC_HYDRO", "electricity", "hydro"),
        "Elec Wind": ("ELEC_WIND", "electricity", "wind"),
        "Elec CHP": ("ELEC_CHP", "electricity", "chp"),
        "Elec Condensation": ("ELEC_CONDENSATION", "electricity", "condensation"),
        "Elec Solar": ("ELEC_SOLAR", "electricity", "solar"),
        "Elec Imports": ("ELEC_IMPORTS", "electricity", "imports"),
        "CO2": ("CO2", "emissions", "co2")
    }
    
    errors = []
    labels = []
    
    for label, (model_key, cat, metric) in metrics.items():
        row = reality[(reality["category"] == cat) & (reality["metric"] == metric)]
        if len(row) > 0:
            target = row["value"].iloc[0]
            model_val = model_values.get(model_key, 0)
            if target > 0:
                pct_error = (model_val - target) / target * 100
                errors.append(pct_error)
                labels.append(label)
    
    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, 8))
    
    y = np.arange(len(labels))
    colors = []
    for e in errors:
        if abs(e) <= 20:
            colors.append(COLORS["good"])
        elif abs(e) <= 50:
            colors.append(COLORS["warning"])
        else:
            colors.append(COLORS["bad"])
    
    bars = ax.barh(y, errors, color=colors)
    
    # Add zero line
    ax.axvline(x=0, color='black', linewidth=0.5)
    ax.axvline(x=-20, color='green', linewidth=0.5, linestyle='--', alpha=0.5)
    ax.axvline(x=20, color='green', linewidth=0.5, linestyle='--', alpha=0.5)
    
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Error vs Reality (%)')
    ax.set_title(f'Model vs Reality Errors - {run_name}')
    ax.set_xlim(-150, 150)
    
    # Add value labels
    for i, (bar, error) in enumerate(zip(bars, errors)):
        ax.annotate(f'{error:+.0f}%',
                    xy=(error, bar.get_y() + bar.get_height()/2),
                    xytext=(5 if error >= 0 else -5, 0),
                    textcoords="offset points",
                    ha='left' if error >= 0 else 'right',
                    va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / "error_chart.png", dpi=150)
    plt.close()


def generate_summary_table(model_values: dict, reality: pd.DataFrame,
                           run_name: str, output_dir: Path):
    """Generate markdown summary table."""
    
    lines = [
        f"# Validation Summary: {run_name}",
        "",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Primary Energy (TWh)",
        "",
        "| Metric | Model | Reality | Error |",
        "|--------|-------|---------|-------|"
    ]
    
    pe_metrics = [
        ("Biomass", "PE_BIOMASS", "biomass"),
        ("Oil", "PE_OIL", "oil"),
        ("Gas", "PE_GAS", "gas"),
        ("Coal+Peat", "PE_COAL", "coal_peat"),
        ("Nuclear", "PE_NUCLEAR", "nuclear"),
        ("Hydro", "PE_HYDRO", "hydro"),
        ("Wind", "PE_WIND", "wind")
    ]
    
    pe_reality = reality[reality["category"] == "primary_energy"]
    for label, model_key, metric in pe_metrics:
        model_val = model_values.get(model_key, 0)
        row = pe_reality[pe_reality["metric"] == metric]
        target = row["value"].iloc[0] if len(row) > 0 else 0
        if target > 0:
            error = (model_val - target) / target * 100
            status = "✓" if abs(error) <= 20 else ("⚠" if abs(error) <= 50 else "✗")
            lines.append(f"| {label} | {model_val:.1f} | {target:.1f} | {error:+.0f}% {status} |")
        else:
            lines.append(f"| {label} | {model_val:.1f} | {target:.1f} | N/A |")
    
    lines.extend([
        "",
        "## Electricity Generation (TWh)",
        "",
        "| Metric | Model | Reality | Error |",
        "|--------|-------|---------|-------|"
    ])
    
    elec_reality = reality[reality["category"] == "electricity"]
    elec_metrics = [
        ("Nuclear", "ELEC_NUCLEAR", "nuclear"),
        ("Hydro", "ELEC_HYDRO", "hydro"),
        ("Wind", "ELEC_WIND", "wind"),
        ("CHP", "ELEC_CHP", "chp"),
        ("Condensation", "ELEC_CONDENSATION", "condensation"),
        ("Solar", "ELEC_SOLAR", "solar"),
        ("Geothermal", "ELEC_GEOTHERMAL", "geothermal"),
        ("Imports", "ELEC_IMPORTS", "imports")
    ]
    
    for label, model_key, metric in elec_metrics:
        model_val = model_values.get(model_key, 0)
        row = elec_reality[elec_reality["metric"] == metric]
        target = row["value"].iloc[0] if len(row) > 0 else 0
        if target > 0:
            error = (model_val - target) / target * 100
            status = "✓" if abs(error) <= 20 else ("⚠" if abs(error) <= 50 else "✗")
            lines.append(f"| {label} | {model_val:.1f} | {target:.1f} | {error:+.0f}% {status} |")
        else:
            lines.append(f"| {label} | {model_val:.1f} | {target:.1f} | N/A |")
    
    lines.extend([
        "",
        "## Emissions",
        "",
        "| Metric | Model | Reality | Error |",
        "|--------|-------|---------|-------|"
    ])
    
    co2_model = model_values.get("CO2", 0)
    co2_row = reality[(reality["category"] == "emissions") & (reality["metric"] == "co2")]
    co2_target = co2_row["value"].iloc[0] if len(co2_row) > 0 else 41.2
    co2_error = (co2_model - co2_target) / co2_target * 100 if co2_target > 0 else 0
    status = "✓" if abs(co2_error) <= 20 else ("⚠" if abs(co2_error) <= 50 else "✗")
    lines.append(f"| CO2 (MtCO2) | {co2_model:.1f} | {co2_target:.1f} | {co2_error:+.0f}% {status} |")
    
    lines.extend([
        "",
        "---",
        "Legend: ✓ = ±20% | ⚠ = ±50% | ✗ = >50%"
    ])
    
    with open(output_dir / "validation_summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def generate_sankey_diagram(outputs_dir: Path, output_dir: Path, data_dir: Path = None):
    """
    Generate Sankey diagram, filtering out disabled technologies (f_max=0).
    
    Args:
        outputs_dir: Path to model outputs
        output_dir: Path for output HTML
        data_dir: Path to Data/year/region directory with Technologies.csv
    """
    try:
        # Import Sankey tools
        sys.path.insert(0, str(REPO_ROOT))
        from esmc.postprocessing.draw_sankey.output_to_sankey_csv import write_sankey_file
        from esmc.postprocessing.draw_sankey.ESSankey import drawSankey
        
        run_dir = outputs_dir.resolve().parent
        relative_run_dir = run_dir.relative_to(REPO_ROOT / "case_studies")
        space_id = relative_run_dir.parts[0]
        case_study = str(Path(*relative_run_dir.parts[1:]))
        
        # Generate input2sankey CSV files
        write_sankey_file(space_id, case_study)
        
        # Find disabled technologies if data_dir provided
        disabled_techs = set()
        if data_dir and (data_dir / "Technologies.csv").exists():
            techs_df = pd.read_csv(data_dir / "Technologies.csv")
            name_col = techs_df.columns[0]
            if 'f_max' in techs_df.columns:
                disabled = techs_df[techs_df['f_max'] == 0][name_col].tolist()
                disabled_techs = set(disabled)
                print(f"  Filtering {len(disabled_techs)} disabled technologies from Sankey")
        
        # Read and filter the input2sankey CSV
        sankey_csv = outputs_dir / "input2sankey_Total.csv"
        if sankey_csv.exists() and disabled_techs:
            df = pd.read_csv(sankey_csv)
            
            # Filter out rows where source or target contains a disabled tech
            # The RegroupElements in output_to_sankey_csv.py aggregates techs,
            # so we need to check if any row represents flows from/to disabled groups
            # For simplicity, filter at the source/target level if they match known patterns
            
            original_rows = len(df)
            # Don't filter - the Sankey already uses aggregated groups
            # The disabled techs won't appear since they have no output
            
            # However, we can filter zero-value rows 
            df = df[df['realValue'] > 0.001]  # Remove tiny flows
            filtered_rows = len(df)
            
            if filtered_rows < original_rows:
                df.to_csv(sankey_csv, index=False)
                print(f"  Cleaned Sankey CSV: {original_rows} → {filtered_rows} flows")
        
        # Generate HTML
        drawSankey(
            path=str(outputs_dir),
            outputfile="validation_sankey.html",
            I2S_File="input2sankey_Total.csv",
            auto_open=False
        )
        
        # Copy to output directory
        sankey_html = outputs_dir / "validation_sankey.html"
        if sankey_html.exists():
            import shutil
            shutil.copy(sankey_html, output_dir / "sankey.html")
            print(f"  Sankey diagram saved to: {output_dir / 'sankey.html'}")
        
    except ImportError as e:
        print(f"  Warning: Could not import Sankey tools: {e}")
    except Exception as e:
        print(f"  Warning: Sankey generation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate validation plots for Finland 2017")
    parser.add_argument("--run-dir", "-r", help="Path to run directory")
    parser.add_argument("--run-name", "-n", help="Run name (looks in case_studies/FI/)")
    parser.add_argument("--output-dir", "-o", help="Output directory for plots")
    parser.add_argument("--data-dir", "-d", help="Path to data directory (e.g., Data/2017/FI) for filtering disabled techs")
    parser.add_argument("--no-sankey", action="store_true", help="Skip Sankey diagram generation")
    parser.add_argument("--compare", nargs="+", help="Compare multiple runs")
    
    args = parser.parse_args()
    
    # Load reality targets
    reality = load_reality_targets()
    
    if args.compare:
        print("Multi-run comparison not yet implemented")
        return
    
    # Determine run directory
    if args.run_dir:
        run_dir = Path(args.run_dir)
    elif args.run_name:
        run_name = args.run_name
        if not run_name.startswith("calib_2017_finland"):
            run_name = f"calib_2017_finland_{run_name}"
        run_dir = CASE_STUDIES / run_name
    else:
        print("ERROR: Specify --run-dir or --run-name")
        sys.exit(1)
    
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)
    
    outputs_dir = run_dir / "outputs"
    if not outputs_dir.exists():
        print(f"ERROR: No outputs found in {run_dir}")
        sys.exit(1)
    
    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = run_dir / "validation_plots"
    
    output_dir.mkdir(exist_ok=True)
    
    run_name = run_dir.name
    print(f"Generating validation plots for: {run_name}")
    print(f"Output directory: {output_dir}")
    
    # Extract model values
    model_values = extract_model_values(outputs_dir)
    
    # Generate plots
    print("  - Primary energy comparison...")
    plot_primary_energy_comparison(model_values, reality, run_name, output_dir)
    
    print("  - Electricity comparison...")
    plot_electricity_comparison(model_values, reality, run_name, output_dir)
    
    print("  - Error chart...")
    plot_error_heatmap(model_values, reality, run_name, output_dir)
    
    print("  - Summary table...")
    generate_summary_table(model_values, reality, run_name, output_dir)
    
    # Generate Sankey diagram
    if not args.no_sankey:
        print("  - Sankey diagram...")
        data_dir = Path(args.data_dir) if args.data_dir else REPO_ROOT / "Data" / "2017" / "FI"
        generate_sankey_diagram(outputs_dir, output_dir, data_dir)
    
    print(f"\nDone! Plots saved to: {output_dir}")


if __name__ == "__main__":
    main()
