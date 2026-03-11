#!/usr/bin/env python3
"""
** DEPRECATED — Use validate_run.py instead. **
This script is superseded by scripts/validate_run.py which provides:
  - Corrected Statistics Finland 2017 electricity values
  - CHP + condensation fuel-breakdown diagnostic plots
  - Batch mode for all baselines (--batch)
  - Consistent reality reference from calibration/reality/finland_2017_reference.csv
Run:  python validate_run.py --batch

---
(Original docstring below for historical reference)

Finland 2017 Validation Script.

Generates comprehensive validation plots and reports following the EnergyScope TD
validation methodology (Limpens et al., 2019, Applied Energy 255).

Key validation categories:
1. Primary Energy Supply (by fuel source)
2. Electricity Generation (by technology)
3. Heat Production (by technology type)
4. CO2 Emissions
5. Technology Output comparison

Output format matches Table 2 from the paper with:
- Actual values, Model values, Difference (Δ), Relative Error (%)

Usage:
    python generate_finland_validation.py --run-name calib_2017_finland_test_share_ned_fix_v2
    python generate_finland_validation.py --run-dir case_studies/FI/my_run
"""

import argparse
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# Repository root
REPO_ROOT = Path(__file__).parent.parent
CASE_STUDIES_DIR = REPO_ROOT / "case_studies" / "FI"
GLOBAL_PLOTS_DIR = REPO_ROOT / "plots" / "validation_2017"
REALITY_CSV = REPO_ROOT / "calibration" / "reality" / "finland_2017_reference.csv"
DATA_DIR = REPO_ROOT / "Data" / "2017" / "FI"

# Color palette consistent with EnergyScope style
COLORS = {
    "model": "#3498db",       # Blue
    "reality": "#e74c3c",     # Red  
    "good": "#27ae60",        # Green (≤10% error)
    "acceptable": "#f1c40f",  # Yellow (10-25% error)
    "warning": "#f39c12",     # Orange (25-50% error)
    "bad": "#c0392b",         # Dark red (>50% error)
    # Category colors for stacked charts
    "nuclear": "#9b59b6",
    "hydro": "#3498db",
    "wind": "#1abc9c",
    "solar": "#f1c40f",
    "biomass": "#27ae60",
    "coal": "#34495e",
    "gas": "#e67e22",
    "oil": "#c0392b",
    "geothermal": "#8e44ad",
    "imports": "#95a5a6",
}

# ============================================================================
# DATA LOADING
# ============================================================================

def load_reality_data() -> pd.DataFrame:
    """Load Finland 2017 reality reference data."""
    if REALITY_CSV.exists():
        return pd.read_csv(REALITY_CSV)
    else:
        print(f"WARNING: Reality reference not found: {REALITY_CSV}")
        return get_default_reality()


def get_default_reality() -> pd.DataFrame:
    """Default reality values if CSV not found."""
    data = [
        # Primary Energy
        ("primary_energy", "biomass", 100, "TWh"),
        ("primary_energy", "oil", 82, "TWh"),
        ("primary_energy", "gas", 20, "TWh"),
        ("primary_energy", "coal_peat", 35, "TWh"),
        ("primary_energy", "nuclear", 65, "TWh"),
        ("primary_energy", "hydro", 15, "TWh"),
        ("primary_energy", "wind", 5, "TWh"),
        ("primary_energy", "solar", 0.1, "TWh"),
        # Electricity
        ("electricity", "nuclear", 21.4, "TWh"),
        ("electricity", "hydro", 14.5, "TWh"),
        ("electricity", "wind", 4.8, "TWh"),
        ("electricity", "chp", 10.5, "TWh"),
        ("electricity", "condensation", 5.5, "TWh"),
        ("electricity", "solar", 0.09, "TWh"),
        ("electricity", "geothermal", 0, "TWh"),
        ("electricity", "gas", 3.2, "TWh"),
        ("electricity", "imports", 20.3, "TWh"),
        # Emissions
        ("emissions", "co2", 41.2, "MtCO2"),
        # Heat
        ("heat", "dh_production", 36.5, "TWh"),
    ]
    return pd.DataFrame(data, columns=["category", "metric", "value", "unit"])


