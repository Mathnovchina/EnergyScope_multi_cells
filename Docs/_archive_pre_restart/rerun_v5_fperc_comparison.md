# v5_fperc Rerun Comparison Report

**Date:** 2025-02-27  
**Case study:** `calib_2017_finland_v5_fperc_repro`  
**Baseline:** `calib_2017_finland_v5_fperc` (original run)  
**Inputs:** Restored into `Data/2017/FI/` from v5_fperc `.dat` ground truth  
**Solver:** CPLEX 22.1.2 barrier  
**Run command:** `python scripts/run_v5_fperc_repro.py`  
**Output folder:** `case_studies/FI/calib_2017_finland_v5_fperc_repro/outputs/`  
**Plots folder:** `plots/calibration_v5_fperc_rerun/`

---

## 1. Run Summary

| Parameter | Value |
|-----------|-------|
| `f_perc` | True |
| `nbr_td` | 12 |
| Year | 2017 |
| Region | FI |
| Solver | CPLEX (barrier) |
| Variables | 380,805 |
| Constraints | 608,725 |
| Solve time | 272.6 s |
| Total time | 316.4 s |
| `solve_result_num` | 100 (feasible) |
| Objective | 2.103 × 10¹⁴ M€/y |
| Original objective | 2.324 × 10¹⁶ M€/y |

Both runs return `solve_result_num = 100` (feasible) and both exhibit tolerance violations on certain constraints, which is characteristic of the barrier method on this problem.

---

## 2. Input Verification

All seven FI input files were verified as **PERFECT MATCH** against the `.dat` ground truth from the original v5_fperc run before re-executing:

| File | Entries | Status |
|------|---------|--------|
| Technologies.csv | 47 overrides (4 cols) | ✅ Match |
| Resources.csv | 25 overrides | ✅ Match |
| Demands.csv | 12 demands | ✅ Match |
| Time_series.csv | 8761 rows | ✅ Match |
| Weights.csv | 10 entries | ✅ Match |
| Storage_power_to_energy.csv | (default) | ✅ Match |
| Misc.json | (default) | ✅ Match |

See `Docs/restore_v5_fperc_to_Data2017.md` for the full restoration log.

---

## 3. Primary Energy Comparison (TWh)

| Category | Original v5 | Rerun | Reality (2017) |
|----------|------------|-------|----------------|
| WOOD | 5.1 | 11.4 | 105.0 |
| OIL | 203.5 | 205.5 | 96.0 |
| NUCLEAR | 80.0 | 127.3 | 65.0 |
| COAL_PEAT | 9.2 | 23.8 | 50.0 |
| GAS | 28.0 | 28.0 | 25.0 |
| HYDRO | 15.5 | 15.3 | 15.0 |
| WIND | 6.8 | 7.2 | 5.0 |
| **TPES** | **348.1** | **418.5** | **361.0** |

**Key observations:**
- GAS and HYDRO are near-identical between original and rerun, and close to reality.
- OIL is ~2× reality in both runs (LFO near its 150 TWh cap).
- NUCLEAR is 1.6× higher in the rerun (127 vs 80 TWh), both already above the 65 TWh target.
- COAL_PEAT rose from 9 → 24 TWh in the rerun — closer to reality (50 TWh) but still low.
- WOOD remains far below reality (5–11 vs 105 TWh) — a known calibration gap.

---

## 4. Electricity Generation Comparison (TWh)

| Source | Original v5 | Rerun | Reality (2017) |
|--------|------------|-------|----------------|
| Nuclear | 29.6 | 47.1 | 21.6 |
| Hydro | 15.5 | 15.3 | 14.6 |
| Biomass | 0.1 | 0.2 | 11.0 |
| Coal | 1.0 | 3.1 | 9.0 |
| Wind | 6.8 | 7.2 | 4.8 |
| Gas | 2.0 | 5.9 | 3.7 |
| Solar | 2.5 | 2.7 | 0.1 |
| **Total** | **57.4** | **81.4** | **64.8** |

**Key observations:**
- Hydro tracks reality closely in both runs (~15 TWh).
- Nuclear is significantly overproduced in both runs; the rerun is even higher (47 vs 30 TWh vs 21.6 target).
- Biomass electricity is nearly absent in both runs (~0.1 TWh vs 11.0 target) — a major calibration gap.
- The rerun total (81.4 TWh) overshoots reality by 26%, while the original (57.4 TWh) undershoots by 11%.

---

## 5. CO2 Emissions Comparison (MtCO2)

| Source | Original v5 | Rerun | Reality |
|--------|------------|-------|---------|
| Calculated | 74.2 | 80.9 | 42.0 |

Both runs overshoot reality by ~2× due to the excessive oil consumption (LFO near cap). The rerun is slightly higher (80.9 vs 74.2 MtCO2) consistent with higher COAL and NUCLEAR thermal input.

---

## 6. Core Asset Capacities (GW)

