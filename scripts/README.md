# Scripts Directory

> EnergyScope Multi-Cells — Finland 2017 Calibration Scripts  
> Last updated: 2026-03-04

This directory contains scripts for running and analyzing Finland 2017 calibration runs.

---

## Quick Start

```bash
# 1. Score ALL calibration runs (100% coverage)
python scripts/score_all_fi_runs.py

# 2. Run manual calibration with a patch (safe, in-memory patching)
python scripts/run_calib_manual.py -n my_test --patch calibration/patches/p01_disable_futuretechs.csv

# 3. Dry run (preview patches without running the model)
python scripts/run_calib_manual.py -n my_test --patch calibration/patches/p01_disable_futuretechs.csv --dry-run

# 4. Generate validation plots for all kept baselines
python scripts/validate_run.py --batch

# 5. Validate a single run
python scripts/validate_run.py --run-dir case_studies/FI/calib_2017_finland_v9
```

---

## Active Scripts (Recommended)

### Core Workflow

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_calib_manual.py` | **Manual calibration runner** — applies patches in-memory via ESMC framework, auto-scores | `python run_calib_manual.py -n test -p patch.csv` |
| `validate_run.py` | **Validation plotter** — generates PE/elec/CO2 charts + error analysis + markdown report per run | `python validate_run.py --batch` |
| `score_all_fi_runs.py` | **Score ALL runs** — scans case_studies/FI/, writes run_rankings.csv with 100% coverage | `python score_all_fi_runs.py` |
| `score_calib_runs.py` | Legacy scoring (less complete, kept for reference) | `python score_calib_runs.py` |

### Reference Scripts (read-only, do not modify)

| Script | Purpose |
|--------|---------|
| `run_esmc_simple_3c 1.py` | Canonical ESMC workflow example (3-country, by P. Thiran) |
| `run_esmc.py` | Multi-case ESMC runner (reference for data modification patterns) |

### Block Calibration (v6/v7)

| Script | Purpose |
|--------|---------|
| `apply_v6_blocks.py` | Apply v6 calibration blocks |
| `apply_v7_blockA.py` | Apply v7 block A |
| `build_v6_block0.py` | Build v6 baseline block |
| `plot_v6_blocks.py` | Plot v6 block results |
| `compare_v6_blocks.py` | Compare v6 blocks |

---

## Directory Structure

```
scripts/
├── run_calib_manual.py     # ★ Manual calibration runner (ESMC framework, in-memory patches)
├── validate_run.py         # ★ Validation plotter (PE/elec/CO2 charts + report)
├── score_all_fi_runs.py    # ★ Score ALL runs with 100% coverage
├── score_calib_runs.py     # Legacy scoring (22 runs only)
├── run_esmc_simple_3c 1.py # Reference ESMC workflow (read-only)
├── run_esmc.py             # Reference multi-case runner (read-only)
├── _archive_20250613/      # Archived old scripts (including old run_calib_manual.py)
├── advanced/               # Advanced/experimental scripts
└── archive/                # Legacy scripts (85+ files)
```

---

## Output Locations

| Output Type | Location |
|-------------|----------|
| **New manual runs** | `case_studies/FI/manual_runs/<timestamp>__<name>/outputs/` |
| **Validation plots** | `case_studies/FI/<run>/validation_plots/` |
| Legacy run results | `case_studies/FI/calib_2017_finland_*/outputs/` |
| Run rankings | `calibration/run_rankings.csv` |
| Reality reference | `calibration/reality/finland_2017_reference.csv` |
| Archived runs | `case_studies/FI/_archive_20260304/` |
| Baseline notes | `case_studies/FI/baseline_notes.md` |

---

## Creating Patches

Patch files are CSVs with columns:
- `file`: Target file name (e.g., `Technologies.csv`)
- `parameter`: Column to modify (e.g., `f_max`)
- `technology_or_resource`: Row identifier (e.g., `NUCLEAR`)
- `value`: New value

Example `calibration/patches/force_coal.csv`:
```csv
file,parameter,technology_or_resource,value
Technologies.csv,fmin_perc,DHN_COGEN_COAL,0.2
Technologies.csv,fmin_perc,COAL_US,0.1
Resources.csv,avail_exterior,COAL,50000
```

---

## Archived Scripts

The `archive/` directory contains 85+ legacy scripts from previous calibration attempts. These are preserved for reference but should not be used directly.

Key archived scripts:
- `debug_*.py` — Debugging tools for infeasibility analysis
- `update_*.py` — Data update scripts
- `fix_*.py` — Bug fix scripts
- `validate_*.py` — Validation tools

---

## Dependencies

Required Python packages:
```bash
pip install pandas numpy matplotlib openpyxl
```

Optional:
```bash
pip install plotly  # For interactive Sankey diagrams
```

---

## Documentation

- [Docs/_index_copilot_docs.md](../Docs/_index_copilot_docs.md) — **Index of all documentation** (start here)
- [Docs/workflow_mess_diagnosis.md](../Docs/workflow_mess_diagnosis.md) — Diagnosis of workflow issues
- [Docs/manual_calibration_foundation.md](../Docs/manual_calibration_foundation.md) — Complete calibration guide
- [Docs/baseline_closest_to_reality.md](../Docs/baseline_closest_to_reality.md) — Best baseline selection
- [case_studies/FI/baseline_notes.md](../case_studies/FI/baseline_notes.md) — Kept baselines and archive notes

---

## Troubleshooting

### "Module not found" errors
```bash
cd EnergyScope_multi_cells
pip install -e .
```

### Solver issues
Ensure CPLEX or Gurobi is properly installed and licensed.

### Unicode errors
Scripts use UTF-8 encoding. If you see encoding errors on Windows:
```bash
# Set Python encoding
set PYTHONIOENCODING=utf-8
python scripts/your_script.py
```

---

*For questions, see the main [README.md](../README.md)*
