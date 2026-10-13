"""Verify the retained Finland biomass pools against ENSPRESO 2035 interpolation."""

from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
WORKBOOK = REPO / "Data" / "exogenous_data" / "ENSPRESO" / "ENSPRESO_BIOMASS.xlsx"
RESOURCE_FILES = (
    "Resources.csv",
    "Resources_S1_BES.csv",
    "Resources_S2_NFS.csv",
    "Resources_S3_BDS.csv",
)
GROUPS = {
    "WET_BIOMASS": ("MINBIOSLU1", "MINBIOGAS1"),
    "ENERGY_CROPS_2": ("MINBIOCRP31", "MINBIOCRP41", "MINBIOCRP41a"),
    "BIOWASTE": ("MINBIOMUN1",),
    "BIOMASS_RESIDUES": ("MINBIOAGRW1",),
}
SLUDGE_TO_BIOGAS = 1 / 3.3462
PJ_TO_GWH = 1000 / 3.6


def expected_values() -> pd.DataFrame:
    energy = pd.read_excel(WORKBOOK, sheet_name="ENER - NUTS0 EnergyCom")
    costs = pd.read_excel(WORKBOOK, sheet_name="COST - NUTS0 EnergyCom")
    data = energy.merge(
        costs,
        on=["Year", "Scenario", "NUTS0", "Energy Commodity"],
        how="inner",
    )
    data = data[
        (data["NUTS0"] == "FI")
        & (data["Scenario"] == "ENS_Med")
        & data["Year"].isin((2030, 2040))
    ].copy()

    by_year = {
        year: frame.set_index("Energy Commodity")
        for year, frame in data.groupby("Year")
    }
    interpolated = by_year[2030].copy()
    interpolated["Value"] = (by_year[2030]["Value"] + by_year[2040]["Value"]) / 2
    cost_column = "NUTS0 Energy Commodity Cost "
    interpolated[cost_column] = (
        by_year[2030][cost_column] + by_year[2040][cost_column]
    ) / 2

    interpolated.loc["MINBIOSLU1", "Value"] *= SLUDGE_TO_BIOGAS
    interpolated.loc["MINBIOSLU1", cost_column] /= SLUDGE_TO_BIOGAS

    rows = []
    for resource, commodities in GROUPS.items():
        selected = interpolated.loc[list(commodities)]
        potential = selected["Value"].sum()
        weighted_cost = (
            selected["Value"] * selected[cost_column]
        ).sum() / potential
        rows.append(
            {
                "resource": resource,
                "avail_local": potential * PJ_TO_GWH,
                "c_op_local": weighted_cost * 3.6 / 1000,
            }
        )
    return pd.DataFrame(rows).set_index("resource")


def main() -> None:
    expected = expected_values()
    failed = False
    for filename in RESOURCE_FILES:
        path = REPO / "Data" / "2035" / "FI" / filename
        actual = pd.read_csv(path, index_col=0).loc[expected.index, expected.columns]
        differences = (actual - expected).abs()
        matches = pd.DataFrame(
            {
                "avail_local": differences["avail_local"] <= 1e-9,
                "c_op_local": differences["c_op_local"] <= 1e-12,
            }
        )
        if not matches.all().all():
            failed = True
            print(f"FAIL {filename}")
            print(actual.compare(expected))
        else:
            print(f"PASS {filename}")

    print("\nExpected 2035 values:")
    print(expected.to_string())
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
