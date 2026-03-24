# Finland 2035 / 2050 Baseline — Preflight Report

**Date**: 2025-01  
**Author**: auto-generated (Copilot session)  
**Status**: PRE-RUN — no optimisation has been launched yet  
**Branch**: `Finland`

---

## 1  Purpose

Prepare **single-cell Finland optimisations for 2035 and 2050** using the
existing `Data/2035/` and `Data/2050/` datasets.  No run may be launched until
every open question in §9 is resolved and the runner script passes dry-run
without warnings.

Companion files:
| Deliverable | Path |
|---|---|
| Provenance CSV | `Data/exogenous_data/FI_baseline_inputs_provenance_2035_2050.csv` |
| Runner script | `scripts/run_fi_baseline_future.py` |
| Hypotheses CSV | `Docs/fi_future_baseline_hypotheses.csv` |
| This report | `Docs/fi_baseline_preflight_2035_2050.md` |

---

## 2  ESMC Data-Layering Architecture

ESMC uses a **three-tier merge** (code: `esmc/utils/region.py` → `read_data()`
+ `esmc/preprocessing/dat_print.py`):

```
Tier 1  Data/<year>/00_INDEP/          region-independent globals
Tier 2  Data/<year>/02_REF_REGION/     reference-region base template
Tier 3  Data/<year>/FI/                Finland overrides  (pandas .update())
```

- **`.update()` semantics**: replaces matching-index rows only.  Cannot add new
  technologies.  Missing rows in FI/ silently inherit REF values.
- **Time series**: never merged — each region reads its own complete 8760 h file
  from `<region>/Time_series.csv`.  `02_REF_REGION/Time_series.csv` is all zeros
  (placeholder).
- **Config dicts** (`Misc.json`, `Misc_indep.json`): deep-merged; FI scalars
  overwrite REF scalars; nested dicts are recursively merged.

### Constraint toggles

| Flag | If `None` / `False` | Affected constraint |
|---|---|---|
| `gwp_limit_overall` | `None` → drops `Minimum_GWP_reduction_global` | GWP budget |
| `re_share_primary` | `None` → drops `Minimum_RE_share` | RE share |
| `f_perc` | `False` → drops `f_max_perc` / `f_min_perc` | Tech share limits |

---

## 3  File Inventory

### 3.1  `Data/2035/`

| Tier | File | Parameters | Source |
|---|---|---|---|
| 00_INDEP | `Layers_in_out.csv` | 167 tech × 39 layers | DEA catalogues |
| 00_INDEP | `Storage_characteristics.csv` | Storage eff, losses | DEA |
| 00_INDEP | `Storage_eff_in.csv` | Storage charge eff | DEA |
| 00_INDEP | `Storage_eff_out.csv` | Storage discharge eff | DEA |
| 00_INDEP | `Misc_indep.json` | i_rate=0.015, gwp_limit=1e15, grid_loss=0.047, 8760h | Thesis defaults |
| 00_INDEP | `Reference_values.csv` | Normalisation ref | Thesis |
| 02_REF | `Technologies.csv` | 167 techs, c_inv/c_maint/lifetime/f_min/f_max | DEA 2035 interpolation |
| 02_REF | `Resources.csv` | Fuel costs, GWP, avail | JRC + EU Ref Scenario |
| 02_REF | `Demands.csv` | End-use demands | EU Ref Scenario 2020 |
| 02_REF | `Misc.json` | gwp_limit=1e15, share_heat_dhn 0.02–0.37, solar_area=1e15 | Thesis defaults (Belgium-based) |
| 02_REF | `Time_series.csv` | All zeros (placeholder) | — |
| 02_REF | `Storage_power_to_energy.csv` | P/E ratios | DEA |
| 02_REF | `Exchanges.csv` | Exchange tech mapping | Thesis |
| FI | `Technologies.csv` | 20 tech overrides (f_min/f_max) | Finland capacity data ~2020 |
| FI | `Resources.csv` | 6 local resources + 9 imported | ENSPRESO + national stats |
| FI | `Demands.csv` | Full sectoral demand | JRC-IDEES + EU Ref Scenario |
| FI | `Misc.json` | short_haul_flights=16.4%, NED shares, elec_export=28095 | Finnish national data |
| FI | `Time_series.csv` | 8760 h wind/solar/hydro/demand | MERRA-2 / OPSD / JRC-EFAS (year 2015) |
| FI | `Storage_power_to_energy.csv` | FI-specific P/E ratios | Derived |
| FI | `Exchanges.csv` | FI exchange tech mapping | Thesis |

### 3.2  `Data/2050/`

**Identical directory structure.**  Key differences from 2035:

