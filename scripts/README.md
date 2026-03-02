# Scripts Directory

> EnergyScope Multi-Cells — Finland 2017 Calibration Scripts  
> Last updated: 2024

This directory contains scripts for running and analyzing Finland 2017 calibration runs.

---

## Quick Start

```bash
# 1. Score all existing calibration runs
python scripts/score_calib_runs.py

# 2. Generate validation plots for a run
python scripts/plot_validate_2017.py --run-name calib_2017_finland

# 3. Run manual calibration with a patch
python scripts/run_calib_manual.py --run-name v12_test --patch patches/my_patch.csv
```

---

## Active Scripts (Recommended)

### Calibration Workflow

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_calib_manual.py` | Manual calibration runner with patches | `python run_calib_manual.py -n test -p patch.csv` |
| `score_calib_runs.py` | Score/rank runs vs reality targets | `python score_calib_runs.py` |
| `plot_validate_2017.py` | Generate validation plots | `python plot_validate_2017.py -n v9` |

### Model Runners

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_esmc.py` | Run EnergyScope model | `python run_esmc.py --case-study FI/v9` |
| `run_calib_2017.py` | Legacy calibration runner | See docstring |
| `run_calib_case.py` | Case study runner | See docstring |

### Analysis & Plotting

| Script | Purpose |
|--------|---------|
| `generate_sankey_data.py` | Generate Sankey diagram data |
| `plot_energy_mix.py` | Plot energy mix charts |
| `generate_validation_plots_and_report.py` | Full validation report |
| `analyze_calibration_gaps.py` | Analyze gaps between model and reality |

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
├── run_calib_manual.py     # ★ Manual calibration runner
├── score_calib_runs.py     # ★ Run scoring/ranking
├── plot_validate_2017.py   # ★ Validation plots
├── run_esmc.py             # Model runner
├── run_calib_2017.py       # Legacy runner
├── analyze_*.py            # Analysis scripts
├── generate_*.py           # Data generation scripts
├── plot_*.py               # Plotting scripts
├── compare_*.py            # Comparison scripts
├── advanced/               # Advanced/experimental scripts
└── archive/                # Legacy scripts (85+ files)
```

---

## Output Locations

Scripts generate outputs in:

| Output Type | Location |
|-------------|----------|
| Run results | `case_studies/FI/calib_2017_finland_*/outputs/` |
| Validation plots | `case_studies/FI/calib_2017_finland_*/validation_plots/` |
| Run rankings | `calibration/run_rankings.csv` |
| Reality reference | `calibration/reality/finland_2017_reference.csv` |
| Sankey data | `case_studies/FI/*/outputs/input2sankey_FI.csv` |

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

- [manual_calibration_foundation.md](../Docs/manual_calibration_foundation.md) — Complete calibration guide
- [baseline_closest_to_reality.md](../Docs/baseline_closest_to_reality.md) — Best baseline selection
- [finland_2017_calibration_dossier.md](../Docs/finland_2017_calibration_dossier.md) — Full calibration dossier

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
