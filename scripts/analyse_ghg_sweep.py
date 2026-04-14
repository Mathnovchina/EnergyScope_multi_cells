#!/usr/bin/env python3
"""
==========================================================================
  analyse_ghg_sweep.py  —  Post-process Finland 2035 GHG parametric sweep
==========================================================================

Reads all sweep run directories, extracts key metrics, builds comparison
tables and Colla-style plots:

  Plot 1 (≈ Colla Figure 3): Primary energy by fuel, stacked bars
         across GHG-savings cases, with system cost annotation.
  Plot 2 (≈ Colla Figure 4): Biomass allocation by final use, stacked
         bars across GHG-savings cases.
  Plot 3: System cost vs GHG savings (curve).
  Plot 4: Actual CO2 vs GHG limit per case.

Also exports a master CSV with all metrics for external analysis.

Usage:
  # Auto-detect sweep runs
  python scripts/analyse_ghg_sweep.py

  # Explicit manifest
  python scripts/analyse_ghg_sweep.py --manifest case_studies/FI/manual_runs/ghg_sweep_2035_manifest.json

  # Include the existing national_plan_2035 run as the ≈50 % reference
  python scripts/analyse_ghg_sweep.py --include-existing
"""

import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
MANUAL_RUNS = REPO_ROOT / "case_studies" / "FI" / "manual_runs"
GHG_BASELINE_2017 = 41_200  # ktCO2/y

# ============================================================================
# COLOUR PALETTES
# ============================================================================

PE_COLOURS = {
    "Nuclear":      "#f4d44d",
    "Wind":         "#7fbfdf",
    "Hydro":        "#1f77b4",
    "Solar":        "#ff9f0e",
    "Biomass":      "#8B6914",
    "Waste":        "#8c564b",
    "Gas":          "#BDB76B",
    "Oil products": "#a0a0a0",
    "Coal":         "#333333",
    "H2 / e-fuels": "#9467bd",
    "Elec import":  "#bcbd22",
}

# NED feedstock colours — hatched overlay on top of bars (Colla style)
NED_COLOURS = {
    "LFO for NED":      "#7f7f7f",
    "Gas for NED":       "#BDB76B",
    "Biomass for NED":   "#8B6914",
    "Waste for NED":     "#8c564b",
}

ELEC_MIX_COLOURS = {
    "Nuclear":                              "#f4d44d",
    "Wind onshore":                         "#7fbfdf",
    "Wind offshore":                        "#1a72b5",
    "Solar PV":                             "#ff9f0e",
    "Hydro":                                "#1f77b4",
    "Gas turbines":                         "#BDB76B",
    "Gas CHP":                              "#8B8A00",
    "Biomass CHP/power":                    "#8B6914",
    "Biomass (conversion co-product)":      "#c49a3c",
    "Electricity import":                   "#bcbd22",
    "Other":                                "#7f7f7f",
}

# Maps technology names → electricity generation category
ELEC_TECH_MAP = {
    "NUCLEAR":                  "Nuclear",
    "WIND_ONSHORE":             "Wind onshore",
    "WIND_OFFSHORE":            "Wind offshore",
    "PV_ROOFTOP":               "Solar PV",
    "PV_UTILITY":               "Solar PV",
    "HYDRO_RIVER":              "Hydro",
    "HYDRO_DAM":                "Hydro",
    "CCGT":                     "Gas turbines",
    "OCGT":                     "Gas turbines",
    "IND_COGEN_GAS":            "Gas CHP",
    "DHN_COGEN_GAS":            "Gas CHP",
    "DEC_COGEN_GAS":            "Gas CHP",
    "DEC_ADVCOGEN_GAS":         "Gas CHP",
    "IND_COGEN_WOOD":           "Biomass CHP/power",
    "DHN_COGEN_WOOD":           "Biomass CHP/power",
    "DHN_COGEN_WASTE":          "Biomass CHP/power",
    "IND_COGEN_WASTE":          "Biomass CHP/power",
    "BIOMASS_TO_POWER":         "Biomass CHP/power",
    "BIOMASS_TO_DIESEL":        "Biomass (conversion co-product)",
    "BIOMASS_TO_JET_FUEL":      "Biomass (conversion co-product)",
    "BIOMASS_TO_METHANOL":      "Biomass (conversion co-product)",
    "BIOMASS_TO_GASOLINE":      "Biomass (conversion co-product)",
    "BIOMASS_TO_LFO":           "Biomass (conversion co-product)",
    "BIOMASS_TO_METHANE":       "Biomass (conversion co-product)",
    "BIOWASTE_TO_DIESEL":       "Biomass (conversion co-product)",
    "BIOWASTE_TO_JET_FUEL":     "Biomass (conversion co-product)",
}

BIOMASS_USE_COLOURS = {
    "HT heat -- boilers (wood)":   "#1f4e79",
    "HT heat -- boilers (waste)":  "#5b9bd5",
    "HT heat -- CHP":              "#ff9f0e",
    "LT heat DHN -- boilers":      "#2ca02c",
    "LT heat DHN -- CHP":          "#98df8a",
    "LT heat decentralised":       "#aec7e8",
    "Electricity":                  "#9467bd",
    "NED / chemicals":              "#d4d4d4",
    "Mobility fuels":               "#e377c2",
    "Biogas / biomethanation":      "#bcbd22",
    "Other":                        "#7f7f7f",
}

BIOMASS_USE_HATCHES = {
    "HT heat -- boilers (wood)":   "",
    "HT heat -- boilers (waste)":  "//",
    "HT heat -- CHP":              "",
    "LT heat DHN -- boilers":      "",
    "LT heat DHN -- CHP":          "\\\\",
    "LT heat decentralised":       "...",
    "Electricity":                  "xx",
    "NED / chemicals":              "///",
    "Mobility fuels":               "",
    "Biogas / biomethanation":      "",
    "Other":                        "",
}


