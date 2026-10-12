"""Read-only summary of the S2BIOM Finland country file (forest and wood-industry streams).

Reads Data/exogenous_data/S2biom/data_FI.xlsx and prints national totals by biomass type,
potential and year, converted to energy, plus road-side cost per type and a cost-supply curve.
Writes CSV tables to --out (default: not written). Changes no model, data or run.

Energy conversion is NOT in the S2BIOM documents (D1.6/D1.8 give kton dry matter only, except
post-consumer wood). The factors below are explicit, editable assumptions (LHV on dry basis).
"""
import argparse
from pathlib import Path

import pandas as pd

XLSX = Path(__file__).resolve().parents[1] / "Data" / "exogenous_data" / "S2biom" / "data_FI.xlsx"

# MWh per tonne dry matter (1 GJ = 0.27778 MWh). ASSUMPTIONS to be sourced before any paper use.
LHV_GJ_PER_T = {"wood": 18.5, "bark": 19.0, "black_liquor": 13.0, "pcw": 16.0}

GROUPS = {
    "stemwood FF+thin (1111-1114)": ([1111, 1112, 1113, 1114], "wood"),
    "logging residues (1211-1214)": ([1211, 1212, 1213, 1214], "wood"),
    "stumps (1221-1222)": ([1221, 1222], "wood"),
    "sawmill residues (4111-4114)": ([4111, 4112, 4113, 4114], "wood"),
    "panel/further processing (4121-4122)": ([4121, 4122], "wood"),
    "bark (4131)": ([4131], "bark"),
    "black liquor (4132)": ([4132], "black_liquor"),
    "post-consumer wood (5211-5212)": ([5211, 5212], "pcw"),
}
COST_TYPES = [1111, 1112, 1113, 1114, 1211, 1212, 1213, 1214, 1221, 1222]
POTENTIALS = ["TECH", "BASE", "HIGH", "UD01", "UD02", "UD03", "UD04", "UD05", "UD06", "UD07", "UD08"]
YEARS = [2012, 2020, 2030]


def mwh_per_t(kind):
    return LHV_GJ_PER_T[kind] / 3.6


def load(xl, name):
    d = xl.parse(name, index_col=0)
    if d.shape[0] == 0:
        return None
    d.columns = [int(c) for c in d.columns]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None, help="folder for CSV outputs")
    args = ap.parse_args()
    pd.set_option("display.width", 250, "display.max_columns", 40, "display.float_format", "{:,.1f}".format)
    xl = pd.ExcelFile(XLSX)

    kt, twh = {}, {}
    for pot in POTENTIALS:
        for yr in YEARS:
            d = load(xl, f"dm_{pot}_{yr}_kton")
            if d is None:
                continue
            for g, (types, kind) in GROUPS.items():
                cols = [t for t in types if t in d.columns]
                if not cols:
                    continue
                s = d[cols].sum().sum()
                kt[(g, pot, yr)] = s
                twh[(g, pot, yr)] = s * mwh_per_t(kind) / 1000.0  # kt dm * MWh/t = GWh -> /1000 = TWh

    def table(src, yr):
        t = pd.Series(src).unstack(level=[1, 2])
        return t.xs(yr, axis=1, level=1)

    kt_t, twh_t = pd.Series(kt).unstack([1, 2]), pd.Series(twh).unstack([1, 2])
    print(f"LHV assumptions (GJ/t dm): {LHV_GJ_PER_T}\n")
    print("== National supply, kton dry matter / yr, 2020 ==")
    print(table(kt, 2020)[[p for p in POTENTIALS if p in table(kt, 2020).columns]])
    print("\n== National supply, TWh / yr, 2020 (LHV assumption above) ==")
    print(table(twh, 2020)[[p for p in POTENTIALS if p in table(twh, 2020).columns]])
    print("\n== TECH and BASE by year, TWh / yr ==")
    print(twh_t[[(p, y) for p in ("TECH", "BASE") for y in YEARS if (p, y) in twh_t.columns]])

    # Road-side cost (identical 2012/2020/2030 for forest types; defined for base potential only)
    cost = load(xl, "rs_cost_2020_euro")
    base = load(xl, "dm_BASE_2020_kton")
    rows = []
    for t in COST_TYPES:
        w = base[t]
        c = cost[t]
        e = mwh_per_t("wood")
        rows.append({
            "type": t, "BASE kt dm": w.sum(), "BASE TWh": w.sum() * e / 1000,
            "cost EUR/t dm (wavg)": (w * c).sum() / w.sum(), "min": c.min(), "max": c.max(),
            "cost EUR/MWh (wavg)": (w * c).sum() / w.sum() / e,
        })
    ct = pd.DataFrame(rows)
    print("\n== Road-side cost (EUR2012, harvest+chipping, no stumpage), BASE 2020 weights ==")
    print(ct)

    # Cost-supply curve: NUTS3 x type blocks, BASE potential, sorted by cost
    blocks = []
    for t in COST_TYPES:
        for r in base.index:
            q = base.at[r, t]
            if q > 0:
                blocks.append((r, t, q * mwh_per_t("wood") / 1000, cost.at[r, t] / mwh_per_t("wood")))
    cs = pd.DataFrame(blocks, columns=["nuts3", "type", "TWh", "EUR_per_MWh"]).sort_values("EUR_per_MWh")
    cs["cum_TWh"] = cs["TWh"].cumsum()
    print("\n== BASE cost-supply (all primary forest types incl. stemwood), cumulative TWh by cost threshold ==")
    for thr in (8, 10, 12, 15, 20, 30):
        print(f"  <= {thr:>2} EUR/MWh : {cs.loc[cs.EUR_per_MWh <= thr, 'TWh'].sum():6.1f} TWh")
    nonstem = cs[~cs["type"].isin([1111, 1112, 1113, 1114])]
    print(f"  residues+stumps only, total {nonstem['TWh'].sum():.1f} TWh")

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        table(kt, 2020).to_csv(args.out / "s2biom_FI_kt_dm_2020.csv")
        table(twh, 2020).to_csv(args.out / "s2biom_FI_TWh_2020.csv")
        ct.to_csv(args.out / "s2biom_FI_cost_by_type_base2020.csv", index=False)
        cs.to_csv(args.out / "s2biom_FI_cost_supply_base2020.csv", index=False)


if __name__ == "__main__":
    main()
