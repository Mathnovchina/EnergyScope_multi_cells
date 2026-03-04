#!/usr/bin/env python3
"""
Unified Validation Plotter for Finland 2017 Calibration.

Generates:
  1. Primary energy bar chart (model vs reality)
  2. Electricity mix bar chart (model vs reality)
  3. CO2 emissions comparison
  4. Horizontal error chart (all metrics)
  5. Markdown validation report (Table 2 style, per Limpens et al. 2019)
  6. CSV validation table

Usage (single run):
    python validate_run.py --run-dir case_studies/FI/calib_2017_finland_v9

Usage (batch — all 7 baselines):
    python validate_run.py --batch

Usage (specific list):
    python validate_run.py --runs v9 p02b_no_oil_chp_v2

Files produced per run → <run_dir>/validation_plots/
    pe_comparison.png
    elec_comparison.png
    co2_comparison.png
    error_chart.png
    validation_report.md
    validation_table.csv
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # headless backend — no GUI needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
CASE_STUDIES = REPO_ROOT / "case_studies" / "FI"
REALITY_CSV = REPO_ROOT / "calibration" / "reality" / "finland_2017_reference.csv"

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
C = {
    "model":      "#3498db",
    "reality":    "#e74c3c",
    "good":       "#27ae60",
    "acceptable": "#f1c40f",
    "warning":    "#f39c12",
    "bad":        "#c0392b",
}

# ---------------------------------------------------------------------------
# Well-known baselines (for --batch)
# ---------------------------------------------------------------------------
BASELINES = [
    "calib_2017_finland",
    "calib_2017_finland_v9",
    "calib_2017_finland_v10_oil_constr",
    "calib_2017_finland_p02b_no_oil_chp_v2",
    "calib_2017_finland_p04_test",
    "calib_2017_finland_p04_fmin_perc",
    "ref_2017_finland",
]


# ============================================================================
# DATA EXTRACTION
# ============================================================================

def load_reality() -> pd.DataFrame:
    """Load the reality reference CSV."""
    if REALITY_CSV.exists():
        return pd.read_csv(REALITY_CSV)
    print(f"ERROR: Reality reference not found at {REALITY_CSV}")
    sys.exit(1)


def reality_val(reality: pd.DataFrame, cat: str, met: str) -> float:
    r = reality[(reality["category"] == cat) & (reality["metric"] == met)]
    return float(r["value"].iloc[0]) if len(r) > 0 else 0.0


def extract(outputs_dir: Path) -> dict:
    """Extract model values from a run's outputs/ directory."""
    v = {}

    # ---- Resources.csv  →  Primary Energy ----
    res_path = outputs_dir / "Resources.csv"
    if res_path.exists():
        df = pd.read_csv(res_path)
        res = {}
        for _, row in df.iterrows():
            total = float(row.get("R_year_local", 0)) + float(row.get("R_year_exterior", 0))
            res[row.iloc[0]] = total / 1000          # GWh → TWh

        v["PE_BIOMASS"] = sum(res.get(r, 0) for r in
            ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"])
        v["PE_OIL"] = sum(res.get(r, 0) for r in
            ["GASOLINE", "DIESEL", "LFO", "JET_FUEL"])
        v["PE_GAS"]     = res.get("GAS", 0)
        v["PE_COAL"]    = res.get("COAL", 0)          # includes peat proxy
        v["PE_NUCLEAR"] = res.get("URANIUM", 0)
        v["PE_HYDRO"]   = res.get("RES_HYDRO", 0)
        v["PE_WIND"]    = res.get("RES_WIND", 0)
        v["PE_SOLAR"]   = res.get("RES_SOLAR", 0)
        v["ELEC_IMPORTS"] = res.get("ELECTRICITY", 0)

    # ---- Year_balance.csv  →  Electricity & Heat ----
    yb_path = outputs_dir / "Year_balance.csv"
    if yb_path.exists():
        yb = pd.read_csv(yb_path, index_col=0)

        def elec(techs):
            return sum(max(0, float(yb.loc[t, "ELECTRICITY"])) for t in techs
                       if t in yb.index and "ELECTRICITY" in yb.columns) / 1000

        v["ELEC_NUCLEAR"]  = elec(["NUCLEAR"])
        v["ELEC_HYDRO"]    = elec(["HYDRO_DAM", "HYDRO_RIVER"])
        v["ELEC_WIND"]     = elec(["WIND_ONSHORE", "WIND_OFFSHORE"])
        v["ELEC_SOLAR"]    = elec(["PV_ROOFTOP", "PV_UTILITY"])
        v["ELEC_GEOTHERMAL"] = elec(["GEOTHERMAL"])

        chp_techs = [
            "DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL", "DHN_COGEN_WASTE",
            "DHN_COGEN_OIL", "IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_COAL",
            "IND_COGEN_WASTE", "DEC_COGEN_GAS", "DEC_COGEN_OIL",
            "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2",
        ]
        v["ELEC_CHP"] = elec(chp_techs)

        # Per-technology breakdown for diagnostic plots (GWh → TWh)
        v["_CHP_DETAIL"] = {}
        for t in chp_techs:
            val = elec([t])
            if val > 0.001:
                v["_CHP_DETAIL"][t] = val

        cond_techs = ["CCGT", "OCGT", "COAL_US", "COAL_IGCC", "CCGT_AMMONIA", "BIOMASS_TO_POWER"]
        v["ELEC_CONDENSATION"] = elec(cond_techs)

        v["_COND_DETAIL"] = {}
        for t in cond_techs:
            val = elec([t])
            if val > 0.001:
                v["_COND_DETAIL"][t] = val

        gas_techs = ["DHN_COGEN_GAS", "IND_COGEN_GAS", "DEC_COGEN_GAS",
                     "DEC_ADVCOGEN_GAS", "CCGT", "OCGT"]
        v["ELEC_GAS"] = elec(gas_techs)

        v["ELEC_TOTAL"] = sum(v.get(k, 0) for k in
            ["ELEC_NUCLEAR", "ELEC_HYDRO", "ELEC_WIND", "ELEC_SOLAR",
             "ELEC_GEOTHERMAL", "ELEC_CHP", "ELEC_CONDENSATION"])

        # DHN heat
        def heat(techs, layer="HEAT_LOW_T_DHN"):
            return sum(max(0, float(yb.loc[t, layer])) for t in techs
                       if t in yb.index and layer in yb.columns) / 1000

        dhn_techs = [
            "DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL", "DHN_COGEN_WASTE",
            "DHN_COGEN_OIL", "DHN_BOILER_GAS", "DHN_BOILER_WOOD", "DHN_BOILER_OIL",
            "DHN_HP_ELEC", "DHN_DEEP_GEO", "DHN_SOLAR",
        ]
        v["HEAT_DHN"] = heat(dhn_techs)

        # Transport shares
        if "MOB_PRIVATE" in yb.columns:
            car_total = sum(max(0, float(yb.loc[t, "MOB_PRIVATE"]))
                            for t in yb.index if t.startswith("CAR_") and "MOB_PRIVATE" in yb.columns
                            and float(yb.loc[t, "MOB_PRIVATE"]) > 0)
            car_gas = max(0, float(yb.loc["CAR_GASOLINE", "MOB_PRIVATE"])) if "CAR_GASOLINE" in yb.index else 0
            v["GASOLINE_CAR_SHARE"] = car_gas / car_total if car_total > 0 else 0

        if "MOB_FREIGHT_ROAD" in yb.columns:
            truck_total = sum(max(0, float(yb.loc[t, "MOB_FREIGHT_ROAD"]))
                              for t in yb.index if t.startswith("TRUCK_")
                              and float(yb.loc[t, "MOB_FREIGHT_ROAD"]) > 0)
            truck_d = max(0, float(yb.loc["TRUCK_DIESEL", "MOB_FREIGHT_ROAD"])) if "TRUCK_DIESEL" in yb.index else 0
            v["DIESEL_TRUCK_SHARE"] = truck_d / truck_total if truck_total > 0 else 0

    # ---- Gwp_breakdown.csv  →  CO2 ----
    gwp_path = outputs_dir / "Gwp_breakdown.csv"
    if gwp_path.exists():
        df = pd.read_csv(gwp_path)
        if "CO2_net" in df.columns:
            v["CO2"] = df["CO2_net"].sum() / 1000      # ktCO2 → MtCO2
        elif "GWP_op" in df.columns:
            v["CO2"] = df["GWP_op"].sum() / 1000

    # Derived
    pe_keys = ["PE_BIOMASS", "PE_OIL", "PE_GAS", "PE_COAL", "PE_NUCLEAR",
               "PE_HYDRO", "PE_WIND", "PE_SOLAR"]
    v["PE_TOTAL"] = sum(v.get(k, 0) for k in pe_keys)
    re = sum(v.get(k, 0) for k in ["PE_BIOMASS", "PE_HYDRO", "PE_WIND", "PE_SOLAR"])
    v["RE_SHARE"] = re / v["PE_TOTAL"] if v["PE_TOTAL"] > 0 else 0

    return v


# ============================================================================
# PLOTTING
# ============================================================================

def plot_pe(model: dict, reality: pd.DataFrame, run_name: str, out: Path):
    fig, ax = plt.subplots(figsize=(12, 6))
    cats  = ["Biomass", "Oil", "Gas", "Coal+Peat", "Nuclear", "Hydro", "Wind", "Solar"]
    mkeys = ["PE_BIOMASS", "PE_OIL", "PE_GAS", "PE_COAL", "PE_NUCLEAR", "PE_HYDRO", "PE_WIND", "PE_SOLAR"]
    rmets = ["biomass", "oil", "gas", "coal_peat", "nuclear", "hydro", "wind", "solar"]

    mvals = [model.get(k, 0) for k in mkeys]
    rvals = [reality_val(reality, "primary_energy", m) for m in rmets]

    x = np.arange(len(cats));  w = 0.35
    ax.bar(x - w/2, mvals, w, label="Model", color=C["model"], edgecolor="white")
    ax.bar(x + w/2, rvals, w, label="Finland 2017", color=C["reality"], edgecolor="white")
    for i in range(len(cats)):
        if mvals[i] > 1:
            ax.text(x[i] - w/2, mvals[i] + 0.5, f"{mvals[i]:.1f}", ha="center", fontsize=7)
        if rvals[i] > 1:
            ax.text(x[i] + w/2, rvals[i] + 0.5, f"{rvals[i]:.1f}", ha="center", fontsize=7)

    ax.set_ylabel("TWh"); ax.set_title(f"Primary Energy — {run_name} vs Finland 2017")
    ax.set_xticks(x); ax.set_xticklabels(cats, rotation=15, ha="right")
    ax.legend(); ax.grid(axis="y", alpha=0.3); ax.set_ylim(bottom=0)
    mt, rt = sum(mvals), sum(rvals)
    ax.text(0.02, 0.97, f"Model total: {mt:.1f} TWh\nReality total: {rt:.1f} TWh",
            transform=ax.transAxes, fontsize=8, va="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    plt.tight_layout(); plt.savefig(out / "pe_comparison.png", dpi=150); plt.close()


def plot_elec(model: dict, reality: pd.DataFrame, run_name: str, out: Path):
    fig, ax = plt.subplots(figsize=(12, 6))
    cats  = ["Nuclear", "Hydro", "Wind", "CHP", "Condensation", "Gas", "Solar", "Imports"]
    mkeys = ["ELEC_NUCLEAR", "ELEC_HYDRO", "ELEC_WIND", "ELEC_CHP",
             "ELEC_CONDENSATION", "ELEC_GAS", "ELEC_SOLAR", "ELEC_IMPORTS"]
    rmets = ["nuclear", "hydro", "wind", "chp", "condensation", "gas", "solar", "imports"]

    mvals = [model.get(k, 0) for k in mkeys]
    rvals = [reality_val(reality, "electricity", m) for m in rmets]

    x = np.arange(len(cats));  w = 0.35
    ax.bar(x - w/2, mvals, w, label="Model", color=C["model"], edgecolor="white")
    ax.bar(x + w/2, rvals, w, label="Finland 2017", color=C["reality"], edgecolor="white")
    for i in range(len(cats)):
        if mvals[i] > 0.3:
            ax.text(x[i] - w/2, mvals[i] + 0.3, f"{mvals[i]:.1f}", ha="center", fontsize=7)

    ax.set_ylabel("TWh"); ax.set_title(f"Electricity Mix — {run_name} vs Finland 2017")
    ax.set_xticks(x); ax.set_xticklabels(cats, rotation=15, ha="right")
    ax.legend(); ax.grid(axis="y", alpha=0.3); ax.set_ylim(bottom=0)
    plt.tight_layout(); plt.savefig(out / "elec_comparison.png", dpi=150); plt.close()


def plot_co2(model: dict, reality: pd.DataFrame, run_name: str, out: Path):
    fig, ax = plt.subplots(figsize=(7, 5))
    co2_m = model.get("CO2", 0)
    co2_r = reality_val(reality, "emissions", "co2")
    bars = ax.bar(["Model", "Finland 2017"], [co2_m, co2_r],
                  color=[C["model"], C["reality"]], edgecolor="white", width=0.5)
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5,
                f"{b.get_height():.1f}", ha="center", fontweight="bold")
    diff = co2_m - co2_r
    rel = diff / co2_r * 100 if co2_r else 0
    ax.set_ylabel("MtCO2")
    ax.set_title(f"CO2 Emissions — {run_name}\nΔ = {diff:+.1f} MtCO2 ({rel:+.1f}%)")
    ax.set_ylim(bottom=0, top=max(co2_m, co2_r) * 1.3)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout(); plt.savefig(out / "co2_comparison.png", dpi=150); plt.close()


def plot_errors(model: dict, reality: pd.DataFrame, run_name: str, out: Path):
    metrics = [
        ("Biomass (PE)",       "PE_BIOMASS",       "primary_energy", "biomass"),
        ("Oil (PE)",           "PE_OIL",           "primary_energy", "oil"),
        ("Gas (PE)",           "PE_GAS",           "primary_energy", "gas"),
        ("Coal+Peat (PE)",     "PE_COAL",          "primary_energy", "coal_peat"),
        ("Nuclear (PE)",       "PE_NUCLEAR",       "primary_energy", "nuclear"),
        ("Hydro (PE)",         "PE_HYDRO",         "primary_energy", "hydro"),
        ("Wind (PE)",          "PE_WIND",          "primary_energy", "wind"),
        ("Nuclear (Elec)",     "ELEC_NUCLEAR",     "electricity",    "nuclear"),
        ("Hydro (Elec)",       "ELEC_HYDRO",       "electricity",    "hydro"),
        ("Wind (Elec)",        "ELEC_WIND",        "electricity",    "wind"),
        ("CHP (Elec)",         "ELEC_CHP",         "electricity",    "chp"),
        ("Gas (Elec)",         "ELEC_GAS",         "electricity",    "gas"),
        ("Condensation (Elec)","ELEC_CONDENSATION", "electricity",   "condensation"),
        ("Imports (Elec)",     "ELEC_IMPORTS",     "electricity",    "imports"),
        ("DH Production",      "HEAT_DHN",         "heat",           "dh_production"),
        ("CO2 Emissions",      "CO2",              "emissions",      "co2"),
    ]

    labels, errors = [], []
    for label, mkey, cat, met in metrics:
        actual = reality_val(reality, cat, met)
        mod = model.get(mkey, 0)
        if actual > 0.01:
            errors.append((mod - actual) / actual * 100)
            labels.append(label)

    fig, ax = plt.subplots(figsize=(10, max(6, len(labels) * 0.45)))
    y = np.arange(len(labels))
    colours = []
    for e in errors:
        if abs(e) <= 10:    colours.append(C["good"])
        elif abs(e) <= 25:  colours.append(C["acceptable"])
        elif abs(e) <= 50:  colours.append(C["warning"])
        else:               colours.append(C["bad"])
    ax.barh(y, errors, color=colours, edgecolor="white")
    ax.axvline(0, color="black", lw=1)
    ax.axvline(-10, color=C["good"], lw=0.8, ls=":", alpha=0.6)
    ax.axvline( 10, color=C["good"], lw=0.8, ls=":", alpha=0.6)
    ax.axvline(-25, color=C["acceptable"], lw=0.8, ls="--", alpha=0.4)
    ax.axvline( 25, color=C["acceptable"], lw=0.8, ls="--", alpha=0.4)
    ax.set_yticks(y); ax.set_yticklabels(labels)
    ax.set_xlabel("Error vs Reality (%)")
    ax.set_title(f"Validation Error — {run_name}")
    maxe = max(abs(min(errors)), abs(max(errors)), 50) * 1.15
    ax.set_xlim(-min(maxe, 200), min(maxe, 200))
    for i, e in enumerate(errors):
        ax.text(min(max(e, -190), 190), i, f" {e:+.0f}%",
                va="center", fontsize=8,
                ha="left" if e >= 0 else "right")
    legend = [mpatches.Patch(color=C["good"], label="≤10%"),
              mpatches.Patch(color=C["acceptable"], label="≤25%"),
              mpatches.Patch(color=C["warning"], label="≤50%"),
              mpatches.Patch(color=C["bad"], label=">50%")]
    ax.legend(handles=legend, loc="lower right", fontsize=7)
    plt.tight_layout(); plt.savefig(out / "error_chart.png", dpi=150); plt.close()


def plot_chp_cond_breakdown(model: dict, reality: pd.DataFrame, run_name: str, out: Path):
    """Diagnostic: shows which technologies produce CHP and condensation electricity."""
    chp_detail = model.get("_CHP_DETAIL", {})
    cond_detail = model.get("_COND_DETAIL", {})

    if not chp_detail and not cond_detail:
        return  # nothing to plot

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ---- CHP breakdown (left) ----
    ax = axes[0]
    chp_reality = reality_val(reality, "electricity", "chp")
    if chp_detail:
        techs = sorted(chp_detail.keys(), key=lambda t: chp_detail[t], reverse=True)
        vals = [chp_detail[t] for t in techs]
        short = [t.replace("DHN_COGEN_", "DHN·").replace("IND_COGEN_", "IND·")
                  .replace("DEC_COGEN_", "DEC·").replace("DEC_ADVCOGEN_", "DEC↑·") for t in techs]
        bars = ax.barh(range(len(techs)), vals, color=C["model"], edgecolor="white")
        ax.set_yticks(range(len(techs)))
        ax.set_yticklabels(short, fontsize=8)
        for i, v in enumerate(vals):
            ax.text(v + 0.1, i, f"{v:.2f}", va="center", fontsize=7)
    ax.axvline(chp_reality, color=C["reality"], ls="--", lw=2, label=f"Reality total: {chp_reality:.1f} TWh")
    model_chp = model.get("ELEC_CHP", 0)
    ax.set_xlabel("TWh")
    ax.set_title(f"CHP Electricity Breakdown\nModel total: {model_chp:.2f} TWh vs Reality: {chp_reality:.1f} TWh")
    ax.legend(fontsize=7)
    ax.grid(axis="x", alpha=0.3)

    # ---- Condensation breakdown (right) ----
    ax = axes[1]
    cond_reality = reality_val(reality, "electricity", "condensation")
    if cond_detail:
        techs = sorted(cond_detail.keys(), key=lambda t: cond_detail[t], reverse=True)
        vals = [cond_detail[t] for t in techs]
        bars = ax.barh(range(len(techs)), vals, color=C["model"], edgecolor="white")
        ax.set_yticks(range(len(techs)))
        ax.set_yticklabels(techs, fontsize=8)
        for i, v in enumerate(vals):
            ax.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=7)
    ax.axvline(cond_reality, color=C["reality"], ls="--", lw=2, label=f"Reality total: {cond_reality:.1f} TWh")
    model_cond = model.get("ELEC_CONDENSATION", 0)
    ax.set_xlabel("TWh")
    ax.set_title(f"Condensation Breakdown\nModel: {model_cond:.2f} TWh vs Reality: {cond_reality:.1f} TWh")
    ax.legend(fontsize=7)
    ax.grid(axis="x", alpha=0.3)

    plt.suptitle(f"CHP & Condensation Fuel Diagnostic — {run_name}", fontsize=11, y=1.01)
    plt.tight_layout()
    plt.savefig(out / "chp_cond_breakdown.png", dpi=150, bbox_inches="tight")
    plt.close()


