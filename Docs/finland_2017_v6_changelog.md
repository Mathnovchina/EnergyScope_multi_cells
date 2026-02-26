# Finland 2017 Calibration v6 — Change Log & Progress Report

**Created:** 2025-02-28  
**Baseline:** v5_fperc_repro (restored 2026-02-26)  
**Goal:** Match Finland 2017 energy statistics within ±20%  
**Backup location:** `Data/2017/FI/backups_v5_fperc/`

---

## Step 1: Constraint Violation Verification ✅

**Finding:** The CPLEX 22.1.2 barrier solver reports "feasible or optimal but numeric issue":

| Variable | F (output) | f_max (input) | Violation |
|----------|-----------|---------------|-----------|
| NUCLEAR | 5.679 GW | 2.8 GW | +103% |
| WIND_ONSHORE | 2.670 GW | 2.1 GW | +27% |
| WIND_OFFSHORE | 0.182 GW | 0.1 GW | +82% |

**Log evidence** (from `case_studies/FI/calib_2017_finland_v5_fperc_repro/log.txt`):
```
CPLEX 22.1.2: reported feasible or optimal but numeric issue; objective 2.103313157e+14
WARNING: "Tolerance violations"
  Type                         MaxAbs [Name]   MaxRel [Name]
* variable bounds              7E+01           1E+01
* algebraic con(s)             1E+04           2E+02
```

**Root cause:** 120 technologies with f_max=1e15 create 15 orders of magnitude variable range.
Barrier solver (crossover=0) cannot achieve meaningful feasibility tolerance.

**Classification:** CONFIRMED solver degeneracy — NOT diagnostic artifacts.

---

## Step 2: Strategy vs Input Audit ✅

**Verified:** Current FI files match v5_fperc restoration exactly.
- Technologies.csv: 47 overrides (all correct)
- Resources.csv: 25 overrides (all correct)
- 120 REF_REGION techs with f_max=1e15 have no FI override (confirming degeneracy source)

**Additional findings vs strategy document:**
- Strategy missed GRID, DHN, EFFICIENCY, BEV_BATT, PHEV_BATT, DEC_THHP_GAS_COLD
- Strategy missed 13 TS_* thermal storage technologies
- NUCLEAR_SMR already f_max=0 in REF (no override needed)
- All proposed changes are directionally correct (no f_max < f_min errors)

---

## Block 0: Degeneracy Fix (NUMERICAL STABILIZATION) ✅

**Date applied:** 2026-02-26  
**Status:** ✅ COMPLETED (universal cap approach)  
**Objective:** 1.94e+07 | solve_result_num=-1

### Changes Applied (130 total):

#### New rows added (121):
- **72 DISABLED** (f_max=0): Future/non-existent technologies
  - Future fuels: CCGT_AMMONIA, COAL_IGCC, BIOMASS_TO_POWER
  - Hydrogen chain: H2_ELECTROLYSIS, H2_NG, H2_BIOMASS, H2_NEW, etc.
  - Power-to-X: POWER_TO_GASOLINE/DIESEL/JET_FUEL/LFO
  - H2-to-liquids: H2_TO_GASOLINE/DIESEL/JET_FUEL/LFO
  - Biomass-to-liquids: BIOMASS_TO_*/BIOWASTE_TO_* (8 techs)
  - CCS: ATM_CCS, INDUSTRY_CCS, CO2_STORAGE
  - Methanol: SYN_METHANOLATION, METHANE_TO_METHANOL, etc.
  - Ammonia: HABER_BOSCH, AMMONIA_TO_H2
  - Alt transport: BUS_COACH_HYDIESEL, BUS_COACH_CNG_STOICH, CAR_NG, etc.
  - Alt shipping: CARGO_LNG/METHANOL/AMMONIA/FUELCELL_*
  - Future storage: H2_STORAGE, AMMONIA_STORAGE, METHANOL_STORAGE, CAES
  - Gas infrastructure: GAS_PIPELINE, GAS_SUBSEA (single-region, not used)
  - Disabled thermal storage: TS_DEC_ADVCOGEN_*, TS_DEC_THHP_GAS

- **35 CAPPED** (realistic f_max): Existing Finnish technologies
  - DHN heating: DHN_HP_ELEC=0.5, DHN_BOILER_GAS=2.0, DHN_BOILER_WOOD=5.0, DHN_COGEN_WASTE=1.0
  - DEC heating: DEC_HP_ELEC=5.0, DEC_BOILER_GAS=5.0, DEC_BOILER_WOOD=10.0, DEC_BOILER_OIL=8.0, etc.
  - Industry: IND_COGEN_GAS=2.0, IND_COGEN_COAL=2.0, IND_DIRECT_ELEC=5.0, etc.
  - Storage: BATT_LI=1.0, GAS/DIESEL/GASOLINE/JET_FUEL/LFO_STORAGE=100
  - Thermal storage: TS_DEC_*=parent cap, TS_DHN/HIGH_TEMP=20.0

- **14 KEPT LARGE** (f_max=100000): Infrastructure/demand-driven
  - GRID, DHN, EFFICIENCY, BEV_BATT, PHEV_BATT
  - Transport: BUS_COACH_DIESEL, TRAMWAY_TROLLEY, TRAIN_PUB/FREIGHT, PLANE_*
  - Shipping/freight: BOAT_FREIGHT_DIESEL, CARGO_LFO, OIL_TO_HVC

