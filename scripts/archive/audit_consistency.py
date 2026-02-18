"""
Finland 2017 Calibration - Comprehensive Consistency Audit
Compares: Model CSVs vs Regions (ENSPRESO/JRC) vs REORG Workbook vs REF defaults
"""
import pandas as pd
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("FINLAND 2017 CALIBRATION - COMPREHENSIVE CONSISTENCY AUDIT")
print("=" * 80)

# ─────────────────────────────────────────────────
# Load all data sources
# ─────────────────────────────────────────────────
md = pd.read_csv(os.path.join(BASE, "Data/2017/FI/Demands.csv"))
mr = pd.read_csv(os.path.join(BASE, "Data/2017/FI/Resources.csv"), index_col=0)
mt = pd.read_csv(os.path.join(BASE, "Data/2017/FI/Technologies.csv"), index_col=0)
with open(os.path.join(BASE, "Data/2017/FI/Misc.json")) as f:
    misc = json.load(f)
with open(os.path.join(BASE, "Data/2017/00_INDEP/Misc_indep.json")) as f:
    mi = json.load(f)

rd = pd.read_csv(os.path.join(BASE, "Data/exogenous_data/regions/Demands.csv"), index_col=[0, 1, 2])
rd_fi = rd.xs("FI", level=1).xs(2015, level=0)

rr = pd.read_csv(os.path.join(BASE, "Data/exogenous_data/regions/Resources.csv"))
rr_fi_av = rr[rr["Unnamed: 1"] == "FI"].iloc[0]
rr_fi_cop = rr[rr["Unnamed: 1"] == "FI"].iloc[1]

rt = pd.read_csv(os.path.join(BASE, "Data/exogenous_data/regions/Technologies.csv"))
rt_fi_fmin = rt[rt["Unnamed: 1"] == "FI"].iloc[0]
rt_fi_fmax = rt[rt["Unnamed: 1"] == "FI"].iloc[1]

anomalies = []

# ─────────────────────────────────────────────────
# A) DEMANDS
# ─────────────────────────────────────────────────
print("\n## A) DEMANDS: Model CSV vs Regions (2015 source) vs REORG Workbook")

reorg_d = {
    "ELECTRICITY": 42911.451, "HEAT_HIGH_T": 59964.823,
    "HEAT_LOW_T_SH": 86661.011, "HEAT_LOW_T_HW": 18967.072,
    "PROCESS_COOLING": 3766.199, "SPACE_COOLING": 2046.707,
    "MOBILITY_PASSENGER": 91991.773, "MOBILITY_FREIGHT": 34442.431,
    "AVIATION_LONG_HAUL": 14871.539, "SHIPPING": 156651.655,
    "NON_ENERGY": 10503.705,
}

for _, row in md.iterrows():
    name = row["parameter name"]
    mt_tot = row["HOUSEHOLDS"] + row["SERVICES"] + row["INDUSTRY"] + row["TRANSPORTATION"]
    rg_tot = rd_fi.loc[name].sum() if name in rd_fi.index else float("nan")
    reo = reorg_d.get(name, float("nan"))

    m1 = "ok" if abs(mt_tot - rg_tot) < 50 else "D={:+.0f}".format(mt_tot - rg_tot)
    m2 = "ok" if abs(mt_tot - reo) < 50 else "D={:+.0f}".format(mt_tot - reo)

    print("  {:<25} model={:>12.1f}  reg2015={:>12.1f} [{:>10}]  reorg={:>12.1f} [{:>10}]".format(
        name, mt_tot, rg_tot, m1, reo, m2))

    if abs(mt_tot - rg_tot) > 100:
        anomalies.append("DEMAND {}: model={:.0f} vs source={:.0f} (delta={:+.0f})".format(
            name, mt_tot, rg_tot, mt_tot - rg_tot))

# ─────────────────────────────────────────────────
# B) BIOMASS RESOURCES
# ─────────────────────────────────────────────────
print("\n## B) BIOMASS RESOURCES: Model vs Regions ENSPRESO defaults")

