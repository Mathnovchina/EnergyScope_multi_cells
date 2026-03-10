# stageA_verify Baseline — Diagnostic Note

**Run:** `20260310_095416__stageA_verify`
**Solver:** CPLEX 22.1.2 barrier, code=0 (optimal), obj=36096.37, 239 iterations
**Score:** 256.1% (target: ≤15%)

---

## 1. Root Cause: FI/Technologies.csv Not Restored

The dominant issue is that `Data/2017/FI/Technologies.csv` on disk contains 2035-era
generic defaults, NOT the calibrated 2017 bounds.

| Property | On disk (actual) | Expected (calibrated) |
|---|---|---|
| Rows | 20 | 58–167 |
| Columns | 3 (`Technologies param, f_min, f_max`) | 5 (+ `fmin_perc, fmax_perc`) |
| WIND_ONSHORE f_max | **35.0** | 1.7–2.1 |
| NUCLEAR f_min | 0.0 | 2.5–2.76 |
| NUCLEAR f_max | 5.0 | 2.8–3.0 |
| HYDRO_RIVER f_max | 4.0 | 1.05–2.1 |
| COAL_US | absent (inherits ∞) | f_min=0.5–3.5, f_max=2.0–4.5 |
| CCGT | absent (inherits ∞) | f_min=0.6, f_max=1.2–1.5 |
| DHN_COGEN_GAS | absent (inherits ∞) | f_min=0.6, f_max=1.5 |
| DHN_COGEN_WOOD | absent (inherits ∞) | f_min=2.5, f_max=15.0 |
| Transport techs | absent | CAR_GASOLINE fmin_perc=0.55, etc. |

**How it happened:** Commit `1d50d60` ("restore") replaced the calibrated FI file with
2035-era defaults. When REF_REGION/Technologies.csv was restored from backup in a
previous session, FI/Technologies.csv was not.

**Backups available:**
- `Data/2017/FI/Technologies.csv.bak_20260308_pre2035` — 167 rows, tight bounds
- `Data/2017/FI/Technologies.csv.bak_20260308_184307` — identical
- Git commit `4ff4207` ("Validation good prices") — 58 rows, 5 columns, tight bounds
- Directory `FI_937940b/` snapshot — 64 rows, tight bounds

---

## 2. Impact on Model Solution

Without tight FI capacity bounds, the cost-minimizing optimizer:
- Installs maximum cheap wind (35 GW → 94.3 TWh; reality: ~2 GW, 4.8 TWh)
- Skips all thermal generation (COAL_US=0, CCGT=0, DHN_COGEN_*=0)
- Deploys absurd 2050-era technologies (CAR_BEV 136 GW, H2_ELECTROLYSIS 2 GW)

### Key technology distortions

| Technology | Model (GW) | Model (TWh) | Reality (TWh) |
|---|---|---|---|
| WIND_ONSHORE | 35.0 | 94.3 | 4.8 |
| HYDRO_RIVER | 4.0 | 26.9 | ~13–15 |
| NUCLEAR | 3.08 | 22.9 | 21.6 |
| COAL_US | 0 | 0 | ~7 |
| CCGT | 0 | 0 | ~2 |
| DHN_COGEN_GAS | 0 | 0 | ~3 |
| DHN_COGEN_WOOD | 0 | 0 | ~8 |
| CAR_BEV | 136 | — | ~0 |
| H2_ELECTROLYSIS | 2.0 | 24.7 consumed | 0 |
| DIESEL_TO_JET_FUEL | 651 | — | small |

### Electricity balance
- Model total production: **168 TWh** (reality: ~67 TWh — 2.5× too high)
- Wind alone accounts for 56% of model production

---

## 3. Score Breakdown (14 metrics)

| Metric | Model | Target | Error% | Weight | Contribution |
|---|---|---|---|---|---|
| ELEC_WIND | 94.29 | 4.8 | 1864% | 1.0 | **1864.4** |
| PE_WIND | 94.29 | 5.0 | 1786% | 0.8 | **1428.7** |
| CO2 | 10.66 | 41.2 | 74% | 2.0 | 148.2 |
| PE_OIL | 13.61 | 82.0 | 83% | 1.5 | 125.1 |
| PE_COAL | 7.09 | 35.0 | 80% | 1.5 | 119.6 |
| ELEC_HYDRO | 26.91 | 14.6 | 84% | 1.2 | 101.2 |
| ELEC_CHP | 5.07 | 20.7 | 76% | 1.2 | 90.6 |
| ELEC_CONDENSATION | 0.00 | 3.3 | 100% | 0.8 | 80.0 |
| PE_HYDRO | 26.91 | 15.0 | 79% | 0.8 | 63.5 |
| PE_BIOMASS | 67.76 | 100.0 | 32% | 1.5 | 48.4 |
| ELEC_SOLAR | 0.00 | 0.044 | 100% | 0.3 | 30.0 |
| PE_GAS | 22.00 | 20.0 | 10% | 1.0 | 10.0 |
| ELEC_NUCLEAR | 22.94 | 21.6 | 6% | 1.5 | 9.3 |
| PE_NUCLEAR | 62.00 | 65.0 | 5% | 1.0 | 4.6 |

**Wind alone accounts for 80% of the total weighted error** (3293/4124).

---

## 4. Verified Correct

- ✅ Stage A disabling (34 techs) is active in the AMPL .dat file
- ✅ REF_REGION/Technologies.csv has correct 2017 DEA costs
- ✅ Scoring targets match `run_calib_manual.py` REALITY_TARGETS
- ✅ CHP grouping (13 techs) and condensation grouping (6 techs) are correct
- ✅ Solver status optimal, no infeasibility
- ✅ `--no-fperc` flag is active (disables fmin_perc/fmax_perc constraints)

---

## 5. Remaining Active Distortions (Stage B candidates)

These technologies are NOT disabled and produce nonzero output:
- SYN_METHANOLATION: 1.3 GW
- HABER_BOSCH: 0.23 GW
- METHANOL_TO_HVC: 0.95 GW
- DIESEL_TO_JET_FUEL: 651 GW
- BUS_COACH_CNG_STOICH: 1.1 GW
- TRUCK_NG: 25.5 GW

---

## 6. Recommended Fix Sequence

1. **MUST DO — Restore FI/Technologies.csv** from backup `bak_20260308_pre2035`
   (167 rows, tight 2017 bounds, includes fmin_perc/fmax_perc).
   This parallels the REF_REGION restoration already done. Without this,
   ALL calibration runs are meaningless.

2. **Re-run baseline** with restored FI file. Score should drop dramatically
   as the model is forced to match ~2017 installed capacities.

3. **Evaluate whether to enable fmin_perc/fmax_perc** (remove `--no-fperc`)
   since the calibrated FI file has those columns for transport share constraints.

4. **Stage B disabling** (21 techs) — apply after confirming the restored
   baseline is stable. Will remove SYN_METHANOLATION, HABER_BOSCH, etc.

---

## 7. VS Code Buffer Warning

`read_file` in this workspace returns the VS Code editor buffer, which still
shows the calibrated 5-column version from commit `4ff4207`. The actual file
on disk (confirmed by Python `open()` and `git diff HEAD`) is the 3-column
2035-era version. **Always verify file contents via terminal when in doubt.**
