# Frozen Baseline Integrity Check

**Date**: 2026-03-10  
**Phase**: Diagnostics (pre-calibration)

## Summary

All 3 integrity checks **PASSED**. The frozen baseline is intact and the diagnostic
infrastructure is correctly integrated.

---

## CHECK 1: Frozen Baseline Run Folder

| Field   | Value |
|---------|-------|
| Run     | `20260310_095416__stageA_verify` |
| code    | 0 |
| status  | OK |
| score   | 256.13% |
| outputs/ | present |
| input_snapshot/reg_technologies.dat | present |

**Result: PASS**

## CHECK 2: Frozen File Integrity

| File | Size | MD5 |
|------|------|-----|
| `Technologies.csv.frozen_baseline_20260310` | 426 bytes | `cf915a9e5487e0ea1d6c0aaa584470f9` |
| `Technologies.csv` (current) | 426 bytes | `cf915a9e5487e0ea1d6c0aaa584470f9` |

- Content: 20 rows (all f_min = 0, various f_max)
- MD5 matches value recorded in `baseline_notes.md`
- Current working file is byte-identical to frozen backup

**Result: PASS**

## CHECK 3: Stage A & Diagnostic Infrastructure

| Component | Status |
|-----------|--------|
| `DISABLED_TECH_STAGE_A` | 34 technologies |
| `apply_fi2017_disabling()` called in main | YES |
| fmin_perc / fmax_perc zeroed in disabling | YES |
| `generate_constraint_diff()` present | YES |
| `_build_infeasibility_diagnostics()` present | YES |

**Result: PASS**

---

## Conclusion

The frozen baseline is untouched, the working file matches the backup exactly, and all
diagnostic functions (CONSTRAINT_DIFF.md, infeasibility diagnostics in FAILURE_SUMMARY.md)
are properly integrated into the run pipeline.

Ready to proceed to verification run `baseline_diagnostics_check`.