| Parameter | 2035 | 2050 | Δ |
|---|---|---|---|
| Electricity demand | (from Demands.csv) | −3.3% | Efficiency gains |
| Cooling demand | — | +18.4% | Climate warming assumption |
| Aviation demand | — | +26.8% | Growth projection |
| GAS cost | 0.044 | 0.053 | +20% |
| PV c_inv (REF) | — | −17% | Learning curve |
| Misc_indep.json | — | adds `RES_IMPORT_CONSTANT` set | May affect import modeling |
| FI/Technologies.csv | 20 overrides | **identical to 2035** | ⚠ See §7 |
| FI/Resources.csv | 6 local resources | **identical to 2035** | ⚠ See §7 |

---

## 4  Thesis Reference Map

Source: Thiran V., "Whole-energy system models for Belgium, Europe, and beyond"
(v2.3, 250 pp).

| Topic | Chapter/Section | Pages | Key content |
|---|---|---|---|
| Technology cost data | §1.2.1 | 80–82 | DEA catalogues [114][128][129]; linear interpolation to target year |
| Demand projection | §1.2.2 | 82–86 | EU Reference Scenario 2020 + JRC-IDEES for baselines |
| Resource potentials | §1.2.3 | 93–99 | ENSPRESO (ENS_Med scenario) for wind/solar/biomass; JRC for hydro |
| Greenfield assumption | §1.2.3 | 94 | _"[wind/solar/hydro] and cross-border transmission are the only ones where we consider the legacy capacity. For all other techs, the model can install any quantity (down to zero)."_ |
| Time series weather year | §1.2.4 | 99–104 | MERRA-2 reanalysis, OPSD, JRC-EFAS; reference year **2015** |
| Fossil-free scenario | §4 | 135–140 | Bans fossil imports (`avail_exterior=0`) rather than GWP cap |
| Multi-cell exchanges | §1.2.5 | 104–108 | NTC-based electricity trade between cells |
| Typical-day method | §1.3 | 108–114 | k-medoids clustering, default 12 TDs (thesis) |

---

## 5  Current Working Set — FI Override Parameters

### 5.1  FI/Technologies.csv  (identical for 2035 and 2050)

| Technology | f_min (GW) | f_max (GW) | Interpretation |
|---|---|---|---|
| NUCLEAR | 4.360 | 5.000 | OL1+OL2+OL3+Loviisa (existing fleet) |
| CCGT | 0.000 | 10.000 | — |
| WIND_ONSHORE | 0.496 | 30.770 | f_min = ~2020 installed |
| WIND_OFFSHORE | 0.000 | 21.270 | No current fleet in ~2020 data |
| PV_ROOFTOP | 0.000 | 13.680 | — |
| PV_UTILITY | 0.000 | 58.780 | — |
| HYDRO_DAM | 1.345 | 2.383 | Tight band (existing dams) |
| HYDRO_RIVER | 3.264 | 3.264 | Fixed (existing run-of-river) |
| GEOTHERMAL_DEEP | 0.000 | 0.000 | Not available in Finland |
| DEC_SOLAR_THERMAL | 0.000 | 9.476 | — |
| DHN_SOLAR_THERMAL | 0.000 | 9.476 | — |
| TRAMWAY_TROLLEY | 0.000 | 0.000 | — |
| BUS_COACH_FC_HYBRIDH2 | 0.000 | 0.730 | — |
| TRAIN_PUB | 0.001 | 0.530 | — |
| TRAIN_FREIGHT | 0.003 | 0.079 | — |
| BOAT_FREIGHT_NG | 0.000 | 0.000 | — |
| BOAT_FREIGHT_DIESEL | 0.000 | 1.000 | — |
| BOAT_FREIGHT_METHANOL | 0.000 | 1.000 | — |
| TRUCK | 0.390 | 3.000 | — |
| DEC_BOILER_GAS | 0.000 | 20.000 | — |

### 5.2  FI/Resources.csv — Local resources

| Resource | avail (GWh/y) | Notes |
|---|---|---|
| WOOD | 110 806 | Forest biomass |
| WET_BIOMASS | 1 451 | Biogas feedstock |
| WASTE | 5 175 | Municipal/industrial waste |
| RES_WIND | 0 | (controlled by f_max, not avail) |
| RES_SOLAR | 0 | (controlled by f_max, not avail) |
| RES_HYDRO | 0 | (controlled by f_max, not avail) |

Import resources (GAS, DIESEL, LFO, etc.) inherit `02_REF_REGION` costs.

### 5.3  Misc.json key config (2035 → 2050)

| Parameter | 2035 | 2050 |
|---|---|---|
| short_haul_flights | 16.4% | 19.7% |
| elec_export | 28 095 GWh | 28 095 GWh |
| NED_batt / NED_BEV / NED_PHEV | 3.6 / 4.2 / 4.2 | 3.6 / 4.2 / 4.2 |