for res in ["WOOD", "WET_BIOMASS", "ENERGY_CROPS_2", "BIOWASTE", "BIOMASS_RESIDUES", "WASTE"]:
    mv = mr.loc[res, "avail_local"] if res in mr.index else 0
    rv = rr_fi_av[res] if res in rr_fi_av.index else 0
    mc = mr.loc[res, "c_op_local"] if res in mr.index else 0
    cv = rr_fi_cop[res] if res in rr_fi_cop.index else 0
    d = mv - rv
    cost_ok = "ok" if abs(mc - cv) < 0.0001 else "DIFF"
    print("  {:<20} avail: model={:>12.2f}  reg={:>12.2f}  delta={:>10.2f}  cost: model={:.6f}  reg={:.6f}  [{}]".format(
        res, mv, rv, d, mc, cv, cost_ok))

    if abs(d) > 10:
        anomalies.append("RESOURCE {}: model={:.0f} vs regions={:.0f} (delta={:+.0f})".format(
            res, mv, rv, d))

# ─────────────────────────────────────────────────
# C) IMPORT PRICES
# ─────────────────────────────────────────────────
print("\n## C) IMPORT PRICES: Model c_op_local vs REORG Final Prices vs REF defaults")

reorg_p = {
    "GASOLINE": 0.0588, "DIESEL": 0.0543, "LFO": 0.0521,
    "JET_FUEL": 0.0359, "GAS": 0.0195, "COAL": 0.0103,
    "URANIUM": 0.0093, "ELECTRICITY": 0.0326,
}
ref_p = {
    "GASOLINE": 0.06, "DIESEL": 0.057, "LFO": 0.055,
    "JET_FUEL": 0.082366, "GAS": 0.02, "COAL": 0.01,
    "URANIUM": 0.003876, "ELECTRICITY": 0.0332,
}

for res in reorg_p:
    mv = mr.loc[res, "c_op_local"] if res in mr.index else float("nan")
    rp = reorg_p[res]
    rfp = ref_p.get(res, float("nan"))
    m = "MATCH" if abs(mv - rp) < 0.001 else "DIFFERS"
    print("  {:<15} model={:.4f}  reorg={:.4f}  REF={:.4f}  [{}]".format(res, mv, rp, rfp, m))

# ─────────────────────────────────────────────────
# D) KEY TECHNOLOGIES
# ─────────────────────────────────────────────────
print("\n## D) KEY TECHNOLOGIES: Model vs Regions ENSPRESO vs REORG Workbook")

reorg_t = {
    "NUCLEAR": (2.76, 2.76), "PV_ROOFTOP": (0.02, 2), "PV_UTILITY": (0, 1),
    "WIND_ONSHORE": (1.5, 5), "WIND_OFFSHORE": (0, 0),
    "HYDRO_DAM": (1.345, 2.383), "HYDRO_RIVER": (3.264, 3.264),
    "GEOTHERMAL": (0, 0.3),
}

for tech in ["NUCLEAR", "PV_ROOFTOP", "PV_UTILITY", "WIND_ONSHORE", "WIND_OFFSHORE",
             "HYDRO_DAM", "HYDRO_RIVER", "GEOTHERMAL"]:
    mfn = mt.loc[tech, "f_min"] if tech in mt.index else 0
    mfx = mt.loc[tech, "f_max"] if tech in mt.index else 0
    rfn = rt_fi_fmin[tech] if tech in rt_fi_fmin.index else 0
    rfx = rt_fi_fmax[tech] if tech in rt_fi_fmax.index else 0

    reorg_str = ""
    if tech in reorg_t:
        rr_fn, rr_fx = reorg_t[tech]
        reorg_str = "reorg=[{},{}]".format(rr_fn, rr_fx)
    print("  {:<20} model=[{:.3f},{:.3f}]  reg=[{:.3f},{:.3f}]  {}".format(
        tech, mfn, mfx, rfn, rfx, reorg_str))

# ─────────────────────────────────────────────────
# E) MISC.JSON SHARES
# ─────────────────────────────────────────────────
print("\n## E) MISC.JSON SHARES")

shares = {
    "share_heat_dhn": 0.45,
    "share_freight_train": 0.277,
    "share_mobility_public": 0.162,
}
for s, v in shares.items():
    mx = misc.get(s + "_max", 0)
    mn = misc.get(s + "_min", 0)
    mid = (mx + mn) / 2
    print("  {:<30} model=[{:.3f},{:.3f}]  REORG={:.3f}  mid={:.3f}".format(s, mn, mx, v, mid))

