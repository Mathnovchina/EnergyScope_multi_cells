"""
Presentation-ready matrix of old (pre-supply-curve) biomass resources — Finland 2035 model.
16:9 slide format, large fonts, data values in each cell.
"""

import os
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams["font.family"] = "DejaVu Sans"

OUTPUT_DIR = r"Data/exogenous_data/Mypaper"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Resources ────────────────────────────────────────────────────────────────
RESOURCES = [
    ("WOOD",             "Forest wood biomass"),
    ("WET_BIOMASS",      "Wet biomass\n(manure, sludge, slurry)"),
    ("ENERGY_CROPS_2",   "Dedicated energy crops\n(perennial grasses, coppice)"),
    ("BIOMASS_RESIDUES", "Agricultural residues\n(straw, stover)"),
    ("BIOWASTE",         "Organic municipal waste\n(food scraps, garden waste)"),
    ("WASTE",            "Mixed municipal solid waste\n(incl. fossil fraction)"),
]

# ─── Parameters (English name, model code, unit) ─────────────────────────────
PARAMS = [
    ("Domestic\navailability",          "avail_local",    "GWh / year"),
    ("Marginal\nsupply cost",           "c_op_local",     "€ / MWh"),
    ("Supply-chain\nGHG emissions",     "gwp_op_local",   "ktCO₂-eq / GWh"),
    ("Direct combustion\nCO₂",         "co2_net",         "ktCO₂-eq / GWh"),
    ("Import option\n(annual cap)",     "avail_exterior", "GWh / year"),
]

# ─── Cell data: (main value string, sub annotation) ───────────────────────────
#     Columns:  avail_local | c_op_local | gwp_op_local | co2_net | avail_exterior
DATA = [
    # WOOD
    [("110 806",    "GWh / year"),
     ("22.1",       "€ / MWh"),
     ("0.0246",     "ktCO₂-eq / GWh"),
     ("0",          "biogenic → C neutral"),
     ("0",          "no import market")],
    # WET_BIOMASS
    [("1 451",      "GWh / year"),
     ("33.1",       "€ / MWh"),
     ("0.0106",     "ktCO₂-eq / GWh"),
     ("0",          "biogenic → C neutral"),
     ("0",          "no import market")],
    # ENERGY_CROPS_2
    [("7 754",      "GWh / year"),
     ("23.5",       "€ / MWh"),
     ("0.0076",     "ktCO₂-eq / GWh"),
     ("0",          "biogenic → C neutral"),
     ("0",          "no import market")],
    # BIOMASS_RESIDUES
    [("4 985",      "GWh / year"),
     ("13.1",       "€ / MWh"),
     ("0.0032",     "ktCO₂-eq / GWh"),
     ("0",          "biogenic → C neutral"),
     ("0",          "no import market")],
    # BIOWASTE
    [("4 721",      "GWh / year"),
     ("0.1",        "€ / MWh  (gate-fee)"),
     ("0.0149",     "ktCO₂-eq / GWh"),
     ("0",          "biogenic → C neutral"),
     ("0",          "no import market")],
    # WASTE
    [("11 095",     "GWh / year"),
     ("6.1",        "€ / MWh  (gate-fee)"),
     ("0.150",      "ktCO₂-eq / GWh"),
     ("0.260",      "fossil fraction ⚠"),
     ("0",          "no import market")],
]

# ─── Colours ──────────────────────────────────────────────────────────────────
C_TITLE   = "#1a1a2e"
C_ROW_HDR = "#264653"
C_COL_HDR = "#2d6a4f"
C_CELL    = "#f8f9fa"
C_CELL_BD = "#ced4da"
C_CODE    = "#e9c46a"
C_UNIT    = "#90e0ef"

# ─── Layout  (16:9, slide-sized) ─────────────────────────────────────────────
FW, FH   = 22, 12.375       # inches — true 16:9 at 96 dpi → 2112 × 1188 px
PAD      = 0.20
TITLE_H  = 0.70

NR = len(RESOURCES)
NC = len(PARAMS)

LABEL_W  = 4.00             # resource-name column
TOTAL_W  = FW - 2 * PAD
PARAM_W  = (TOTAL_W - LABEL_W) / NC

HDR_H    = 1.60             # parameter-header row
BODY_H   = FH - 2 * PAD - TITLE_H - HDR_H
ROW_H    = BODY_H / NR      # ≈ 1.47

GRID_TOP = FH - PAD - TITLE_H
HDR_BOT  = GRID_TOP - HDR_H
X0       = PAD

GAP = 0.07

# ─── Figure ───────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(FW, FH), facecolor="white")
ax  = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis("off")

