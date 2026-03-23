"""Dump all technology + resource costs used in the model."""
import pandas as pd
import csv
import os

# ── Technology costs from REF_REGION ─────────────────────────────────────────
tech = pd.read_csv("Data/2017/02_REF_REGION/Technologies.csv", skiprows=[1,2])
tech = tech.dropna(subset=["Technologies param"])
tech = tech.set_index("Technologies param")
tech.index = tech.index.astype(str).str.strip()

for col in ["c_inv", "c_maint", "lifetime", "c_p", "gwp_constr"]:
    tech[col] = pd.to_numeric(tech[col], errors="coerce")

tech = tech[~tech.index.duplicated(keep="first")]
active = tech[tech["c_inv"].notna()].sort_index()

print("=" * 110)
print("TECHNOLOGY COSTS (from Data/2017/02_REF_REGION/Technologies.csv)")
print("=" * 110)
header = "{:<30s} | {:>10s} | {:>10s} | {:>5s} | {:>6s} | {:>10s}".format(
    "Technology", "c_inv", "c_maint", "life", "c_p", "gwp_constr")
print(header)
units = "{:<30s} | {:>10s} | {:>10s} | {:>5s} | {:>6s} | {:>10s}".format(
    "", "MEUR/GW", "MEUR/GWa", "yrs", "", "ktCO2/GW")
print(units)
print("-" * 110)
for t in active.index:
    r = active.loc[t]
    gwp = float(r["gwp_constr"]) if pd.notna(r["gwp_constr"]) else 0.0
    line = "{:<30s} | {:>10.2f} | {:>10.2f} | {:>5.0f} | {:>6.4f} | {:>10.2f}".format(
        t, float(r["c_inv"]), float(r["c_maint"]), float(r["lifetime"]),
        float(r["c_p"]), gwp)
    print(line)

print(f"\nTotal technologies with cost data: {len(active)}")

# ── Resource costs from patches ──────────────────────────────────────────────
print("\n" + "=" * 80)
print("RESOURCE COSTS (from calibration/patches/restore_v9_baseline.csv)")
print("=" * 80)
print(f"{'Resource':<25s} | {'c_op_local':>12s} | {'Source'}")
print(f"{'':25s} | {'MEUR/GWh':>12s} |")
print("-" * 80)

res_costs = {}
with open("calibration/patches/restore_v9_baseline.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if "Resources" in row["file"] and "c_op" in row["parameter"]:
            res_costs[row["technology_or_resource"]] = float(row["value"])

for r_name in sorted(res_costs.keys()):
    print(f"{r_name:<25s} | {res_costs[r_name]:>12.6f} | restore_v9_baseline")

# ── Also from INDEP resources ────────────────────────────────────────────────
print("\n" + "=" * 80)
print("RESOURCE COSTS (from Data/2017/00_INDEP/Resources_indep.csv)")
print("=" * 80)
res_indep = pd.read_csv("Data/2017/00_INDEP/Resources_indep.csv", index_col=0)
print(res_indep.to_string())

# ── Check Layers_in_out for completeness ─────────────────────────────────────
print("\n" + "=" * 80)
print("LAYERS_IN_OUT (from Data/2017/00_INDEP/Layers_in_out.csv) — first 5 rows")
print("=" * 80)
lio = pd.read_csv("Data/2017/00_INDEP/Layers_in_out.csv", index_col=0)
print("Shape:", lio.shape)
print("Columns:", list(lio.columns)[:20], "...")
print(lio.iloc[:5, :8].to_string())

# ── Compare Excel sheet 05_Pricing_Pipeline vs actual resource costs ─────────
print("\n" + "=" * 80)
print("COMPARISON: Excel 05_Pricing_Pipeline vs Actual Patch Costs")
print("=" * 80)
excel_prices = {
    "GASOLINE": 0.06, "DIESEL": 0.05, "LFO": 0.05, "JET_FUEL": 0.05,
    "GAS": 0.02, "COAL": 0.015, "URANIUM": 0.005, "ELECTRICITY": 0.05,
}
for res in sorted(excel_prices.keys()):
    excel_val = excel_prices[res]
    actual_val = res_costs.get(res, None)
    if actual_val is not None:
        match = "OK" if abs(excel_val - actual_val) < 0.001 else f"MISMATCH (Excel={excel_val}, Actual={actual_val})"
        print(f"  {res:<20s}  Excel={excel_val:.4f}  Actual={actual_val:.4f}  {match}")
    else:
        print(f"  {res:<20s}  Excel={excel_val:.4f}  Actual=NOT IN PATCHES")
