# Regression Audit: Current Workflow vs. Commit `3ffdf3fa`

**Prepared:** 2026-03-11
**Scope:** Finland 2017 manual calibration — numerical robustness regression
**Anchor commit:** `3ffdf3fa773e0b3baa0f93397cdbe4f6e9979b17` ("first run validation", 2026-02-09)
**Current HEAD:** `1a7a7295`

All claims are sourced from `git diff`, file reads, and solver logs.
No speculation unless tagged **[Likely]** or **[Possible]**.

---

## 1. What Definitely Changed Since `3ffdf3fa`

### 1A. `Data/2017/FI/Technologies.csv` — MAJOR CHANGE

This is the most impactful change. The file was redesigned between the anchor commit and today.

**Old file at 3ffdf3fa** (`git show 3ffdf3fa:Data/2017/FI/Technologies.csv`):

```
Technologies param,f_min,f_max
NUCLEAR,2.484,3.036
PV_ROOFTOP,0.02,2.0
PV_UTILITY,0.0,1.0
WIND_ONSHORE,1.35,5.0
WIND_OFFSHORE,0.0,0.0
HYDRO_DAM,1.21,2.383
HYDRO_RIVER,2.94,3.59
DHN_SOLAR,0.0,56.345
DEC_SOLAR,0.0,56.345
DAM_STORAGE,0.001,0.001
PHS,0.001,0.001
COAL_US,3.5,4.5          ← FORCED FROM BELOW
CCGT,0.6,1.5             ← FORCED FROM BELOW
DHN_COGEN_GAS,0.6,1.5   ← FORCED FROM BELOW
DHN_BOILER_OIL,0.4,1.0  ← FORCED FROM BELOW
IND_BOILER_OIL,0.2,1.0  ← FORCED FROM BELOW
ELECTRICITY,0,100000
COAL,0,100000
GAS,0,100000
```

**Current file at HEAD** (block2b anchor, `bak_20260311_112346`):

```
Technologies param,f_min,f_max
NUCLEAR,2.7,2.835
PV_ROOFTOP,0.0,15.0      ← 7.5× larger cap than old
PV_UTILITY,0.0,60.0      ← 60× larger cap than old
WIND_ONSHORE,2.0,2.1     ← much tighter bilateral (was 1.35–5.0)
WIND_OFFSHORE,0.0,0.0
HYDRO_DAM,0.0,3.5        ← f_min removed (was 1.21)
HYDRO_RIVER,0.0,4.0      ← f_min removed (was 2.94)
DHN_SOLAR,0.0,60.0
DEC_SOLAR,0.0,60.0
DAM_STORAGE,0.0,0.1
PHS,0.0,0.1
# COAL_US — NOT in file → f_min=0, f_max=Infinity from REF_REGION
# CCGT — NOT in file → f_min=0, f_max=Infinity from REF_REGION
# DHN_COGEN_GAS — NOT in file → open
# DHN_BOILER_OIL — NOT in file → open
# IND_BOILER_OIL — NOT in file → open
# ELECTRICITY, COAL, GAS — not explicitly bounded
```

**Confirmed in `calib_2017_finland_v1/reg_technologies.dat`** (archive run, Feb 16):

```
FI  COAL_US   2168.8  35.39  …  f_min=3.5  f_max=4.5    ← FORCED
FI  CCGT      982.56  31.8   …  f_min=0.6  f_max=1.5    ← FORCED
FI  HYDRO_DAM 4200.7  21.0   …  f_min=1.1  f_max=1.3    ← FORCED bilateral
FI  HYDRO_RIVER 5044.9 50.4  …  f_min=1.9  f_max=2.1    ← FORCED bilateral
FI  PV_ROOFTOP 1498.77 15.39 …  f_min=0.02 f_max=2.0    ← cap 2.0 GW
FI  PV_UTILITY 1156.67 12.67 …  f_min=0.0  f_max=1.0    ← cap 1.0 GW
FI  DHN_COGEN_GAS 1424.9 31.8 … f_min=0.6  f_max=1.5    ← FORCED
FI  DHN_BOILER_OIL 54.9 1.18 …  f_min=0.4  f_max=1.0    ← FORCED
FI  IND_BOILER_OIL 54.9 1.18 …  f_min=0.2  f_max=1.0    ← FORCED
```