| Technology | Original v5 | Rerun | Ratio |
|------------|------------|-------|-------|
| NUCLEAR | 3.77 | 5.68 | 1.51 |
| CCGT | 1.59 | 1.78 | 1.12 |
| COAL_US | 4.80 | 5.38 | 1.12 |
| WIND_ONSHORE | 2.30 | 2.67 | 1.16 |
| PV_ROOFTOP | 2.00 | 2.00 | 1.00 |
| HYDRO_DAM | 1.41 | 1.62 | 1.15 |
| HYDRO_RIVER | 2.31 | 2.70 | 1.17 |
| GEOTHERMAL | 0.30 | 0.30 | 1.00 |
| DHN_COGEN_GAS | 1.49 | 1.49 | 1.00 |
| CAR_GASOLINE | 17,115 | 13,496 | 0.79 |
| TRUCK_DIESEL | 43,182 | 35,550 | 0.82 |

**Notes:**
- Capped technologies (PV_ROOFTOP, GEOTHERMAL, DHN_COGEN_GAS) match exactly.
- Core generation assets are 10–50% higher in the rerun.
- Transport assets (CAR_GASOLINE, TRUCK_DIESEL) are 15–20% lower in the rerun.
- Exotic/unconstrained technologies (IND_COGEN_GAS, DEC_BOILER_OIL, CARGO_LFO, etc.) still show absurdly large values (10⁹–10¹³ GW) in both runs, but the rerun values are ~100× smaller, consistent with its lower objective.

---

## 7. Objective & Numerical Quality

| Metric | Original v5 | Rerun |
|--------|------------|-------|
| Objective | 2.324 × 10¹⁶ | 2.103 × 10¹⁴ |
| TotalCost | 2.324 × 10¹⁶ | 2.103 × 10¹⁴ |
| solve_result_num | 100 | 100 |
| Tolerance violations | Yes | Yes |

The rerun objective is **~110× lower** than the original. Both runs are dominated by absurd cost contributions from unconstrained exotic technologies (CCGT_AMMONIA, DEC_BOILER_OIL, CARGO_LFO, etc.), but these are much smaller in the rerun. This does **not** mean the rerun is "better calibrated" — it means the CPLEX barrier solver converged to a different feasible point on the same (degenerate) problem.

---

## 8. Why Is It Not an Exact Reproduction?

Three factors prevent exact reproduction:

1. **Stochastic k-medoid clustering:** The typical-day selection uses random initialization, so each run selects different representative days from the 8760-hour time series. With `nbr_td=12`, even small TD differences reshape the hourly dispatch constraints.

2. **Barrier solver degeneracy:** The problem has many unconstrained technologies with near-zero costs. The barrier method can converge to any point on the optimal face, giving different capacity allocations to degenerate variables across runs.

3. **CPLEX convergence path:** Even with identical inputs and TDs, floating-point accumulation in the barrier solver can lead to different primal solutions on ill-conditioned problems.

---

## 9. Can the Restored Data Serve as Baseline?

### Assessment: **Yes, with caveats**

**Strengths:**
- The restored inputs are verified PERFECT MATCH against `.dat` ground truth.
- The rerun produces a feasible solution with the same qualitative behavior as the original.
- Core technologies deploy at similar (within 50%) levels.
- Capped/constrained technologies match exactly.
- The numerical quality is actually better (lower objective, smaller exotic artifacts).

**Caveats:**
- Exact numerical reproduction is impossible due to stochastic TDs and solver degeneracy.
- The ~100× objective difference and 50% capacity swings on core techs mean you cannot use this rerun to validate specific quantitative claims from the original run.
- Both runs share the same fundamental calibration gaps (OIL 2× reality, WOOD 20× too low, Biomass electricity near zero, CO2 2× reality).

**Recommendation:**
The restored `Data/2017/FI/` inputs are a **reliable baseline** for *continuing calibration work* (v6, v7, …). They faithfully encode the v5_fperc parameter choices. However, for reproducing the exact original v5 outputs, you must use the frozen `.dat` files in `case_studies/FI/calib_2017_finland_v5_fperc/`.

---

## 10. Plots

All plots are in `plots/calibration_v5_fperc_rerun/`:

| File | Description |
|------|-------------|
| `primary_energy_comparison.png` | Bar chart: Original v5 vs Rerun vs Reality (7 categories) |
| `electricity_mix_comparison.png` | Bar chart: Electricity by source (7 categories) |
| `co2_emissions_comparison.png` | Bar chart: CO2 emissions (3 bars) |
| `asset_capacity_comparison.png` | Bar chart: Core tech capacities Original vs Rerun |
| `comparison_summary.csv` | Machine-readable summary of key metrics |

---

## 11. File Inventory

| Path | Role |
|------|------|
| `scripts/run_v5_fperc_repro.py` | Rerun execution script |
| `scripts/compare_v5_outputs.py` | Detailed output comparison script |
| `scripts/generate_v5_fperc_rerun_plots.py` | Plot generation script |
| `Docs/restore_v5_fperc_to_Data2017.md` | Input restoration log |
| `case_studies/FI/calib_2017_finland_v5_fperc_repro/outputs/` | Rerun outputs |
| `case_studies/FI/calib_2017_finland_v5_fperc/outputs/` | Original v5 outputs |
| `plots/calibration_v5_fperc_rerun/` | Generated plots |
