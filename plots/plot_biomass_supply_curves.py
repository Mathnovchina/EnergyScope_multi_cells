# -*- coding: utf-8 -*-
"""
Finnish Wood Biomass Supply Curves \u2014 Finland 2035
Three scenarios: S1-BES, S2-NFS, S3-BDS
Data read directly from Data/2035/FI/Resources_S*.csv
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
X_MAX = 148   # chart right edge (TWh); backstop lines extend to here

# ── Load data from CSVs ──────────────────────────────────────────────────────
def load_scenario(filepath):
    """Return dict {resource: (avail_GWh, c_op_EUR_per_kWh)}"""
    df = pd.read_csv(filepath, index_col=0)
    df.columns = ["avail", "c_op"]
    return {name: (float(row["avail"]), float(row["c_op"])) for name, row in df.iterrows()}

scenarios = {
    "S1-BES":  load_scenario(os.path.join(BASE, "Data/2035/FI/Resources_S1_BES.csv")),
    "S2-NFS":  load_scenario(os.path.join(BASE, "Data/2035/FI/Resources_S2_NFS.csv")),
    "S3-BDS":  load_scenario(os.path.join(BASE, "Data/2035/FI/Resources_S3_BDS.csv")),
}

STEP_KEYS = ["WOOD_FI1", "WOOD_FI2", "WOOD_FI3", "WOOD_FI4", "WOOD_FI5"]
STEP_LABELS = [
    "Step 1: Industrial by-products\n(black liquor, bark, sawdust)",
    "Step 2: Logging residues\n(branches, tops — MINBIOFRSR1)",
    "Step 3: Secondary woodchips\n(MINBIOWOOW1 + W1a)",
    "Step 4: Fuelwood & landscape\n(MINBIOWOO + FRSR1a)",
    "Step 5: Baltic/Nordic imports\n(unlimited backstop)",
]

SC_STYLE = {
    "S1-BES": {"color": "#a04000", "lw": 2.4, "label": "S1 - BES: stylised high-mobilisation case"},
    "S2-NFS": {"color": "#4a4a4a", "lw": 2.4, "label": "S2 - NFS: ENSPRESO-medium reference"},
    "S3-BDS": {"color": "#1e6b3c", "lw": 2.4, "label": "S3 - BDS: conservative biodiversity case"},
}

# Step background shading colours (very light)
STEP_BG = ["#f9f2d8", "#e8f4fb", "#edfbea", "#fdf0e8", "#f5eef8"]

# ── Build staircase segments ─────────────────────────────────────────────────
def build_staircase(sc_data, keys):
    """
    Returns (xs, ys, cumulative_domestic_TWh, list_of_step_spans).
    Backstop step extends to X_MAX so the line reaches the right chart edge.
    """
    xs, ys = [], []
    spans = []
    cum = 0.0
    prev_c = None
    for i, k in enumerate(keys):
        avail_ghw, c_op_kwh = sc_data[k]
        c_mwh = c_op_kwh * 1000.0          # EUR/kWh \u2192 EUR/MWh
        is_backstop = (avail_ghw >= 500_000)
        width = (X_MAX - cum) if is_backstop else avail_ghw / 1000.0

        if prev_c is not None:
            xs += [cum, cum]
            ys += [prev_c, c_mwh]
        xs += [cum, cum + width]
        ys += [c_mwh, c_mwh]
        spans.append((cum, cum + width, c_mwh, is_backstop))
        cum = cum + width
        prev_c = c_mwh

    domestic = sum(sc_data[k][0] for k in keys if sc_data[k][0] < 500_000) / 1000.0
    return xs, ys, domestic, spans


# ── Figure layout: single main panel ─────────────────────────────────────────
fig = plt.figure(figsize=(13.2, 6.6))
ax_main = fig.add_axes([0.08, 0.12, 0.84, 0.80])

# ── Compute all staircases ───────────────────────────────────────────────────
all_data = {}
for sc_name, sc_data in scenarios.items():
    xs, ys, dom, spans = build_staircase(sc_data, STEP_KEYS)
    all_data[sc_name] = {"xs": xs, "ys": ys, "dom": dom, "spans": spans}

# ── Step background bands on main panel (S2-NFS positions as reference) ─────
ref_spans = all_data["S2-NFS"]["spans"]
for i, (xl, xr, c_mwh, backstop) in enumerate(ref_spans):
    ax_main.axvspan(xl, xr, alpha=0.07, color=STEP_BG[i],
                    ymin=0, ymax=1, zorder=0)

# ── Draw staircases ──────────────────────────────────────────────────────────
dom_offsets = {"S1-BES": 2.5, "S2-NFS": 0, "S3-BDS": -2.5}
for sc_name, style in SC_STYLE.items():
    d = all_data[sc_name]
    ax_main.plot(d["xs"], d["ys"], color=style["color"], lw=style["lw"],
                 label=style["label"], solid_capstyle="butt")
    # Domestic ceiling dashed line
    ax_main.axvline(d["dom"], color=style["color"], lw=0.9, ls="--", alpha=0.4)
    ax_main.text(d["dom"] - 0.6, 4 + dom_offsets[sc_name],
                 f'{d["dom"]:.0f} TWh', color=style["color"],
                 fontsize=8, ha="right", rotation=90, va="bottom")

# Right-edge arrow to indicate backstop is unlimited
ax_main.annotate(
    "", xy=(X_MAX + 0.5, 70), xytext=(X_MAX - 5, 70),
    arrowprops=dict(arrowstyle="-|>", color="#888", lw=1.3, mutation_scale=12),
    annotation_clip=False,
)
ax_main.text(X_MAX + 1, 70, "unlimited", fontsize=8, color="#888",
             va="center", ha="left", clip_on=False)

ax_main.set_xlim(-2, X_MAX)
ax_main.set_ylim(0, 78)
ax_main.set_xticks(range(0, X_MAX, 10))
ax_main.set_xlabel("Cumulative available supply (TWh/yr)", fontsize=11)
ax_main.set_ylabel("Marginal supply cost (€/MWh)", fontsize=11)
ax_main.set_title(
    "Finnish Forest-Biomass Supply Curves for 2035\n"
    "S1 BES | S2 NFS | S3 BDS",
    fontsize=11,
)
ax_main.legend(
    loc="center right",
    fontsize=9.3,
    framealpha=0.95,
    bbox_to_anchor=(0.985, 0.56),
    borderaxespad=0.3,
    title="Forest scenario",
    title_fontsize=9.5,
)
ax_main.grid(True, alpha=0.22, ls=":")

# Panel label
ax_main.annotate("a)", xy=(0.015, 0.975), xycoords="axes fraction",
                 fontsize=12, fontweight="bold", color="#1a252f",
                 ha="left", va="top",
                 bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                           edgecolor="none", alpha=0.75))

# Backstop label
ax_main.text(84, 67.5, "Baltic/Nordic import backstop (70 €/MWh)",
             fontsize=8.5, color="#555")

# ── Save ─────────────────────────────────────────────────────────────────────
out_base = os.path.join(BASE, "plots", "biomass_supply_curves_fi_2035")
for ext, kwargs in {
    "png": {"dpi": 160},
    "pdf": {},
}.items():
    out = f"{out_base}.{ext}"
    plt.savefig(out, bbox_inches="tight", **kwargs)
    print(f"Saved: {out}")
