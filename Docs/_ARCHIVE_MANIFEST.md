# Archive Manifest — 2026-03-11 Restart Cleanup

## Summary

Workspace cleaned for Finland 2017 calibration restart.
All files moved (nothing deleted). Archives are retrievable.

## Archive Locations

### `Docs/_archive_pre_restart/` (26 files)
Archived Docs:
- finland_2017_decision_log.md
- manual_calibration_workflow.md
- rerun_v5_fperc_comparison.md
- restore_v5_fperc_to_Data2017.md
- validation_plots_audit.md
- workflow_mess_diagnosis.md
- workflow_reset_findings.md
- audit_diagnostic/ (19 files — full v6-era diagnostic subfolder)

### `_archive_debug_scripts/` (8 files)
Root-level one-time debug/analysis scripts:
- align_inputs.py, check_f_min.py, check_resources_alignment.py
- check_technologies_update.py, debug_technologies.py, explore_inv.py
- verify_enspreso.py, update_dea_excel.py

### `scripts/_archive_pre_restart/` (2 files)
Old automated scripts:
- run_calib_2017.py, run_calib_case.py

### `calibration/_archive_patches/` (28 files)
All patch CSVs (p01–p21, block_future_techs variants, restore files, manual patches, relax_all).

### `Data/2017/FI/_archive_tech_backups/` (10 files)
Old FI/Technologies.csv backups and copies.
Kept on disk: .bak_20260308_184307 (v10-era), .bak_20260308_pre2035, Technologies_937940b_backup.

### `plots/_archive/` (8 folders)
Old calibration plot folders: v5, v5_rerun, v6, v7, v8, v11, methodical_Feb14, v6_blocks.

## Files Restored

- `Data/2017/02_REF_REGION/Technologies.csv` — restored to HEAD (DEA 2023 costs)

## Files Created

- `Data/2017/FI/Technologies.csv` — new v10-based restart file (23 rows, minimal disablings)
- `Docs/manual_fi_calibration_tutorial.md`
- `Docs/disabled_technologies_audit.md`
- `Docs/restart_active_working_set.md`
- `Docs/_ARCHIVE_MANIFEST.md` (this file)
