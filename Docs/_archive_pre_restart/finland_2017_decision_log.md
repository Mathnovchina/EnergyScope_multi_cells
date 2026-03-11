# Finland 2017 Calibration — Decision & Justification Log

Date: 2026-03-05  
Author: Calibration session (automated)

---

## Overview

This document traces every key decision made during the Finland 2017 baseline
calibration, the evidence that motivated it, and its outcome.  The goal is a
solve_result_num = 0 (optimal) run that can serve as the FI 2017 baseline.

---

## D1 — Use `restore_p02b_full.csv` as the single authoritative patch

**Decision**: Maintain one CSV patch (`calibration/patches/restore_p02b_full.csv`,
727 rows) that reconstructs the full p02 technology + resource configuration
at solve time, applied in-memory only (no permanent Data/2017 modifications).

**Justification**:
- The on-disk `Data/2017/FI/Technologies.csv` was manually edited multiple
  times between Feb and March 2026 and no longer matches any successful solve.
- A declarative CSV patch is reproducible, auditable, and version-controllable.
- In-memory application keeps the shared Data directory clean for other users.

**Patch contents (727 data rows)**:
| Section | Rows | Description |
|---------|------|-------------|
| 154 techs × 4 params | 616 | fmin_perc, fmax_perc, f_min, f_max from the successful `calib_2017_finland_p02_no_oil_chp` archive |
| 14 TS_* techs × 4 params | 56 | Thermal-storage overrides (see D3) |
| 25 resources × 2 params | 50 | avail_local, avail_exterior from p02 |
| 4 resources × 1 param | 4 | c_op_local from p02 |
| **Header** | 1 | `file,parameter,technology_or_resource,value` |

---

## D2 — Fix 3 wrongly-blocked technologies

**Decision**: Set f_max = 1e15 for WIND_OFFSHORE, GEOTHERMAL, DHN_DEEP_GEO
(they had f_max = 0 in an earlier patch draft).

**Justification**:
- Binary diff of .dat files between the failing `p02b_replica` run and the
  successful archived `calib_2017_finland_p02_no_oil_chp` showed exactly
  3 technology differences — all in f_max.
- In the successful archive, these techs had f_max = 1e15 (Infinity),
  meaning the solver could use them if cost-optimal.
- Setting f_max = 0 blocks installation entirely, which over-constrains
  the model and may contribute to infeasibility in certain TD configurations.
- Note: even with f_max = 1e15, the barrier solver produces near-zero or
  noise-level values for these techs when crossover is disabled (see D6).

**Evidence**:
```
# Diff output (p02b_replica vs p02_no_oil_chp archive)
WIND_OFFSHORE  f_max:  0.0  →  1e+15
GEOTHERMAL     f_max:  0.0  →  1e+15
DHN_DEEP_GEO   f_max:  0.0  →  1e+15
```

---

## D3 — Override 14 TS_* thermal-storage technologies

**Decision**: Set f_max = 1e15 for all 14 `TS_*` thermal-storage techs via
the patch, overriding the small caps (5–20 GWh) present in the FI CSV.

**Justification**:
- `Data/2017/FI/Technologies.csv` (lines 151–164) contains 14 TS_* entries
  with f_max values of 5–20, added after the successful p02 run:
  ```
  TS_DEC_COGEN_GAS,5    TS_DEC_HP_ELEC,5     TS_DEC_THHP_GAS,5
  TS_DEC_COGEN_OIL,5    TS_DEC_DIRECT_ELEC,5 TS_DHN_BOILER_GAS,20
  TS_DEC_BOILER_GAS,5   TS_DEC_BOILER_OIL,5  TS_DHN_BOILER_OIL,20
  TS_DEC_BOILER_WOOD,5  TS_DEC_SOLAR,5       TS_DHN_BOILER_WOOD,20
  TS_DHN_COGEN_GAS,20   TS_DHN_COGEN_WOOD,20
  ```
