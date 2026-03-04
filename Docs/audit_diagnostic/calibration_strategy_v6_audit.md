# Calibration Strategy v6 — Comprehensive Audit Report

**Date:** 2026-02-26  
**Audited Document:** `Docs/calibration_strategy_v6.md`  
**Data Files Audited:**
- `Data/2017/FI/Technologies.csv` (current FI overrides)
- `Data/2017/FI/Resources.csv` (current FI resource overrides)
- `Data/2017/02_REF_REGION/Technologies.csv` (REF defaults)
- `Data/2017/00_INDEP/Layers_in_out.csv` (technology efficiencies)
- `Data/2017/FI/Resources_v11_backup.csv` (historical reference)
- `Data/2017/FI/Technologies_v11_backup.csv` (historical reference)

---

## EXECUTIVE SUMMARY

The strategy document contains **significant data staleness**: it was written against a prior data baseline (matching `Resources_v11_backup.csv` and `Technologies_v11_backup.csv`), but the current FI files have been substantially modified since. Key impacts:

1. **All 5 "current" resource values in the strategy are WRONG** — current FI Resources.csv has `avail_exterior = 1e15` for all fossil fuels, not the specific caps the strategy references.
2. **6 technology "current" values are incorrect** vs actual FI Technologies.csv.
3. **2 technologies listed as "MODIFY" don't exist** in current FI overrides (should be "ADD").
4. **10 technologies listed as "ADD" already exist** in FI overrides (should be "MODIFY").
5. **1 phantom technology** (DHN_BOILER_COAL) in FI overrides doesn't exist in REF_REGION or Layers_in_out.
6. **2 counterproductive fmin_perc proposals** would REDUCE wood/coal forcing below current FI values.
7. **1 proposal would inadvertently RE-ENABLE a disabled technology** (WIND_OFFSHORE).
8. **8 storage technologies** mentioned in Priority 0 are omitted from implementation tables (Section 7).
9. **0 infeasibility issues** (no proposed f_max < f_min).
10. **0 missing technologies** in REF_REGION (all strategy technologies exist, except the phantom DHN_BOILER_COAL).

---

## CRITICAL FINDING: DATA BASELINE DRIFT

The strategy states "Baseline: v5_fperc restored inputs in `Data/2017/FI/`" but the values it references as "Current" match `Resources_v11_backup.csv`, not the actual current files.

| Resource | Strategy "Current" | Actual Current FI | v11_backup | Match? |
|----------|-------------------|-------------------|------------|--------|
| LFO avail_exterior | 150,000 | **1,000,000,000,000,000** | 150,000 | Strategy = v11 backup |
| JET_FUEL avail_exterior | 15,000 | **1,000,000,000,000,000** | 15,000 | Strategy = v11 backup |
| URANIUM avail_exterior | 100,000 | **1,000,000,000,000,000** | 100,000 | Strategy = v11 backup |
| GAS avail_exterior | 28,000 | **1,000,000,000,000,000** | 28,000 | Strategy = v11 backup |
| COAL avail_exterior | 50,000 | **1,000,000,000,000,000** | 50,000 | Strategy = v11 backup |
| GASOLINE avail_exterior | 15,000 | **1,000,000,000,000,000** | 15,000 | Strategy = v11 backup |
| DIESEL avail_exterior | 25,000 | **1,000,000,000,000,000** | 25,000 | Strategy = v11 backup |
| WOOD avail_local | 110,806 | **136,263.89** | 110,805.66 | Strategy = v11 backup |
| WOOD c_op_local | 0.022 | **0.0276** | 0.022084 | Strategy = v11 backup |

**Implication:** With all fossil fuel caps at 1e15, the proposed changes from the strategy represent MUCH larger reductions than the strategy calculates. The delta is not "150,000 → 80,000" for LFO but rather "1e15 → 80,000".

---

## SECTION A: TECHNOLOGY-BY-TECHNOLOGY AUDIT

### A.1 Priority 0 — Technologies to Disable (f_max = 0)