---

## 6  Numeric Warnings

| # | Severity | Issue | Recommendation |
|---|---|---|---|
| N1 | **HIGH** | 163 / 167 REF_REGION techs have `f_max = 1e15` | Cap at 100 GW (power) / 1000 GW (storage) via patch — see hypothesis H08 |
| N2 | **HIGH** | `gwp_limit_overall = 1e15` in both years | Effectively no GWP constraint. Must set meaningful value — see H01–H05 |
| N3 | **MEDIUM** | `solar_area = 1e15` in REF Misc.json | May cause large coefficient in LP. Consider FI-specific cap (~200 km²) |
| N4 | **MEDIUM** | `02_REF_REGION/Time_series.csv` all zeros | Expected. FI/Time_series.csv provides real data. Verify no code path reads REF ts. |
| N5 | **LOW** | 2050 `Misc_indep.json` has `RES_IMPORT_CONSTANT` set not in 2035 | May affect import modelling. Verify code handles missing set gracefully for 2035. |
| N6 | **LOW** | `grid_loss = 0.047` (both years) | Acceptable for Finland (historical ~5%). No action needed. |

---

## 7  Decisions Log

Decisions recorded 2025-03-24.  Marked ✅ = decided, ⚠️ = needs specific values.

### 7.1  Brownfield f_min for 2035 and 2050 ✅

FI/Technologies.csv is **byte-for-byte identical** between 2035 and 2050.
This means `WIND_ONSHORE f_min = 0.496 GW` (≈ 2020 installed), while Finland
had 6.9 GW wind installed by 2024.

**Decision**: YES — update f_min via patches to reflect committed/built capacity.
See hypotheses H06, H07.  Exact values to be set in patch files.

### 7.2  Identical FI resource availability for 2035 and 2050

FI/Resources.csv (local resources) is identical between years.  WOOD =
110 806 GWh in both.

**Status**: Open.  May adjust biomass potential if justified by LULUCF data.

### 7.3  GWP constraint strategy ✅

**Decision**: Use `gwp_limit_overall` in config dict (not fossil-fuel ban).

#### Model GWP accounting (verified from AMPL source)

- **Constraint**: `sum{c in REGIONS, r in RESOURCES} CO2_net[c,r] <= gwp_limit_overall`
- **CO2_net**: direct combustion emissions only (not lifecycle GWP)
- **Units**: **ktCO2-eq./year** throughout (co2_net factor in ktCO2/GWh × resource use in GWh)
- Imported electricity has `co2_net = 0` (no emissions attributed to imports)

#### Finnish national climate plan trajectory

| Reference point | GHG emissions | Source |
|---|---|---|
| Finland 2017 (calibrated) | **41 200 ktCO2** | ESMC v37 calibration (0.1% error vs Statistics Finland) |
| Finland total GHG 2017 | ~55 000 ktCO2-eq | UNFCCC (incl. agriculture, waste, industrial process) |
| LULUCF net sink 2017 | ~−21 000 ktCO2 | Statistics Finland (declining trend) |
| **Non-energy sectors** (agriculture, waste, process) | **~10 000–13 000 ktCO2** | Hard to abate; stable over time |

**Carbon Neutrality Act (2035)**: Net emissions ≤ LULUCF sink capacity.
- Pessimistic LULUCF sink estimate: ~21 000 ktCO2
- Total GHG budget: ~21 000 ktCO2
- Non-energy residual: ~10 000–13 000 ktCO2
- **Energy-system budget: ~8 000–11 000 ktCO2** (aggressive)
- Progressive interpretation (50% reduction from 2017): **~21 000 ktCO2**

**EU Climate Law (2050)**: Net-zero; Finland targets climate-positive.
- Near-zero energy system: **~3 000 ktCO2** (residual waste/process heat)

#### Recommended `--gwp-limit` values

| Run | gwp_limit | Rationale | Feasibility |
|---|---|---|---|
| 2035 progressive (first run) | **21 000** | ~50% reduction from 2017; aligned with national plan | Low risk |
| 2035 moderate | 15 000 | ~60% reduction; energy sector only | Medium |
| 2035 strict (sensitivity) | 0 | Net-zero energy system | High risk |
| 2050 near-zero (first run) | **3 000** | Residual emissions from hard-to-abate | Low–Medium |
| 2050 strict (sensitivity) | 0 | Full net-zero | Medium |

### 7.4  Electricity trade ✅

**Decision**: Allow trade.  Patch sets `avail_exterior = 25 000 GWh` for
ELECTRICITY in both `fi_baseline_2035.csv` and `fi_baseline_2050.csv`.
Note: imported electricity has `co2_net = 0`, so trade does not affect GWP
accounting (consistent with multi-cell model where each cell tracks own emissions).

