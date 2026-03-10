"""Compare wind allocations between Block 1 and Block 2."""
import pandas as pd

for label, path in [
    ("BLOCK 1 (pre-wind)", "case_studies/FI/manual_runs/20260310_140633__block1_nuclear_v2/outputs"),
    ("BLOCK 2 (wind constrained)", "case_studies/FI/manual_runs/20260310_142104__block2_wind_from_block1/outputs"),
]:
    assets = pd.read_csv(path + "/Assets.csv")
    print(f"=== {label} ===")
    for _, row in assets.iterrows():
        tech = row.iloc[0]
        if "WIND" in str(tech):
            F = row["F"]
            fmin = row["f_min"]
            fmax = row["f_max"]
            fyear = row["F_year"]
            print(f"  {tech:20s}  F={F:8.3f} GW  f_min={fmin:.1f}  f_max={fmax:.1f}  F_year={fyear:10.1f} GWh")
    print()

print("=== FINLAND 2017 REALITY ===")
print("  WIND_ONSHORE:  ~2.0 GW installed, ~4.8 TWh generation")
print("  WIND_OFFSHORE: ~0 GW (essentially no offshore wind in 2017)")
print()
print("=== KEY FINDING ===")
print("In Block 1 (no wind constraint): model chose ~25 GW wind total")
print("  -> mainly WIND_ONSHORE at max bound")
print("In Block 2 (WIND_ONSHORE capped at 2.1 GW): model shifted to")
print("  WIND_OFFSHORE at ~24 GW (unconstrained, max=25 GW)")
print("  -> total wind generation only dropped slightly because OFFSHORE compensated")
print()
print("The ELEC_WIND/PE_WIND metrics sum ONSHORE + OFFSHORE.")
print("To reduce total wind to reality (~5 TWh), WIND_OFFSHORE must also be constrained.")
