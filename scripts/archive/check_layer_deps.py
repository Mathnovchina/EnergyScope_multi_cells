"""Quick check of critical layer dependencies for the staged disable table."""
import pandas as pd

lio = pd.read_csv("Data/2017/00_INDEP/Layers_in_out.csv", index_col=0)
lio.columns = lio.columns.str.strip()
lio.index = lio.index.str.strip()

for layer in ["H2", "CO2_CAPTURED", "AMMONIA", "METHANOL", "HVC", "GAS"]:
    if layer not in lio.columns:
        print(f"--- {layer}: NOT IN LAYERS ---")
        continue
    prod = lio[lio[layer] > 0]
    cons = lio[lio[layer] < 0]
    print(f"=== {layer} PRODUCERS ({len(prod)}) ===")
    for t in prod.index:
        val = prod.loc[t, layer]
        print(f"  {t}: {val}")
    print(f"=== {layer} CONSUMERS ({len(cons)}) ===")
    for t in cons.index:
        val = cons.loc[t, layer]
        print(f"  {t}: {val}")
    print()