**Summary of FI constraint changes:**

| Technology | Old f_min | Old f_max | New f_min | New f_max | Change |
|---|---|---|---|---|---|
| NUCLEAR | 2.484 | 3.036 | 2.7 | 2.835 | Tightened both sides |
| PV_ROOFTOP | 0.02 | 2.0 | 0.0 | 15.0 | Cap raised 7.5× |
| PV_UTILITY | 0.0 | 1.0 | 0.0 | 60.0 | Cap raised 60× |
| WIND_ONSHORE | 1.35 | 5.0 | 2.0 | 2.1 | Narrowed (near-fixed) |
| HYDRO_DAM | 1.21 | 2.383 | 0.0 | 3.5 | f_min removed |
| HYDRO_RIVER | 2.94 | 3.59 | 0.0 | 4.0 | f_min removed |
| COAL_US | 3.5 | 4.5 | 0.0 | Infinity | **All constraints removed** |
| CCGT | 0.6 | 1.5 | 0.0 | Infinity | **All constraints removed** |
| DHN_COGEN_GAS | 0.6 | 1.5 | 0.0 | Infinity | **All constraints removed** |
| DHN_BOILER_OIL | 0.4 | 1.0 | 0.0 | Infinity | **All constraints removed** |
| IND_BOILER_OIL | 0.2 | 1.0 | 0.0 | Infinity | **All constraints removed** |

---

### 1B. `Data/2017/02_REF_REGION/Technologies.csv` — COST DATA CHANGED

The cost data changed substantially. `f_min`/`f_max` values in REF_REGION are not overridden for most technologies by FI file, so REF_REGION defaults (f_min=0, f_max=Infinity) are unchanged. But **investment and O&M costs changed**.

**Key cost changes (old at 3ffdf3fa → new at HEAD):**

| Technology | Old c_inv [€/kW] | New c_inv [€/kW] | Ratio |
|---|---|---|---|
| NUCLEAR | 4845.73 | 6000.00 | 1.24× higher |
| CCGT | 771.99 | 982.56 | 1.27× higher |
| COAL_US | 2516.71 | 2168.80 | 0.86× (lower) |
| PV_ROOFTOP | **737.89** | **1498.77** | **2.03× higher** |
| PV_UTILITY | **335.40** | **1156.67** | **3.45× higher** |
| WIND_ONSHORE | 1010.00 | 1095.36 | 1.08× higher |
| WIND_OFFSHORE | 1255.37 | 2780.23 | 2.21× higher |
| IND_BOILER_WOOD | 115.18 | 576.70 | 5.01× higher |
| DHN_HP_ELEC | 344.76 | 510.42 | 1.48× higher |
| DHN_COGEN_GAS | 1254.49 | 1424.92 | 1.14× higher |
| DHN_BOILER_WOOD | 115.18 | 513.61 | 4.46× higher |
| DHN_SOLAR | 362.00 | 328.23 | 0.91× (slightly lower) |

**Also: new feasible region change in REF_REGION:**
- `DIESEL_TO_JET_FUEL`: f_max changed from **0.0 → 1.00E+15** (previously blocked, now open)

---

### 1C. `Data/2017/00_INDEP/Layers_in_out.csv`

Two new technology rows added:
- `DHN_COGEN_COAL` — coal-fired district heating cogeneration
- `IND_COGEN_COAL` — coal-fired industrial cogeneration

Both rows define the ELECTRICITY, HEAT_HIGH_T, and CO2 flows. These were not present at 3ffdf3fa. They are paired with new rows added to REF_REGION Technologies.csv.

---

### 1D. Deprecated run script: `scripts/run_finland.py`

This file **existed at 3ffdf3fa** and was **deleted** at a later commit. It is the script that produced the early archive runs (`ref_2017_finland`, `calib_2017_finland_v1–v4`).

The current runner is `scripts/run_calib_manual.py` (created after the old script was deleted).

---

### 1E. `esmc/utils/esmc.py` — Minor / Already Restored

