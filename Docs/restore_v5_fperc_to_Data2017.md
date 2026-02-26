# Restoration of v5_fperc Calibration State into Data/2017

**Date**: 2026-02-26  
**Purpose**: Restore the exact input state that produced `plots/calibration_v5_fperc` and `case_studies/FI/calib_2017_finland_v5_fperc`  
**Method**: Reverse-engineer FI overrides from compiled `.dat` files, diff against `02_REF_REGION`, write minimal override CSVs  
**Verification**: PERFECT MATCH — pipeline merge reproduces all 169 tech and 35 resource values from v5 `.dat`

---

## 1. Files Inspected

| File / Directory | Purpose |
|---|---|
| `plots/calibration_v5_fperc/` | 3 PNGs + 1 Sankey HTML — target outputs |
| `case_studies/FI/calib_2017_finland_v5_fperc/` | Full AMPL run: `.mod`, `.dat`, `outputs/`, `log.txt` |
| `case_studies/FI/calib_2017_finland_v5_fperc/log.txt` | CPLEX 22.1.2 barrier, solve_result_num=100, obj=2.32e16 |
| `case_studies/FI/calib_2017_finland_v5_fperc/reg_technologies.dat` | Ground truth for all 169 FI tech params |
| `case_studies/FI/calib_2017_finland_v5_fperc/reg_resources.dat` | Ground truth for all 35 FI resource params |
| `case_studies/FI/calib_2017_finland_v5_fperc/reg_demands.dat` | Demand values (matched current Demands.csv) |
| `case_studies/FI/calib_2017_finland_v5_fperc/reg_12TD.dat` | Typical days (hash-identical across v5/v6/v7) |
| `Data/2017/02_REF_REGION/Technologies.csv` | 169-tech reference (header=[0], skiprows=[1], index_col=3) |
| `Data/2017/02_REF_REGION/Resources.csv` | 35-resource reference (header=[2], index_col=2) |
| `Data/2017/FI/Misc.json` | 21 misc params — already matched v5 (no change needed) |
| `Data/2017/FI/Demands.csv` | 11 end-use demands — already matched v5 |
| `Data/2017/FI/Storage_power_to_energy.csv` | PHS override (7.353362) — already matched v5 |
| `Data/2017/FI/Weights.csv` | 9 clustering weights — unchanged across all calibration versions |
| `Data/2017/FI/Time_series.csv` | 8760×14 hourly profiles — unchanged (reg_12TD.dat hash identical v5↔v6↔v7) |

---

## 2. Files Modified

### `Data/2017/FI/Technologies.csv`

**Previous state**: 937940b git commit state (from failed Feb14 reproduction attempt)  
- 59 lines, 4 columns (f_min, f_max, fmin_perc, fmax_perc)  
- NUCLEAR: 2.5–2.8 | HYDRO_RIVER: 1.9–2.1 | COAL_US: 3.5–4.5  
- DHN_COGEN_GAS fmax_perc=0.2 | DHN_BOILER_OIL fmax_perc=0.1

**Restored state**: v5_fperc (47 overrides, 4 columns)  
- NUCLEAR: **2.7**–2.8 | WIND_OFFSHORE: 0.0–**0.1** (was 0.0)
- DHN_COGEN_GAS: fmin_perc=**0.05**, fmax_perc=**1.0** (was 0, 0.2)
- DHN_COGEN_COAL: fmin_perc=**0.15** (was 0.3)
- DHN_COGEN_WOOD: fmin_perc=**0.0** (was 0.3)
- IND_BOILER_WOOD: fmin_perc=**0.0** (was 0.4)
- IND_BOILER_GAS: fmax_perc=**1.0** (was 0.2)
- IND_BOILER_OIL: f_min=**0.2**, f_max=**1.0** (was 0.0, 1.0)
- IND_COGEN_WOOD: f_min=**1.0** (new entry)
- DEC_DIRECT_ELEC: fmin_perc=**0.2** (new entry)
- DHN_BOILER_OIL: fmax_perc=**1.0** (was 0.1)
- CAR_PHEV: fmax_perc=**1.0** (was 0.01)
- CAR_HEV: fmax_perc=**1.0** (was 0.05)
- HVAC_LINE: f_max=**3.5** (new entry)
- HVDC_SUBSEA: f_max=**1.5** (new entry)
- Removed entries not in v5: ELECTRICITY, COAL, GAS (no capacity bounds needed)
- Removed entries not in v5: BUS_COACH_DIESEL, CARGO_*, BOAT_FREIGHT_*, BATT_LI, TS_DEC_TH, TS_DHN_TH