# ─────────────────────────────────────────────────
# F) NETWORK LOSSES
# ─────────────────────────────────────────────────
print("\n## F) NETWORK LOSSES (Misc_indep vs REORG documented FI values)")
e_loss = mi["loss_network"]["ELECTRICITY"]
h_loss = mi["loss_network"]["HEAT_LOW_T_DHN"]
print("  Misc_indep (used by model): ELECTRICITY={}, HEAT_LOW_T_DHN={}".format(e_loss, h_loss))
print("  REORG workbook (FI-specific): Loss(Elec)=0.03, Loss(HeatLowTDhn)=0.085")
print("  STATUS: MISMATCH - Misc_indep has REF defaults, not FI-calibrated values")
print("  IMPACT: Model uses {:.1f}% elec loss instead of 3%, and {:.1f}% DHN loss instead of 8.5%".format(
    e_loss * 100, h_loss * 100))
anomalies.append("LOSSES: Misc_indep ELEC={:.1f}%/DHN={:.1f}% vs REORG FI=3%/8.5% (NOT OVERRIDDEN)".format(
    e_loss * 100, h_loss * 100))

# ─────────────────────────────────────────────────
# G) MARKET SHARE CONSTRAINTS
# ─────────────────────────────────────────────────
print("\n## G) MARKET SHARE CONSTRAINTS (fmin_perc / fmax_perc)")

has_fmin_perc = "fmin_perc" in mt.columns
has_fmax_perc = "fmax_perc" in mt.columns
print("  Columns present: fmin_perc={}, fmax_perc={}".format(has_fmin_perc, has_fmax_perc))

if has_fmin_perc or has_fmax_perc:
    mask = pd.Series(False, index=mt.index)
    if has_fmin_perc:
        mask = mask | (mt["fmin_perc"] > 0)
    if has_fmax_perc:
        mask = mask | (mt["fmax_perc"] < 1)
    constrained = mt[mask]
    for tech in constrained.index:
        fp_min = mt.loc[tech, "fmin_perc"] if has_fmin_perc else 0.0
        fp_max = mt.loc[tech, "fmax_perc"] if has_fmax_perc else 1.0
        if fp_min > 0 or fp_max < 1:
            print("  {:<25} fmin_perc={:.2f}  fmax_perc={:.2f}".format(tech, fp_min, fp_max))
    anomalies.append("{} techs have non-default fmin_perc/fmax_perc constraints".format(len(constrained)))
else:
    print("  No fmin_perc/fmax_perc columns found (Feb14 style - no market share constraints)")
    anomalies.append("Technologies.csv has no fmin_perc/fmax_perc columns")

# ─────────────────────────────────────────────────
# H) UNCAPPED IMPORTS
# ─────────────────────────────────────────────────
print("\n## H) UNCAPPED IMPORTS (exterior = 1e15)")

for res in mr.index:
    ext = mr.loc[res, "avail_exterior"]
    if ext > 1e10:
        print("  {:<20} avail_exterior={:.0e}  c_op_local={:.4f}".format(res, ext, mr.loc[res, "c_op_local"]))
        if res in ["GASOLINE", "DIESEL", "LFO", "GAS", "COAL"]:
            anomalies.append("IMPORT {}: uncapped (1e15) - no binding constraint on volume".format(res))

# ─────────────────────────────────────────────────
# I) NUCLEAR CONSTRAINT CHECK
# ─────────────────────────────────────────────────
print("\n## I) NUCLEAR CONSTRAINT EVOLUTION")
n_fmin = mt.loc["NUCLEAR", "f_min"]
n_fmax = mt.loc["NUCLEAR", "f_max"]
print("  Current model:  [{}, {}]".format(n_fmin, n_fmax))
print("  REORG workbook: [2.76, 2.76]  (fixed)")
print("  Feb14 repro:    [2.484, 3.036] (relaxed +/-10%)")
print("  Regions ENSPRESO: f_min=0, f_max=0")
if abs(n_fmin - 2.76) > 0.01 or abs(n_fmax - 2.76) > 0.01:
    anomalies.append("NUCLEAR: model=[{},{}] differs from REORG [2.76,2.76] and Feb14 [2.484,3.036]".format(
        n_fmin, n_fmax))

# ─────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────
print("\n" + "=" * 80)
print("ANOMALIES SUMMARY ({} total)".format(len(anomalies)))
print("=" * 80)

for i, a in enumerate(anomalies, 1):
    print("  [{:2d}] {}".format(i, a))

print("\n--- END OF AUDIT ---")
