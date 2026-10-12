"""Read-only: where does the WOOD layer go in the 9 canonical Paper-1 runs?

Reads paper1/results/<run>/Year_balance.csv (layer balance by technology, GWh/y) and
paper1/results/<run>/Resources.csv. Prints, per run, the supply of the WOOD layer by
resource and its consumption by end-use group (TWh/y). Changes nothing.
"""
import glob
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper1", "results")

GROUPS = {
    "NED chemical feedstock (HVC + methanol)": ["BIOMASS_TO_HVC", "BIOMASS_TO_METHANOL"],
    "Industrial heat (IND_BOILER_WOOD, IND_COGEN_WOOD)": ["IND_BOILER_WOOD", "IND_COGEN_WOOD"],
    "District heat (DHN_BOILER_WOOD, DHN_COGEN_WOOD)": ["DHN_BOILER_WOOD", "DHN_COGEN_WOOD"],
    "Decentralised heat (DEC_BOILER_WOOD)": ["DEC_BOILER_WOOD"],
    "Biofuels/biomethane (diesel, jet, methane)": ["BIOMASS_TO_DIESEL", "BIOMASS_TO_JET_FUEL", "BIOMASS_TO_METHANE"],
    "Power only (BIOMASS_TO_POWER)": ["BIOMASS_TO_POWER"],
}
RES = ["WOOD_FI1", "WOOD_FI2", "WOOD_FI3", "WOOD_FI4", "WOOD_FI5", "ENERGY_CROPS_2"]


def main():
    pd.set_option("display.width", 250, "display.max_columns", 30, "display.float_format", "{:,.1f}".format)
    supply, use = {}, {}
    for d in sorted(glob.glob(os.path.join(ROOT, "*", ""))):
        name = os.path.basename(os.path.dirname(d))
        yb = pd.read_csv(os.path.join(d, "Year_balance.csv"), index_col=0)["WOOD"]
        rs = pd.read_csv(os.path.join(d, "Resources.csv"), index_col=0)["R_year_local"]
        supply[name] = pd.Series({r: rs.get(r, 0.0) / 1000 for r in RES})
        use[name] = pd.Series({g: -yb.reindex(t).fillna(0).sum() / 1000 for g, t in GROUPS.items()})
        resid = -yb[yb < 0].sum() / 1000 - use[name].sum()
        assert abs(resid) < 0.05, (name, resid)
    S, U = pd.DataFrame(supply), pd.DataFrame(use)
    print("== WOOD-layer supply by resource, TWh/y (energy crops also feed the WOOD layer) ==")
    print(S.loc[(S.abs() > 0.05).any(axis=1)].T.assign(TOTAL=S.sum()))
    print("\n== WOOD-layer use by end-use group, TWh/y ==")
    print(U.T.assign(TOTAL=U.sum()))
    print("\n== Share of NED chemical feedstock in total wood use, % ==")
    print((U.iloc[0] / U.sum() * 100).round(0).to_string())


if __name__ == "__main__":
    main()
