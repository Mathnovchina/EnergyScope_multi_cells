# Finland 2017 — Traceability Index

> Maps every model parameter back to its data source, through the full pipeline:
>
> **External source** → **Workbook sheet** → **CSV file** → **print_to_dat** → **AMPL parameter**
>
> Generated: 2025-02-18 | Model year: 2017 | Region: FI

---

## Reading Guide

| Column | Meaning |
|--------|---------|
| **AMPL param** | Name as it appears in the `.dat` / `.mod` file |
| **CSV path** | File the preprocessing pipeline reads |
| **Tier** | INDEP / REF / FI (which tier supplies the value) |
| **Workbook sheet** | Row-level traceability inside the REORG workbook |
| **External source** | Original data provider |

---

## 1. Technologies

### 1.1 Cost & lifetime parameters (inherited from REF_REGION)

These values come from `02_REF_REGION/Technologies.csv` and are **not overridden** by FI:

| AMPL param | Technologies (examples) | Tier | Workbook ref | External source |
|------------|----------------------|------|-------------|----------------|
| c_inv | All 170 techs | REF | 03_MODEL_INPUTS rows 25-58 | DEA Technology Catalogue 2023 (14 key techs interpolated to 2017; 153 at 2035 default) |
| c_maint | All 170 techs | REF | 03_MODEL_INPUTS | DEA Technology Catalogue |
| gwp_constr | All 170 techs | REF | — | ESMC defaults |
| lifetime | All 170 techs | REF | — | DEA Technology Catalogue |
| c_p | All 170 techs | REF | — | DEA Technology Catalogue |

### 1.2 Capacity bounds (FI overrides)

| AMPL param | Technology | FI/Technologies.csv value | Tier | Workbook ref | External source |
|------------|-----------|--------------------------|------|-------------|----------------|
| f_min | NUCLEAR | 2.5 GW | FI | 03_MODEL_INPUTS row 37 (2.76 GW in WB) | Statistics Finland — Energy Authority: Loviisa 1&2 + OL 1&2 |
| f_max | NUCLEAR | 2.8 GW | FI | 03_MODEL_INPUTS row 37 (2.76 GW in WB) | Statistics Finland |
| f_min | WIND_ONSHORE | 2.0 GW | FI | 03_MODEL_INPUTS row 40 (1.5 GW in WB) | Finnish Wind Power Association |
| f_max | WIND_ONSHORE | 2.1 GW | FI | 03_MODEL_INPUTS row 40 (5.0 GW in WB) | Finnish Wind Power Association |
| f_min | HYDRO_DAM | 1.1 GW | FI | 03_MODEL_INPUTS row 42 (1.345 GW in WB) | Statistics Finland |
| f_max | HYDRO_DAM | 1.3 GW | FI | 03_MODEL_INPUTS row 42 (2.383 GW in WB) | Statistics Finland |
| f_min | HYDRO_RIVER | 1.9 GW | FI | 03_MODEL_INPUTS row 43 (3.264 GW in WB) | Statistics Finland |
| f_max | HYDRO_RIVER | 2.1 GW | FI | 03_MODEL_INPUTS row 43 (3.264 GW in WB) | Statistics Finland |
| f_min | COAL_US | 3.5 GW | FI | — | Estimate for 2017 coal fleet |
| f_max | COAL_US | 4.5 GW | FI | — | Estimate for 2017 coal fleet |
| f_min | CCGT | 0.6 GW | FI | — | Estimate for 2017 gas fleet |
| f_max | CCGT | 1.5 GW | FI | — | Estimate for 2017 gas fleet |
| f_min | PV_ROOFTOP | 0.02 GW | FI | — | Finnish Energy / solar growth data |
| f_max | PV_ROOFTOP | 2.0 GW | FI | — | Potential estimation |
| f_max | DHN_SOLAR | (derived) | FI | — | solar_area_ground parameter |
| f_max | DEC_SOLAR | (derived) | FI | — | solar_area_rooftop parameter |

> **Note**: CSV values differ from REORG workbook values because the CSV was updated post-workbook (Feb 10-17 evolution). The CSV is authoritative.

