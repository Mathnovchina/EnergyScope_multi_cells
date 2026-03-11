# Finland 2017 — Pre-Run Recap (937940b State)

> **Date**: 2025-02-27  
> **Data commit**: 937940b (Feb 12 "validation")  
> **Script**: `scripts/run_feb14_repro.py`  
> **Case study output**: `case_studies/FI/calib_2017_finland_repro/`  
> **Solver**: CPLEX via AMPL | 12 typical days | f_perc = True

---

## Scenario Description

Single-country (FI) whole-energy-system optimization for 2017.  
Minimizes total annualized cost subject to capacity constraints, resource limits,
demand satisfaction, and a renewable-energy primary share target (41%).

## Key Data State (937940b)

### Technologies — 63 overrides
| Cluster | Notable values |
|---------|---------------|
| **Nuclear** | 2.7–2.835 GW (Loviisa + Olkiluoto 1&2) |
| **Hydro** | DAM 1.21–2.2, RIVER 1.0–1.05 GW |
| **Wind** | Onshore 2.0–2.1, Offshore 0–0.1 GW |
| **Coal** | COAL_US 0.5–2.0 GW (low floor — may underuse coal) |
| **Gas** | CCGT 0.6–1.5, DHN_COGEN_GAS 0.6–2.5 GW |
| **Transport** | CAR_BEV/PHEV/FUEL_CELL banned; CAR_HEV 0–50 GW uncapped |
| **Industrial** | IND_BOILER_WOOD 6–50, IND_BOILER_COAL 4–50 (fmin_perc=0.3) |
| **DHN** | DHN_COGEN_COAL 2.5–50 (fmin_perc=0.2), DHN_BOILER_COAL banned |

### Resources — 25 overrides
| Cluster | Notable values |
|---------|---------------|
| **Biomass** | WOOD 110,806 GWh local (c_op=0.022); 10,000 exterior |
| **Fossil caps** | GAS 25k, COAL 60k, OIL 50k, GASOLINE 30k, DIESEL 40k, LFO 50k, JET_FUEL 15k |
| **RE fuels** | All at avail_exterior = 0.001 (effectively disabled) |
| **H2/NH3/MeOH** | Disabled (avail_exterior = 0) |

### Misc (unchanged between commits)
- DHN share: 44.9–45.1%, Public mobility: 16.0–16.2%, Rail freight: 27.5–27.7%
- RE share primary: 41%, Elec import/export: 3 GW, Solar area: 346 km²

## NO Market Share Constraints (fmin_perc/fmax_perc)

At 937940b, the Technologies.csv has only 3 data columns: `f_min, f_max, fmin_perc`.
There is **NO fmax_perc column**. Only 2 technologies have fmin_perc > 0:
- IND_BOILER_COAL: fmin_perc = 0.3
- DHN_COGEN_COAL: fmin_perc = 0.2

**No transport share constraints** (CAR_GASOLINE, TRUCK_DIESEL, etc. are unconstrained).
**No heat sector caps** (gas/oil boilers uncapped).
The optimizer is free to choose any technology mix within absolute capacity bounds.

## Expected Weak Points

| # | Issue | Expected Impact |
|---|-------|----------------|
| 1 | **No transport share constraints** | Optimizer may choose unrealistic car modal split |
| 2 | **COAL_US only 0.5–2.0 GW** | May under-represent coal (reality: ~3.5 GW fleet) |
| 3 | **HYDRO_RIVER only 1.0–1.05 GW** | Well below Finnish reality (~3.2 GW) |
| 4 | **LFO_RE at 0.001** | Should prevent the 95 TWh anomaly seen in the existing outputs |
| 5 | **OIL resource** | Silently ignored (not in REF_REGION — orphan override) |
| 6 | **WOOD exterior 10,000 GWh** | Allows wood import (unusual — Finland is biomass-sufficient) |
| 7 | **GAS at c_op=0.20** | 200 €/MWh — 10× higher than later calibrations (0.02). May suppress gas use. |
| 8 | **Grid losses 8.64%** | Finland reality ~3%, over-penalizes electricity |
| 9 | **DH losses 5%** | Finland reality ~8.5%, under-penalizes DH heat |
| 10 | **2035 technology costs** | 153/170 techs at future cost levels |
| 11 | **2015 demands/time-series** | ~2 years stale vs 2017 |
| 12 | **k-medoids non-determinism** | Different TD selection → different results each run |

## Finland 2017 Reality Indicators (comparison targets)

| Indicator | Finland 2017 reality | Source |
|-----------|---------------------|--------|
| **Total primary energy** | ~380 TWh | Statistics Finland |
| **Electricity generation** | 65.1 TWh | Statistics Finland |
| **Nuclear** | 21.6 TWh (33.1%) | TVO/Fortum |
| **Hydro** | 14.6 TWh (22.4%) | Statistics Finland |
| **Wind** | 4.8 TWh (7.4%) | Finnish Wind Power Assoc |
| **CHP** | 25.0 TWh (38.4%) | Statistics Finland |
| **Condensation (coal/gas)** | 4.1 TWh (6.3%) | Statistics Finland |
| **Solar** | 0.04 TWh (0.06%) | Statistics Finland |
| **Net imports** | 20.4 TWh | ENTSO-E |
| **Coal TPES** | ~35 TWh | Statistics Finland |
| **Gas TPES** | ~20 TWh | Statistics Finland |
| **Oil TPES** | ~82 TWh | Statistics Finland |
| **Biomass TPES** | ~100 TWh | Statistics Finland |
| **CO2 emissions** | 41.2 MtCO2 | Statistics Finland |
| **DH production** | 36.5 TWh | Finnish Energy |
| **DH share of space heating** | ~45% | Finnish Energy |
