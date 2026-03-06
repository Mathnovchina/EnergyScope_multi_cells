# Manual Run Workflow — Finland 2017 (FI-only)

## What is this?

`scripts/run_calib_manual.py` is a single-country calibration runner for
Finland 2017.  It follows the same ESMC pipeline as `run_calib_case.py` but
adds: input snapshoting, in-memory patches, automatic scoring, validation
plots, and metadata tracking.

**Data/2017/ is never modified.**

## Quick start

```bash
# Baseline (no patches, f_perc=True, crossover=1)
python scripts/run_calib_manual.py -n baseline

# With a patch
python scripts/run_calib_manual.py -n test_nuclear \
    -p calibration/patches/nuclear_cap.csv

# Dry-run (preview patch diffs, no solve)
python scripts/run_calib_manual.py -n preview \
    -p calibration/patches/nuclear_cap.csv --dry-run

# Disable fmin_perc / fmax_perc
python scripts/run_calib_manual.py -n no_fperc --no-fperc

# Force dual simplex (for infeasibility diagnosis)
python scripts/run_calib_manual.py -n diag_simplex --solver simplex
```

## Config defaults

| Parameter | Default | Flag |
|-----------|---------|------|
| `f_perc` | `True` | `--no-fperc` to disable |
| `gwp_limit_overall` | `None` | `--gwp-limit <val>` |
| `re_share_primary` | `None` | `--re-share <val>` |
| `nbr_td` | `12` | `--nbr-td <val>` |
| `solver` | `barrier` | `--solver simplex` |

## Output layout

```
case_studies/FI/manual_runs/<YYYYMMDD_HHMMSS>__<name>/
  outputs/                  # ESMC result CSVs (Resources, Year_balance, …)
  input_snapshot/           # frozen .dat files for reproducibility
  validation_plots/         # pe/elec/co2/error charts + validation_report.md
  patch_applied/            # copies of patch CSVs + diff_summary.txt
  run_metadata.json         # config, score, solve info, git commit
  run_notes.md              # template for your observations
  log.txt                   # AMPL/CPLEX primary solver log
  log_fallback.txt          # (only if fallback was triggered)
```

## Solver strategy

The script uses **barrier + crossover=1** (NOT the old ESMC default of
crossover=0, which caused tolerance violations with f_perc=True).
If the solve returns an ambiguous status (code -1 or 100–199), it retries
**once** with dual simplex.  Both logs are saved.

| Code | Meaning |
|------|---------|
| 0 | Optimal — results are reliable |
| -1 | Unknown (barrier interior) — triggers fallback |
| 200–299 | Infeasible — check log for conflicting constraints |
| 400–499 | Limit reached (time/iterations) |

## Scoring

Each successful solve is scored against `calibration/reality/finland_2017_reference.csv`
using weighted absolute percentage error (14 metrics, same as `score_all_fi_runs.py`).

The row is appended/updated in `calibration/run_rankings.csv`.

### Score all runs at once

```bash
python scripts/score_all_fi_runs.py                     # top-level only
python scripts/score_all_fi_runs.py --include-archive   # include archives
python scripts/score_all_fi_runs.py --top 10 -v         # verbose top 10
```

### Typical score ranges

- **40–50**: Good calibration (v9, v10)
- **100–160**: Vanilla baseline without patches
- **10000+**: Tolerance violation or broken run

## Patch format

Create a CSV with columns: `file`, `parameter`, `technology_or_resource`, `value`.

```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_max,NUCLEAR,8000
Technologies.csv,fmin_perc,IND_BOILER_WOOD,0.25
Resources.csv,avail_local,COAL,50000
```

Patches are applied **in-memory** after `init_regions()`.  The original
`Data/2017/FI/` files are never touched.  Copies of applied patches are
saved in `patch_applied/` with a `diff_summary.txt` showing old → new values.

## Data safety rules

1. **Data/ is NEVER modified** — all patches apply to in-memory DataFrames
2. **Input snapshots** are saved in each run's `input_snapshot/` directory
3. **Patches** are copied to `patch_applied/` with a diff summary
4. Each run is fully self-contained and reproducible from its snapshot
old→new diffs is written to the run folder.

## Comparing runs

```bash
# Visual comparison
python scripts/validate_run.py --runs baseline_ok test_nuclear

# Tabular comparison
# Open calibration/run_rankings.csv — sorted by ascending score
```

## CLI reference

| Flag | Default | Description |
|------|---------|-------------|
| `--run-name` / `-n` | (required) | Output folder name |
| `--patch` / `-p` | none | Patch CSV (repeatable) |
| `--description` / `-d` | "" | Human note in metadata |
| `--dry-run` | false | Preview patches, no solve |
| `--no-fperc` | false | Disable percentage constraints |
| `--gwp-limit` | None | GWP cap (ktCO2/y) |
| `--re-share` | None | Min RE share |
| `--nbr-td` | 12 | Typical days |
| `--skip-plots` | false | Skip validation charts |