### 1.3 Market share constraints (FI overrides — fmin_perc / fmax_perc)

| AMPL param | Technology | Value | Tier | Workbook ref | External source |
|------------|-----------|-------|------|-------------|----------------|
| fmin_perc | IND_BOILER_WOOD | 0.40 | FI | 05_VALIDATION row 9 | Calibration decision: biomass mandate |
| fmin_perc | DHN_COGEN_WOOD | 0.30 | FI | 05_VALIDATION row 10 | Calibration decision: CHP biomass |
| fmin_perc | DHN_COGEN_COAL | 0.30 | FI | 05_VALIDATION row 8 | Calibration decision: sunk costs |
| fmin_perc | DHN_BOILER_COAL | 0.10 | FI | 05_VALIDATION row 8 | Calibration decision |
| fmin_perc | IND_BOILER_COAL | 0.10 | FI | 05_VALIDATION row 8 | Calibration decision |
| fmax_perc | DHN_COGEN_GAS | 0.20 | FI | — | Calibration decision: gas constrained |
| fmax_perc | DHN_BOILER_OIL | 0.10 | FI | — | Calibration decision: oil limited |
| fmax_perc | IND_BOILER_GAS | 0.20 | FI | — | Calibration decision: gas limited |
| fmin_perc / fmax_perc | CAR_GASOLINE | 0.55 / 0.65 | FI | — | Statistics Finland modal split data |
| fmin_perc / fmax_perc | CAR_DIESEL | 0.30 / 0.40 | FI | — | Statistics Finland |
| fmax_perc | CAR_BEV | 0.01 | FI | — | Negligible 2017 fleet |
| fmax_perc | CAR_PHEV | 0.01 | FI | — | Negligible 2017 fleet |
| fmax_perc | CAR_HEV | 0.05 | FI | — | Small 2017 fleet |
| fmin_perc / fmax_perc | TRUCK_DIESEL | 0.90 / 1.00 | FI | — | Statistics Finland |
| fmax_perc | TRUCK_NG | 0.05 | FI | — | Statistics Finland |
| fmin_perc / fmax_perc | BUS_COACH_DIESEL | 0.90 / 1.00 | FI | — | Statistics Finland |
| fmin_perc / fmax_perc | CARGO_LFO | 0.95 / 1.00 | FI | — | Maritime statistics |
| fmax_perc | CARGO_LNG | 0.05 | FI | — | Maritime statistics |
| fmin_perc / fmax_perc | BOAT_FREIGHT_DIESEL | 0.95 / 1.00 | FI | — | Maritime statistics |
| fmax_perc | BOAT_FREIGHT_NG | 0.05 | FI | — | Maritime statistics |

### 1.4 Banned technologies

| Technology | f_min/f_max | Tier | Reason |
|------------|-----------|------|--------|
| PT_POWER_BLOCK | 0/0 | FI | No CSP |
| ST_POWER_BLOCK | 0/0 | FI | No CSP |
| PT_COLLECTOR | 0/0 | FI | No CSP |
| ST_COLLECTOR | 0/0 | FI | No CSP |
| TIDAL_STREAM | 0/0 | FI | No tidal |
| TIDAL_RANGE | 0/0 | FI | No tidal |
| WAVE | 0/0 | FI | No wave |
| DHN_DEEP_GEO | 0/0 | FI | No deep geothermal |
| CCGT_AMMONIA | 0/0 | FI | Not relevant 2017 |
| COAL_IGCC | 0/0 | FI | Not relevant 2017 |

---

## 2. Resources

### 2.1 Local resources