# ============================================================================
# DATA LOADING (mirrors postprocess_future.py but keeps it self-contained)
# ============================================================================

def load_csv(outputs: Path, name: str) -> pd.DataFrame:
    p = outputs / name
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, index_col=0)


def load_objective(outputs: Path) -> float:
    for name in ["TotalCost.csv", "Objective.csv"]:
        p = outputs / name
        if p.exists():
            df = pd.read_csv(p, index_col=0)
            return float(df.iloc[0, 0])
    return float("nan")


# ============================================================================
# EXTRACTION FUNCTIONS
# ============================================================================

def extract_primary_energy(res: pd.DataFrame) -> dict:
    """Primary energy by resource group (TWh). Extended with coal + elec imports."""
    if res.empty:
        return {}

    def _sum(resources):
        s = 0.0
        for r in resources:
            if r in res.index:
                row = res.loc[r]
                s += float(row.get("R_year_local", 0)) + float(row.get("R_year_exterior", 0))
        return s / 1000  # GWh → TWh

    return {
        "Biomass":      _sum(["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"]),
        "Waste":        _sum(["WASTE"]),
        "Nuclear":      _sum(["URANIUM"]),
        "Wind":         _sum(["RES_WIND"]),
        "Hydro":        _sum(["RES_HYDRO"]),
        "Solar":        _sum(["RES_SOLAR"]),
        "Gas":          _sum(["GAS", "GAS_RE"]),
        "Oil products": _sum(["GASOLINE", "DIESEL", "LFO", "JET_FUEL",
                               "GASOLINE_RE", "DIESEL_RE", "LFO_RE", "JET_FUEL_RE"]),
        "Coal":         _sum(["COAL"]),
        "H2 / e-fuels": _sum(["H2", "H2_RE", "AMMONIA", "AMMONIA_RE", "METHANOL", "METHANOL_RE"]),
        "Elec import":  _sum(["ELECTRICITY"]),
    }


def extract_gwp_totals(gwp: pd.DataFrame) -> dict:
    if gwp.empty:
        return {}
    result = {}
    for col in ["GWP_constr", "GWP_op", "CO2_net"]:
        if col in gwp.columns:
            result[col] = float(gwp[col].sum())
    return result


def extract_co2_from_resources(res: pd.DataFrame) -> float:
    """CO2_EMISSIONS from Resources.csv (exterior consumption)."""
    if res.empty:
        return float("nan")
    if "CO2_EMISSIONS" in res.index:
        row = res.loc["CO2_EMISSIONS"]
        return float(row.get("R_year_exterior", 0))
    return float("nan")


# ---- BIOMASS ALLOCATION BY FINAL USE ----

# Maps technology names → final-use category (Colla Figure 4 equivalents)
BIOMASS_TECH_MAP = {
    # HT heat -- boilers (split wood vs waste for visibility)
    "IND_BOILER_WOOD":          "HT heat -- boilers (wood)",
    "IND_BOILER_BIOWASTE":      "HT heat -- boilers (wood)",
    "IND_BOILER_WASTE":         "HT heat -- boilers (waste)",
    # HT heat -- CHP
    "IND_COGEN_WOOD":           "HT heat -- CHP",
    "IND_COGEN_WASTE":          "HT heat -- CHP",
    # LT heat DHN -- boilers
    "DHN_BOILER_WOOD":          "LT heat DHN -- boilers",
    # LT heat DHN -- CHP
    "DHN_COGEN_WOOD":           "LT heat DHN -- CHP",
    "DHN_COGEN_WASTE":          "LT heat DHN -- CHP",
    # LT heat decentralised
    "DEC_BOILER_WOOD":          "LT heat decentralised",
    "DEC_COGEN_WOOD":           "LT heat decentralised",
    "DEC_ADVCOGEN_WOOD":        "LT heat decentralised",
    # Electricity (dedicated biomass power)
    "BIOMASS_TO_POWER":         "Electricity",
    # NED / chemicals
    "BIOMASS_TO_HVC":           "NED / chemicals",
    "BIOMASS_TO_METHANOL":      "NED / chemicals",
    "BIOWASTE_TO_METHANOL":     "NED / chemicals",
    # Mobility fuels (pyrolysis / gasification → liquid or gas fuels)
    "BIOMASS_TO_DIESEL":        "Mobility fuels",
    "BIOMASS_TO_GASOLINE":      "Mobility fuels",
    "BIOMASS_TO_JET_FUEL":      "Mobility fuels",
    "BIOMASS_TO_LFO":           "Mobility fuels",
    "BIOMASS_TO_METHANE":       "Mobility fuels",
    "BIOWASTE_TO_DIESEL":       "Mobility fuels",
    "BIOWASTE_TO_GASOLINE":     "Mobility fuels",
    "BIOWASTE_TO_JET_FUEL":     "Mobility fuels",
    "BIOWASTE_TO_LFO":          "Mobility fuels",
    "BIOWASTE_TO_METHANE":      "Mobility fuels",
    # Biogas / biomethanation
    "BIOMETHANATION_WET_BIOMASS":  "Biogas / biomethanation",
    "BIOMETHANATION_BIOWASTE":     "Biogas / biomethanation",
    # H2 from biomass
    "H2_BIOMASS":               "Other",
}

# Biomass resource columns in Year_balance
BIOMASS_RESOURCE_COLS = ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES",
                         "ENERGY_CROPS_2", "WASTE"]


