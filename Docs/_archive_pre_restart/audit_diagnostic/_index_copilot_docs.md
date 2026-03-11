# Index of Copilot-Generated Documentation

*Generated: 2026-03-04. Covers all `.md` files in `Docs/`.*

---

## 1. baseline_closest_to_reality.md
Identifies which calibration run is closest to Finland 2017 reality using weighted percentage error scoring. Recommends `calib_2017_finland_v9` (score 39.2%) as the starting baseline; `v10_oil_constr` (39.2%) is a close second.
**References:** `v9`, `v10_oil_constr`, reality targets.
**Status:** Valid reference. The scoring methodology and rankings are still usable.

## 2. calibration_strategy_v6.md
Comprehensive strategy document for the v6 calibration iteration. Explains ESMC optimizer mechanics and documents six calibration levers (`f_min`, `f_max`, `fmin_perc`, `fmax_perc`, `avail_local`, `avail_exterior`) with AMPL formulations. Plans to match Finland 2017 energy statistics using restored v5_fperc inputs.
**References:** `Data/2017/FI/` CSVs, AMPL model equations, v5_fperc baseline.
**Status:** **OBSOLETE** — the audit (`calibration_strategy_v6_audit.md`) found all 5 resource values wrong, 6 technology values incorrect, multiple ADD/MODIFY mismatches vs current data files.

## 3. calibration_strategy_v6_audit.md
Audit of `calibration_strategy_v6.md` against actual data files. Confirms significant data staleness: all 5 "current" resource values wrong, 6 technology values incorrect, phantom technologies, counterproductive fmin_perc proposals. **Supersedes** the strategy doc.
**References:** `Data/2017/FI/`, `02_REF_REGION/`, backup files.
**Status:** Valid — this audit is the authoritative correction.

## 4. esmc_solver_audit.md
Technical audit of the ESMC framework architecture and CPLEX solver configuration. Documents class hierarchy (`Esmc → OptiProbl → Region → TemporalAggregation`), execution flow, and solver option mechanism in `esmc/utils/esmc.py`.
**References:** `esmc/utils/esmc.py`, `opti_probl.py`, `region.py`, `temporal_aggregation.py`.
**Status:** Valid — current technical documentation of the solver pipeline.

## 5. finland_2017_calibration_dossier.md
Complete audit of every data source, hypothesis, and override used in Finland 2017. Covers technologies, resources/trade, demands, misc/policy parameters, layers/efficiencies, time series, storage, network losses. Uses three-tier data hierarchy (INDEP → REF_REGION → FI).
**References:** All `Data/2017/` files, REORG calibration workbook.
**Status:** Valid reference — comprehensive provenance document.

## 6. finland_2017_consistency_checks.md
Automated cross-check report across all data tiers and the REORG workbook. 15 checks; result: 2 warnings, 0 errors. Warnings: CCGT_AMMONIA in FI but not REF (no-op); 2/11 demands differ >5% from workbook.
**References:** `Data/2017/FI/`, `02_REF_REGION/`, `00_INDEP/`.
**Status:** Valid final report.

## 7. finland_2017_end_of_day_review.md
End-of-day review of 2026-03-02 session testing `fmin_perc` for CHP calibration. Confirms fmin_perc mechanism is functional; `f_perc: False` was disabling all fmin_perc constraints.
**References:** `run_calib_manual.py`, patches, p13_clean and others.
**Status:** Session log — no standalone deliverable, but contains useful insight.

## 8. finland_2017_lever_map.md
Maps exact data state of the Feb 14 calibration run by reverse-engineering inputs from compiled `.dat` files. VERIFIED: PERFECT MATCH for Technologies.csv and Resources.csv reconstructed from `reg_technologies.dat`. Identifies relevant git commits (937940b, a20876d).
**References:** `calib_2017_finland/`, git commits 937940b, a20876d.
**Status:** Valid — provenance document for the Feb 14 baseline.

## 9. finland_2017_patch_journal.md
Tracks controlled micro-patches from `v10_oil_constr` baseline. Documents a critical issue: Data/2017 CSVs have been modified since v10 was created, causing solver divergence with regenerated .dat files. Proposes `--reuse-dat` as workaround.
**References:** `run_calib_manual.py`, `Data/2017/*.csv`, v10 `.dat` files.
**Status:** Active — documents a blocking issue still relevant.

