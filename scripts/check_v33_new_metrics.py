"""Quick sanity-check: score v33 outputs with the expanded metric set."""
import pandas as pd
from pathlib import Path

outdir = Path("case_studies/FI/manual_runs/20260323_134343__v33_oil_biomass3/outputs")

REALITY_TARGETS = {
    "PE_BIOMASS":        (100.0,  1.5),
    "PE_OIL":            (82.0,   1.5),
    "PE_GAS":            (20.0,   1.0),
    "PE_COAL":           (35.0,   1.5),
    "PE_NUCLEAR":        (65.0,   1.0),
    "PE_HYDRO":          (15.0,   0.8),
    "PE_WIND":           (5.0,    0.8),
    "ELEC_NUCLEAR":      (21.6,   1.5),
    "ELEC_HYDRO":        (14.6,   1.2),
    "ELEC_WIND":         (4.8,    1.0),
    "ELEC_CHP":          (20.735, 1.2),
    "ELEC_CONDENSATION": (3.284,  0.8),
    "ELEC_SOLAR":        (0.044,  0.3),
    "CO2":               (41.2,   2.0),
    "ELEC_GAS":          (3.2,    0.0),   # informational: structurally over-produced
    "ELEC_IMPORTS":      (20.426, 0.0),   # new: informational
    "HEAT_DHN":          (36.5,   0.0),   # new: informational
}

m = {}

df = pd.read_csv(outdir / "Resources.csv")
lookup = {r["Resources"]: r.get("R_year_local", 0) + r.get("R_year_exterior", 0)
          for _, r in df.iterrows()}
m["PE_BIOMASS"] = sum(lookup.get(r, 0) for r in
    ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"]) / 1000
m["PE_OIL"]    = sum(lookup.get(r, 0) for r in
    ["GASOLINE", "DIESEL", "LFO", "JET_FUEL"]) / 1000
m["PE_GAS"]     = lookup.get("GAS", 0) / 1000
m["PE_COAL"]    = lookup.get("COAL", 0) / 1000
m["PE_NUCLEAR"] = lookup.get("URANIUM", 0) / 1000
m["PE_HYDRO"]   = lookup.get("RES_HYDRO", 0) / 1000
m["PE_WIND"]    = lookup.get("RES_WIND", 0) / 1000

elec_ext = df.loc[df["Resources"] == "ELECTRICITY", "R_year_exterior"]
m["ELEC_IMPORTS"] = float(elec_ext.iloc[0]) / 1000 if not elec_ext.empty else 0.0

yb = pd.read_csv(outdir / "Year_balance.csv", index_col="Elements")

def elec(techs):
    return sum(max(0.0, float(yb.loc[t, "ELECTRICITY"]))
               for t in techs if t in yb.index) / 1000

m["ELEC_NUCLEAR"]  = elec(["NUCLEAR"])
m["ELEC_HYDRO"]    = elec(["HYDRO_DAM", "HYDRO_RIVER"])
m["ELEC_WIND"]     = elec(["WIND_ONSHORE", "WIND_OFFSHORE"])
m["ELEC_SOLAR"]    = elec(["PV_ROOFTOP", "PV_UTILITY"])

chp_techs = [
    "DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL",
    "DHN_COGEN_WASTE", "DHN_COGEN_OIL",
    "IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_COAL", "IND_COGEN_WASTE",
    "DEC_COGEN_GAS", "DEC_COGEN_OIL", "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2",
]
m["ELEC_CHP"] = elec(chp_techs)
cond_techs = ["CCGT", "OCGT", "COAL_US", "COAL_IGCC", "CCGT_AMMONIA", "BIOMASS_TO_POWER"]
m["ELEC_CONDENSATION"] = elec(cond_techs)

gas_elec_techs = ["DHN_COGEN_GAS", "IND_COGEN_GAS", "DEC_COGEN_GAS",
                  "DEC_ADVCOGEN_GAS", "CCGT", "OCGT"]
m["ELEC_GAS"] = elec(gas_elec_techs)

if "HEAT_LOW_T_DHN" in yb.columns:
    dhn_col = yb["HEAT_LOW_T_DHN"]
    m["HEAT_DHN"] = float(dhn_col[dhn_col > 0].sum()) / 1000

gwp = pd.read_csv(outdir / "Gwp_breakdown.csv")
m["CO2"] = (gwp["CO2_net"].sum() if "CO2_net" in gwp.columns
            else gwp["GWP_op"].sum()) / 1000

# Score
ws, wt = 0.0, 0.0
results = {}
for k, (target, w) in REALITY_TARGETS.items():
    if k in m and target > 0:
        err = abs(m[k] - target) / target * 100
        results[k] = {"model": m[k], "target": target, "err": err, "w": w}
        ws += err * w
        wt += w
score = ws / wt

info_keys = {k for k, (_, w) in REALITY_TARGETS.items() if w == 0}
print(f"\n{'='*62}")
print(f"  V33 re-scored with expanded dashboard")
print(f"  SCORE: {score:.2f}%  ({len(REALITY_TARGETS)-len(info_keys)} scored metrics)")
print(f"{'='*62}")
print(f"  {'Metric':<22} {'Model':>8} {'Target':>8} {'Error':>8}")
print(f"  {'-'*52}")
for k in sorted(results):
    if k in info_keys:
        continue
    i = results[k]
    print(f"  {k:<22} {i['model']:>8.2f} {i['target']:>8.1f} {i['err']:>7.1f}%")
info_present = [k for k in sorted(results) if k in info_keys]
if info_present:
    print(f"  {'--- informational (not scored) ---':^52}")
    for k in info_present:
        i = results[k]
        print(f"  {k:<22} {i['model']:>8.2f} {i['target']:>8.1f} {i['err']:>7.1f}%  [info]")
print()
