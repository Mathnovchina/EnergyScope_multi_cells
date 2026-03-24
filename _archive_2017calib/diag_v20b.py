import pandas as pd, pathlib

run = pathlib.Path("case_studies/FI/manual_runs/20260316_130543__v20_disable_biomass_hvc")
yb  = pd.read_csv(run / "outputs" / "Year_balance.csv", index_col=0)
ass = pd.read_csv(run / "outputs" / "Assets.csv", index_col=0)
gwp = pd.read_csv(run / "outputs" / "Gwp_breakdown.csv")
res_df = pd.read_csv(run / "outputs" / "Resources.csv")

res = {}
for _, row in res_df.iterrows():
    tot = float(row.get("R_year_local", 0)) + float(row.get("R_year_exterior", 0))
    res[str(row.iloc[0])] = tot / 1000

def elec(techs):
    return sum(max(0, float(yb.loc[t, "ELECTRICITY"])) for t in techs
               if t in yb.index and "ELECTRICITY" in yb.columns) / 1000

REALITY = {
    "PE_BIOMASS":        (100.0, 1.5),
    "PE_OIL":            (82.0,  1.5),
    "PE_GAS":            (20.0,  1.0),
    "PE_COAL":           (35.0,  1.5),
    "PE_NUCLEAR":        (65.0,  1.0),
    "PE_HYDRO":          (15.0,  0.8),
    "PE_WIND":           (5.0,   0.8),
    "ELEC_NUCLEAR":      (21.6,  1.5),
    "ELEC_HYDRO":        (14.6,  1.2),
    "ELEC_WIND":         (4.8,   1.0),
    "ELEC_CHP":          (20.735, 1.2),
    "ELEC_CONDENSATION": (3.284, 0.8),
    "ELEC_SOLAR":        (0.044, 0.3),
    "CO2":               (41.2,  2.0),
}
chp_techs  = ["DHN_COGEN_GAS","DHN_COGEN_WOOD","DHN_COGEN_COAL","DHN_COGEN_WASTE",
              "DHN_COGEN_OIL","IND_COGEN_GAS","IND_COGEN_WOOD","IND_COGEN_COAL",
              "IND_COGEN_WASTE","DEC_COGEN_GAS","DEC_COGEN_OIL","DEC_ADVCOGEN_GAS","DEC_ADVCOGEN_H2"]
cond_techs = ["CCGT","OCGT","COAL_US","COAL_IGCC","CCGT_AMMONIA","BIOMASS_TO_POWER"]

m = {
    "PE_BIOMASS": sum(res.get(r,0) for r in ["WOOD","WET_BIOMASS","BIOWASTE","BIOMASS_RESIDUES","ENERGY_CROPS_2"]),
    "PE_OIL":     sum(res.get(r,0) for r in ["GASOLINE","DIESEL","LFO","JET_FUEL"]),
    "PE_GAS":     res.get("GAS", 0),
    "PE_COAL":    res.get("COAL", 0),
    "PE_NUCLEAR": res.get("URANIUM", 0),
    "PE_HYDRO":   res.get("RES_HYDRO", 0),
    "PE_WIND":    res.get("RES_WIND", 0),
    "ELEC_NUCLEAR":      elec(["NUCLEAR"]),
    "ELEC_HYDRO":        elec(["HYDRO_DAM","HYDRO_RIVER"]),
    "ELEC_WIND":         elec(["WIND_ONSHORE","WIND_OFFSHORE"]),
    "ELEC_CHP":          elec(chp_techs),
    "ELEC_CONDENSATION": elec(cond_techs),
    "ELEC_SOLAR":        elec(["PV_ROOFTOP","PV_UTILITY"]),
    "CO2":               gwp["CO2_net"].sum() / 1000,
}