## 10. finland_2017_prerun_recap.md
Pre-run recap at git commit 937940b. Single-country FI optimisation for 2017, 12 TDs, f_perc=True, 41% RE share. Summarizes 63 technology overrides.
**References:** `run_feb14_repro.py`, commit 937940b.
**Status:** Valid historical snapshot.

## 11. finland_2017_session3_handoff.md
Handoff documenting blocking issue: `run_calib_manual.py` regenerates .dat from CSVs when cloning, causing solver divergence (24.9M vs 49,677 objective).
**References:** `run_calib_manual.py`, v10, p22, p23 runs.
**Status:** Documents known blocking issue — still relevant.

## 12. finland_2017_stepback_audit.md
Pre-session audit. Confirms 29 runs and 16 patches from 2026-03-02 session. `f_perc: False` was disabling fmin_perc constraints. CHP went from 5.2 to 50.7 TWh in p13 but solver gave "unknown status".
**References:** `case_studies/FI/`, patches, AMPL `.mod` file.
**Status:** Audit note — useful context.

## 13. finland_2017_traceability_index.md
Full traceability map from every AMPL parameter back to its external data source, through pipeline: External → Workbook → CSV → print_to_dat → AMPL. Covers technologies, resources, demands with tier attribution.
**References:** `02_REF_REGION/`, `Data/2017/FI/`, `.dat`/`.mod` files.
**Status:** Valid — canonical provenance reference.

## 14. finland_2017_v6_block_results.md
Block-by-block results for v6 calibration (Blocks 0–6). Notes CPLEX barrier with crossover disabled; tolerance violations (MaxAbs up to ~10^5) mean capacity caps only approximately enforced. Objective dropped from 2.32e+16 (v5_fperc) to 1.62e+07 (Block5_coal).
**References:** v6 block runs, plots.
**Status:** Valid results report.

## 15. finland_2017_v6_changelog.md
Change log for v6 calibration. Root cause found: 120 technologies with f_max=1e15 creating 15 orders of magnitude variable range, preventing barrier solver from meaningful feasibility tolerance.
**References:** `v5_fperc_repro/log.txt`, `Data/2017/FI/backups_v5_fperc/`.
**Status:** Valid — documents root cause of solver degeneracy.

## 16. finland_post_v6_diagnosis.md
Post-v6 diagnosis: URANIUM overconsumption (+201%), oil high (+30%), biomass low (-52%), constraint violations persist (NUCLEAR 112% over f_max), future techs deploying at ~100 GW despite f_max=100. Solver degeneracy NOT fully resolved.
**References:** v6 Block 6 results, 2017 reality.
**Status:** Valid diagnosis — identifies remaining gaps.

## 17. finland_typical_days_audit.md
Audit of k-medoids typical day selection in `esmc/preprocessing/temporal_aggregation.py`. Verifies preprocessing pipeline from Time_series.csv (8760h) through normalization, clustering, TD mapping.
**References:** `temporal_aggregation.py`, `Time_series.csv`, TD outputs.
**Status:** Valid audit.

## 18. manual_calibration_foundation.md
Step-by-step reference for manual calibration. Repository structure, data architecture (3-tier hierarchy), reality targets, model-to-reality mapping, key levers, common pitfalls.
**References:** `Data/2017/` directory tree, general ESMC workflow.
**Status:** Valid reference.

## 19. manual_calibration_workflow.md
Practical workflow guide. Data structure, run scripts, running the model, creating patches, comparing runs, troubleshooting. Written by Copilot on 2026-03-03.
**References:** `run_calib_manual.py`, patches, reality reference.
**Status:** Valid — but the runner script it documents is being replaced in this cleanup.

## 20. rerun_v5_fperc_comparison.md
Comparison between original `v5_fperc` and its reproduction (`v5_fperc_repro`). Reproduction used restored inputs but produced a 100x different objective (2.103e14 vs 2.324e16), confirming numerical sensitivity.
**References:** `v5_fperc_repro/`, `run_v5_fperc_repro.py`.
**Status:** Valid comparison report.

## 21. restore_v5_fperc_to_Data2017.md
Documents reverse-engineering and restoration of exact input state for `v5_fperc`. VERIFIED: PERFECT MATCH for all 169 tech and 35 resource values.
**References:** `v5_fperc/` `.dat` files, `Data/2017/FI/`.
**Status:** Valid — completed and verified restoration.