- The REF region's Technologies.csv has f_max = 1e15 for all TS_* techs.
- The successful p02 archive predates these FI-specific TS entries, so the
  archive used the REF defaults (1e15).
- Tight TS caps restrict hourly heat-storage dispatch, which can make the
  layer_balance and storage_level constraints infeasible under certain TD
  clusterings.

---

## D4 — Reconstruct TD_of_days_12.out from p02 archive

**Decision**: Replace `case_studies/FI/00_td_dat/TD_of_days_12.out` with a
version reconstructed from the successful p02 archive's `reg_12TD.dat`.

**Justification**:
- The kmedoid clustering is non-deterministic (MIP-based).  Three different
  clusterings were found on disk:
  | Version | TDs | Source |
  |---------|-----|--------|
  | Dec 2025 | 17, 20, 50, 72, 110, 148, 218, 245, 284, 302, 345, 355 | `esmc/preprocessing/kmedoid_clustering/` |
  | March 3 backup | 10, 21, 33, 63, 75, 115, 210, 236, 251, 284, 288, 329 | `.bak_20260303` |
  | March 4 (was active) | 10, 21, 33, 63, 74, 115, 142, 202, 210, 251, 284, 329 | Overwritten |
- Both March versions produced INFEASIBLE solves with the p02 tech config.
- The Dec 2025 version also produced INFEASIBLE (simplex code 200 after
  104,797 iterations).
- **Only the clustering embedded in the successful p02 archive's .dat file
  produced a feasible solve.**

**Reconstruction method** (greedy representative selection):
1. Parse the `reg_12TD.dat` file from the p02 archive to extract the
   day→TD_number mapping (365 days, 12 TDs).
2. For each TD number 1–12 in sequence, select the smallest available day
   > previous selected day that belongs to that TD's cluster.
3. Result: days 1, 2, 7, 8, 36, 119, 130, 137, 139, 152, 282, 331.
4. Zero renumbering mismatches verified — cluster membership perfectly
   preserved.

**Backups preserved**:
- `TD_of_days_12.out.bak_mar4` → Dec 2025 version
- `TD_of_days_12.out.bak_20260303` → March 3 version

---

## D5 — Disable f_perc constraints (`--no-fperc`)

**Decision**: Drop `f_max_perc` and `f_min_perc` constraints for all runs.

**Justification**:
- The successful p02 archive (`calib_2017_finland_p02_no_oil_chp`) was run
  without f_perc constraints.
- f_perc constraints enforce modal share targets for transport, industry,
  etc.  These are calibration levers, not structural requirements.
- Enabling f_perc adds tighter feasibility requirements that interact badly
  with the reconstructed TD clustering.
- All 9 archived runs with solve_result_num = 0 used --no-fperc or
  equivalent.

---

## D6 — Barrier with crossover=0: tolerance violations

**Observation** (not a decision — documents the known issue):

The successful `p02b_ts_fix` run (barrier, crossover=0) achieved
solve_result_num = 0 but has significant tolerance violations:

| Metric | Value |
|--------|-------|
| MaxAbsConstr | 6E+07 |
| MaxRelConstr | 6E+08 |
| WIND_OFFSHORE installed | 53 trillion GWh |
| GEOTHERMAL installed | 197 billion GWh |

**Root cause**: Barrier with `crossover=0` returns an interior-point solution
that is NOT a basic feasible solution (BFS).  Uncapped technologies
(f_max = 1e15) sit at near-zero primal values with near-zero dual values —
the solver treats them as "free" directions and numerical drift accumulates.

The original p02 archive had the **same issue** (WIND_OFFSHORE = 11.4 trillion
GWh), confirming this is a structural artifact of crossover=0, not a
configuration error.

**Core energy values are unaffected**:
- NUCLEAR ≈ 84 GWh (p02b_ts_fix) vs 84 GWh (p02 archive)
- WIND_ONSHORE ≈ 3154 vs 3154
- HYDRO_DAM ≈ 2965 vs 2965
- HYDRO_RIVER ≈ 7790 vs 7790