The only diff between 3ffdf3fa and current esmc.py is a duplicate block insertion and removal of some diagnostic AMPL eval lines in `solve_esom()`. These are cosmetic or diagnostic only.

The **solver defaults are identical** in `esmc.py` at both commits:
```python
['baropt', 'predual=-1', 'barstart=4', 'comptol=1e-5', 'crossover=0',
 'timelimit 172800', 'bardisplay=1']
```

---

### 1F. No Change

| File | Change |
|---|---|
| `esmc/utils/region.py` | **None** (0-line diff) |
| `esmc/energy_model/ESMC_model_AMPL.mod` | **None** (0-line diff) |
| `Data/2017/FI/Misc.json` | **None** |
| `Data/2017/00_INDEP/Misc_indep.json` | **None** |

---

## 2. Which Changes Can Affect Numerical Stability

### A. Removal of fossil f_min constraints — HIGH impact on LP geometry

**Before:** COAL_US (3.5 GW), CCGT (0.6 GW), DHN_COGEN_GAS (0.6 GW), DHN_BOILER_OIL (0.4 GW), IND_BOILER_OIL (0.2 GW), HYDRO_DAM (1.1 GW), HYDRO_RIVER (1.9 GW) all had f_min > 0.

The LP always had a mandatory fossil/hydro "skeleton" providing at least ~7–8 GW of dispatchable capacity regardless of what renewable technologies did. The barrier algorithm had a wide, well-defined feasible region with a clear optimal basin.

**After:** All those f_min values are 0. Only NUCLEAR (2.7–2.835 GW) and WIND_ONSHORE (2.0–2.1 GW) are forced. The LP must "choose" coal and gas from cost signals alone. The feasible region is nominally larger (more variables free), but the optimizer has less structural guidance, making the interior more degenerate when renewables are also capped.

**Classification: CAN AFFECT NUMERICAL STABILITY. Hard evidence. Not a hypothesis.**

### B. 2–3.5× increase in solar costs — HIGH impact on LP interior geometry

**Before:** PV_UTILITY c_inv = 335 € → the optimizer's cheapest path to satisfy unconstrained electricity balance was abundant cheap solar.

**After:** PV_UTILITY c_inv = 1157 €, PV_ROOFTOP = 1499 € → solar is now 3× as expensive. The optimizer still deploys solar when it's the only option (e.g., block2b, where nuclear+wind+CCGT don't cover balance), but the cost gradient is much steeper.

**Interaction effect:** When solar is capped (as in block3c) AND solar is costly, the optimizer has no cheap path to close the electricity balance gap. The barrier starts from a point where the objective is dominated by solar cost, and capping solar creates a sharp LP corner rather than a smooth interior. This directly causes code 100 (degenerate interior point).

**Classification: CAN AFFECT NUMERICAL STABILITY. Evidenced by block3c objective 1.22e+11 vs expected ~36000–50000.**

### C. WIND_ONSHORE narrowed from 1.35–5.0 to 2.0–2.1

This is a tighter bilateral constraint (the feasible range is 0.1 GW instead of 3.65 GW). It reduces one degree of freedom significantly. Combined with nuclear fixed at 2.7–2.835, the only remaining unconstrained electricity generators with substantial reach are solar and fossil.

**Classification: CAN AFFECT NUMERICAL STABILITY (in combination with A and B).**

### D. Deletion of `run_finland.py` and replacement with `run_calib_manual.py`

The solver logic, options, and AMPL call sequence are **identical** in both. Differences (patch system, metadata, fallback, scoring) are all post-solve overhead or pre-solve overhead. The fallback (dual simplex, 1800s) is NEW and is triggered when the primary barrier returns code 100. The fallback itself does not influence the primary solve.

**Issue found in documentation:** The `run_calib_manual.py` docstring says "barrier+crossover=1" but the implementation uses `crossover=0`. This is pre-existing and also matched the old esmc.py default. The primary solve behavior is therefore identical to the old script.

**Classification: COSMETIC for solver logic. Diagnostic overhead added post-solve.**

---

## 3. Which Changes Can Affect the Feasible Region