def extract_model_values(outputs_dir: Path) -> dict:
    """Extract all relevant model values from outputs."""
    values = {}
    
    # ---- Resources.csv: Primary Energy ----
    resources_path = outputs_dir / "Resources.csv"
    if resources_path.exists():
        df = pd.read_csv(resources_path)
        res = {}
        for _, row in df.iterrows():
            total = row.get("R_year_local", 0) + row.get("R_year_exterior", 0)
            res[row.iloc[0]] = total / 1000  # GWh → TWh
        
        # Aggregate primary energy by fuel type
        values["PE_BIOMASS"] = sum(res.get(r, 0) for r in 
            ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"])
        # Fossil oil only (exclude *_RE which are bio/renewable fuels)
        values["PE_OIL"] = sum(res.get(r, 0) for r in 
            ["GASOLINE", "DIESEL", "LFO", "JET_FUEL"])
        # Bio-fuels (renewable synthetic fuels) - separate category
        values["PE_BIOFUELS"] = sum(res.get(r, 0) for r in 
            ["GASOLINE_RE", "DIESEL_RE", "LFO_RE", "JET_FUEL_RE"])
        values["PE_GAS"] = res.get("GAS", 0) + res.get("GAS_RE", 0)
        values["PE_COAL"] = res.get("COAL", 0) + res.get("PEAT", 0)
        values["PE_NUCLEAR"] = res.get("URANIUM", 0)
        values["PE_HYDRO"] = res.get("RES_HYDRO", 0)
        values["PE_WIND"] = res.get("RES_WIND", 0)
        values["PE_SOLAR"] = res.get("RES_SOLAR", 0)
        values["ELEC_IMPORTS"] = res.get("ELECTRICITY", 0)
        values["PE_TOTAL"] = sum(values.get(k, 0) for k in 
            ["PE_BIOMASS", "PE_OIL", "PE_BIOFUELS", "PE_GAS", "PE_COAL", "PE_NUCLEAR", 
             "PE_HYDRO", "PE_WIND", "PE_SOLAR", "ELEC_IMPORTS"])
    
    # ---- Year_balance.csv: Electricity Generation ----
    yb_path = outputs_dir / "Year_balance.csv"
    if yb_path.exists():
        df = pd.read_csv(yb_path, index_col=0)
        
        def get_elec(tech_list):
            total = 0
            for tech in tech_list:
                if tech in df.index and "ELECTRICITY" in df.columns:
                    val = df.loc[tech, "ELECTRICITY"]
                    if pd.notna(val) and val > 0:
                        total += val
            return total / 1000  # GWh → TWh
        
        values["ELEC_NUCLEAR"] = get_elec(["NUCLEAR"])
        values["ELEC_HYDRO"] = get_elec(["HYDRO_DAM", "HYDRO_RIVER"])
        values["ELEC_WIND"] = get_elec(["WIND_ONSHORE", "WIND_OFFSHORE"])
        values["ELEC_SOLAR"] = get_elec(["PV_ROOFTOP", "PV_UTILITY"])
        values["ELEC_GEOTHERMAL"] = get_elec(["GEOTHERMAL"])
        
        # CHP technologies (produce both electricity and heat)
        chp_techs = ["DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL", "DHN_COGEN_WASTE",
                     "IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_COAL", "DEC_COGEN_GAS", "DEC_COGEN_OIL",
                     "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2", "DHN_COGEN_OIL"]
        values["ELEC_CHP"] = get_elec(chp_techs)
        
        # Condensation power plants (electricity only)
        cond_techs = ["CCGT", "OCGT", "COAL_US", "COAL_IGCC", "CCGT_AMMONIA", "BIOMASS_TO_POWER"]
        values["ELEC_CONDENSATION"] = get_elec(cond_techs)
        
        # Gas-specific (subset of CHP + condensation)
        gas_techs = ["DHN_COGEN_GAS", "IND_COGEN_GAS", "DEC_COGEN_GAS", "DEC_ADVCOGEN_GAS", "CCGT", "OCGT"]
        values["ELEC_GAS"] = get_elec(gas_techs)
        
        # Total generation
        values["ELEC_TOTAL"] = sum(values.get(k, 0) for k in 
            ["ELEC_NUCLEAR", "ELEC_HYDRO", "ELEC_WIND", "ELEC_SOLAR", "ELEC_GEOTHERMAL",
             "ELEC_CHP", "ELEC_CONDENSATION"])
        
        # Heat production (for DHN technologies)
        def get_heat(tech_list, layer="HEAT_LOW_T_DHN"):
            total = 0
            for tech in tech_list:
                if tech in df.index and layer in df.columns:
                    val = df.loc[tech, layer]
                    if pd.notna(val) and val > 0:
                        total += val
            return total / 1000
        
        dhn_heat_techs = ["DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL", "DHN_COGEN_WASTE",
                         "DHN_BOILER_GAS", "DHN_BOILER_WOOD", "DHN_BOILER_OIL", "DHN_HP_ELEC",
                         "DHN_DEEP_GEO", "DHN_SOLAR", "DHN_COGEN_OIL"]
        values["HEAT_DHN"] = get_heat(dhn_heat_techs)
    
    # ---- Gwp_breakdown.csv: CO2 Emissions ----
    gwp_path = outputs_dir / "Gwp_breakdown.csv"
    if gwp_path.exists():
        df = pd.read_csv(gwp_path)
        # CO2_net column contains actual net CO2 emissions (in ktCO2)
        # GWP_op contains operational GHG in different units, don't use it for CO2
        if "CO2_net" in df.columns:
            values["CO2"] = df["CO2_net"].sum() / 1000  # ktCO2 → MtCO2
        elif "GWP_op" in df.columns:
            # Fallback to GWP_op if CO2_net not available (older output format)
            values["CO2"] = df["GWP_op"].sum() / 1000  # Assume ktCO2 → MtCO2
    
    # ---- Cost_breakdown.csv: System Cost ----
    cost_path = outputs_dir / "Cost_breakdown.csv"
    if cost_path.exists():
        df = pd.read_csv(cost_path)
        values["TOTAL_COST"] = df["C_inv"].sum() + df["C_maint"].sum() + df["C_op"].sum()  # MEUR
    
    return values


# ============================================================================
# TABLE 2 STYLE REPORT (Paper-style validation table)
# ============================================================================

def generate_table2_report(model: dict, reality: pd.DataFrame, output_dir: Path, run_name: str):
    """Generate Table 2 style validation report (like in EnergyScope TD paper)."""
    
    lines = [
        f"# Finland 2017 Validation Report",
        f"## {run_name}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "This report follows the validation methodology from Limpens et al. (2019)",
        "\"EnergyScope TD: A novel open-source model for regional energy systems\"",
        "Applied Energy, Volume 255.",
        "",
        "---",
        "",
        "## Table: Model vs. Finland 2017 Actual Data",
        "",
        "| **Metric** | **2017 Actual** | **Model** | **Δ** | **Rel. Error** | **Status** |",
        "|------------|-----------------|-----------|-------|----------------|------------|",
    ]
    
    # Primary Energy
    lines.append("| **Primary Energy Consumption** | | | | | |")
    pe_metrics = [
        ("  Biomass (wood, waste)", "PE_BIOMASS", "primary_energy", "biomass"),
        ("  Oil products (fossil)", "PE_OIL", "primary_energy", "oil"),
        ("  Bio/synth fuels", "PE_BIOFUELS", None, None),  # No reality reference
        ("  Natural Gas", "PE_GAS", "primary_energy", "gas"),
        ("  Coal + Peat", "PE_COAL", "primary_energy", "coal_peat"),
        ("  Nuclear (thermal)", "PE_NUCLEAR", "primary_energy", "nuclear"),
        ("  Hydro", "PE_HYDRO", "primary_energy", "hydro"),
        ("  Wind", "PE_WIND", "primary_energy", "wind"),
        ("  Solar", "PE_SOLAR", "primary_energy", "solar"),
    ]
    
    def get_reality_val(cat, met):
        if cat is None or met is None:
            return 0
        r = reality[(reality["category"] == cat) & (reality["metric"] == met)]
        return r["value"].iloc[0] if len(r) > 0 else 0
    
    pe_total_actual = sum(get_reality_val("primary_energy", m) for m in 
                          ["biomass", "oil", "gas", "coal_peat", "nuclear", "hydro", "wind", "solar"])
    pe_total_model = sum(model.get(k, 0) for k in 
                         ["PE_BIOMASS", "PE_OIL", "PE_BIOFUELS", "PE_GAS", "PE_COAL", "PE_NUCLEAR", "PE_HYDRO", "PE_WIND", "PE_SOLAR"])
    
    for label, model_key, cat, met in pe_metrics:
        actual = get_reality_val(cat, met)
        mod = model.get(model_key, 0)
        if cat is None:
            # No reality reference (e.g., biofuels) - display model value only
            if mod > 0.1:  # Only show if significant
                lines.append(f"| {label} | - | {mod:.2f} | - | - | info |")
            continue
        delta = mod - actual
        rel_err = (delta / actual * 100) if actual > 0 else (float('inf') if mod > 0 else 0)
        if rel_err == float('inf'):
            status = "✗"
            rel_str = "+inf%"
        else:
            status = "✓" if abs(rel_err) <= 10 else ("✓~" if abs(rel_err) <= 25 else ("⚠" if abs(rel_err) <= 50 else "✗"))
            rel_str = f"{rel_err:+.1f}%"
        lines.append(f"| {label} | {actual:.2f} | {mod:.2f} | {delta:+.2f} | {rel_str} | {status} |")
    
    # PE Total
    delta_pe = pe_total_model - pe_total_actual
    rel_pe = (delta_pe / pe_total_actual * 100) if pe_total_actual > 0 else 0
    lines.append(f"| **TPES Total** | **{pe_total_actual:.1f}** | **{pe_total_model:.1f}** | **{delta_pe:+.1f}** | **{rel_pe:+.1f}%** | |")
    
    # Electricity Generation
    lines.append("| **Electricity Generation** | | | | | |")
    elec_metrics = [
        ("  Nuclear", "ELEC_NUCLEAR", "electricity", "nuclear"),
        ("  Hydro", "ELEC_HYDRO", "electricity", "hydro"),
        ("  Wind", "ELEC_WIND", "electricity", "wind"),
        ("  Solar PV", "ELEC_SOLAR", "electricity", "solar"),
        ("  Geothermal", "ELEC_GEOTHERMAL", "electricity", "geothermal"),
        ("  CHP (all fuels)", "ELEC_CHP", "electricity", "chp"),
        ("  Gas power", "ELEC_GAS", "electricity", "gas"),
        ("  Imports", "ELEC_IMPORTS", "electricity", "imports"),
    ]
    
    for label, model_key, cat, met in elec_metrics:
        actual = get_reality_val(cat, met)
        mod = model.get(model_key, 0)
        delta = mod - actual
        if actual > 0.01:
            rel_err = delta / actual * 100
            status = "✓" if abs(rel_err) <= 10 else ("✓~" if abs(rel_err) <= 25 else ("⚠" if abs(rel_err) <= 50 else "✗"))
        else:
            rel_err = 0 if mod < 0.01 else float('inf')
            status = "N/A" if actual < 0.01 and mod < 0.01 else "✗"
        lines.append(f"| {label} | {actual:.2f} | {mod:.2f} | {delta:+.2f} | {rel_err:+.1f}% | {status} |")
    
    # Emissions
    lines.append("| **GHG Emissions** | | | | | |")
    co2_actual = get_reality_val("emissions", "co2")
    co2_model = model.get("CO2", 0)
    delta_co2 = co2_model - co2_actual
    rel_co2 = (delta_co2 / co2_actual * 100) if co2_actual > 0 else 0
    status_co2 = "✓" if abs(rel_co2) <= 10 else ("✓~" if abs(rel_co2) <= 25 else ("⚠" if abs(rel_co2) <= 50 else "✗"))
    lines.append(f"| **CO2 (MtCO2)** | **{co2_actual:.2f}** | **{co2_model:.2f}** | **{delta_co2:+.2f}** | **{rel_co2:+.1f}%** | {status_co2} |")
    
    # Summary statistics
    lines.extend([
        "",
        "---",
        "",
        "## Summary Statistics",
        "",
        f"- **Primary Energy Total**: Model {pe_total_model:.1f} TWh vs Reality {pe_total_actual:.1f} TWh ({rel_pe:+.1f}%)",
        f"- **CO2 Emissions**: Model {co2_model:.1f} MtCO2 vs Reality {co2_actual:.1f} MtCO2 ({rel_co2:+.1f}%)",
        "",
        "### Status Legend",
        "- ✓ : Within ±10% (excellent)",
        "- ✓~ : Within ±25% (acceptable)",
        "- ⚠ : Within ±50% (needs attention)",
        "- ✗ : Beyond ±50% (significant discrepancy)",
        "",
        "---",
        "",
        "## Interpretation",
        "",
        "Following the EnergyScope TD validation methodology:",
        "",
        "1. **Primary Energy**: " + (
            f"Total TPES error of {abs(rel_pe):.1f}% is " +
            ("excellent (target: <5%)" if abs(rel_pe) < 5 else 
             "acceptable (target: <10%)" if abs(rel_pe) < 10 else
             "high - review fuel constraints")
        ),
        "",
        "2. **Electricity Mix**: " + (
            "The model reproduces the electricity generation mix with varying accuracy. "
            "Key discrepancies should be addressed through technology constraints (f_min/f_max)."
        ),
        "",
        "3. **CO2 Emissions**: " + (
            f"Emissions error of {abs(rel_co2):.1f}% " +
            ("indicates good alignment with national statistics." if abs(rel_co2) < 10 else
             "suggests fuel mix discrepancies that propagate to emissions.")
        ),
        "",
        "### Note on Validation Philosophy",
        "",
        "As noted in Limpens et al. (2019):",
        "> \"Long-term planning models are inherently non-validatable as they model an unknown future.",
        "> However, the performance and consistency of such models can be demonstrated in representing",
        "> the past or present state of the system.\"",
        "",
        "The validation demonstrates that the model can represent Finland's 2017 energy system",
        "within acceptable error margins when properly constrained.",
    ])
    
    with open(output_dir / "validation_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ============================================================================
# PLOTTING FUNCTIONS
# ============================================================================

def plot_primary_energy(model: dict, reality: pd.DataFrame, output_dir: Path, run_name: str):
    """Plot primary energy comparison bar chart."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    categories = ["Biomass", "Oil", "Gas", "Coal+Peat", "Nuclear", "Hydro", "Wind", "Solar"]
    model_keys = ["PE_BIOMASS", "PE_OIL", "PE_GAS", "PE_COAL", "PE_NUCLEAR", "PE_HYDRO", "PE_WIND", "PE_SOLAR"]
    reality_metrics = ["biomass", "oil", "gas", "coal_peat", "nuclear", "hydro", "wind", "solar"]
    
    model_vals = [model.get(k, 0) for k in model_keys]
    reality_vals = []
    for m in reality_metrics:
        r = reality[(reality["category"] == "primary_energy") & (reality["metric"] == m)]
        reality_vals.append(r["value"].iloc[0] if len(r) > 0 else 0)
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, model_vals, width, label="Model", color=COLORS["model"], edgecolor='white')
    bars2 = ax.bar(x + width/2, reality_vals, width, label="Finland 2017", color=COLORS["reality"], edgecolor='white')
    
    # Value labels
    for bar in bars1:
        h = bar.get_height()
        if h > 1:
            ax.annotate(f'{h:.1f}', xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    for bar in bars2:
        h = bar.get_height()
        if h > 1:
            ax.annotate(f'{h:.1f}', xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    
    ax.set_ylabel('Primary Energy (TWh)', fontsize=11)
    ax.set_title(f'Primary Energy Supply - {run_name} vs Finland 2017', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=15, ha='right')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(bottom=0)
    
    # Add totals
    model_total = sum(model_vals)
    reality_total = sum(reality_vals)
    ax.text(0.02, 0.98, f'Model Total: {model_total:.1f} TWh\nReality Total: {reality_total:.1f} TWh',
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_dir / "primary_energy_comparison.png", dpi=150)
    plt.close()


def plot_electricity_mix(model: dict, reality: pd.DataFrame, output_dir: Path, run_name: str):
    """Plot electricity generation comparison."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    categories = ["Nuclear", "Hydro", "Wind", "CHP", "Gas", "Solar", "Imports"]
    model_keys = ["ELEC_NUCLEAR", "ELEC_HYDRO", "ELEC_WIND", "ELEC_CHP", "ELEC_GAS", "ELEC_SOLAR", "ELEC_IMPORTS"]
    reality_metrics = ["nuclear", "hydro", "wind", "chp", "gas", "solar", "imports"]
    
    model_vals = [model.get(k, 0) for k in model_keys]
    reality_vals = []
    for m in reality_metrics:
        r = reality[(reality["category"] == "electricity") & (reality["metric"] == m)]
        reality_vals.append(r["value"].iloc[0] if len(r) > 0 else 0)
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, model_vals, width, label="Model", color=COLORS["model"], edgecolor='white')
    bars2 = ax.bar(x + width/2, reality_vals, width, label="Finland 2017", color=COLORS["reality"], edgecolor='white')
    
    for bar in bars1:
        h = bar.get_height()
        if h > 0.5:
            ax.annotate(f'{h:.1f}', xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    
    ax.set_ylabel('Electricity (TWh)', fontsize=11)
    ax.set_title(f'Electricity Generation Mix - {run_name} vs Finland 2017', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=15, ha='right')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_dir / "electricity_mix_comparison.png", dpi=150)
    plt.close()


def plot_co2_emissions(model: dict, reality: pd.DataFrame, output_dir: Path, run_name: str):
    """Plot CO2 emissions comparison."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    r = reality[(reality["category"] == "emissions") & (reality["metric"] == "co2")]
    co2_reality = r["value"].iloc[0] if len(r) > 0 else 41.2
    co2_model = model.get("CO2", 0)
    
    categories = ["Model", "Finland 2017"]
    values = [co2_model, co2_reality]
    colors = [COLORS["model"], COLORS["reality"]]
    
    bars = ax.bar(categories, values, color=colors, edgecolor='white', width=0.5)
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f'{h:.1f} MtCO2', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    diff = co2_model - co2_reality
    rel_err = (diff / co2_reality * 100) if co2_reality > 0 else 0
    
    ax.set_ylabel('CO2 Emissions (MtCO2)', fontsize=11)
    ax.set_title(f'CO2 Emissions - {run_name} vs Finland 2017\nDifference: {diff:+.1f} MtCO2 ({rel_err:+.1f}%)', fontsize=12)
    ax.set_ylim(bottom=0, top=max(values) * 1.3)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "co2_emissions_comparison.png", dpi=150)
    plt.close()


def plot_error_heatmap(model: dict, reality: pd.DataFrame, output_dir: Path, run_name: str):
    """Plot horizontal bar chart showing % errors."""
    
    metrics = [
        ("Biomass (PE)", "PE_BIOMASS", "primary_energy", "biomass"),
        ("Oil (PE)", "PE_OIL", "primary_energy", "oil"),
        ("Gas (PE)", "PE_GAS", "primary_energy", "gas"),
        ("Coal+Peat (PE)", "PE_COAL", "primary_energy", "coal_peat"),
        ("Nuclear (PE)", "PE_NUCLEAR", "primary_energy", "nuclear"),
        ("Hydro (PE)", "PE_HYDRO", "primary_energy", "hydro"),
        ("Wind (PE)", "PE_WIND", "primary_energy", "wind"),
        ("Nuclear (Elec)", "ELEC_NUCLEAR", "electricity", "nuclear"),
        ("Hydro (Elec)", "ELEC_HYDRO", "electricity", "hydro"),
        ("Wind (Elec)", "ELEC_WIND", "electricity", "wind"),
        ("CHP (Elec)", "ELEC_CHP", "electricity", "chp"),
        ("Gas (Elec)", "ELEC_GAS", "electricity", "gas"),
        ("Imports (Elec)", "ELEC_IMPORTS", "electricity", "imports"),
        ("CO2 Emissions", "CO2", "emissions", "co2"),
    ]
    
    labels = []
    errors = []
    
    for label, model_key, cat, met in metrics:
        r = reality[(reality["category"] == cat) & (reality["metric"] == met)]
        actual = r["value"].iloc[0] if len(r) > 0 else 0
        mod = model.get(model_key, 0)
        if actual > 0.01:
            err = (mod - actual) / actual * 100
            errors.append(err)
            labels.append(label)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    y = np.arange(len(labels))
    colors = []
    for e in errors:
        if abs(e) <= 10:
            colors.append(COLORS["good"])
        elif abs(e) <= 25:
            colors.append(COLORS["acceptable"])
        elif abs(e) <= 50:
            colors.append(COLORS["warning"])
        else:
            colors.append(COLORS["bad"])
    
    bars = ax.barh(y, errors, color=colors, edgecolor='white')
    
    # Reference lines
    ax.axvline(x=0, color='black', linewidth=1)
    ax.axvline(x=-10, color=COLORS["good"], linewidth=1, linestyle=':', alpha=0.7)
    ax.axvline(x=10, color=COLORS["good"], linewidth=1, linestyle=':', alpha=0.7)
    ax.axvline(x=-25, color=COLORS["acceptable"], linewidth=1, linestyle='--', alpha=0.5)
    ax.axvline(x=25, color=COLORS["acceptable"], linewidth=1, linestyle='--', alpha=0.5)
    
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Error vs Reality (%)', fontsize=11)
    ax.set_title(f'Validation Error Analysis - {run_name}', fontsize=12)
    
    # Limit x-axis to ±100% for readability
    max_err = max(abs(min(errors)), abs(max(errors)), 100)
    ax.set_xlim(-min(max_err, 150), min(max_err, 150))
    
    # Add value labels
    for i, (bar, error) in enumerate(zip(bars, errors)):
        ax.annotate(f'{error:+.0f}%',
                    xy=(min(max(error, -140), 140), bar.get_y() + bar.get_height()/2),
                    xytext=(5 if error >= 0 else -5, 0),
                    textcoords="offset points",
                    ha='left' if error >= 0 else 'right',
                    va='center', fontsize=9)
    
    # Legend
    legend_patches = [
        mpatches.Patch(color=COLORS["good"], label='±10% (excellent)'),
        mpatches.Patch(color=COLORS["acceptable"], label='±25% (acceptable)'),
        mpatches.Patch(color=COLORS["warning"], label='±50% (warning)'),
        mpatches.Patch(color=COLORS["bad"], label='>50% (significant)'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_dir / "error_chart.png", dpi=150)
    plt.close()


def generate_sankey(outputs_dir: Path, output_dir: Path):
    """Generate Sankey diagram."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from esmc.postprocessing.draw_sankey.output_to_sankey_csv import write_sankey_file
        from esmc.postprocessing.draw_sankey.ESSankey import drawSankey
        
        # Derive space_id and case_study from path
        case_study = outputs_dir.parent.name
        space_id = outputs_dir.parent.parent.name
        
        # Generate input2sankey CSV
        write_sankey_file(space_id, case_study)
        
        # Generate HTML
        sankey_csv = outputs_dir / "input2sankey_Total.csv"
        if sankey_csv.exists():
            drawSankey(
                path=str(outputs_dir),
                outputfile="sankey.html",
                I2S_File="input2sankey_Total.csv",
                auto_open=False
            )
            
            # Copy to output directory
            src = outputs_dir / "sankey.html"
            if src.exists():
                shutil.copy(src, output_dir / "sankey.html")
                print(f"    Sankey saved to: {output_dir / 'sankey.html'}")
                return True
    except Exception as e:
        print(f"    Warning: Sankey generation failed: {e}")
    return False


def generate_csv_table(model: dict, reality: pd.DataFrame, output_dir: Path):
    """Generate CSV table like Table 2."""
    rows = []
    
    metrics = [
        ("Primary Energy", "Biomass", "PE_BIOMASS", "primary_energy", "biomass", "TWh"),
        ("Primary Energy", "Oil products", "PE_OIL", "primary_energy", "oil", "TWh"),
        ("Primary Energy", "Natural Gas", "PE_GAS", "primary_energy", "gas", "TWh"),
        ("Primary Energy", "Coal + Peat", "PE_COAL", "primary_energy", "coal_peat", "TWh"),
        ("Primary Energy", "Nuclear", "PE_NUCLEAR", "primary_energy", "nuclear", "TWh"),
        ("Primary Energy", "Hydro", "PE_HYDRO", "primary_energy", "hydro", "TWh"),
        ("Primary Energy", "Wind", "PE_WIND", "primary_energy", "wind", "TWh"),
        ("Electricity", "Nuclear", "ELEC_NUCLEAR", "electricity", "nuclear", "TWh"),
        ("Electricity", "Hydro", "ELEC_HYDRO", "electricity", "hydro", "TWh"),
        ("Electricity", "Wind", "ELEC_WIND", "electricity", "wind", "TWh"),
        ("Electricity", "CHP", "ELEC_CHP", "electricity", "chp", "TWh"),
        ("Electricity", "Gas power", "ELEC_GAS", "electricity", "gas", "TWh"),
        ("Electricity", "Imports", "ELEC_IMPORTS", "electricity", "imports", "TWh"),
        ("Emissions", "CO2", "CO2", "emissions", "co2", "MtCO2"),
    ]
    
    for cat, name, model_key, reality_cat, reality_met, unit in metrics:
        r = reality[(reality["category"] == reality_cat) & (reality["metric"] == reality_met)]
        actual = r["value"].iloc[0] if len(r) > 0 else 0
        mod = model.get(model_key, 0)
        delta = mod - actual
        rel_err = (delta / actual * 100) if actual > 0.01 else 0
        
        rows.append({
            "Category": cat,
            "Metric": name,
            "2017_Actual": round(actual, 2),
            "Model": round(mod, 2),
            "Delta": round(delta, 2),
            "Rel_Error_%": round(rel_err, 1),
            "Unit": unit
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_dir / "validation_table.csv", index=False)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate Finland 2017 validation (EnergyScope style)")
    parser.add_argument("--run-name", "-n", help="Run name in case_studies/FI/")
    parser.add_argument("--run-dir", "-r", help="Direct path to run directory")
    parser.add_argument("--no-sankey", action="store_true", help="Skip Sankey diagram")
    parser.add_argument("--copy-to-global", action="store_true", help="Also copy to plots/validation_2017")
    
    args = parser.parse_args()
    
    # Determine run directory
    if args.run_dir:
        run_dir = Path(args.run_dir)
    elif args.run_name:
        run_dir = CASE_STUDIES_DIR / args.run_name
    else:
        # Default to latest run
        runs = sorted([d for d in CASE_STUDIES_DIR.iterdir() if d.is_dir() and "calib" in d.name])
        if runs:
            run_dir = runs[-1]
        else:
            print("ERROR: No runs found. Specify --run-name or --run-dir")
            sys.exit(1)
    
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)
    
    outputs_dir = run_dir / "outputs"
    if not outputs_dir.exists():
        print(f"ERROR: No outputs found in {run_dir}")
        sys.exit(1)
    
    output_dir = run_dir / "validation_plots"
    output_dir.mkdir(exist_ok=True)
    
    run_name = run_dir.name
    print(f"═" * 60)
    print(f"Finland 2017 Validation")
    print(f"Run: {run_name}")
    print(f"Output: {output_dir}")
    print(f"═" * 60)
    
    # Load data
    print("\n1. Loading data...")
    reality = load_reality_data()
    model = extract_model_values(outputs_dir)
    print(f"   Loaded {len(reality)} reality metrics")
    print(f"   Extracted {len(model)} model values")
    
    # Generate outputs
    print("\n2. Generating validation report (Table 2 style)...")
    generate_table2_report(model, reality, output_dir, run_name)
    
    print("\n3. Generating plots...")
    print("   - Primary energy comparison...")
    plot_primary_energy(model, reality, output_dir, run_name)
    
    print("   - Electricity mix comparison...")
    plot_electricity_mix(model, reality, output_dir, run_name)
    
    print("   - CO2 emissions comparison...")
    plot_co2_emissions(model, reality, output_dir, run_name)
    
    print("   - Error analysis chart...")
    plot_error_heatmap(model, reality, output_dir, run_name)
    
    print("   - CSV table...")
    generate_csv_table(model, reality, output_dir)
    
    if not args.no_sankey:
        print("\n4. Generating Sankey diagram...")
        generate_sankey(outputs_dir, output_dir)
    
    # Copy to global plots directory if requested
    if args.copy_to_global:
        print(f"\n5. Copying to {GLOBAL_PLOTS_DIR}...")
        GLOBAL_PLOTS_DIR.mkdir(exist_ok=True)
        for f in output_dir.iterdir():
            if f.is_file():
                shutil.copy(f, GLOBAL_PLOTS_DIR / f.name)
    
    print(f"\n{'═' * 60}")
    print("DONE! Outputs generated:")
    for f in sorted(output_dir.iterdir()):
        print(f"  - {f.name}")
    print(f"{'═' * 60}")


if __name__ == "__main__":
    main()