| AMPL param | Resource | CSV value | Tier | Workbook ref | External source |
|------------|---------|-----------|------|-------------|----------------|
| avail | WOOD | 110,805.66 GWh | FI | 03_MODEL_INPUTS row 14, 04_PRICES | ENSPRESO / local expert estimate |
| c_op | WOOD | 0.022084 M€/GWh | FI | 04_PRICES_PIPELINE row 3 | Local wood price / stat.fi |
| avail | WET_BIOMASS | 1,450.62 GWh | FI | 03_MODEL_INPUTS row 15 | ENSPRESO |
| c_op | WET_BIOMASS | 0.033104 M€/GWh | FI | 04_PRICES | ENSPRESO |
| avail | ENERGY_CROPS_2 | 7,754.11 GWh | FI | 03_MODEL_INPUTS row 16 | ENSPRESO |
| c_op | ENERGY_CROPS_2 | 0.023524 M€/GWh | FI | 04_PRICES | ENSPRESO |
| avail | BIOWASTE | 4,720.94 GWh | FI | 03_MODEL_INPUTS row 17 | ENSPRESO |
| c_op | BIOWASTE | 0.000112 M€/GWh | FI | 04_PRICES | Near-zero gate-fee |
| avail | BIOMASS_RESIDUES | 4,985.24 GWh | FI | 03_MODEL_INPUTS row 18 | ENSPRESO |
| c_op | BIOMASS_RESIDUES | 0.013135 M€/GWh | FI | 04_PRICES | ENSPRESO |
| avail | WASTE | 11,095.02 GWh | FI | 03_MODEL_INPUTS row 19 | Stat.fi waste generation data |
| c_op | WASTE | 0.006079 M€/GWh | FI | 04_PRICES | Stat.fi cost data |

### 2.2 Fossil fuel prices

| AMPL param | Resource | c_op_local FI | c_op_exterior INDEP | Tier applied | Workbook ref | External source |
|------------|---------|---------------|--------------------|----|-------------|----------------|
| c_op | GASOLINE | 0.0588 | 0.082366 | FI | 04_PRICES row 3 | Statistics Finland retail prices |
| c_op | DIESEL | 0.0543 | 0.080 | FI | 04_PRICES row 4 | Statistics Finland retail prices |
| c_op | LFO | 0.0521 | 0.060 | FI | 04_PRICES row 5 | Statistics Finland heating oil |
| c_op | JET_FUEL | 0.0359 | 0.080 | FI | 04_PRICES row 6 | CIF spot estimate |
| c_op | GAS | 0.0195 | 0.044253 | FI | 04_PRICES row 7 | Gasum / stat.fi |
| c_op | COAL | 0.0103 | 0.017658 | FI | 04_PRICES row 8 | Stat.fi coal import price |
| c_op | URANIUM | 0.0093 | 0.003876 | FI | 04_PRICES row 9 | IAEA / stat.fi |
| c_op | ELECTRICITY | 0.0326 | 0.084330 | FI | 04_PRICES row 10 | NordPool Finland area price |

### 2.3 Disabled resources

| Resource | avail_exterior | Tier | Workbook ref |
|----------|---------------|------|-------------|
| GASOLINE_RE | 0 | FI | — |
| DIESEL_RE | 0 | FI | — |
| LFO_RE | 0 | FI | — |
| JET_FUEL_RE | 0 | FI | — |
| GAS_RE | 0 | FI | — |
| H2_RE | 0 | FI | — |
| AMMONIA_RE | 0 | FI | — |
| METHANOL_RE | 0 | FI | — |

---

## 3. Demands

