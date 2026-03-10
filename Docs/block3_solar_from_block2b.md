# Block 3 — Solar (from Block 2b) — FAILED

**Run name:** `block3_solar_from_block2b`
**Directory:** `case_studies/FI/manual_runs/20260310_151215__block3_solar_from_block2b/`
**Timestamp:** 2026-03-10 15:12
**Git:** `1d50d60a` on branch `Finland`

## Active substantive constraints attempted (5)

| Technology | f_min | f_max | Rationale |
|---|---|---|---|
| NUCLEAR | 2.7 | 2.835 | Finland 2017 nuclear fleet |
| WIND_ONSHORE | 2.0 | 2.1 | Finland 2017 onshore wind |
| WIND_OFFSHORE | 0.0 | 0.0 | No offshore wind in Finland 2017 |
| PV_UTILITY | 0.0 | 0.1 | Finland 2017 had ~0 utility-scale PV |
| PV_ROOFTOP | 0.0 | 0.3 | Finland 2017 had ~0.3 GW rooftop PV |

All constraints correctly propagated to .dat (verified in input_snapshot).

## Solve status

- **Primary (barrier):** code=100 — "feasible or optimal but numeric issue"
  - Objective: 5.23e+17 (essentially infinity)
  - Numeric violations: variable bounds up to 3E-05, algebraic constraints up to 6E+05
  - 134 barrier iterations, 0 simplex iterations
- **Fallback (dual simplex):** Never completed. log_fallback.txt ends at model compilation (213 lines). No solve result written.
- **No outputs directory, no run_metadata.json, no FAILURE_SUMMARY.md**
- **Run effectively FAILED**

## Likely root cause

With wind (onshore + offshore) and solar (utility + rooftop) all heavily capped, the model cannot supply enough electricity to meet demands. The remaining flexible supply consists mainly of:
- HYDRO (unconstrained, but limited by resource availability)
- CHP/cogeneration (already at high levels in Block 2b)
- Gas power (limited resource)
- Imports (capped at 25 TWh)

The Block 2b run required ~29 TWh from solar + 30 TWh from HYDRO_RIVER + 30 TWh from DEC_COGEN_OIL to balance. Removing solar without providing alternatives likely made the electricity balance impossible.

## Checkpoints

Current working file is still the Block 3 edited version (PV_UTILITY=0.0/0.1, PV_ROOFTOP=0.0/0.3). Must be restored to Block 2b before any further work.

Pre-block3 checkpoint: `Technologies.csv.block2b_offshore_zero_keep_20260310` (md5=385b578b)
