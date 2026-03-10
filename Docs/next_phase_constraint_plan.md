# Next Phase — Incremental Constraint Tightening

**Starting point**: `frozen_baseline` run (code=0, score=256.1%)  
**FI file**: 20 rows, all `f_min=0`, frozen as `Technologies.csv.frozen_baseline_20260310`

## Method

Add **one coherent block at a time** to `Data/2017/FI/Technologies.csv`.  
After each addition, run:
```
python scripts/run_calib_manual.py -n <block_name> --no-fperc
```
If infeasible, revert to the frozen baseline and relax the offending bound.

## Suggested order

### Block 1 — NUCLEAR
Add: `NUCLEAR,2.7,2.835`  
Rationale: Finland had 2.77 GW nuclear in 2017. Narrow band, low risk.

### Block 2 — WIND_ONSHORE
Add: `WIND_ONSHORE,2,2.1`  
Rationale: 2.04 GW installed. This is the biggest error source (1865%).

### Block 3 — HYDRO
Add: `HYDRO_DAM,1.21,2.2` and `HYDRO_RIVER,1,1.05`  
Rationale: Hydro is well-known and bounded.

### Block 4 — COAL_US + CCGT
Add: `COAL_US,0.5,2` and `CCGT,0.6,1.5`  
Rationale: Gas and coal generation. Currently unconstrained (Infinity f_max).

### Block 5 — Future tech disabling
Add rows with `f_min=0,f_max=0` for:
CAR_BEV, CAR_PHEV, CAR_FUEL_CELL, TRUCK_FUEL_CELL, TRUCK_ELEC,
SMR, DEC_ELEC_COLD, DEC_THHP_GAS_COLD, DHN_BOILER_COAL, CAR_METHANOL,
BUS_COACH_FC_HYBRIDH2, COAL_IGCC, CCGT_AMMONIA  
(Some overlap with Stage A — that's fine, belt-and-suspenders.)

### Block 6 — Heat sector (DHN)
Add DHN bounds from FI_937940b:
DHN_COGEN_GAS 0.6/2.5, DHN_COGEN_WOOD 1/50, DHN_BOILER_WOOD 3/50, etc.

### Block 7 — Heat sector (industrial + decentralized)
Add IND and DEC bounds from FI_937940b.

### Block 8 — Transport caps
Add transport bounds from FI_937940b.

## Recovery command

If any block causes infeasibility:
```
Copy-Item Data/2017/FI/Technologies.csv.frozen_baseline_20260310 Data/2017/FI/Technologies.csv -Force
```

## Reference

FI_937940b bounds: `Data/2017/FI_937940b/Technologies.csv` (63 rows)  
Audit: `Docs/fi_override_audit.md`  
Baseline run: `case_studies/FI/manual_runs/20260310_095416__stageA_verify/`  
Verification run: `case_studies/FI/manual_runs/20260310_125955__frozen_baseline/`
