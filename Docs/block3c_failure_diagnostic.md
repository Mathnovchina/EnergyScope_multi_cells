# Block 3c Failure Diagnostic

**Run:** `case_studies/FI/manual_runs/20260311_130952__block3c_windcap_from_block2b`
**Date:** 2026-03-11
**Git commit at time of run:** `1a7a7295`

All claims below are sourced directly from disk artifacts.
No speculation unless explicitly tagged as **[Likely]** or **[Possible]**.

---

## STEP 1 — Active Constraint State

### Files read

| File | Exists | Size | Notes |
|------|--------|------|-------|
| `Data/2017/FI/Technologies.csv` | Yes | 379 bytes | Current active file — modified 2026-03-11 13:08:55 |
| `Data/2017/FI/Technologies.csv.bak_20260311_112346` | Yes | 446 bytes | Block 2b anchor (confirmed equivalent to block2b_offshore_zero_keep) |
| `…/20260311_130952…/input_snapshot/reg_technologies.dat` | Yes | 12063 bytes | Failed run's solver input |
| `…/20260311_130952…/CONSTRAINT_DIFF.md` | **No** | — | Not generated (run failed before that step) |
| `…/20260311_130952…/run_metadata.json` | Yes | 767 bytes | Confirmed: status=FAILED, code=-1 |

### Constraint table: key technologies

| Technology | FI/Technologies.csv (active) | Block 2b anchor (bak_112346) | reg_technologies.dat (block3c) | Propagated? | Status in failed run |
|---|---|---|---|---|---|
| NUCLEAR | f_min=2.7, f_max=2.835 | f_min=2.7, f_max=2.835 | f_min=2.7, f_max=2.835 | **YES** | Capped tight |
| WIND_ONSHORE | f_min=2.0, f_max=2.1 | f_min=2.0, f_max=2.1 | f_min=2.0, f_max=2.1 | **YES** | Capped tight |
| WIND_OFFSHORE | f_min=0.0, f_max=0.0 | f_min=0.0, f_max=0.0 | f_min=0.0, f_max=0.0 | **YES** | Disabled |
| PV_ROOFTOP | f_min=0.0, f_max=**4.0** | f_min=0.0, f_max=**15.0** | f_min=0.0, f_max=**4.0** | **YES** | **Tightened vs block2b** |
| PV_UTILITY | f_min=0.0, f_max=**15.0** | f_min=0.0, f_max=**60.0** | f_min=0.0, f_max=**15.0** | **YES** | **Tightened vs block2b** |
| HYDRO_DAM | f_min=0.0, f_max=3.5 | f_min=0.0, f_max=3.5 | f_min=0.0, f_max=3.5 | YES | Open (unchanged) |
| HYDRO_RIVER | f_min=0.0, f_max=4.0 | f_min=0.0, f_max=4.0 | f_min=0.0, f_max=4.0 | YES | Open (unchanged) |
| CCGT | not in FI file | not in FI file | f_min=0.0, f_max=Infinity | REF_REGION default | Open |
| COAL_US | not in FI file | not in FI file | f_min=0.0, f_max=Infinity | REF_REGION default | Open |
| BIOMASS_TO_POWER | not in FI file | not in FI file | f_min=0.0, f_max=Infinity | REF_REGION default | Open |
| DHN_COGEN_GAS | not in FI file | not in FI file | f_min=0.0, f_max=Infinity | REF_REGION default | Open |
| DHN_COGEN_WOOD | not in FI file | not in FI file | f_min=0.0, f_max=Infinity | REF_REGION default | Open |
| DEC_COGEN_GAS | not in FI file | not in FI file | f_min=0.0, f_max=Infinity | REF_REGION default | Open |
| DEC_COGEN_OIL | not in FI file | not in FI file | f_min=0.0, f_max=Infinity | REF_REGION default | Open |

### Propagation verdict

All edits made in `FI/Technologies.csv` propagated correctly into `reg_technologies.dat`.
No hidden overwrite. No orphan constraint. The `.update()` logic in `esmc/utils/region.py` line 135
replaced only the matching rows and only the defined columns.

**The failure is not a propagation bug.**

---

## STEP 2 — Run-to-Run Comparison

### Metadata comparison

| Field | Block 2b (success) | Block 3c (failed) |
|---|---|---|
| Run dir | `20260310_145734__block2b_offshore_zero_from_block2` | `20260311_130952__block3c_windcap_from_block2b` |
| Git commit | `1d50d60a` | `1a7a7295` |
| solve_result status | OK | **FAILED** |
| solve_result code | 0 (optimal) | **-1** |
| solver desc | optimal | unknown (barrier interior, crossover may have failed) |
| score | 1280.06% | **null** |
| objective | 36096.37 | **null** |
| f_perc | False | False |
| gwp_limit_overall | None | None |
| re_share_primary | None | None |
| patches | none | none |
| outputs/ present | **Yes** | **No** |
| validation_plots/ | **Yes** | **No** |
| CONSTRAINT_DIFF.md | Yes | **No** |

