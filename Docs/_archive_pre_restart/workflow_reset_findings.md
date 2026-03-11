# Workflow Reset Findings

Date: 2026-03-05  
Purpose: Audit of all Docs/ + conversation history → actionable status report.

---

## 1. Document Status Summary

### Authoritative (still correct)
- **manual_run_fi.md** — documents `run_calib_manual_fi.py` (the FI-only runner)
- **recalibration_restart_plan.md** — defines non-negotiable rules (no Data/ edits, input snapshots, scoring every run)
- **finland_2017_calibration_dossier.md** — single source of truth for data sources, overrides, known limitations
- **finland_2017_reality_reference_audit.md** — maps 26 reality metrics to model outputs
- **restore_v5_fperc_to_Data2017.md** — verified .dat→CSV reconstruction log
- **validate_run.py** — current plotter (491 lines), produces pe/elec/co2/error charts

### Outdated or contradictory
- **manual_calibration_workflow.md** — references old 713-line script version; commands will fail
- **calibration_strategy_v6.md** — all "current" values are stale (FI Resources.csv drifted to 1e15 defaults); DO NOT EXECUTE without re-baselining
- **finland_2017_end_of_day_review.md** — session notes from March 2; useful context but not current

### DANGEROUS (modify shared Data/)
- **workflow_mess_diagnosis.md** — describes past damage from .dat regeneration bug and unsolicited copilot runs
- **calibration_strategy_v6_audit.md** — exposes 10+ critical errors in v6 strategy; phantom DHN_BOILER_COAL
- **finland_2017_decision_log.md** — rewrites TD_of_days_12.out directly; in-memory patch approach for Data/ but TD file is persistent

---

## 2. What Broke and When

### Root cause chain
1. **TD clustering non-determinism**: The kmedoid MIP re-clustered on March 4, producing a different TD mapping than the one used for successful solves. Three distinct clusterings found on disk — only the one embedded in the p02 archive produced feasible solves.
2. **Data/2017/FI drift**: Technologies.csv was manually edited multiple times (Feb→March). 14 TS_* thermal-storage techs with tight f_max caps (5–20 GWh) were added post-p02, making the model infeasible under many TD clusterings.
3. **crossover=0 default**: ESMC's default CPLEX option `crossover=0` produces interior-point solutions, not basic feasible solutions. For large-scale constraints (fmin_perc at ~1e5 GWh), barrier tolerance of 1e-5 → ~10 GWh violations → `solve_result_num = -1` ("unknown").
4. **Unsolicited autonomous runs**: Runs p22–p30 created by Copilot without user request, cluttering the workspace.

### "Baseline no-patch run" stopped working because:
- Technologies.csv accumulated TS_* overrides that conflict with the frozen TD clustering
- Resources.csv drifted from calibrated values to 1e15 defaults for fossils
- `crossover=0` always risks returning code -1 with f_perc=True active

### Observed solve codes
| Code | Meaning | Observed in |
|------|---------|-------------|
| 0 | Optimal | 16 runs (calib_2017_finland, v1–v10, p02, p04, p08, p09, p24, ref_2017) |
| -1 | Unknown/interior | 8+ runs (baseline_nopatch, p02b_replica, manual_runs baselines) |
| 200 | Infeasible (simplex) | p02b_crossover (crossover=2 failed during simplex cleanup) |
| 299 | Infeasible (presolve) | p10, p11, p12, test_share_ned_fix_v2 |
| 999 | Failure | p02b_crossover (time/resource limit) |

### Repeated pitfalls
- **Patching shared Data/**: Any CSV edit under Data/2017/ is invisible to runs that already generated .dat files, and corrupts reproducibility for future runs.
- **f_perc behavior**: `f_perc: False` silently drops ALL percentage constraints. `f_perc: True` (the default) keeps them, but the solver must handle scale issues (~1e5 GWh sectors).
- **Solver instability**: barrier+crossover=0 → code -1 with f_perc constraints. barrier+crossover=2 → infeasible during crossover. standalone `dual` simplex → crash during model hand-off to CPLEX.

---

## 3. Script State

### `scripts/run_calib_manual.py` (638 lines) — GOOD, nearly complete
- Already uses `case_studies/FI/manual_runs/<timestamp>__<name>/`
- Default: barrier + crossover=1 (the correct setting)
- Has: `--no-fperc`, `--dry-run`, `--data-dir`, `--solver`, `--skip-plots`, `--nbr-td`
- In-memory patches only, input snapshots saved
- Scores runs, appends to ranking CSV, generates validation plots
- One fallback allowed (barrier → dual simplex on code -1 or 100–199)

### `scripts/run_calib_manual_fi.py` (~420 lines) — OLDER FI-only runner
- Created during prior session; uses `case_studies/FI/<run_name>/` (no manual_runs prefix)
- Default: barrier + crossover=0 (the problematic setting, later amended with --crossover flag)
- Has accumulated many session-specific hacks (TS overrides, etc.)
- **SUPERSEDED** by `run_calib_manual.py` which has the correct crossover=1 default

### `scripts/validate_run.py` (491 lines) — GOOD
- Standalone plotter; produces pe_comparison.png, elec_comparison.png, error_chart.png, co2_comparison.png, chp_cond_breakdown.png, plus markdown report
- Called by run_calib_manual.py post-solve

### `scripts/score_all_fi_runs.py` — NEEDS CREATION
- Does not exist yet. Run_rankings.csv was populated by individual run scripts, not a batch scanner.

---

## 4. Current Data/2017/FI State

| File | Status |
|------|--------|
| Technologies.csv | **DRIFTED** — has 14 TS_* entries with f_max=5–20 not present in any successful run; phantom DHN_BOILER_COAL |
| Resources.csv | **DRIFTED** — fossil avail_exterior may be at 1e15 defaults, not calibrated caps |
| Time_series.csv | Unchanged since Feb 18, 2026 |
| Demands.csv | Unchanged since Feb 18, 2026 |
| Misc.json | Modified March 2, 2026 |

---

## 5. Actionable Next Steps

1. **DO NOT TOUCH** Data/2017/ — use `--data-dir` or patches instead
2. **Use `run_calib_manual.py`** (not `run_calib_manual_fi.py`) — it has crossover=1 default
3. **Create `score_all_fi_runs.py`** to batch-scan all existing runs
4. **Test baseline run**: `python scripts/run_calib_manual.py -n baseline` with no patches, f_perc=True (default), crossover=1 (default)
5. **If baseline fails with code -1**: the Data/2017 state is incompatible with f_perc=True; will need a patch or alternate data profile
6. **Archive** all runs with missing outputs, code 299, or code -1 with known tolerance issues
7. **Key risk**: No existing run with f_perc=True achieved solve_result_num=0 and clean outputs simultaneously. The 16 successful runs used either f_perc=False or crossover=0 (producing tolerance artifacts).