# ============================================================================
# REPORT & TABLE
# ============================================================================

def write_report(model: dict, reality: pd.DataFrame, run_name: str, out: Path):
    """Write markdown validation report (Table 2 style)."""
    L = []
    L.append(f"# Finland 2017 Validation Report — {run_name}")
    L.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append("")
    L.append("Methodology: Limpens et al. (2019) *Applied Energy* 255.")
    L.append("")

    def row(label, mkey, cat, met, unit="TWh"):
        actual = reality_val(reality, cat, met)
        mod = model.get(mkey, 0)
        delta = mod - actual
        if actual > 0.01:
            rel = delta / actual * 100
            s = "✓" if abs(rel) <= 10 else ("~" if abs(rel) <= 25 else ("⚠" if abs(rel) <= 50 else "✗"))
            return f"| {label} | {actual:.2f} | {mod:.2f} | {delta:+.2f} | {rel:+.1f}% | {s} |"
        elif mod > 0.01:
            return f"| {label} | {actual:.2f} | {mod:.2f} | {delta:+.2f} | N/A | info |"
        else:
            return f"| {label} | {actual:.2f} | {mod:.2f} | - | - | ok |"

    hdr = "| Metric | Actual | Model | Δ | Rel. Err | Status |"
    sep = "|--------|--------|-------|---|----------|--------|"

    L.append("## Primary Energy (TWh)")
    L.append(""); L.append(hdr); L.append(sep)
    for lab, mk, met in [("Biomass","PE_BIOMASS","biomass"),("Oil","PE_OIL","oil"),
                          ("Gas","PE_GAS","gas"),("Coal+Peat","PE_COAL","coal_peat"),
                          ("Nuclear","PE_NUCLEAR","nuclear"),("Hydro","PE_HYDRO","hydro"),
                          ("Wind","PE_WIND","wind"),("Solar","PE_SOLAR","solar")]:
        L.append(row(lab, mk, "primary_energy", met))

    L.append("")
    L.append("## Electricity Generation (TWh)")
    L.append(""); L.append(hdr); L.append(sep)
    for lab, mk, met in [("Nuclear","ELEC_NUCLEAR","nuclear"),("Hydro","ELEC_HYDRO","hydro"),
                          ("Wind","ELEC_WIND","wind"),("CHP (all)","ELEC_CHP","chp"),
                          ("Condensation","ELEC_CONDENSATION","condensation"),
                          ("Gas power","ELEC_GAS","gas"),("Solar","ELEC_SOLAR","solar"),
                          ("Imports","ELEC_IMPORTS","imports")]:
        L.append(row(lab, mk, "electricity", met))

    L.append("")
    L.append("## Heat")
    L.append(""); L.append(hdr); L.append(sep)
    L.append(row("DH production", "HEAT_DHN", "heat", "dh_production"))

    L.append("")
    L.append("## Emissions")
    L.append(""); L.append(hdr); L.append(sep)
    L.append(row("CO2", "CO2", "emissions", "co2", "MtCO2"))

    # Summary
    pe_m = model.get("PE_TOTAL", 0)
    pe_r = reality_val(reality, "primary_energy", "total")
    co2_m = model.get("CO2", 0)
    co2_r = reality_val(reality, "emissions", "co2")
    re_m = model.get("RE_SHARE", 0)
    re_r = reality_val(reality, "misc", "re_share_primary")

    L.extend(["", "## Summary",
              f"- PE Total: model {pe_m:.1f} TWh vs reality {pe_r:.1f} TWh ({(pe_m-pe_r)/pe_r*100:+.1f}%)" if pe_r else "",
              f"- CO2: model {co2_m:.1f} MtCO2 vs reality {co2_r:.1f} MtCO2 ({(co2_m-co2_r)/co2_r*100:+.1f}%)" if co2_r else "",
              f"- RE share: model {re_m:.1%} vs reality {re_r:.1%}",
              "", "Legend: ✓ ≤10% | ~ ≤25% | ⚠ ≤50% | ✗ >50%"])

    (out / "validation_report.md").write_text("\n".join(L), encoding="utf-8")