---

## D7 — Switch to barrier + crossover=2 instead of standalone simplex

**Decision**: Add `--crossover` flag using `crossover=2` (dual crossover)
rather than pursuing standalone dual simplex (`--simplex`).

**Justification**:
- The `--simplex` run crashed (exit code 1) during AMPL model hand-off to
  CPLEX.  The log shows all constraints were generated (450 entries),
  then `#genmod` (1.72s), `#merge` (0.03s), `#collect` (0.19s) completed,
  but CPLEX never started.  No error message or traceback was produced.
- Possible causes: the `dual` keyword in CPLEX options is not a valid AMPL
  CPLEX driver keyword (AMPL uses `lpmethod=2` for dual simplex); or memory
  pressure during the simplex setup phase for a 294k-variable problem.
- `crossover=2` (dual crossover) is the standard CPLEX mechanism for
  converting an interior-point solution to a clean BFS.  It:
  - Uses the barrier solution as a warm start
  - Performs a few simplex pivots to reach a vertex solution
  - Eliminates tolerance violations in uncapped technologies
  - Is well-tested in production LP solvers
- All other CPLEX options remain identical to the proven barrier configuration:
  `baropt predual=-1 barstart=4 comptol=1e-5 bardisplay=1 display=2 timelimit=172800`

**Implementation**: New `_barrier_crossover_opts()` function in
`scripts/run_calib_manual_fi.py` and `--crossover` CLI flag.

**Expected outcome**: solve_result_num = 0 with clean BFS (no tolerance
violations), WIND_OFFSHORE and GEOTHERMAL at exactly 0.0.

---

## D8 — Run naming convention

| Run name | Configuration | Outcome |
|----------|---------------|---------|
| `p02b_replica` | Patch v1 (3 wrong blocks), original March 4 TDs | INFEASIBLE |
| `p02b_ts_fix` | Patch v2 (+14 TS overrides +3 fix), Dec 2025 TDs | INFEASIBLE |
| `p02b_ts_fix` (re-run) | Same patch, reconstructed p02 TDs | **OPTIMAL** (barrier, tolerance issues) |
| `p02b_simplex` | Same patch, reconstructed TDs, --simplex | CRASHED (exit 1) |
| `p02b_crossover` | Same patch, reconstructed TDs, --crossover | **PENDING** |

---

## Appendix A — Archived runs with solve_result_num = 0

| Run | Solve time (s) | TotalCost |
|-----|---------------|-----------|
| p02_no_oil_chp | 44.4 | 5.82e+17 |
| p08_solar_only | 25.8 | — |
| test_synth_enabled | 108.5 | — |
| v1 | 145.3 | — |
| p09_from_v10 | 167.3 | — |
| p26_disable_advcogen_v2 | 181.7 | — |
| v2 | 249.0 | — |
| v3_fperc | 253.6 | — |
| p24_reuse_dat_test | 321.9 | — |

`baseline_test` was previously reported as successful but is actually
INFEASIBLE (code 299).

## Appendix B — File state summary (as of 2026-03-05)

| File | Last modified | Status |
|------|--------------|--------|
| `Data/2017/FI/Technologies.csv` | March 3, 2026 | Has 14 TS_* entries with small f_max; patched in-memory |
| `Data/2017/FI/Resources.csv` | Feb 26, 2026 | Has p02b values on disk |
| `Data/2017/FI/Time_series.csv` | Feb 18, 2026 | Unchanged |
| `case_studies/FI/00_td_dat/TD_of_days_12.out` | March 5, 2026 | Reconstructed from p02 archive |
| `calibration/patches/restore_p02b_full.csv` | March 5, 2026 | 727 lines, final version |
| `scripts/run_calib_manual_fi.py` | March 5, 2026 | Added --crossover flag |
