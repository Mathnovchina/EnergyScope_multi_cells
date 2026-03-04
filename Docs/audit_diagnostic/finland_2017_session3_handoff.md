# Finland 2017 Calibration - Session 3 Handoff

**Date:** 2026-03-03  
**Status:** BLOCKED - Need to debug solver divergence

---

## Critical Finding: Data Regeneration Problem

### The Issue
When `run_calib_manual.py` clones a baseline and runs the model, **the .dat files are regenerated from CSVs**, not reused from the cloned run. This causes the model to solve differently even with identical settings.

**Evidence:**
| Run | CPLEX Status | Objective | Notes |
|-----|--------------|-----------|-------|
| v10_oil_constr (original) | **optimal** | 49,677 | Created Feb 17 |
| p22_nochange_test (clone, no patches) | unknown | 24.9M | Created Mar 3 |
| p23_defaults_test (clone, default opts) | unknown | 24.9M | Created Mar 3 |

The cloned runs fail even though:
1. No patches were applied (p22)
2. Same CPLEX options as original (p23)
3. Same `f_perc: False` setting

### Root Cause Hypothesis
The `run_calib_manual.py` script calls:
```python
my_model.read_data_indep()
my_model.init_regions()
my_model.init_ta(algo='kmedoid')  # This might vary!
my_model.print_td_data()
my_model.print_data(indep=True)   # Regenerates all .dat files
```

**The regenerated .dat files differ from the original** because:
1. Typical days clustering may produce different results (stochastic?)
2. Or the underlying CSV data in `Data/2017/` has changed since v10 was created

### What Needs to Be Done Next Session

1. **Compare .dat files directly**:
   ```powershell
   # Check if reg_technologies.dat differs
   fc.exe "case_studies/FI/calib_2017_finland_v10_oil_constr/reg_technologies.dat" `
          "case_studies/FI/calib_2017_finland_p23_defaults_test/reg_technologies.dat"
   ```

2. **Add `--skip-regeneration` flag** to `run_calib_manual.py`:
   - Clone the run directory
   - Apply patches ONLY to the existing .dat files (or to CSVs, then regenerate)
   - Do NOT re-run kmedoid clustering
   - Reuse the cloned .dat files directly

3. **Or use a simpler approach**:
   - Directly run AMPL on the cloned .dat files
   - Apply patches by editing the .dat files post-hoc

---

## Current State of run_calib_manual.py

**Line 305:** `f_perc: False` (was changed during debugging)

**Lines 340-346:** Using default CPLEX options:
```python
my_model.set_esom()  # Uses framework defaults
```

**Previous custom options (commented out):** crossover=1, comptol=1e-5

---

## Runs Created This Session

| Run | Patches | f_perc | CPLEX | Status | Notes |
|-----|---------|--------|-------|--------|-------|
| p20_disable_advcogen | ADVCOGEN=0 | True | crossover=1 | unknown | 2E+05 violations |
| p21_disable_advcogen_nofperc | ADVCOGEN=0 | False | crossover=1 | unknown | 8E+04 violations |
| p22_nochange_test | None | False | crossover=1 | unknown | 2E+05 violations |
| p23_defaults_test | None | False | defaults | unknown | Same failure |

All Session 3 runs failed despite matching settings to v10.

---

## Key Files Modified

1. **scripts/run_calib_manual.py**:
   - Line 305: `f_perc: False`
   - Lines 340-346: Simplified to `my_model.set_esom()` (default options)

2. **calibration/patches/** (new files):
   - `p20_disable_advcogen.csv`
   - `p21_disable_advcogen_nofperc.csv`

3. **Docs/finland_2017_patch_journal.md** (created)

---

## Baseline Ranking (Still Valid)

| Run | Status | Objective | CHP (GWh) | DEC_ADVCOGEN_GAS |
|-----|--------|-----------|-----------|-------------------|
| **v10_oil_constr** | optimal | 49,677 | 22,643 | 14,370 |
| v9 | optimal | 47,195 | 5,220 | 0 |

v10 remains the best baseline (optimal, closest CHP to target).

---

## Next Session Priority

**FIRST:** Fix the data regeneration issue before ANY more calibration runs.

Options:
1. Add `--reuse-dat` flag to run_calib_manual.py
2. Create a minimal "solve only" script that uses existing .dat files
3. Manually edit .dat files for patches

**AFTER THAT:** Resume controlled patch sequence starting with p20 (disable ADVCOGEN).

---

## Quick Commands for Next Session

```powershell
# Compare .dat files
fc.exe "case_studies/FI/calib_2017_finland_v10_oil_constr/reg_technologies.dat" "case_studies/FI/calib_2017_finland_p23_defaults_test/reg_technologies.dat" | Select-Object -First 50

# Check what v10 baseline produces:
cd case_studies/FI/calib_2017_finland_v10_oil_constr
# (Re-run AMPL directly using existing .dat files)

# List all recent runs
Get-ChildItem "case_studies/FI" -Directory | Where-Object { $_.Name -like "calib_2017*p2*" } | Select-Object Name, LastWriteTime
```

---

*End of Session 3 - 2026-03-03*