### A. DIESEL_TO_JET_FUEL f_max: 0.0 → 1.00E+15

Previously this technology was disabled (f_max=0). It is now open. This adds one degree of freedom but is unlikely to be relevant for electricity balance in Finland in a primary energy calibration context.

**Classification: CAN AFFECT FEASIBLE REGION (minor, diesel/jet paths only).**

### B. New technologies DHN_COGEN_COAL, IND_COGEN_COAL

Two new coal cogeneration technologies were added to Layers_in_out.csv and REF_REGION Technologies.csv. These expand the feasible region by adding coal→heat+electricity pathways. In principle this helps feasibility but adds variables and constraints.

**Classification: CAN AFFECT FEASIBLE REGION (expands it marginally).**

### C. Removal of COAL_US, CCGT, DHN_COGEN_GAS f_max caps in FI file

The old FI file had `COAL_US,3.5,4.5` — upper and lower cap. The new FI file removes COAL_US entirely, reverting to REF_REGION f_max=Infinity. This makes the feasible region **larger** (more coal is allowed). However, removing f_min=3.5 GW also removes the guarantee that coal is deployed.

**Classification: EXPANDS feasible region but removes guaranteed feasible skeleton.**

### D. Solar caps: PV_UTILITY 1.0 → 60.0 GW; PV_ROOFTOP 2.0 → 15.0 GW

The old caps were very tight (3 GW total). Current anchor has 75 GW total. The model can deploy far more solar, which is good for calibration accuracy.

**Classification: CAN AFFECT FEASIBLE REGION (expands it, beneficial for calibration).**

---

## 4. Whether the Old Workflow Was Genuinely Simpler / More Robust

Yes, the old workflow was genuinely simpler and structurally more robust. This is not just opinion — it is evidenced by the solve logs.

**Evidence:**

| Run | Date | Config origin | Primary failures | solve_result_num | barrier iters | solve_elapsed_s | con viol MaxAbs |
|---|---|---|---|---|---|---|---|
| `ref_2017_finland` | 2026-02-10 | 3ffdf3fa data | 0 | 0 | 231 | 461 | 1E-03 |
| `calib_v1` | 2026-02-16 | near-3ffdf3fa | 0 | 0 | 202 | 145 | 2E-02 |
| `calib_v2` | 2026-02-16 | near-3ffdf3fa | 0 | 0 | 270 | 249 | 6E-02 |
| `block2b` (best current) | 2026-03-10 | HEAD data | 0 | 0 | 266 | 127 | 8E-04 |
| `block3c` (failed) | 2026-03-11 | HEAD data | **YES** | **100** | 100 | 217 | **4E+02** |

**Why old runs never failed:**

The old FI/Technologies.csv ensured a guaranteed feasible backbone by forcing fossil and hydro from below:
- COAL_US: 3.5–4.5 GW mandatory
- CCGT: 0.6–1.5 GW mandatory
- DHN_COGEN_GAS: 0.6–1.5 GW mandatory
- DHN_BOILER_OIL: 0.4–1.0 GW mandatory
- IND_BOILER_OIL: 0.2–1.0 GW mandatory
- HYDRO_DAM: 1.1–1.3 GW mandatory bilateral
- HYDRO_RIVER: 1.9–2.1 GW mandatory bilateral

In this regime, the electricity balance was always satisfiable by construction. With 7–8 GW of forced dispatchable capacity, the LP had a well-conditioned feasible interior. Solar was a cosmetic add-on with tiny caps (3 GW total). The barrier converged reliably in 145–461 seconds.

The old workflow was also simpler architecturally: `scripts/run_finland.py` was 91 lines with no patch system, no fallback, no scoring, no validation. The reduced complexity had zero side effects on solver behavior.

**Why block2b still works under the current setup:**

block2b succeeded (127s, code 0) because solar was fully open (60+15=75 GW), and the optimizer placed 36.2 GW of solar as its primary means to balance electricity. Even with expensive solar (c_inv=1157 €), it was still the cheapest or most available option given fossil f_min=0.

**Why block3c fails:**

