"""Build an evidence-based Finnish biomass import-tier benchmark.

The calculation combines:
- Luke imported chips actually consumed by heating and power plants;
- Luke net pellet imports (imports less exports);
- Luke's official energy factors for chips and pellets;
- UN Comtrade 2024 CIF values;
- the ECB 2024 USD/EUR annual exchange rate;
- Luke's official Finnish long-distance wood-transport cost;
- HaminaKotka's published port dues; and
- Eurostat Finnish HICP harmonisation to the model's inherited EUR2015 basis.

It reports a proposal for review. It does not modify model inputs.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
from statistics import mean
from typing import Any

import requests


LUKE_CHIPS_URL = (
    "https://statdb.luke.fi/PxWeb/api/v1/en/LUKE/met/puukay/pe/"
    "0800_puukay.px"
)
LUKE_PELLETS_URL = (
    "https://statdb.luke.fi/PxWeb/api/v1/en/LUKE/met/puukay/pp/"
    "1900_puukay.px"
)
LUKE_TRANSPORT_URL = (
    "https://statdb.luke.fi/PxWeb/api/v1/en/LUKE/met/zzz_lak/"
    "Teollisuuspuun%20korjuu%20ja%20kaukokuljetus/"
    "05.15_Teollisuuspuun_kaukokuljetuksen_yksikkoku.px"
)
COMTRADE_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
ECB_URL = "https://data-api.ecb.europa.eu/service/data/EXR/A.USD.EUR.SP00.A"
EUROSTAT_HICP_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "prc_hicp_aind"
)
HAMINAKOTKA_TARIFF_URL = (
    "https://www.haminakotka.com/sites/default/files/attachment/"
    "HKS_Pricelist_2025.pdf"
)

CENTRAL_YEARS = ("2022", "2023", "2024")
CHIP_MWH_PER_SOLID_M3 = 2.0
PELLET_MWH_PER_TONNE = 4.7
MODEL_PRICE_YEAR = "2015"
TRANSPORT_PRICE_YEAR = "2021"
PORT_DUE_PRICE_YEAR = "2025"
CHIP_PORT_DUE_EUR_PER_SOLID_M3 = 0.64
PELLET_PORT_DUE_EUR_PER_TONNE = 1.40


def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def _get_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def _luke_query(
    url: str, selections: list[tuple[str, list[str]]]
) -> dict[str, Any]:
    payload = {
        "query": [
            {
                "code": code,
                "selection": {"filter": "item", "values": values},
            }
            for code, values in selections
        ],
        "response": {"format": "json-stat2"},
    }
    return _post_json(url, payload)


def _fetch_luke_transport_cost() -> float:
    metadata = _get_json(LUKE_TRANSPORT_URL, {})
    year_var, method_var, cost_var = metadata["variables"]
    method_index = method_var["valueTexts"].index(
        "Total long-distance transportation"
    )
    cost_index = cost_var["valueTexts"].index("Unit cost - e/m³")
    response = _luke_query(
        LUKE_TRANSPORT_URL,
        [
            (year_var["code"], [TRANSPORT_PRICE_YEAR]),
            (method_var["code"], [method_var["values"][method_index]]),
            (cost_var["code"], [cost_var["values"][cost_index]]),
        ],
    )
    if len(response["value"]) != 1:
        raise ValueError("Expected one Luke transport-cost observation")
    return float(response["value"][0])


def _fetch_luke_flows() -> tuple[
    dict[str, float], dict[str, float], dict[str, float]
]:
    years = [*CENTRAL_YEARS, "2025"]
    energy_chips = _luke_query(
        LUKE_CHIPS_URL,
        [
            ("INFO", ["THAK_LAMVOI_M3T"]),
            ("A", years),
        ],
    )
    energy_chip_values = {
        year: float(value)
        for year, value in zip(years, energy_chips["value"], strict=True)
    }
    total_chips = _luke_query(
        LUKE_CHIPS_URL,
        [
            ("INFO", ["THAK_M3T"]),
            ("A", years),
        ],
    )
    total_chip_values = {
        year: float(value)
        for year, value in zip(years, total_chips["value"], strict=True)
    }

    pellets = _luke_query(
        LUKE_PELLETS_URL,
        [
            ("INFO", ["TT"]),
            ("A", years),
            ("TOI", ["VIE", "TUO"]),
        ],
    )
    values = pellets["value"]
    net_pellet_values = {
        year: float(values[index * 2 + 1] - values[index * 2])
        for index, year in enumerate(years)
    }
    return energy_chip_values, total_chip_values, net_pellet_values


def _fetch_comtrade_world(
    hs_codes: tuple[str, ...],
) -> dict[str, dict[str, float | bool]]:
    response = _get_json(
        COMTRADE_URL,
        {
            "period": "2024",
            "reporterCode": "246",
            "flowCode": "M",
            "partnerCode": "0",
            "cmdCode": ",".join(hs_codes),
            "partner2Code": "0",
            "customsCode": "C00",
            "motCode": "0",
            "maxRecords": "500",
        },
    )
    records = response.get("data", [])
    records_by_code = {str(record["cmdCode"]): record for record in records}
    missing_codes = set(hs_codes) - records_by_code.keys()
    if missing_codes:
        raise ValueError(
            f"Comtrade response is missing HS codes: {sorted(missing_codes)}"
        )
    return {
        code: {
            "net_weight_kg": float(records_by_code[code]["netWgt"]),
            "cif_usd": float(records_by_code[code]["primaryValue"]),
            "net_weight_estimated": bool(
                records_by_code[code].get("isNetWgtEstimated", False)
            ),
            "primary_value_estimated": bool(
                records_by_code[code].get(
                    "isPrimaryValueEstimated", False
                )
            ),
        }
        for code in hs_codes
    }


def _fetch_ecb_usd_per_eur() -> float:
    response = requests.get(
        ECB_URL,
        params={
            "startPeriod": "2024",
            "endPeriod": "2024",
            "format": "csvdata",
        },
        timeout=60,
    )
    response.raise_for_status()
    records = list(csv.DictReader(io.StringIO(response.text)))
    if len(records) != 1:
        raise ValueError(f"Expected one ECB observation, got {len(records)}")
    return float(records[0]["OBS_VALUE"])


def _fetch_hicp() -> dict[str, float]:
    response = _get_json(
        EUROSTAT_HICP_URL,
        {
            "lang": "en",
            "freq": "A",
            "unit": "INX_A_AVG",
            "coicop": "CP00",
            "geo": "FI",
            "sinceTimePeriod": "2010",
            "untilTimePeriod": PORT_DUE_PRICE_YEAR,
        },
    )
    year_positions = response["dimension"]["time"]["category"]["index"]
    values = response["value"]
    return {
        year: float(values[str(position)])
        for year, position in year_positions.items()
    }


def _scenario_energy(
    chip_thousand_solid_m3: float, net_pellet_thousand_tonnes: float
) -> dict[str, float]:
    chip_twh = (
        chip_thousand_solid_m3
        * 1_000
        * CHIP_MWH_PER_SOLID_M3
        / 1_000_000
    )
    pellet_twh = (
        net_pellet_thousand_tonnes
        * 1_000
        * PELLET_MWH_PER_TONNE
        / 1_000_000
    )
    return {
        "chips_twh": chip_twh,
        "net_pellets_twh": pellet_twh,
        "total_twh": chip_twh + pellet_twh,
    }


def build_benchmark() -> dict[str, Any]:
    chips, total_chip_imports, net_pellets = _fetch_luke_flows()
    transport_eur2021_per_solid_m3 = _fetch_luke_transport_cost()
    trade = _fetch_comtrade_world(("440121", "440122", "440131"))
    chip_trade = {code: trade[code] for code in ("440121", "440122")}
    pellet_trade = trade["440131"]
    usd_per_eur = _fetch_ecb_usd_per_eur()
    hicp = _fetch_hicp()

    central_chip = mean(chips[year] for year in CENTRAL_YEARS)
    central_pellet = mean(net_pellets[year] for year in CENTRAL_YEARS)
    annual_scenarios = {
        year: _scenario_energy(chips[year], net_pellets[year])
        for year in CENTRAL_YEARS
    }
    high_year = max(
        CENTRAL_YEARS,
        key=lambda year: annual_scenarios[year]["total_twh"],
    )

    scenarios = {
        "central_2022_2024_mean": _scenario_energy(
            central_chip, central_pellet
        ),
        "finite_high_2022_2024_max": _scenario_energy(
            chips[high_year], net_pellets[high_year]
        ),
        "downside_2025": _scenario_energy(
            chips["2025"], net_pellets["2025"]
        ),
    }
    scenarios["central_2022_2024_mean"].update(
        {
            "chips_thousand_solid_m3": central_chip,
            "net_pellets_thousand_tonnes": central_pellet,
        }
    )
    scenarios["finite_high_2022_2024_max"].update(
        {
            "reference_year": int(high_year),
            "chips_thousand_solid_m3": chips[high_year],
            "net_pellets_thousand_tonnes": net_pellets[high_year],
        }
    )
    scenarios["downside_2025"].update(
        {
            "chips_thousand_solid_m3": chips["2025"],
            "net_pellets_thousand_tonnes": net_pellets["2025"],
        }
    )

    chip_cif_eur = sum(
        float(record["cif_usd"]) for record in chip_trade.values()
    ) / usd_per_eur
    chip_2024_energy_mwh = (
        total_chip_imports["2024"] * 1_000 * CHIP_MWH_PER_SOLID_M3
    )
    chip_cif_eur_per_mwh = chip_cif_eur / chip_2024_energy_mwh

    pellet_cif_eur = float(pellet_trade["cif_usd"]) / usd_per_eur
    pellet_2024_energy_mwh = (
        float(pellet_trade["net_weight_kg"])
        / 1_000
        * PELLET_MWH_PER_TONNE
    )
    pellet_cif_eur_per_mwh = pellet_cif_eur / pellet_2024_energy_mwh

    central = scenarios["central_2022_2024_mean"]
    weighted_cif = (
        chip_cif_eur_per_mwh * central["chips_twh"]
        + pellet_cif_eur_per_mwh * central["net_pellets_twh"]
    ) / central["total_twh"]

    cif_eur2015_per_mwh = (
        weighted_cif * hicp[MODEL_PRICE_YEAR] / hicp["2024"]
    )
    inland_transport_eur2021_per_mwh = (
        transport_eur2021_per_solid_m3 / CHIP_MWH_PER_SOLID_M3
    )
    inland_transport_eur2015_per_mwh = (
        inland_transport_eur2021_per_mwh
        * hicp[MODEL_PRICE_YEAR]
        / hicp[TRANSPORT_PRICE_YEAR]
    )
    chip_port_due_eur2025_per_mwh = (
        CHIP_PORT_DUE_EUR_PER_SOLID_M3 / CHIP_MWH_PER_SOLID_M3
    )
    pellet_port_due_eur2025_per_mwh = (
        PELLET_PORT_DUE_EUR_PER_TONNE / PELLET_MWH_PER_TONNE
    )
    weighted_port_due_eur2025_per_mwh = (
        chip_port_due_eur2025_per_mwh * central["chips_twh"]
        + pellet_port_due_eur2025_per_mwh
        * central["net_pellets_twh"]
    ) / central["total_twh"]
    port_due_eur2015_per_mwh = (
        weighted_port_due_eur2025_per_mwh
        * hicp[MODEL_PRICE_YEAR]
        / hicp[PORT_DUE_PRICE_YEAR]
    )
    delivered_eur2015_per_mwh = (
        cif_eur2015_per_mwh
        + inland_transport_eur2015_per_mwh
        + port_due_eur2015_per_mwh
    )

    return {
        "model_price_year": int(MODEL_PRICE_YEAR),
        "implemented_finite_tier": {
            "availability_gwh_per_year": round(
                central["total_twh"] * 1_000
            ),
            "cost_eur2015_per_mwh": round(delivered_eur2015_per_mwh, 1),
            "model_c_op_meur_per_gwh": round(
                delivered_eur2015_per_mwh / 1_000, 5
            ),
        },
        "implemented_unlimited_stress_tier": {
            "availability_gwh_per_year": 1_000_000,
            "cost_eur2015_per_mwh": 81.5,
            "model_c_op_meur_per_gwh": 0.0815,
            "basis": (
                "author-defined EUR2015 stress assumption inspired by "
                "Colla et al. artificial RoW-II backstop"
            ),
            "qualification": (
                "not a Finnish observation or a price-year conversion "
                "of Colla's value"
            ),
        },
        "official_energy_factors": {
            "chips_mwh_per_solid_m3": CHIP_MWH_PER_SOLID_M3,
            "pellets_mwh_per_tonne": PELLET_MWH_PER_TONNE,
        },
        "observed_flows": {
            "energy_chips_thousand_solid_m3": chips,
            "total_chip_imports_thousand_solid_m3": total_chip_imports,
            "net_pellets_thousand_tonnes": net_pellets,
        },
        "scenarios": scenarios,
        "cost_components": {
            "chips_cif_eur2024_per_mwh": chip_cif_eur_per_mwh,
            "pellets_cif_eur2024_per_mwh": pellet_cif_eur_per_mwh,
            "central_weighted_cif_eur2024_per_mwh": weighted_cif,
            "central_weighted_cif_eur2015_per_mwh": (
                cif_eur2015_per_mwh
            ),
            "luke_total_long_distance_transport_eur2021_per_solid_m3": (
                transport_eur2021_per_solid_m3
            ),
            "conservative_inland_transport_eur2015_per_mwh": (
                inland_transport_eur2015_per_mwh
            ),
            "haminakotka_weighted_port_due_eur2015_per_mwh": (
                port_due_eur2015_per_mwh
            ),
            "central_delivered_eur2015_per_mwh": (
                delivered_eur2015_per_mwh
            ),
        },
        "inflation_factors": {
            "eur2024_to_eur2015": (
                hicp[MODEL_PRICE_YEAR] / hicp["2024"]
            ),
            "eur2021_to_eur2015": (
                hicp[MODEL_PRICE_YEAR] / hicp[TRANSPORT_PRICE_YEAR]
            ),
            "eur2025_to_eur2015": (
                hicp[MODEL_PRICE_YEAR] / hicp[PORT_DUE_PRICE_YEAR]
            ),
            "hicp": {
                MODEL_PRICE_YEAR: hicp[MODEL_PRICE_YEAR],
                TRANSPORT_PRICE_YEAR: hicp[TRANSPORT_PRICE_YEAR],
                "2024": hicp["2024"],
                PORT_DUE_PRICE_YEAR: hicp[PORT_DUE_PRICE_YEAR],
            },
        },
        "exchange_rate": {
            "year": 2024,
            "usd_per_eur": usd_per_eur,
        },
        "qualifications": [
            "The 2025 imported-chip observation is provisional.",
            "Net pellet imports avoid counting re-exports as Finnish supply.",
            "The CIF benchmark uses all Finnish 2024 chip and pellet imports; "
            "the chip price combines Luke solid-volume energy with Comtrade value.",
            "Luke's all-mode 2021 long-distance transport average is applied per "
            "MWh to both products as a conservative national-node proxy; it is "
            "not an observed port-to-plant contract.",
            "The HaminaKotka port due is public, but commercial stevedoring is "
            "not separately observable; loading and unloading are represented "
            "by the conservative Luke transport proxy.",
            "The pellet port due uses the higher dry-bulk EUR/t tariff rather "
            "than converting the lower CN 44.01 wood EUR/m3 tariff.",
            "Finland's all-items HICP is a transparent general deflator, not a "
            "freight-specific index.",
            "No growth beyond observed 2022-2024 flows is assumed for 2035.",
            "The EUR2015 delivered cost is held constant in real terms to 2035.",
        ],
        "sources": {
            "luke_methodology": (
                "https://www.luke.fi/en/statistics/wood-consumption/"
                "documentation-of-statistics-wood-consumption-0"
            ),
            "luke_chips_api": LUKE_CHIPS_URL,
            "luke_pellets_api": LUKE_PELLETS_URL,
            "luke_transport_api": LUKE_TRANSPORT_URL,
            "comtrade_api": COMTRADE_URL,
            "ecb_api": ECB_URL,
            "eurostat_hicp_api": EUROSTAT_HICP_URL,
            "haminakotka_2025_tariff": HAMINAKOTKA_TARIFF_URL,
            "model_price_year": (
                "Thiran thesis, parameter table: c_op in M EUR2015/GWh"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the proposed Finnish biomass import-tier benchmark."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for the JSON result. The model is never modified.",
    )
    args = parser.parse_args()

    result = build_benchmark()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
