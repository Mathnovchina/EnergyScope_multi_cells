# Finland 2017 Calibration - Step-Back Audit

**Date:** 2026-03-03  
**Purpose:** Technical audit before resuming calibration  
**Status:** Read-only analysis, no new model runs

---

## 1. Yesterday Recap (2026-03-02)

### What Was Attempted
Testing `fmin_perc` approach to force CHP production to match Finland 2017 reality data (~25 TWh).

### Session Results
- **29 runs** created in `case_studies/FI/`
- **16 patch files** created in `calibration/patches/`
- **Key discovery**: `f_perc: False` in config was disabling all fmin_perc constraints
- **Partial success**: CHP production increased from 5.2 → 50.7 TWh in p13, but solver gave "unknown status"

---

## 2. Confirmed Findings (High Confidence)

### 2.1 The fmin_perc Mechanism Works

**Evidence:**
- v9 baseline (f_perc=False): CHP = 5.2 TWh
- p13_clean (f_perc=True + fmin_perc): CHP = 50.7 TWh

**AMPL Implementation (esmc/energy_model/ESMC_model_AMPL.mod:656-659):**
```ampl
subject to f_min_perc {c in REGIONS, eut in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE[eut]}:
    sum {t in PERIODS, ...} (F_t [c,j,h,td] * t_op[h,td]) >= fmin_perc [c,j] * 
    (sum {j2 in TECHNOLOGIES_OF_END_USES_TYPE[eut], ...} (F_t [c, j2, h, td] * t_op[h,td])
    + sum {r in RESOURCES, ...} (layers_in_out [r, eut] * ...));
```

The constraint forces a technology to produce **at least fmin_perc% of total sector output**.

### 2.2 The f_perc Config Controls Constraint Activation

**Evidence from esmc/utils/esmc.py (lines 701-712):**
```python
if self.f_perc:
    # drop specific f_perc for train pub and tramway if all f_perc are considered
    self.esom.ampl.get_constraint('f_max_perc_train_pub').drop()
    self.esom.ampl.get_constraint('f_max_perc_tramway').drop()
    self.esom.ampl.get_constraint('f_max_perc_ind_direct_elec').drop()
else:
    # drop general f_perc constraints
    self.esom.ampl.get_constraint('f_max_perc').drop()
    self.esom.ampl.get_constraint('f_min_perc').drop()
```

**Interpretation:**
- `f_perc: True` → general f_min_perc and f_max_perc constraints are ACTIVE
- `f_perc: False` → these constraints are DROPPED (ineffective)

### 2.3 IND_COGEN_COAL Was Missing from Validation

**Evidence:** After adding it to `chp_techs` list in `generate_finland_validation.py`, CHP reported went from 0 → 1.2 TWh for v9 baseline.

### 2.4 FI/Technologies.csv Is an Override File

**Evidence from esmc/utils/region.py (lines 124-134):**
- For ref_region (02_REF_REGION): reads full CSV with all columns
- For regional files (FI): reads partial CSV and uses `df.update()` to merge

**Correct format for FI/Technologies.csv:**
```csv
Technologies param,f_min,f_max,fmin_perc,fmax_perc
AMMONIA_STORAGE,0.0,100.0,0.0,1.0
...
```

### 2.5 f_max=100 Does Not Disable Technologies

**Evidence from Docs/finland_post_v6_diagnosis.md:**
> "setting f_max=100 does NOT disable a technology — it caps it at 100 GW, which the solver happily uses"

Technologies like DEC_ADVCOGEN_GAS, H2_ELECTROLYSIS were deploying at ~99 GW.

**Correct approach:** Use `f_max=0` to truly disable.

---

## 3. Uncertain Findings (Needs Investigation)

### 3.1 Solver "Unknown Status" with f_perc=True

**Symptom:** All f_perc=True runs return solve_result_num=-1

**Comparison of tolerance violations:**

| Run | Status | Variable Bounds MaxAbs | Algebraic Constraints MaxAbs |
|-----|--------|------------------------|------------------------------|
| v9 (f_perc=False) | optimal (0) | - | **1E-02** |
| p13 (f_perc=True) | unknown (-1) | **7E+01** | **1E+05** |

**Magnitude difference:** p13 has 10 million times worse algebraic constraint violations than v9.

**Possible causes (in order of likelihood):**
1. fmin_perc constraints create numerically challenging structure (percentage of aggregate)
2. Interaction between fmin_perc and other constraints creates near-infeasible regions
3. CPLEX barrier algorithm tolerance settings inadequate for this constraint structure
4. The constraint RHS involves sums that can be very large (1E+05 GWh scale)

**This is NOT a data corruption issue** — it's a structural numerical difficulty.

