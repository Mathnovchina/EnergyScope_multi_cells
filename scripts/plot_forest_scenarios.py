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
        "label":  "S1 — High potential\nBioeconomy strategy",
        "short":  "S1 — High potential",
        "abbr":   "S1",
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
        "label":  "S2 — Reference\nPolicy-trend baseline",
        "short":  "S2 — Reference",
        "abbr":   "S2",
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
        "label":  "S3 — Low potential\nBiodiversity-first",
        "short":  "S3 — Low potential",
        "abbr":   "S3",
        "color":  "#1e6b3c",          # forest green (biodiversity-first)
        "bg":     "#eafaf1",          # very light green background
        "avail_gwh": {
            "FI1": 32000,
            "FI2": 32000 + 6000,
            "FI3": 32000 + 6000 + 1500,
            "FI4": 32000 + 6000 + 1500 + 500,
        },
    },
}

GHG_TARGETS = ["unconstrained", "ghg_95pct", "ghg_95pct_nonuke"]
GHG_LABELS  = ["Unconstrained", "−95% GHG\n(with nuclear)", "−95% GHG\n(nuclear phase-out)"]

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
    ("-",  "#1a7a2e", "Availability cap after FI-1"),
    ("--", "#74c476", "Availability cap after FI-1+2"),
    ("-.", "#d4a017", "Availability cap after FI-1+2+3"),
    (":",  "#c0392b", "Availability cap after FI-1+2+3+4"),
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
    fig = plt.figure(figsize=(18, 10.6))
    gs  = fig.add_gridspec(
        2, 3,
        height_ratios=[2.5, 1.2],
        hspace=0.32, wspace=0.10,
        left=0.07, right=0.82, top=0.88, bottom=0.08,
    )
    axes_top = [fig.add_subplot(gs[0, c]) for c in range(3)]
    axes_bot = [fig.add_subplot(gs[1, c]) for c in range(3)]

    bar_w   = 0.55
    x       = np.arange(len(GHG_TARGETS))
    scen_keys = list(SCENARIOS.keys())

    # Shared Y ranges
    y_top_max = 330
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

        ax_bot.text(
            0.11, 0.95,
            "Wood used by supply tier\n(lines = cumulative domestic caps)",
            transform=ax_bot.transAxes,
            ha="left", va="top",
            fontsize=8.2, color="#34495e",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.8),
            zorder=5,
        )

        top_box = ax_top.get_position()
        bot_box = ax_bot.get_position()
        fig.text(
            (top_box.x0 + top_box.x1) / 2,
            (top_box.y0 + bot_box.y1) / 2,
            scen_info["label"].replace("\n", "  ·  "),
            ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="white",
            bbox=dict(
                boxstyle="round,pad=0.28", facecolor=scen_info["color"],
                edgecolor="none", alpha=0.92,
            ),
        )

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
        title="Bottom row: wood tiers used\nand availability caps", title_fontsize=9,
        ncol=1, borderpad=0.8,
    )

    # ─── PANEL LABELS a)–f) ───────────────────────────────────────────────
    panel_labels = ["a)", "b)", "c)", "d)", "e)", "f)"]
    all_axes = axes_top + axes_bot
    for ax, lbl in zip(all_axes, panel_labels):
        ax.annotate(
            lbl,
            xy=(0.015, 0.88 if ax in axes_top else 0.975),
            xycoords="axes fraction",
            fontsize=11, fontweight="bold", color="#1a252f",
            ha="left", va="top",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.75),
        )

    # ─── FIGURE TITLE ─────────────────────────────────────────────────────
    fig.suptitle(
        "Finland 2035 — Energy mix & biomass supply ladder\n"
        "under different forest management intensity  ×  GHG reduction ambition",
        fontsize=13.5, fontweight="bold", y=0.965,
        color="#1a252f",
    )

    # ─── SAVE ─────────────────────────────────────────────────────────────
    for suffix, kwargs in {
        ".png": {"dpi": 200},
        ".pdf": {},
    }.items():
        outpath = OUT_DIR / f"forest_scenarios_2035_energy_matrix{suffix}"
        fig.savefig(outpath, bbox_inches="tight", facecolor="white", **kwargs)
        print(f"  Saved → {outpath}")
    plt.close()

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
    bar_w      = 0.24
    group_gap  = 1.45          # distance between GHG groups
    x_groups   = np.arange(len(GHG_TARGETS)) * group_gap
    offsets    = np.array([-bar_w * 1.15, 0.0, bar_w * 1.15])

    fig, ax = plt.subplots(figsize=(14.6, 7.9))
    fig.subplots_adjust(left=0.08, right=0.72, top=0.84, bottom=0.14)
    ax.set_facecolor("#fafafa")

    for gi, xg in enumerate(x_groups):
        ax.axvspan(xg - 0.48, xg + 0.48, color="#f5f7f8" if gi % 2 == 0 else "#eef4f7", alpha=0.85, zorder=0)

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

    # ── X-axis labels: each bar gets S1 / S2 / S3, group title stays above ─
    bar_positions = []
    bar_labels = []
    bar_colors = []
    for xg in x_groups:
        for scen_key, offset in zip(scen_keys, offsets):
            bar_positions.append(xg + offset)
            bar_labels.append(SCENARIOS[scen_key]["abbr"])
            bar_colors.append(SCENARIOS[scen_key]["color"])

    ax.set_xticks(bar_positions)
    ax.set_xticklabels(bar_labels, fontsize=10, fontweight="bold")
    for tick_label, tick_color in zip(ax.get_xticklabels(), bar_colors):
        tick_label.set_color(tick_color)

    for gi, xg in enumerate(x_groups):
        ax.annotate(
            GHG_LABELS[gi].replace("\n", " "),
            xy=(xg, 119.5),
            ha="center", va="bottom",
            fontsize=10, fontweight="bold", color="#1a252f",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#d0d7de", alpha=0.95),
        )

    for left, right in zip(x_groups[:-1], x_groups[1:]):
        ax.axvline((left + right) / 2, color="#c9d1d9", lw=1.0, ls=":", zorder=1)

    # ── Y axis ────────────────────────────────────────────────────────────
    ax.set_ylim(0, 128)
    ax.set_ylabel("Biomass used  (TWh/y)", fontsize=11)
    ax.grid(axis="y", alpha=0.25, zorder=0)
    ax.set_xlim(x_groups[0] - 0.72, x_groups[-1] + 0.72)

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

    category_legend = ax.legend(
        handles, labels,
        loc="upper left", bbox_to_anchor=(1.01, 1.00),
        fontsize=8.3, framealpha=0.95, ncol=1,
        title="Final use", title_fontsize=9,
    )

    # Scenario colour patch legend (outside right, below category legend)
    scen_handles = [
        mpatches.Patch(
            facecolor="white", edgecolor=SCENARIOS[s]["color"],
            linewidth=2, label=SCENARIOS[s]["short"],
        )
        for s in scen_keys
    ]
    ax.add_artist(category_legend)
    ax.legend(
        scen_handles,
        [SCENARIOS[s]["short"] for s in scen_keys],
        loc="upper left", bbox_to_anchor=(1.01, 0.43),
        fontsize=9, framealpha=0.95, title="Forest scenario\n(bar border)",
        title_fontsize=8.5,
    )

    # ── Title ──────────────────────────────────────────────────────────────
    ax.set_title(
        "Finland 2035 — Biomass allocation by final use\n"
        "bars grouped by GHG target; S1/S2/S3 identified by coloured borders and x-axis labels",
        fontsize=11.5, fontweight="bold", color="#1a252f",
    )

    for suffix, kwargs in {
        ".png": {"dpi": 200},
        ".pdf": {},
    }.items():
        outpath = OUT_DIR / f"forest_scenarios_2035_biomass_allocation{suffix}"
        fig.savefig(outpath, bbox_inches="tight", facecolor="white", **kwargs)
        print(f"  Saved → {outpath}")
    plt.close()


if __name__ == "__main__":
    main()