| # | Technology | Strategy Block | Proposed Action | Current FI Override | Current REF Value | Delta Needed | Classification |
|---|-----------|---------------|-----------------|--------------------|--------------------|--------------|----------------|
| 1 | CCGT_AMMONIA | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | numerical stabilization |
| 2 | COAL_IGCC | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 3 | BIOMASS_TO_POWER | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 4 | DEC_ADVCOGEN_GAS | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 5 | DEC_ADVCOGEN_H2 | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 6 | DEC_THHP_GAS | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15, fmax_perc=0 | **REF already has fmax_perc=0** — possibly already effectively disabled. Adding f_max=0 is redundant but harmless | historical realism |
| 7 | BUS_COACH_FC_HYBRIDH2 | 0 | Set f_max=0 (already 0) | **f_max=0 in FI** | f_min=0, f_max=1e15 | **No change needed** — already disabled | historical realism |
| 8 | CAR_FUEL_CELL | 0 | Set f_max=0 (already 0) | **f_max=0 in FI** | f_min=0, f_max=1e15 | **No change needed** — already disabled | historical realism |
| 9 | CAR_METHANOL | 0 | Set f_max=0 (already 0) | **f_max=0 in FI** | f_min=0, f_max=1e15 | **No change needed** — already disabled | historical realism |
| 10 | TRUCK_ELEC | 0 | Set f_max=0 (already 0) | **f_max=0 in FI** | f_min=0, f_max=1e15 | **No change needed** — already disabled | historical realism |
| 11 | TRUCK_FUEL_CELL | 0 | Set f_max=0 (already 0) | **f_max=0 in FI** | f_min=0, f_max=1e15 | **No change needed** — already disabled | historical realism |
| 12 | BUS_COACH_HYDIESEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 13 | BUS_COACH_CNG_STOICH | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 14 | PLANE_H2_SHORT_HAUL | 0 | Set f_max=0 (if present) | No FI override | **f_max=0 already in REF** | **No change needed** — already disabled in REF | historical realism |
| 15 | BOAT_FREIGHT_NG | 0 | Set f_max=0 | **FI has f_max=100000, fmax_perc=0.05** | f_min=0, f_max=1e15 | **⚠️ MISCLASSIFIED as ADD** — must MODIFY existing FI override to f_max=0 | historical realism |
| 16 | BOAT_FREIGHT_METHANOL | 0 | Set f_max=0 | **FI has f_max=0** | f_min=0, f_max=1e15 | **No change needed** — already disabled in FI | historical realism |
| 17 | CARGO_LNG | 0 | Set f_max=0 | **FI has f_max=100000, fmax_perc=0.05** | f_min=0, f_max=1e15 | **⚠️ MISCLASSIFIED as ADD** — must MODIFY existing FI override to f_max=0 | historical realism |
| 18 | CARGO_METHANOL | 0 | Set f_max=0 | **FI has f_max=0** | f_min=0, f_max=1e15 | **No change needed** — already disabled | historical realism |
| 19 | CARGO_AMMONIA | 0 | Set f_max=0 | **FI has f_max=0** | f_min=0, f_max=1e15 | **No change needed** — already disabled | historical realism |
| 20 | CARGO_FUELCELL_LH2 | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 21 | CARGO_FUELCELL_AMMONIA | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 22 | CARGO_RETRO_METHANOL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 23 | CARGO_RETRO_AMMONIA | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 24 | H2_ELECTROLYSIS | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 25 | H2_NG | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 26 | H2_BIOMASS | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 27 | H2_RETROFITTED | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | numerical stabilization |
| 28 | H2_NEW | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | numerical stabilization |
| 29 | H2_SUBSEA_RETRO | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | numerical stabilization |
| 30 | H2_SUBSEA_NEW | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | numerical stabilization |
| 31 | BIOMASS_TO_METHANE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 32 | BIOWASTE_TO_METHANE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 33 | SYN_METHANATION | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 34 | BIOMETHANATION_WET_BIOMASS | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 35 | BIOMETHANATION_BIOWASTE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 36 | BIOMASS_TO_GASOLINE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 37 | BIOMASS_TO_DIESEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 38 | BIOMASS_TO_JET_FUEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 39 | BIOMASS_TO_LFO | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 40 | BIOWASTE_TO_GASOLINE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 41 | BIOWASTE_TO_DIESEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 42 | BIOWASTE_TO_JET_FUEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 43 | BIOWASTE_TO_LFO | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 44 | DIESEL_TO_JET_FUEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 45 | ATM_CCS | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 46 | INDUSTRY_CCS | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 47 | CO2_STORAGE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 48 | SYN_METHANOLATION | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 49 | METHANE_TO_METHANOL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 50 | BIOMASS_TO_METHANOL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 51 | BIOWASTE_TO_METHANOL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 52 | HABER_BOSCH | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 53 | POWER_TO_GASOLINE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 54 | POWER_TO_DIESEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 55 | POWER_TO_JET_FUEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 56 | POWER_TO_LFO | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 57 | H2_TO_GASOLINE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 58 | H2_TO_DIESEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 59 | H2_TO_JET_FUEL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 60 | H2_TO_LFO | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 61 | AMMONIA_TO_H2 | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 62 | GAS_TO_HVC | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 63 | BIOMASS_TO_HVC | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 64 | METHANOL_TO_HVC | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 65 | TRUCK_METHANOL | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 66 | TRUCK_NG | 0 | Set f_max=0 | **FI has f_max=100000, fmax_perc=0.05** | f_min=0, f_max=1e15 | **⚠️ MISCLASSIFIED** — must MODIFY existing FI override | historical realism |
| 67 | CAR_NG | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | historical realism |
| 68 | GAS_PIPELINE | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | numerical stabilization |
| 69 | GAS_SUBSEA | 0 | Set f_max=0 | No FI override | f_min=0, f_max=1e15 | Add FI override f_max=0 | numerical stabilization |

