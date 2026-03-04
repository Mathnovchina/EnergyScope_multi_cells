# Finland 2017 Calibration - Patch Journal

**Created:** 2026-03-03  
**Purpose:** Track controlled micro-patches for Finland 2017 calibration  
**Baseline:** calib_2017_finland_v10_oil_constr

---

## Critical Discovery (2026-03-03)

### Data Divergence Issue

**Problem:** The Data/2017/*.csv files have been modified since v10 was created (Feb 17). This causes new runs to produce incorrect .dat files and solver failures.

**Evidence:**
- v10 reg_technologies.dat: 11,890 bytes, 146/172 lines differ from current
- Example: NUCLEAR f_min = 2.5 (v10) vs 2.76 (current)
- New runs get "unknown status" with massive tolerance violations (8E+04)
- Reusing v10's .dat files produces optimal solve (objective 51,499)

**Solution:** Use `--reuse-dat` flag to use baseline .dat files directly without regenerating from CSV.

**Limitation:** With `--reuse-dat`, CSV patches are ignored. To make changes, we need to:
1. Directly edit .dat files, OR
2. Fix Data/2017/*.csv to match what produced v10, OR
3. Create patch workflow that edits .dat files directly

---

## Baseline Selection

### Run Ranking (2026-03-03)

| Run | Status | Objective | CHP (GWh) | Nuclear (GWh) | Notes |
|-----|--------|-----------|-----------|---------------|-------|
| v9 | **optimal** | 47,195 | 5,220 | 20,824 | Clean but low CHP |
| v10_oil_constr | **optimal** | 49,677 | 22,643 | 20,824 | Better CHP, has oil constraints |
| p13_clean | unknown | 14.9M | 50,700 | ~72,000 | CHP works but solver failed |
| p16_no_advcogen | unknown | 24.2M | ~18,000 | ~80,000 | Disabled ADVCOGEN |

### Selection: v10_oil_constr

**Rationale:**
1. **Optimal solve status** - trustworthy results
2. **CHP at 22.6 TWh** - closest to target (25 TWh) among optimal runs
3. **Oil constraints** - established pattern for Finland specifics
4. Nuclear matches target (20.8 TWh vs 21.9 TWh reality)

**Issue:** DEC_ADVCOGEN_GAS at 14.4 TWh (unrealistic futuristic tech dominating)

**Target CHP Distribution (Finland 2017 reality):**
- Total CHP: ~25 TWh electricity
- IND_COGEN_* should dominate (~12-15 TWh from industrial CHP)
- DHN_COGEN_* ~8-10 TWh
- DEC_COGEN_*/ADVCOGEN should be minimal (future techs)

---

## CPLEX Options

Using improved CPLEX options with crossover enabled:

```python
cplex_options = ['baropt',
                 'predual=-1',
                 'barstart=4',
                 'comptol=1e-5',
                 'crossover=1',      # NEW: Enable crossover
                 'timelimit 172800',
                 'bardisplay=1',
                 'display=2']
```

**Change from default:** `crossover=1` instead of `crossover=0`

---

## Patch Sequence

### Patch 01: Disable ADVCOGEN (Minimum Viable Fix)

**Status:** PLANNED  
**Strategy:** Single change to test crossover=1 and remove unrealistic tech

**Changes:**
```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_max,DEC_ADVCOGEN_GAS,0
Technologies.csv,f_max,DEC_ADVCOGEN_H2,0
```

**Expected Effect:**
- DEC_ADVCOGEN_GAS: 14.4 → 0 TWh
- CHP will need to redistribute to other technologies
- Model should still be optimal (no fmin_perc yet)

**Success Criteria:**
1. solve_result_num = 0 (optimal)
2. CHP redistributes to IND_COGEN_* or DHN_COGEN_*
3. No cost explosion (objective < 60,000)

---

### Patch 02: Gentle IND_COGEN_WOOD fmin_perc (If Patch 01 succeeds)

**Status:** PLANNED  
**Strategy:** Add single fmin_perc constraint to test solver stability

**Changes:**
```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_max,DEC_ADVCOGEN_GAS,0
Technologies.csv,f_max,DEC_ADVCOGEN_H2,0
Technologies.csv,fmin_perc,IND_COGEN_WOOD,0.05
```

**Expected Effect:**
- IND_COGEN_WOOD forced to ≥5% of industrial heat/electricity
- Tests whether crossover=1 resolves tolerance issues

**Success Criteria:**
1. solve_result_num = 0 (optimal)
2. IND_COGEN_WOOD > 5 TWh
3. Constraint violations < 1E-02

---

### Patch 03+ : Progressive CHP Tuning

**Status:** PENDING  
**Depends on:** Patch 01-02 results

Will add more fmin_perc constraints if solver proves stable.

---

## Run Log

| Date | Patch | Run Name | Status | Objective | CHP | Nuclear | Notes |
|------|-------|----------|--------|-----------|-----|---------|-------|
| 2026-03-02 | baseline | v10_oil_constr | optimal | 49,677 | 22,643 | 20,824 | Starting point |
| | p01 | (planned) | - | - | - | - | Disable ADVCOGEN |
| | p02 | (planned) | - | - | - | - | + fmin_perc IND_COGEN_WOOD |

---

*Updated: 2026-03-03 (initial creation)*
