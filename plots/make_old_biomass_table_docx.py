# -*- coding: utf-8 -*-
"""
Generate a Word document summarising the OLD biomass resource categories
(Finland 2035, before the WOOD -> WOOD_FI1..5 supply-curve split).

Values are read from the model input files:
  - Data/2035/FI/Resources.csv (FI override at commit HEAD~40, pre-split):
        avail_local, c_op_local
  - Data/2035/02_REF_REGION/Resources.csv:
        avail_exterior, gwp_op_local (direct+indirect, local)
  - Data/2035/00_INDEP/Resources_indep.csv:
        gwp_op_exterior (direct+indirect, exterior), c_op_exterior (price exterior),
        co2_net (direct combustion emissions)
"""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "Data", "exogenous_data", "Mypaper",
                   "old_biomass_categories_FI2035.docx")

# ---------------------------------------------------------------------------
# Old biomass categories (pre-split). Values transcribed from the model files.
#   avail_local [GWh/y]            <- FI/Resources.csv (pre-split, HEAD~40)
#   c_op_local  [Meuro/GWh]        <- FI/Resources.csv (pre-split)
#   gwp_op_local [ktCO2-eq/GWh]    <- 02_REF_REGION/Resources.csv (direct+indirect, local)
#   co2_net      [ktCO2-eq/GWh]    <- 00_INDEP/Resources_indep.csv (direct combustion)
#   avail_ext   [GWh/y]            <- 02_REF_REGION/Resources.csv (exterior availability)
#   c_op_ext    [Meuro/GWh]        <- 00_INDEP/Resources_indep.csv (price of exterior)
#   gwp_op_ext  [ktCO2-eq/GWh]     <- 00_INDEP/Resources_indep.csv (direct+indirect, exterior)
# ---------------------------------------------------------------------------
rows = [
    # name, avail_local, c_op_local, gwp_op_local, co2_net, avail_ext, c_op_ext, gwp_op_ext
    ("WOOD",             110805.66, 0.022084, 0.02456, 0.0, 0.0, 0.0,        0.02456),
    ("WET_BIOMASS",        1450.62, 0.033104, 0.01056, 0.0, 0.0, 0.0,        0.01056),
    ("ENERGY_CROPS_2",     7754.11, 0.023524, 0.00756, 0.0, 0.0, 0.0,        0.00756),
    ("BIOMASS_RESIDUES",   4985.24, 0.013135, 0.00324, 0.0, 0.0, 0.0,        0.00324),
    ("BIOWASTE",           4720.94, 0.000112, 0.01488, 0.0, 0.0, 0.0,        0.01488),
    ("WASTE",             11095.02, 0.006079, 0.15010, 0.26, 0.0, 0.023081,  0.15010),
]

definitions = [
    ("WOOD",
     "Lignocellulosic woody biomass. Forest-origin products and residues: pulp/sawmill "
     "by-products (black liquor, bark, sawdust), logging residues (branches, tops, stumps), "
     "secondary woodchips, direct fuelwood and landscape-care wood. Feeds the WOOD layer "
     "(boilers, CHP, gasification, wood-to-fuels). ENSPRESO codes MINBIOWOOa + MINBIOFRSR1 + "
     "MINBIOWOOW1(+a) + MINBIOWOO + MINBIOFRSR1a. *** This is the single resource later split "
     "into WOOD_FI1..WOOD_FI5. ***"),
    ("WET_BIOMASS",
     "Wet organic biomass (sewage sludge, manure, wet organic waste) used by anaerobic "
     "digestion / biomethanation to produce GAS. ENSPRESO code MINBIOSLU1 (sludge). "
     "Feeds the WET_BIOMASS layer."),
    ("ENERGY_CROPS_2",
     "Lignocellulosic energy crops grown on dedicated land: miscanthus, switchgrass and "
     "short-rotation coppice (willow). ENSPRESO codes MINBIOCRP31 + MINBIOCRP41. "
     "Not affected by forest-management policy."),
    ("BIOMASS_RESIDUES",
     "Agricultural residues (cereal straw, stover) - NOT forest residues. ENSPRESO code "
     "MINBIOAGRW1. Feeds the BIOWASTE layer. Independent of forest management; this is the "
     "category that is sometimes confused with logging residues (which are inside WOOD)."),
    ("BIOWASTE",
     "Biodegradable municipal and organic waste directed to energy recovery (anaerobic "
     "digestion / biowaste streams). ENSPRESO code MINBIOMUN1. Feeds the BIOWASTE layer."),
    ("WASTE",
     "Municipal solid waste for incineration (non-biogenic fraction). Classified as "
     "'Other non-renewable' rather than biomass: it carries non-zero DIRECT combustion CO2 "
     "(0.26 ktCO2-eq/GWh). Included here for completeness. Feeds the WASTE layer."),
]

