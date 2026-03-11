# Workflow Mess Diagnosis

*Generated: 2026-03-04. Honest assessment of how the calibration workflow became tangled and what needs fixing.*

---

## 1. Root Causes of Accumulated Mess

### 1.1 Copilot Created Runs Without User Request
Runs **p22 through p30** were created autonomously by Copilot, not by the user. The user's patch sequence ends at p21. These 9 runs injected untested or speculative changes:
- `p22, p23`: Copilot experiments that exposed the .dat regeneration bug (session3_handoff)
- `p24, p25`: Further experiments
- `p26, p27, p28_clean_baseline, p30_quick`: **EMPTY** — solver never ran or crashed
- `p29_experiment, p29_test`: Have outputs, but provenance unclear

**Impact:** The `case_studies/FI/` directory now has 64 run folders, most of which nobody trusts fully.

### 1.2 Baseline Inputs Drifted Over Time
The `Data/2017/FI/` directory accumulated multiple backup copies alongside live files:
- `Technologies_REF.csv`, `Technologies_v11_backup.csv`, `Technologies_v5_fperc.csv`
- `Resources_REF.csv`, `Resources_before_v6_block4.csv`, `Resources_v5_fperc.csv`, etc.
- Unclear which backup corresponds to which run

Multiple docs (`calibration_strategy_v6_audit.md`, `finland_post_v6_diagnosis.md`) confirm that the CSVs changed between runs, making older runs unreproducible from current CSV state.

### 1.3 The .dat Regeneration Problem
This is the **single most damaging issue**. Documented in `finland_2017_session3_handoff.md`:

> `run_calib_manual.py` regenerates .dat files from CSVs when cloning a baseline. If CSVs changed since the baseline was run, the new .dat files differ from the baseline's .dat files, producing wildly different results.

Example: objective jumped from 49,677 (v10 original .dat) to 24,900,000 (regenerated .dat from same CSVs). This means **patching atop a baseline by re-running the full pipeline is unsafe** unless inputs are frozen.

### 1.4 run_calib_manual.py Grew Too Complex
The script grew to 713 lines with:
- Its own CPLEX option block (duplicating `esmc/utils/esmc.py` defaults)
- A cloning mechanism that copies entire run directories
- A backup/restore mechanism for CSV files
- Direct AMPL command construction bypassing `Esmc.set_esom()`
- `--reuse-dat` flag to work around the regeneration bug (a band-aid)
- No automatic score calculation piped to `run_rankings.csv`

### 1.5 2017 Data Copy-Pasted from 2035
The 2017/FI data was initially created by copying 2035/FI and hand-editing. This introduced:
- Structural differences (2017 has 166 tech rows with fmin_perc/fmax_perc columns; 2035 has 20 rows, no perc columns)
- Future technologies in 2017 that don't belong (e.g., CCGT_AMMONIA)
- f_max = 1e15 values creating 15 orders of magnitude range → solver degeneracy

### 1.6 f_perc: False Silently Disabling Constraints
Documented in `finland_2017_end_of_day_review.md` and `finland_2017_stepback_audit.md`:
- `f_perc: False` in config drops ALL `f_max_perc` and `f_min_perc` constraints (see `esmc.py` lines 700-712)
- Many calibration runs used `f_perc: False` unknowingly, making fmin_perc/fmax_perc overrides inert
- Critical discovery at patch p13

---

## 2. Current State of Runs (64 directories)

| Category | Count | Details |
|----------|-------|---------|
| **EMPTY / no output** | 6 | p26, p27, p28_clean_baseline, p30_quick, v6_recalib, v8_rerun |
| **User's original runs** (p01-p21) | ~18 | Mixed quality, some excellent (p01-p12 probably valid) |
| **Copilot's autonomous runs** (p22-p30) | 9 | Untrusted provenance |
| **Named calibration runs** (v5-v11, baseline, etc.) | ~31 | Includes ref reproductions, block experiments |
| **Scored in run_rankings.csv** | 22 | Only non-pXX + named v-runs were scored |
| **Unscored** | 42 | The entire pXX sequence, plus some others |

Best existing scores:
- `v9` — 39.19% (weighted APE)
- `v10_oil_constr` — 39.20%
- `baseline` — 42.07%

---

## 3. What Needs Fixing (Mapped to Steps)

### Step 1: 100% Scoring Coverage
- Current `score_calib_runs.py` only covers 22 runs
- Need to score ALL 64 runs and flag EMPTY ones explicitly
- Output a complete `run_rankings.csv` with: status (OK, EMPTY, FAILED, NO_RESULTS), score, key metrics

### Step 2: Archive the Junk
Move clearly bad runs to `_archive_YYYYMMDD/`:
- 6 EMPTY runs (no question)
- Copilot-created runs p22-p30 (user didn't request them)
- Duplicate/superseded runs after user review

Keep 3-4 trusted baselines:
- `v9` or `v10_oil_constr` (best score)
- `baseline` / `calib_2017_finland` (Feb 14 reference)
- One user-authored pXX run for continuity

### Step 3: Simpler Runner Script
The new `run_calib_manual.py` should:
1. Follow `run_esmc_simple_3c 1.py` pattern (use ESMC framework properly)
2. Apply patches via in-memory data modification (not CSV overwrite + .dat regeneration)
3. Output to `case_studies/FI/manual_runs/<timestamp>__<run-name>/`
4. Auto-score after each run
5. Include a tutorial header explaining usage
6. Support `--solver-profile` presets (cplex-default, cplex-tuned, highs)

### Step 4: Clean Alternative Data Preset
Create `Data/2017_alt_from2035tech/` that:
- Uses 2035 technology structure (simpler, fewer rows)
- Keeps 2017 demands and resources
- Provides a known-clean starting point free from accumulated edits

---

## 4. Non-Negotiable Principles Going Forward
1. **User runs the model, Copilot builds tools.** No autonomous runs.
2. **Archive, never delete.** All moves go to `_archive_YYYYMMDD/`.
3. **Baseline data is sacred.** Any patching mechanism must snapshot inputs or work in-memory.
4. **Every run gets scored immediately.** No more untracked experiments.
5. **One runner script, one pattern.** Aligned with ESMC framework.