def extract_biomass_allocation(yb: pd.DataFrame) -> dict:
    """
    Compute biomass allocation by final-use category (GWh).

    For each technology that consumes biomass (negative value in any
    BIOMASS_RESOURCE_COLS column), sum the absolute input and map to
    a final use category via BIOMASS_TECH_MAP.

    Returns: {category: GWh_consumed}
    """
    if yb.empty:
        return {}

    bio_cols = [c for c in BIOMASS_RESOURCE_COLS if c in yb.columns]
    if not bio_cols:
        return {}

    allocation = {}
    unmapped = {}

    for tech in yb.index:
        consumption = 0.0
        for col in bio_cols:
            val = float(yb.loc[tech, col])
            if val < -0.01:
                consumption += abs(val)

        if consumption > 0.01:
            category = BIOMASS_TECH_MAP.get(tech, None)
            if category is None:
                unmapped[tech] = consumption
                category = "Other"
            allocation[category] = allocation.get(category, 0.0) + consumption

    if unmapped:
        print(f"  WARNING: Unmapped biomass consumers: {unmapped}")

    return allocation


# NED / HVC feedstock technologies — maps to NED feedstock category for hatched overlay
NED_TECH_MAP = {
    "OIL_TO_HVC":       "LFO for NED",
    "GAS_TO_HVC":       "Gas for NED",
    "BIOMASS_TO_HVC":   "Biomass for NED",
}

# Resources consumed by NED techs (for primary energy accounting)
NED_INPUT_RESOURCES = {
    "OIL_TO_HVC":       ["LFO", "GASOLINE", "DIESEL"],
    "GAS_TO_HVC":       ["GAS"],
    "BIOMASS_TO_HVC":   ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES"],
}


def extract_ned_feedstock(yb: pd.DataFrame) -> dict:
    """Extract NED feedstock inputs by fuel type (GWh consumed).

    Returns: {"LFO for NED": GWh, "Gas for NED": GWh, "Biomass for NED": GWh}
    """
    if yb.empty:
        return {}
    result = {}
    for tech, label in NED_TECH_MAP.items():
        if tech not in yb.index:
            continue
        # Sum absolute consumption across all input resource columns
        consumption = 0.0
        for res_col in NED_INPUT_RESOURCES.get(tech, []):
            if res_col in yb.columns:
                val = float(yb.loc[tech, res_col])
                if val < -0.01:
                    consumption += abs(val)
        if consumption > 0.01:
            result[label] = result.get(label, 0.0) + consumption
    return result


# Gas consumer technologies for the gas breakdown plot
GAS_CONSUMER_MAP = {
    "DEC_THHP_GAS":           "Decentralised heat (gas HP)",
    "DHN_COGEN_GAS":          "DHN CHP (gas)",
    "DHN_BOILER_GAS":         "DHN boiler (gas)",
    "DEC_COGEN_GAS":          "Dec. CHP (gas)",
    "DEC_ADVCOGEN_GAS":       "Dec. adv. CHP (gas)",
    "IND_COGEN_GAS":          "Industrial CHP (gas)",
    "IND_BOILER_GAS":         "Industrial boiler (gas)",
    "CCGT":                   "CCGT (electricity)",
    "OCGT":                   "OCGT (electricity)",
    "H2_NG":                  "H2 from gas (SMR)",
    "BUS_COACH_CNG_STOICH":   "CNG buses",
    "CARGO_LNG":              "LNG cargo",
    "BOAT_FREIGHT_NG":        "NG freight boats",
    "GAS_TO_HVC":             "Gas to HVC (NED)",
    "GAS_STORAGE":            "Gas storage",
}


def extract_electricity_mix(yb: pd.DataFrame, res: pd.DataFrame) -> dict:
    """
    Compute electricity production by technology category (GWh/y).
    Uses the ELECTRICITY column from Year_balance (positive = producer).
    Also adds electricity imports from Resources.csv.

    Returns: {category: GWh_produced}
    """
    result = {}
    unmapped = {}

    if not yb.empty and "ELECTRICITY" in yb.columns:
        for tech in yb.index:
            val = float(yb.loc[tech, "ELECTRICITY"])
            if val > 0.5:
                cat = ELEC_TECH_MAP.get(tech.strip(), None)
                if cat is None:
                    unmapped[tech] = val
                    cat = "Other"
                result[cat] = result.get(cat, 0.0) + val

    # Electricity imports
    if not res.empty and "ELECTRICITY" in res.index:
        imp = float(res.loc["ELECTRICITY"].get("R_year_exterior", 0))
        if imp > 0.5:
            result["Electricity import"] = result.get("Electricity import", 0.0) + imp

    if unmapped:
        print(f"  WARNING: Unmapped electricity producers: {unmapped}")

    return result


def extract_gas_breakdown(yb: pd.DataFrame) -> dict:
    if yb.empty or "GAS" not in yb.columns:
        return {}
    result = {}
    gas = yb["GAS"]
    # Consumers (negative values)
    for tech in gas.index:
        val = float(gas[tech])
        if val < -0.5:
            label = GAS_CONSUMER_MAP.get(tech.strip(), tech.strip())
            result[label] = result.get(label, 0.0) + abs(val)
    return result


def extract_cost_by_sector(cost: pd.DataFrame) -> dict:
    """Total cost (C_inv + C_maint + C_op) by sector. Returns {sector: M€/y}."""
    if cost.empty:
        return {}
    # Minimal sector map for quick aggregation
    sector_map = _load_sector_map()
    totals = {}
    for tech, row in cost.iterrows():
        sector = sector_map.get(tech, "Other")
        val = float(row.get("C_inv", 0)) + float(row.get("C_maint", 0)) + float(row.get("C_op", 0))
        if abs(val) > 0.01:
            totals[sector] = totals.get(sector, 0.0) + val
    return totals


def _load_sector_map() -> dict:
    """Import SECTOR_MAP from postprocess_future.py if available, else use minimal."""
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from postprocess_future import SECTOR_MAP
        return SECTOR_MAP
    except ImportError:
        return {}


# ============================================================================
# RUN DISCOVERY
# ============================================================================