| AMPL param | End-use | Total (GWh or Mpkm/Mtkm) | Tier | Workbook ref | External source |
|------------|---------|---------------------------|------|-------------|----------------|
| end_uses_demand_year | ELECTRICITY | 43,007 GWh | FI | 03_MODEL_INPUTS row 2 (42,912) | JRC-IDEES / Eurostat 2015 |
| end_uses_demand_year | HEAT_HIGH_T | 59,821 GWh | FI | 03_MODEL_INPUTS row 3 (59,965) | JRC-IDEES 2015 |
| end_uses_demand_year | HEAT_LOW_T_SH | 85,636 GWh | FI | 03_MODEL_INPUTS row 4 (86,661) | JRC-IDEES 2015 |
| end_uses_demand_year | HEAT_LOW_T_HW | 20,379 GWh | FI | 03_MODEL_INPUTS row 5 **(18,967 in WB = 7.4% diff)** | JRC-IDEES 2015 |
| end_uses_demand_year | PROCESS_COOLING | 3,757 GWh | FI | 03_MODEL_INPUTS row 6 | JRC-IDEES 2015 |
| end_uses_demand_year | SPACE_COOLING | 2,095 GWh | FI | 03_MODEL_INPUTS row 7 | JRC-IDEES 2015 |
| end_uses_demand_year | MOBILITY_PASSENGER | 90,844 Mpkm | FI | 03_MODEL_INPUTS row 8 (91,992) | Eurostat / stat.fi |
| end_uses_demand_year | MOBILITY_FREIGHT | 36,490 Mtkm | FI | 03_MODEL_INPUTS row 9 **(34,442 in WB = 5.9% diff)** | Eurostat / stat.fi |
| end_uses_demand_year | AVIATION_LONG_HAUL | 15,363 Mpkm | FI | 03_MODEL_INPUTS row 10 | Eurostat aviation |
| end_uses_demand_year | SHIPPING | 148,985 Mtkm | FI | 03_MODEL_INPUTS row 11 | Eurostat maritime stats |
| end_uses_demand_year | NON_ENERGY | 10,708 GWh | FI | 03_MODEL_INPUTS row 12 | JRC-IDEES 2015 |

### Demand sectoral breakdown

Sectors in Demands.csv: Households, Services, Industry, Transportation.

| End-use | Households | Services | Industry | Transportation |
|---------|-----------|----------|----------|---------------|
| ELECTRICITY | 8,760 | 10,822 | 23,425 | 0 |
| HEAT_HIGH_T | 0 | 0 | 59,821 | 0 |
| HEAT_LOW_T_SH | 38,557 | 24,967 | 22,112 | 0 |
| HEAT_LOW_T_HW | 6,009 | 5,240 | 9,130 | 0 |
| MOB_PASSENGER | 0 | 0 | 0 | 90,844 |
| MOB_FREIGHT | 0 | 0 | 0 | 36,490 |

---

## 4. Miscellaneous / Policy Constraints

### 4.1 FI/Misc.json overrides

| AMPL param | FI value | REF default | Tier | Workbook ref | External source |
|------------|---------|------------|------|-------------|----------------|
| %Dhn (share_heat_dhn_min/max) | 0.449–0.451 | 0.02–0.37 | FI | 99_ARCHIVE row 1 (0.45) | Finnish Energy — DH statistics |
| %Public (share_mobility_public_min/max) | 0.160–0.162 | 0.199–0.5 | FI | 99_ARCHIVE row 4 (0.1608) | Statistics Finland / Eurostat modal split |
| %Rail (share_freight_train_min/max) | 0.275–0.277 | 0.109–0.25 | FI | 99_ARCHIVE row 5 (0.2761) | Statistics Finland |
| %Boat (share_freight_boat_min/max) | 0.154–0.156 | 0.156–0.3 | FI | — | Eurostat inland waterway |
| share_freight_road_max | 1.0 | 3.0 | FI | — | Corrected to physical limit |
| %ShortHaul (share_short_haul_flights_min/max) | 0.1643–0.1644 | 0 | FI | — | Eurostat aviation |
| re_share_primary | 0.41 | 0 | FI | 03_MODEL_INPUTS row 65 | Finland's actual RE share (Statistics Finland) |
| elec_import_capacity | 3 GW | — | FI | 06_ASSUMPTIONS row 12 | ENTSO-E interconnection data |
| elec_export_capacity | 3 GW | — | FI | 06_ASSUMPTIONS row 12 | ENTSO-E |
| import_capacity | 4.5 GW | 0 | FI | — | Gas + elec total |
| solar_area_ground | 345.75 km² | 1e15 | FI | — | ENSPRESO ground-based solar |
| solar_area_ground_high_irr | 0 | 1e15 | FI | — | No high-irradiance in Finland |
| solar_area_rooftop | 80.49 km² | 1e15 | FI | — | ENSPRESO rooftop potential |
| solar_area | 338,000 | — | FI | — | Solar area total |
| share_ned | HVC=0.779, MeOH=0.029, NH3=0.192 | all=0 | FI | — | JRC-IDEES petrochemicals split |

### 4.2 Misc_indep.json (global — not traceable per country)