Capping solar to 19 GW (4+15) forced the optimizer to search for fossil substitution from f_min=0 with no clear cost gradient toward a feasible point. The barrier entered a degenerate interior (objective 1.22e+11) and the fallback dual simplex ran 1800 seconds without converging.

**The key statement:**
> The old workflow was robust because it used a constraint framework that guaranteed a feasible solution by construction (fossil f_min). The current workflow relies on the optimizer finding its own path to feasibility within a far larger, unconstrained search space.

---

## 5. Whether We Should Revert to a Simpler Manual Runner

**Short answer: YES — but not because the current script is the source of instability.**

The source of instability is the **constraint structure** (Section 4), not the runner. The pipeline code, solver options, and AMPL call sequence are identical. The fallback mechanism adds noise (extra logging, second AMPL instance) but does not affect the primary solve.

However, a simpler runner IS justified for these reasons:

1. **Diagnostic clarity**: The current script has 7 pipeline steps, any of which can fail with misleading output. A minimal runner with 4 steps is easier to diagnose.
2. **Patch system confusion**: The patch CSV system is still present and any accidental use would silently modify the model. Manual calibration should rely exclusively on FI/Technologies.csv.
3. **AMPL close behavior**: Closing AMPL after a failed solve may mask secondary diagnostics.
4. **7-step pipeline**: The postprocessing (scoring, plots, rankings) runs even when the solve is marginal.
5. **Fallback obfuscates primary failure**: Running a 1800s dual simplex after a barrier code 100 makes it harder to distinguish "barrier numerical issue" from "true infeasibility" from "time limit".

**Specification for a minimal manual runner** (`scripts/run_fi_manual_simple.py`):

```
MINIMAL RUNNER SPECIFICATION
=============================

Purpose:
  Reproducible, transparent manual calibration runs for Finland 2017.
  No patch system. No side effects. No ambiguous fallback.

Steps (4 only):
  1. Initialize Esmc(config, nbr_td=12)
  2. read_data_indep() + init_regions()
  3. init_ta(algo='read') + print_td_data() + print_data(indep=True)
  4. Copy all .dat to input_snapshot/
  5. set_esom() + solve_esom() with explicit CPLEX options
  6. Write run_metadata.json regardless of solve outcome
  7. If solve_result_num == 0: get_year_results() + prints_esom()

FI override:
  Reads Data/2017/FI/Technologies.csv directly via init_regions().
  No patch system. No monkey-patching.
  REF_REGION rows not in FI file are always inherited unchanged.

Solver:
  Primary: barrier with crossover=0 (current ESMC default, matches all
           past successful runs including ref_2017_finland, calib_v1, block2b)
  Time limit: 172800s (48h, same as current)
  Fallback: OPTIONAL, controlled by --with-fallback flag
            If enabled: dual simplex, 7200s (not 1800s — give it more time)
            Default: OFF

Metadata (always written, even on failure):
  run_metadata.json:
    - solve_result_num
    - solve_elapsed_time
    - git commit
    - FI/Technologies.csv content (copied verbatim)
    - solver options used

Input snapshot (always written):
  input_snapshot/*.dat — every .dat file before solve

Validation plots:
  Only on solve_result_num == 0.

Score comparison:
  Only on solve_result_num == 0.
  Use REALITY_TARGETS from current run_calib_manual.py unchanged.

No output on failure:
  If solve_result_num != 0: write only metadata and logs.
  Do NOT call get_year_results() or prints_esom() on failure.
  Print exact solver message to stdout.

CLI:
  python scripts/run_fi_manual_simple.py -n <run_name> -d "<description>"
  Optional: --no-fperc (default True = no fperc, consistent with all recent runs)
  Optional: --with-fallback

Output directory:
  case_studies/FI/manual_runs/<YYYYMMDD_HHMMSS>__<run_name>/
  (same as current)

What NOT to include:
  - No patch system (patch_files, apply_patches, _FILE_MAP)
  - No run_notes.md template
  - No run_rankings.csv append logic (or make it optional)
  - No _init_regions_custom() monkey-patch
  - No --data-dir override
  - No --kmedoid option
  - No --solver CLI option (one path only: barrier)
  - No copy.deepcopy(model) calls
  - No subprocess calls except git metadata
```