def write_csv(model: dict, reality: pd.DataFrame, out: Path):
    """Write CSV validation table."""
    metrics = [
        ("Primary Energy","Biomass","PE_BIOMASS","primary_energy","biomass","TWh"),
        ("Primary Energy","Oil","PE_OIL","primary_energy","oil","TWh"),
        ("Primary Energy","Gas","PE_GAS","primary_energy","gas","TWh"),
        ("Primary Energy","Coal+Peat","PE_COAL","primary_energy","coal_peat","TWh"),
        ("Primary Energy","Nuclear","PE_NUCLEAR","primary_energy","nuclear","TWh"),
        ("Primary Energy","Hydro","PE_HYDRO","primary_energy","hydro","TWh"),
        ("Primary Energy","Wind","PE_WIND","primary_energy","wind","TWh"),
        ("Primary Energy","Solar","PE_SOLAR","primary_energy","solar","TWh"),
        ("Electricity","Nuclear","ELEC_NUCLEAR","electricity","nuclear","TWh"),
        ("Electricity","Hydro","ELEC_HYDRO","electricity","hydro","TWh"),
        ("Electricity","Wind","ELEC_WIND","electricity","wind","TWh"),
        ("Electricity","CHP","ELEC_CHP","electricity","chp","TWh"),
        ("Electricity","Condensation","ELEC_CONDENSATION","electricity","condensation","TWh"),
        ("Electricity","Gas","ELEC_GAS","electricity","gas","TWh"),
        ("Electricity","Solar","ELEC_SOLAR","electricity","solar","TWh"),
        ("Electricity","Imports","ELEC_IMPORTS","electricity","imports","TWh"),
        ("Heat","DH production","HEAT_DHN","heat","dh_production","TWh"),
        ("Emissions","CO2","CO2","emissions","co2","MtCO2"),
    ]
    rows = []
    for cat, name, mkey, rcat, rmet, unit in metrics:
        actual = reality_val(reality, rcat, rmet)
        mod = model.get(mkey, 0)
        delta = mod - actual
        rel = (delta / actual * 100) if actual > 0.01 else 0
        rows.append({"Category": cat, "Metric": name, "Actual_2017": round(actual, 2),
                      "Model": round(mod, 2), "Delta": round(delta, 2),
                      "Rel_Error_%": round(rel, 1), "Unit": unit})
    pd.DataFrame(rows).to_csv(out / "validation_table.csv", index=False)