**Summary P0-Disable:** 69 technologies. 7 already disabled (no change needed). 3 misclassified (exist in FI but listed as ADD). 59 genuinely need new FI overrides.

---

### A.2 Priority 0 — Technologies to Cap (realistic f_max)

| # | Technology | Proposed f_max | Current FI Override | Current REF Value | Delta Needed | Classification |
|---|-----------|---------------|--------------------|--------------------|--------------|----------------|
| 70 | DHN_HP_ELEC | 0.5 | No FI override | f_max=1e15 | Add FI override f_max=0.5 | historical realism |
| 71 | DHN_BOILER_GAS | 2.0 | No FI override | f_max=1e15 | Add FI override f_max=2.0 | historical realism |
| 72 | DHN_BOILER_WOOD | 5.0 | No FI override | f_max=1e15 | Add FI override f_max=5.0 | historical realism |
| 73 | DHN_COGEN_WASTE | 1.0 | No FI override | f_max=1e15 | Add FI override f_max=1.0 | historical realism |
| 74 | DEC_HP_ELEC | 5.0 | No FI override | f_max=1e15 | Add FI override f_max=5.0 | historical realism |
| 75 | DEC_COGEN_GAS | 0.5 | No FI override | f_max=1e15 | Add FI override f_max=0.5 | historical realism |
| 76 | DEC_COGEN_OIL | 0.5 | No FI override | f_max=1e15 | Add FI override f_max=0.5 | historical realism |
| 77 | DEC_BOILER_GAS | 5.0 | No FI override | f_max=1e15 | Add FI override f_max=5.0 | historical realism |
| 78 | DEC_BOILER_WOOD | 10.0 | No FI override | f_max=1e15 | Add FI override f_max=10.0 | historical realism |
| 79 | DEC_BOILER_OIL | 8.0 | No FI override | f_max=1e15 | Add FI override f_max=8.0 | historical realism |
| 80 | DEC_ELEC_COLD | 5.0 | No FI override | f_max=1e15 | Add FI override f_max=5.0 | historical realism |
| 81 | IND_COGEN_GAS | 2.0 | No FI override | f_max=1e15 | Add FI override f_max=2.0 | historical realism |
| 82 | IND_COGEN_WASTE | 1.0 | No FI override | f_max=1e15 | Add FI override f_max=1.0 | historical realism |
| 83 | IND_COGEN_COAL | 2.0 | No FI override | f_max=1e15 | Add FI override f_max=2.0 | historical realism |
| 84 | IND_BOILER_BIOWASTE | 1.0 | No FI override | f_max=1e15 | Add FI override f_max=1.0 | historical realism |
| 85 | IND_BOILER_WASTE | 1.0 | No FI override | f_max=1e15 | Add FI override f_max=1.0 | historical realism |
| 86 | IND_DIRECT_ELEC | 5.0 | No FI override | f_max=1e15 | Add FI override f_max=5.0 | historical realism |
| 87 | BUS_COACH_DIESEL | 100000 | **FI has f_min=0, f_max=100000** | f_max=1e15 | **⚠️ MISCLASSIFIED** — already exists in FI with this value. No change to f_max needed. Strategy Section 7 proposes fmin_perc=0.5 vs current FI fmin_perc=0.9 — this **REDUCES** bus-diesel forcing | calibration forcing |
| 88 | TRAMWAY_TROLLEY | 100000 | No FI override | f_max=1e15, fmax_perc=0.3 | Add FI override f_max=100000. **Note:** Strategy Section 7 proposes fmax_perc=0.5 which is MORE permissive than REF default of 0.3 | historical realism |
| 89 | TRAIN_PUB | 100000 | No FI override | f_max=1e15, fmax_perc=0.5 | Add FI override f_max=100000 | numerical stabilization |
| 90 | PLANE_SHORT_HAUL | 100000 | No FI override | f_max=1e15 | Add FI override f_max=100000 | numerical stabilization |
| 91 | TRAIN_FREIGHT | 100000 | No FI override | f_max=1e15 | Add FI override f_max=100000 | numerical stabilization |
| 92 | BOAT_FREIGHT_DIESEL | 100000 | **FI has f_min=0, f_max=100000, fmin_perc=0.95** | f_max=1e15 | **⚠️ MISCLASSIFIED** — already exists. Strategy Section 7 proposes fmin_perc=0.9 vs current 0.95 — **REDUCES** forcing | calibration forcing |
| 93 | CARGO_LFO | 100000 | **FI has f_min=15, f_max=100000, fmin_perc=0.95** | f_max=1e15 | **⚠️ MISCLASSIFIED** — already exists. Strategy Section 7 proposes fmin_perc=0.9 vs current 0.95 — **REDUCES** forcing | calibration forcing |
| 94 | BATT_LI | 1.0 | **FI has f_min=0, f_max=100000** | f_max=1e15 | **⚠️ MISCLASSIFIED** — must MODIFY existing FI f_max from 100000 → 1.0 | historical realism |
| 95 | CAES | 0.0 | No FI override | f_max=1e15 | Add FI override f_max=0 | historical realism |
| 96 | GAS_STORAGE | 100 | No FI override | f_max=1e15 | **⚠️ NOT IN SECTION 7 TABLES** — Add FI override f_max=100 | numerical stabilization |
| 97 | H2_STORAGE | 0.0 | No FI override | f_max=1e15 | **⚠️ NOT IN SECTION 7 TABLES** — Add FI override f_max=0 | historical realism |
| 98 | DIESEL_STORAGE | 100 | No FI override | f_max=1e15 | **⚠️ NOT IN SECTION 7 TABLES** — Add FI override f_max=100 | numerical stabilization |
| 99 | JET_FUEL_STORAGE | 100 | No FI override | f_max=1e15 | **⚠️ NOT IN SECTION 7 TABLES** — Add FI override f_max=100 | numerical stabilization |
| 100 | GASOLINE_STORAGE | 100 | No FI override | f_max=1e15 | **⚠️ NOT IN SECTION 7 TABLES** — Add FI override f_max=100 | numerical stabilization |
| 101 | LFO_STORAGE | 100 | No FI override | f_max=1e15 | **⚠️ NOT IN SECTION 7 TABLES** — Add FI override f_max=100 | numerical stabilization |
| 102 | AMMONIA_STORAGE | 0.0 | No FI override | f_max=1e15 | **⚠️ NOT IN SECTION 7 TABLES** — Add FI override f_max=0 | historical realism |
| 103 | METHANOL_STORAGE | 0.0 | No FI override | f_max=1e15 | **⚠️ NOT IN SECTION 7 TABLES** — Add FI override f_max=0 | historical realism |

