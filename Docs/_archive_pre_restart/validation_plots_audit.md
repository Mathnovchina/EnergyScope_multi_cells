# Validation Plots Audit

**Date**: 2025-06-14  
**Scope**: Finland 2017 calibration — validation plotting workflow

---

## Part 1: Does `run_calib_manual.py` produce validation plots?

**Answer: No.**

The refactored `run_calib_manual.py` (483 lines) has a 7-step workflow:
1. Init ESMC
2. Read Data/2017
3. Apply patches in-memory
4. Temporal aggregation
5. Generate .dat files
6. Solve
7. Collect results + auto-score → append to `run_rankings.csv`

There is **no plotting step**. The old version (`_archive_20250613/run_calib_manual_old.py`, 713 lines) called plotting functions, but these were dropped during the refactor.

**Recommendation**: Keep the runner lean (no plotting). Use `scripts/validate_run.py` as a standalone post-processing step.

---

## Part 2: Reality Reference Exhaustiveness

The reference file `calibration/reality/finland_2017_reference.csv` was audited.

### Original state (26 rows, 7 columns)
- Only 11 metrics were used by the scoring engine (`run_calib_manual.py` and `score_all_fi_runs.py`)
- 15 metrics in the CSV were **not scored at all**: `primary_energy/total`, `primary_energy/solar`, `electricity/generation`, `electricity/chp`, `electricity/condensation`, `electricity/solar`, `electricity/geothermal`, `electricity/gas`, `electricity/peat`, `electricity/imports`, `heat/dh_production`, `heat/dh_share`, `transport/*`, `misc/re_share_primary`
- No `model_key` column existed — the mapping from reality metric to model output was implicit

### Key mapping issues found:
1. **Coal vs coal_peat**: Reality says 35 TWh for "coal_peat" but the model has only `COAL` as a resource — no separate PEAT. This is acceptable because Finland's ESMC data lumps coal+peat into COAL.
2. **Electricity peat** (2.6 TWh): Cannot be extracted from the model since peat is not a separate resource. Marked as unmappable.
3. **CHP electricity** (25 TWh): Was in reference but not scored. Now mapped to `DHN_COGEN_*` + `IND_COGEN_*` + `DEC_COGEN_*` + `DEC_ADVCOGEN_*`.
4. **Gas electricity** (3.2 TWh): Was in reference but not scored. Now mapped to gas CHP techs + CCGT + OCGT.
5. **DH production** (36.5 TWh): Was in reference but not scored. Now mapped to all DHN_* techs in HEAT_LOW_T_DHN layer.

### Updated state (26 rows, 9 columns)
Added two new columns:
- `model_key`: The programmatic key used in extraction (e.g. `PE_BIOMASS`, `ELEC_CHP`)
- `model_mapping`: Exact formula showing which model outputs and files are used

---

## Part 3: Source Material in `Data/exogenous_data/`

The directory contains:
- `EnergyScope_Finland_calibration_template_v4.xlsx` — calibration template
- `Finland_2017_v6_calibration_tracker.xlsx` — v6 tracker
- `Finland_MASTER_Calibration.xlsx` — master calibration file
- `Finland_MASTER_Calibration_REORG.xlsx` — reorganized version
- `ehk_2017_2018-12-11_en.pdf` — Finnish energy statistics
- `technology_data_catalogue_for_el_and_dh.pdf` — Danish Energy Agency reference
- `DEA_Elec_Heat.xlsx` — DEA data
- `ENSPRESO/` — wind/solar/biomass potential data
- `regions/`, `csp/`, `gis/` — geographic data

**Assessment**: The Excel tracker files are the authoritative source for calibration targets, but cannot be read by the script (binary format). The current CSV reference values are consistent with the sources listed in the "source" column (Statistics Finland, IEA, IAEA, Fingrid, ENTSO-E).

---

## Part 4: Actions Taken

1. **Updated `calibration/reality/finland_2017_reference.csv`**:
   - Added `model_key` column (programmatic identifier)
   - Added `model_mapping` column (exact extraction formula)
   - Documented that PEAT is lumped into COAL
   - Documented unmappable metrics (electricity/peat)

2. **Created `scripts/validate_run.py`** (unified validation plotter):
   - Replaces three overlapping scripts: `plot_validate_2017.py`, `generate_validation_plots_and_report.py`, `generate_finland_validation.py`
   - Extracts 24 model metrics (up from 11 in scorer): PE×8, ELEC×8 (incl CHP, condensation, gas, imports), HEAT_DHN, CO2, PE_TOTAL, RE_SHARE, transport shares
   - Generates 6 output files per run: `pe_comparison.png`, `elec_comparison.png`, `co2_comparison.png`, `error_chart.png`, `validation_report.md`, `validation_table.csv`
   - Supports `--batch` (all 7 baselines), `--run-dir`, `--run-name`, `--runs`

3. **Ran validation on all 7 baselines** — 7/7 succeeded, plots in each `validation_plots/` directory.

---

## Part 5: Existing Plotting Scripts Status

| Script | Lines | Status | Recommendation |
|--------|-------|--------|----------------|
| `validate_run.py` (NEW) | 320 | **Active** — authoritative plotter | Use this |
| `generate_finland_validation.py` | 762 | Superseded by validate_run.py | Archive |
| `plot_validate_2017.py` | 578 | Superseded by validate_run.py | Archive |
| `generate_validation_plots_and_report.py` | 335 | Hardcoded to one run, inline data | Archive |

---

## Part 6: Run-level Validation Summary

All 7 baselines now have `validation_plots/` with:
- `pe_comparison.png` — primary energy bar chart
- `elec_comparison.png` — electricity mix bar chart
- `co2_comparison.png` — CO2 emissions comparison
- `error_chart.png` — horizontal error analysis (16 metrics)
- `validation_report.md` — Table 2 style markdown report
- `validation_table.csv` — machine-readable validation data

Previously only 5/7 had validation plots. Now all 7 do, with consistent methodology.
