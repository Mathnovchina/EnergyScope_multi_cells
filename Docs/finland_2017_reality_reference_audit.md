# Finland 2017 Reality Reference Audit

**Date**: 2025-06-14  
**File**: `calibration/reality/finland_2017_reference.csv`

---

## Overview

| Property | Before | After |
|----------|--------|-------|
| Rows | 26 | 26 (unchanged) |
| Columns | 7 | 9 (+model_key, +model_mapping) |
| Metrics scored by runner | 11 | 11 (unchanged — scorer is separate) |
| Metrics plotted by validate_run.py | — | 18 |
| Metrics with model mapping | 0 | 23 (3 unmappable) |

---

## Column Definitions

| Column | Description |
|--------|-------------|
| `category` | Grouping: primary_energy, electricity, heat, emissions, transport, misc |
| `metric` | Specific measurement within category |
| `value` | Finland 2017 actual value |
| `unit` | TWh, MtCO2, or fraction |
| `weight` | Scoring weight (used by run_calib_manual.py and score_all_fi_runs.py) |
| `source` | Data provenance |
| `model_key` | **NEW** — programmatic key used in extraction code (e.g. PE_BIOMASS) |
| `model_mapping` | **NEW** — exact formula: which files/rows/columns to read |
| `notes` | Human-readable explanation |

---

## Metric-by-Metric Mapping

### Primary Energy (8 metrics)
| metric | value | model_key | Extractable? | Notes |
|--------|-------|-----------|-------------|-------|
| total | 380 TWh | — | Computed as sum | Derived from other PE metrics |
| biomass | 100 TWh | PE_BIOMASS | ✅ | WOOD+WET_BIOMASS+BIOWASTE+BIOMASS_RESIDUES+ENERGY_CROPS_2 |
| oil | 82 TWh | PE_OIL | ✅ | GASOLINE+DIESEL+LFO+JET_FUEL (fossil only) |
| gas | 20 TWh | PE_GAS | ✅ | GAS resource |
| coal_peat | 35 TWh | PE_COAL | ⚠️ Proxy | Model has COAL only — peat is lumped in |
| nuclear | 65 TWh | PE_NUCLEAR | ✅ | URANIUM resource |
| hydro | 15 TWh | PE_HYDRO | ✅ | RES_HYDRO resource |
| wind | 5 TWh | PE_WIND | ✅ | RES_WIND resource |
| solar | 0.1 TWh | PE_SOLAR | ✅ | RES_SOLAR resource |

### Electricity (11 metrics)
| metric | value | model_key | Extractable? | Notes |
|--------|-------|-----------|-------------|-------|
| generation | 65.1 TWh | ELEC_TOTAL | ✅ | Sum of domestic generation |
| nuclear | 21.4 TWh | ELEC_NUCLEAR | ✅ | NUCLEAR in Year_balance |
| hydro | 14.5 TWh | ELEC_HYDRO | ✅ | HYDRO_DAM + HYDRO_RIVER |
| wind | 4.8 TWh | ELEC_WIND | ✅ | WIND_ONSHORE + WIND_OFFSHORE |
| chp | 25.0 TWh | ELEC_CHP | ✅ | All *_COGEN_* + DEC_ADVCOGEN_* techs |
| condensation | 5.5 TWh | ELEC_CONDENSATION | ✅ | CCGT+OCGT+COAL_US+COAL_IGCC+CCGT_AMMONIA+BIOMASS_TO_POWER |
| solar | 0.09 TWh | ELEC_SOLAR | ✅ | PV_ROOFTOP + PV_UTILITY |
| geothermal | 0 TWh | ELEC_GEOTHERMAL | ✅ | GEOTHERMAL tech |
| gas | 3.2 TWh | ELEC_GAS | ✅ | Gas CHP + gas condensation |
| **peat** | **2.6 TWh** | — | **❌ Not extractable** | Peat is not a separate resource |
| imports | 20.3 TWh | ELEC_IMPORTS | ✅ | ELECTRICITY resource (exterior) |

### Heat (2 metrics)
| metric | value | model_key | Extractable? | Notes |
|--------|-------|-----------|-------------|-------|
| dh_production | 36.5 TWh | HEAT_DHN | ✅ | All DHN_* techs in HEAT_LOW_T_DHN layer |
| dh_share | 0.45 | — | ⚠️ Complex | Needs Demands data, not in standard outputs |

### Emissions (1 metric)
| metric | value | model_key | Extractable? | Notes |
|--------|-------|-----------|-------------|-------|
| co2 | 41.2 MtCO2 | CO2 | ✅ | Sum of CO2_net from Gwp_breakdown.csv |

### Transport (2 metrics)
| metric | value | model_key | Extractable? | Notes |
|--------|-------|-----------|-------------|-------|
| gasoline_car_share | 0.60 | GASOLINE_CAR_SHARE | ✅ | CAR_GASOLINE / total car mobility |
| diesel_truck_share | 0.95 | DIESEL_TRUCK_SHARE | ✅ | TRUCK_DIESEL / total truck mobility |

### Misc (1 metric)
| metric | value | model_key | Extractable? | Notes |
|--------|-------|-----------|-------------|-------|
| re_share_primary | 0.41 | RE_SHARE | ✅ | (biomass+hydro+wind+solar) / total PE |

---

## Known Limitations

1. **PEAT**: Not a separate model resource. Finland uses significant peat for energy (historically ~15 TWh). The model's COAL resource acts as a coal+peat proxy. The reality target of 35 TWh for "coal_peat" includes both. Individual peat electricity (2.6 TWh) cannot be scored.

2. **DH share**: Requires comparing DHN demand to total heating demand, which needs Demands data not present in standard outputs. Not included in validation plots.

3. **CHP double-counting risk**: CHP technologies produce both electricity and heat. CHP electricity is counted in ELEC_CHP but NOT added to nuclear/hydro/wind counts. Gas CHP *is* included in both ELEC_CHP and ELEC_GAS — these overlap by design (gas is a fuel subset of CHP). The error chart treats them independently.

4. **Electricity imports**: Mapped to ELECTRICITY resource exterior consumption. In reality this is net imports (imports minus exports). The model typically shows only imports since Finland is a net importer.

---

## Scoring vs Plotting Coverage

The scoring engine in `run_calib_manual.py` uses **11 metrics** with specific weights:
PE_BIOMASS(1.5), PE_OIL(1.5), PE_GAS(1.0), PE_COAL(1.5), PE_NUCLEAR(1.0), PE_HYDRO(0.8), PE_WIND(0.8), ELEC_NUCLEAR(1.5), ELEC_HYDRO(1.2), ELEC_WIND(1.0), CO2(2.0)

The validation plotter `validate_run.py` extracts **24 metrics** and plots **18** against reality.

The scoring is intentionally conservative (fewer metrics, larger weight on big categories) to avoid overfitting. The plotting is intentionally comprehensive to give human reviewers full visibility.
