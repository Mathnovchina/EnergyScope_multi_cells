#!/usr/bin/env python3
"""
plot_forest_scenarios.py
========================
Matrix visualization: 3 forest scenarios × 3 GHG targets, Finland 2035.

Layout (2 rows × 3 columns):
  Row A: Primary energy mix (stacked bars by carrier)
  Row B: Finnish biomass supply tiers (stacked + cumulative availability lines)

Also produces a Colla-style biomass allocation figure:
  Grouped bars: 3 GHG targets × 3 forest scenarios, stacked by final use

Outputs:
  plots/forest_scenarios_2035_energy_matrix.png
  plots/forest_scenarios_2035_biomass_allocation.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

# ─── PATHS ────────────────────────────────────────────────────────────────
REPO_ROOT  = Path(__file__).resolve().parents[1]
FOREST_DIR = REPO_ROOT / "case_studies" / "FI" / "forest_scenarios_2035"
OUT_DIR    = REPO_ROOT / "plots"
OUT_DIR.mkdir(exist_ok=True)

# ─── SCENARIO METADATA ───────────────────────────────────────────────────
# S1-BES = Bioeconomy Strategy: intensive harvest, HIGH biomass potential
#          → pro-bioeconomy, negative for biodiversity conservation
# S2-NFS = No Forest Strategy (reference): BAU / policy-trend baseline
# S3-BDS = Biodiversity Strategy: conservation-first, LOW biomass potential
#          → pro-biodiversity, constrained bioeconomy
SCENARIOS = {
    "S1_BES": {
        "label":  "S1 — High potential\n(Bioeconomy strategy, –biodiversity)",
        "short":  "S1: High potential",
        "color":  "#a04000",          # dark amber-brown (intensive harvest)
        "bg":     "#fef5e7",          # very light amber background
        "avail_gwh": {                # cumulative tier availability limits (GWh)
            "FI1": 54530,
            "FI2": 54530 + 45857,
            "FI3": 54530 + 45857 + 15052,
            "FI4": 54530 + 45857 + 15052 + 6504,
        },
    },
    "S2_NFS": {
        "label":  "S2 — Reference (BAU)\n(Policy trends / neutral)",
        "short":  "S2: BAU / Ref.",
        "color":  "#4a4a4a",          # dark gray (neutral)
        "bg":     "#f6f6f6",          # neutral background
        "avail_gwh": {
            "FI1": 45442,
            "FI2": 45442 + 38214,
            "FI3": 45442 + 38214 + 12543,
            "FI4": 45442 + 38214 + 12543 + 5420,
        },
    },
    "S3_BDS": {
        "label":  "S3 — Low potential\n(Biodiversity-friendly, +conservation)",
        "short":  "S3: Low potential",
        "color":  "#1e6b3c",          # forest green (biodiversity-first)
        "bg":     "#eafaf1",          # very light green background
        "avail_gwh": {
            "FI1": 43188,
            "FI2": 43188 + 20690,
            "FI3": 43188 + 20690 + 6272,
            "FI4": 43188 + 20690 + 6272 + 4071,
        },
    },
}

GHG_TARGETS = ["unconstrained", "ghg_95pct_nonuke", "ghg_95pct"]
GHG_LABELS  = ["Unconstrained", "−95% GHG\n(nuclear phase-out)", "−95% GHG\n(with nuclear)"]

# ─── COLOR PALETTES ──────────────────────────────────────────────────────
CARRIER_COLORS = {
    "Oil products":       "#808080",   # mid-gray
    "Gas":                "#bdb76b",   # dark khaki
    "Nuclear":            "#f7dc6f",   # light yellow
    "Hydro":              "#1a5276",   # navy blue
    "Wind":               "#85c1e9",   # sky blue
    "Solar":              "#e67e22",   # orange
    "Other biomass":      "#6e2f1a",   # dark brown
    "Finnish forestry":   "#1e8449",   # forest green
}
# Stacking order (bottom to top) — most fossil at bottom, cleanest at top
CARRIER_ORDER = [
    "Oil products", "Gas", "Nuclear", "Hydro",
    "Wind", "Solar", "Other biomass", "Finnish forestry",
]

TIER_COLORS = {
    "WOOD_FI1": "#1a7a2e",   # deep green  (cheapest, most sustainable)
    "WOOD_FI2": "#74c476",   # medium green
    "WOOD_FI3": "#d4a017",   # amber
    "WOOD_FI4": "#c0392b",   # red
    "WOOD_FI5": "#6c1a15",   # dark red (backstop — expensive)
}
TIER_LABELS = {
    "WOOD_FI1": "FI-1  (~11 €/MWh)",
    "WOOD_FI2": "FI-2  (~22 €/MWh)",
    "WOOD_FI3": "FI-3  (~27 €/MWh)",
    "WOOD_FI4": "FI-4  (~33 €/MWh)",
    "WOOD_FI5": "FI-5  backstop",
}
TIER_ORDER = ["WOOD_FI1", "WOOD_FI2", "WOOD_FI3", "WOOD_FI4", "WOOD_FI5"]

# Availability limit dash styles (cumulative up to tier FI1 … FI4)
AVAIL_STYLES = [
    ("-",  "#1a7a2e", "≤ FI-1 cap"),
    ("--", "#74c476", "≤ FI-1+2 cap"),
    ("-.", "#d4a017", "≤ FI-1+2+3 cap"),
    (":",  "#c0392b", "≤ FI-1+2+3+4 cap"),
]

# ─── BIOMASS ALLOCATION (Colla Fig. 4 equivalent) ────────────────────────
# Technology → final-use category mapping
BIOMASS_TECH_MAP = {
    "IND_BOILER_WOOD":              "HT heat — boilers (wood)",
    "IND_BOILER_BIOWASTE":          "HT heat — boilers (wood)",
    "IND_BOILER_WASTE":             "HT heat — boilers (waste)",
    "IND_COGEN_WOOD":               "HT heat — CHP",
    "IND_COGEN_WASTE":              "HT heat — CHP",
    "DHN_BOILER_WOOD":              "LT heat — DHN boilers",
    "DHN_COGEN_WOOD":               "LT heat — DHN CHP",
    "DHN_COGEN_WASTE":              "LT heat — DHN CHP",
    "DEC_BOILER_WOOD":              "LT heat — decentralised",
    "DEC_COGEN_WOOD":               "LT heat — decentralised",
    "DEC_ADVCOGEN_WOOD":            "LT heat — decentralised",
    "BIOMASS_TO_POWER":             "Electricity",
    "BIOMASS_TO_HVC":               "NED / chemicals",
    "BIOMASS_TO_METHANOL":          "NED / chemicals",
    "BIOWASTE_TO_METHANOL":         "NED / chemicals",
    "BIOMASS_TO_DIESEL":            "Mobility fuels",
    "BIOMASS_TO_GASOLINE":          "Mobility fuels",
    "BIOMASS_TO_JET_FUEL":          "Mobility fuels",
    "BIOMASS_TO_LFO":               "Mobility fuels",
    "BIOMASS_TO_METHANE":           "Mobility fuels",
    "BIOWASTE_TO_DIESEL":           "Mobility fuels",
    "BIOWASTE_TO_JET_FUEL":         "Mobility fuels",
    "BIOMETHANATION_WET_BIOMASS":   "Biogas / biomethanation",
    "BIOMETHANATION_BIOWASTE":      "Biogas / biomethanation",
}
BIOMASS_RESOURCE_COLS = [
    "WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2", "WASTE",
]

# Final-use category display order (bottom → top), colours, hatch
ALLOC_ORDER = [
    "HT heat — boilers (wood)",
    "HT heat — boilers (waste)",
    "HT heat — CHP",
    "LT heat — DHN boilers",
    "LT heat — DHN CHP",
    "LT heat — decentralised",
    "Electricity",
    "NED / chemicals",
    "Mobility fuels",
    "Biogas / biomethanation",
]
ALLOC_COLORS = {
    "HT heat — boilers (wood)":    "#1a5276",   # dark navy (solid — wood)
    "HT heat — boilers (waste)":   "#1a5276",   # same navy, hatched
    "HT heat — CHP":               "#e67e22",   # orange
    "LT heat — DHN boilers":       "#27ae60",   # green
    "LT heat — DHN CHP":           "#a9dfbf",   # light green
    "LT heat — decentralised":     "#7fb3d3",   # light blue
    "Electricity":                 "#f7dc6f",   # yellow
    "NED / chemicals":             "#aaaaaa",   # gray, hatched
    "Mobility fuels":              "#e91e8c",   # hot pink
    "Biogas / biomethanation":     "#c8e026",   # yellow-green
}
ALLOC_HATCHES = {
    "HT heat — boilers (waste)":   "////",
    "NED / chemicals":             "////",
}

# ─── DATA LOADING ────────────────────────────────────────────────────────
def _val(res: pd.DataFrame, resource: str, col: str = "R_year_local") -> float:
    """Safely extract one value from Resources.csv."""
    if resource in res.index:
        v = res.loc[resource, col] if col in res.columns else 0
        return float(v) if pd.notna(v) else 0.0
    return 0.0


def load_run(run_dir: Path) -> dict:
    out = run_dir / "outputs"
    res = pd.read_csv(out / "Resources.csv", index_col=0, encoding="latin-1")

    def s(*resources):
        """Sum R_year_local + R_year_exterior for a list of resources → TWh."""
        total = sum(
            _val(res, r, "R_year_local") + _val(res, r, "R_year_exterior")
            for r in resources
        )
        return total / 1000

    carriers = {
        "Oil products": s(
            "GASOLINE", "DIESEL", "LFO", "JET_FUEL",
            "GASOLINE_RE", "DIESEL_RE", "LFO_RE", "JET_FUEL_RE",
        ),
        "Gas":              s("GAS", "GAS_RE"),
        "Nuclear":          s("URANIUM"),
        "Hydro":            s("RES_HYDRO"),
        "Wind":             s("RES_WIND"),
        "Solar":            s("RES_SOLAR"),
        "Finnish forestry": s("WOOD_FI1", "WOOD_FI2", "WOOD_FI3", "WOOD_FI4", "WOOD_FI5"),
        "Other biomass":    s("WET_BIOMASS", "BIOMASS_RESIDUES", "BIOWASTE",
                              "ENERGY_CROPS_2", "WASTE"),
    }

    tiers = {t: _val(res, t, "R_year_local") for t in TIER_ORDER}

    cost_df = pd.read_csv(out / "TotalCost.csv", index_col=0)
    cost    = float(cost_df.iloc[0, 0])

    gwp_df  = pd.read_csv(out / "Gwp_breakdown.csv", index_col=0, encoding="latin-1")
    gwp     = float(gwp_df.select_dtypes("number").sum().sum()) / 1000  # kt → Mt

    # Biomass allocation by final use (from Year_balance)
    yb       = pd.read_csv(out / "Year_balance.csv", index_col=0)
    bio_cols = [c for c in BIOMASS_RESOURCE_COLS if c in yb.columns]
    alloc: dict[str, float] = {}
    for tech in yb.index:
        consumption = sum(
            abs(float(yb.loc[tech, c]))
            for c in bio_cols
            if float(yb.loc[tech, c]) < -0.01
        )
        if consumption > 0.01:
            cat = BIOMASS_TECH_MAP.get(tech, "Other")
            alloc[cat] = alloc.get(cat, 0.0) + consumption / 1000  # GWh → TWh

    return {"carriers": carriers, "tiers": tiers, "cost": cost, "gwp": gwp, "alloc": alloc}


def find_run(scenario: str, ghg: str) -> Path | None:
    """Return the most recent completed run directory for this scenario × GHG target."""
    matches = []
    for d in FOREST_DIR.iterdir():
        if not d.is_dir():
            continue
        parts = d.name.split("__")
        if len(parts) < 3:
            continue
        if parts[1] == scenario and parts[2] == ghg:
            if (d / "outputs" / "TotalCost.csv").exists():
                matches.append(d)
    return sorted(matches)[-1] if matches else None


# ─── PLOTTING ────────────────────────────────────────────────────────────
def main():
    # 1. Load all 9 runs
    data: dict[tuple, dict] = {}
    for scen in SCENARIOS:
        for ghg in GHG_TARGETS:
            run_dir = find_run(scen, ghg)
            if run_dir is None:
                print(f"  WARNING: run not found — {scen} × {ghg}")
                continue
            data[(scen, ghg)] = load_run(run_dir)
    print(f"  Loaded {len(data)}/9 runs")

    # 2. Reference cost for Δ annotation (S2_NFS unconstrained)
    ref_cost = data.get(("S2_NFS", "unconstrained"), {}).get("cost", None)

    # 3. Build figure
    fig = plt.figure(figsize=(17, 11))
    gs  = fig.add_gridspec(
        2, 3,
        height_ratios=[2.5, 1.2],
        hspace=0.42, wspace=0.10,
        left=0.07, right=0.82, top=0.91, bottom=0.07,
    )
    axes_top = [fig.add_subplot(gs[0, c]) for c in range(3)]
    axes_bot = [fig.add_subplot(gs[1, c]) for c in range(3)]

    bar_w   = 0.55
    x       = np.arange(len(GHG_TARGETS))
    scen_keys = list(SCENARIOS.keys())

    # Shared Y ranges
    y_top_max = 310
    y_bot_max = 145

    for col_i, scen_key in enumerate(scen_keys):
        scen_info = SCENARIOS[scen_key]
        ax_top   = axes_top[col_i]
        ax_bot   = axes_bot[col_i]

        # ── Panel A: Primary energy stacked bars ──────────────────────────
        ax_top.set_facecolor(scen_info["bg"])
        bottoms = np.zeros(len(GHG_TARGETS))

        for carrier in CARRIER_ORDER:
            vals = np.array([
                data.get((scen_key, ghg), {}).get("carriers", {}).get(carrier, 0)
                for ghg in GHG_TARGETS
            ])
            ax_top.bar(
                x, vals, bar_w, bottom=bottoms,
                color=CARRIER_COLORS[carrier],
                label=carrier, zorder=3, edgecolor="white", linewidth=0.3,
            )
            bottoms += vals

        # Total bar height for annotations
        totals = np.array([
            sum(data.get((scen_key, ghg), {}).get("carriers", {}).values() or [0])
            for ghg in GHG_TARGETS
        ])

        # GHG annotation above bars
        for i, ghg in enumerate(GHG_TARGETS):
            key = (scen_key, ghg)
            if key in data:
                gwp  = data[key]["gwp"]
                cost = data[key]["cost"]
                ax_top.annotate(
                    f"{gwp:.1f} Mt",
                    xy=(x[i], totals[i] + 3),
                    ha="center", va="bottom",
                    fontsize=8, color="#1a252f", fontweight="bold",
                )
                # Cost annotation inside bar bottom (with Δ from S2_NFS ref)
                if ref_cost is not None:
                    delta = cost - ref_cost
                    sign  = "+" if delta >= 0 else ""
                    ax_top.annotate(
                        f"{cost:.0f}\n({sign}{delta:.0f})",
                        xy=(x[i], 6),
                        ha="center", va="bottom",
                        fontsize=6.5, color="white", fontweight="bold",
                    )

        # Column header band (colored top spine)
        for spine in ax_top.spines.values():
            spine.set_edgecolor(scen_info["color"])
            spine.set_linewidth(2)

        # Formatting
        ax_top.set_xlim(-0.5, len(GHG_TARGETS) - 0.5)
        ax_top.set_ylim(0, y_top_max)
        ax_top.set_xticks(x)
        ax_top.set_xticklabels(GHG_LABELS, fontsize=9)
        ax_top.yaxis.set_minor_locator(MultipleLocator(10))
        ax_top.grid(axis="y", which="major", alpha=0.2, zorder=0)
        ax_top.grid(axis="y", which="minor", alpha=0.10, zorder=0, linestyle=":")

        if col_i == 0:
            ax_top.set_ylabel("Primary energy  (TWh/y)", fontsize=9.5)
        else:
            ax_top.set_yticklabels([])

        # Column title
        ax_top.set_title(
            scen_info["label"],
            fontsize=11, fontweight="bold", color="white",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor=scen_info["color"],
                edgecolor="none", alpha=0.9,
            ),
            pad=8,
        )

        # ── Panel B: Biomass tier stacked bars ────────────────────────────
        ax_bot.set_facecolor(scen_info["bg"])
        for spine in ax_bot.spines.values():
            spine.set_edgecolor(scen_info["color"])
            spine.set_linewidth(2)

        tier_bottoms = np.zeros(len(GHG_TARGETS))
        for tier in TIER_ORDER:
            vals = np.array([
                data.get((scen_key, ghg), {}).get("tiers", {}).get(tier, 0) / 1000
                for ghg in GHG_TARGETS
            ])
            if vals.max() > 0.5:   # skip invisible slivers
                ax_bot.bar(
                    x, vals, bar_w, bottom=tier_bottoms,
                    color=TIER_COLORS[tier],
                    label=TIER_LABELS[tier], zorder=3,
                    edgecolor="white", linewidth=0.3,
                )
            tier_bottoms += vals

        # Annotate total Finnish biomass on top
        for i, ghg in enumerate(GHG_TARGETS):
            key = (scen_key, ghg)
            if key in data:
                tot_fi = sum(data[key]["tiers"].values()) / 1000
                if tot_fi > 1:
                    ax_bot.annotate(
                        f"{tot_fi:.0f}",
                        xy=(x[i], tier_bottoms[i] + 1),
                        ha="center", va="bottom",
                        fontsize=7.5, color="#333333",
                    )

        # Cumulative availability reference lines
        avail = scen_info["avail_gwh"]
        cum_keys = ["FI1", "FI2", "FI3", "FI4"]
        for (ls, lc, lbl), ck in zip(AVAIL_STYLES, cum_keys):
            cap_twh = avail[ck] / 1000
            if cap_twh < y_bot_max:
                ax_bot.axhline(
                    cap_twh, ls=ls, lw=1.4, color=lc, alpha=0.75, zorder=2,
                )

        # Formatting
        ax_bot.set_xlim(-0.5, len(GHG_TARGETS) - 0.5)
        ax_bot.set_ylim(0, y_bot_max)
        ax_bot.set_xticks(x)
        ax_bot.set_xticklabels(GHG_LABELS, fontsize=9)
        ax_bot.grid(axis="y", which="major", alpha=0.2, zorder=0)

        if col_i == 0:
            ax_bot.set_ylabel("Finnish wood biomass  (TWh/y)", fontsize=9.5)
        else:
            ax_bot.set_yticklabels([])

    # ─── LEGENDS (right side) ─────────────────────────────────────────────
    # Panel A: energy carriers
    carrier_handles = [
        mpatches.Patch(facecolor=CARRIER_COLORS[c], label=c)
        for c in CARRIER_ORDER
    ]
    cost_note = mpatches.Patch(
        facecolor="none", edgecolor="none",
        label="Top of bar: GHG (Mt CO₂)\nBar base: cost M€ (Δ vs S2 BAU ref.)",
    )
    leg_a = fig.legend(
        handles=carrier_handles + [cost_note],
        loc="upper left", bbox_to_anchor=(0.833, 0.91),
        fontsize=8.5, framealpha=0.97,
        title="a–c  Primary energy carriers", title_fontsize=9,
        ncol=1, borderpad=0.8,
    )

    # Panel B: biomass tiers + availability lines
    tier_handles = [
        mpatches.Patch(facecolor=TIER_COLORS[t], label=TIER_LABELS[t])
        for t in TIER_ORDER if t != "WOOD_FI5"
    ]
    avail_handles = [
        Line2D([0], [0], ls=ls, lw=1.4, color=lc, alpha=0.75, label=lbl)
        for ls, lc, lbl in AVAIL_STYLES
    ]
    fig.legend(
        handles=tier_handles + [mpatches.Patch(facecolor="none", edgecolor="none", label="")] + avail_handles,
        loc="lower left", bbox_to_anchor=(0.833, 0.06),
        fontsize=8.5, framealpha=0.97,
        title="d–f  Finnish biomass tiers\n   & availability limits", title_fontsize=9,
        ncol=1, borderpad=0.8,
    )

    # ─── PANEL LABELS a)–f) ───────────────────────────────────────────────
    panel_labels = ["a)", "b)", "c)", "d)", "e)", "f)"]
    all_axes = axes_top + axes_bot
    for ax, lbl in zip(all_axes, panel_labels):
        ax.annotate(
            lbl, xy=(0.015, 0.975), xycoords="axes fraction",
            fontsize=11, fontweight="bold", color="#1a252f",
            ha="left", va="top",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.75),
        )

    # ─── FIGURE TITLE ─────────────────────────────────────────────────────
    fig.suptitle(
        "Finland 2035 — Energy mix & biomass supply ladder\n"
        "under forest biodiversity policy  ×  GHG reduction ambition",
        fontsize=13.5, fontweight="bold", y=0.98,
        color="#1a252f",
    )

    # ─── SAVE ─────────────────────────────────────────────────────────────
    outpath = OUT_DIR / "forest_scenarios_2035_energy_matrix.png"
    fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Saved → {outpath}")

    # 4. Biomass allocation figure (Colla Fig. 4 style)
    plot_biomass_allocation(data)


def plot_biomass_allocation(data: dict) -> None:
    """
    Colla Fig. 4 equivalent: biomass allocation by final use.

    Layout: single panel, X = 3 GHG groups, within each group 3 bars
    (S1-BES | S2-NFS | S3-BDS), stacked by final-use category.
    Highlights the constant NED demand and the 95%-GHG mobility fuel surge.
    """
    scen_keys  = list(SCENARIOS.keys())
    n_scen     = len(scen_keys)
    bar_w      = 0.22
    group_gap  = 0.85          # distance between GHG groups
    x_groups   = np.arange(len(GHG_TARGETS)) * group_gap
    offsets    = np.linspace(-(n_scen - 1) / 2, (n_scen - 1) / 2, n_scen) * bar_w

    fig, ax = plt.subplots(figsize=(12, 7.5))
    ax.set_facecolor("#fafafa")

    scen_hatch = {"S1_BES": None, "S2_NFS": "....", "S3_BDS": "xxxx"}

    for si, scen_key in enumerate(scen_keys):
        scen_info = SCENARIOS[scen_key]
        x_bars    = x_groups + offsets[si]
        bottoms   = np.zeros(len(GHG_TARGETS))

        for cat in ALLOC_ORDER:
            vals = np.array([
                data.get((scen_key, ghg), {}).get("alloc", {}).get(cat, 0.0)
                for ghg in GHG_TARGETS
            ])
            if vals.max() < 0.1:
                continue

            hatch = ALLOC_HATCHES.get(cat, None)
            ax.bar(
                x_bars, vals, bar_w, bottom=bottoms,
                color=ALLOC_COLORS[cat],
                hatch=hatch,
                edgecolor="white" if hatch is None else "#555555",
                linewidth=0.4,
                label=cat,
                zorder=3,
            )
            bottoms += vals

        # Scenario border: thin colored edge on each bar group
        for i, (xb, ghg) in enumerate(zip(x_bars, GHG_TARGETS)):
            total = bottoms[i]
            ax.bar(
                xb, total, bar_w,
                fill=False,
                edgecolor=scen_info["color"],
                linewidth=1.5,
                zorder=4,
            )

        # Total label above each bar
        for i, (xb, ghg) in enumerate(zip(x_bars, GHG_TARGETS)):
            key = (scen_key, ghg)
            if key in data:
                tot = sum(data[key]["alloc"].values())
                ax.annotate(
                    f"{tot:.1f}",
                    xy=(xb, bottoms[i] + 0.8),
                    ha="center", va="bottom",
                    fontsize=7.5, color=scen_info["color"], fontweight="bold",
                )

    # ── X-axis labels with GHG group and scenario sub-labels ──────────────
    ax.set_xticks(x_groups)
    ax.set_xticklabels(GHG_LABELS, fontsize=11, fontweight="bold")

    # Scenario legend below each group (one tick-mark set per scenario offset)
    for si, scen_key in enumerate(scen_keys):
        scen_info = SCENARIOS[scen_key]
        for gi, xg in enumerate(x_groups):
            ax.annotate(
                scen_info["short"],
                xy=(xg + offsets[si], -4.5),
                ha="center", va="top",
                fontsize=7, color=scen_info["color"],
                fontweight="bold",
                annotation_clip=False,
            )

    # ── Y axis ────────────────────────────────────────────────────────────
    ax.set_ylim(0, 100)
    ax.set_ylabel("Biomass used  (TWh/y)", fontsize=11)
    ax.grid(axis="y", alpha=0.25, zorder=0)
    ax.set_xlim(x_groups[0] - 0.55, x_groups[-1] + 0.55)

    # ── Constant NED reference line ────────────────────────────────────────
    ned_val = 28.7   # always constant across all 9 runs
    ax.axhline(
        ned_val, color="#888888", ls="--", lw=1.2, zorder=2,
        label=f"NED/chemicals floor  ({ned_val} TWh, constant)",
    )
    ax.annotate(
        f"← NED floor: {ned_val} TWh (invariant)", color="#666666",
        xy=(x_groups[-1] + 0.45, ned_val + 0.8), fontsize=8, ha="right",
    )

    # ── Legend ─────────────────────────────────────────────────────────────
    # De-duplicate legend entries (matplotlib auto-duplicates from looped bars)
    seen = set()
    handles, labels = [], []
    for h, lbl in zip(*ax.get_legend_handles_labels()):
        if lbl not in seen and lbl in ALLOC_ORDER + [
            f"NED/chemicals floor  ({ned_val} TWh, constant)"
        ]:
            seen.add(lbl)
            handles.append(h)
            labels.append(lbl)

    ax.legend(
        handles, labels,
        loc="upper left", bbox_to_anchor=(0.01, 0.99),
        fontsize=8.5, framealpha=0.95, ncol=2,
        title="Biomass final use", title_fontsize=9,
    )

    # Scenario colour patch legend (top right)
    scen_handles = [
        mpatches.Patch(
            facecolor="white", edgecolor=SCENARIOS[s]["color"],
            linewidth=2, label=SCENARIOS[s]["short"],
        )
        for s in scen_keys
    ]
    ax.legend(
        scen_handles,
        [SCENARIOS[s]["short"] for s in scen_keys],
        loc="upper right", bbox_to_anchor=(0.99, 0.99),
        fontsize=9, framealpha=0.95, title="Forest scenario\n(bar border colour)",
        title_fontsize=8.5,
    )
    # Re-add full legend (categories) on top
    ax.add_artist(ax.get_legend())   # keep scenario legend
    leg2 = ax.legend(
        handles, labels,
        loc="upper left", bbox_to_anchor=(0.01, 0.99),
        fontsize=8, framealpha=0.95, ncol=1,
        title="Biomass final use", title_fontsize=9,
    )

    # ── Title ──────────────────────────────────────────────────────────────
    ax.set_title(
        "Finland 2035 — Biomass allocation by final use\n"
        "forest biodiversity policy  ×  GHG reduction ambition  (inspired by Colla et al. 2022, Fig. 4)",
        fontsize=11.5, fontweight="bold", color="#1a252f",
    )

    outpath = OUT_DIR / "forest_scenarios_2035_biomass_allocation.png"
    fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Saved → {outpath}")


if __name__ == "__main__":
    main()