| AMPL param | Value | Tier | Source |
|------------|-------|------|--------|
| i_rate | 0.05 | INDEP | ESMC default |
| gwp_limit_overall | 1e15 | INDEP | No constraint |
| loss_network ELECTRICITY | 0.0864 | INDEP | EU-average grid losses |
| loss_network HEAT_LOW_T_DHN | 0.05 | INDEP | EU-average DH losses |
| power_density_pv | 0.085 GW/km² | INDEP | Literature |
| sm_max | 4 | INDEP | CSP solar multiple |
| c_grid_extra | 367.8 M€/GW | INDEP | Literature |
| EV_batt_charge_time (BATT_LI) | 4 h | INDEP | — |
| EV_batt_discharge_time | 1 h | INDEP | — |

---

## 5. Efficiencies (Layers_in_out)

| AMPL param | Path | Tier | Rows × Cols | Source |
|------------|------|------|-------------|--------|
| layers_in_out | `00_INDEP/Layers_in_out.csv` | INDEP | ~130 × 38 | ESMC default matrix (DEA-based) |

This matrix is **not overrideable per country**. Key Finnish-relevant efficiencies:

| Technology | Input layer | Value | Output layer | Value | Source for efficiency |
|------------|-----------|-------|------------|-------|---------------------|
| NUCLEAR | URANIUM | -2.7027 | ELECTRICITY | 1.0 | DEA ~37% efficiency |
| COAL_US | COAL | -2.0408 | ELECTRICITY | 1.0 | DEA ~49% |
| CCGT | GAS | -1.5873 | ELECTRICITY | 1.0 | DEA ~63% |
| IND_BOILER_WOOD | WOOD | -1.1568 | HEAT_HIGH_T | 1.0 | DEA ~86.4% |
| DHN_COGEN_WOOD | WOOD | -1.8868 | ELEC 0.34 + DHN 1.0 | — | DEA total ~71% |
| IND_BOILER_COAL | COAL | -1.2195 | HEAT_HIGH_T | 1.0 | DEA ~82% |

> **Note**: REORG workbook mentions 15-20% efficiency degradation for wood/coal boilers for 2017 fleet. It is unclear if this was applied to the current Layers_in_out.csv. The values above appear to be standard DEA BAT values.

---

## 6. Time Series & Temporal

| File | Path | Tier | Source | Notes |
|------|------|------|--------|-------|
| Time_series.csv | `FI/Time_series.csv` | FI | ENTSOE, renewables.ninja, JRC-IDEES (2015 year) | 8760h × 13 profiles |
| Weights.csv | `FI/Weights.csv` | FI | Calibration-determined | HEAT_LOW_T_SH=0.204, SPACE_COOLING=0.087 |

---

## 7. Storage

| File | Path | Tier | Source |
|------|------|------|--------|
| Storage_characteristics.csv | `00_INDEP/` | INDEP | ESMC defaults |
| Storage_eff_in.csv | `00_INDEP/` | INDEP | ESMC defaults |
| Storage_eff_out.csv | `00_INDEP/` | INDEP | ESMC defaults |
| Storage_power_to_energy.csv | `FI/` | FI | PHS: 7.353h charge/discharge only |

---

## 8. Pipeline Trace (Example: NUCLEAR → .dat)

```
External: Statistics Finland → Loviisa 1&2 = 1.012 GW, OL 1&2 = 1.76 GW
→ Total nuclear capacity ~ 2.77 GW
→ REORG 03_MODEL_INPUTS: NUCLEAR f_min=2.76, f_max=2.76
→ Calibration adjustments: relaxed to f_min=2.5, f_max=2.8
→ FI/Technologies.csv: NUCLEAR, 2.5, 2.8, ,
→ REF_REGION deepcopy (c_inv=5006.1, c_maint=106.7, lifetime=60, c_p=0.85)
→ FI.update( f_min=2.5, f_max=2.8)
→ concat_reg_data()
→ print_df() → ESMC_2017_FI/ESMC_12TD.dat: param f_min := ... NUCLEAR 2.5 ...
→ AMPL: f_min['NUCLEAR'] = 2.5
```