def find_sweep_runs(manifest_path: Path = None,
                    include_existing: bool = False,
                    suffix: str = "") -> list:
    """
    Find sweep run directories.

    Returns list of dict: {label, savings_pct, gwp_limit, run_dir, outputs_dir}
    """
    runs = []
    sfx = re.escape(suffix)  # literal suffix for regex

    # From manifest
    if manifest_path and manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        for case in manifest.get("cases", []):
            if not case.get("success", False):
                continue
            # Find the run directory by matching label in folder names
            label = case["label"]
            run_dir = _find_run_dir(f"sweep_{label}{suffix}")
            if run_dir:
                runs.append({
                    "label": label,
                    "savings_pct": case.get("savings_pct"),
                    "gwp_limit": case.get("gwp_limit"),
                    "run_dir": run_dir,
                    "outputs_dir": run_dir / "outputs",
                })

    # Auto-discover sweep runs by folder name pattern
    if not runs:
        pat = rf"sweep_(unconstrained|ghg_\d+pct){sfx}$"
        for d in sorted(MANUAL_RUNS.iterdir()):
            if not d.is_dir():
                continue
            m = re.search(pat, d.name)
            if m and (d / "outputs" / "Year_balance.csv").exists():
                tag = m.group(1)
                if tag == "unconstrained":
                    pct = None
                    gwp = None
                else:
                    pct = int(re.search(r"(\d+)", tag).group(1))
                    gwp = round(GHG_BASELINE_2017 * (1 - pct / 100))
                runs.append({
                    "label": tag,
                    "savings_pct": pct,
                    "gwp_limit": gwp,
                    "run_dir": d,
                    "outputs_dir": d / "outputs",
                })

    # Include existing national_plan_2035 run as reference
    if include_existing:
        existing = _find_run_dir("national_plan_2035")
        if existing and (existing / "outputs" / "Year_balance.csv").exists():
            # Check if we already have a ~50% case
            has_50 = any(r["savings_pct"] == 50 for r in runs if r["savings_pct"] is not None)
            label = "national_plan_2035 (~49%)" if not has_50 else "national_plan_2035"
            runs.append({
                "label": label,
                "savings_pct": 49,  # 21000/41200 ≈ 49%
                "gwp_limit": 21000,
                "run_dir": existing,
                "outputs_dir": existing / "outputs",
            })

    # Sort by savings_pct (None = unconstrained first)
    runs.sort(key=lambda r: r["savings_pct"] if r["savings_pct"] is not None else -1)
    return runs


def _find_run_dir(name_fragment: str) -> Path:
    """Find the most recent run directory whose run-name (after '__') equals name_fragment exactly."""
    candidates = sorted(
        [d for d in MANUAL_RUNS.iterdir()
         if d.is_dir() and d.name.endswith(f"__{name_fragment}")
         and (d / "outputs" / "Year_balance.csv").exists()],
        reverse=True,
    )
    return candidates[0] if candidates else None


# ============================================================================
# MASTER TABLE CONSTRUCTION
# ============================================================================

def build_master_table(runs: list) -> pd.DataFrame:
    """
    Extract all metrics from each run and build a master DataFrame.
    """
    rows = []
    all_pe_cats = set()
    all_bio_cats = set()
    all_ned_cats = set()
    all_gas_cats = set()
    all_elec_cats = set()

    for run in runs:
        print(f"  Loading: {run['label']} -- {run['run_dir'].name}")
        outputs = run["outputs_dir"]

        res = load_csv(outputs, "Resources.csv")
        yb = load_csv(outputs, "Year_balance.csv")
        cost = load_csv(outputs, "Cost_breakdown.csv")
        gwp = load_csv(outputs, "Gwp_breakdown.csv")
        obj = load_objective(outputs)

        pe = extract_primary_energy(res)
        bio = extract_biomass_allocation(yb)
        ned = extract_ned_feedstock(yb)
        gas_bk = extract_gas_breakdown(yb)
        elec_mix = extract_electricity_mix(yb, res)
        gwp_t = extract_gwp_totals(gwp)
        co2_res = extract_co2_from_resources(res)

        row = {
            "label": run["label"],
            "savings_pct": run["savings_pct"],
            "gwp_limit": run["gwp_limit"],
            "system_cost_MEur": obj,
            "co2_actual_kt": co2_res,
            "co2_net_kt": gwp_t.get("CO2_net", float("nan")),
            "gwp_constr_kt": gwp_t.get("GWP_constr", float("nan")),
            "gwp_op_kt": gwp_t.get("GWP_op", float("nan")),
        }

        # Primary energy columns
        for cat, val in pe.items():
            row[f"PE_{cat}_TWh"] = val
            all_pe_cats.add(cat)
        row["PE_total_TWh"] = sum(pe.values())

        # Biomass allocation columns
        for cat, val in bio.items():
            row[f"BIO_{cat}_GWh"] = val
            all_bio_cats.add(cat)
        row["BIO_total_GWh"] = sum(bio.values())

        # NED feedstock columns
        for cat, val in ned.items():
            row[f"NED_{cat}_GWh"] = val
            all_ned_cats.add(cat)
        row["NED_total_GWh"] = sum(ned.values())

        # Gas breakdown columns
        for cat, val in gas_bk.items():
            row[f"GAS_{cat}_GWh"] = val
            all_gas_cats.add(cat)

        # Electricity mix columns
        for cat, val in elec_mix.items():
            row[f"ELECMIX_{cat}_GWh"] = val
            all_elec_cats.add(cat)
        row["ELECMIX_total_GWh"] = sum(elec_mix.values())

        rows.append(row)

    df = pd.DataFrame(rows)

    # Fill NaN for missing categories
    for cat in all_pe_cats:
        col = f"PE_{cat}_TWh"
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)
    for cat in all_bio_cats:
        col = f"BIO_{cat}_GWh"
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)
    for cat in all_ned_cats:
        col = f"NED_{cat}_GWh"
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)
    for cat in all_gas_cats:
        col = f"GAS_{cat}_GWh"
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)
    for cat in all_elec_cats:
        col = f"ELECMIX_{cat}_GWh"
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)

    return df


