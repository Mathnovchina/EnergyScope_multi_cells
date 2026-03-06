# Recalibration Restart Plan — Finland 2017

*Generated: 2025-06-13. This document is the single reference for restarting the calibration workflow from a clean state.*

---

## 1. What Changed (Summary of Fixes)

### 1.1 Solver: `crossover=0` → `crossover=1`

**Root cause of ALL `solve_result_num = -1` failures:**
The old ESMC default in `esmc/utils/esmc.py` line 684 was `crossover=0`, which tells CPLEX barrier to skip simplex crossover. The barrier solution is *interior* to the feasible polytope — for most constraints (simple bounds, balance equations) this is harmless. But for `fmin_perc` constraints, which compare technology output against total sector output (~1e5 GWh), a 0.01% barrier tolerance translates to ~10 GWh violation. CPLEX reports this as `solve_result_num = -1` (unknown/failure) with MaxAbs variable-bound violations of 1e2 and algebraic-constraint violations of 1e5.

**Fix:** `run_calib_manual.py` now uses `crossover=1` as the default CPLEX option. After barrier converges, CPLEX runs simplex crossover to find a basic feasible solution (vertex) that satisfies all constraints exactly. This should produce `solve_result_num = 0` for any feasible model.

**Fallback:** If barrier+crossover still fails (code -1 or 100-199), the script automatically retries with dual simplex, which provides a clear infeasibility certificate if the model is truly infeasible.

> **Note:** The ESMC framework default (`esmc/utils/esmc.py`) was NOT modified. The fix lives entirely in `run_calib_manual.py`'s custom `ampl_options`.

### 1.2 Input Snapshot

Every run now saves a frozen copy of all `.dat` files to `run_dir/input_snapshot/`. This means:
- Even if `Data/2017/` CSVs change later, you can see exactly what was fed to AMPL
- You can diff two runs' inputs: `diff run_A/input_snapshot/ run_B/input_snapshot/`

### 1.3 Data Safety

`Data/2017/` is **NEVER modified** by `run_calib_manual.py`. All patches are applied to in-memory DataFrames after `init_regions()`. The `.dat` files are generated from those DataFrames, never from the CSV files directly.

### 1.4 Script Cleanup

- `run_calib_manual.py` rewritten from 592 lines to ~490 lines
- Removed: `--simplex` (broken AMPL MP option syntax), cloning mechanism, CSV backup/restore, `--reuse-dat`
- Added: `--solver {barrier,simplex}`, `--data-dir`, `--skip-plots`, input snapshot, automatic fallback
- Style aligned with `run_esmc_simple_3c 1.py` (simple linear pipeline, no cloning)

---

## 2. Baseline Command

The ONE command to verify that the tooling works:

```bash
python scripts/run_calib_manual.py -n baseline
```

This runs with:
- Standard `Data/2017/` inputs (no patches)
- `f_perc=True` (fmin_perc/fmax_perc constraints active)
- 12 typical days (read from frozen `TD_of_days_12.out`)
- Barrier + crossover=1 solver
- Automatic scoring against 14 reality targets
- Validation plots (PE, Elec, CO2, error chart, markdown report)

**Expected outcome:** `solve_result_num = 0` (optimal). If this fails, the model itself (Data/2017 bounds + resources) is genuinely infeasible and needs patch work.

---

## 3. Patch Workflow

Once the baseline produces `solve_result_num = 0`:

### 3.1 Create a Patch File

```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_max,NUCLEAR,8000
Technologies.csv,fmin_perc,DHN_COGEN_GAS,0.05
Resources.csv,avail_local,COAL,50000
```

Save to `calibration/patches/my_patch.csv`.

### 3.2 Dry-Run to Verify

```bash
python scripts/run_calib_manual.py -n test_patch \
    -p calibration/patches/my_patch.csv --dry-run
```

This shows what would change without running the model.

### 3.3 Run with Patch

```bash
python scripts/run_calib_manual.py -n test_patch \
    -p calibration/patches/my_patch.csv \
    -d "Testing nuclear and CHP bounds"
```

### 3.4 Compare Scores

```bash
python scripts/score_all_fi_runs.py --verbose
```

Or check `calibration/run_rankings.csv` directly.

### 3.5 Validate

```bash
python scripts/validate_run.py --run-name <run_folder_name>
```

---

## 4. Scoring System

**14 metrics** compared against Finland 2017 reality (from `calibration/reality/finland_2017_reference.csv`):

