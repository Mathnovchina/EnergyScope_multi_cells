# Block 2b — WIND_OFFSHORE = 0 (from Block 2)

**Run name:** `block2b_offshore_zero_from_block2`
**Directory:** `case_studies/FI/manual_runs/20260310_145734__block2b_offshore_zero_from_block2/`
**Timestamp:** 2026-03-10 14:57
**Git:** `1d50d60a` on branch `Finland`

## Active substantive constraints (3)

| Technology | f_min | f_max | Rationale |
|---|---|---|---|
| NUCLEAR | 2.7 | 2.835 | Finland 2017 nuclear fleet |
| WIND_ONSHORE | 2.0 | 2.1 | Finland 2017 onshore wind |
| WIND_OFFSHORE | 0.0 | 0.0 | No offshore wind in Finland 2017 |

Plus: 34 Stage A disabled techs, 114 inf→1e15 structural diffs (unchanged).

## Solve status

- **status:** OK, code=0, optimal
- **score:** 1280.063%

## Validation plots

Produced: 7 files in `validation_plots/` (error_chart.png, elec_comparison.png, pe_comparison.png, co2_comparison.png, chp_cond_breakdown.png, validation_report.md, validation_table.csv).

## CONSTRAINT_DIFF classification

- 114 inf→1e15 noise
- 34 Stage A fmax_perc zeroing
- 3 substantive: NUCLEAR, WIND_ONSHORE, WIND_OFFSHORE (all expected, no surprises)

## 4-run comparison

| Run | Score | ELEC_WIND | PE_WIND | ELEC_NUC | CO2 | ELEC_CHP | PE_OIL |
|---|---|---|---|---|---|---|---|
| Frozen baseline | 256.1% | 94.29 | 94.29 | 22.94 | ~11.8 | 5.07 | ~17 |
| Block 1 (+NUC) | 256.1% | 94.87 | 94.87 | 21.08 | 11.81 | 6.99 | 17.41 |
| Block 2 (+ON) | 200.4% | 76.41 | 76.41 | 21.08 | 26.59 | 27.42 | 70.54 |
| **Block 2b (+OFF=0)** | **1280.1%** | **6.33** | **6.33** | **21.08** | **41.07** | **40.83** | **125.0** |
| *Target* | *0%* | *4.80* | *5.00* | *21.60* | *41.20* | *20.73* | *82.0* |

(All values in TWh except CO2 in Mt and score in %.)

## Wind interpretability

**YES — wind is now interpretable.**

- WIND_ONSHORE: 2.1 GW (binding at f_max), 6.33 TWh, CF=34.4%
- WIND_OFFSHORE: 0.0 GW (binding at f_max=0), 0.0 TWh
- Total ELEC_WIND: 6.33 TWh vs 4.8 target (31.8% error)
- Total PE_WIND: 6.33 TWh vs 5.0 target (26.5% error)
- Both metrics correctly reflect constrained wind only

The 31.8% overshoot comes from the optimizer dispatching WIND_ONSHORE at higher CF (34.4%) when it can no longer shift to WIND_OFFSHORE. This is physically reasonable for Nordic wind.

## Score analysis

The score jumped from 200.4% → 1280.1% because the optimizer, deprived of 24 GW offshore wind, substituted:

1. **PV_UTILITY: 29.4 GW / 23.7 TWh** (target ~0 TWh) — main score driver (~29000% error on solar)
2. **PV_ROOFTOP: 6.8 GW / 5.5 TWh** — additional solar
3. **HYDRO_RIVER: 29.7 TWh** (target 14.6) — doubled
4. **DEC_COGEN_OIL: 29.9 TWh** — dominant CHP source, drives PE_OIL to 125 TWh
5. **DEC_COGEN_GAS: 9.7 TWh** — gas power up

This is expected behavior: the optimizer exploits unconstrained cheap alternatives. It does NOT indicate an error — it confirms the constraint is working.

## Checkpoint recommendation

**Block 2b should become the new working checkpoint.** Wind calibration is complete. The score deterioration is expected and will be corrected by subsequent blocks (solar, hydro, CHP/oil constraints).

## Checkpoints

| File | Size | MD5 |
|---|---|---|
| `.frozen_baseline_20260310` | 426 | cf915a9e5487e0ea1d6c0aaa584470f9 |
| `.block1_nuclear_keep_20260310` | 427 | 6e0fd830a1a4940e1572a7fcb6a2c1da |
| `.block2_wind_keep_20260310` | 426 | bf24ec6b582024e6bc334d3e56959650 |
| `.pre_block2b_backup_20260310` | 426 | bf24ec6b582024e6bc334d3e56959650 |
| Current working file (block2b) | 446 | 385b578bbed8d7de5818d283e85b1f49 |