def rbox(ax, x, y, w, h, fc, ec="none", lw=0, r=0.12):
    ax.add_patch(FancyBboxPatch(
        (x + GAP, y + GAP), w - 2*GAP, h - 2*GAP,
        boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2
    ))

# ── Title ─────────────────────────────────────────────────────────────────────
rbox(ax, PAD, FH - PAD - TITLE_H, TOTAL_W, TITLE_H, C_TITLE, r=0.15)
ax.text(FW / 2, FH - PAD - TITLE_H / 2,
        "Biomass resources — characterisation parameters  (Finland 2035, pre-supply-curve)",
        ha="center", va="center", fontsize=22, fontweight="bold",
        color="white", zorder=3)

# ── Corner cell ───────────────────────────────────────────────────────────────
rbox(ax, X0, HDR_BOT, LABEL_W, HDR_H, C_TITLE, r=0.12)
ax.text(X0 + LABEL_W / 2, HDR_BOT + HDR_H / 2,
        "Resource", ha="center", va="center",
        fontsize=19, fontweight="bold", color="white", zorder=3)

# ── Parameter header cells ────────────────────────────────────────────────────
for j, (name, code, unit) in enumerate(PARAMS):
    x = X0 + LABEL_W + j * PARAM_W
    rbox(ax, x, HDR_BOT, PARAM_W, HDR_H, C_COL_HDR, r=0.12)
    ax.text(x + PARAM_W / 2, HDR_BOT + HDR_H * 0.68, name,
            ha="center", va="center", fontsize=15, fontweight="bold",
            color="white", linespacing=1.45, zorder=3)
    ax.text(x + PARAM_W / 2, HDR_BOT + HDR_H * 0.30, code,
            ha="center", va="center", fontsize=13,
            color=C_UNIT, style="italic", zorder=3)
    ax.text(x + PARAM_W / 2, HDR_BOT + HDR_H * 0.10, f"[{unit}]",
            ha="center", va="center", fontsize=11,
            color="#b0e0e6", style="italic", zorder=3)

# ── Resource rows ─────────────────────────────────────────────────────────────
for i, (code, desc) in enumerate(RESOURCES):
    y = HDR_BOT - (i + 1) * ROW_H

    # alternating row stripe for readability
    stripe_color = "#eaf2f0" if i % 2 == 0 else "white"
    ax.add_patch(FancyBboxPatch(
        (X0, y), TOTAL_W, ROW_H,
        boxstyle="round,pad=0,rounding_size=0",
        facecolor=stripe_color, edgecolor="none", zorder=1
    ))

    # Resource-name card
    rbox(ax, X0, y, LABEL_W, ROW_H, C_ROW_HDR, r=0.10)
    ax.text(X0 + LABEL_W / 2, y + ROW_H * 0.70, code,
            ha="center", va="center", fontsize=15, fontweight="bold",
            color=C_CODE, family="monospace", zorder=3)
    ax.text(X0 + LABEL_W / 2, y + ROW_H * 0.28, desc,
            ha="center", va="center", fontsize=12, color="#a8dadc",
            linespacing=1.4, zorder=3)

    # Data cells
    for j in range(NC):
        x = X0 + LABEL_W + j * PARAM_W
        if i == 5 and j == 3:          # WASTE co2_net — red highlight
            cell_bg = "#fde8ea"
        elif j == 4:                   # imports column — grey
            cell_bg = "#ececec"
        else:
            cell_bg = C_CELL
        rbox(ax, x, y, PARAM_W, ROW_H, cell_bg, ec=C_CELL_BD, lw=0.9, r=0.09)

        val, sub = DATA[i][j]
        val_color = "#1a1a2e" if val != "0" else "#888888"
        sub_color = "#c0392b" if "⚠" in sub else "#888888"

        ax.text(x + PARAM_W / 2, y + ROW_H * 0.63, val,
                ha="center", va="center", fontsize=18, fontweight="bold",
                color=val_color, zorder=3)
        ax.text(x + PARAM_W / 2, y + ROW_H * 0.24, sub,
                ha="center", va="center", fontsize=11,
                color=sub_color, style="italic", zorder=3)

# ─── Save ─────────────────────────────────────────────────────────────────────
for ext in ("png", "pdf"):
    out = os.path.join(OUTPUT_DIR, f"old_biomass_parameters_visual.{ext}")
    kw = dict(bbox_inches="tight", facecolor="white")
    if ext == "png":
        kw["dpi"] = 150
    plt.savefig(out, **kw)
    print(f"Saved: {out}")

plt.close()