**Summary P0-Cap:** 34 technologies. 6 misclassified (exist in FI but listed as ADD). 8 omitted from Section 7 implementation tables. 20 genuinely need new FI overrides.

---

### A.3 Priority 0 — Technologies in Section 7 ADD table but not in narrative

These additional technologies appear in the Section 7 "Quick Reference" ADD table:

| # | Technology | Proposed | Current FI Override | Current REF Value | Delta Needed | Classification |
|---|-----------|----------|--------------------|--------------------|--------------|----------------|
| 104 | IND_ELEC_COLD | f_max=5 | No FI override | f_max=1e15 | Add FI override f_max=5 | historical realism |
| 105 | OIL_TO_HVC | f_max=100000, fmin_perc=0.9 | No FI override | f_max=1e15 | Add FI override | calibration forcing |

---

### A.4 Priority 1 — OIL Resource Changes

| # | Resource | Strategy "Current" | **Actual Current FI** | Proposed | Actual Delta | Classification |
|---|----------|-------------------|----------------------|----------|-------------|----------------|
| 106 | LFO avail_exterior | 150,000 | **1e15** | 80,000 | 1e15 → 80,000 (not 150k→80k) | calibration forcing |
| 107 | DIESEL avail_exterior | 25,000 | **1e15** | 25,000 | 1e15 → 25,000 (not "keep") | calibration forcing |
| 108 | GASOLINE avail_exterior | 15,000 | **1e15** | 16,000 | 1e15 → 16,000 (not "keep") | calibration forcing |
| 109 | JET_FUEL avail_exterior | 15,000 | **1e15** | 5,000 | 1e15 → 5,000 (not 15k→5k) | calibration forcing |

**⚠️ ALL CURRENT VALUES WRONG.** The strategy underestimates the magnitude of change needed.

---

### A.5 Priority 2 — Force Wood/Biomass (fmin_perc changes)

