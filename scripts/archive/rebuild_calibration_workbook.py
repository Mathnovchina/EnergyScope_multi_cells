"""
Rebuild Finland_MASTER_Calibration_old_UPDATED.xlsx
====================================================
Comprehensive calibration workbook for Finland 2017.
All sheets populated from the actual model CSV files + audit data.

Run from the repo root:
    python scripts/rebuild_calibration_workbook.py
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "Data" / "2017"
FI   = DATA / "FI"
REF  = DATA / "02_REF_REGION"
INDEP = DATA / "00_INDEP"
OUT  = ROOT / "Data" / "exogenous_data" / "Finland_MASTER_Calibration_old_UPDATED.xlsx"

# ── styles ───────────────────────────────────────────────────────────────────
HEADER_FONT  = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
HEADER_FILL  = PatternFill("solid", fgColor="2F5496")
SUBHDR_FILL  = PatternFill("solid", fgColor="D6E4F0")
SUBHDR_FONT  = Font(name="Calibri", bold=True, size=11)
TITLE_FONT   = Font(name="Calibri", bold=True, size=14, color="2F5496")
WARN_FILL    = PatternFill("solid", fgColor="FFF2CC")
PASS_FILL    = PatternFill("solid", fgColor="D9EFDF")
FAIL_FILL    = PatternFill("solid", fgColor="F8D7DA")
THIN_BORDER  = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)

def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = THIN_BORDER

def style_subheader(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = SUBHDR_FONT
        cell.fill = SUBHDR_FILL
        cell.border = THIN_BORDER

def auto_width(ws, min_w=10, max_w=40):
    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        adj = min(max(length + 2, min_w), max_w)
        ws.column_dimensions[get_column_letter(col_cells[0].column)].width = adj

def write_table(ws, headers, rows, start_row=1):
    """Write headers + data rows, return next free row."""
    for c, h in enumerate(headers, 1):
        ws.cell(row=start_row, column=c, value=h)
    style_header(ws, start_row, len(headers))
    r = start_row + 1
    for row_data in rows:
        for c, val in enumerate(row_data, 1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(wrap_text=True)
        r += 1
    return r

# ── load data ────────────────────────────────────────────────────────────────
fi_tech  = pd.read_csv(FI / "Technologies.csv", index_col=0)
fi_res   = pd.read_csv(FI / "Resources.csv", index_col=0)
fi_dem   = pd.read_csv(FI / "Demands.csv", index_col=0)
fi_misc  = json.loads((FI / "Misc.json").read_text())
fi_wgt   = pd.read_csv(FI / "Weights.csv", index_col=0)
fi_sto   = pd.read_csv(FI / "Storage_power_to_energy.csv", index_col=0)

# REF Technologies (complex header)
ref_tech_raw = pd.read_csv(REF / "Technologies.csv")
ref_tech_raw.columns = [
    "Category", "Subcategory", "Technologies name", "Technologies param",
    "c_inv", "c_maint", "gwp_constr", "lifetime", "c_p",
    "fmin_perc", "fmax_perc", "f_min", "f_max", "Comment",
]
ref_tech = ref_tech_raw.iloc[1:].copy()
ref_tech["Technologies param"] = ref_tech["Technologies param"].str.strip()
ref_tech = ref_tech.set_index("Technologies param")
for col in ["c_inv", "c_maint", "gwp_constr", "lifetime", "c_p",
            "fmin_perc", "fmax_perc", "f_min", "f_max"]:
    ref_tech[col] = pd.to_numeric(ref_tech[col], errors="coerce")

ref_res  = pd.read_csv(REF / "Resources.csv")
# REF Resources has complex multi-row header
ref_misc = json.loads((REF / "Misc.json").read_text())
indep_misc = json.loads((INDEP / "Misc_indep.json").read_text())
indep_res  = pd.read_csv(INDEP / "Resources_indep.csv")

# Layers_in_out
lio = pd.read_csv(INDEP / "Layers_in_out.csv", index_col=0)

# ══════════════════════════════════════════════════════════════════════════════
wb = Workbook()

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 0: Overview
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.active
ws.title = "00_Overview"
ws.cell(row=1, column=1, value="Finland 2017 — Master Calibration File").font = TITLE_FONT
ws.merge_cells("A1:D1")

info = [
    ("Region", "Finland (FI)"),
    ("Model year", "2017"),
    ("Branch", "finlandnew"),
    ("Model", "EnergyScope Multi-Cells (ESMC)"),
    ("Solver", "CPLEX"),
    ("Typical days", "12 (k-medoids)"),
    ("f_perc mode", "True (market share constraints active)"),
    ("Generated", datetime.now().strftime("%Y-%m-%d %H:%M")),
    ("", ""),
    ("DATA ARCHITECTURE", ""),
    ("Tier 1 (00_INDEP)", "Universal constants: efficiencies (Layers_in_out), storage, network losses, i_rate"),
    ("Tier 2 (02_REF_REGION)", "Reference defaults: 170 technologies (costs, lifetimes, c_p), 35 resources"),
    ("Tier 3 (FI/)", "Finland-specific overrides: capacity bounds, prices, demands, shares"),
    ("Pipeline", "REF_REGION.deepcopy() -> FI.update() -> concat_reg_data -> mask(>1e14) -> .dat -> AMPL"),
    ("", ""),
    ("SUMMARY OF FI OVERRIDES", ""),
    ("Technologies", f"{len(fi_tech)} rows overriding REF defaults (capacity bounds + market shares)"),
    ("Resources", f"{len(fi_res)} rows (local biomass + fossil prices + RE fuel disabling)"),
    ("Demands", "11 end-use demands"),
    ("Misc.json", f"{len(fi_misc)} parameters overriding REF defaults"),
]
r = 3
for item, value in info:
    ws.cell(row=r, column=1, value=item).font = Font(bold=True) if item else Font()
    ws.cell(row=r, column=2, value=value)
    r += 1

auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 1: Data Traceability
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("01_Data_Traceability")

traceability = [
    # (Category, Parameter, Year, Source, Source_File, Model_File, AMPL_Param, Notes)
    ("Demands", "ELECTRICITY", 2017, "JRC-IDEES/Eurostat 2015", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", "2015 data as proxy for 2017"),
    ("Demands", "HEAT_HIGH_T", 2017, "JRC-IDEES/Eurostat 2015", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", "Industrial high-temp heat"),
    ("Demands", "HEAT_LOW_T_SH", 2017, "JRC-IDEES/Eurostat 2015", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", "Space heating"),
    ("Demands", "HEAT_LOW_T_HW", 2017, "JRC-IDEES/Eurostat 2015", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", "Hot water"),
    ("Demands", "PROCESS_COOLING", 2017, "JRC-IDEES/Eurostat 2015", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", ""),
    ("Demands", "SPACE_COOLING", 2017, "JRC-IDEES/Eurostat 2015", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", ""),
    ("Demands", "MOBILITY_PASSENGER", 2017, "Eurostat/stat.fi", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", ""),
    ("Demands", "MOBILITY_FREIGHT", 2017, "Eurostat/stat.fi", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", ""),
    ("Demands", "AVIATION_LONG_HAUL", 2017, "Eurostat aviation", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", ""),
    ("Demands", "SHIPPING", 2017, "Eurostat maritime", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", ""),
    ("Demands", "NON_ENERGY", 2017, "JRC-IDEES 2015", "Data/exogenous_data/regions/Demands.csv", "Data/2017/FI/Demands.csv", "end_uses_demand_year", "Petrochemicals"),
    ("Technologies", "Capacity bounds (f_min/f_max)", 2017, "Statistics Finland / Energy Authority", "-", "Data/2017/FI/Technologies.csv", "f_min, f_max", "34 techs with FI-specific bounds"),
    ("Technologies", "Market shares (fmin_perc/fmax_perc)", 2017, "Statistics Finland / calibration", "-", "Data/2017/FI/Technologies.csv", "fmin_perc, fmax_perc", "22 techs with share constraints"),
    ("Technologies", "Costs (c_inv, c_maint)", 2035, "DEA Technology Catalogue 2023", "-", "Data/2017/02_REF_REGION/Technologies.csv", "c_inv, c_maint", "14 key techs updated to 2017; 153 at 2035 default"),
    ("Technologies", "Efficiencies (layers_in_out)", "All", "DEA / ESMC defaults", "-", "Data/2017/00_INDEP/Layers_in_out.csv", "layers_in_out", "~130 techs x 38 layers; NOT per-country"),
    ("Resources", "Biomass availability (6 types)", 2017, "ENSPRESO / local estimates", "Data/exogenous_data/regions/", "Data/2017/FI/Resources.csv", "avail", "6 local bio/waste resources"),
    ("Resources", "Fossil fuel prices (8 fuels)", 2017, "Statistics Finland", "Data/exogenous_data/regions/", "Data/2017/FI/Resources.csv", "c_op", "FI-specific prices override REF"),
    ("Resources", "RE fuel disabling", 2017, "Calibration decision", "-", "Data/2017/FI/Resources.csv", "avail", "8 RE fuels set to avail_exterior=0"),
    ("Resources", "Exterior prices (c_op_exterior)", "All", "ESMC defaults", "-", "Data/2017/00_INDEP/Resources_indep.csv", "c_op_exterior", "35 resources; applies if not overridden by FI"),
    ("Misc", "DHN share", 2020, "Finnish Energy", "-", "Data/2017/FI/Misc.json", "share_heat_dhn_min/max", "0.449-0.451"),
    ("Misc", "Public mobility share", 2019, "stat.fi", "-", "Data/2017/FI/Misc.json", "share_mobility_public_min/max", "0.160-0.162"),
    ("Misc", "Freight rail share", 2019, "stat.fi", "-", "Data/2017/FI/Misc.json", "share_freight_train_min/max", "0.275-0.277"),
    ("Misc", "RE share primary", 2017, "Statistics Finland", "-", "Data/2017/FI/Misc.json", "re_share_primary", "0.41"),
    ("Misc", "Interconnection capacity", 2017, "ENTSO-E", "-", "Data/2017/FI/Misc.json", "elec_import/export_capacity", "3 GW each"),
    ("Misc", "Solar area (ground)", 2017, "ENSPRESO", "-", "Data/2017/FI/Misc.json", "solar_area_ground", "345.75 km2"),
    ("Misc", "Solar area (rooftop)", 2017, "ENSPRESO", "-", "Data/2017/FI/Misc.json", "solar_area_rooftop", "80.49 km2"),
    ("Misc", "Network losses", "All", "ESMC defaults (global)", "-", "Data/2017/00_INDEP/Misc_indep.json", "loss_network", "ELEC=8.64%, DHN=5% (NOT per-country)"),
    ("TimeSeries", "Hourly profiles (8760h x 13)", 2015, "ENTSOE / renewables.ninja / JRC-IDEES", "-", "Data/2017/FI/Time_series.csv", "t_op", "2015 profiles as proxy for 2017"),
    ("Weights", "TD demand weights", 2017, "Calibration", "-", "Data/2017/FI/Weights.csv", "weights", "HEAT_LOW_T_SH=0.204, SPACE_COOLING=0.087"),
    ("Storage", "PHS power-to-energy", 2017, "Calibration", "-", "Data/2017/FI/Storage_power_to_energy.csv", "storage_charge_time", "7.35h charge/discharge"),
]

headers = ["Data_Category", "Specific_Parameter", "Year_Applied", "Source_Origin",
           "Source_File_Path", "Model_Location", "AMPL_Parameter", "Notes"]
write_table(ws, headers, traceability)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 2: Demands
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("02_Demands")

dem_headers = ["Category", "Subcategory", "Parameter", "HOUSEHOLDS", "SERVICES",
               "INDUSTRY", "TRANSPORTATION", "Total", "Units"]
dem_rows = []
for idx, row in fi_dem.iterrows():
    cat = idx
    subcat = row.get("Subcategory", "")
    param = row.get("parameter name", "")
    hh = row.get("HOUSEHOLDS", 0)
    sv = row.get("SERVICES", 0)
    ind = row.get("INDUSTRY", 0)
    tr = row.get("TRANSPORTATION", 0)
    units = row.get("Units", "")
    # convert to float safely
    try:
        hh_f, sv_f, ind_f, tr_f = float(hh), float(sv), float(ind), float(tr)
        total = hh_f + sv_f + ind_f + tr_f
    except (ValueError, TypeError):
        total = ""
        hh_f, sv_f, ind_f, tr_f = hh, sv, ind, tr
    dem_rows.append([cat, subcat, param, round(hh_f, 2), round(sv_f, 2),
                     round(ind_f, 2), round(tr_f, 2), round(total, 2) if isinstance(total, (int, float)) else total, units])

write_table(ws, dem_headers, dem_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 3: Technologies (FI overrides)
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("03_Technologies_FI")

tech_headers = ["Technology", "f_min", "f_max", "fmin_perc", "fmax_perc",
                "REF_c_inv", "REF_c_maint", "REF_lifetime", "REF_c_p",
                "REF_f_min", "REF_f_max", "Category", "Notes"]
tech_rows = []
for tech_name in fi_tech.index:
    name = str(tech_name).strip()
    if not name or name == "nan":
        continue
    row = fi_tech.loc[tech_name]
    f_min = row.get("f_min", "")
    f_max = row.get("f_max", "")
    fmin_p = row.get("fmin_perc", "")
    fmax_p = row.get("fmax_perc", "") if "fmax_perc" in fi_tech.columns else ""

    # REF data
    ref_cinv = ref_cmaint = ref_life = ref_cp = ref_fmin = ref_fmax = ""
    if name in ref_tech.index:
        rr = ref_tech.loc[name]
        if isinstance(rr, pd.DataFrame):
            rr = rr.iloc[0]
        ref_cinv = rr.get("c_inv", "")
        ref_cmaint = rr.get("c_maint", "")
        ref_life = rr.get("lifetime", "")
        ref_cp = rr.get("c_p", "")
        ref_fmin = rr.get("f_min", "")
        ref_fmax = rr.get("f_max", "")
        if pd.notna(ref_fmax) and ref_fmax > 1e10:
            ref_fmax = "1e15 (uncapped)"

    # Categorize
    cat = ""
    note = ""
    if isinstance(f_max, (int, float)) and not pd.isna(f_max) and f_max == 0:
        cat = "BANNED"
        note = "Disabled for Finland (f_max=0)"
    elif isinstance(fmin_p, (int, float)) and not pd.isna(fmin_p) and fmin_p > 0:
        cat = "FORCED_SHARE"
        note = f"Forced min share {fmin_p}"
    elif isinstance(fmax_p, (int, float)) and not pd.isna(fmax_p) and fmax_p < 1 and fmax_p > 0:
        cat = "CAPPED_SHARE"
        note = f"Capped max share {fmax_p}"
    elif isinstance(f_min, (int, float)) and not pd.isna(f_min) and f_min > 0:
        cat = "CAPACITY_BOUND"
    else:
        cat = "OVERRIDE"

    # Clean NaN for display
    def clean(v):
        if isinstance(v, float) and (pd.isna(v) or np.isnan(v)):
            return ""
        return v

    tech_rows.append([name, clean(f_min), clean(f_max), clean(fmin_p), clean(fmax_p),
                      clean(ref_cinv), clean(ref_cmaint), clean(ref_life), clean(ref_cp),
                      clean(ref_fmin), clean(ref_fmax), cat, note])

write_table(ws, tech_headers, tech_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 4: Resources (FI)
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("04_Resources_FI")

res_headers = ["Resource", "avail_local (GWh)", "c_op_local (MEUR/GWh)",
               "avail_exterior (GWh)", "Category", "Source"]
res_rows = []
for res_name in fi_res.index:
    name = str(res_name).strip()
    if not name or name == "nan":
        continue
    row = fi_res.loc[res_name]
    avl = row.get("avail_local", 0)
    cop = row.get("c_op_local", 0)
    avx = row.get("avail_exterior", 0)

    if avl > 0 and avx == 0:
        cat = "LOCAL_BIOMASS"
        src = "ENSPRESO / local estimates"
    elif avx > 0:
        cat = "IMPORT_FOSSIL"
        src = "Statistics Finland"
    elif str(name).endswith("_RE") or name in ("H2", "H2_RE", "AMMONIA", "AMMONIA_RE", "METHANOL", "METHANOL_RE"):
        cat = "DISABLED"
        src = "Not applicable for 2017"
    else:
        cat = "OTHER"
        src = ""

    res_rows.append([name, avl, cop, avx, cat, src])

write_table(ws, res_headers, res_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 5: Pricing Pipeline
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("05_Pricing_Pipeline")

ws.cell(row=1, column=1, value="Fossil Fuel Pricing Pipeline — Finland 2017").font = TITLE_FONT
ws.merge_cells("A1:F1")

pricing_headers = ["Resource", "FI_c_op_local (MEUR/GWh)", "REF_c_op_local (MEUR/GWh)",
                   "INDEP_c_op_exterior (MEUR/GWh)", "Price_Used", "Source"]

# Build REF resource prices lookup (manual from our data extraction)
ref_prices = {
    "ELECTRICITY": 0.0332, "GASOLINE": 0.06, "DIESEL": 0.057, "LFO": 0.055,
    "JET_FUEL": 0.082366, "GAS": 0.02, "COAL": 0.01, "URANIUM": 0.003876,
}
indep_prices = {
    "ELECTRICITY": 0.08433, "GASOLINE": 0.082366, "DIESEL": 0.079744,
    "LFO": 0.060151, "JET_FUEL": 0.079744, "GAS": 0.044253,
    "COAL": 0.017658, "URANIUM": 0.003876,
}

price_rows = []
for res_name in ["GASOLINE", "DIESEL", "LFO", "JET_FUEL", "GAS", "COAL", "URANIUM", "ELECTRICITY"]:
    fi_price = ""
    if res_name in fi_res.index:
        fi_price = fi_res.loc[res_name, "c_op_local"]
    ref_p = ref_prices.get(res_name, "")
    ind_p = indep_prices.get(res_name, "")
    price_rows.append([
        res_name, fi_price, ref_p, ind_p,
        "FI override" if fi_price else "REF default",
        "Statistics Finland" if res_name != "ELECTRICITY" else "NordPool"
    ])

write_table(ws, pricing_headers, price_rows, start_row=3)

# Conversions
r = 3 + len(price_rows) + 3
ws.cell(row=r, column=1, value="Conversions & Notes").font = SUBHDR_FONT
r += 1
conv_data = [
    ("EUR_2015_to_2017", "1.02", "Approximate deflation factor"),
    ("GJ_to_MWh", "0.277778", "Standard physical conversion"),
    ("JET_FUEL decision", "0.0359 used (not 0.0824)", "High value likely included taxes; 0.0359 = CIF spot estimate"),
    ("WOOD price", "0.022084 MEUR/GWh", "Kept from local estimate, not recalculated"),
]
for item in conv_data:
    for c, val in enumerate(item, 1):
        ws.cell(row=r, column=c, value=val).border = THIN_BORDER
    r += 1

auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 6: Misc Parameters
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("06_Misc_Parameters")

misc_headers = ["Parameter", "FI_Value", "REF_Value", "Change", "Source", "Notes"]
misc_rows = []

# Build comparison
ref_misc_flat = {}
for k, v in ref_misc.items():
    if isinstance(v, dict):
        for kk, vv in v.items():
            ref_misc_flat[k + "." + kk] = vv
    else:
        ref_misc_flat[k] = v

def fmt_val(v):
    if isinstance(v, dict):
        return str(v)
    return v

for param, fi_val in sorted(fi_misc.items()):
    ref_val = ref_misc.get(param, "NOT IN REF")
    if isinstance(fi_val, dict) and isinstance(ref_val, dict):
        change = "dict override"
    elif isinstance(ref_val, (int, float)) and isinstance(fi_val, (int, float)):
        if ref_val != 0:
            pct = (fi_val - ref_val) / abs(ref_val) * 100
            change = f"{pct:+.1f}%"
        else:
            change = f"0 -> {fi_val}"
    else:
        change = "override"

    src = ""
    notes = ""
    if "dhn" in param:
        src = "Finnish Energy (2024)"
        notes = "District heating ~45% of space heating"
    elif "public" in param:
        src = "Statistics Finland"
        notes = "(bus+rail)/(car+bus+rail)"
    elif "freight_train" in param:
        src = "Statistics Finland"
        notes = "rail/(rail+road)"
    elif "freight_boat" in param:
        src = "Eurostat inland waterway"
    elif "re_share" in param:
        src = "Statistics Finland"
        notes = "Finland actual RE share 2017"
    elif "elec_" in param and "capacity" in param:
        src = "ENTSO-E"
        notes = "Interconnection SE, EE, RU"
    elif "solar_area" in param:
        src = "ENSPRESO"
    elif "ned" in param:
        src = "JRC-IDEES"
        notes = "Non-energy demand split"
    elif "import_capacity" in param:
        src = "Estimate"
        notes = "Gas + electricity"

    misc_rows.append([param, fmt_val(fi_val), fmt_val(ref_val), change, src, notes])

write_table(ws, misc_headers, misc_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 7: Global Parameters (INDEP)
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("07_Global_Parameters")

ws.cell(row=1, column=1, value="Global Parameters (00_INDEP) — Not Overrideable per Country").font = TITLE_FONT
ws.merge_cells("A1:D1")

g_headers = ["Parameter", "Value", "Notes", "Finland Reality"]
g_rows = [
    ("i_rate", 0.05, "5% discount rate", ""),
    ("gwp_limit_overall", "1e15", "No GHG constraint", ""),
    ("loss_network ELECTRICITY", 0.0864, "8.64% grid losses (EU average)", "~3% (Finnish Energy) — OVERESTIMATED"),
    ("loss_network HEAT_LOW_T_DHN", 0.05, "5% DH losses (EU average)", "~8.5% (Finnish Energy) — UNDERESTIMATED"),
    ("power_density_pv", 0.085, "GW/km2", ""),
    ("power_density_solar_thermal", 0.026, "GW/km2", ""),
    ("sm_max", 4, "Solar multiple max (CSP)", "Not relevant for Finland"),
    ("c_grid_extra", 367.8, "M€/GW grid reinforcement", ""),
    ("vehicule_capacity CAR_PHEV", 50.4, "kWh", ""),
    ("vehicule_capacity CAR_BEV", 50.4, "kWh", ""),
    ("batt_per_car CAR_PHEV", 10.0, "kWh", ""),
    ("batt_per_car CAR_BEV", 50.0, "kWh", ""),
]
write_table(ws, g_headers, g_rows, start_row=3)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 8: Key Efficiencies
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("08_Key_Efficiencies")

ws.cell(row=1, column=1, value="Key Technology Efficiencies (from 00_INDEP/Layers_in_out.csv)").font = TITLE_FONT
ws.merge_cells("A1:F1")

eff_headers = ["Technology", "Primary Input", "Input Value", "Primary Output", "Efficiency (%)", "CO2_INDUSTRY"]
eff_techs = [
    "NUCLEAR", "COAL_US", "CCGT", "WIND_ONSHORE", "WIND_OFFSHORE",
    "HYDRO_DAM", "HYDRO_RIVER", "PV_ROOFTOP", "PV_UTILITY",
    "IND_BOILER_WOOD", "IND_BOILER_COAL", "IND_BOILER_GAS", "IND_BOILER_OIL",
    "DHN_COGEN_WOOD", "DHN_COGEN_COAL", "DHN_COGEN_GAS",
    "DHN_BOILER_OIL", "DHN_BOILER_GAS", "DHN_BOILER_WOOD",
    "DEC_HP_ELEC", "DEC_BOILER_GAS", "DEC_BOILER_OIL", "DEC_BOILER_WOOD",
    "DEC_DIRECT_ELEC", "DEC_COGEN_GAS",
    "CAR_GASOLINE", "CAR_DIESEL", "CAR_BEV", "CAR_PHEV", "CAR_HEV",
    "TRUCK_DIESEL", "TRUCK_NG", "BUS_COACH_DIESEL",
    "CARGO_LFO", "CARGO_LNG", "BOAT_FREIGHT_DIESEL", "BOAT_FREIGHT_NG",
]

eff_rows = []
for t in eff_techs:
    if t not in lio.index:
        continue
    row = lio.loc[t]
    nonzero = row[row != 0]
    # Find primary input (most negative)
    inputs = nonzero[nonzero < 0]
    if len(inputs) == 0:
        continue
    primary_in_name = inputs.idxmin()
    primary_in_val = inputs.min()
    # Efficiency = 1 / abs(primary_in_val) * 100
    eff = round(1.0 / abs(primary_in_val) * 100, 1)

    # CO2
    co2 = nonzero.get("CO2_INDUSTRY", 0)

    eff_rows.append([t, primary_in_name, round(primary_in_val, 4), "see Layers_in_out", eff, round(co2, 4) if co2 != 0 else ""])

write_table(ws, eff_headers, eff_rows, start_row=3)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 9: Time Series & Weights
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("09_TimeSeries_Weights")

ws.cell(row=1, column=1, value="Time Series & Weights — Finland 2017").font = TITLE_FONT
ws.merge_cells("A1:D1")

tw_headers = ["Profile", "Weight", "Source", "Notes"]
tw_rows = []
for ts_name in fi_wgt.index:
    w = fi_wgt.loc[ts_name, "Weights"]
    src = ""
    notes = ""
    if "WIND" in ts_name or "HYDRO" in ts_name or "PV" in ts_name:
        src = "renewables.ninja / ENTSOE"
        notes = "2015 hourly profiles"
    elif ts_name == "ELECTRICITY":
        src = "ENTSOE"
        notes = "2015 hourly profile, weight=1.0"
    elif ts_name == "HEAT_LOW_T_SH":
        src = "JRC-IDEES"
        notes = "Heating demand profile"
    elif ts_name == "SPACE_COOLING":
        src = "JRC-IDEES"
        notes = "Cooling demand profile"
    elif ts_name == "TIDAL":
        notes = "All zeros (no tidal in Finland)"
    tw_rows.append([ts_name, w, src, notes])

write_table(ws, tw_headers, tw_rows, start_row=3)

# Storage section
r = 3 + len(tw_rows) + 3
ws.cell(row=r, column=1, value="Storage Overrides (FI/)").font = SUBHDR_FONT
r += 1
sto_headers = ["Storage", "charge_time (h)", "discharge_time (h)"]
sto_rows = []
for s in fi_sto.index:
    sto_rows.append([s, fi_sto.loc[s, "storage_charge_time"], fi_sto.loc[s, "storage_discharge_time"]])
write_table(ws, sto_headers, sto_rows, start_row=r)

auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 10: UD Parameters (Finnish Energy sourced)
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("10_UD_Parameters")

ud_headers = ["Parameter", "Symbol", "Value", "Baseline Year", "How Computed", "Primary Source"]
ud_rows = [
    ("District heating share", "%Dhn", 0.45, 2020, "Space-heating market share proxy", "Finnish Energy (2024), Energy Year 2023"),
    ("DH network losses", "Loss(HeatLowTDhn)", 0.085, 2020, "8-9% typical DH distribution losses", "Finnish Energy (2024), DH networks"),
    ("Public mobility share", "%Public", 0.1608, 2019, "(bus+rail)/(car+bus+rail)", "Statistics Finland"),
    ("Freight rail share", "%Rail", 0.2761, 2019, "rail/(rail+road)", "Statistics Finland"),
    ("Electricity grid losses", "Loss(Elec)", 0.03, 2022, "Finnish grid losses ~3%", "Energy in Finland 2022 (YLE/doria.fi)"),
    ("RE share primary", "re_share_primary", 0.41, 2017, "Renewable share of TPES", "Statistics Finland"),
    ("Solar area (ground)", "solar_area_ground", 345.75, 2017, "ENSPRESO ground PV potential", "JRC ENSPRESO"),
    ("Solar area (rooftop)", "solar_area_rooftop", 80.49, 2017, "ENSPRESO rooftop PV potential", "JRC ENSPRESO"),
    ("Elec import capacity", "elec_import_capacity", 3.0, 2017, "SE+EE+RU interconnection", "ENTSO-E TYNDP"),
    ("Elec export capacity", "elec_export_capacity", 3.0, 2017, "SE+EE+RU interconnection", "ENTSO-E TYNDP"),
]
write_table(ws, ud_headers, ud_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 11: Comparators
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("11_Comparators")

comp_headers = ["Case Study", "%Dhn", "%Public", "%Rail", "Loss(Elec)", "Loss(DHN)", "Source", "Notes"]
comp_rows = [
    ("Switzerland (Moret 2017)", 0.064, 0.2, 0.368, 0.07, 0.05, "Moret (2017), Table A.26", "Modal shares exogenous"),
    ("Belgium (Limpens 2021)", 0.02, 0.199, 0.109, 0.047, 0.069, "Limpens (2021), Table C.23", "%Boat=15.6%"),
    ("Finland (this work)", 0.45, 0.16, 0.276, "0.0864 (model) / 0.03 (real)", "0.05 (model) / 0.085 (real)", "Statistics Finland / Finnish Energy", "Model uses global INDEP losses"),
]
write_table(ws, comp_headers, comp_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 12: Validation 2017
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("12_Validation_2017")

val_headers = ["Category", "Sub-Category", "Parameter/Tech", "Model Config", "Real 2017", "Gap/Decision", "Hypothesis", "Action"]
val_rows = [
    ("Resources", "Import (Legacy)", "Natural Gas", "avail_exterior=28000, c_op=0.02", "~25 TWh consumption", "Constrained to represent legacy contracts", "Gas driven by infra not economics", "Set avail_exterior=28000"),
    ("Resources", "Import (Legacy)", "Light Fuel Oil (LFO)", "avail_exterior=150000", "~10-15 TWh heating", "Large ceiling to avoid infeasibility", "Previous runs leaked 100 TWh when Gas constrained", "avail_exterior=150000"),
    ("Resources", "Import (Legacy)", "Coal", "avail_exterior=50000", "~15-20 TWh", "Covering coal fleet", "Coal fleet still running in 2017", "Set high ceiling"),
    ("Technologies", "Heat/CHP", "IND_BOILER_WOOD fmin_perc=0.4", "Forced 40% min", "Biomass dominant in industry", "Model prefers gas", "Finnish biomass mandate/tradition", "fmin_perc=0.4"),
    ("Technologies", "Heat/CHP", "DHN_COGEN_WOOD fmin_perc=0.3", "Forced 30% min", "Biomass CHP significant", "Model prefers gas CHP", "CHP biomass in Finland", "fmin_perc=0.3"),
    ("Technologies", "Heat/CHP", "DHN_COGEN_COAL fmin_perc=0.3", "Forced 30% min", "Coal CHP sunk costs", "Would not invest in coal CHP", "Existing fleet must be represented", "fmin_perc=0.3"),
    ("Technologies", "Heat/CHP", "DHN_COGEN_GAS fmax_perc=0.2", "Capped at 20%", "Small gas CHP share", "Model over-invests in gas CHP", "Gas CHP limited", "fmax_perc=0.2"),
    ("Technologies", "Transport", "CAR_GASOLINE 55-65%", "fmin/max_perc", "~60% of car fleet", "Dominant fuel 2017", "Fleet composition", "fmin/fmax_perc constraints"),
    ("Technologies", "Transport", "TRUCK_DIESEL 90-100%", "fmin/max_perc", "~95% of trucks", "Near total dominance", "No electric trucks 2017", "fmin/fmax_perc"),
    ("Efficiency", "Boilers", "Wood/Coal boilers", "Standard DEA values", "2017 fleet older", "15-20% degradation noted", "REORG: efficiency degradation mentioned", "UNCLEAR if applied to Layers_in_out"),
    ("Costs", "All technologies", "c_inv / c_maint", "Mostly 2035 DEA defaults", "2017 costs different", "14 key techs fixed, 153 at 2035", "Relative ranking ~OK for calibration", "scripts/fix_technologies_errors.py"),
    ("Network", "Grid losses", "ELECTRICITY", "8.64% (global INDEP)", "~3% in Finland", "5.6pp overestimate", "Cannot override per country", "Structural limitation"),
]
write_table(ws, val_headers, val_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 13: Issues & Decisions Log
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("13_Issues_Decisions")

iss_headers = ["Date", "Issue", "Decision", "Rationale", "Status"]
iss_rows = [
    ("2026-01-26", "2017 demand data source", "Use JRC-IDEES/Eurostat 2015 as proxy", "Best available statistical data", "Closed"),
    ("2026-01-26", "Cost learning curves", "Use static 2035 costs for now", "No learning script in repo; impact low for calibration", "Open"),
    ("2026-02-10", "Transport/heat mode shares", "Set tight bands for all modal splits", "Force 2017 fleet composition", "Implemented"),
    ("2026-02-10", "Nuclear capacity", "Relaxed to 2.484-3.036 GW", "Originally fixed at 2.76; relaxed for solver flexibility", "Implemented"),
    ("2026-02-10", "HYDRO_RIVER capacity", "Set to 2.94-3.59 GW", "Updated from Statistics Finland", "Implemented"),
    ("2026-02-10", "Technology costs (14 key techs)", "Updated from DEA 2023 interpolated to 2017", "scripts/fix_technologies_errors.py", "Implemented"),
    ("2026-02-12", "Fuel switch constraint", "Force biomass >40% in IND, limit gas <20% in DHN", "Model prioritizes gas; reality biomass-dominated", "Implemented"),
    ("2026-02-12", "Electricity imports", "Allow 5GW (later 3GW) imports", "Model crashed without import capacity", "Implemented"),
    ("2026-02-14", "Feb14 calibration (Sankey match)", "Produced matching calibration plots", "plots/calibration_methodical_Feb14/", "Closed"),
    ("2026-02-17", "Fossil fuel prices updated", "Recalculated all 8 fossil prices", "Statistics Finland data validation", "Implemented"),
    ("2026-02-17", "JET_FUEL price", "Used 0.0359 instead of 0.0824", "High value likely tax-inclusive; 0.0359 = CIF spot", "Closed"),
    ("2026-02-17", "RE fuels disabled", "All 8 RE fuel carriers set to avail=0", "No RE fuel imports in 2017", "Implemented"),
    ("2026-02-18", "Complete audit", "15-check consistency run", "All checks pass except 2 demand discrepancies (7.4%, 5.9%)", "Documented"),
    ("2026-02-18", "Grid losses mismatch", "Documented as structural limitation", "INDEP 8.64% vs Finnish 3% — cannot override per country", "Open"),
    ("2026-02-18", "Efficiency degradation", "Unclear if applied", "REORG mentions 15-20% for 2017 fleet; not visible in current Layers_in_out", "Open"),
]
write_table(ws, iss_headers, iss_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 14: Consistency Checks
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("14_Consistency_Checks")

ws.cell(row=1, column=1, value="Automated Consistency Checks — 2025-02-18").font = TITLE_FONT
ws.merge_cells("A1:D1")

cc_headers = ["Check #", "Description", "Result", "Detail"]
cc_rows = [
    (1, "FI tech names subset of REF", "WARN", "CCGT_AMMONIA in FI but not parsed from REF (banned, no-op)"),
    (2, "f_min <= f_max (all rows)", "PASS", "All capacity bounds consistent"),
    (3, "fmin_perc <= fmax_perc (all rows)", "PASS", "All share constraints consistent"),
    (4, "Resource prices documented", "PASS", "6 local + 8 import prices all present and positive"),
    (5, "Misc share bounds in [0,1], min<=max", "PASS", "All 8 share pairs valid"),
    (6, "Demand magnitudes positive", "PASS", "All 11 end-uses positive"),
    (7, "FI Misc vs REF override documentation", "PASS", "21 overrides catalogued"),
    (8, "Network losses in [0, 0.2]", "PASS", "ELEC=0.0864, DHN=0.05"),
    (9, "Tightly constrained technologies", "INFO", "DAM_STORAGE, PHS at f_min=f_max=0.001 (expected)"),
    (10, "Disabled technologies", "PASS", "10+ techs banned (all geographically justified)"),
    (11, "Biomass CSV vs REORG workbook", "MATCH", "All 6 biomass resources identical"),
    (12, "Demands CSV vs REORG workbook", "WARN", "HEAT_LOW_T_HW +7.4%, MOBILITY_FREIGHT +5.9%"),
    (13, "fmin_perc > 0 usage", "PASS", "11 techs with forced minimum share"),
    (14, "fmax_perc < 1 usage", "PASS", "11 techs with capped maximum share"),
    (15, "RE fuels disabled", "PASS", "All 8 renewable fuel carriers at avail_exterior=0"),
]
r = write_table(ws, cc_headers, cc_rows, start_row=3)

# Color code
for row_idx in range(4, r):
    result_cell = ws.cell(row=row_idx, column=3)
    if result_cell.value == "PASS" or result_cell.value == "MATCH":
        result_cell.fill = PASS_FILL
    elif result_cell.value == "WARN":
        result_cell.fill = WARN_FILL
    elif result_cell.value == "FAIL":
        result_cell.fill = FAIL_FILL
    elif result_cell.value == "INFO":
        result_cell.fill = SUBHDR_FILL

auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 15: Active Resources
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("15_Active_Resources")

ar_headers = ["Resource", "Active", "Category", "avail_local", "avail_exterior", "c_op_local"]
ar_rows = []
for res_name in fi_res.index:
    name = str(res_name).strip()
    if not name or name == "nan":
        continue
    row = fi_res.loc[res_name]
    avl = row.get("avail_local", 0)
    avx = row.get("avail_exterior", 0)
    cop = row.get("c_op_local", 0)
    active = (avl > 0 or avx > 0)
    cat = ""
    if avl > 0 and avx == 0:
        cat = "Bio/Waste"
    elif avx > 0:
        cat = "Fossil/Import"
    else:
        cat = "Disabled"
    ar_rows.append([name, active, cat, avl, avx, cop])

write_table(ws, ar_headers, ar_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 16: Sources Library
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("16_Sources_Library")

sl_headers = ["Source_ID", "Source_Name", "URL", "Used_For", "Data_Year", "Notes"]
sl_rows = [
    ("SF_EA", "Statistics Finland — Energy Authority", "stat.fi", "Nuclear/wind/hydro capacity", "2017", ""),
    ("SF_ES", "Statistics Finland — Energy Statistics", "stat.fi", "Fuel prices, modal splits", "2017-2019", ""),
    ("FE_2024", "Finnish Energy (2024)", "energia.fi", "DHN share, DH/grid losses", "2020-2024", "Proxy years"),
    ("EF_2022", "Energy in Finland 2022", "doria.fi", "Grid losses (3%)", "2022", ""),
    ("JRC_IDEES", "JRC-IDEES / Eurostat", "ec.europa.eu", "End-use demands (11 sectors)", "2015", "Used as 2017 proxy"),
    ("ENTSOE", "ENTSO-E Transparency Platform", "entsoe.eu", "Hourly electricity profiles, interconnections", "2015-2017", ""),
    ("RN", "Renewables.ninja", "renewables.ninja", "Wind/solar hourly profiles", "2015", ""),
    ("DEA", "DEA Technology Catalogue 2023", "ens.dk", "Technology costs (c_inv, c_maint)", "2023 (interp to 2017)", "14 key techs updated"),
    ("NP", "NordPool", "nordpoolgroup.com", "Electricity import price", "2017", "~33 EUR/MWh"),
    ("EUROSTAT", "Eurostat Key Figures", "ec.europa.eu/eurostat", "Modal split, aviation", "2017-2019", ""),
    ("ENSPRESO", "ENSPRESO (JRC)", "ec.europa.eu/jrc", "Biomass potentials, solar/wind area", "2017", ""),
    ("REORG_WB", "Finland_MASTER_Calibration_REORG.xlsx", "Local", "Master calibration register", "2026", "9 sheets"),
]
write_table(ws, sl_headers, sl_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 17: Method Notes
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("17_Method_Notes")

ws.cell(row=1, column=1, value="Data Flow & Methodology").font = TITLE_FONT
ws.merge_cells("A1:D1")

method_headers = ["Stage", "Description", "Key Files", "Notes"]
method_rows = [
    ("1. Data Origin", "External sources (JRC-IDEES, stat.fi, DEA, ENSPRESO)", "Data/exogenous_data/regions/", "Country-specific raw data"),
    ("2. Preprocessing", "Transform external data into ESMC CSV format", "scripts/update_demands_from_regions.py, scripts/update_data_*", "Python pandas pipelines"),
    ("3. Tier Assembly", "Three-tier: INDEP -> REF_REGION -> FI overrides", "Data/2017/00_INDEP/, 02_REF_REGION/, FI/", "FI/ only has overrides, rest inherited"),
    ("4. Data Merge", "REF_REGION.deepcopy() then FI.update()", "esmc/preprocessing/preprocessing.py", "Cell-by-cell override on deepcopy"),
    ("5. Masking", "Values > 1e14 replaced with 'Infinity'", "esmc/preprocessing/dat_print.py", "AMPL uses Infinity keyword"),
    ("6. DAT Generation", "CSV -> AMPL .dat file", "esmc/preprocessing/dat_print.py", "print_df() function"),
    ("7. AMPL/CPLEX", "Solve LP whole-energy-system model", "esmc/energy_model/", "12 typical days, f_perc=True"),
    ("8. Post-processing", "Extract results, generate plots", "esmc/postprocessing/", "Sankey diagrams, cost breakdowns"),
]
write_table(ws, method_headers, method_rows, start_row=3)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 18: Change Log
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("18_Change_Log")

cl_headers = ["Date", "Author", "Change", "Files Affected", "Notes"]
cl_rows = [
    ("2026-01-26", "User", "Initial workbook creation", "Finland_MASTER_Calibration_old_UPDATED.xlsx", "Consolidated from previous calibration files"),
    ("2026-02-10", "User", "Transport/heat share constraints added", "Data/2017/FI/Technologies.csv, Misc.json", "fmin_perc/fmax_perc for transport, heat technologies"),
    ("2026-02-10", "User", "Nuclear relaxed to 2.484-3.036 GW", "Data/2017/FI/Technologies.csv", "Was fixed at 2.76"),
    ("2026-02-10", "User", "14 key tech costs updated", "Data/2017/02_REF_REGION/Technologies.csv", "DEA 2023 interpolated to 2017"),
    ("2026-02-12", "User", "Fuel switch constraints (biomass/coal)", "Data/2017/FI/Technologies.csv", "fmin_perc for IND_BOILER_WOOD, DHN_COGEN_WOOD/COAL"),
    ("2026-02-14", "User", "Feb14 calibration run (matched Sankey)", "plots/calibration_methodical_Feb14/", "Best calibration result to date"),
    ("2026-02-17", "Copilot", "Fossil fuel prices recalculated", "Data/2017/FI/Resources.csv", "All 8 prices from Statistics Finland"),
    ("2026-02-17", "Copilot", "URANIUM + ELECTRICITY prices added", "Data/2017/FI/Resources.csv", "0.0093 and 0.0326 MEUR/GWh"),
    ("2026-02-17", "Copilot", "JET_FUEL price corrected to 0.0359", "Data/2017/FI/Resources.csv", "Was 0.0824 (tax-inclusive error)"),
    ("2026-02-18", "Copilot", "Complete audit & consistency checks", "docs/finland_2017_*.md", "15 checks, 2 warnings, 0 errors"),
    ("2026-02-18", "Copilot", "Workbook rebuilt from scratch", "This file", "All sheets populated from actual CSV data + audit results"),
]
write_table(ws, cl_headers, cl_rows)
auto_width(ws)

# ┌─────────────────────────────────────────────────────────────────────────────
# │ Sheet 19: Assumptions & Decisions
# └─────────────────────────────────────────────────────────────────────────────
ws = wb.create_sheet("19_Assumptions_Decisions")

ad_headers = ["Topic", "Decision", "Rationale", "Impact", "Status"]
ad_rows = [
    ("Demand proxy year", "2015 JRC-IDEES used for 2017", "Best available data quality", "~2 year lag; acceptable", "Accepted"),
    ("Time series proxy", "2015 hourly profiles for 2017", "Consistent with demand year", "Weather differences possible", "Accepted"),
    ("Technology costs", "2035 DEA defaults (14 key techs fixed to 2017)", "No full 2017 cost dataset available", "Relative ranking approximately preserved", "Partial fix"),
    ("JET_FUEL price", "0.0359 instead of 0.0824 MEUR/GWh", "0.0824 likely tax-inclusive pump price", "Significant impact on aviation fuel cost", "Closed"),
    ("WOOD price", "0.022084 kept unchanged", "Per user instructions", "Biomass competitiveness preserved", "Closed"),
    ("Grid losses", "8.64% (global INDEP, cannot override)", "Model structural limitation", "Over-estimates electricity for Finland (~3% real)", "Open"),
    ("DH losses", "5% (global INDEP, cannot override)", "Model structural limitation", "Under-estimates heat for Finland (~8.5% real)", "Open"),
    ("Biomass forcing", "fmin_perc 30-40% for wood boilers/CHP", "Model prefers cheap gas; Finland biomass-dominant", "Forces realistic fuel mix", "Implemented"),
    ("Coal forcing", "fmin_perc 10-30% for coal CHP/boilers", "Sunk cost plants still running in 2017", "Prevents premature coal phase-out in model", "Implemented"),
    ("Gas capping", "fmax_perc 20% for gas CHP/boilers", "Gas share limited in 2017 Finland", "Prevents over-investment in gas", "Implemented"),
    ("EV penetration", "fmax_perc 1% BEV/PHEV, 5% HEV", "Negligible EV fleet in 2017", "Prevents anachronistic electrification", "Implemented"),
    ("RE fuels", "All 8 RE fuel carriers disabled (avail=0)", "No renewable fuel imports in 2017", "Prevents synthetic fuel pathways", "Implemented"),
    ("Nuclear flexibility", "f_min=2.484, f_max=3.036 (±10% of 2.76)", "Solver flexibility around known capacity", "Allows adjustment for c_p uncertainty", "Implemented"),
    ("k-medoids non-determinism", "12 typical days, no fixed seed", "Default ESMC config", "Different runs may give different results", "Known issue"),
    ("Efficiency degradation", "15-20% mentioned but unclear if applied", "REORG notes aging fleet penalty", "Would reduce boiler/CHP efficiency to ~2017 levels", "Open"),
    ("PEAT not modeled", "Peat not in resource list", "ESMC has no PEAT resource type", "Finland uses peat (~5% TPES); not represented", "Open"),
    ("OIL (HFO) as LFO proxy", "LFO used for all oil products", "No separate HFO resource", "Slight price/efficiency mismatch for heavy fuel oil", "Accepted"),
]
write_table(ws, ad_headers, ad_rows)
auto_width(ws)

# ══════════════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════════════
wb.save(OUT)
print(f"Workbook saved to: {OUT}")
print(f"Sheets: {wb.sheetnames}")
print(f"Total sheets: {len(wb.sheetnames)}")