#### Existing FI rows modified (9):
| Technology | Old f_max | New f_max | Reason |
|-----------|----------|----------|--------|
| DEC_DIRECT_ELEC | 100000 | 5.0 | Finnish decentralised electric heating limited |
| DHN_COGEN_COAL | 100000 | 5.0 | Coal CHP capacity bounded |
| DHN_COGEN_WOOD | 100000 | 10.0 | Wood CHP capacity bounded |
| IND_BOILER_COAL | 100000 | 5.0 | Industrial coal boiler bounded |
| IND_BOILER_GAS | 100000 | 5.0 | Industrial gas boiler bounded |
| IND_BOILER_WOOD | 100000 | 15.0 | Industrial wood boiler bounded |
| IND_COGEN_WOOD | 100000 | 8.0 | Industrial wood CHP bounded |
| TRUCK_METHANOL | 100000 | 0.0 | Non-existent, disabled |
| TRUCK_NG | 100000 | 0.0 | Non-existent, disabled |

### Expected Impact:
- Variable range reduced from 15 to ~5 orders of magnitude
- Barrier solver should converge properly
- Constraint violations (NUCLEAR, WIND) should disappear
- Solution quality dramatically improved (no more 10¹¹ GW deployments)

### Block 0 Results:
| metric | v5_fperc | Block 0 | Change |
|--------|---------|---------|--------|
| TOTAL_OIL | 203,546 | 137,926 | -32% |
| WOOD | 3,024 | 15,353 | +408% |
| COAL | 9,188 | 19,347 | +111% |
| URANIUM | 79,959 | 120,558 | +51% |
| Max tech F | 6.5e13 | 78,043 | -99.9999% |

---

## Block 1: Oil Overconsumption Fix (HISTORICAL REALISM) ✅

**Status:** ✅ COMPLETED | Obj=2.47e+07

### Planned Changes:
| Item | Parameter | Current | Proposed | Classification |
|------|----------|---------|----------|---------------|
| LFO | avail_exterior | 150000 | 80000 | Historical realism |
| JET_FUEL | avail_exterior | 15000 | 5000 | Historical realism |

---

## Block 2: Biomass Forcing (CALIBRATION FORCING) ✅

**Status:** ✅ COMPLETED | Obj=1.67e+07 | WOOD 15K→52K GWh

### Planned Changes:
| Technology | Parameter | Current | Proposed | Classification |
|-----------|----------|---------|----------|---------------|
| IND_BOILER_WOOD | fmin_perc | 0.0 | 0.30 | Calibration forcing |
| IND_COGEN_WOOD | fmin_perc | 0.0 | 0.15 | Calibration forcing |
| DHN_COGEN_WOOD | fmin_perc | 0.0 | 0.30 | Calibration forcing |
| DEC_BOILER_WOOD | fmin_perc | 0.0 | 0.15 | Calibration forcing |
| GAS | avail_exterior | 28000 | 22000 | Calibration forcing |
| COAL | avail_exterior | 50000 | 35000 | Calibration forcing |

---

## Block 3: Nuclear Tightening (HISTORICAL REALISM) ✅

**Status:** ✅ COMPLETED | Obj=2.57e+07 | URANIUM cap violated (192K vs 62K input)

### Planned Changes:
| Item | Parameter | Current | Proposed | Classification |
|------|----------|---------|----------|---------------|
| NUCLEAR | f_min | 2.70 | 2.76 | Historical realism |
| URANIUM | avail_exterior | 100000 | 62000 | Historical realism |

---

## Block 4: Solar Cap (HISTORICAL REALISM) ✅

**Status:** ✅ COMPLETED | Obj=2.63e+07 | RES_SOLAR -1.8K GWh

### Planned Changes:
| Technology | Parameter | Current | Proposed | Classification |
|-----------|----------|---------|----------|---------------|
| PV_ROOFTOP | f_max | 2.0 | 0.05 | Historical realism |
| PV_UTILITY | f_max | 1.0 | 0.02 | Historical realism |

---

## Block 5: Coal/Peat Rebalancing (CALIBRATION FORCING) ✅

**Status:** ✅ COMPLETED | Obj=1.62e+07 | COAL +5K GWh

### Planned Changes:
| Technology | Parameter | Current | Proposed | Classification |
|-----------|----------|---------|----------|---------------|
| IND_BOILER_COAL | fmin_perc | 0.10 | 0.15 | Calibration forcing |
| DHN_COGEN_COAL | fmin_perc | 0.15 | 0.20 | Calibration forcing |

---

## Block 6: Electricity Mix (CALIBRATION FORCING) ✅

**Status:** ✅ COMPLETED | Obj=2.12e+07 | WIND -1.4K GWh

### Planned Changes:
| Technology | Parameter | Current | Proposed | Classification |
|-----------|----------|---------|----------|---------------|
| CCGT | f_max | 1.5 | 1.2 | Calibration forcing |
| WIND_ONSHORE | f_max / f_min | 2.0-2.1 | 1.5-1.7 | Historical realism |
| WIND_OFFSHORE | f_max | 0.1 | 0.03 | Historical realism |

---

## Reality Targets (Finland 2017)

| Category | Reality | v5 Model | Target Range |
|----------|---------|----------|-------------|
| Wood (TWh) | 105 | 11 | 60-80 |
| Oil (TWh) | 96 | 206 | 90-100 |
| Nuclear (TWh thermal) | 65 | 127 | 55-65 |
| Coal+Peat (TWh) | 50 | 24 | 35-45 |
| Gas (TWh) | 25 | 28 | 20-25 |
| Hydro (TWh) | 15 | 15.3 | 14-16 |
| Wind (TWh) | 5 | 7.2 | 4-6 |
| CO₂ (MtCO₂) | 42 | 80.9 | 40-50 |