### `Data/2017/FI/Resources.csv`

**Previous state**: 937940b state  
- 14 override lines + exotic formatting  
- GAS c_op_local=0.0195 (correct; 937940b had 0.20 but that was from an even earlier state)  
- Fossil imports: all at 1e15 (unlimited)  
- BIOMASS_RESIDUES avail_local=352.67 (very low)

**Restored state**: v5_fperc (25 overrides)  
- WOOD: 110805.66 GWh @ 0.022084 M€/GWh  
- BIOMASS_RESIDUES: **4985.24** GWh @ 0.013135 (was 352.67)  
- BIOWASTE: **4720.94** GWh @ **0.000112** (was 2497.39 @ 0.000201)  
- WET_BIOMASS: **1450.62** GWh @ **0.033104** (was 1680.30 @ 0.023724)  
- ENERGY_CROPS_2: **7754.11** GWh @ **0.023524** (was 2832.45 @ 0.018467)  
- GAS: avail_exterior=**28000** (was 1e15)  
- COAL: avail_exterior=**50000**, c_op=**0.015** (was 0, 0.0103)  
- LFO: avail_exterior=**150000**, c_op=**0.05** (was 1e15, 0.0521)  
- GASOLINE: avail_exterior=**15000**, c_op=**0.06** (was 1e15, 0.0588)  
- DIESEL: avail_exterior=**25000**, c_op=**0.05** (was 1e15, 0.0543)  
- JET_FUEL: avail_exterior=**15000**, c_op=**0.05** (was 1e15, 0.0359)  
- URANIUM: avail_exterior=**100000**, c_op=**0.005** (was 1e15, 0.0093)  
- ELECTRICITY: avail_exterior=**25000**, c_op=**0.05** (was 0, 0.0332)  
- All RE fuels (GASOLINE_RE, DIESEL_RE, LFO_RE, JET_FUEL_RE, GAS_RE): avail_exterior=**0** (was 1e15)  
- H2, H2_RE, AMMONIA, AMMONIA_RE, METHANOL, METHANOL_RE: avail_exterior=**0** (was 1e15)  
- WASTE: **11095.02** GWh @ **0.006079** (unchanged)

---

## 3. Files NOT Modified (already correct)

| File | Reason |
|---|---|
| `Demands.csv` | All 11 end-use demands identical to v5 (verified by script) |
| `Misc.json` | All 21 parameters identical to v5 |
| `Storage_power_to_energy.csv` | PHS override matches v5 |
| `Weights.csv` | Unchanged across all calibration versions |
| `Time_series.csv` | reg_12TD.dat hash identical (SHA256 3D94CC4A…) across v5/v6/v7 |

---

## 4. Backups Created

| Backup File | Contents |
|---|---|
| `Technologies_v11_backup.csv` | v11+ calibration state (from previous session) |
| `Resources_v11_backup.csv` | v11+ calibration state |
| `Technologies_937940b_backup_20260226.csv` | 937940b state (pre-restoration snapshot) |
| `Resources_937940b_backup_20260226.csv` | 937940b state (pre-restoration snapshot) |

---

## 5. Key Differences: v5_fperc vs 937940b

### Input Philosophy
- **937940b**: Unlimited fossil imports (1e15), minimal share constraints, work-in-progress
- **v5_fperc**: Finite fossil caps (28–150k GWh), transport & heat share constraints, RE fuels disabled

### Critical Capacity Bounds
| Technology | 937940b | v5_fperc | Note |
|---|---|---|---|
| NUCLEAR f_min | 2.5 | 2.7 | Tighter lower bound |
| WIND_OFFSHORE f_max | 0.0 | 0.1 | Allows small offshore |
| DHN_COGEN_GAS fmin_perc | 0.0 | 0.05 | Forces min gas CHP |
| DEC_DIRECT_ELEC fmin_perc | — | 0.20 | Forces min direct elec heating |
| IND_COGEN_WOOD f_min | — | 1.0 | Forces min wood CHP |