# ============================================================================
# PLOTTING
# ============================================================================

def _case_labels(df: pd.DataFrame) -> list:
    """Build readable x-axis labels."""
    labels = []
    for _, row in df.iterrows():
        if row["savings_pct"] is None or pd.isna(row.get("savings_pct", None)):
            labels.append("Uncon-\nstrained")
        else:
            labels.append(f"{int(row['savings_pct'])}%")
    return labels


def plot_primary_energy_sweep(df: pd.DataFrame, out: Path):
    """
    Colla Figure 3 analogue: Stacked primary energy by fuel (GWh/year),
    with system cost as dash markers on right Y-axis, and NED feedstock
    shown as hatched overlay on top.
    """
    pe_cats = ["Coal", "Oil products", "Gas", "Elec import",
               "Nuclear", "Hydro", "Wind", "Solar",
               "Biomass", "Waste", "H2 / e-fuels"]
    active_cats = [c for c in pe_cats if df.get(f"PE_{c}_TWh", pd.Series([0])).sum() > 0.1]

    ned_cats = ["LFO for NED", "Gas for NED", "Biomass for NED", "Waste for NED"]
    active_ned = [c for c in ned_cats if df.get(f"NED_{c}_GWh", pd.Series([0])).sum() > 0.1]

    x = np.arange(len(df))
    labels = _case_labels(df)
    bar_width = 0.7

    fig, ax1 = plt.subplots(figsize=(15, 8))

    # --- Stacked bars: primary energy (GWh/year) ---
    bottoms = np.zeros(len(df))
    for cat in active_cats:
        col = f"PE_{cat}_TWh"
        vals = (df[col].values if col in df.columns else np.zeros(len(df))) * 1000  # TWh -> GWh
        color = PE_COLOURS.get(cat, "#cccccc")
        ax1.bar(x, vals, bottom=bottoms, label=cat, color=color,
                edgecolor="white", linewidth=0.5, width=bar_width)
        bottoms += vals

    # --- NED feedstock hatched overlay on top ---
    ned_bottom = bottoms.copy()
    for cat in active_ned:
        col = f"NED_{cat}_GWh"
        vals = df[col].values if col in df.columns else np.zeros(len(df))
        color = NED_COLOURS.get(cat, "#bbbbbb")
        ax1.bar(x, vals, bottom=ned_bottom, label=cat,
                color=color, edgecolor="black", linewidth=0.5,
                hatch="///", alpha=0.7, width=bar_width)
        ned_bottom += vals

    # --- Right Y-axis: system cost (M euro/year) as dash markers ---
    ax2 = ax1.twinx()
    costs_MEur = df["system_cost_MEur"].values
    ax2.plot(x, costs_MEur, "s-", color="#1f4e79", markersize=8,
             linewidth=1.5, markerfacecolor="#1f4e79", markeredgecolor="#1f4e79",
             label="Costs (right axis)", zorder=10)
    ax2.set_ylabel("System yearly costs (M€/year)", fontsize=11, color="#1f4e79")
    ax2.tick_params(axis="y", labelcolor="#1f4e79")
    # Scale right axis to be comparable to Colla layout
    cost_min = costs_MEur[~np.isnan(costs_MEur)].min() if len(costs_MEur) > 0 else 0
    cost_max = costs_MEur[~np.isnan(costs_MEur)].max() if len(costs_MEur) > 0 else 1
    cost_margin = (cost_max - cost_min) * 0.3 if cost_max > cost_min else 500
    ax2.set_ylim(cost_min - cost_margin * 5, cost_max + cost_margin)

    # --- Formatting ---
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_xlabel("GHG savings vs 2017 baseline (41.2 MtCO$_2$)", fontsize=11)
    ax1.set_ylabel("Primary energy (GWh/year)", fontsize=11)
    ax1.set_title("Finland 2035 -- Primary Energy by Source vs GHG Savings\n"
                  "(inspired by Colla et al. 2022, Fig. 3)", fontsize=13)
    ax1.set_ylim(bottom=0)
    ax1.grid(axis="y", alpha=0.2)

    # Combined legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8, ncol=2,
               framealpha=0.9)

    plt.tight_layout()
    fname = out / "fig3_primary_energy_vs_ghg.png"
    plt.savefig(fname, dpi=200)
    plt.close()
    print(f"  -> {fname}")


def plot_biomass_allocation_sweep(df: pd.DataFrame, out: Path):
    """
    Colla Figure 4 analogue: Stacked biomass allocation by final use,
    with hatching patterns to distinguish sub-categories and total
    annotated above each bar.
    """
    bio_cats = ["HT heat -- boilers (wood)", "HT heat -- boilers (waste)",
                "HT heat -- CHP",
                "LT heat DHN -- boilers", "LT heat DHN -- CHP",
                "LT heat decentralised", "Electricity",
                "NED / chemicals", "Mobility fuels",
                "Biogas / biomethanation", "Other"]
    active_cats = [c for c in bio_cats if df.get(f"BIO_{c}_GWh", pd.Series([0])).sum() > 0.1]

    x = np.arange(len(df))
    labels = _case_labels(df)
    bar_width = 0.7

    fig, ax = plt.subplots(figsize=(15, 8))
    bottoms = np.zeros(len(df))

    for cat in active_cats:
        col = f"BIO_{cat}_GWh"
        vals = df[col].values if col in df.columns else np.zeros(len(df))
        color = BIOMASS_USE_COLOURS.get(cat, "#cccccc")
        hatch = BIOMASS_USE_HATCHES.get(cat, "")
        ax.bar(x, vals, bottom=bottoms, label=cat, color=color,
               edgecolor="white", linewidth=0.5, width=bar_width,
               hatch=hatch)
        bottoms += vals

    # Annotate total biomass (GWh)
    for i in range(len(df)):
        if bottoms[i] > 100:
            ax.text(i, bottoms[i] + bottoms.max() * 0.01,
                    f"{bottoms[i]/1000:.1f} TWh",
                    ha="center", va="bottom", fontsize=7, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_xlabel("GHG savings vs 2017 baseline (41.2 MtCO$_2$)", fontsize=11)
    ax.set_ylabel("Biomass used (GWh/year)", fontsize=11)
    ax.set_title("Finland 2035 -- Biomass Allocation by Final Use vs GHG Savings\n"
                 "(inspired by Colla et al. 2022, Fig. 4)", fontsize=13)
    ax.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.9)
    ax.grid(axis="y", alpha=0.2)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    fname = out / "fig4_biomass_allocation_vs_ghg.png"
    plt.savefig(fname, dpi=200)
    plt.close()
    print(f"  -> {fname}")