### 7.5  District heating share bounds ✅

REF_REGION default: `share_heat_dhn_min = 0.02`, `share_heat_dhn_max = 0.37`.
Finland 2017 calibration used 0.449–0.451 (tight band).
Finland reality: ~46% DHN share (2023).
FI 2035/2050 Misc.json has **no DHN override** — inherits REF 0.02–0.37.

**Decision**: Override via runner CLI — `--dhn-min 0.42 --dhn-max 0.50`:
- Lower bound 0.42: allows slight infrastructure consolidation
- Upper bound 0.50: allows expansion (Finnish policy targets ~50% by 2050)

### 7.6  Typical-day count ✅

**Decision**: 12 typical days (thesis default).  Runner default updated.

### 7.7  Numeric f_max capping ✅

**Decision**: NO capping.  163/167 techs at f_max=1e15 is the multi-cell
default and has not caused issues.  Leave as-is.

---

## 8  Data Provenance Summary

Full provenance in `Data/exogenous_data/FI_baseline_inputs_provenance_2035_2050.csv`.

| Source dataset | Files affected | Reference |
|---|---|---|
| DEA Technology Catalogues [114][128][129] | Layers_in_out, Storage_*, Technologies (REF) | Thesis §1.2.1 p.80 |
| EU Reference Scenario 2020 | Demands (REF + FI) | Thesis §1.2.2 p.82 |
| JRC-IDEES | Demands (sectoral detail) | Thesis §1.2.2 p.84 |
| ENSPRESO (ENS_Med) | Resources (renewables) | Thesis §1.2.3 p.93 |
| JRC Hydropower | Hydro capacity + time series | Thesis §1.2.3 p.98 |
| MERRA-2 / OPSD | Wind + solar time series (weather year 2015) | Thesis §1.2.4 p.99 |
| Finnish national statistics | FI/Technologies f_min/f_max, Misc.json | 2017 calibration heritage |

### Git provenance

Key commits touching `Data/2035/` and `Data/2050/`:
- `27b8c35` — Initial addition of 2035/2050 data
- `40a03df` — CSV separator standardisation
- `bab40a9` — Demand recomputation
- `a03c6b5` — latest update

---

## 9  Do-Not-Touch List

These files/directories must **not** be modified during future-year runs:

| Path | Reason |
|---|---|
| `Data/2017/` | 2017 calibration data (v37 final). Frozen. |
| `Data/*/00_INDEP/` | Shared across all regions. Patches only via runner. |
| `Data/*/02_REF_REGION/` | Shared reference template. Patches only via runner. |
| `calibration/` | 2017 calibration patches (18 patches, v37). Frozen. |
| `esmc/` | Model source code. No modifications for scenario runs. |

**Safe to modify** (with git tracking):
- `Data/*/FI/` — Finland overrides (but commit before each run)
- `scripts/run_fi_baseline_future.py` — runner script
- `case_studies/FI/manual_runs/` — output directory

---

## 10  Recommended Run Sequence

1. **Dry run 2035**: `python scripts/run_fi_baseline_future.py --year 2035 --name national_plan_2035 --dry-run --kmedoid --gwp-limit 21000 --dhn-min 0.42 --dhn-max 0.50 -p calibration/patches/fi_baseline_2035.csv`
2. **Review** `run_metadata.json` and `README.md` in output directory
3. **First solve** (2035, national plan): `python scripts/run_fi_baseline_future.py --year 2035 --name national_plan_2035 --kmedoid --gwp-limit 21000 --dhn-min 0.42 --dhn-max 0.50 -p calibration/patches/fi_baseline_2035.csv`
4. **Validate**: energy balance, capacity mix, cost breakdown, CO2_net total
5. **2050 solve**: `python scripts/run_fi_baseline_future.py --year 2050 --name national_plan_2050 --kmedoid --gwp-limit 3000 --dhn-min 0.42 --dhn-max 0.50 -p calibration/patches/fi_baseline_2050.csv`
6. **Sensitivity**: tighten 2035 to `--gwp-limit 15000`, then `--gwp-limit 0`

---

## 11  Archive Housekeeping

**DONE** (2025-03-24): All 131 runs from 2017 calibration moved to
`case_studies/FI/_archive_2017calib/`.  `manual_runs/` is now empty and
ready for 2035/2050 runs.

Also archived:
- Root-level utility scripts (14 files) → `_archive_2017calib/`
- scripts/ calibration scripts (12 files) → `scripts/_archive_2017calib/`

Runner script: use `--name` with descriptive prefixes (e.g.,
`baseline_2035_v1_gwp15k`) to clearly identify future runs.
