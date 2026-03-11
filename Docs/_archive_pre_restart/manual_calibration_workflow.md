# Manual Calibration Workflow for Finland 2017

## Overview

This document provides a comprehensive guide for manual calibration runs of the EnergyScope Multi-Cells model for Finland 2017. It covers the data structure, run scripts, patch creation, and troubleshooting.

---

## Table of Contents

1. [Data Structure](#data-structure)
2. [Understanding the Run Scripts](#understanding-the-run-scripts)
3. [Running the Model](#running-the-model)
4. [Creating Patches](#creating-patches)
5. [Comparing Runs](#comparing-runs)
6. [Troubleshooting](#troubleshooting)
7. [Key Files Reference](#key-files-reference)

---

## Data Structure

### Directory Layout

```
Data/
├── 2017/                          # Historical year data (calibration target)
│   ├── 00_INDEP/                  # Independent/shared data
│   │   ├── Layers_in_out.csv
│   │   ├── Misc_indep.json
│   │   ├── Resources_indep.csv
│   │   ├── Storage_characteristics.csv
│   │   ├── Storage_eff_in.csv
│   │   └── Storage_eff_out.csv
│   ├── 01_EXCH/                   # Exchange data (if multi-region)
│   ├── 02_REF_REGION/             # Reference region defaults
│   │   ├── Technologies.csv       # Default technology parameters
│   │   ├── Resources.csv          # Default resource parameters
│   │   ├── Demands.csv
│   │   └── ...
│   └── FI/                        # Finland-specific overrides
│       ├── Technologies.csv       # ★ MAIN CALIBRATION FILE
│       ├── Resources.csv          # ★ Resource availability
│       ├── Demands.csv            # ★ Energy demands
│       └── ...
├── 2035/                          # Future year projections
│   └── FI/                        # (similar structure)
└── exogenous_data/
    ├── Finland_2017_v6_calibration_tracker.xlsx   # Tracks results across runs
    ├── Finland_MASTER_Calibration_REORG.xlsx      # Master calibration data
    └── Finland_MASTER_Calibration_old_UPDATED.xlsx
```

### Key Data Files (Data/2017/FI/)

| File | Purpose | Key Columns |
|------|---------|-------------|
| `Technologies.csv` | Technology capacity bounds | `f_min`, `f_max`, `fmin_perc`, `fmax_perc` |
| `Resources.csv` | Resource availability | `avail_local`, `c_op_local`, `avail_exterior` |
| `Demands.csv` | Energy service demands | `ELECTRICITY`, `HEAT_LOW_T_SH`, etc. |

### 2017 vs 2035 Key Differences

The 2017 data was adapted from 2035 with these changes:

| Parameter | 2017 Value | 2035 Value | Notes |
|-----------|------------|------------|-------|
| NUCLEAR f_min | 2.5 GW | 4.36 GW | Lower installed capacity |
| WIND_ONSHORE f_max | 2.1 GW | 30.77 GW | Much less wind in 2017 |
| PV_ROOFTOP f_max | 2.0 GW | 13.68 GW | Less solar in 2017 |
| Technologies count | 166 | 20 | 2017 includes all tech types |
| Extra columns | fmin_perc, fmax_perc | - | Percentage constraints |

---

## Understanding the Run Scripts

### Script Categorization

Runs in `case_studies/FI/` follow naming patterns:

| Pattern | Script | Description |
|---------|--------|-------------|
| `calib_2017_finland_pXX_*` | `run_calib_manual.py` | Manual calibration runs with patches |
| `calib_2017_finland_vX` | Other scripts | Version-based calibration runs |
| `calib_2017_finland` | Baseline | Original baseline run |

### run_calib_manual.py Workflow

```
1. Clone baseline    → Creates copy of existing run directory
2. Apply patches     → Modifies Data/2017/FI/ files (with backup)
3. Run model         → Executes AMPL solver
4. Restore backups   → Returns Data/2017/FI/ to original state
5. Generate plots    → Creates validation charts
6. Save metadata     → Records run parameters
```

---

## Running the Model

### Prerequisites

1. Activate virtual environment:
   ```powershell
   & .\.venv\Scripts\Activate.ps1
   ```

2. Ensure solver is available (CPLEX, Gurobi, or HiGHS)

### Basic Commands

```powershell
# Dry run (validate without executing)
python scripts/run_calib_manual.py --run-name p29_test --dry-run

# Full run with default baseline
python scripts/run_calib_manual.py --run-name p29_myrun --solver cplex

# Run with a patch file
python scripts/run_calib_manual.py --run-name p30_experiment --patch calibration/patches/p01_disable_futuretechs.csv

# Multiple patches
python scripts/run_calib_manual.py --run-name p31_combined --patch calibration/patches/p01_disable_futuretechs.csv --patch calibration/patches/p20_disable_advcogen.csv

# Clone from a specific baseline
python scripts/run_calib_manual.py --run-name p32_fromv9 --from-baseline calib_2017_finland_v9

# Quick run reusing existing .dat files (no CSV regeneration)
python scripts/run_calib_manual.py --run-name p33_quick --reuse-dat
```

### Command Options

| Option | Description |
|--------|-------------|
| `--run-name`, `-n` | **Required.** Run identifier (auto-prefixed with `calib_2017_finland_`) |
| `--from-baseline`, `-b` | Baseline to clone (default: `calib_2017_finland`) |
| `--patch`, `-p` | CSV patch file(s) to apply (repeatable) |
| `--description`, `-d` | Run description |
| `--dry-run` | Prepare but don't execute |
| `--skip-plots` | Skip validation plot generation |
| `--solver` | Solver choice: `cplex`, `gurobi`, `highs` |
| `--reuse-dat` | Use existing .dat files without regenerating |

---

## Creating Patches

### Patch File Format

Patches are CSV files with 4 columns:

```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_max,DEC_ADVCOGEN_GAS,0
Technologies.csv,f_min,NUCLEAR,2.8
Resources.csv,avail_local,WOOD,150000
```

### Column Reference

| Column | Description | Valid Values |
|--------|-------------|--------------|
| `file` | Target CSV file | `Technologies.csv`, `Resources.csv` |
| `parameter` | Column to modify | `f_min`, `f_max`, `fmin_perc`, `fmax_perc`, `avail_local`, etc. |
| `technology_or_resource` | Row identifier | Technology name (e.g., `NUCLEAR`) or resource name (e.g., `WOOD`) |
| `value` | New value | Numeric value |

### Common Patch Scenarios

**1. Disable a technology:**
```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_max,DEC_ADVCOGEN_GAS,0
```

**2. Force minimum capacity:**
```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_min,NUCLEAR,2.8
Technologies.csv,f_max,NUCLEAR,2.8
```

**3. Constrain percentage share:**
```csv
file,parameter,technology_or_resource,value
Technologies.csv,fmin_perc,IND_BOILER_WOOD,0.4
Technologies.csv,fmax_perc,IND_BOILER_WOOD,0.6
```

**4. Adjust resource availability:**
```csv
file,parameter,technology_or_resource,value
Resources.csv,avail_local,WOOD,150000
```

### Creating a New Patch

1. Create a CSV file in `calibration/patches/`:
   ```powershell
   New-Item -Path "calibration/patches/p34_my_experiment.csv" -ItemType File
   ```

2. Add header and modifications:
   ```csv
   file,parameter,technology_or_resource,value
   Technologies.csv,f_max,MY_TECH,10
   ```

3. Test with dry run:
   ```powershell
   python scripts/run_calib_manual.py --run-name p34_test --patch calibration/patches/p34_my_experiment.csv --dry-run
   ```

---

## Comparing Runs

### Output Files Location

After a successful run, outputs are in:
```
case_studies/FI/calib_2017_finland_pXX_name/outputs/
├── TotalCost.csv          # Objective function value
├── Assets.csv             # Installed capacities (F, f_min, f_max, F_year)
├── Resources.csv          # Resource consumption
├── Year_balance.csv       # Energy balance by layer
├── Cost_breakdown.csv     # Cost components
├── Gwp_breakdown.csv      # GHG emissions breakdown
└── Solve_info.csv         # Solver status and timing
```

### Quick Comparison Script

```python
import pandas as pd
from pathlib import Path

def compare_runs(run1_name, run2_name):
    base = Path('case_studies/FI')
    
    assets1 = pd.read_csv(base / run1_name / 'outputs' / 'Assets.csv')
    assets2 = pd.read_csv(base / run2_name / 'outputs' / 'Assets.csv')
    
    # Compare key technologies
    key_techs = ['NUCLEAR', 'COAL_US', 'WIND_ONSHORE', 'DHN_COGEN_WOOD']
    
    for tech in key_techs:
        f1 = assets1.loc[assets1['Technologies'] == tech, 'F'].values
        f2 = assets2.loc[assets2['Technologies'] == tech, 'F'].values
        print(f"{tech}: {f1[0]:.2f} vs {f2[0]:.2f}")

# Usage
compare_runs('calib_2017_finland', 'calib_2017_finland_p25_disable_advcogen_reusedat')
```

### Reality Targets (Finland 2017)

Reference values are in `calibration/reality/finland_2017_reference.csv`:

| Metric | Target | Unit | Weight |
|--------|--------|------|--------|
| Total primary energy | 380 | TWh | 1.0 |
| Nuclear generation | 21.4 | TWh | 1.5 |
| Hydro generation | 14.5 | TWh | 1.2 |
| Wind generation | 4.8 | TWh | 1.0 |
| CHP electricity | 25.0 | TWh | 1.2 |
| CO2 emissions | 41.2 | MtCO2 | 2.0 |

---

## Troubleshooting

### Common Issues

**1. "Run directory already exists"**
```powershell
Remove-Item -Recurse -Force "case_studies\FI\calib_2017_finland_pXX_name"
```

**2. Empty outputs folder**
- Check the `log.txt` file in the run directory
- Solver might have failed or timed out
- Try different solver: `--solver highs`

**3. "Entity not found" warning during patch**
- Check technology/resource name spelling in patch file
- Match exact name from Technologies.csv or Resources.csv

**4. Solver timeout**
- Default timeout is 172800 seconds (48 hours)
- For testing, use `--reuse-dat` to skip CSV regeneration

### Checking Run Status

```powershell
# List recent runs
Get-ChildItem "case_studies\FI" | Where-Object { $_.Name -like "calib_2017*" } | Sort-Object LastWriteTime -Descending | Select-Object -First 10 Name, LastWriteTime

# Check if run has outputs
Test-Path "case_studies\FI\calib_2017_finland_pXX_name\outputs\TotalCost.csv"

# View log tail
Get-Content "case_studies\FI\calib_2017_finland_pXX_name\log.txt" -Tail 50
```

---

## Key Files Reference

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `run_calib_manual.py` | `scripts/` | Main calibration runner |
| `finland_2017_reference.csv` | `calibration/reality/` | Reality targets |
| `Patch files (*.csv)` | `calibration/patches/` | Parameter modifications |

### Existing Patches

| Patch | Purpose |
|-------|---------|
| `p01_disable_futuretechs.csv` | Disable future technologies not available in 2017 |
| `p20_disable_advcogen.csv` | Disable advanced cogeneration |
| `p05_consolidated_fix.csv` | Consolidated calibration fixes |

### Successful Baseline Runs

These runs have valid outputs and can be used as `--from-baseline`:

| Run Name | Status | Notes |
|----------|--------|-------|
| `calib_2017_finland` | ✅ OK | Original baseline |
| `calib_2017_finland_p01_test` | ✅ OK | First patch test |
| `calib_2017_finland_p25_disable_advcogen_reusedat` | ✅ OK | Quick reuse-dat run |
| `calib_2017_finland_v9` | ✅ OK | Version 9 calibration |

### Excel Tracker Files

| File | Sheets | Purpose |
|------|--------|---------|
| `Finland_2017_v6_calibration_tracker.xlsx` | Resources, Technologies, Objective, Violations | Track results across v6 block runs |
| `Finland_MASTER_Calibration_REORG.xlsx` | Multiple sheets | Master calibration data (reorganized) |

---

## Quick Start Checklist

1. [ ] Activate virtual environment: `& .\.venv\Scripts\Activate.ps1`
2. [ ] Choose baseline: `calib_2017_finland` or a specific version
3. [ ] Prepare patch file (if needed): `calibration/patches/pXX_name.csv`
4. [ ] Dry run first: `python scripts/run_calib_manual.py --run-name pXX_test --dry-run`
5. [ ] Full run: `python scripts/run_calib_manual.py --run-name pXX_name --solver cplex`
6. [ ] Check outputs: `case_studies/FI/calib_2017_finland_pXX_name/outputs/`
7. [ ] Compare with reality targets in `calibration/reality/finland_2017_reference.csv`

---

*Generated: 2026-03-03*
