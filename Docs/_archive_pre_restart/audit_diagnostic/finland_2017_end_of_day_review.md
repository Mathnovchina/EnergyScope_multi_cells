# Finland 2017 Calibration - End-of-Day Review

**Date:** 2026-03-02  
**Session Focus:** Testing fmin_perc approach for CHP calibration  
**Document Status:** Audit-only (no new runs executed)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Chronological Reconstruction](#2-chronological-reconstruction)
3. [Data & Script Changes](#3-data--script-changes)
4. [Run Results Summary](#4-run-results-summary)
5. [Confirmed vs Uncertain Findings](#5-confirmed-vs-uncertain-findings)
6. [Patch Inventory](#6-patch-inventory)
7. [Safe Baseline for Next Session](#7-safe-baseline-for-next-session)
8. [Open Questions & Blocking Issues](#8-open-questions--blocking-issues)
9. [Recommended Next Steps](#9-recommended-next-steps)

---

## 1. Executive Summary

### What Was Attempted
Testing the `fmin_perc` approach to force CHP production in the Finland 2017 calibration model.

### What Worked
- **fmin_perc mechanism confirmed functional**: CHP production increased from 5.2 TWh to 50.7 TWh when `f_perc=True` and fmin_perc constraints applied
- **IND_COGEN_COAL validation bug fixed**: Was missing from CHP electricity calculation
- **Global data corruption identified and restored**: `Data/2017/FI/Technologies.csv` had wrong format
- **Patch system operational**: 16 patch files created and applied successfully

### What Did NOT Work
- **Solver stability**: All runs with `f_perc=True` produce "unknown solution status" (solve_result_num=-1)
- **Nuclear/gas power explosion**: Nuclear jumps to 72-81 TWh (vs 21.4 reality) when CHP constrained
- **No clean optimal solution**: 29 runs today, none achieved optimal status with fmin_perc active
- **DEC_ADVCOGEN_GAS takeover**: Takes 37 TWh when enabled, distorting results

### Net Outcome
**Partial success**: Proved fmin_perc works, but solver tolerance issues remain unresolved.

---

## 2. Chronological Reconstruction

| Time | Run | Purpose | Outcome |
|------|-----|---------|---------|
| AM | p01_test | Test basic patch system | Infeasible (wrong f_perc config) |
| AM | p02_with_fmin | Disable oil CHP + geothermal | Cost explosion (7e17) |
| AM | p02b_disabled_only | Disable only | Cost explosion |
| PM | p03_force_chp | Force CHP with f_min | Presolve infeasible |
| PM | p04_chp_fmin_perc | First fmin_perc attempt | Cost explosion, CHP=0 |
| PM | p05-p09 | Solar thermal fix attempts | Various failures |
| PM | p10-p12 | Enable f_perc=True | ATM_CCS presolve infeasibility |
| PM | **p13_clean** | Clean global data + f_perc=True | **CHP=50.7 TWh** ✓ unknown status |
| PM | p14_tuned | Adjust fmin_perc values | Moderate improvement |
| PM | p15_mild | Conservative fmin_perc | CHP undershooting |
| PM | **p16_no_advcogen** | Disable DEC_ADVCOGEN* | **CHP=18.2 TWh** better balance |
| PM | p17_disable_only | f_max=0 only, no fmin_perc | CHP drops back |
| PM | p18_fmin_only | Test fmin_perc isolation | Similar to p16 |
| PM | p19_baseline_test | No patches, f_perc=True | Baseline comparison |

### Key Discovery Timeline

1. **~11:00** - Realized `f_perc: False` was disabling all fmin_perc constraints
2. **~17:00** - Found global `Technologies.csv` was corrupted with wrong format
3. **~17:30** - p13_clean achieved first successful CHP production with fmin_perc
4. **~18:00** - Discovered DEC_ADVCOGEN_GAS explosion problem

---

## 3. Data & Script Changes

### Files Restored from Git
| File | Issue | Action |
|------|-------|--------|
| `Data/2017/FI/Technologies.csv` | Had full columns instead of override-only format | `git checkout HEAD --` |
| `Data/2017/FI/Misc.json` | Formatting changes | `git checkout HEAD --` |

### Scripts Modified
| File | Change | Status |
|------|--------|--------|
| `scripts/generate_finland_validation.py` | Added `IND_COGEN_COAL` to chp_techs list | **Valid fix** |
| `scripts/run_calib_manual.py` | `f_perc` toggled True↔False | Currently: `f_perc: False` |

### New Untracked Files
| Path | Purpose |
|------|---------|
| `calibration/` | New folder with 16 patch CSV files |
| `scripts/run_calib_manual.py` | Manual patch runner script |
| `scripts/generate_finland_validation.py` | Finland-specific validation report generator |
| `scripts/score_calib_runs.py` | Run scoring utility |

### Git Status Summary
```
Modified (tracked):
  M Data/exogenous_data/Finland_MASTER_Calibration_old_UPDATED.xlsx
  M scripts/generate_validation_plots_and_report.py
  M scripts/run_calib_2017.py
  M scripts/run_calib_case.py

Untracked (new):
  ?? calibration/
  ?? scripts/generate_finland_validation.py
  ?? scripts/run_calib_manual.py
```

---

## 4. Run Results Summary

### Key Runs Comparison

| Run Name | f_perc | TotalCost | Solve Status | CHP (TWh) | Nuclear (TWh) | Notes |
|----------|--------|-----------|--------------|-----------|---------------|-------|
| **v9 (baseline)** | False | 47,194 | optimal | 5.2 | 20.8 | Clean reference |
| **v10_oil_constr** | False | 49,676 | optimal | ~5 | ~21 | With oil constraints |
| p02b_disabled_only | False | 7.1e17 | fail | 0 | - | Cost explosion |
| p10_fperc_enabled | True | 0 | infeasible | - | - | ATM_CCS conflict |
| **p13_clean** | True | 14,978,618 | unknown | **50.7** | 72.0 | CHP works! |
| **p16_no_advcogen** | True | 24,196,093 | unknown | **18.2** | 80.7 | Better CHP balance |
| p19_baseline_test | True | 18,393,677 | unknown | - | - | No patches baseline |

### Solver Status Codes
- `0` = Optimal solution
- `-1` = Unknown status (tolerance violations)

---

## 5. Confirmed vs Uncertain Findings

### ✓ CONFIRMED (High Confidence)

1. **fmin_perc mechanism works**
   - Evidence: p13_clean achieved CHP=50.7 TWh vs 5.2 TWh baseline
   - Condition: Requires `f_perc: True` in Esmc config

2. **IND_COGEN_COAL was missing from validation**
   - Evidence: CHP reported as 0 when actually 1.2 TWh
   - Fix: Added to `chp_techs` list in generate_finland_validation.py

3. **Global data format matters**
   - Evidence: Runs failed until Technologies.csv format restored
   - FI/Technologies.csv is **override-only**: columns `f_min,f_max,fmin_perc,fmax_perc`

4. **DEC_ADVCOGEN_GAS explodes when fmin_perc active**
   - Evidence: Takes 37.8 TWh in p13, displaces realistic CHP mix
   - Must be disabled with `f_max=0`

### ⚠ UNCERTAIN (Needs Investigation)

1. **Why all f_perc=True runs have "unknown status"**
   - Symptom: solve_result_num=-1 with algebraic constraint violations
   - Possible causes:
     - fmin_perc constraints create near-infeasible regions
     - CPLEX barrier algorithm sensitivity to constraint structure
     - Tolerance settings incompatible with fmin_perc

2. **Nuclear power explosion with CHP constraints**
   - When CHP forced up, nuclear jumps 3x+ (21→72 TWh)
   - May need nuclear fmax_perc constraint to balance

3. **Solar PV overcounting (859% error in p13)**
   - Model installs 0.9 TWh vs 0.1 reality
   - May need f_max constraint

---

## 6. Patch Inventory

All patches in `calibration/patches/`:

| Patch File | Purpose | Recommended |
|------------|---------|-------------|
| `p01_disable_futuretechs.csv` | Early test | ❌ Superseded |
| `p02_disable_oil_chp.csv` | Disable oil CHP | ⚠ Partial |
| `p03_force_chp.csv` | f_min approach | ❌ Causes infeasibility |
| `p04_chp_fmin_perc.csv` | First fmin_perc | ❌ Missing disables |
| `p05-p08_*.csv` | Solar thermal fix attempts | ❌ Debugging |
| `p12_with_atm_ccs_fix.csv` | ATM_CCS workaround | ⚠ Limited |
| **`p13_clean.csv`** | Comprehensive v1 | ⚠ High CHP |
| `p14_tuned.csv` | Moderate fmin_perc | ⚠ Nuclear issue |
| `p15_mild.csv` | Conservative | ⚠ Low CHP |
| **`p16_no_advcogen.csv`** | Best balance | **✓ Current best** |
| `p17_disable_only.csv` | No fmin_perc | ❌ CHP drops |

### Recommended Patch: p16_no_advcogen.csv

```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_max,DEC_COGEN_OIL,0
Technologies.csv,f_max,WIND_OFFSHORE,0
Technologies.csv,f_max,GEOTHERMAL,0
Technologies.csv,f_max,DHN_DEEP_GEO,0
Technologies.csv,f_max,PT_POWER_BLOCK,0
Technologies.csv,f_max,ST_POWER_BLOCK,0
Technologies.csv,f_max,DEC_ADVCOGEN_GAS,0
Technologies.csv,f_max,DEC_ADVCOGEN_H2,0
Technologies.csv,fmin_perc,DHN_COGEN_WOOD,0.10
Technologies.csv,fmin_perc,DHN_COGEN_COAL,0.10
Technologies.csv,fmin_perc,IND_COGEN_WOOD,0.10
Technologies.csv,fmin_perc,IND_COGEN_COAL,0.05
```

---

## 7. Safe Baseline for Next Session

### Known Good Configuration

**Use `calib_2017_finland_v9` as reference baseline:**
- TotalCost: 47,194
- Solve status: optimal (0)
- No solver tolerance issues
- CHP: 5.2 TWh (low but stable)

### To Resume Calibration

1. Start from clean git state:
   ```powershell
   git status Data/
   # Ensure Technologies.csv shows no modifications
   ```

2. Configuration to use:
   ```yaml
   f_perc: True  # Required for fmin_perc to work
   ```

3. Start with `p16_no_advcogen.csv` patch

4. Address solver tolerance before proceeding

---

## 8. Open Questions & Blocking Issues

### BLOCKING: Solver "Unknown Status"

**Symptom:** All f_perc=True runs return solve_result_num=-1

**Impact:** Cannot trust fmin_perc results at production quality

**Diagnostic needed:**
- Extract CPLEX log from a f_perc=True run
- Check `_interm` folder for solver logs
- Review tolerance settings in AMPL options

### Open Questions

| # | Question | Priority |
|---|----------|----------|
| 1 | Why does enabling fmin_perc cause solver tolerance violations? | **High** |
| 2 | Is nuclear explosion a constraint feedback effect or data issue? | High |
| 3 | Should we use fmax_perc for nuclear instead of fmin_perc for CHP? | Medium |
| 4 | Are there CPLEX options to improve barrier algorithm stability? | Medium |
| 5 | Can we validate fmin_perc against known-good AMPL examples? | Low |

---

## 9. Recommended Next Steps

### Immediate (Next Session Start)

1. **Extract CPLEX solver log** from p13_clean or p16 run
   - Look for constraint violations, dual infeasibility
   - Check barrier crossover status

2. **Test solver tolerance options**
   - `option cplex_options 'barconvtol=1e-4';`
   - `option cplex_options 'feasibilityrelax=1';`

3. **Validate fmin_perc in isolation**
   - Create minimal test case with single fmin_perc constraint
   - Verify solver behavior without full model complexity

### Medium Term

4. **Constrain nuclear** instead of forcing CHP
   - Add `Technologies.csv,fmax_perc,NUCLEAR,0.25` to limit nuclear share
   - Let model find CHP/gas balance organically

5. **Review f_perc constraint structure** in AMPL model
   - File: `esmc/energy_model/es_model.mod`
   - Search for `fmin_perc` implementation

### Documentation

6. **Commit validated changes**:
   ```powershell
   git add scripts/generate_finland_validation.py
   git add calibration/patches/p16_no_advcogen.csv
   git commit -m "Add validation script and p16 patch"
   ```

---

## Appendix: Validation Snapshots

### p13_clean (CHP=50.7 TWh)
| Metric | Model | Reality | Error |
|--------|-------|---------|-------|
| Nuclear | 72.0 | 21.4 | +236% ✗ |
| CHP | 49.0 | 25.0 | +96% ✗ |
| CO2 | 34.7 | 41.2 | -16% ✓ |

### p16_no_advcogen (CHP=18.2 TWh)
| Metric | Model | Reality | Error |
|--------|-------|---------|-------|
| Nuclear | 80.7 | 21.4 | +277% ✗ |
| CHP | 18.2 | 25.0 | -27% ⚠ |
| CO2 | 29.0 | 41.2 | -30% ⚠ |

### v9 baseline (CHP=5.2 TWh)
| Metric | Model | Reality | Error |
|--------|-------|---------|-------|
| Nuclear | 20.8 | 21.4 | -2.7% ✓ |
| CHP | 5.2 | 25.0 | -79% ✗ |
| CO2 | 16.8 | 41.2 | -59% ✗ |

---

*End of review document*