print("="*70)
print("SCORECARD v20")
rows = [(k, m.get(k,0.0), tgt, w) for k,(tgt,w) in REALITY.items()]
rows_s = sorted(rows, key=lambda x: -abs(x[2]-x[1])/x[2]*100)
total_we = total_w = 0.0
print("  %-22s %8s %8s %7s %4s %8s" % ("Metric","Model","Target","Error%","W","WxErr"))
print("-"*70)
for k,mv,tgt,w in rows_s:
    err = abs(mv-tgt)/tgt*100; we = err*w; total_we+=we; total_w+=w
    flag = " <<<" if err>15 else (" ok" if err<6 else "")
    print("  %-22s %8.2f %8.1f %6.1f%% %4.1f %8.2f%s" % (k,mv,tgt,err,w,we,flag))
print("-"*70)
print("  %-22s %8s %8s %6.1f%% %4.1f" % ("SCORE","","",total_we/total_w,total_w))

print()
print("="*70)
print("CHP BREAKDOWN  gap=%.2f TWh to fill" % (20.735-m["ELEC_CHP"]))
print("="*70)
for t in chp_techs:
    if t in yb.index and "ELECTRICITY" in yb.columns:
        v = yb.loc[t,"ELECTRICITY"]
        if abs(v)>1:
            cap = ass.loc[t,"F"] if (t in ass.index and "F" in ass.columns) else float("nan")
            hc = "HEAT_LOW_T_DHN" if "DHN" in t else "HEAT_HIGH_T"
            h = yb.loc[t,hc]/1000 if hc in yb.columns else 0
            print("  %-35s elec=%+.3f  heat=%.2f  F=%.3f GW" % (t,v/1000,h,cap))

print()
print("="*70)
cap_w = ass.loc["WIND_ONSHORE","F"] if ("WIND_ONSHORE" in ass.index and "F" in ass.columns) else 0
gen_w = elec(["WIND_ONSHORE"])
cp_w  = gen_w/(cap_w*8.76)*100 if cap_w>0 else 0
need  = 4.8/(gen_w/cap_w) if cap_w>0 else 0
print("WIND  target=4.8  model=%.2f  excess=%.2f TWh" % (m["ELEC_WIND"],m["ELEC_WIND"]-4.8))
print("  WIND_ONSHORE: F=%.3f GW  gen=%.3f TWh  cp=%.1f%%" % (cap_w,gen_w,cp_w))
print("  To hit 4.8 TWh => fmax ~ %.3f GW" % need)

print()
print("="*70)
print("OIL  target=82.0  model=%.2f  gap=%.2f TWh" % (m["PE_OIL"],82-m["PE_OIL"]))
print("="*70)
for r in ["LFO","DIESEL","GASOLINE","JET_FUEL"]:
    if r in res: print("  %-15s %.2f TWh" % (r,res[r]))
print("LFO by tech:")
if "LFO" in yb.columns:
    for idx,v in yb["LFO"].sort_values().items():
        if abs(v)>10: print("  %-35s %+.3f TWh" % (idx,v/1000))

print()
print("="*70)
print("GAS  target=20.0  model=%.2f  excess=%.2f TWh (cap=22000 GWh)" % (m["PE_GAS"],m["PE_GAS"]-20))
print("="*70)
if "GAS" in yb.columns:
    for idx,v in yb["GAS"].sort_values().items():
        if abs(v)>50: print("  %-35s %+.3f TWh" % (idx,v/1000))

print()
print("="*70)
print("BIOMASS  target=100.0  model=%.2f TWh" % m["PE_BIOMASS"])
print("="*70)
for r in ["WOOD","WET_BIOMASS","BIOWASTE","BIOMASS_RESIDUES","ENERGY_CROPS_2"]:
    if r in res and res[r]>0.01: print("  %-20s %.2f TWh" % (r,res[r]))
print("WOOD by tech:")
if "WOOD" in yb.columns:
    for idx,v in yb["WOOD"].sort_values().items():
        if abs(v)>100: print("  %-35s %+.3f TWh" % (idx,v/1000))