# ============================================================================
# ORCHESTRATION
# ============================================================================

def validate_one(run_dir: Path, reality: pd.DataFrame):
    """Validate a single run and write all outputs."""
    outputs_dir = run_dir / "outputs"
    if not outputs_dir.exists():
        print(f"  SKIP (no outputs): {run_dir.name}")
        return False

    out = run_dir / "validation_plots"
    out.mkdir(exist_ok=True)
    name = run_dir.name

    print(f"  Validating: {name}")
    model = extract(outputs_dir)
    print(f"    Extracted {len(model)} model metrics")

    plot_pe(model, reality, name, out)
    plot_elec(model, reality, name, out)
    plot_co2(model, reality, name, out)
    plot_errors(model, reality, name, out)
    plot_chp_cond_breakdown(model, reality, name, out)
    write_report(model, reality, name, out)
    write_csv(model, reality, out)

    print(f"    → {out}")
    return True


def main():
    p = argparse.ArgumentParser(description="Validation plotter — Finland 2017")
    p.add_argument("--run-dir", "-r", help="Path to a single run directory")
    p.add_argument("--run-name", "-n", help="Run name in case_studies/FI/")
    p.add_argument("--runs", nargs="+", help="List of run names to validate")
    p.add_argument("--batch", action="store_true", help="Validate all 7 baselines")
    args = p.parse_args()

    reality = load_reality()
    print(f"Loaded {len(reality)} reality metrics from {REALITY_CSV.name}")

    dirs = []
    if args.batch:
        dirs = [CASE_STUDIES / b for b in BASELINES]
    elif args.runs:
        for rn in args.runs:
            d = CASE_STUDIES / rn
            if not d.exists():
                d = CASE_STUDIES / f"calib_2017_finland_{rn}"
            dirs.append(d)
    elif args.run_dir:
        dirs = [Path(args.run_dir)]
    elif args.run_name:
        d = CASE_STUDIES / args.run_name
        if not d.exists():
            d = CASE_STUDIES / f"calib_2017_finland_{args.run_name}"
        dirs = [d]
    else:
        print("Specify --batch, --run-dir, --run-name, or --runs")
        sys.exit(1)

    ok = 0
    for d in dirs:
        if not d.exists():
            print(f"  NOT FOUND: {d}")
            continue
        if validate_one(d, reality):
            ok += 1

    print(f"\nDone: {ok}/{len(dirs)} runs validated.")


if __name__ == "__main__":
    main()
