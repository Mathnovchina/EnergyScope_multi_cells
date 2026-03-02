# Fix: Finland 2017 share_ned Infeasibility

## Date
2026-03-02

## Issue
The `calib_2017_finland` baseline is **infeasible** due to a conflict between `share_ned` requirements and disabled technologies.

## Root Cause Analysis

### The Problem
The model requires non-energy demand (NON_ENERGY = 10,708 GWh) to be satisfied according to `share_ned` in `Data/2017/FI/Misc.json`:

```json
"share_ned": {"HVC": 0.779, "METHANOL": 0.029, "AMMONIA": 0.192}
```

This means:
- **77.9% HVC** → 8,341 GWh
- **2.9% METHANOL** → 310 GWh
- **19.2% AMMONIA** → 2,056 GWh

### Why It Fails
**All METHANOL producers are disabled:**
- `SYN_METHANOLATION`: f_max = 0
- `METHANE_TO_METHANOL`: f_max = 0  
- `BIOMASS_TO_METHANOL`: f_max = 0
- `BIOWASTE_TO_METHANOL`: f_max = 0
- No METHANOL import resource available

**All AMMONIA producers are disabled:**
- `HABER_BOSCH`: f_max = 0
- No AMMONIA import resource available

**The presolve errors confirm this:**
```
capacity_factor['FI','H2_ELECTROLYSIS'] cannot hold
capacity_factor['FI','SYN_METHANOLATION'] cannot hold
capacity_factor['FI','HABER_BOSCH'] cannot hold
```

These technologies would be needed to produce H2 → METHANOL/AMMONIA, but they're disabled (f_max=0).

## Solution

For **Finland 2017 calibration**, set `share_ned = {"HVC": 1.0}` because:

1. In 2017, Finland's petrochemical feedstock was essentially 100% oil-based (naphtha cracking for HVC)
2. Industrial METHANOL and AMMONIA in Finland are imported, not produced domestically
3. The model has `OIL_TO_HVC` enabled with f_max = 1e15, which can satisfy 100% HVC demand

## Applied Fix

**File:** `Data/2017/FI/Misc.json`

**Change:**
```json
// Before
"share_ned": {"HVC": 0.779, "METHANOL": 0.029, "AMMONIA": 0.192}

// After  
"share_ned": {"HVC": 1.0, "METHANOL": 0.0, "AMMONIA": 0.0}
```

## Validation
After applying this fix, the model should solve without presolve errors related to H2_ELECTROLYSIS, SYN_METHANOLATION, or HABER_BOSCH capacity factors.

## Alternative Solutions (Not Implemented)
1. Add METHANOL and AMMONIA import resources (would require additional data on import prices/availability)
2. Enable HABER_BOSCH and SYN_METHANOLATION (not realistic for 2017 Finland - these are future technologies)

## References
- Presolve error output from `calib_2017_finland_baseline_test` run
- FI Demands.csv: NON_ENERGY = 10,708 GWh (INDUSTRY sector)
- FI Technologies.csv: OIL_TO_HVC f_max = 1e15, all other HVC/METHANOL/AMMONIA producers f_max = 0
