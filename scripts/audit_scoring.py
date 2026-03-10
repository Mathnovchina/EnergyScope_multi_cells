"""Reproduce scoring logic step by step for stageA_verify baseline."""
import pandas as pd

base = "case_studies/FI/manual_runs/20260310_095416__stageA_verify/outputs"

res = pd.read_csv(f"{base}/Resources.csv", index_col="Resources")
yb = pd.read_csv(f"{base}/Year_balance.csv", index_col="Elements")

def r_total(name):
    if name not in res.index:
        return 0
    row = res.loc[name]
    return row.get("R_year_local", 0) + row.get("R_year_exterior", 0)

pe = {
    "PE_BIOMASS": sum(r_total(r) for r in ["WOOD","WET_BIOMASS","BIOWASTE","BIOMASS_RESIDUES","ENERGY_CROPS_2"]) / 1000,
    "PE_OIL": sum(r_total(r) for r in ["GASOLINE","DIESEL","LFO","JET_FUEL"]) / 1000,
    "PE_GAS": r_total("GAS") / 1000,
    "PE_COAL": r_total("COAL") / 1000,
    "PE_NUCLEAR": r_total("URANIUM") / 1000,
    "PE_HYDRO": r_total("RES_HYDRO") / 1000,
    "PE_WIND": r_total("RES_WIND") / 1000,
}

targets = {
    "PE_BIOMASS": 100.0, "PE_OIL": 82.0, "PE_GAS": 20.0, "PE_COAL": 35.0,
    "PE_NUCLEAR": 65.0, "PE_HYDRO": 15.0, "PE_WIND": 5.0,
    "ELEC_NUCLEAR": 21.6, "ELEC_HYDRO": 14.6, "ELEC_WIND": 4.8,
    "ELEC_CHP": 20.735, "ELEC_CONDENSATION": 3.284, "ELEC_SOLAR": 0.044,
    "CO2": 41.2,
}

print("=== PRIMARY ENERGY (TWh) ===")
for k, v in pe.items():
    print(f"  {k:<15} {v:>8.2f}  (target: {targets[k]:.1f})")

def elec(techs):
    return sum(max(0.0, float(yb.loc[t, "ELECTRICITY"])) for t in techs if t in yb.index) / 1000

chp = ["DHN_COGEN_GAS","DHN_COGEN_WOOD","DHN_COGEN_COAL","DHN_COGEN_WASTE","DHN_COGEN_OIL",
       "IND_COGEN_GAS","IND_COGEN_WOOD","IND_COGEN_COAL","IND_COGEN_WASTE",
       "DEC_COGEN_GAS","DEC_COGEN_OIL","DEC_ADVCOGEN_GAS","DEC_ADVCOGEN_H2"]
cond = ["CCGT","OCGT","COAL_US","COAL_IGCC","CCGT_AMMONIA","BIOMASS_TO_POWER"]

elec_metrics = {
    "ELEC_NUCLEAR": elec(["NUCLEAR"]),
    "ELEC_HYDRO": elec(["HYDRO_DAM","HYDRO_RIVER"]),
    "ELEC_WIND": elec(["WIND_ONSHORE","WIND_OFFSHORE"]),
    "ELEC_SOLAR": elec(["PV_ROOFTOP","PV_UTILITY"]),
    "ELEC_CHP": elec(chp),
    "ELEC_CONDENSATION": elec(cond),
}

print("\n=== ELECTRICITY (TWh) ===")
for k, v in elec_metrics.items():
    print(f"  {k:<20} {v:>8.3f}  (target: {targets[k]:.3f})")

print("\n--- CHP breakdown ---")
for t in chp:
    if t in yb.index:
        val = float(yb.loc[t, "ELECTRICITY"])
        if abs(val) > 0.001:
            print(f"  {t}: {val:.1f} GWh = {val/1000:.3f} TWh")

print("\n--- Condensation breakdown ---")
for t in cond:
    if t in yb.index:
        val = float(yb.loc[t, "ELECTRICITY"])
        if abs(val) > 0.001:
            print(f"  {t}: {val:.1f} GWh = {val/1000:.3f} TWh")

gwp = pd.read_csv(f"{base}/Gwp_breakdown.csv")
co2_col = "CO2_net" if "CO2_net" in gwp.columns else "GWP_op"
co2_mt = gwp[co2_col].sum() / 1000
print(f"\n=== CO2: {co2_mt:.2f} MtCO2  (target: 41.2) ===")

print("\n=== SCORE RECALCULATION ===")
all_m = {**pe, **elec_metrics, "CO2": co2_mt}
weights = {
    "PE_BIOMASS": 1.5, "PE_OIL": 1.5, "PE_GAS": 1.0, "PE_COAL": 1.5,
    "PE_NUCLEAR": 1.0, "PE_HYDRO": 0.8, "PE_WIND": 0.8,
    "ELEC_NUCLEAR": 1.5, "ELEC_HYDRO": 1.2, "ELEC_WIND": 1.0,
    "ELEC_CHP": 1.2, "ELEC_CONDENSATION": 0.8, "ELEC_SOLAR": 0.3,
    "CO2": 2.0,
}
wsum, wtot = 0, 0
for k, (tgt, w) in sorted(zip(targets.keys(), zip(targets.values(), [weights[k] for k in targets]))):
    k2 = sorted(targets.keys())[sorted(zip(targets.keys(), zip(targets.values(), [weights[k] for k in targets]))).index((k, (tgt, w)))]
# Simpler approach
for k in sorted(targets.keys()):
    tgt = targets[k]
    w = weights[k]
    model_val = all_m.get(k, 0)
    err = abs(model_val - tgt) / tgt * 100
    contrib = err * w
    wsum += contrib
    wtot += w
    binding = ""
    if k == "PE_WIND":
        binding = " <-- ROOT CAUSE"
    print(f"  {k:<20} model={model_val:>8.2f}  target={tgt:>8.1f}  err={err:>7.1f}%  w={w}  contrib={contrib:.1f}")
    
score = wsum / wtot
print(f"\nFINAL SCORE: {score:.1f}%")