def plot_cost_vs_ghg(df: pd.DataFrame, out: Path):
    """System cost (bn€/y) vs GHG savings."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Prepare x-values
    x_vals = []
    costs = []
    for _, row in df.iterrows():
        pct = row.get("savings_pct")
        if pct is None or pd.isna(pct):
            # For unconstrained, use actual savings from model result
            co2 = row.get("co2_actual_kt", float("nan"))
            if not np.isnan(co2):
                actual_pct = (1 - co2 / GHG_BASELINE_2017) * 100
                x_vals.append(actual_pct)
            else:
                x_vals.append(0)
        else:
            x_vals.append(pct)
        costs.append(row.get("system_cost_MEur", float("nan")) / 1000)

    ax.plot(x_vals, costs, "o-", color="#2c3e50", linewidth=2, markersize=8)
    for xv, c in zip(x_vals, costs):
        if not np.isnan(c):
            ax.annotate(f"{c:.1f}", (xv, c), textcoords="offset points",
                        xytext=(0, 10), ha="center", fontsize=8)

    ax.set_xlabel("GHG savings vs 2017 (%)")
    ax.set_ylabel("System cost (bn€/year)")
    ax.set_title("Finland 2035 — System Cost vs GHG Savings")
    ax.grid(alpha=0.3)
    ax.set_xlim(-5, 100)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    fname = out / "cost_vs_ghg_savings.png"
    plt.savefig(fname, dpi=200)
    plt.close()
    print(f"  -> {fname}")


def plot_co2_actual_vs_limit(df: pd.DataFrame, out: Path):
    """Actual CO₂ net vs GWP constraint limit per case."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(df))
    labels = _case_labels(df)
    w = 0.35

    # Use co2_net_kt (the metric used in the AMPL GWP constraint)
    actual = df["co2_net_kt"].values / 1000  # → MtCO2
    limits = []
    for _, row in df.iterrows():
        gwp = row.get("gwp_limit")
        if gwp is None or pd.isna(gwp):
            limits.append(float("nan"))
        else:
            limits.append(gwp / 1000)
    limits = np.array(limits)

    ax.bar(x - w/2, actual, w, label="Model CO₂ net", color="#c0392b",
           edgecolor="white", alpha=0.85)
    valid_lim = ~np.isnan(limits)
    if valid_lim.any():
        ax.bar(x[valid_lim] + w/2, limits[valid_lim], w,
               label="GWP constraint", color="#e8daef",
               edgecolor="#8e44ad", hatch="//", alpha=0.85)

    for i in range(len(df)):
        if not np.isnan(actual[i]):
            ax.text(i - w/2, actual[i] + 0.3, f"{actual[i]:.1f}",
                    ha="center", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_xlabel("GHG savings case")
    ax.set_ylabel("MtCO₂/year (net)")
    ax.set_title("Finland 2035 — Net CO₂ Emissions vs GWP Constraint")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    fname = out / "co2_actual_vs_limit.png"
    plt.savefig(fname, dpi=200)
    plt.close()
    print(f"  -> {fname}")


# Colours for gas consumers
GAS_BREAKDOWN_COLOURS = {
    "Decentralised heat (gas HP)":  "#c0392b",
    "DHN CHP (gas)":                "#e74c3c",
    "DHN boiler (gas)":             "#f1948a",
    "Dec. CHP (gas)":               "#d35400",
    "Dec. adv. CHP (gas)":          "#e67e22",
    "Industrial CHP (gas)":         "#f39c12",
    "Industrial boiler (gas)":      "#f7dc6f",
    "CCGT (electricity)":           "#2980b9",
    "OCGT (electricity)":           "#5dade2",
    "H2 from gas (SMR)":            "#1abc9c",
    "CNG buses":                    "#16a085",
    "LNG cargo":                    "#27ae60",
    "NG freight boats":             "#2ecc71",
    "Gas to HVC (NED)":             "#8e44ad",
    "Gas storage":                  "#95a5a6",
}


def plot_gas_breakdown(df: pd.DataFrame, out: Path):
    """
    New plot: Gas consumption by end-use across GHG sweep scenarios.
    Shows how gas consumers are displaced as GHG constraint tightens.
    """
    # Collect all gas categories that appear
    gas_cols = [c for c in df.columns if c.startswith("GAS_") and c.endswith("_GWh")]
    gas_cats = [c.replace("GAS_", "").replace("_GWh", "") for c in gas_cols]
    # Keep only non-trivial categories
    active = [(cat, col) for cat, col in zip(gas_cats, gas_cols)
              if df[col].sum() > 0.1]
    if not active:
        print("  -> (no gas data, skipping gas breakdown plot)")
        return

    # Sort by total descending
    active.sort(key=lambda pair: -df[pair[1]].sum())
    cats = [a[0] for a in active]
    cols = [a[1] for a in active]

    x = np.arange(len(df))
    labels = _case_labels(df)
    bar_width = 0.7

    fig, ax = plt.subplots(figsize=(15, 8))
    bottoms = np.zeros(len(df))

    for cat, col in zip(cats, cols):
        vals = df[col].values
        color = GAS_BREAKDOWN_COLOURS.get(cat, "#cccccc")
        ax.bar(x, vals, bottom=bottoms, label=cat, color=color,
               edgecolor="white", linewidth=0.5, width=bar_width)
        bottoms += vals

    # Annotate total gas
    for i in range(len(df)):
        if bottoms[i] > 100:
            ax.text(i, bottoms[i] + bottoms.max() * 0.01,
                    f"{bottoms[i]/1000:.1f} TWh",
                    ha="center", va="bottom", fontsize=7, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_xlabel("GHG savings vs 2017 baseline (41.2 MtCO$_2$)", fontsize=11)
    ax.set_ylabel("Gas consumption (GWh/year)", fontsize=11)
    ax.set_title("Finland 2035 -- Gas Consumption by End-Use vs GHG Savings",
                 fontsize=13)
    ax.legend(loc="upper right", fontsize=8, ncol=2, framealpha=0.9)
    ax.grid(axis="y", alpha=0.2)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    fname = out / "fig5_gas_breakdown_vs_ghg.png"
    plt.savefig(fname, dpi=200)
    plt.close()
    print(f"  -> {fname}")


def plot_electricity_mix_sweep(df: pd.DataFrame, out: Path):
    """
    New plot (Fig 6): Electricity production mix (GWh/y) across GHG savings cases,
    stacked by generation category, with total annotated above each bar.

    Shows how the electricity portfolio shifts as GHG constraints tighten:
    nuclear is constant (brownfield floor), wind grows, gas declines.
    """
    elec_order = [
        "Nuclear", "Hydro", "Wind onshore", "Wind offshore", "Solar PV",
        "Gas turbines", "Gas CHP",
        "Biomass CHP/power", "Biomass (conversion co-product)",
        "Electricity import", "Other",
    ]
    active = [(cat, f"ELECMIX_{cat}_GWh") for cat in elec_order
              if f"ELECMIX_{cat}_GWh" in df.columns
              and df[f"ELECMIX_{cat}_GWh"].sum() > 0.1]

    if not active:
        print("  -> (no electricity mix data, skipping electricity mix plot)")
        return

    x = np.arange(len(df))
    labels = _case_labels(df)
    bar_width = 0.7

    fig, ax1 = plt.subplots(figsize=(15, 8))
    bottoms = np.zeros(len(df))

    for cat, col in active:
        vals = df[col].values
        color = ELEC_MIX_COLOURS.get(cat, "#cccccc")
        ax1.bar(x, vals, bottom=bottoms, label=cat, color=color,
                edgecolor="white", linewidth=0.5, width=bar_width)
        bottoms += vals

    # Annotate total electricity (TWh)
    for i in range(len(df)):
        if bottoms[i] > 100:
            ax1.text(i, bottoms[i] + bottoms.max() * 0.01,
                     f"{bottoms[i]/1000:.1f} TWh",
                     ha="center", va="bottom", fontsize=7, fontweight="bold")

    # Right axis: system cost
    ax2 = ax1.twinx()
    costs_MEur = df["system_cost_MEur"].values
    ax2.plot(x, costs_MEur, "s-", color="#1f4e79", markersize=8,
             linewidth=1.5, markerfacecolor="#1f4e79",
             label="System cost (right axis)", zorder=10)
    ax2.set_ylabel("System yearly costs (M€/year)", fontsize=11, color="#1f4e79")
    ax2.tick_params(axis="y", labelcolor="#1f4e79")
    cost_min = np.nanmin(costs_MEur) if len(costs_MEur) > 0 else 0
    cost_max = np.nanmax(costs_MEur) if len(costs_MEur) > 0 else 1
    margin = (cost_max - cost_min) * 0.3 if cost_max > cost_min else 500
    ax2.set_ylim(cost_min - margin * 5, cost_max + margin)

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_xlabel("GHG savings vs 2017 baseline (41.2 MtCO$_2$)", fontsize=11)
    ax1.set_ylabel("Electricity production (GWh/year)", fontsize=11)
    ax1.set_title("Finland 2035 -- Electricity Production Mix vs GHG Savings",
                  fontsize=13)
    ax1.set_ylim(bottom=0)
    ax1.grid(axis="y", alpha=0.2)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8, ncol=2,
               framealpha=0.9)

    plt.tight_layout()
    fname = out / "fig6_electricity_mix_vs_ghg.png"
    plt.savefig(fname, dpi=200)
    plt.close()
    print(f"  -> {fname}")


# ============================================================================
# MAIN
# ============================================================================

def parse_args():
    p = argparse.ArgumentParser(description="Analyse Finland 2035 GHG sweep results")
    p.add_argument("--manifest", default=None,
                   help="Path to ghg_sweep_2035_manifest.json")
    p.add_argument("--include-existing", action="store_true",
                   help="Include the existing national_plan_2035 run (≈49%% savings)")
    p.add_argument("--output-dir", default=None,
                   help="Directory for output plots/CSV (default: manual_runs/ghg_sweep_analysis/)")
    p.add_argument("--keep-duplicates", action="store_true",
                   help="Keep runs whose system cost is identical to unconstrained "
                        "(by default they are collapsed into one)")
    p.add_argument("--suffix", default="",
                   help="Directory name suffix for run discovery (e.g. '_nuke_phaseout')")
    return p.parse_args()


def _deduplicate_runs(df: pd.DataFrame) -> pd.DataFrame:
    """Drop runs whose constraint doesn't bind (identical system cost as
    unconstrained).  Keeps the unconstrained row itself and the first
    binding case for each distinct cost level.
    """
    if len(df) < 2:
        return df
    ref_cost = df.iloc[0]["system_cost_MEur"]
    keep = [True]  # always keep unconstrained
    for i in range(1, len(df)):
        cost = df.iloc[i]["system_cost_MEur"]
        # If cost differs by less than 0.5 M€ from unconstrained, skip it
        if abs(cost - ref_cost) < 0.5:
            keep.append(False)
        else:
            keep.append(True)
    dropped = sum(1 for k in keep if not k)
    if dropped:
        labels = [df.iloc[i]["label"] for i, k in enumerate(keep) if not k]
        print(f"  Dropped {dropped} non-binding runs: {', '.join(labels)}")
    return df[keep].reset_index(drop=True)


def main():
    args = parse_args()

    manifest_path = None
    if args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            manifest_path = REPO_ROOT / manifest_path
    else:
        default_manifest = MANUAL_RUNS / "ghg_sweep_2035_manifest.json"
        if default_manifest.exists():
            manifest_path = default_manifest

    # Discover runs
    print("Discovering sweep runs ...")
    runs = find_sweep_runs(manifest_path, include_existing=args.include_existing,
                           suffix=args.suffix)

    if not runs:
        print("ERROR: No sweep runs found. Run the sweep first or use --include-existing.")
        sys.exit(1)

    print(f"\nFound {len(runs)} runs:")
    for r in runs:
        gwp_str = f"{r['gwp_limit']:,} kt" if r['gwp_limit'] is not None else "unconstrained"
        print(f"  {r['label']:25s}  gwp={gwp_str:>20s}  dir={r['run_dir'].name}")

    # Output directory
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        dirname = "ghg_sweep_analysis" + (args.suffix if args.suffix else "")
        out_dir = MANUAL_RUNS / dirname
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build master table
    print(f"\nExtracting metrics ...")
    df = build_master_table(runs)

    # Save full CSV (all runs including duplicates)
    csv_path = out_dir / "ghg_sweep_2035_master.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  Master CSV -> {csv_path}")

    # Deduplicate non-binding runs for cleaner plots
    if not args.keep_duplicates:
        df_plot = _deduplicate_runs(df)
    else:
        df_plot = df

    # Print summary table
    print(f"\n{'='*90}")
    print(f"  SWEEP SUMMARY TABLE (Finland 2035)")
    print(f"{'='*90}")
    summary_cols = ["label", "gwp_limit", "system_cost_MEur", "co2_net_kt",
                    "co2_actual_kt", "PE_total_TWh", "BIO_total_GWh"]
    avail_cols = [c for c in summary_cols if c in df_plot.columns]
    print(df_plot[avail_cols].to_string(index=False))
    print()

    # Generate plots (using deduplicated data)
    print("Generating plots ...")
    plot_primary_energy_sweep(df_plot, out_dir)
    plot_biomass_allocation_sweep(df_plot, out_dir)
    plot_cost_vs_ghg(df_plot, out_dir)
    plot_co2_actual_vs_limit(df_plot, out_dir)
    plot_gas_breakdown(df_plot, out_dir)
    plot_electricity_mix_sweep(df_plot, out_dir)

    # Write analysis summary
    summary_path = out_dir / "analysis_summary.md"
    _write_analysis_summary(df, runs, summary_path)
    print(f"  -> {summary_path}")

    print(f"\n{'='*70}")
    print(f"  Analysis complete. Results in: {out_dir}")
    print(f"{'='*70}")