| # | Technology | Strategy "Current fmin_perc" | **Actual Current FI fmin_perc** | Proposed fmin_perc | Direction | Classification |
|---|-----------|-----------------------------|---------------------------------|-------------------|-----------|----------------|
| 110 | IND_BOILER_WOOD | 0.0 | **0.40** | 0.30 | **⚠️ DECREASE** (contradicts goal of forcing MORE wood) | calibration forcing |
| 111 | IND_COGEN_WOOD | 0.0 | **No FI override** (REF default=0) | 0.15 | Increase ✓ | calibration forcing |
| 112 | DHN_COGEN_WOOD | 0.0 | **0.30** | 0.30 | **No change** (already at proposed level) | calibration forcing |
| 113 | DEC_BOILER_WOOD | 0.0 | **No FI override** (REF default=0) | 0.15 | Increase ✓ — but DEC_BOILER_WOOD not in FI, needs ADD | calibration forcing |

**⚠️ CRITICAL:** IND_BOILER_WOOD fmin_perc would go DOWN from 0.40 → 0.30, which is the OPPOSITE of the strategy's stated goal to increase wood usage.

**⚠️ CRITICAL:** DHN_COGEN_WOOD fmin_perc is ALREADY at 0.30 in FI. The strategy proposes 0.30 as if it's a new change. No delta exists for this parameter.

### Priority 2 — Fossil Resource Tightening

| # | Resource | Strategy "Current" | **Actual Current FI** | Proposed | Actual Delta | Classification |
|---|----------|-------------------|----------------------|----------|-------------|----------------|
| 114 | GAS avail_exterior | 28,000 | **1e15** | 22,000 | 1e15 → 22,000 | calibration forcing |
| 115 | COAL avail_exterior | 50,000 | **1e15** | 35,000 | 1e15 → 35,000 | calibration forcing |

---

### A.6 Priority 3 — Nuclear

| # | Technology/Resource | Strategy "Current" | **Actual Current FI** | Proposed | Actual Delta | Classification |
|---|-------------------|-------------------|----------------------|----------|-------------|----------------|
| 116 | NUCLEAR f_min | 2.7 | **2.5** | 2.76 | 2.5 → 2.76 (not 2.7→2.76) | historical realism |
| 117 | NUCLEAR f_max | 2.8 | **2.8** | 2.80 | No change ✓ | historical realism |
| 118 | URANIUM avail_exterior | 100,000 | **1e15** | 62,000 | 1e15 → 62,000 (not 100k→62k) | calibration forcing |

**⚠️** Strategy says NUCLEAR f_min is currently 2.7 but actual FI has 2.5.

---

### A.7 Priority 4 — Solar

| # | Technology | Strategy "Current" | **Actual Current FI** | Proposed | Actual Delta | Classification |
|---|-----------|-------------------|----------------------|----------|-------------|----------------|
| 119 | PV_ROOFTOP f_max | 2.0 | **2.0** | 0.05 | 2.0 → 0.05 ✓ | historical realism |
| 120 | PV_UTILITY f_max | 1.0 | **1.0** | 0.02 | 1.0 → 0.02 ✓ | historical realism |

These are correct ✓.

---

### A.8 Priority 5 — Coal/Peat

| # | Technology/Resource | Strategy "Current" | **Actual Current FI** | Proposed | Actual Delta | Classification |
|---|-------------------|-------------------|----------------------|----------|-------------|----------------|
| 121 | IND_BOILER_COAL fmin_perc | 0.10 | **0.10** | 0.15 | 0.10 → 0.15 ✓ | calibration forcing |
| 122 | DHN_COGEN_COAL fmin_perc | 0.15 | **0.30** | 0.20 | **⚠️ DECREASE** from 0.30 → 0.20 (contradicts goal) | calibration forcing |
| 123 | COAL avail_exterior | 50,000 | **1e15** | 40,000 | 1e15 → 40,000 | calibration forcing |