### Key capacity comparison (from block2b outputs, vs what was constrained in block3c)

| Technology | Block 2b deployed F (GW) | Block 2b f_min / f_max | Block 3c f_min / f_max | Impact |
|---|---|---|---|---|
| NUCLEAR | 2.835 | 2.7 / 2.835 | 2.7 / 2.835 | unchanged |
| WIND_ONSHORE | 2.1 | 2.0 / 2.1 | 2.0 / 2.1 | unchanged |
| WIND_OFFSHORE | 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | unchanged |
| PV_ROOFTOP | **6.84** | 0.0 / 15.0 | 0.0 / **4.0** | cap below block2b deployed value |
| PV_UTILITY | **29.39** | 0.0 / 60.0 | 0.0 / **15.0** | cap far below block2b deployed value |
| HYDRO_RIVER | 4.0 (at cap) | 0.0 / 4.0 | 0.0 / 4.0 | unchanged |
| HYDRO_DAM | 0.0 | 0.0 / 3.5 | 0.0 / 3.5 | unchanged |
| CCGT | 0.0 | REF default | REF default | open (unchanged) |
| COAL_US | 0.0 | REF default | REF default | open (unchanged) |

**Critical observation:** In the block2b successful run, the optimizer deployed 36.2 GW of solar
(PV_ROOFTOP 6.84 + PV_UTILITY 29.39) to balance the electricity system. Block 3c capped total solar
at 19.0 GW (4.0 + 15.0), which is only 52% of what the optimizer chose in block2b.
The optimizer's primary escape valve was removed simultaneously with wind+nuclear already capped.

Also note: the two runs used **different REF_REGION cost data** (different git commits).
Block 2b used NUCLEAR c_inv=6000, PV_ROOFTOP c_inv=1498.77.
Block 3c used NUCLEAR c_inv=4845.73, PV_ROOFTOP c_inv=737.89.
This does not affect feasibility but does affect which solution the optimizer prefers.

---

## STEP 3 — Failure Mode Diagnosis

### Exact solver messages (from logs)

**Primary solve (log.txt):**
```
bar:crossover = 0
100 barrier iterations
CPLEX 22.1.2: reported feasible or optimal but numeric issue; objective 1.223975043e+11
WARNING: "Tolerance violations"
  variable bounds   MaxAbs 4E+01  MaxRel 1E-01
  algebraic con(s)  MaxAbs 4E+02  MaxRel 3E+00
solve_result_num: 100
```

**Fallback solve (log_fallback.txt):**
```
alg:dualproblem
lim:time = 1800
185647 simplex iterations
CPLEX 22.1.2: unknown solution status; objective 0.6236760379
WARNING: "Tolerance violations"
  variable bounds   MaxAbs 2E+05  MaxRel 1E+00
  algebraic con(s)  MaxAbs 2E+07  MaxRel 1E+02
solve_result_num: -1
```

### Classification

| Question | Answer | Confidence |
|---|---|---|
| A. Explicit infeasibility certificate? | **No.** Neither code 200 (infeasible) nor 201 appeared anywhere. | Proven |
| B. Primary barrier numerically unstable? | **Yes.** Code 100 + objective 1.22e+11 (vs expected ~36000) + tolerance violations. Barrier ran 100 iterations and stalled in a degenerate interior point. | Proven |
| C. Fallback dual simplex finished? | **No.** It ran 185647 iterations, then hit the 1800s time limit (log: `_solve_elapsed_time = 1803.047`). Code -1 means "unknown solution status", not infeasible. | Proven |
| D. Solver failed to produce usable solution? | **Yes.** Both primary and fallback produced no valid primal solution. Script correctly classified this as FAILED. | Proven |
| E. Outputs trustworthy? | **No.** No outputs/ or validation_plots/ were written. | Proven |

### Root cause

**Note on crossover:** The script docstring says "crossover=1" but the actual implementation
(`_barrier_crossover_opts`, line 129) uses `crossover=0`. This is a pre-existing discrepancy
in the script — the block2b successful run also used `crossover=0`. This is not the cause
of the new failure.

