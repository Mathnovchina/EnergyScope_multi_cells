# Manual Finland 2017 Calibration — Step-by-Step Tutorial

**Created**: 2026-03-11  
**Purpose**: Exact commands for each step of a manual calibration run.  
**Rule**: Never edit `esmc/` code. All calibration is via CSV files + solver script.

---

## 1. Pre-Flight: Verify Data Files

Before every run, confirm the four key files are in the expected state.

```powershell
# Check REF_REGION/Technologies.csv matches HEAD (DEA 2023 costs)
git diff HEAD -- "Data/2017/02_REF_REGION/Technologies.csv"
# Should return EMPTY (no diff). If not: git checkout HEAD -- "Data/2017/02_REF_REGION/Technologies.csv"

# Check FI/Resources.csv prices are correct
Select-String "COAL|DIESEL|GAS[^O]|URANIUM" "Data\2017\FI\Resources.csv"

# Check FI/Technologies.csv is the file you intend to use
Get-Content "Data\2017\FI\Technologies.csv"
```

## 2. Backup Before Every Edit

```powershell
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "Data\2017\FI\Technologies.csv" "Data\2017\FI\Technologies.csv.bak_$ts"
```

Name the backup with a tag after running, so you know what it represents:
```powershell
# Example: after your run succeeds or fails
Rename-Item "Data\2017\FI\Technologies.csv.bak_$ts" "Data\2017\FI\Technologies.csv.bak_${ts}_description"
```

## 3. Edit FI/Technologies.csv

The file has 3 columns: `Technologies param,f_min,f_max`  
Only technologies that differ from REF_REGION defaults need to be here.

**Format rules:**
- Header: `Technologies param,f_min,f_max`
- One technology per row
- f_min/f_max in GW (installed capacity)
- Use `0,0` to disable a technology
- Omit a technology to use REF_REGION defaults (f_min=0, f_max=1e15)

**Example — minimal file for v10-style run:**
```csv
Technologies param,f_min,f_max
NUCLEAR,2.5,2.8
CCGT,0.6,1.5
COAL_US,3.5,4.5
PV_ROOFTOP,0.02,2.0
PV_UTILITY,0.0,1.0
WIND_ONSHORE,2.0,2.1
WIND_OFFSHORE,0,0
HYDRO_DAM,1.1,1.3
HYDRO_RIVER,1.9,2.1
DHN_COGEN_GAS,0.6,1.5
DHN_BOILER_OIL,0.4,1.0
IND_BOILER_OIL,0.2,1.0
PT_POWER_BLOCK,0,0
ST_POWER_BLOCK,0,0
PT_COLLECTOR,0,0
ST_COLLECTOR,0,0
TIDAL_STREAM,0,0
TIDAL_RANGE,0,0
WAVE,0,0
DHN_DEEP_GEO,0,0
GEOTHERMAL,0,0.3
DAM_STORAGE,0,0.1
PHS,0,0.1
```

## 4. Run the Model

```powershell
.venv\Scripts\python.exe scripts\run_calib_manual.py `
  --data-dir Data\2017 `
  --run-name "my_description" `
  --no-fperc
```

**Flags:**
- `--data-dir Data\2017` — path to the data directory
- `--run-name "tag"` — descriptive name (appears in output folder name)
- `--no-fperc` — skip fmin_perc/fmax_perc columns (use only f_min/f_max)
- Without `--no-fperc`: also reads fmin_perc and fmax_perc columns if present

The script:
1. Creates timestamped output folder under `case_studies/FI/manual_runs/`
2. Saves input snapshot (copies of all CSV inputs)
3. Runs CPLEX barrier (crossover=0, timelimit 172800s)
4. Falls back to dual simplex (1800s) if barrier fails
5. Saves `run_metadata.json` with solve code, score, timestamps

## 5. Check Results

```powershell
# Find latest run
$latest = Get-ChildItem "case_studies\FI\manual_runs" -Directory | Sort-Object Name -Descending | Select-Object -First 1
Write-Host $latest.Name

# Check solve status
Get-Content "$($latest.FullName)\run_metadata.json" | ConvertFrom-Json | Select-Object solve_code, score, run_name

# solve_code meanings:
#   0  = optimal
#  -1  = infeasible
#   2  = unbounded
#  100 = feasible but not optimal (time limit)
```

## 6. Score & Validate

```powershell
# Score all runs
.venv\Scripts\python.exe scripts\score_all_fi_runs.py

# Validate specific run
.venv\Scripts\python.exe scripts\validate_run.py "$($latest.FullName)"
```

## 7. Compare to Reality

Reference data: `calibration/reality/finland_2017_reference.csv`

Key reality values for Finland 2017 (GW installed):
| Technology | Reality |
|---|---|
| NUCLEAR | 2.764 |
| CCGT + gas CHP | ~1.2 |
| COAL (total) | ~3.8 |
| WIND_ONSHORE | 2.04 |
| HYDRO (total) | ~3.2 |
| PV (total) | ~0.04 |

## 8. Iterate

Based on results:
1. Backup current FI/Technologies.csv (step 2)
2. Adjust f_min/f_max values (step 3)
3. Re-run (step 4)
4. Compare score (step 5-6)

**Calibration strategy:**
- Start with well-known technologies (nuclear, hydro) tightly constrained
- Add fossil backbone (CCGT, COAL_US) with moderate ranges
- Add renewables (PV, wind) with wide ranges initially
- Tighten ranges once base score is acceptable

## 9. Revert a Bad Edit

```powershell
# List available backups
Get-ChildItem "Data\2017\FI" -Filter "Technologies.csv.bak*" | Format-Table Name, LastWriteTime -AutoSize

# Restore from backup
Copy-Item "Data\2017\FI\Technologies.csv.bak_TIMESTAMP" "Data\2017\FI\Technologies.csv"
```

## 10. Override Mechanism Reference

The model loads data in this order:
1. `Data/2017/02_REF_REGION/Technologies.csv` — full technology database (costs, lifetimes, f_min=0/f_max=1e15 for most)
2. `Data/2017/FI/Technologies.csv` — FI overrides applied via `pandas.DataFrame.update()` (only matching cells are overwritten)

This means:
- Any technology NOT in FI/Technologies.csv keeps its REF_REGION defaults
- To constrain a technology: add it to FI/Technologies.csv with specific f_min/f_max
- To disable a technology: set f_min=0, f_max=0 in FI/Technologies.csv
- REF_REGION costs (c_inv, c_maint, etc.) are NEVER overridden by FI — only f_min/f_max