### 3.2 Nuclear Explosion with CHP Constraints

**Observation:**
- v9 (no fmin_perc): Nuclear = 20.8 TWh ✓
- p13 (with fmin_perc): Nuclear = 72.0 TWh (3.4x higher)

**Hypothesis:** When CHP is forced up, the model compensates elsewhere. Nuclear has low operating cost, so the optimizer increases nuclear to offset CHP-related costs.

**Uncertain:** Whether this is:
- A valid model response (revealing CHP forcing is costly)
- A constraint feedback bug
- A numerical artifact from the "unknown status" solve

### 3.3 DEC_ADVCOGEN_GAS Takeover

**Observation:** In p13, DEC_ADVCOGEN_GAS produces 37.8 TWh (taking over CHP category).

**Hypothesis:** This technology has favorable cost parameters and satisfies the fmin_perc constraint for the HEAT_LOW_T or similar end-use category.

**Uncertain:** Whether disabling it is the right approach or if its parameters need correction.

---

## 4. Likely Wrong or Misleading

### 4.1 Contradictory Comment in run_calib_manual.py

**Line 305:**
```python
'f_perc': True,  # Disable fmin_perc/fmax_perc for now
```

The comment says "Disable" but the value is `True`, which **enables** them. This confusion likely led to debugging in wrong directions.

### 4.2 Yesterday's Interpretation of "Data Corruption"

Yesterday's synthesis mentioned:
> "Global data corrupted: Data/2017/FI/Technologies.csv was modified with wrong c_p values"

**Clarification:** This was NOT corruption but rather an **incorrect file format**. The file temporarily had full columns (like REF_REGION) instead of the minimal override format. The `update()` logic would have worked correctly IF columns matched, but parsing failed.

This is a **format issue**, not data corruption.

### 4.3 Cost Explosion Runs

Several runs showed TotalCost values like 7.1e17. These are NOT valid solutions — they represent solver failures where artificial penalty variables dominated.

**Should be discarded entirely.**

---

## 5. What Should Be Kept

| Item | Location | Status |
|------|----------|--------|
| **v9 baseline** | `case_studies/FI/calib_2017_finland_v9/` | ✓ Safe reference |
| **v10_oil_constr baseline** | `case_studies/FI/calib_2017_finland_v10_oil_constr/` | ✓ Safe reference |
| **p16_no_advcogen patch** | `calibration/patches/p16_no_advcogen.csv` | ⚠ Best attempt, but non-optimal solve |
| **generate_finland_validation.py** | `scripts/generate_finland_validation.py` | ✓ With IND_COGEN_COAL fix |
| **run_calib_manual.py** | `scripts/run_calib_manual.py` | ⚠ Fix contradictory comment |

---

## 6. What Should Be Discarded

| Item | Reason |
|------|--------|
| All runs with TotalCost > 1e10 | Solver failures |
| p01-p12 runs | Superseded by later attempts |
| Patches p01-p08 | Debugging attempts, superseded |
| Any interpretation based on "unknown status" runs | Not trustworthy |

---

## 7. Key Blockers Before More Calibration

### Blocker 1: Solver Tolerance (CRITICAL)

**Problem:** f_perc=True runs produce 1E+05 constraint violations, making results unreliable.

**Required before proceeding:**
1. Understand WHY fmin_perc causes such large violations
2. Test CPLEX tolerance options (barconvtol, comptol)
3. Possibly enable crossover (currently disabled)

### Blocker 2: Understand Nuclear Feedback

**Problem:** Nuclear triples when CHP is constrained. Cannot trust this as valid model behavior until solver issues resolved.

### Blocker 3: Script Configuration Consistency

**Problem:** Multiple scripts with different `f_perc` settings:
- run_calib_manual.py: `f_perc: True` (with wrong comment)
- run_calib_case.py: `f_perc: True`
- Various historical runs: mixed

**Required:** Single source of truth for config.

---

## 8. Summary Assessment

| Category | Status | Notes |
|----------|--------|-------|
| **fmin_perc mechanism** | ✓ Confirmed working | Affects CHP as expected |
| **Solver stability** | ✗ Not resolved | Major tolerance violations |
| **Data integrity** | ✓ Restored | FI/Technologies.csv correct format |
| **Validation script** | ✓ Fixed | IND_COGEN_COAL added |
| **Nuclear explosion** | ? Unknown cause | Blocked by solver issues |
| **DEC_ADVCOGEN takeover** | ⚠ Workaround exists | f_max=0 disables it |
| **Ready for calibration** | ✗ NO | Solve blocker first |

---

*Next step: See esmc_solver_audit.md for CPLEX options analysis*