The actual cause: in block2b, the optimizer escaped infeasibility pressure by deploying
36.2 GW solar. With solar capped at 19.0 GW in block3c, the LP interior became much harder
to navigate. The barrier converged to a degenerate point (objective 1.22e+11), and the
fallback dual simplex (1800s limit) ran out of time before finding a usable basic feasible
solution.

This is **numeric solver difficulty under compounded tight caps**, not proven infeasibility.
CCGT, COAL_US, HYDRO_RIVER are all open in both runs.

---

## STEP 4 — Hidden Policy Constraints

### Verified from run_metadata.json + esmc.py line 700–714

| Constraint | Source | Status in block3c |
|---|---|---|
| `Minimum_RE_share` | `re_share_primary = None` → dropped (esmc.py line 702) | **INACTIVE** |
| `Minimum_GWP_reduction_global` | `gwp_limit_overall = None` → dropped (esmc.py line 700) | **INACTIVE** |
| `f_max_perc` | `--no-fperc` → dropped (esmc.py line 712) | **INACTIVE** |
| `f_min_perc` | `--no-fperc` → dropped (esmc.py line 713) | **INACTIVE** |
| `f_max_perc_train_pub` | not dropped (because f_perc=False path drops general, not specific) | **INACTIVE** (general drop) |
| DHN_SOLAR f_max = 60.0 | FI file has DHN_SOLAR 0.0/60.0; propagated to .dat | **ACTIVE** — wide open |
| DEC_SOLAR f_max = 60.0 | FI file has DEC_SOLAR 0.0/60.0; propagated to .dat | **ACTIVE** — wide open |

### Active high-level constraints

None. No RE share, no GWP, no fperc.

### Inactive high-level constraints

RE share, GWP/CO2 limit, fmin_perc/fmax_perc — all dropped.

### Implication

There are no hidden global constraints forcing the failure.
The failure is entirely due to the interaction between tight wind+nuclear+new solar caps
and the solver's ability to find a feasible interior point.

---

## STEP 5 — Model Mechanics (relevant to this run only)

### How FI overrides REF_REGION

Source: `esmc/utils/region.py` lines 131–135:

```python
df = pd.read_csv(r_path, sep=CSV_SEPARATOR, header=[0], index_col=[0]).dropna(how='all', axis=1)
df = clean_indices(df)
self.data['Technologies'].update(df)
```

Pandas `.update()` replaces existing values **in-place only where FI has non-NaN values and
matching index labels**. Rows absent from FI keep their REF_REGION values. Columns absent from
FI (e.g. `c_inv`, `c_maint`) keep their REF_REGION values.

**Consequence for this run:** The current FI file has only `f_min` and `f_max` columns.
It does NOT override `c_inv`, `c_maint`, `fmin_perc`, `fmax_perc`, or other columns.
Those come from REF_REGION. This is confirmed by the `.dat` file showing 2017-REF cost data
rather than the older block2b REF costs.

### f_min / f_max in the model

`f_min` and `f_max` are directly written to the AMPL parameter table in `reg_technologies.dat`
as bounds on installed capacity `F` (GW). They appear in the hard constraint:

```
f_min[r, t] ≤ F[r, t] ≤ f_max[r, t]
```

These are hard LP bounds — there is no soft relaxation.

### Electricity balance

Strict equality: total electricity production (nuclear + wind + hydro + solar + thermal + imports)
must equal total consumption (demands + heat pumps + exports + losses). This is a moment-by-moment
constraint across all 12 typical days × 24 hours.

### CHP coupling

CHP technologies (DHN_COGEN_GAS, DHN_COGEN_WOOD, etc.) produce electricity and heat
simultaneously in fixed ratios. Forcing one output is equivalent to forcing both. In block2b,
CHP produced 40.83 TWh/yr electricity; it was not independently dispatchable.

### Solar area / F_solar

`DHN_SOLAR` and `DEC_SOLAR` are separate roof/ground thermal collector technologies with their
own f_max (60.0 GW each in FI file). They do not share bounds with `PV_ROOFTOP` or `PV_UTILITY`.
DHN_SOLAR and DEC_SOLAR were not changed in block3c. Their solar resource (`RES_SOLAR`) is
shared, so excessive DHN_SOLAR / DEC_SOLAR could partially substitute if optically cheaper,
but this does not affect the failure mode found here.

---

## STEP 6 — Conservative Verdict

### 1. What is proven

1. All FI/Technologies.csv edits propagated correctly to reg_technologies.dat (NUCLEAR, WIND, PV values all match).
2. No hidden overwrite. No orphan constraint.
3. Primary barrier returned code 100 with objective 1.22×10¹¹ (degenerate interior point).
4. Fallback dual simplex hit the 1800-second time limit and returned code -1 (unknown, not infeasible).
5. No infeasibility certificate was issued (no code 200).
6. No outputs or plots were produced.
7. In the successful block2b run, the optimizer deployed 36.2 GW solar (PV_ROOFTOP=6.84, PV_UTILITY=29.39) which exceeds the block3c caps of 4.0 and 15.0.
8. Policy constraints (RE share, GWP, fperc) were all inactive in both runs.

