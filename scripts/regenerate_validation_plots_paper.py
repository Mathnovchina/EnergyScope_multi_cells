#!/usr/bin/env python3
"""
Regenerate the two validation comparison plots for the paper (PDF format),
with clean academic titles (no run identifier).

Outputs (written to Data/exogenous_data/Mypaper/):
  validation_2017_pe_comparison.pdf
  validation_2017_elec_comparison.pdf
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[1]
RUN_DIR     = REPO / "case_studies/FI/manual_runs/20260323_173930__2017_baseline"
OUTPUTS_DIR = RUN_DIR / "outputs"
REALITY_CSV = REPO / "calibration/reality/finland_2017_reference.csv"
OUT_DIR     = REPO / "Data/exogenous_data/Mypaper"

# ---------------------------------------------------------------------------
# Colour palette  (matches validate_run.py)
# ---------------------------------------------------------------------------
C = {
    "model":   "#3498db",
    "reality": "#e74c3c",
}

# ---------------------------------------------------------------------------
# Data extraction  (replicates validate_run.extract())
# ---------------------------------------------------------------------------
def reality_val(reality: pd.DataFrame, cat: str, met: str) -> float:
    r = reality[(reality["category"] == cat) & (reality["metric"] == met)]
    return float(r["value"].iloc[0]) if len(r) > 0 else 0.0


def extract(outputs_dir: Path) -> dict:
    v = {}
    # Resources.csv → Primary Energy
    res_path = outputs_dir / "Resources.csv"
    if res_path.exists():
        df = pd.read_csv(res_path)
        res = {}
        for _, row in df.iterrows():
            total = float(row.get("R_year_local", 0)) + float(row.get("R_year_exterior", 0))
            res[str(row.iloc[0])] = total / 1000   # GWh → TWh
        v["PE_BIOMASS"] = sum(res.get(r, 0) for r in
            ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"])
        v["PE_OIL"]     = sum(res.get(r, 0) for r in ["GASOLINE", "DIESEL", "LFO", "JET_FUEL"])
        v["PE_GAS"]     = res.get("GAS", 0)
        v["PE_COAL"]    = res.get("COAL", 0)
        v["PE_NUCLEAR"] = res.get("URANIUM", 0)
        v["PE_HYDRO"]   = res.get("RES_HYDRO", 0)
        v["PE_WIND"]    = res.get("RES_WIND", 0)
        v["PE_SOLAR"]   = res.get("RES_SOLAR", 0)
        v["ELEC_IMPORTS"] = res.get("ELECTRICITY", 0)

    # Year_balance.csv → Electricity
    yb_path = outputs_dir / "Year_balance.csv"
    if yb_path.exists():
        yb = pd.read_csv(yb_path, index_col=0)
        def elec(techs):
            return sum(max(0, float(yb.loc[t, "ELECTRICITY"]))
                       for t in techs if t in yb.index and "ELECTRICITY" in yb.columns) / 1000
        v["ELEC_NUCLEAR"]     = elec(["NUCLEAR"])
        v["ELEC_HYDRO"]       = elec(["HYDRO_DAM", "HYDRO_RIVER"])
        v["ELEC_WIND"]        = elec(["WIND_ONSHORE", "WIND_OFFSHORE"])
        v["ELEC_SOLAR"]       = elec(["PV_ROOFTOP", "PV_UTILITY"])
        v["ELEC_GEOTHERMAL"]  = elec(["GEOTHERMAL"])
        chp = ["DHN_COGEN_GAS","DHN_COGEN_WOOD","DHN_COGEN_COAL","DHN_COGEN_WASTE",
               "DHN_COGEN_OIL","IND_COGEN_GAS","IND_COGEN_WOOD","IND_COGEN_COAL",
               "IND_COGEN_WASTE","DEC_COGEN_GAS","DEC_COGEN_OIL",
               "DEC_ADVCOGEN_GAS","DEC_ADVCOGEN_H2"]
        v["ELEC_CHP"]         = elec(chp)
        v["ELEC_CONDENSATION"]= elec(["CCGT","OCGT","COAL_US","COAL_IGCC",
                                       "CCGT_AMMONIA","BIOMASS_TO_POWER"])
        # Gas breakdown (cross-cuts CHP + condensation)
        v["ELEC_GAS"]         = elec(["DHN_COGEN_GAS","IND_COGEN_GAS","DEC_COGEN_GAS",
                                       "DEC_ADVCOGEN_GAS","CCGT","OCGT"])
    return v


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------
def _bar_labels(ax, x, mvals, rvals, w, threshold=1.0):
    for i, (mv, rv) in enumerate(zip(mvals, rvals)):
        if mv > threshold:
            ax.text(x[i] - w/2, mv + 0.5, f"{mv:.1f}", ha="center", fontsize=7)
        if rv > threshold:
            ax.text(x[i] + w/2, rv + 0.5, f"{rv:.1f}", ha="center", fontsize=7)


def plot_pe(model: dict, reality: pd.DataFrame, out_path: Path):
    cats  = ["Biomass", "Oil", "Gas", "Coal+Peat", "Nuclear", "Hydro", "Wind", "Solar"]
    mkeys = ["PE_BIOMASS","PE_OIL","PE_GAS","PE_COAL","PE_NUCLEAR","PE_HYDRO","PE_WIND","PE_SOLAR"]
    rmets = ["biomass","oil","gas","coal_peat","nuclear","hydro","wind","solar"]

    mvals = [model.get(k, 0) for k in mkeys]
    rvals = [reality_val(reality, "primary_energy", m) for m in rmets]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(cats)); w = 0.35
    ax.bar(x - w/2, mvals, w, label="Model",          color=C["model"],   edgecolor="white")
    ax.bar(x + w/2, rvals, w, label="Finland 2017",   color=C["reality"], edgecolor="white")
    _bar_labels(ax, x, mvals, rvals, w)

    ax.set_ylabel("TWh", fontsize=11)
    ax.set_title("Primary energy supply by carrier — model vs. Finland 2017 statistics",
                 fontsize=12, pad=10)
    ax.set_xticks(x); ax.set_xticklabels(cats, rotation=15, ha="right", fontsize=10)
    ax.legend(fontsize=10); ax.grid(axis="y", alpha=0.3); ax.set_ylim(bottom=0)

    mt, rt = sum(mvals), sum(rvals)
    ax.text(0.02, 0.97, f"Model total: {mt:.1f} TWh\nStatistics Finland total: {rt:.1f} TWh",
            transform=ax.transAxes, fontsize=8, va="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    plt.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved {out_path}")


def plot_elec(model: dict, reality: pd.DataFrame, out_path: Path):
    cats  = ["Nuclear", "Hydro", "Wind", "CHP", "Condensation", "Solar", "Imports"]
    mkeys = ["ELEC_NUCLEAR","ELEC_HYDRO","ELEC_WIND","ELEC_CHP",
             "ELEC_CONDENSATION","ELEC_SOLAR","ELEC_IMPORTS"]
    rmets = ["nuclear","hydro","wind","chp","condensation","solar","imports"]

    mvals = [model.get(k, 0) for k in mkeys]
    rvals = [reality_val(reality, "electricity", m) for m in rmets]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(cats)); w = 0.35
    ax.bar(x - w/2, mvals, w, label="Model",          color=C["model"],   edgecolor="white")
    ax.bar(x + w/2, rvals, w, label="Finland 2017",   color=C["reality"], edgecolor="white")
    _bar_labels(ax, x, mvals, rvals, w, threshold=0.3)

    ax.set_ylabel("TWh", fontsize=11)
    ax.set_title("Electricity generation by technology — model vs. Finland 2017 statistics",
                 fontsize=12, pad=10)
    ax.set_xticks(x); ax.set_xticklabels(cats, rotation=15, ha="right", fontsize=10)
    ax.legend(fontsize=10); ax.grid(axis="y", alpha=0.3); ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Reading outputs from: {OUTPUTS_DIR}")
    model   = extract(OUTPUTS_DIR)
    reality = pd.read_csv(REALITY_CSV)

    plot_pe(  model, reality, OUT_DIR / "validation_2017_pe_comparison.pdf")
    plot_elec(model, reality, OUT_DIR / "validation_2017_elec_comparison.pdf")
    print("Done.")