### Resource Availability
| Resource | 937940b exterior | v5_fperc exterior | Note |
|---|---|---|---|
| GAS | 1e15 | 28,000 | Finite cap |
| COAL | 0 → 1e15 | 50,000 | Finite cap |
| LFO | 1e15 | 150,000 | Finite but very high |
| GASOLINE_RE | 1e15 | 0 | RE fuels disabled |
| DIESEL_RE | 1e15 | 0 | RE fuels disabled |

---

## 6. v5_fperc Original Run Characteristics

- **Solver**: CPLEX 22.1.2, barrier method
- **Problem size**: 380,824 variables, 608,740 constraints
- **Solve time**: 253s barrier + 31s AMPL elapsed
- **Result**: solve_result_num = 100 (feasible)
- **Objective**: 2.32×10¹⁶ M€/y (numerical issues — some unconstrained techs at 10¹² GW)
- **f_perc**: True (market share constraints active)
- **nbr_td**: 12

### Known Issues in v5 Output
- Unreasonable capacities for unconstrained technologies (CCGT_AMMONIA at 2.7×10¹² GW)
- LFO consumption near cap (149,139 / 150,000 GWh) — over-reliance on oil
- Very low biomass utilization (WOOD: 3,024 / 110,806 GWh)
- Objective value astronomically high due to numerical artifacts

---

## 7. Verification Scripts

| Script | Purpose | Result |
|---|---|---|
| `scripts/generate_v5_csvs.py` | Extract v5 overrides from .dat, diff vs REF, write CSVs | 47 tech + 25 res overrides |
| `scripts/verify_v5_restoration.py` | Pipeline-merge simulation vs .dat ground truth | **PERFECT MATCH** |
| `scripts/compare_v5_demands.py` | Compare demands and storage_power_to_energy | All match |
| `scripts/extract_v5_inputs.py` | Earlier extraction (superseded by generate_v5_csvs.py) | Reference only |

---

## 8. Unresolved Ambiguities

1. **LFO cap at 150,000 GWh**: Extremely high for Finland 2017 calibration. The optimizer saturates this cap, suggesting LFO may be too cheap relative to alternatives. Consider reducing for future runs.

2. **Objective value 2.32×10¹⁶**: The original v5 run had severe numerical issues with unconstrained technologies. A rerun might benefit from tighter upper bounds on exotic technologies (CCGT_AMMONIA, synthetic fuel chains, etc.).

3. **RE fuels completely disabled**: All renewable fuel imports set to 0. This is appropriate for 2017 calibration but would need to change for forward-looking scenarios.

4. **COAL avail_exterior = 50,000 but COAL_US f_max = 4.5 GW**: At 0.868 capacity factor, max annual COAL_US output ≈ 34,200 GWh — well within the 50,000 GWh cap. The binding constraint is the f_max, not the resource.

---

## 9. Rerun Procedure

```python
python scripts/run_v5_fperc_repro.py
```

Config: `f_perc=True, nbr_td=12, year=2017, regions_names=['FI']`  
Case study name: `calib_2017_finland_v5_fperc_repro`  
Expected: Feasible solution (solve_result_num ∈ {0, 100}), ~253s solve time

---

## 10. Restoration Checklist

- [x] Inspected `plots/calibration_v5_fperc` (4 files)
- [x] Inspected `case_studies/FI/calib_2017_finland_v5_fperc` (full output)
- [x] Parsed v5 `.dat` files (47 tech + 25 resource overrides)
- [x] Verified Demands.csv matches v5
- [x] Verified Storage_power_to_energy.csv matches v5
- [x] Verified Misc.json matches v5
- [x] Verified Time_series.csv / Weights.csv stable (hash check)
- [x] Backed up 937940b state (with date stamp)
- [x] Wrote Technologies.csv (47 v5 overrides)
- [x] Wrote Resources.csv (25 v5 overrides)
- [x] Verified via pipeline-merge simulation: **PERFECT MATCH**
- [x] Created diff log (`Docs/restore_v5_fperc_to_Data2017.md`)
- [x] Created rerun script (`scripts/run_v5_fperc_repro.py`)