def _write_analysis_summary(df: pd.DataFrame, runs: list, path: Path):
    """Write markdown summary of the sweep analysis."""
    lines = [
        "# Finland 2035 GHG-Savings Sweep — Analysis Summary",
        "",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        f"GHG baseline: Finland 2017 = {GHG_BASELINE_2017:,} ktCO₂/y",
        f"Cases analysed: {len(df)}",
        "",
        "## Methodology",
        "",
        "Inspired by Colla et al. (2022) — *Optimal Use of Lignocellulosic Biomass",
        "for the Energy Transition*. GHG savings fractions applied to Finland 2017",
        "baseline via `gwp_limit = 41200 × (1 − savings)` in EnergyScope Multi Cells.",
        "",
        "**Key differences from Colla:**",
        "- Single WOOD resource (no geographic disaggregation of biomass supply)",
        "- HVC as NED proxy (smaller share than Belgian NED)",
        "- Baseline year: 2017 (not 2015)",
        "- Finnish system: nuclear-heavy, DHN-heavy",
        "",
        "## Summary Table",
        "",
    ]

    # Table
    lines.append("| Case | GWP limit (kt) | Cost (bn€/y) | CO₂ actual (Mt) | PE total (TWh) | Biomass total (TWh) |")
    lines.append("|------|----------------|---------------|------------------|----------------|---------------------|")
    for _, row in df.iterrows():
        gwp = f"{row['gwp_limit']:,.0f}" if row.get("gwp_limit") is not None and not pd.isna(row.get("gwp_limit", float("nan"))) else "None"
        cost = f"{row['system_cost_MEur']/1000:.2f}" if not pd.isna(row.get("system_cost_MEur", float("nan"))) else "—"
        co2 = f"{row['co2_actual_kt']/1000:.1f}" if not pd.isna(row.get("co2_actual_kt", float("nan"))) else "—"
        pe = f"{row.get('PE_total_TWh', 0):.0f}"
        bio = f"{row.get('BIO_total_GWh', 0)/1000:.1f}"
        lines.append(f"| {row['label']} | {gwp} | {cost} | {co2} | {pe} | {bio} |")

    lines.append("")
    lines.append("## Plots")
    lines.append("")
    lines.append("- `fig3_primary_energy_vs_ghg.png` — Primary energy by source (cf. Colla Fig. 3)")
    lines.append("- `fig4_biomass_allocation_vs_ghg.png` — Biomass allocation by final use (cf. Colla Fig. 4)")
    lines.append("- `cost_vs_ghg_savings.png` — System cost curve")
    lines.append("- `co2_actual_vs_limit.png` — Model CO₂ vs constraint")
    lines.append("")
    lines.append("## Run Details")
    lines.append("")
    for run in runs:
        lines.append(f"- **{run['label']}**: `{run['run_dir'].name}`")

    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