| Category | Metrics | Source |
|----------|---------|--------|
| Primary Energy | Biomass, Oil, Gas, Coal, Nuclear, Hydro, Wind | Statistics Finland 2019 |
| Electricity | Nuclear, Hydro, Wind, CHP, Condensation, Solar | Statistics Finland 2019 |
| Emissions | CO2 | UNFCCC 2017 inventory |

**Score formula:** Weighted average of absolute percentage errors. Lower = better. Weights reflect importance and confidence in reality data.

**Best scores achieved so far:**
| Run | Score | Notes |
|-----|-------|-------|
| v9 | 39.2% | Best overall, recommended starting point |
| v10_oil_constr | 39.2% | Oil constraint variant |
| calib baseline | 42.1% | Best CO2 + oil match |

---

## 5. Archiving

To clean up failed/empty runs:

```bash
# Archive all empty runs (no outputs/)
python scripts/archive_runs.py --empty

# Archive all failed runs (solve_result_num != 0)
python scripts/archive_runs.py --failed

# Archive specific runs
python scripts/archive_runs.py p26 p27 p28_clean_baseline

# Dry-run first
python scripts/archive_runs.py --empty --dry-run
```

Archived runs go to `case_studies/FI/_archive_YYYYMMDD/` with a README.

---

## 6. File Inventory

### Scripts (active)
| File | Purpose |
|------|---------|
| `scripts/run_calib_manual.py` | **Main calibration runner** — baseline + patches |
| `scripts/validate_run.py` | Validation plots (6 outputs per run) |
| `scripts/score_all_fi_runs.py` | Batch scorer, writes `run_rankings.csv` |
| `scripts/archive_runs.py` | Archive broken/empty runs |
| `scripts/compare_dat_bounds.py` | Diagnostic: diff .dat files between runs |

### Data
| Path | Purpose |
|------|---------|
| `Data/2017/` | Standard data profile (166 tech rows) |
| `Data/2017_alt_from2035tech/` | Alternative profile (20 tech rows, no fperc) |
| `calibration/reality/finland_2017_reference.csv` | Reality targets (26 rows, single source of truth) |
| `calibration/run_rankings.csv` | Score leaderboard |
| `calibration/patches/` | Patch files for manual experiments |

### Run Outputs
Each run in `case_studies/FI/manual_runs/<timestamp>__<name>/` contains:
```
outputs/              — Resources.csv, Year_balance.csv, Gwp_breakdown.csv, ...
input_snapshot/       — Frozen .dat files (exact AMPL inputs)
validation_plots/     — pe_comparison.png, elec_comparison.png, ...
run_metadata.json     — Config, patches, score, git commit, command
log.txt               — AMPL/CPLEX solver log
```

---

## 7. Known Technical Issues

### 7.1 Data/2017 Drift from Frozen Baselines
The current `Data/2017/FI/Technologies.csv` has 179 parameter differences across 152 technologies compared to the frozen baseline `.dat` files. Most changes are tighter `f_max` bounds (from infinity to 5-100 GW). Resource availability also decreased (LFO -47%, JET_FUEL -67%, GAS -21%, COAL -30%, URANIUM -38%).

These changes are *intentional* tightenings from the calibration process but may make the model tighter than needed. If the baseline command fails, the first thing to check is whether these bounds are too restrictive.

### 7.2 PEAT Limitation
Finland's PEAT consumption (~14 TWh) is lumped into COAL in the ESMC model because there is no separate PEAT resource. This is documented in `finland_2017_reality_reference_audit.md`.

### 7.3 CHP Double-Counting Risk
The CHP reality target (20.735 TWh) covers all cogeneration electricity. The model has 13 CHP technology types. When comparing, ensure you include all of them (the scoring code does this correctly).

### 7.4 f_perc=False Trap
Using `--no-fperc` disables ALL `fmin_perc` and `fmax_perc` constraints. This makes any `fmin_perc`/`fmax_perc` values in Technologies.csv inert. Only use `--no-fperc` if you explicitly want to ignore percentage-based technology bounds.

---

## 8. Rules for Future Sessions

1. **NO autonomous runs.** Copilot makes tooling; user runs the model.
2. **NO permanent Data/2017 modifications.** Only in-memory patches.
3. **ONE baseline command must work.** If `python scripts/run_calib_manual.py -n baseline` fails, fix the tooling first.
4. **Every run gets a score.** No exceptions. Check `run_rankings.csv`.
5. **Input snapshots are mandatory.** Every run's `.dat` files are frozen.
6. **Archive broken runs.** Don't let `case_studies/FI/` accumulate garbage.
