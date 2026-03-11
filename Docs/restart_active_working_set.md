# Restart Active Working Set — Finland 2017 Calibration

**Created**: 2026-03-11  
**Purpose**: Define exactly which files matter, what state they should be in, and the first action to take.

---

## Active Data Files (4 files)

| # | File | Current State | Required State | Action |
|---|---|---|---|---|
| 1 | `Data/2017/02_REF_REGION/Technologies.csv` | **REVERTED** — old pre-DEA costs (NUCLEAR=4846) | HEAD state — DEA 2023 costs (NUCLEAR=6000) | `git checkout HEAD -- "Data/2017/02_REF_REGION/Technologies.csv"` |
| 2 | `Data/2017/FI/Technologies.csv` | **block3c dead** — PV caps wrong, no fossil backbone | New v10-style file (see below) | Create new file |
| 3 | `Data/2017/FI/Resources.csv` | **CORRECT** — prices match Excel/v10 | Keep as-is | None |
| 4 | `Data/2017/02_REF_REGION/Resources.csv` | **CORRECT** — prices match Excel/v10 | Keep as-is | None |

---

## Active Scripts (3 files)

| File | Purpose | State |
|---|---|---|
| `scripts/run_calib_manual.py` | Run model manually | OK — working, no changes needed |
| `scripts/validate_run.py` | Validate a run against reality | OK |
| `scripts/score_all_fi_runs.py` | Score all manual runs | OK |

---

## Reference Files (read-only, do not edit)

| File | Purpose |
|---|---|
| `calibration/reality/finland_2017_reference.csv` | Reality data for scoring |
| `case_studies/FI/calib_2017_finland_v10_oil_constr/` | v10 run outputs + .dat files (score=40.4) |
| `case_studies/FI/calib_2017_finland_v9/` | v9 run outputs (score=45.3) |
| `Data/2017/FI/Technologies.csv.bak_20260308_184307` | v10-era 4-column backup (166 techs) |
| `Docs/manual_fi_calibration_tutorial.md` | Step-by-step tutorial |
| `Docs/disabled_technologies_audit.md` | Technology constraint analysis |
| `Docs/regression_audit_vs_3ffdf3fa.md` | Regression analysis from prior session |
| `Docs/manual_calibration_foundation.md` | Calibration principles |

---

## Proposed Restart FI/Technologies.csv

Based on v10 (score=40.4) with 3-column format (no fperc, use `--no-fperc` flag):

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
GEOTHERMAL,0,0.3
PT_POWER_BLOCK,0,0
ST_POWER_BLOCK,0,0
PT_COLLECTOR,0,0
ST_COLLECTOR,0,0
TIDAL_STREAM,0,0
TIDAL_RANGE,0,0
WAVE,0,0
DHN_DEEP_GEO,0,0
DAM_STORAGE,0,0.1
PHS,0,0.1
```

This is 23 rows. v10 had 166 rows (4-column format). The key difference: unlisted technologies default to REF_REGION (f_min=0, f_max=1e15), which is what the model expects when running with `--no-fperc`.

---

## Step-by-Step Restart Sequence

```powershell
# 1. Restore REF_REGION costs to HEAD (DEA 2023)
git checkout HEAD -- "Data/2017/02_REF_REGION/Technologies.csv"

# 2. Backup current (broken) FI/Technologies.csv
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "Data\2017\FI\Technologies.csv" "Data\2017\FI\Technologies.csv.bak_${ts}_pre_restart"

# 3. Write new FI/Technologies.csv (paste the CSV above)
# OR copy from a prepared file

# 4. Run baseline
.venv\Scripts\python.exe scripts\run_calib_manual.py --data-dir Data\2017 --run-name "restart_v10_baseline" --no-fperc

# 5. Check result
$latest = Get-ChildItem "case_studies\FI\manual_runs" -Directory | Sort-Object Name -Descending | Select-Object -First 1
Get-Content "$($latest.FullName)\run_metadata.json" | ConvertFrom-Json | Select-Object solve_code, score
```

**Expected**: solve_code=0, score in range 40-60 (matching v10).

---

## esmc/utils/esmc.py Note

`git diff HEAD` shows modifications to this file (duplicate code removal, comment changes). The user rule is **no esmc changes**. Current working copy has these changes already present. If they cause issues, restore with:
```powershell
git checkout HEAD -- "esmc/utils/esmc.py"
```

---

## What NOT to Touch

- `esmc/` directory — no code changes
- `scripts/run_calib_manual.py` — no solver changes  
- `Data/2017/02_REF_REGION/` — after restoring HEAD, do not modify
- `Data/2017/FI/Resources.csv` — prices are correct, do not change
- Patch files in `calibration/patches/` — not used in manual workflow
