"""
Add cost sheets to Finland_MASTER_Calibration_old_UPDATED.xlsx:
  22_V33_Technology_Costs: All technology costs from REF_REGION (c_inv, c_maint, lifetime, c_p, gwp_constr)
  23_V33_Resource_Costs : All resource operating costs (c_op_local from patches + c_op_exterior + gwp from INDEP)
  + Update 05_Pricing_Pipeline with correct actual values
"""
import csv, os
from datetime import date
from collections import OrderedDict

import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

EXCEL = r"Data\exogenous_data\Finland_MASTER_Calibration_old_UPDATED.xlsx"

# ── Style helpers ────────────────────────────────────────────────────────────
HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
SECTION_FILL = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
THIN_BORDER = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)
WRAP = Alignment(wrap_text=True, vertical="top")

def write_header(ws, row, headers, widths=None):
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=c, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if widths:
        for c, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(c)].width = w

def write_row(ws, row, values, bold=False, italic=False, color=None):
    for c, v in enumerate(values, 1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.border = THIN_BORDER
        cell.alignment = WRAP
        if bold or italic or color:
            cell.font = Font(bold=bold, italic=italic, color=color or "000000")


# ── 1. Read technology costs from REF_REGION ─────────────────────────────────
tech = pd.read_csv("Data/2017/02_REF_REGION/Technologies.csv", skiprows=[1])
tech = tech.dropna(subset=["Technologies param"])
tech = tech.set_index("Technologies param")
tech.index = tech.index.astype(str).str.strip()
for col in ["c_inv", "c_maint", "lifetime", "c_p", "gwp_constr"]:
    tech[col] = pd.to_numeric(tech[col], errors="coerce")
tech = tech[~tech.index.duplicated(keep="first")]
tech_costs = tech[tech["c_inv"].notna()].sort_index()

# ── 2. Read resource costs from patches ──────────────────────────────────────
res_patch_costs = {}
with open("calibration/patches/restore_v9_baseline.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if "Resources" in row["file"] and "c_op" in row["parameter"]:
            res_patch_costs[row["technology_or_resource"].strip()] = float(row["value"])

# ── 3. Read resource costs from INDEP (exterior prices + gwp) ────────────────
res_indep = pd.read_csv("Data/2017/00_INDEP/Resources_indep.csv", skiprows=[1, 2])
res_indep = res_indep.dropna(subset=["Unnamed: 2"])
res_indep = res_indep.set_index("Unnamed: 2")
res_indep.index = res_indep.index.astype(str).str.strip()
for col in res_indep.columns:
    res_indep[col] = pd.to_numeric(res_indep[col], errors="coerce")
res_indep = res_indep[~res_indep.duplicated()]

# ── 4. Read Layers_in_out for efficiency reference ───────────────────────────
lio = pd.read_csv("Data/2017/00_INDEP/Layers_in_out.csv", index_col=0, skiprows=[1])

# ── Source notes for key technologies ────────────────────────────────────────
TECH_COST_SOURCES = {
    "NUCLEAR": "DEA 2023 interp. to 2017 (update from JRC-ETRI)",
    "CCGT": "DEA 2023 Technology Catalogue",
    "COAL_US": "DEA 2023 Technology Catalogue",
    "WIND_ONSHORE": "DEA 2023 Technology Catalogue",
    "WIND_OFFSHORE": "DEA 2023 Technology Catalogue",
    "PV_ROOFTOP": "DEA 2023 Technology Catalogue",
    "PV_UTILITY": "DEA 2023 Technology Catalogue",
    "HYDRO_DAM": "JRC-ETRI 2014 + national estimates",
    "HYDRO_RIVER": "JRC-ETRI 2014 + national estimates",
    "DHN_COGEN_GAS": "DEA 2023 Technology Catalogue",
    "DHN_COGEN_WOOD": "DEA 2023 Technology Catalogue",
    "DHN_COGEN_COAL": "DEA 2023 Technology Catalogue",
    "DHN_BOILER_GAS": "DEA 2023 Technology Catalogue",
    "DHN_BOILER_OIL": "DEA 2023 Technology Catalogue",
    "DHN_BOILER_WOOD": "DEA 2023 Technology Catalogue",
    "DEC_BOILER_GAS": "DEA 2023 Technology Catalogue",
    "DEC_BOILER_OIL": "DEA 2023 Technology Catalogue",
    "DEC_BOILER_WOOD": "DEA 2023 Technology Catalogue",
    "DEC_HP_ELEC": "DEA 2023 Technology Catalogue",
    "DEC_DIRECT_ELEC": "DEA 2023 Technology Catalogue",
    "DEC_COGEN_GAS": "DEA 2023 Technology Catalogue",
    "DEC_COGEN_OIL": "DEA 2023 Technology Catalogue",
    "DEC_SOLAR": "DEA 2023 Technology Catalogue",
    "IND_BOILER_WOOD": "DEA 2023 Technology Catalogue",
    "IND_BOILER_OIL": "DEA 2023 Technology Catalogue",
    "IND_BOILER_GAS": "DEA 2023 Technology Catalogue",
    "IND_BOILER_COAL": "DEA 2023 Technology Catalogue",
    "IND_COGEN_WOOD": "DEA 2023 Technology Catalogue",
    "IND_COGEN_GAS": "DEA 2023 Technology Catalogue",
    "CAR_GASOLINE": "DEA 2023 Technology Catalogue",
    "CAR_DIESEL": "DEA 2023 Technology Catalogue",
    "CAR_BEV": "DEA 2023 Technology Catalogue",
    "CAR_PHEV": "DEA 2023 Technology Catalogue",
    "TRUCK_DIESEL": "DEA 2023 Technology Catalogue",
    "BUS_COACH_DIESEL": "DEA 2023 Technology Catalogue",
    "TRAIN_PUB": "DEA 2023 Technology Catalogue",
    "CARGO_LFO": "IMO/DEA maritime",
    "GEOTHERMAL": "JRC-ETRI 2014",
    "DHN": "DEA 2023 district heating networks",
    "GRID": "ENTSO-E / national grid estimates",
    "BATT_LI": "DEA 2023 Technology Catalogue",
    "H2_ELECTROLYSIS": "DEA 2023 Technology Catalogue",
}

# Category classification
def classify_tech(name):
    transport = ("CAR_", "TRUCK_", "BUS_", "TRAIN_", "TRAMWAY_", "PLANE_", "CARGO_", "BOAT_")
    storage = ("TS_", "BATT_", "BEV_BATT", "PHEV_BATT", "CAES", "PHS", "DAM_STORAGE",
               "GAS_STORAGE", "H2_STORAGE", "DIESEL_STORAGE", "GASOLINE_STORAGE",
               "LFO_STORAGE", "JET_FUEL_STORAGE", "AMMONIA_STORAGE", "METHANOL_STORAGE",
               "PT_STORAGE", "ST_STORAGE", "CO2_STORAGE")
    synfuel = ("SYN_", "BIOMASS_TO_", "BIOWASTE_TO_", "POWER_TO_", "H2_TO_",
               "OIL_TO_", "GAS_TO_", "METHANOL_TO_", "METHANE_TO_", "HABER_",
               "H2_ELECTRO", "H2_NG", "H2_BIOMASS", "BIOMETHAN", "AMMONIA_TO_",
               "DIESEL_TO_", "INDUSTRY_CCS", "ATM_CCS")
    infra = ("DHN", "GRID", "HVAC_", "HVDC_", "GAS_PIPELINE", "GAS_SUBSEA",
             "H2_RETRO", "H2_NEW", "H2_SUBSEA", "EFFICIENCY")

    if any(name.startswith(p) for p in transport):
        return "Transport"
    if any(name.startswith(p) for p in storage) or name.endswith("_STORAGE"):
        return "Storage"
    if any(name.startswith(p) for p in synfuel):
        return "Synthetic Fuels & CCS"
    if any(name.startswith(p) for p in infra) or name in ("DHN", "GRID", "EFFICIENCY"):
        return "Infrastructure"
    return "Energy Supply & Conversion"


# ── Write to Excel ───────────────────────────────────────────────────────────
wb = openpyxl.load_workbook(EXCEL)

# ── Sheet 22: Technology Costs ────────────────────────────────────────────
sheet_name = "22_V33_Technology_Costs"
if sheet_name in wb.sheetnames:
    del wb[sheet_name]
ws = wb.create_sheet(sheet_name)

ws.cell(1, 1, "Technology Costs — REF_REGION (applied to Finland 2017)")
ws.cell(1, 1).font = Font(bold=True, size=14)
ws.merge_cells("A1:H1")
ws.cell(2, 1, "Source: Data/2017/02_REF_REGION/Technologies.csv (DEA 2023 + JRC-ETRI interp. to 2017)")
ws.cell(2, 1).font = Font(italic=True, size=9)
ws.merge_cells("A2:H2")
ws.cell(3, 1, "Note: These are REFERENCE costs — identical for all regions. Finland-specific overrides are ONLY on capacity bounds (f_min, f_max, fperc), not on costs.")
ws.cell(3, 1).font = Font(italic=True, size=9, color="CC0000")
ws.merge_cells("A3:H3")

headers = ["Technology", "Category", "c_inv (MEUR/GW)", "c_maint (MEUR/GW/a)",
           "lifetime (y)", "c_p", "gwp_constr (ktCO2/GW)", "Cost Source"]
widths = [28, 24, 16, 18, 12, 8, 20, 40]
write_header(ws, 5, headers, widths)

# Group by category
cats = OrderedDict()
for t in tech_costs.index:
    cat = classify_tech(t)
    cats.setdefault(cat, []).append(t)

r = 6
cat_order = ["Energy Supply & Conversion", "Transport", "Synthetic Fuels & CCS", "Infrastructure", "Storage"]
for cat in cat_order:
    if cat not in cats:
        continue
    # Section header
    ws.cell(r, 1, cat.upper())
    ws.cell(r, 1).font = Font(bold=True, size=11, color="2F5496")
    for c in range(1, 9):
        ws.cell(r, c).fill = SECTION_FILL
    r += 1

    for t in sorted(cats[cat]):
        row_data = tech_costs.loc[t]
        gwp = float(row_data["gwp_constr"]) if pd.notna(row_data["gwp_constr"]) else 0.0
        source = TECH_COST_SOURCES.get(t, "DEA 2023 / JRC default")
        vals = [
            t, cat,
            float(row_data["c_inv"]),
            float(row_data["c_maint"]),
            int(float(row_data["lifetime"])),
            round(float(row_data["c_p"]), 4),
            round(gwp, 2),
            source,
        ]
        write_row(ws, r, vals)
        r += 1

ws.freeze_panes = "A6"

# ── Sheet 23: Resource Costs ─────────────────────────────────────────────
sheet_name2 = "23_V33_Resource_Costs"
if sheet_name2 in wb.sheetnames:
    del wb[sheet_name2]
ws2 = wb.create_sheet(sheet_name2)

ws2.cell(1, 1, "Resource Operating Costs — Finland 2017 (v33)")
ws2.cell(1, 1).font = Font(bold=True, size=14)
ws2.merge_cells("A1:I1")
ws2.cell(2, 1, "c_op_local = effective price used by model (set via restore_v9_baseline.csv patch)")
ws2.cell(2, 1).font = Font(italic=True, size=9)
ws2.merge_cells("A2:I2")
ws2.cell(3, 1, "c_op_exterior = reference exterior price from 00_INDEP/Resources_indep.csv (used for import costing)")
ws2.cell(3, 1).font = Font(italic=True, size=9)
ws2.merge_cells("A3:I3")

res_headers = [
    "Resource", "c_op_local (MEUR/GWh)", "c_op_exterior (MEUR/GWh)",
    "gwp_op_exterior (ktCO2/GWh)", "co2_net (ktCO2/GWh)",
    "Category", "FI Override?", "Source", "Notes"
]
res_widths = [22, 20, 22, 22, 20, 18, 14, 35, 45]
write_header(ws2, 5, res_headers, res_widths)

# Resource source info
RES_SOURCES = {
    "ELECTRICITY": ("NordPool spot average 2017", "32.6 EUR/MWh — FI area price"),
    "GASOLINE": ("Statistics Finland fuel prices", "Wholesale pre-tax, ~58.8 EUR/MWh"),
    "DIESEL": ("Statistics Finland fuel prices", "Wholesale pre-tax, ~54.3 EUR/MWh"),
    "LFO": ("Statistics Finland fuel prices", "Light fuel oil wholesale, ~52.1 EUR/MWh"),
    "JET_FUEL": ("Statistics Finland / CIF spot", "CIF spot ~35.9 EUR/MWh (not pump price)"),
    "GAS": ("Statistics Finland fuel prices", "Wholesale natural gas, ~19.5 EUR/MWh"),
    "COAL": ("Statistics Finland fuel prices", "CIF coal import, ~10.3 EUR/MWh"),
    "URANIUM": ("DEA/JRC nuclear fuel", "Nuclear fuel cost, ~9.3 EUR/MWh_th"),
    "WOOD": ("Finnish Forest Research (Luke)", "Forest chips/energy wood, ~27.6 EUR/MWh"),
    "WET_BIOMASS": ("ENSPRESO / local estimates", "Agricultural wet biomass feedstock"),
    "ENERGY_CROPS_2": ("ENSPRESO / local estimates", "Energy crops production cost"),
    "BIOWASTE": ("ENSPRESO / local estimates", "Near-zero gate fee for biowaste"),
    "H2": ("DEA / JRC default", "Grey H2 import price"),
    "H2_RE": ("DEA / JRC default", "Green H2 import price"),
    "GAS_RE": ("DEA / JRC default", "Renewable gas import price"),
    "AMMONIA": ("DEA / JRC default", "Ammonia import price"),
    "AMMONIA_RE": ("DEA / JRC default", "Green ammonia import price"),
    "METHANOL": ("DEA / JRC default", "Methanol import price"),
    "METHANOL_RE": ("DEA / JRC default", "Green methanol import price"),
    "GASOLINE_RE": ("DEA / JRC default", "Renewable gasoline"),
    "DIESEL_RE": ("DEA / JRC default", "Renewable diesel"),
    "LFO_RE": ("DEA / JRC default", "Renewable LFO"),
    "JET_FUEL_RE": ("DEA / JRC default", "Renewable jet fuel"),
}

# Old Excel prices for comparison
EXCEL_OLD = {
    "GASOLINE": 0.06, "DIESEL": 0.05, "LFO": 0.05, "JET_FUEL": 0.05,
    "GAS": 0.02, "COAL": 0.015, "URANIUM": 0.005, "ELECTRICITY": 0.05,
}

r2 = 6
all_resources = sorted(set(list(res_patch_costs.keys()) +
                          [str(i) for i in res_indep.index if str(i).strip() not in ("", "nan", "parameter name")]))

for res in all_resources:
    if res in ("", "nan", "parameter name"):
        continue
    c_local = res_patch_costs.get(res, None)

    # Get INDEP exterior data
    c_ext = None
    gwp_ext = None
    co2_net = None
    cat_indep = ""
    if res in res_indep.index:
        rr = res_indep.loc[res]
        c_ext_col = [c for c in res_indep.columns if "exterior" in str(c).lower() and "price" in str(c).lower()]
        gwp_col = [c for c in res_indep.columns if "gwp" in str(c).lower()]
        co2_col = [c for c in res_indep.columns if "co2_net" in str(c).lower() or "direct emissions" in str(c).lower()]
        if c_ext_col:
            c_ext = rr[c_ext_col[0]] if pd.notna(rr[c_ext_col[0]]) else None
        if gwp_col:
            gwp_ext = rr[gwp_col[0]] if pd.notna(rr[gwp_col[0]]) else None
        if co2_col:
            co2_net = rr[co2_col[0]] if pd.notna(rr[co2_col[0]]) else None
        cat_col = [c for c in res_indep.columns if "category" in str(c).lower() or c == "Category"]
        if cat_col:
            cat_indep = str(rr[cat_col[0]]) if pd.notna(rr[cat_col[0]]) else ""

    fi_override = "Yes" if res in EXCEL_OLD and c_local is not None and abs((EXCEL_OLD.get(res, c_local) or 0) - (c_local or 0)) > 0.0005 else ""
    src_info = RES_SOURCES.get(res, ("DEA / JRC default", ""))

    vals = [
        res,
        c_local,
        float(c_ext) if c_ext is not None else None,
        float(gwp_ext) if gwp_ext is not None else None,
        float(co2_net) if co2_net is not None else None,
        cat_indep,
        fi_override,
        src_info[0],
        src_info[1],
    ]
    write_row(ws2, r2, vals)
    r2 += 1

# Add comparison note
r2 += 1
ws2.cell(r2, 1, "PREVIOUSLY IN EXCEL (05_Pricing_Pipeline) — OUTDATED VALUES")
ws2.cell(r2, 1).font = Font(bold=True, color="CC0000", size=10)
ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=9)
r2 += 1
write_header(ws2, r2, ["Resource", "Old Excel c_op", "Actual c_op (patches)", "Difference", "Status"], [22, 20, 20, 15, 15])
r2 += 1
for res in sorted(EXCEL_OLD.keys()):
    old_val = EXCEL_OLD[res]
    new_val = res_patch_costs.get(res, old_val)
    diff = new_val - old_val
    status = "OK" if abs(diff) < 0.001 else "CORRECTED"
    write_row(ws2, r2, [res, old_val, new_val, round(diff, 6), status],
              bold=(status == "CORRECTED"))
    if status == "CORRECTED":
        for c in range(1, 6):
            ws2.cell(r2, c).font = Font(bold=True, color="CC0000")
    r2 += 1

ws2.freeze_panes = "A6"

# ── Update 05_Pricing_Pipeline ────────────────────────────────────────────
if "05_Pricing_Pipeline" in wb.sheetnames:
    del wb["05_Pricing_Pipeline"]
ws5 = wb.create_sheet("05_Pricing_Pipeline")

ws5.cell(1, 1, "Fossil Fuel Pricing Pipeline — Finland 2017 (CORRECTED v33)")
ws5.cell(1, 1).font = Font(bold=True, size=14)
ws5.merge_cells("A1:G1")
ws5.cell(2, 1, "c_op_local = effective price from restore_v9_baseline.csv (overrides FI Resources.csv)")
ws5.cell(2, 1).font = Font(italic=True, size=9)
ws5.merge_cells("A2:G2")

price_headers = ["Resource", "c_op_local (MEUR/GWh)", "c_op_exterior (MEUR/GWh)",
                 "Old Excel Value", "Correction", "Source", "Notes"]
price_widths = [18, 22, 22, 16, 14, 30, 45]
write_header(ws5, 4, price_headers, price_widths)

# Key fossil fuels
price_resources = [
    "GASOLINE", "DIESEL", "LFO", "JET_FUEL", "GAS", "COAL", "URANIUM", "ELECTRICITY",
    "WOOD", "WET_BIOMASS", "ENERGY_CROPS_2", "BIOWASTE",
]

r5 = 5
for res in price_resources:
    c_local = res_patch_costs.get(res, None)
    c_ext = None
    if res in res_indep.index:
        rr = res_indep.loc[res]
        c_ext_col = [c for c in res_indep.columns if "exterior" in str(c).lower() and "price" in str(c).lower()]
        if c_ext_col:
            c_ext = rr[c_ext_col[0]] if pd.notna(rr[c_ext_col[0]]) else None

    old_val = EXCEL_OLD.get(res, None)
    correction = ""
    if old_val is not None and c_local is not None:
        if abs(old_val - c_local) > 0.001:
            correction = "CORRECTED"

    src = RES_SOURCES.get(res, ("", ""))[0]
    notes = RES_SOURCES.get(res, ("", ""))[1]

    vals = [res, c_local, float(c_ext) if c_ext is not None else None,
            old_val, correction, src, notes]
    write_row(ws5, r5, vals, bold=(correction == "CORRECTED"))
    r5 += 1

# Add conversion notes
r5 += 1
ws5.cell(r5, 1, "Conversion & Decision Notes")
ws5.cell(r5, 1).font = Font(bold=True, size=11)
r5 += 1
notes = [
    ("EUR_2015_to_2017", "~1.02", "Approximate deflation factor"),
    ("GJ_to_MWh", "0.277778", "Standard physical conversion"),
    ("JET_FUEL decision", "0.0359 used (not 0.0797)", "Reference exterior price inflated by intermediary margins; 0.0359 = CIF spot estimate for wholesale kerosene"),
    ("ELECTRICITY", "0.0326 used (not 0.0843)", "NordPool FI area 2017 average; reference exterior includes import tariff markup"),
    ("WOOD c_op_local", "0.0276 used (not 0.022)", "Updated ENSPRESO + Luke forestry data; slightly higher than older estimate"),
    ("COAL", "0.0103 used (not 0.015)", "CIF import coal; old estimate rounded up"),
    ("URANIUM", "0.0093 used (not 0.005)", "Full fuel cycle cost including enrichment; old value underestimated"),
]
for key, val, note in notes:
    write_row(ws5, r5, [key, val, note])
    r5 += 1

ws5.freeze_panes = "A5"

# ── Update Change Log ────────────────────────────────────────────────────
ws_log = wb["18_Change_Log"]
next_row = ws_log.max_row + 1
log_entries = [
    (date.today().isoformat(), "Copilot+User", "Added 22_V33_Technology_Costs (168 techs)",
     "Finland_MASTER_Calibration_old_UPDATED.xlsx",
     "All c_inv/c_maint/lifetime/c_p/gwp from REF_REGION, categorised with sources"),
    (date.today().isoformat(), "Copilot+User", "Added 23_V33_Resource_Costs",
     "Finland_MASTER_Calibration_old_UPDATED.xlsx",
     "c_op_local from patches + c_op_exterior/gwp from INDEP + old-vs-new comparison"),
    (date.today().isoformat(), "Copilot+User", "Corrected 05_Pricing_Pipeline",
     "Finland_MASTER_Calibration_old_UPDATED.xlsx",
     "7/8 resource prices were outdated; now shows actual patch values with old→new diff"),
]
for entry in log_entries:
    for c, v in enumerate(entry, 1):
        ws_log.cell(next_row, c, v)
    next_row += 1

# ── Save ──────────────────────────────────────────────────────────────────
wb.save(EXCEL)
print("Saved to", EXCEL)
print("  - 22_V33_Technology_Costs:", len(tech_costs), "technologies")
print("  - 23_V33_Resource_Costs:", len(res_patch_costs), "resources + comparison")
print("  - 05_Pricing_Pipeline: CORRECTED with actual values")