# ---------------------------------------------------------------------------
doc = Document()

style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10)

h = doc.add_heading("Old biomass resource categories — Finland 2035", level=1)

p = doc.add_paragraph()
p.add_run("Reference configuration BEFORE the WOOD supply-curve split "
          "(single WOOD resource). ").bold = True
p.add_run("Use this as the 'before' state to explain the change to the stepwise "
          "WOOD_FI1..WOOD_FI5 ladder.")

# Provenance note
pv = doc.add_paragraph()
pv.add_run("Parameter provenance (three input files): ").bold = True
doc.add_paragraph(
    "avail_local, c_op_local  ->  Data/2035/FI/Resources.csv  (region-specific override)",
    style="List Bullet")
doc.add_paragraph(
    "avail_exterior, gwp_op_local (direct+indirect, local)  ->  Data/2035/02_REF_REGION/Resources.csv",
    style="List Bullet")
doc.add_paragraph(
    "c_op_exterior (price of exterior), gwp_op_exterior (direct+indirect, exterior), "
    "co2_net (direct emissions)  ->  Data/2035/00_INDEP/Resources_indep.csv",
    style="List Bullet")

# ---- Main parameter table -------------------------------------------------
doc.add_heading("Parameters and units", level=2)

headers = [
    "Resource",
    "avail_local\n[GWh/y]",
    "c_op_local\n[Meuro/GWh]\n(= EUR/MWh)",
    "gwp_op_local\ndirect+indirect\n[ktCO2-eq/GWh]",
    "co2_net\ndirect\n[ktCO2-eq/GWh]",
    "avail_exterior\n[GWh/y]",
    "c_op_exterior\nprice exterior\n[Meuro/GWh]",
    "gwp_op_exterior\ndirect+indirect\n[ktCO2-eq/GWh]",
]

table = doc.add_table(rows=1, cols=len(headers))
table.style = "Light Grid Accent 1"
table.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr = table.rows[0].cells
for i, t in enumerate(headers):
    hdr[i].text = t
    for par in hdr[i].paragraphs:
        for run in par.runs:
            run.font.bold = True
            run.font.size = Pt(8)

def fmt(v, dec):
    return f"{v:,.{dec}f}"

for (name, al, col, gl, co2, ae, ce, ge) in rows:
    c = table.add_row().cells
    eur_mwh = col * 1000.0  # Meuro/GWh -> EUR/MWh
    c[0].text = name
    c[1].text = fmt(al, 1)
    c[2].text = f"{col:.6f}\n({eur_mwh:.2f})"
    c[3].text = f"{gl:.5f}"
    c[4].text = f"{co2:.3f}"
    c[5].text = fmt(ae, 1)
    c[6].text = f"{ce:.6f}"
    c[7].text = f"{ge:.5f}"
    for ci, cell in enumerate(c):
        for par in cell.paragraphs:
            par.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            for run in par.runs:
                run.font.size = Pt(8.5)

note = doc.add_paragraph()
note.add_run("Notes: ").bold = True
note.add_run(
    "(1) All domestic biomass has avail_exterior = 0, so imports are disabled and the "
    "exterior price/emission columns are not actually used by the optimiser (shown for "
    "completeness). (2) c_op_local is the marginal supply cost; 1 Meuro/GWh = 1000 EUR/MWh. "
    "(3) Biomass direct combustion CO2 (co2_net) is 0 because biogenic carbon is treated as "
    "neutral; only WASTE carries a non-zero direct factor. (4) gwp_op_local captures the "
    "supply-chain (harvesting, processing, transport) life-cycle emissions.")

# ---- Definitions ----------------------------------------------------------
doc.add_heading("Definition of each category", level=2)

dt = doc.add_table(rows=1, cols=2)
dt.style = "Light Grid Accent 1"
dt.columns[0].width = Inches(1.4)
dt.columns[1].width = Inches(5.4)
dh = dt.rows[0].cells
dh[0].text = "Resource"
dh[1].text = "Physical definition"
for cell in dh:
    for par in cell.paragraphs:
        for run in par.runs:
            run.font.bold = True

for name, desc in definitions:
    c = dt.add_row().cells
    c[0].text = name
    c[1].text = desc
    for run in c[0].paragraphs[0].runs:
        run.font.bold = True
    for cell in c:
        for par in cell.paragraphs:
            for run in par.runs:
                run.font.size = Pt(9)

doc.save(OUT)
print("Saved:", OUT)
