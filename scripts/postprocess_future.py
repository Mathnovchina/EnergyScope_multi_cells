#!/usr/bin/env python3
"""
================================================================
  postprocess_future.py  —  Analysis plots for Finland 2035/2050
================================================================

Generates per-run validation plots and Sankey diagrams for future
scenario runs solved by run_fi_baseline_future.py.

Plots produced (saved to <run_dir>/validation_plots/):
  1. capacity_comparison.png  — installed capacity (GW) for top techs
  2. electricity_mix.png      — yearly electricity production (TWh)
  3. heat_supply.png          — DHN + DEC heat supply
  4. primary_energy.png       — primary energy by resource group
  5. cost_breakdown.png       — C_inv + C_maint by sector
  6. gwp_breakdown.png        — lifecycle GWP + direct CO2
  7. comparison_2035_2050.png — side-by-side key metrics (generated
                                 only when both runs are processed)
  8. summary_report.md        — text summary

Sankeys (saved to <run_dir>/outputs/, HTML viewable in browser):
  input2sankey_Total.csv           — CSV data for Sankey
  generated_sankey_Total.html      — interactive Plotly Sankey

Usage
-----
  # Both years + 2017 Sankey (auto-detect latest successful run dirs)
  python scripts/postprocess_future.py --auto

  # Explicit run dirs + Sankey for 2017 too
  python scripts/postprocess_future.py \\
      --run-2035 case_studies/FI/manual_runs/20260324_141200__national_plan_2035 \\
      --run-2050 case_studies/FI/manual_runs/20260324_142019__national_plan_2050 \\
      --run-2017 case_studies/FI/_archive_2017calib/20260323_173930__v37_solar \\
      --sankey

  # Plots only, skip Sankey
  python scripts/postprocess_future.py --auto --skip-sankey
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

MANUAL_RUNS = REPO_ROOT / "case_studies" / "FI" / "manual_runs"

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
COLOURS = {
    "2035": "#3498db",
    "2050": "#e74c3c",
    "2017": "#27ae60",
    "C_inv": "#2980b9",
    "C_maint": "#7fb3d3",
    "C_op": "#d5e8f3",
    "GWP_constr": "#8e44ad",
    "GWP_op": "#e8daef",
    "CO2_net": "#c0392b",
}

# Technology sector mapping for cost breakdown  #
SECTOR_MAP = {
    # Power sector
    "NUCLEAR": "Power", "NUCLEAR_SMR": "Power",
    "CCGT": "Power", "CCGT_AMMONIA": "Power",
    "COAL_US": "Power", "COAL_IGCC": "Power", "BIOMASS_TO_POWER": "Power",
    "PV_ROOFTOP": "Power", "PV_UTILITY": "Power",
    "WIND_ONSHORE": "Power", "WIND_OFFSHORE": "Power",
    "HYDRO_DAM": "Power", "HYDRO_RIVER": "Power",
    "GEOTHERMAL": "Power", "TIDAL_STREAM": "Power", "TIDAL_RANGE": "Power",
    "WAVE": "Power",
    # Heat – DHN
    "DHN_HP_ELEC": "Heat-DHN", "DHN_COGEN_GAS": "Heat-DHN",
    "DHN_COGEN_WOOD": "Heat-DHN", "DHN_COGEN_WASTE": "Heat-DHN",
    "DHN_BOILER_GAS": "Heat-DHN", "DHN_BOILER_WOOD": "Heat-DHN",
    "DHN_BOILER_OIL": "Heat-DHN", "DHN_DEEP_GEO": "Heat-DHN", "DHN_SOLAR": "Heat-DHN",
    # Heat – DEC
    "DEC_HP_ELEC": "Heat-DEC", "DEC_THHP_GAS": "Heat-DEC",
    "DEC_COGEN_GAS": "Heat-DEC", "DEC_COGEN_OIL": "Heat-DEC",
    "DEC_ADVCOGEN_GAS": "Heat-DEC", "DEC_ADVCOGEN_H2": "Heat-DEC",
    "DEC_BOILER_GAS": "Heat-DEC", "DEC_BOILER_WOOD": "Heat-DEC",
    "DEC_BOILER_OIL": "Heat-DEC", "DEC_SOLAR": "Heat-DEC", "DEC_DIRECT_ELEC": "Heat-DEC",
    # Industry
    "IND_COGEN_GAS": "Industry", "IND_COGEN_WOOD": "Industry", "IND_COGEN_WASTE": "Industry",
    "IND_BOILER_GAS": "Industry", "IND_BOILER_WOOD": "Industry",
    "IND_BOILER_BIOWASTE": "Industry", "IND_BOILER_OIL": "Industry",
    "IND_BOILER_COAL": "Industry", "IND_BOILER_WASTE": "Industry",
    "IND_DIRECT_ELEC": "Industry", "IND_ELEC_COLD": "Industry",
    # Transport
    "CAR_GASOLINE": "Transport", "CAR_DIESEL": "Transport", "CAR_NG": "Transport",
    "CAR_BEV": "Transport", "CAR_PHEV": "Transport", "CAR_HEV": "Transport",
    "CAR_FUEL_CELL": "Transport", "CAR_METHANOL": "Transport",
    "BUS_COACH_DIESEL": "Transport", "BUS_COACH_FC_HYBRIDH2": "Transport",
    "TRAIN_PUB": "Transport", "TRAIN_FREIGHT": "Transport",
    "TRUCK_DIESEL": "Transport", "TRUCK_ELEC": "Transport",
    "TRUCK_FUEL_CELL": "Transport", "TRUCK_NG": "Transport", "TRUCK_METHANOL": "Transport",
    "BOAT_FREIGHT_DIESEL": "Transport", "BOAT_FREIGHT_NG": "Transport",
    "BOAT_FREIGHT_METHANOL": "Transport",
    # Hydrogen / synthetic fuels
    "H2_ELECTROLYSIS": "H2/Synfuels", "H2_NG": "H2/Synfuels", "H2_BIOMASS": "H2/Synfuels",
    "HABER_BOSCH": "H2/Synfuels", "SYN_METHANATION": "H2/Synfuels",
    # Storage
    "BATT_LI": "Storage", "BEV_BATT": "Storage", "PHEV_BATT": "Storage",
    "TS_DHN_DAILY": "Storage", "TS_DHN_SEASONAL": "Storage",
    "TS_DEC_HP_ELEC": "Storage",
}

# ============================================================================
# DATA EXTRACTION
# ============================================================================

def load_assets(outputs: Path) -> pd.DataFrame:
    p = outputs / "Assets.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, index_col=0)


def load_year_balance(outputs: Path) -> pd.DataFrame:
    p = outputs / "Year_balance.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, index_col=0)


def load_resources(outputs: Path) -> pd.DataFrame:
    p = outputs / "Resources.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, index_col=0)


def load_cost(outputs: Path) -> pd.DataFrame:
    p = outputs / "Cost_breakdown.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, index_col=0)


def load_gwp(outputs: Path) -> pd.DataFrame:
    p = outputs / "Gwp_breakdown.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, index_col=0)


def load_objective(outputs: Path) -> float:
    p = outputs / "TotalCost.csv"
    if p.exists():
        df = pd.read_csv(p, header=None)
        return float(df.iloc[0, 0])
    p = outputs / "Objective.csv"
    if p.exists():
        df = pd.read_csv(p, header=None)
        return float(df.iloc[0, 0])
    return float("nan")


def extract_electricity(yb: pd.DataFrame) -> dict:
    """Extract electricity production by source (TWh) from Year_balance."""
    if yb.empty or "ELECTRICITY" not in yb.columns:
        return {}

    def _get(techs):
        s = 0.0
        for t in techs:
            if t in yb.index:
                v = float(yb.loc[t, "ELECTRICITY"])
                if v > 0:
                    s += v
        return s / 1000  # GWh → TWh

    return {
        "Nuclear": _get(["NUCLEAR", "NUCLEAR_SMR"]),
        "Hydro": _get(["HYDRO_DAM", "HYDRO_RIVER"]),
        "Wind": _get(["WIND_ONSHORE", "WIND_OFFSHORE"]),
        "Solar PV": _get(["PV_ROOFTOP", "PV_UTILITY"]),
        "CHP": _get([
            "DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_WASTE",
            "IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_WASTE",
            "DEC_COGEN_GAS", "DEC_COGEN_OIL",
            "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2",
        ]),
        "Condensation": _get(["CCGT", "OCGT", "COAL_US", "COAL_IGCC", "BIOMASS_TO_POWER"]),
        "Geothermal": _get(["GEOTHERMAL"]),
    }


def extract_heat(yb: pd.DataFrame) -> dict:
    """Extract DHN + DEC heat supply (TWh) from Year_balance."""
    if yb.empty:
        return {}

    dhn_techs = [
        "DHN_HP_ELEC", "DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_WASTE",
        "DHN_BOILER_GAS", "DHN_BOILER_WOOD", "DHN_BOILER_OIL",
        "DHN_DEEP_GEO", "DHN_SOLAR",
    ]
    dec_techs = [
        "DEC_HP_ELEC", "DEC_THHP_GAS",
        "DEC_COGEN_GAS", "DEC_COGEN_OIL", "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2",
        "DEC_BOILER_GAS", "DEC_BOILER_WOOD", "DEC_BOILER_OIL",
        "DEC_SOLAR", "DEC_DIRECT_ELEC",
    ]

    def _col_sum(techs, col):
        if col not in yb.columns:
            return 0.0
        s = 0.0
        for t in techs:
            if t in yb.index:
                v = float(yb.loc[t, col])
                if v > 0:
                    s += v
        return s / 1000

    return {
        "DHN HP": _col_sum(["DHN_HP_ELEC"], "HEAT_LOW_T_DHN"),
        "DHN CHP+Boiler": _col_sum([t for t in dhn_techs if t != "DHN_HP_ELEC"], "HEAT_LOW_T_DHN"),
        "DEC HP": _col_sum(["DEC_HP_ELEC"], "HEAT_LOW_T_DECEN"),
        "DEC Gas/Wood": _col_sum([t for t in dec_techs if t != "DEC_HP_ELEC"], "HEAT_LOW_T_DECEN"),
        "Ind Heat (HT)": _col_sum(
            ["IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_WASTE",
             "IND_BOILER_GAS", "IND_BOILER_WOOD", "IND_BOILER_BIOWASTE",
             "IND_BOILER_OIL", "IND_BOILER_COAL", "IND_BOILER_WASTE",
             "IND_DIRECT_ELEC"], "HEAT_HIGH_T"),
    }


def extract_primary_energy(res: pd.DataFrame) -> dict:
    """Primary energy by resource group (TWh)."""
    if res.empty:
        return {}

    def _sum(resources):
        s = 0.0
        for r in resources:
            if r in res.index:
                row = res.loc[r]
                s += float(row.get("R_year_local", 0)) + float(row.get("R_year_exterior", 0))
        return s / 1000

    return {
        "Biomass": _sum(["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"]),
        "Waste": _sum(["WASTE"]),
        "Nuclear": _sum(["URANIUM"]),
        "Wind": _sum(["RES_WIND"]),
        "Hydro": _sum(["RES_HYDRO"]),
        "Solar": _sum(["RES_SOLAR"]),
        "Gas": _sum(["GAS", "GAS_RE"]),
        "Oil products": _sum(["GASOLINE", "DIESEL", "LFO", "JET_FUEL",
                               "GASOLINE_RE", "DIESEL_RE", "LFO_RE", "JET_FUEL_RE"]),
        "H2/Ammonia": _sum(["H2", "H2_RE", "AMMONIA", "AMMONIA_RE", "METHANOL", "METHANOL_RE"]),
    }


def extract_capacity(assets: pd.DataFrame, threshold_gw: float = 0.005) -> pd.DataFrame:
    """Top technologies by installed capacity F (GW)."""
    if assets.empty or "F" not in assets.columns:
        return pd.DataFrame()
    cap = assets["F"].copy()
    cap = cap[cap > threshold_gw].sort_values(ascending=False)
    return cap


def extract_cost_by_sector(cost: pd.DataFrame) -> pd.DataFrame:
    """Sum C_inv + C_maint by sector."""
    if cost.empty:
        return pd.DataFrame()
    rows = []
    for tech, row in cost.iterrows():
        sector = SECTOR_MAP.get(tech, "Other")
        c_inv = float(row.get("C_inv", 0))
        c_maint = float(row.get("C_maint", 0))
        c_op = float(row.get("C_op", 0))
        if abs(c_inv) + abs(c_maint) + abs(c_op) > 0.1:
            rows.append({"sector": sector, "C_inv": c_inv, "C_maint": c_maint, "C_op": c_op})
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df.groupby("sector")[["C_inv", "C_maint", "C_op"]].sum().sort_values("C_inv", ascending=False)


def extract_gwp_totals(gwp: pd.DataFrame) -> dict:
    """Sum GWP components (ktCO2-eq)."""
    if gwp.empty:
        return {}
    result = {}
    if "GWP_constr" in gwp.columns:
        result["GWP_constr"] = float(gwp["GWP_constr"].sum())
    if "GWP_op" in gwp.columns:
        result["GWP_op"] = float(gwp["GWP_op"].sum())
    if "CO2_net" in gwp.columns:
        result["CO2_net"] = float(gwp["CO2_net"].sum())
    return result


# ============================================================================
# PLOTTING FUNCTIONS
# ============================================================================

def plot_capacity(cap_dict: dict, out: Path):
    """Installed capacity comparison across years."""
    # Collect all technologies with any nonzero capacity
    all_techs = sorted(
        {t for cap in cap_dict.values() for t in cap.index},
        key=lambda t: max(cap.get(t, 0) for cap in cap_dict.values()),
        reverse=True,
    )
    # Keep only top 30
    all_techs = all_techs[:30]
    if not all_techs:
        return

    years = list(cap_dict.keys())
    x = np.arange(len(all_techs))
    w = 0.8 / len(years)
    fig, ax = plt.subplots(figsize=(16, 7))

    for i, yr in enumerate(years):
        cap = cap_dict[yr]
        vals = [cap.get(t, 0.0) for t in all_techs]
        color = COLOURS.get(yr, "#888")
        bars = ax.bar(x + (i - len(years) / 2 + 0.5) * w, vals, w,
                      label=yr, color=color, edgecolor="white", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(all_techs, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("Installed capacity (GW)")
    ax.set_title("Installed Capacity — Finland Baseline Scenarios")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(out / "capacity_comparison.png", dpi=150)
    plt.close()


def plot_electricity(elec_dict: dict, out: Path):
    cats = ["Nuclear", "Hydro", "Wind", "Solar PV", "CHP", "Condensation", "Geothermal"]
    years = list(elec_dict.keys())
    x = np.arange(len(cats))
    w = 0.8 / len(years)

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, yr in enumerate(years):
        d = elec_dict[yr]
        vals = [d.get(c, 0.0) for c in cats]
        color = COLOURS.get(yr, "#888")
        ax.bar(x + (i - len(years) / 2 + 0.5) * w, vals, w,
               label=yr, color=color, edgecolor="white", alpha=0.85)
        # label nonzero bars
        for j, v in enumerate(vals):
            if v > 0.5:
                ax.text(x[j] + (i - len(years) / 2 + 0.5) * w, v + 0.3,
                        f"{v:.1f}", ha="center", fontsize=6)

    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=15, ha="right")
    ax.set_ylabel("TWh/year")
    ax.set_title("Electricity Production Mix — Finland Baseline Scenarios")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(out / "electricity_mix.png", dpi=150)
    plt.close()


def plot_heat(heat_dict: dict, out: Path):
    cats = ["DHN HP", "DHN CHP+Boiler", "DEC HP", "DEC Gas/Wood", "Ind Heat (HT)"]
    years = list(heat_dict.keys())
    x = np.arange(len(cats))
    w = 0.8 / len(years)

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, yr in enumerate(years):
        d = heat_dict[yr]
        vals = [d.get(c, 0.0) for c in cats]
        color = COLOURS.get(yr, "#888")
        ax.bar(x + (i - len(years) / 2 + 0.5) * w, vals, w,
               label=yr, color=color, edgecolor="white", alpha=0.85)
        for j, v in enumerate(vals):
            if v > 0.3:
                ax.text(x[j] + (i - len(years) / 2 + 0.5) * w, v + 0.2,
                        f"{v:.1f}", ha="center", fontsize=6)

    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=15, ha="right")
    ax.set_ylabel("TWh/year")
    ax.set_title("Heat Supply — Finland Baseline Scenarios")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(out / "heat_supply.png", dpi=150)
    plt.close()


def plot_primary_energy(pe_dict: dict, out: Path):
    cats = ["Biomass", "Waste", "Nuclear", "Wind", "Hydro", "Solar", "Gas", "Oil products", "H2/Ammonia"]
    years = list(pe_dict.keys())
    x = np.arange(len(cats))
    w = 0.8 / len(years)

    fig, ax = plt.subplots(figsize=(13, 6))
    for i, yr in enumerate(years):
        d = pe_dict[yr]
        vals = [d.get(c, 0.0) for c in cats]
        color = COLOURS.get(yr, "#888")
        ax.bar(x + (i - len(years) / 2 + 0.5) * w, vals, w,
               label=yr, color=color, edgecolor="white", alpha=0.85)
        for j, v in enumerate(vals):
            if v > 1.0:
                ax.text(x[j] + (i - len(years) / 2 + 0.5) * w, v + 0.5,
                        f"{v:.0f}", ha="center", fontsize=6)

    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=20, ha="right")
    ax.set_ylabel("TWh/year")
    ax.set_title("Primary Energy by Source — Finland Baseline Scenarios")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(out / "primary_energy.png", dpi=150)
    plt.close()


def plot_cost_sector(cost_dict: dict, out: Path):
    """Stacked bar: C_inv + C_maint by sector for each year."""
    years = list(cost_dict.keys())
    # Collect all sectors
    all_sectors = sorted({s for df in cost_dict.values() for s in df.index},
                         key=lambda s: max(
                             (cost_dict[yr].loc[s, "C_inv"] + cost_dict[yr].loc[s, "C_maint"])
                             for yr in years if s in cost_dict[yr].index
                         ), reverse=True)
    if not all_sectors:
        return

    x = np.arange(len(years))
    w = 0.6

    fig, ax = plt.subplots(figsize=(10, 7))
    import matplotlib
    colormap = matplotlib.colormaps.get_cmap("tab10").resampled(len(all_sectors))

    bottoms = np.zeros(len(years))
    for k, sector in enumerate(all_sectors):
        cinv_vals = []
        for yr in years:
            df = cost_dict[yr]
            if sector in df.index:
                cinv_vals.append(df.loc[sector, "C_inv"] + df.loc[sector, "C_maint"])
            else:
                cinv_vals.append(0.0)
        ax.bar(x, cinv_vals, w, bottom=bottoms,
               label=sector, color=colormap(k), edgecolor="white", alpha=0.85)
        bottoms += np.array(cinv_vals)

    # Total cost annotation
    for i, yr in enumerate(years):
        ax.text(i, bottoms[i] + 50, f"{bottoms[i]:.0f} M€", ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylabel("Cost (M€/year)")
    ax.set_title("System Cost (C_inv + C_maint) by Sector — Finland Scenarios")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "cost_breakdown.png", dpi=150)
    plt.close()


def plot_gwp(gwp_dict: dict, obj_dict: dict, out: Path):
    """GWP components + direct CO2 bar chart."""
    years = list(gwp_dict.keys())
    x = np.arange(len(years))
    w = 0.5

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    # Left: stacked GWP components
    ax = axes[0]
    components = ["GWP_constr", "GWP_op", "CO2_net"]
    labels_map = {"GWP_constr": "Construction GWP", "GWP_op": "Operation GWP", "CO2_net": "Direct CO2"}
    colours_map = {"GWP_constr": "#8e44ad", "GWP_op": "#d7bde2", "CO2_net": "#c0392b"}
    bottoms = np.zeros(len(years))
    for comp in components:
        vals = [gwp_dict[yr].get(comp, 0.0) / 1000 for yr in years]  # ktCO2 → MtCO2
        ax.bar(x, vals, w, bottom=bottoms, label=labels_map[comp],
               color=colours_map[comp], edgecolor="white", alpha=0.85)
        bottoms += np.array(vals)
    for i in range(len(years)):
        ax.text(i, bottoms[i] + 0.2, f"{bottoms[i]:.1f}", ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(years)
    ax.set_ylabel("MtCO2-eq/year")
    ax.set_title("GWP Breakdown (lifecycle + direct)")
    ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)

    # Right: direct CO2 relative to GWP limit
    ax = axes[1]
    gwp_limits = {"2035": 21.0, "2050": 3.0}  # MtCO2 (21000 and 3000 ktCO2)
    co2_vals = [gwp_dict[yr].get("CO2_net", 0.0) / 1000 for yr in years]
    limit_vals = [gwp_limits.get(yr, float("nan")) for yr in years]
    bars = ax.bar(x - 0.2, co2_vals, 0.35, label="Model CO2_net", color="#c0392b", edgecolor="white")
    ax.bar(x + 0.2, limit_vals, 0.35, label="GWP limit", color="#e8daef", edgecolor="#8e44ad", hatch="//")
    for b in bars:
        if b.get_height() > 0.1:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.1,
                    f"{b.get_height():.1f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(years)
    ax.set_ylabel("MtCO2/year")
    ax.set_title("Direct CO2 vs Constraint Limit")
    ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    plt.suptitle("GWP & Emissions — Finland Baseline Scenarios", fontsize=12)
    plt.tight_layout()
    plt.savefig(out / "gwp_breakdown.png", dpi=150)
    plt.close()


# ============================================================================
# SUMMARY REPORT
# ============================================================================

def write_summary_report(run_dirs: dict, out: Path, extracted: dict):
    lines = []
    lines.append("# Finland Future Scenarios — Analysis Summary")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("\nRuns analysed:")
    for yr, rd in run_dirs.items():
        lines.append(f"- **{yr}**: `{rd.name}`")

    for yr, rd in run_dirs.items():
        d = extracted.get(yr, {})
        lines.append(f"\n---\n## {yr} Results\n")
        obj = d.get("objective", float("nan"))
        lines.append(f"**Total system cost:** {obj:,.0f} M€/year")

        gwp = d.get("gwp", {})
        co2 = gwp.get("CO2_net", 0.0)
        gwp_lc = sum(gwp.get(k, 0) for k in ["GWP_constr", "GWP_op", "CO2_net"])
        lines.append(f"\n**Direct CO2:** {co2/1000:.1f} MtCO2/year")
        lines.append(f"**Lifecycle GWP:** {gwp_lc/1000:.1f} MtCO2-eq/year")

        elec = d.get("electricity", {})
        if elec:
            lines.append(f"\n### Electricity (TWh/year)")
            lines.append("| Source | TWh |")
            lines.append("|--------|-----|")
            for k, v in sorted(elec.items(), key=lambda x: -x[1]):
                if v > 0.05:
                    lines.append(f"| {k} | {v:.1f} |")
            lines.append(f"| **TOTAL** | **{sum(elec.values()):.1f}** |")

        pe = d.get("primary_energy", {})
        if pe:
            lines.append(f"\n### Primary Energy (TWh/year)")
            lines.append("| Source | TWh |")
            lines.append("|--------|-----|")
            for k, v in sorted(pe.items(), key=lambda x: -x[1]):
                if v > 0.5:
                    lines.append(f"| {k} | {v:.1f} |")

    (out / "summary_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  Summary report -> {out / 'summary_report.md'}")


# ============================================================================
# SANKEY
# ============================================================================

def run_sankey(space_id: str, case_study: str, label: str, auto_open: bool = False):
    """Generate Sankey CSV for one run and render HTML."""
    try:
        from esmc.postprocessing.draw_sankey.output_to_sankey_csv import write_sankey_file
        from esmc.postprocessing.draw_sankey.ESSankey import drawSankey
        from pathlib import Path as _P

        print(f"  Sankey [{label}]: writing input2sankey CSV...")
        write_sankey_file(space_id, case_study)

        proj_dir = REPO_ROOT
        output_dir = proj_dir / "case_studies" / space_id / case_study / "outputs"

        # Draw sankey for Total (and any individual cells if multi-cell)
        import glob
        pattern = str(output_dir / "input2sankey_*.csv")
        csv_files = glob.glob(pattern)
        if not csv_files:
            print(f"  WARNING: no input2sankey_*.csv found in {output_dir}")
            return

        for csv_path in sorted(csv_files):
            csv_name = Path(csv_path).name
            cell_name = csv_name.replace("input2sankey_", "").replace(".csv", "")
            html_name = f"generated_sankey_{cell_name}.html"
            print(f"    Rendering {html_name}...")
            drawSankey(
                path=str(output_dir),
                outputfile=html_name,
                I2S_File=csv_name,
                auto_open=auto_open,
            )
            print(f"    -> {output_dir / html_name}")

    except ImportError as e:
        print(f"  Sankey [{label}]: import error — {e}")
    except Exception as e:
        print(f"  Sankey [{label}]: FAILED — {e}")
        import traceback; traceback.print_exc()


# ============================================================================
# AUTO-DETECT LATEST RUNS
# ============================================================================

def find_latest_run(year_tag: str) -> Path:
    """Find the most recent successful run directory for a given year tag."""
    candidates = sorted(
        [d for d in MANUAL_RUNS.iterdir()
         if d.is_dir() and year_tag in d.name and (d / "outputs" / "Year_balance.csv").exists()],
        reverse=True,
    )
    return candidates[0] if candidates else None


# ============================================================================
# MAIN
# ============================================================================

def parse_args():
    p = argparse.ArgumentParser(description="Postprocess Finland future scenario runs")
    p.add_argument("--run-2035", default=None,
                   help="Path to 2035 run directory")
    p.add_argument("--run-2050", default=None,
                   help="Path to 2050 run directory")
    p.add_argument("--run-2017", default=None,
                   help="Path to 2017 run directory (for Sankey only)")
    p.add_argument("--auto", action="store_true",
                   help="Auto-detect latest 2035 and 2050 run directories")
    p.add_argument("--sankey", action="store_true", default=True,
                   help="Generate Sankey diagrams (default: True)")
    p.add_argument("--skip-sankey", action="store_true",
                   help="Skip Sankey generation")
    p.add_argument("--open-browser", action="store_true",
                   help="Auto-open Sankey HTML in browser after generation")
    return p.parse_args()


def main():
    args = parse_args()
    do_sankey = args.sankey and not args.skip_sankey

    # ---- Resolve run directories ----
    run_dirs: dict[str, Path] = {}

    if args.auto or (args.run_2035 is None and args.run_2050 is None):
        r35 = find_latest_run("2035")
        r50 = find_latest_run("2050")
        if r35:
            run_dirs["2035"] = r35
            print(f"  Auto-detected 2035: {r35.name}")
        if r50:
            run_dirs["2050"] = r50
            print(f"  Auto-detected 2050: {r50.name}")
    else:
        if args.run_2035:
            p = Path(args.run_2035)
            if not p.is_absolute():
                p = REPO_ROOT / p
            run_dirs["2035"] = p
        if args.run_2050:
            p = Path(args.run_2050)
            if not p.is_absolute():
                p = REPO_ROOT / p
            run_dirs["2050"] = p

    # 2017 dir for Sankey
    run_2017_dir = None
    if args.run_2017:
        p = Path(args.run_2017)
        if not p.is_absolute():
            p = REPO_ROOT / p
        run_2017_dir = p
    else:
        # Default to final 2017 baseline (v37_solar, archived)
        default_2017 = REPO_ROOT / "case_studies" / "FI" / "_archive_2017calib" / "20260323_173930__v37_solar"
        if default_2017.exists() and (default_2017 / "outputs" / "Year_balance.csv").exists():
            run_2017_dir = default_2017
            print(f"  Auto-detected 2017: {run_2017_dir.name}")

    if not run_dirs:
        print("ERROR: No run directories found. Use --auto or specify --run-2035 / --run-2050.")
        sys.exit(1)

    # ---- Load data & produce plots per run ----
    extracted: dict = {}
    cap_dict: dict = {}
    elec_dict: dict = {}
    heat_dict: dict = {}
    pe_dict: dict = {}
    cost_dict: dict = {}
    gwp_dict: dict = {}
    obj_dict: dict = {}

    for yr, run_dir in run_dirs.items():
        print(f"\n{'='*60}")
        print(f"  Processing {yr}: {run_dir.name}")
        print(f"{'='*60}")

        outputs = run_dir / "outputs"
        if not outputs.exists():
            print(f"  ERROR: outputs/ not found in {run_dir}")
            continue

        # Load
        assets = load_assets(outputs)
        yb = load_year_balance(outputs)
        res = load_resources(outputs)
        cost = load_cost(outputs)
        gwp = load_gwp(outputs)
        obj = load_objective(outputs)

        # Extract
        cap = extract_capacity(assets)
        elec = extract_electricity(yb)
        heat = extract_heat(yb)
        pe = extract_primary_energy(res)
        cost_s = extract_cost_by_sector(cost)
        gwp_t = extract_gwp_totals(gwp)

        cap_dict[yr] = cap
        elec_dict[yr] = elec
        heat_dict[yr] = heat
        pe_dict[yr] = pe
        if not cost_s.empty:
            cost_dict[yr] = cost_s
        gwp_dict[yr] = gwp_t
        obj_dict[yr] = obj

        extracted[yr] = {
            "objective": obj,
            "electricity": elec,
            "heat": heat,
            "primary_energy": pe,
            "gwp": gwp_t,
        }

        # Per-run validation_plots dir
        vp = run_dir / "validation_plots"
        vp.mkdir(exist_ok=True)
        print(f"  Plots -> {vp}")

        # Per-run individual plots
        if not cap.empty:
            fig_cap, ax_cap = plt.subplots(figsize=(13, 6))
            vals = cap.values
            labels = cap.index.tolist()
            color = COLOURS.get(yr, "#3498db")
            bars = ax_cap.barh(labels, vals, color=color, edgecolor="white", alpha=0.85)
            for b in bars:
                w = b.get_width()
                if w > 0.05:
                    ax_cap.text(w + 0.02, b.get_y() + b.get_height() / 2,
                                f"{w:.2f} GW", va="center", fontsize=7)
            ax_cap.set_xlabel("Installed capacity (GW)")
            ax_cap.set_title(f"Installed Capacity — Finland {yr}")
            ax_cap.invert_yaxis()
            ax_cap.grid(axis="x", alpha=0.3)
            plt.tight_layout()
            plt.savefig(vp / "capacity_installed.png", dpi=150)
            plt.close()
            print(f"    capacity_installed.png")

        # Electricity mix (single year)
        if elec:
            fig_e, ax_e = plt.subplots(figsize=(10, 5))
            s_elec = sorted(elec.items(), key=lambda x: -x[1])
            names = [k for k, v in s_elec if v > 0.05]
            vals = [v for k, v in s_elec if v > 0.05]
            color = COLOURS.get(yr, "#3498db")
            bars = ax_e.bar(names, vals, color=color, edgecolor="white", alpha=0.85)
            for b in bars:
                if b.get_height() > 0.5:
                    ax_e.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                              f"{b.get_height():.1f}", ha="center", fontsize=8)
            ax_e.set_ylabel("TWh/year")
            ax_e.set_title(f"Electricity Mix — Finland {yr}  (total: {sum(vals):.1f} TWh)")
            ax_e.set_xticks(range(len(names)))
            ax_e.set_xticklabels(names, rotation=15, ha="right")
            ax_e.grid(axis="y", alpha=0.3); ax_e.set_ylim(bottom=0)
            plt.tight_layout()
            plt.savefig(vp / "electricity_mix.png", dpi=150)
            plt.close()
            print(f"    electricity_mix.png")

        # Primary energy (single year)
        if pe:
            fig_pe, ax_pe = plt.subplots(figsize=(10, 5))
            s_pe = sorted(pe.items(), key=lambda x: -x[1])
            names = [k for k, v in s_pe if v > 0.5]
            vals = [v for k, v in s_pe if v > 0.5]
            color = COLOURS.get(yr, "#3498db")
            bars = ax_pe.bar(names, vals, color=color, edgecolor="white", alpha=0.85)
            for b in bars:
                if b.get_height() > 1:
                    ax_pe.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                               f"{b.get_height():.0f}", ha="center", fontsize=8)
            ax_pe.set_ylabel("TWh/year")
            ax_pe.set_title(f"Primary Energy — Finland {yr}  (total: {sum(vals):.0f} TWh)")
            ax_pe.set_xticks(range(len(names)))
            ax_pe.set_xticklabels(names, rotation=20, ha="right")
            ax_pe.grid(axis="y", alpha=0.3); ax_pe.set_ylim(bottom=0)
            plt.tight_layout()
            plt.savefig(vp / "primary_energy.png", dpi=150)
            plt.close()
            print(f"    primary_energy.png")

        # GWP (single year)
        if gwp_t:
            fig_g, ax_g = plt.subplots(figsize=(7, 5))
            comp = {k: v / 1000 for k, v in gwp_t.items()}
            name_map = {"GWP_constr": "Construction\nGWP", "GWP_op": "Operation\nGWP", "CO2_net": "Direct\nCO2"}
            names = [name_map.get(k, k) for k in comp]
            vals = list(comp.values())
            bar_c = ["#8e44ad", "#d7bde2", "#c0392b"]
            bars = ax_g.bar(names, vals, color=bar_c[:len(names)], edgecolor="white")
            for b in bars:
                ax_g.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.2,
                          f"{b.get_height():.1f}", ha="center", fontsize=9, fontweight="bold")
            lim = {"2035": 21.0, "2050": 3.0}.get(yr)
            if lim is not None:
                ax_g.axhline(lim, color="red", ls="--", lw=1.5,
                             label=f"CO2 constraint: {lim:.0f} MtCO2")
                ax_g.legend(fontsize=8)
            ax_g.set_ylabel("MtCO2-eq/year")
            ax_g.set_title(f"GWP Breakdown — Finland {yr}")
            ax_g.grid(axis="y", alpha=0.3); ax_g.set_ylim(bottom=0)
            plt.tight_layout()
            plt.savefig(vp / "gwp_breakdown.png", dpi=150)
            plt.close()
            print(f"    gwp_breakdown.png")

        # Cost breakdown (single year)
        if not cost_s.empty:
            fig_c, ax_c = plt.subplots(figsize=(10, 6))
            import matplotlib
            cmap = matplotlib.colormaps.get_cmap("tab10").resampled(len(cost_s))
            bottoms = 0.0
            for k_idx, sector in enumerate(cost_s.index):
                cinv = cost_s.loc[sector, "C_inv"]
                cmaint = cost_s.loc[sector, "C_maint"]
                total = cinv + cmaint
                ax_c.bar(0, cinv, 0.5, bottom=bottoms, color=cmap(k_idx), alpha=0.9,
                         label=f"{sector} ({total:.0f} M€)")
                ax_c.bar(0, cmaint, 0.5, bottom=bottoms + cinv,
                         color=cmap(k_idx), alpha=0.55, hatch="//")
                bottoms += total
            solid = mpatches.Patch(color="grey", alpha=0.9, label="C_inv (solid)")
            hatch = mpatches.Patch(color="grey", alpha=0.55, hatch="//", label="C_maint (hatched)")
            handles, labels = ax_c.get_legend_handles_labels()
            ax_c.legend(handles=handles + [solid, hatch], fontsize=8, loc="upper right")
            ax_c.set_xlim(-0.5, 0.5)
            ax_c.set_xticks([0]); ax_c.set_xticklabels([yr])
            ax_c.set_ylabel("M€/year")
            ax_c.set_title(f"System Cost Breakdown — Finland {yr}  ({obj:,.0f} M€ total)")
            ax_c.grid(axis="y", alpha=0.3)
            plt.tight_layout()
            plt.savefig(vp / "cost_breakdown.png", dpi=150)
            plt.close()
            print(f"    cost_breakdown.png")

    # ---- Cross-year comparison plots (only if both years present) ----
    if len(run_dirs) >= 2:
        # One shared output dir for comparison — use manual_runs/
        comp_out = MANUAL_RUNS / "comparison_plots"
        comp_out.mkdir(exist_ok=True)
        print(f"\n  Comparison plots -> {comp_out}")

        plot_capacity(cap_dict, comp_out)
        print("    capacity_comparison.png")
        plot_electricity(elec_dict, comp_out)
        print("    electricity_mix.png")
        plot_heat(heat_dict, comp_out)
        print("    heat_supply.png")
        plot_primary_energy(pe_dict, comp_out)
        print("    primary_energy.png")
        if cost_dict:
            plot_cost_sector(cost_dict, comp_out)
            print("    cost_breakdown.png")
        if gwp_dict:
            plot_gwp(gwp_dict, obj_dict, comp_out)
            print("    gwp_breakdown.png")

        write_summary_report(run_dirs, comp_out, extracted)

    # ---- Sankey ----
    if do_sankey:
        print(f"\n{'='*60}")
        print("  SANKEY DIAGRAMS")
        print(f"{'='*60}")

        for yr, run_dir in run_dirs.items():
            # Determine space_id and case_study relative to case_studies/FI/
            cs_fi = REPO_ROOT / "case_studies" / "FI"
            rel = run_dir.relative_to(cs_fi)
            case_study_str = str(rel).replace("\\", "/")
            print(f"\n  [{yr}] space_id=FI  case_study={case_study_str}")
            run_sankey("FI", case_study_str, yr, auto_open=args.open_browser)

        if run_2017_dir is not None:
            cs_fi = REPO_ROOT / "case_studies" / "FI"
            try:
                rel = run_2017_dir.relative_to(cs_fi)
                case_study_str = str(rel).replace("\\", "/")
                print(f"\n  [2017] space_id=FI  case_study={case_study_str}")
                run_sankey("FI", case_study_str, "2017", auto_open=args.open_browser)
            except ValueError:
                print(f"  [2017] Run dir is outside case_studies/FI — skipping Sankey")

    print(f"\n{'='*60}")
    print("  POSTPROCESSING COMPLETE")
    print(f"{'='*60}")
    for yr, run_dir in run_dirs.items():
        print(f"  [{yr}] validation_plots/ -> {run_dir / 'validation_plots'}")
    if len(run_dirs) >= 2:
        print(f"  Comparison -> {MANUAL_RUNS / 'comparison_plots'}")


if __name__ == "__main__":
    main()
