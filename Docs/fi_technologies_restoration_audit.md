# FI/Technologies.csv Restoration Audit

**Date:** 2026-03-10
**Author:** Copilot (automated calibration assistant)
**Status:** Pre-restoration — written before any file is changed

---

## What was found

`Data/2017/FI/Technologies.csv` on disk is the wrong file.

| Property | On disk (broken) | Backup pre2035 | Git 4ff4207 |
|---|---|---|---|
| Rows | 20 | 166 | 57 |
| Columns | f_min, f_max | f_min, f_max, fmin_perc, fmax_perc | f_min, f_max, fmin_perc, fmax_perc |
| WIND_ONSHORE f_min/f_max | 0 / 35 | 1.5 / 1.7 | 2.0 / 2.1 |
| NUCLEAR f_min/f_max | 0 / 5 | 2.76 / 2.8 | 2.5 / 2.8 |
| HYDRO_RIVER f_min/f_max | 0 / 4 | 1.9 / 2.1 | 1.9 / 2.1 |
| COAL_US f_min/f_max | ABSENT | 3.5 / 4.5 | 3.5 / 4.5 |
| CCGT f_min/f_max | ABSENT | 0.6 / 1.2 | 0.6 / 1.5 |
| DHN_COGEN_GAS f_min/f_max | ABSENT | 0.6 / 1.5 | 0.6 / 1.5 |
| DHN_COGEN_WOOD f_min/f_max | ABSENT | 2.5 / 15 | 2.5 / 1e5 |
| H2_ELECTROLYSIS | ABSENT | 0 / 100 | ABSENT |
| DIESEL_TO_JET_FUEL | ABSENT | 0 / 100 | ABSENT |

The broken file is a generic 2035-era template (20 rows, all f_min=0, wide f_max).
It was introduced by git commit `1d50d60` ("restore") which overwrote the calibrated
FI file. The REF_REGION/Technologies.csv was restored from backup in a prior session,
but FI/Technologies.csv was not.

---

## Why this is a structural baseline problem

Without the correct FI override file, the optimizer receives no meaningful capacity
bounds for Finland 2017. The REF_REGION defaults are f_min=0, f_max=1e15 for all
technologies. The broken FI file only overrides 20 of 166+ technologies, and those
overrides use 2035-era expansion limits (WIND_ONSHORE f_max=35 GW).

This produces a fundamentally wrong solution:
- Wind: 94 TWh (target 5 TWh) — 19× too high
- Coal/Gas/CHP: zero (target ~30 TWh combined)
- CO2: 10.7 Mt (target 41.2 Mt)
- Score: 256% (target <15%)

No amount of calibration patching can fix a wrong baseline file.

---

## Which backup is proposed

**`Data/2017/FI/Technologies.csv.bak_20260308_pre2035`** is proposed as the restore source.

Evidence supporting this choice:
1. **Comprehensive coverage**: 166 rows covering all technologies (vs 57 in git 4ff4207)
2. **Tighter generation bounds**: WIND_ONSHORE f_max=1.7 (vs 2.1 in 4ff4207), consistent with ~1.7 GW installed in Finland 2017
3. **Thermal generation present**: COAL_US 3.5–4.5, CCGT 0.6–1.2, DHN_COGEN_GAS 0.6–1.5, DHN_COGEN_WOOD 2.5–15
4. **Two identical backups agree**: `bak_20260308_pre2035` and `bak_20260308_184307` are byte-identical (confirmed)
5. **Timestamps indicate intent**: Both made on 2026-03-08, named "pre2035" = deliberate backup before the 2035-era overwrite
6. **Includes fmin_perc/fmax_perc**: IND_BOILER_WOOD fmin_perc=0.3, DHN_COGEN_WOOD fmin_perc=0.3, etc. — useful for future calibration even if `--no-fperc` is used now

The git 4ff4207 version is an alternative but has only 57 rows and looser f_max on
several key techs (DHN_COGEN_WOOD 1e5, IND_BOILER_WOOD 1e5). The pre2035 backup
is more conservative and comprehensive.

---

## What will be changed

1. Create a timestamped backup of the current broken file: `Technologies.csv.bak_20260310_pre_restore`
2. Copy `Technologies.csv.bak_20260308_pre2035` → `Technologies.csv`
3. Verify the restored file from disk (not editor buffer)

## What will NOT be changed

- `Data/2017/02_REF_REGION/Technologies.csv` — already correct
- `scripts/run_calib_manual.py` Stage A disabling — remains active
- Scoring targets in REALITY_TARGETS — unchanged
- No new patches, no manual capacity tweaks
- No cost changes
- `--no-fperc` flag — kept for this baseline run (fmin_perc/fmax_perc disabled)
