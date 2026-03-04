# Finland 2017 Calibration Dossier

> **Scope**: Complete audit of every data source, hypothesis, and override used in the
> EnergyScope Multi-Cells Finland 2017 calibration.
>
> **Generated**: 2026-02-18 | **Model year**: 2017 | **Region**: FI

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technologies](#2-technologies)
3. [Resources & Trade](#3-resources--trade)
4. [Demands](#4-demands)
5. [Misc / Policy Parameters](#5-misc--policy-parameters)
6. [Layers & Efficiencies](#6-layers--efficiencies)
7. [Time Series & Temporal Aggregation](#7-time-series--temporal-aggregation)
8. [Storage](#8-storage)
9. [Network Losses & Infrastructure](#9-network-losses--infrastructure)
10. [Consistency Check Results](#10-consistency-check-results)
11. [Known Issues & Open Questions](#11-known-issues--open-questions)
12. [Source Registry](#12-source-registry)

---

## 1. Architecture Overview

The ESMC model uses a **three-tier data hierarchy**:

| Tier | Path | Role | Scope |
|------|------|------|-------|
| **00_INDEP** | `Data/2017/00_INDEP/` | Year-independent, country-independent constants | Universal |
| **02_REF_REGION** | `Data/2017/02_REF_REGION/` | Reference defaults for all countries (170 technologies, 35 resources) | Pan-European |
| **FI/** | `Data/2017/FI/` | Finland-specific **overrides only** | Finland |

**Pipeline**: `REF_REGION.deepcopy()` → `FI.update()` (cell-by-cell) → `concat_reg_data()` → `mask(>1e14, 'Infinity')` → `print_df()` → `.dat` → AMPL/CPLEX

Anything **not** in `FI/` inherits the REF_REGION default unchanged.

### Files in each tier

| File | 00_INDEP | 02_REF_REGION | FI/ |
|------|----------|---------------|-----|
| Technologies.csv | — | 170 rows, 14 cols (c_inv, c_maint, gwp_constr, lifetime, c_p, fmin_perc, fmax_perc, f_min, f_max) | Override: ~55 rows, 5 cols (f_min, f_max, fmin_perc, fmax_perc) |
| Resources.csv | — | 35 rows (avail_local, avail_exterior, gwp_op_local, c_op_local) | Override: 14–25 rows (avail_local, c_op_local, avail_exterior) |
| Resources_indep.csv | 35 rows (c_op_exterior, gwp_op_exterior, co2_net) | — | — |
| Demands.csv | — | 11 end-uses × 4 sectors | Override: 11 end-uses × 4 sectors |
| Misc.json | — | ~15 params (shares, areas) | Override: 21 params changed |
| Misc_indep.json | loss_network, i_rate, EV params | — | — |
| Layers_in_out.csv | 170 techs × 38 layers (efficiency matrix) | — | — |
| Time_series.csv | — | 8760 h × 13 profiles | Override: 8760 h × 13 profiles |
| Weights.csv | — | 10 demand weights | Override: 10 demand weights |
| Storage_*.csv | characteristics, eff_in, eff_out (31 storage techs) | — | — |
| Storage_power_to_energy.csv | — | — | Override: PHS only |

---

## 2. Technologies

### 2.1 What FI overrides vs what it inherits

**FI overrides** (current state — 55 non-empty rows):

| Category | Technologies overridden | What is set |
|----------|----------------------|-------------|
| **Power generation** | NUCLEAR, PV_ROOFTOP, PV_UTILITY, WIND_ONSHORE, WIND_OFFSHORE, HYDRO_DAM, HYDRO_RIVER, COAL_US, CCGT, GEOTHERMAL | f_min, f_max |
| **Banned** | PT_POWER_BLOCK, ST_POWER_BLOCK, PT_COLLECTOR, ST_COLLECTOR, TIDAL_STREAM, TIDAL_RANGE, WAVE, DHN_DEEP_GEO, CCGT_AMMONIA, COAL_IGCC | f_min=0, f_max=0 |
| **CHP / boilers** | DHN_COGEN_GAS, DHN_BOILER_OIL, IND_BOILER_OIL, IND_BOILER_WOOD, DHN_COGEN_WOOD, DHN_COGEN_COAL, DHN_BOILER_COAL, IND_BOILER_COAL, IND_BOILER_GAS | f_min, f_max, fmin_perc, fmax_perc |
| **Transport** | CAR_GASOLINE, CAR_DIESEL, CAR_BEV, CAR_PHEV, CAR_HEV, TRUCK_DIESEL, TRUCK_NG, BUS_COACH_DIESEL, CARGO_LFO, CARGO_LNG, BOAT_FREIGHT_DIESEL, BOAT_FREIGHT_NG, etc. | fmin_perc, fmax_perc |
| **Solar thermal** | DHN_SOLAR, DEC_SOLAR | f_max (area-limited) |
| **Storage** | DAM_STORAGE, PHS, BATT_LI, TS_DEC_TH, TS_DHN_TH | f_min/f_max bounds |
| **Resources** | ELECTRICITY, COAL, GAS | f_min, f_max (import-related bounds) |

**FI inherits unchanged** (from REF_REGION):
- All technology **costs** (c_inv, c_maint) — the REF values are 2035 DEA-based costs
- All technology **lifetimes**
- All **capacity factors** (c_p)
- All **GWP construction** values
- All **synthetic fuel** technologies (BIOMASS_TO_POWER, H2_ELECTROLYSIS, SYN_METHANATION, HABER_BOSCH, POWER_TO_*, etc.)
- All CCS technologies
- DEC_HP_ELEC, DEC_BOILER_*, DEC_COGEN_* (except where explicitly overridden)

### 2.2 Key technology assumptions

| Technology | f_min (GW) | f_max (GW) | fmin_perc | fmax_perc | Source / Rationale |
|------------|-----------|-----------|-----------|-----------|-------------------|
| NUCLEAR | 2.5 | 2.8 | 0.0 | 1.0 | Loviisa 1&2 (1.012 GW) + Olkiluoto 1&2 (1.76 GW). No OL3 in 2017. Source: Statistics Finland Energy Authority |
| WIND_ONSHORE | 2.0 | 2.1 | 0.0 | 1.0 | ~2 GW installed 2017. Source: Statistics Finland Energy Statistics |
| WIND_OFFSHORE | 0.0 | 0.0 | 0.0 | 1.0 | No significant offshore wind in 2017 |
| HYDRO_DAM | 1.1 | 1.3 | 0.0 | 1.0 | Existing reservoir hydro |
| HYDRO_RIVER | 1.9 | 2.1 | 0.0 | 1.0 | Existing run-of-river |
| PV_ROOFTOP | 0.02 | 2.0 | 0.0 | 1.0 | Very small installed base, up to 2 GW potential |
| COAL_US | 3.5 | 4.5 | 0.0 | 1.0 | Coal condensation plants forced to represent 2017 fleet |
| CCGT | 0.6 | 1.5 | 0.0 | 1.0 | Gas combined cycle |
| DAM_STORAGE | 0.001 | 0.001 | — | — | Fixed (represents existing pumped/dam storage) |
| PHS | 0.001 | 0.001 | — | — | Fixed |

### 2.3 Market share constraints (fmin_perc / fmax_perc)

Activated by `f_perc: True` in run config.

| Technology | fmin_perc | fmax_perc | Rationale |
|------------|-----------|-----------|-----------|
| IND_BOILER_WOOD | 0.4 | 1.0 | Finland biomass mandate/industry |
| DHN_COGEN_WOOD | 0.3 | 1.0 | Biomass CHP forced |
| DHN_COGEN_COAL | 0.3 | 1.0 | Coal CHP sunk costs |
| DHN_BOILER_COAL | 0.1 | 1.0 | Coal boiler minimum |
| IND_BOILER_COAL | 0.1 | 1.0 | Coal boiler minimum |
| DHN_COGEN_GAS | 0.0 | 0.2 | Gas CHP capped |
| DHN_BOILER_OIL | 0.0 | 0.1 | Oil boiler capped |
| IND_BOILER_GAS | 0.0 | 0.2 | Gas boiler capped |
| CAR_GASOLINE | 0.55 | 0.65 | Dominant car fuel 2017 |
| CAR_DIESEL | 0.30 | 0.40 | Second car fuel |
| CAR_BEV | 0.0 | 0.01 | Negligible in 2017 |
| CAR_PHEV | 0.0 | 0.01 | Negligible in 2017 |
| CAR_HEV | 0.0 | 0.05 | Small share |
| TRUCK_DIESEL | 0.9 | 1.0 | Near-total truck dominance |
| TRUCK_NG | 0.0 | 0.05 | Small NG truck share |
| BUS_COACH_DIESEL | 0.9 | 1.0 | Diesel buses dominant |
| CARGO_LFO | 0.95 | 1.0 | LFO dominant in shipping |
| CARGO_LNG | 0.0 | 0.05 | Small LNG share |
| BOAT_FREIGHT_DIESEL | 0.95 | 1.0 | Diesel dominant inland freight |
| BOAT_FREIGHT_NG | 0.0 | 0.05 | Small NG share |

### 2.4 Cost data warning

**CRITICAL**: All technology costs (c_inv, c_maint) in REF_REGION are based on **2035 DEA Technology Catalogue** values. For a 2017 calibration, these costs are anachronistic. The REORG workbook's validation log notes:

> "FAILED: 167/167 techs have identical costs to 2035" (2026-02-10)

Subsequently, 14 key technologies were updated from DEA 2023 catalogue interpolated to 2017 via `scripts/fix_technologies_errors.py`. However, 153 minor technologies retain 2035 default costs. This is acceptable for calibration since the model minimizes **total annual cost** and the relative ranking matters more than absolute values, but it introduces a systematic bias.

### 2.5 Banned technologies (f_max = 0)

| Technology | Reason |
|------------|--------|
| PT_POWER_BLOCK, ST_POWER_BLOCK | No CSP in Finland |
| PT_COLLECTOR, ST_COLLECTOR | No CSP in Finland |
| TIDAL_STREAM, TIDAL_RANGE, WAVE | No tidal/wave in Finland |
| DHN_DEEP_GEO | No deep geothermal in Finland |
| CCGT_AMMONIA | Not applicable for 2017 |
| COAL_IGCC | Not applicable for 2017 |
| CAR_FUEL_CELL | Not applicable for 2017 |
| TRUCK_ELEC, TRUCK_FUEL_CELL | Not applicable for 2017 |
| BUS_COACH_FC_HYBRIDH2 | Not applicable for 2017 |
| CAR_METHANOL, CARGO_METHANOL, CARGO_AMMONIA, BOAT_FREIGHT_METHANOL | Not applicable for 2017 |

---

## 3. Resources & Trade

### 3.1 Local resources (FI override)

| Resource | avail_local (GWh/y) | c_op_local (M€/GWh) | Source |
|----------|--------------------|--------------------|--------|
| WOOD | 110,805.66 | 0.022084 | Local expert estimates / original calibration |
| WET_BIOMASS | 1,450.62 | 0.033104 | Local expert estimates |
| ENERGY_CROPS_2 | 7,754.11 | 0.023524 | Local expert estimates |
| BIOWASTE | 4,720.94 | 0.000112 | Near-free disposal feedstock |
| BIOMASS_RESIDUES | 4,985.24 | 0.013135 | Local expert estimates |
| WASTE | 11,095.02 | 0.006079 | Local expert estimates |

**Total local biomass + waste**: ~140,811 GWh/y

> **Cross-check vs REORG workbook**: All 6 biomass values match REORG MODEL_INPUTS exactly (CHECK 11: PASS).

### 3.2 Exterior (imported) resources

| Resource | avail_exterior (GWh/y) | c_op_local override (M€/GWh) | c_op_exterior (00_INDEP) | Price used | Source |
|----------|----------------------|------------------------------|-------------------------|-----------|--------|
| GASOLINE | 1e15 (unlimited) | 0.0588 | 0.082 | **FI override** | Statistics Finland, tax-inclusive |
| DIESEL | 1e15 | 0.0543 | 0.080 | **FI override** | Statistics Finland, tax-inclusive |
| LFO | 1e15 | 0.0521 | 0.060 | **FI override** | Statistics Finland, heating oil |
| JET_FUEL | 1e15 | 0.0359 | 0.080 | **FI override** | Spot market CIF estimate |
| GAS | 1e15 | 0.0195 | 0.044 | **FI override** | Gas market import price (gasum/stat.fi) |
| COAL | 1e15 | 0.0103 | 0.018 | **FI override** | Coal import price analysis (stat.fi) |
| URANIUM | 1e15 | 0.0093 | 0.004 | **FI override** | |
| ELECTRICITY | 1e15 | 0.0326 | 0.084 | **FI override** | NordPool ~33 €/MWh |

**Important**: The FI override prices (`c_op_local` column) take effect because the model sees these resources as having `avail_exterior = 1e15` (from REF). The `c_op_exterior` from 00_INDEP still applies but is overridden by the regional `c_op_local` when local availability is set via the pipeline.

### 3.3 Disabled resources (avail_exterior = 0 in FI)

All renewable fuels and synthetic carriers are disabled for 2017:

| Disabled | Reason |
|----------|--------|
| GASOLINE_RE, DIESEL_RE, LFO_RE, JET_FUEL_RE, GAS_RE | No renewable fuel imports in 2017 |
| H2, H2_RE | No hydrogen economy in 2017 |
| AMMONIA, AMMONIA_RE | No green ammonia in 2017 |
| METHANOL, METHANOL_RE | No methanol imports in 2017 |

### 3.4 Price pipeline (from REORG workbook)

| Resource | Previous price | Final 2017 price | Change |
|----------|---------------|-------------------|--------|
| GASOLINE | 0.06 | 0.0588 | -2% |
| DIESEL | 0.057 | 0.0543 | -5% |
| LFO | 0.055 | 0.0521 | -5% |
| JET_FUEL | **0.0824** | **0.0359** | **-56%** |
| GAS | 0.02 | 0.0195 | -3% |
| COAL | 0.01 | 0.0103 | +3% |
| URANIUM | — | 0.0093 | New |
| ELECTRICITY | — | 0.0326 | New |

> **JET_FUEL decision**: The high value (0.0824) was identified as likely including taxes or being a pump price. 0.0359 reflects realistic CIF/Spot jet fuel price. (Source: REORG Assumptions sheet)

---

## 4. Demands

### 4.1 End-use demands (FI/Demands.csv)

| End-use | Households | Services | Industry | Transport | Total | Unit |
|---------|-----------|----------|----------|-----------|-------|------|
| ELECTRICITY | 8,760 | 10,822 | 23,425 | 0 | **43,007** | GWh |
| HEAT_HIGH_T | 0 | 0 | 59,821 | 0 | **59,821** | GWh |
| HEAT_LOW_T_SH | 38,557 | 24,967 | 22,112 | 0 | **85,636** | GWh |
| HEAT_LOW_T_HW | 6,009 | 5,240 | 9,130 | 0 | **20,379** | GWh |
| PROCESS_COOLING | 0 | 0 | 3,757 | 0 | **3,757** | GWh |
| SPACE_COOLING | 404 | 1,171 | 520 | 0 | **2,095** | GWh |
| MOBILITY_PASSENGER | 0 | 0 | 0 | 90,844 | **90,844** | Mpkm |
| MOBILITY_FREIGHT | 0 | 0 | 0 | 36,490 | **36,490** | Mtkm |
| AVIATION_LONG_HAUL | 0 | 0 | 0 | 15,363 | **15,363** | Mpkm |
| SHIPPING | 0 | 0 | 0 | 148,985 | **148,985** | Mtkm |
| NON_ENERGY | 0 | 0 | 10,708 | 0 | **10,708** | GWh |

### 4.2 Demand sources

| Source | Data |
|--------|------|
| **Origin** | JRC-IDEES / Eurostat **2015** statistical data |
| **Intermediate file** | `Data/exogenous_data/regions/Demands.csv` |
| **Script** | `scripts/update_demands_from_regions.py` |
| **Proxy year** | **2015 used as proxy for 2017** (REORG: "Used 2015 statistical data as proxy for 2017 due to data quality and availability") |

### 4.3 Demand cross-check (CSV vs REORG workbook)

| End-use | FI/Demands.csv | REORG workbook | Delta |
|---------|---------------|----------------|-------|
| ELECTRICITY | 43,007 | 42,912 | 0.2% |
| HEAT_HIGH_T | 59,821 | 59,965 | 0.2% |
| HEAT_LOW_T_SH | 85,636 | 86,661 | 1.2% |
| HEAT_LOW_T_HW | 20,379 | 18,967 | **7.4%** |
| MOBILITY_PASSENGER | 90,844 | 91,992 | 1.2% |
| MOBILITY_FREIGHT | 36,490 | 34,442 | **5.9%** |

> **Discrepancies**: HEAT_LOW_T_HW (+7.4%) and MOBILITY_FREIGHT (+5.9%) differ between the CSV and the REORG workbook. The REORG workbook likely contains an earlier snapshot. The CSV values are the authoritative ones loaded by the model.

---

## 5. Misc / Policy Parameters

### 5.1 FI/Misc.json (21 overrides vs REF)

| Parameter | REF value | FI value | Source / Rationale |
|-----------|----------|----------|-------------------|
| **share_heat_dhn_min** | 0.02 | **0.449** | Finnish Energy: district heat ≈ 45% of space heating market (2020 proxy) |
| **share_heat_dhn_max** | 0.37 | **0.451** | Tight band: ±0.1% around 45% |
| **share_mobility_public_min** | 0.199 | **0.160** | stat.fi: (bus+rail)/(car+bus+rail) ≈ 16.1% (2019 pre-COVID data) |
| **share_mobility_public_max** | 0.5 | **0.162** | Tight band |
| **share_freight_train_min** | 0.109 | **0.275** | stat.fi: rail/(rail+road) ≈ 27.6% |
| **share_freight_train_max** | 0.25 | **0.277** | Tight band |
| **share_freight_boat_min** | 0.156 | **0.154** | Small inland water freight |
| **share_freight_boat_max** | 0.3 | **0.156** | Tight band |
| **share_freight_road_max** | 3 | **1** | Corrected to plausible range |
| **share_short_haul_flights_min** | 0 | **0.1643** | Eurostat modal split |
| **share_short_haul_flights_max** | 0 | **0.1644** | Tight band |
| **re_share_primary** | 0 | **0.41** | Finland RE share target/actual |
| **elec_import_capacity** | MISSING | **3** GW | Finland interconnection capacity |
| **elec_export_capacity** | MISSING | **3** GW | Finland interconnection capacity |
| **import_capacity** | 0 | **4.5** GW | Total import capacity (gas + elec) |
| **solar_area_ground** | 1e15 | **345.75** km² | Finland ground-mounted solar potential |
| **solar_area_ground_high_irr** | 1e15 | **0.0** | No high-irradiance area in Finland |
| **solar_area_rooftop** | 1e15 | **80.49** km² | Finland rooftop potential |
| **solar_area** | MISSING | **338,000** | Solar area parameter |
| **share_ned** | all zeros | HVC=0.779, METHANOL=0.029, AMMONIA=0.192 | Non-energy demand split |

### 5.2 Misc_indep.json (global, not overrideable per region)

| Parameter | Value | Note |
|-----------|-------|------|
| i_rate | 0.05 | 5% discount rate |
| gwp_limit_overall | 1e15 | No GHG constraint (effectively unconstrained) |
| loss_network ELECTRICITY | 0.0864 | 8.64% grid losses — **NOTE**: FI should be ~3% per Finnish Energy data |
| loss_network HEAT_LOW_T_DHN | 0.05 | 5% DH losses — vs Finnish Energy 8.5% |
| power_density_pv | 0.085 GW/km² | |
| sm_max | 4 | Solar multiple max |
| c_grid_extra | 367.8 M€/GW | Grid reinforcement cost |

> **ISSUE**: Electricity grid losses are 8.64% globally (Misc_indep) but Finnish Energy reports only 3% for Finland. This is a known compromise — the INDEP file cannot be overridden per country. Similarly, DH losses are 5% globally but Finnish Energy reports 8.5%. These mismatches partially offset each other.

---

## 6. Layers & Efficiencies

### 6.1 Layers_in_out.csv (00_INDEP)

This is a 170×38 matrix defining the input/output efficiency of every technology across all energy layers. It is **not overrideable per country** in the current pipeline.

Key efficiencies for Finland-relevant technologies:

| Technology | Fuel input (per GWh_out) | Elec output | Heat output | CO2_INDUSTRY |
|------------|--------------------------|------------|------------|-------------|
| NUCLEAR | -2.7027 URANIUM | 1.0 ELEC | — | — |
| COAL_US | -2.0408 COAL | 1.0 ELEC | — | 0.7347 |
| CCGT | -1.5873 GAS | 1.0 ELEC | — | 0.3175 |
| WIND_ONSHORE | -1.0 RES_WIND | 1.0 ELEC | — | — |
| HYDRO_RIVER | -1.0 RES_HYDRO | 1.0 ELEC | — | — |
| IND_BOILER_WOOD | -1.1568 WOOD | — | 1.0 HHT | 0.4512 |
| DHN_COGEN_WOOD | -1.8868 WOOD | 0.3396 ELEC | 1.0 DHN | 0.7359 |
| DHN_COGEN_COAL | -1.8868 COAL | 0.3396 ELEC | 1.0 DHN | 0.7359 |
| IND_BOILER_COAL | -1.2195 COAL | — | 1.0 HHT | 0.4390 |
| DHN_COGEN_GAS | -2.5000 GAS | 1.25 ELEC | 1.0 DHN | 0.5000 |
| CAR_GASOLINE | -0.4968 GASOLINE | — | — | — → 1.0 MOB_PRIVATE |
| TRUCK_DIESEL | -0.5126 DIESEL | — | — | — → 1.0 MOB_FREIGHT_ROAD |

### 6.2 REORG workbook notes on efficiency degradation

The VALIDATION_2017 sheet notes:

> "Wood Boilers & CHP: Degraded 15-20% — 2017 fleet is older/less efficient than 2035 BAT"
> "Coal Boilers: Degraded 15-20%"
> "Layers_in_out: IND_BOILER/COGEN_WOOD degraded 15-20%"

**Status**: These degraded efficiencies are documented as hypotheses but it is unclear if they were applied to the current 00_INDEP Layers_in_out.csv (since it cannot be region-specific). The current values appear to be the standard ESMC values, not degraded.

---

## 7. Time Series & Temporal Aggregation

### 7.1 Time_series.csv (FI/)

- **Shape**: 8,760 hours × 13 profiles
- **Profiles**: ELECTRICITY, HEAT_LOW_T_SH, SPACE_COOLING, MOBILITY_PASSENGER, MOBILITY_FREIGHT, PV, WIND_ONSHORE, WIND_OFFSHORE, HYDRO_DAM, HYDRO_RIVER, TIDAL, SOLAR, CSP
- **Source year**: **2015** time profiles (ENTSOE, Renewables.ninja, JRC-IDEES) used as proxy for 2017
- **TIDAL**: All values = 0.0001 (effectively zero — no tidal in Finland)
- **CSP**: All values = 0.0001 (no CSP)

### 7.2 Weights.csv (FI/)

Controls relative weighting of demand profiles in temporal aggregation:

| Profile | Weight |
|---------|--------|
| ELECTRICITY | 1.0 |
| HEAT_LOW_T_SH | 0.204 |
| SPACE_COOLING | 0.087 |
| WIND_OFFSHORE | 1.0 |
| WIND_ONSHORE | 1.0 |
| HYDRO_DAM | 1.0 |
| HYDRO_RIVER | 1.0 |
| PV | 1.0 |
| TIDAL | 0.0 |

### 7.3 Temporal aggregation

Config: `nbr_td: 12` (12 typical days). Method: k-medoids clustering on weighted time series.

> **Non-determinism warning**: k-medoids uses random initialization → different runs can produce different typical day selections → different results. This is a known reproducibility issue.

---

## 8. Storage

### 8.1 Storage_power_to_energy.csv (FI/)

Only PHS overridden:

| Storage | charge_time (h) | discharge_time (h) |
|---------|----------------|-------------------|
| PHS | 7.353 | 7.353 |

### 8.2 Storage parameters (00_INDEP)

31 storage technologies defined globally:

| Key storages | availability | losses | eff_in | eff_out |
|-------------|-------------|--------|--------|---------|
| DAM_STORAGE | 1.0 | 0 | 0.99 (ELEC) | 0.99 (ELEC) |
| PHS | 1.0 | 0 | 0.866 (ELEC) | 0.866 (ELEC) |
| BATT_LI | 1.0 | 0.0002 | 0.95 (ELEC) | 0.95 (ELEC) |
| TS_DHN_DAILY | 1.0 | 0.00833 | 1.0 (DHN) | 1.0 (DHN) |
| TS_DHN_SEASONAL | 1.0 | 0.000061 | 1.0 (DHN) | 1.0 (DHN) |
| GAS_STORAGE | 1.0 | 0 | 0.99 (GAS) | 0.995 (GAS) |
| H2_STORAGE | 1.0 | 0 | 0.9 (H2) | 0.98 (H2) |

---

## 9. Network Losses & Infrastructure

### 9.1 Grid losses

| Network | Global (Misc_indep) | Finnish reality | Discrepancy |
|---------|-------|--------|------------|
| ELECTRICITY | 8.64% | ~3% (Finnish Energy 2022) | **Over-estimated by ~5.6pp** |
| HEAT_LOW_T_DHN | 5.0% | ~8.5% (Finnish Energy 2024) | **Under-estimated by ~3.5pp** |

These are global parameters in 00_INDEP and cannot be overridden by FI/. This is a structural limitation of the model for single-country calibration.

### 9.2 Interconnection

| Parameter | Value | Source |
|-----------|-------|--------|
| elec_import_capacity | 3 GW | Finland interconnections (SE, EE, RU) |
| elec_export_capacity | 3 GW | Finland interconnections |
| import_capacity (total) | 4.5 GW | Gas + electricity |
| FI-EE Gas (Balticconnector) | 0 GW | Not operational in 2017 (opened 2020) |

---

## 10. Consistency Check Results

### Summary: 2 issues found

| Check | Result |
|-------|--------|
| 1. FI tech names vs REF | **1 WARN**: CCGT_AMMONIA in FI but not in REF (no-op: f_max=0) |
| 2. f_min ≤ f_max | PASS |
| 3. fmin_perc ≤ fmax_perc | PASS |
| 4. Resource prices FI vs INDEP | OK (FI overrides are deliberate) |
| 5. Misc share bounds [0,1], min≤max | PASS |
| 6. Demand magnitudes | All positive |
| 7. FI Misc vs REF overrides | 21 overrides documented |
| 8. Network losses | OK (within 0–20% range) |
| 9. Tightly constrained | DAM_STORAGE, PHS (ratio=1.0 — fixed) |
| 10. Disabled technologies | 10 technologies banned (all justified) |
| 11. Biomass CSV vs REORG workbook | **PERFECT MATCH** (all 6 values) |
| 12. Demands CSV vs REORG workbook | **2 WARN**: HEAT_LOW_T_HW (+7.4%), MOBILITY_FREIGHT (+5.9%) |
| 13. fmin_perc usage | Market shares forced for heat/coal/transport |
| 14. fmax_perc caps | Gas, oil, EVs capped |
| 15. RE fuels | All disabled (avail_exterior=0) |

### Detail on warnings

1. **CCGT_AMMONIA** appears in FI/Technologies.csv with f_max=0 but is not in REF_REGION. This is a no-op (technology is banned so it has no effect) but the name creates an orphan override.

2. **Demand discrepancies** (7.4% and 5.9%): The FI/Demands.csv values differ from the REORG workbook. This is because the workbook was a planning document based on slightly different source data. The CSV values are authoritative — they are what the model actually loads.

---

## 11. Known Issues & Open Questions

### 11.1 Structural issues

| Issue | Impact | Status |
|-------|--------|--------|
| Grid losses (8.64%) too high for Finland (3%) | Over-estimates electricity needed for same demand | **Open** — cannot override per-country in 00_INDEP |
| DH losses (5%) too low for Finland (8.5%) | Under-estimates heat needed for DH | **Open** — same structural limit |
| Technology costs from 2035 DEA | c_inv/c_maint are future costs, not 2017 | **Partially fixed** — 14 key techs updated, 153 remain at 2035 |
| 2015 demands used as 2017 proxy | ~2 years stale | **Accepted** — JRC-IDEES data quality issue |
| 2015 time series used for 2017 | Weather/demand profiles from wrong year | **Accepted** — consistent with demands |
| k-medoids non-determinism | Different runs → different typical days | **Known** — use seed or increase nbr_td |

### 11.2 Calibration decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| Force biomass >40% in IND_BOILER_WOOD | Model prefers gas (cheaper); reality: biomass mandate | REORG 12_Issues_Decisions_Log |
| Force coal 10-30% in DHN/IND | Sunk-cost plants still running in 2017 | REORG 07_VALIDATION_2017 |
| Allow 5 GW electricity imports | Required for feasibility | REORG 12_Issues_Decisions_Log |
| JET_FUEL price = 0.0359 not 0.0824 | 0.0824 was mislabeled pump price | REORG Assumptions_and_Decisions |
| WOOD price kept unchanged | Per user instructions | REORG Assumptions_and_Decisions |

### 11.3 Open questions

1. Should Layers_in_out efficiency degradation (15-20% for 2017 fleet) be applied? If so, a country-specific Layers_in_out mechanism is needed.
2. Should OIL (crude/heavy fuel oil) be explicitly enabled? Current model uses LFO as proxy.
3. PEAT is mentioned as a local Finnish resource but is not modeled — should it be added?
4. The re_share_primary = 0.41 constraint may be too aggressive for a cost-minimization model — it forces renewable share above what the optimizer would naturally choose.

---

## 12. Source Registry

### 12.1 External sources cited

| Source | Used for | URL |
|--------|---------|-----|
| Statistics Finland — Energy Authority | Nuclear capacity | stat.fi |
| Statistics Finland — Energy Statistics | Wind capacity, road/rail statistics | stat.fi |
| Finnish Energy (2024) — District Heating | DHN share (45%), DH losses (8.5%) | energia.fi |
| Energy in Finland 2022 | Grid losses (3%) | doria.fi |
| JRC-IDEES / Eurostat 2015 | All end-use demands | ec.europa.eu |
| ENTSOE, Renewables.ninja | Hourly time series (2015) | entsoe.eu, renewables.ninja |
| DEA Technology Catalogue (2023) | 14 key technology costs (interpolated to 2017) | ens.dk |
| NordPool | Electricity import price (~33 €/MWh) | nordpoolgroup.com |
| Eurostat Key Figures | Modal split data | ec.europa.eu/eurostat |
| ENSPRESO (JRC) | Biomass potentials, solar/wind potentials | ec.europa.eu/jrc |

### 12.2 Internal workbooks

| Workbook | Location | Role |
|----------|---------|------|
| Finland_MASTER_Calibration_REORG.xlsx | Data/exogenous_data/ | Master calibration register (9 sheets) |
| Finland_MASTER_Calibration_old_UPDATED.xlsx | Data/exogenous_data/ | Previous calibration file (24 sheets) |
| DEA_Elec_Heat.xlsx | Data/exogenous_data/ | DEA technology catalogue data (~50 sheets) |
| EnergyScope_Finland_calibration_template_v4.xlsx | Data/exogenous_data/ | Calibration template (5 sheets) |

### 12.3 Key scripts

| Script | Purpose |
|--------|---------|
| scripts/run_calib_case.py | Main calibration runner |
| scripts/reverse_engineer_feb14.py | Reconstructed Technologies.csv from .dat |
| scripts/reverse_engineer_resources.py | Reconstructed Resources.csv from .dat |
| scripts/verify_reconstruction.py | Verified PERFECT MATCH of .dat files |
| esmc/preprocessing/dat_print.py | CSV → AMPL .dat conversion |
| esmc/preprocessing/preprocessing.py | Full preprocessing pipeline |