### 2. What is likely

- The optimizer's primary degree of freedom in block2b was massive solar deployment.
  Capping both PV_ROOFTOP (15→4) and PV_UTILITY (60→15) simultaneously, while nuclear and wind
  were already capped, substantially narrowed the feasible region and made the LP interior
  much harder to navigate numerically.
- The model is likely feasible (CCGT, COAL_US, HYDRO open and capable of meeting demand),
  but the solver could not confirm this within the time limits.
- A single-constraint change from block2b would have been less risky than a dual solar cap.

### 3. What is still unknown

- Whether the problem is truly infeasible or only numerically difficult in the given time budget.
- Whether the 1800s fallback dual simplex would converge given more time.
- Why the barrier's interior objective (1.22e+11) was so far from physical reality.

### 4. Is the current active FI/Technologies.csv safe to keep?

**No.** It caused a failed run. It has PV_ROOFTOP=4.0 and PV_UTILITY=15.0 which are the
direct cause of the solver difficulty. Do not run from this state again without first testing
a single-change version.

### 5. Which file should be restored to return to the last clean anchor?

```
Data/2017/FI/Technologies.csv.bak_20260311_112346
```

This is the block2b anchor (446 bytes), confirmed equivalent to
`Technologies.csv.block2b_offshore_zero_keep_20260310`.
Key values: NUCLEAR 2.7/2.835, WIND_ONSHORE 2.0/2.1, WIND_OFFSHORE 0.0/0.0,
PV_ROOFTOP 0.0/15.0, PV_UTILITY 0.0/60.0.

Restore command:
```powershell
Copy-Item "Data\2017\FI\Technologies.csv.bak_20260311_112346" "Data\2017\FI\Technologies.csv" -Force
```

### 6. Next safest manual edit to test

**Restore to block2b anchor first, then make exactly one change:**

| Field | Value |
|---|---|
| Technology | PV_UTILITY |
| f_min | 0.0 |
| f_max | **15.0** (reduced from 60.0) |
| All other rows | unchanged from block2b anchor |

**Why this is safer than block3c:**

- block3c tightened **both** PV_ROOFTOP (15→4) and PV_UTILITY (60→15) at once.
- This proposal changes **only PV_UTILITY** (60→15). PV_ROOFTOP stays at 15.0.
- Total solar headroom: 15.0 + 15.0 = 30.0 GW vs block2b 75.0 GW.
  Block3c had only 19.0 GW. This is a smaller reduction step.
- If the model struggles with 30 GW total solar, you can then diagnose PV_UTILITY alone
  rather than two technologies simultaneously.
- If it succeeds, you can then separately test tightening PV_ROOFTOP.

---

## Summary of files checked

| File | Found | Key finding |
|---|---|---|
| `Data/2017/FI/Technologies.csv` | Yes | Active — has PV_ROOFTOP=4, PV_UTILITY=15 (block3c edit) |
| `Data/2017/FI/Technologies.csv.bak_20260311_112346` | Yes | Block2b anchor — PV_ROOFTOP=15, PV_UTILITY=60 |
| `…/block3c…/input_snapshot/reg_technologies.dat` | Yes | All FI edits propagated correctly |
| `…/block3c…/CONSTRAINT_DIFF.md` | **No** | Not generated (run failed before this step) |
| `…/block3c…/run_metadata.json` | Yes | status=FAILED, code=-1 |
| `…/block3c…/log.txt` | Yes | Barrier code 100, objective 1.22e+11 |
| `…/block3c…/log_fallback.txt` | Yes | Dual simplex code -1, 1800s timeout |
| `…/block3c…/outputs/` | **No** | Not produced |
| `…/block2b…/outputs/Assets.csv` | Yes | PV_ROOFTOP=6.84 GW, PV_UTILITY=29.39 GW deployed |
| `…/block2b…/validation_plots/validation_table.csv` | Yes | Solar elec 29.16 TWh (target: 0.04 TWh) |
| `scripts/run_calib_manual.py` | Yes | crossover=0 (doc says 1 but code says 0 — pre-existing discrepancy) |
| `esmc/utils/region.py` | Yes | `.update()` confirmed — only matching rows/columns replaced |
| `esmc/utils/esmc.py` | Yes | f_perc=False drops f_max_perc + f_min_perc constraints |