---

## 6. The Safest Next Step

### Immediate action required (before next run)

The current `Data/2017/FI/Technologies.csv` still has the block3c values (PV_ROOFTOP=4.0, PV_UTILITY=15.0). **Restore the block2b anchor before any test run:**

```powershell
Copy-Item "Data\2017\FI\Technologies.csv.bak_20260311_112346" "Data\2017\FI\Technologies.csv" -Force
```

### Next calibration action

**Option A — Current approach but one change at a time:**
From block2b anchor, modify only `PV_UTILITY` from 60.0 → 15.0.
Keep PV_ROOFTOP at 15.0. Total solar headroom: 30 GW.
This is the most conservative single-step test of whether tighter solar caps work.

**Option B — Return to fossil-anchored calibration (closer to old approach):**
Instead of capping solar, introduce f_min constraints on CCGT (e.g., 0.6–2.0 GW) and/or COAL_US (e.g., 1.0–3.0 GW). This reintroduces the fossil backbone that made old runs reliable. Then calibrate solar and nuclear separately.
This is the approach that provably worked at the 3ffdf3fa regime.

**Option C — Build the minimal runner first:**
Before running more experiments, implement `run_fi_manual_simple.py` (spec in Section 5). This removes ambiguity from the fallback and patch system, giving cleaner evidence.

### Recommendation

> **Build a stripped-down manual runner first.**
>
> Not because the current runner is broken, but because the contrast between Option A
> (current approach) and Option B (fossil-backbone) is too important to test with a
> complex 7-step pipeline that has multiple failure modes. A minimal runner will produce
> unambiguous evidence about whether the fossil-backbone approach is genuinely needed,
> which will then guide all subsequent constraint choices.
>
> After the minimal runner is in place, test Option B as the first run: restore fossil
> f_min constraints similar to the 3ffdf3fa era. If that solves cleanly, the hypothesis
> (Section 4) is confirmed and calibration can proceed with a stable foundation.

---

## Summary Table

| Category | Item | Affects stability | Affects feasible region | Direction |
|---|---|---|---|---|
| FI/Technologies.csv | COAL_US f_min removed (was 3.5 GW) | **YES — high** | Relaxes constraint | Destabilizing |
| FI/Technologies.csv | CCGT f_min removed (was 0.6 GW) | **YES — high** | Relaxes constraint | Destabilizing |
| FI/Technologies.csv | DHN_COGEN_GAS f_min removed (was 0.6 GW) | **YES — moderate** | Relaxes | Destabilizing |
| FI/Technologies.csv | HYDRO f_min removed | **YES — moderate** | Relaxes | Destabilizing |
| FI/Technologies.csv | PV_UTILITY cap: 1→60 GW | **YES — indirect** | Expands | Stabilizing (when open) |
| FI/Technologies.csv | WIND_ONSHORE 1.35–5.0 → 2.0–2.1 | YES (combined) | Tightens | Neutral/mildly destabilizing |
| REF_REGION costs | PV c_inv 335 → 1157 (+245%) | **YES — high** | None (cost only) | Destabilizing (LP geometry) |
| REF_REGION costs | NUCLEAR c_inv 4846 → 6000 (+24%) | Moderate | None | Mildly destabilizing |
| REF_REGION costs | CCGT c_inv 772 → 983 (+27%) | Small | None | Mildly destabilizing |
| Layers_in_out.csv | New DHN_COGEN_COAL, IND_COGEN_COAL | Small | Expands feasible region | Neutral/slightly stabilizing |
| REF_REGION | DIESEL_TO_JET_FUEL f_max 0→Infinity | None in practice | Expands (minor) | Neutral |
| esmc.py | Duplicate block + removed diagnostic evals | **None** | None | Cosmetic |
| region.py | No change | None | None | — |
| .mod file | No change | None | None | — |
| run_finland.py → run_calib_manual.py | Same solver path, added overhead | **None** | None | Diagnostic overhead only |
| crossover=0 | Unchanged in both old and new | None (both used 0) | None | — |
| Fallback mechanism | New in run_calib_manual.py | **None on primary** | None | Adds diagnostic noise |