**⚠️** DHN_COGEN_COAL fmin_perc would DECREASE from 0.30 to 0.20. Strategy claims current is 0.15; actual is 0.30.  
**Note:** COAL resource already counted under Priority 2 (#115 proposes 35,000); Priority 5 proposes 40,000. Internal inconsistency.

---

### A.9 Priority 6 — Electricity Mix

| # | Technology | Strategy "Current" | **Actual Current FI** | Proposed | Actual Delta | Classification |
|---|-----------|-------------------|----------------------|----------|-------------|----------------|
| 124 | CCGT f_max | 1.5 | **1.5** | 1.2 | 1.5 → 1.2 ✓ | calibration forcing |
| 125 | WIND_ONSHORE f_max | 2.1 | **2.1** | **1.6 (P6) or 1.7 (S7)** | 2.1 → 1.6 or 1.7 — **INTERNAL INCONSISTENCY** | calibration forcing |
| 126 | WIND_ONSHORE f_min | (not in P6) | **2.0** | **1.5 (S7 only)** | 2.0 → 1.5 — Section 7 proposes lowering f_min, not mentioned in Section 6 narrative | calibration forcing |
| 127 | WIND_OFFSHORE f_max | **0.1** | **0.0** | 0.03 | **⚠️ WOULD RE-ENABLE** from 0.0 → 0.03 (strategy thinks current is 0.1) | calibration forcing |

**⚠️ WIND_OFFSHORE:** Strategy believes current f_max=0.1 but actual is 0.0 (already disabled). Proposed f_max=0.03 would ENABLE offshore wind — the opposite of the intention.

**⚠️ WIND_ONSHORE internal inconsistency:** Priority 6 narrative says f_max=1.6, Section 7 table says f_max=1.7.

---

### A.10 Additional Technologies in Section 7 MODIFY table

| # | Technology | Strategy "In FI?" | **Actual FI Status** | Issue |
|---|-----------|------------------|---------------------|-------|
| 128 | IND_COGEN_WOOD | MODIFY (says current 1.0/100000) | **NOT in FI overrides** | Should be ADD, not MODIFY. REF default: f_min=0, f_max=1e15 |
| 129 | DEC_DIRECT_ELEC | MODIFY (says current 0/100000) | **NOT in FI overrides** | Should be ADD, not MODIFY. REF defaults: f_max=1e15, fmax_perc=0.6 |

---

## SECTION B: CROSS-REFERENCE CHECKS

### B.1 Technologies in Strategy NOT in REF_REGION

| Technology | In REF? | In Layers_in_out? | Issue |
|-----------|---------|-------------------|-------|
| All 127+ technologies | ✓ Yes | ✓ Yes | No missing technology errors |

**Result:** All technologies mentioned in the strategy exist in REF_REGION. ✓

### B.2 Phantom Technology in Current FI (Not Referenced by Strategy)

| Technology | In FI? | In REF? | In Layers_in_out? | Issue |
|-----------|--------|---------|-------------------|-------|
| **DHN_BOILER_COAL** | ✓ FI override: f_min=0.5, f_max=100000, fmin_perc=0.1 | **✗ NOT FOUND** | **✗ NOT FOUND** | **PHANTOM** — FI references a technology that doesn't exist in the model. Override is silently ignored or causes error. Strategy doesn't mention this at all. |

### B.3 f_max < f_min Check (Infeasibility)

Checked all proposed f_min/f_max pairs across the strategy:

| Technology | Proposed f_min | Proposed f_max | Feasible? |
|-----------|---------------|---------------|-----------|
| NUCLEAR | 2.76 | 2.80 | ✓ |
| PV_ROOFTOP | 0.02 | 0.05 | ✓ |
| PV_UTILITY | 0.00 | 0.02 | ✓ |
| WIND_ONSHORE | 1.5 | 1.6–1.7 | ✓ |
| WIND_OFFSHORE | 0.0 | 0.03 | ✓ |
| CCGT | 0.6 | 1.2 | ✓ |
| IND_BOILER_WOOD | 5.0 | 15.0 | ✓ |
| IND_COGEN_WOOD | 1.0 | 8.0 | ✓ |
| DHN_COGEN_WOOD | 2.5 | 10.0 | ✓ |
| DHN_COGEN_COAL | 0.5 | 5.0 | ✓ |
| IND_BOILER_COAL | 0.5 | 5.0 | ✓ |
| DEC_DIRECT_ELEC | 0.0 | 5.0 | ✓ |
| All P0-Disable (f_min=0, f_max=0) | 0 | 0 | ✓ |

**Result:** No infeasibility from f_max < f_min in proposed values. ✓

### B.4 Internal Inconsistencies Within Strategy Document

| # | Issue | Section(s) | Details |
|---|-------|-----------|---------|
| 1 | WIND_ONSHORE f_max | P6 vs S7 | P6 says f_max=1.6, S7 says f_max=1.7 |
| 2 | COAL avail_exterior | P2 vs P5 | P2 proposes 35,000; P5 proposes 40,000 |
| 3 | 8 storage techs omitted | P0 vs S7 | P0 lists GAS_STORAGE, H2_STORAGE, DIESEL_STORAGE, JET_FUEL_STORAGE, GASOLINE_STORAGE, LFO_STORAGE, AMMONIA_STORAGE, METHANOL_STORAGE — none appear in S7 tables |
| 4 | IND_COGEN_WOOD in wrong table | S7 | Listed in "MODIFY" but tech doesn't exist in FI overrides — should be in "ADD" |
| 5 | DEC_DIRECT_ELEC in wrong table | S7 | Listed in "MODIFY" but tech doesn't exist in FI overrides — should be in "ADD" |
| 6 | WIND_OFFSHORE f_max | P6 | Claims current is 0.1, actual is 0.0 — proposal would re-enable the tech |
| 7 | NUCLEAR f_min | P3, S7 | Claims current is 2.7, actual is 2.5 |
| 8 | IND_BOILER_WOOD fmin_perc | P2 | Strategy proposes 0.30 to "force wood usage" but current FI already has 0.40 — proposal REDUCES forcing |
| 9 | DHN_COGEN_WOOD fmin_perc | P2 | Strategy proposes 0.30 as new; current FI already has 0.30 — no change |
| 10 | DHN_COGEN_COAL fmin_perc | P5 | Strategy claims current is 0.15, proposes 0.20; actual FI has 0.30 — proposal REDUCES forcing |

---

## SECTION C: RESOURCE AUDIT

### C.1 Complete Resource Comparison

| Resource | Current FI avail_local | Current FI c_op_local | Current FI avail_exterior | Strategy "Current" avail_ext | Strategy Proposed avail_ext | v11_backup avail_ext |
|----------|----------------------|---------------------|-------------------------|-----------------------------|-----------------------------|---------------------|
| WOOD | 136,263.89 | 0.0276 | 0.0 | 110,806 (local) | No change proposed | 110,805.66 (local) |
| WET_BIOMASS | 1,680.30 | 0.0237 | 0.0 | — | — | — |
| ENERGY_CROPS_2 | 2,832.45 | 0.0185 | 0.0 | — | — | — |
| BIOWASTE | 2,497.39 | 0.0002 | 0.0 | — | — | — |
| BIOMASS_RESIDUES | 352.67 | 0.0131 | 0.0 | — | — | — |
| WASTE | 11,095.02 | 0.0061 | 0.0 | — | — | — |
| GASOLINE | 0.0 | 0.0588 | **1e15** | 15,000 | 16,000 | 15,000 |
| DIESEL | 0.0 | 0.0543 | **1e15** | 25,000 | 25,000 | 25,000 |
| LFO | 0.0 | 0.0521 | **1e15** | 150,000 | 80,000 | 150,000 |
| JET_FUEL | 0.0 | 0.0359 | **1e15** | 15,000 | 5,000 | 15,000 |
| GAS | 0.0 | 0.0195 | **1e15** | 28,000 | 22,000 | 28,000 |
| COAL | 0.0 | 0.0103 | **1e15** | 50,000 | 35,000–40,000 | 50,000 |
| URANIUM | 0.0 | 0.0093 | **1e15** | 100,000 | 62,000 | 100,000 |
| ELECTRICITY | 0.0 | 0.0326 | **1e15** | — | — | 25,000 |

### C.2 Resource Discrepancy Impact

Because all current FI fossil avail_exterior values are 1e15 (not the v11 values the strategy references), implementing the strategy as written would impose caps where currently **none exist at all**. This makes every resource change simultaneously:
- A **degeneracy fix** (removing 1e15 values)
- A **calibration forcing** (setting specific caps)

The strategy's gap analysis (Section 2) was computed against the v11 values. The current data would produce DIFFERENT model results than those described in Section 2.

---

## SECTION D: TECHNOLOGIES IN FI NOT MENTIONED IN STRATEGY

These technologies have FI overrides but are not addressed by the strategy:

| Technology | Current FI Values | Notes |
|-----------|-------------------|-------|
| PT_POWER_BLOCK | f_max=0 | Already disabled ✓ |
| ST_POWER_BLOCK | f_max=0 | Already disabled ✓ |
| PT_COLLECTOR | f_max=0 | Already disabled ✓ |
| ST_COLLECTOR | f_max=0 | Already disabled ✓ |
| HYDRO_DAM | f_min=1.1, f_max=1.3 | Correctly bounded ✓ |
| HYDRO_RIVER | f_min=1.9, f_max=2.1 | Correctly bounded ✓ |
| TIDAL_STREAM | f_max=0 | Already disabled ✓ |
| TIDAL_RANGE | f_max=0 | Already disabled ✓ |
| WAVE | f_max=0 | Already disabled ✓ |
| GEOTHERMAL | f_min=0, f_max=0.3 | Bounded ✓ |
| DHN_DEEP_GEO | f_max=0 | Already disabled ✓ |
| DHN_SOLAR | f_max=56.345 | **⚠️ NOT MENTIONED** — 56 GW seems absurdly high for Finland. Should be reviewed. |
| DEC_SOLAR | f_max=56.345 | **⚠️ NOT MENTIONED** — Same issue. |
| DAM_STORAGE | f_min=0.001, f_max=0.001 | Bounded ✓ |
| PHS | f_min=0.001, f_max=0.001 | Bounded ✓ |
| COAL_US | f_min=3.5, f_max=4.5 | **⚠️ NOT DISCUSSED** — Strategy mentions COAL_US in gap analysis but proposes no f_min/f_max changes. 3.5–4.5 GW coal power is high for Finland 2017. |
| DHN_COGEN_GAS | f_min=0.6, f_max=1.5, fmax_perc=0.2 | Specific bounds ✓ |
| DHN_BOILER_OIL | f_min=0.4, f_max=1.0, fmax_perc=0.1 | Specific bounds ✓ |
| IND_BOILER_OIL | f_min=0, f_max=1.0 | Bounded ✓ |
| IND_BOILER_GAS | fmax_perc=0.2 | Capped share ✓ |
| CAR_GASOLINE | fmin_perc=0.55, fmax_perc=0.65 | Not discussed but reasonable ✓ |
| CAR_DIESEL | fmin_perc=0.3, fmax_perc=0.4 | Not discussed but reasonable ✓ |
| CAR_BEV | fmax_perc=0.01 | Not discussed but reasonable ✓ |
| CAR_PHEV | fmax_perc=0.01 | Not discussed but reasonable ✓ |
| CAR_HEV | fmax_perc=0.05 | Not discussed but reasonable ✓ |
| TRUCK_DIESEL | fmin_perc=0.9 | Not discussed ✓ |
| **DHN_BOILER_COAL** | f_min=0.5, f_max=100000, fmin_perc=0.1 | **⚠️ PHANTOM** — Tech doesn't exist in model |
| ELECTRICITY (resource tech) | f_max=100000 | Not discussed |
| COAL (resource tech) | f_max=100000 | Not discussed |
| GAS (resource tech) | f_max=100000 | Not discussed |
| TS_DEC_TH | f_max=100000 | Not discussed |
| TS_DHN_TH | f_max=100000 | Not discussed |

---

## SECTION E: SUMMARY STATISTICS

| Metric | Count |
|--------|-------|
| Total technologies in strategy | ~129 |
| Technologies to disable (f_max=0) | 69 |
| Technologies to cap (realistic f_max) | 34 |
| Technologies to modify (fmin/fmax_perc) | ~14 |
| Resource changes proposed | 7 (LFO, DIESEL, GASOLINE, JET_FUEL, GAS, COAL, URANIUM) |
| Technologies already disabled in FI (no-op) | 7 |
| Technologies already disabled in REF (no-op) | 1 (PLANE_H2_SHORT_HAUL) |
| Misclassified ADD↔MODIFY | 12 |
| Incorrect "current" values in strategy | 10+ |
| Internal inconsistencies in strategy | 10 |
| Counterproductive proposals (reduce forcing) | 3 (IND_BOILER_WOOD, DHN_COGEN_WOOD, DHN_COGEN_COAL) |
| f_max < f_min checks: failures | **0** ✓ |
| Technologies not in REF_REGION | **0** ✓ (except phantom DHN_BOILER_COAL in FI) |
| Technologies inadvertently re-enabled | 1 (WIND_OFFSHORE) |
| Storage techs omitted from Section 7 | 8 |
| Suspicious large caps in current FI (untouched) | 2 (DHN_SOLAR=56.3 GW, DEC_SOLAR=56.3 GW) |

---

## SECTION F: RECOMMENDED CORRECTIONS BEFORE IMPLEMENTATION

1. **Re-baseline the strategy** against current FI data files (all fossil resources at 1e15, updated WOOD values, changed technology bounds).
2. **Fix IND_BOILER_WOOD fmin_perc**: Current FI has 0.40. If goal is more wood, keep ≥0.40 or raise it. Do NOT lower to 0.30.
3. **Fix DHN_COGEN_COAL fmin_perc**: Current FI has 0.30 (not 0.15 as strategy claims). Decide whether to keep 0.30 or change; don't unknowingly reduce.
4. **Fix DHN_COGEN_WOOD fmin_perc**: Already at 0.30 in FI. Acknowledge no change needed or specify different target.
5. **Fix WIND_OFFSHORE**: Current is f_max=0.0 (disabled). If intent is to keep it disabled, don't set f_max=0.03.
6. **Fix NUCLEAR f_min**: Strategy says current is 2.7; actual is 2.5. Update strategy or adjust proposal.
7. **Remove DHN_BOILER_COAL from FI Technologies.csv** — it's a phantom technology not in REF or Layers_in_out.
8. **Move IND_COGEN_WOOD and DEC_DIRECT_ELEC** from Section 7 MODIFY to ADD table.
9. **Add 8 missing storage technologies** to Section 7 implementation tables.
10. **Resolve COAL cap inconsistency**: P2 says 35,000, P5 says 40,000.
11. **Resolve WIND_ONSHORE f_max inconsistency**: P6 says 1.6, S7 says 1.7.
12. **Review DHN_SOLAR and DEC_SOLAR f_max=56.345 GW** — suspiciously high for Finland, not addressed by strategy.
13. **Review COAL_US f_min=3.5 GW** — high for Finland 2017, not addressed by strategy.
