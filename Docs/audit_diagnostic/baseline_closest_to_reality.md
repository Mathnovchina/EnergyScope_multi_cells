# Baseline Closest to Reality

> Finland 2017 Calibration — Best Baseline Selection  
> Generated: 2024

This document identifies the calibration run closest to Finland 2017 reality and provides a reproducibility recipe.

---

## Executive Summary

Based on weighted percentage error scoring against Finland 2017 reality targets:

| Rank | Run | Score | Status |
|------|-----|-------|--------|
| **1** | `calib_2017_finland_v9` | 39.2% | **RECOMMENDED BASELINE** |
| 2 | `calib_2017_finland_v10_oil_constr` | 39.2% | Very close second |
| 3 | `calib_2017_finland` | 42.1% | Original good run |

The **v9** run is recommended as the starting baseline for further manual calibration.

---

## Top 3 Runs — Detailed Comparison

### 1. calib_2017_finland_v9 (Score: 39.2%)

| Metric | Model | Reality | Error |
|--------|-------|---------|-------|
| CO2 (MtCO2) | 16.8 | 41.2 | -59% ✗ |
| Elec Nuclear (TWh) | 20.8 | 21.6 | -4% ✓ |
| Elec Hydro (TWh) | 15.6 | 14.6 | +7% ✓ |
| Elec Wind (TWh) | 6.3 | 4.8 | +32% ⚠ |
| PE Biomass (TWh) | 43.5 | 100.0 | -56% ✗ |
| PE Coal (TWh) | 22.1 | 35.0 | -37% ⚠ |
| PE Gas (TWh) | 29.8 | 20.0 | +49% ⚠ |
| PE Nuclear (TWh) | 56.3 | 65.0 | -13% ✓ |
| PE Oil (TWh) | 0.0 | 82.0 | -100% ✗ |
| PE Hydro (TWh) | 15.6 | 15.0 | +4% ✓ |

**Strengths**: Excellent nuclear & hydro match  
**Weaknesses**: Zero oil, low biomass, very low CO2

### 2. calib_2017_finland_v10_oil_constr (Score: 39.2%)

| Metric | Model | Reality | Error |
|--------|-------|---------|-------|
| CO2 (MtCO2) | 18.2 | 41.2 | -56% ✗ |
| PE Oil (TWh) | 38.6 | 82.0 | -53% ✗ |
| PE Biomass (TWh) | 49.5 | 100.0 | -50% ✗ |
| PE Coal (TWh) | 13.9 | 35.0 | -60% ✗ |
| PE Gas (TWh) | 0.0 | 20.0 | -100% ✗ |

**Strengths**: Better oil representation than v9  
**Weaknesses**: Zero gas, lower coal

### 3. calib_2017_finland (Score: 42.1%)

| Metric | Model | Reality | Error |
|--------|-------|---------|-------|
| CO2 (MtCO2) | 24.5 | 41.2 | -41% ⚠ |
| PE Oil (TWh) | 70.4 | 82.0 | -14% ✓ |
| PE Biomass (TWh) | 66.9 | 100.0 | -33% ⚠ |
| PE Coal (TWh) | 0.0 | 35.0 | -100% ✗ |
| PE Hydro (TWh) | 26.7 | 15.0 | +78% ✗ |

**Strengths**: Best oil match, highest CO2 (closest to reality)  
**Weaknesses**: Zero coal, hydro overestimate

---

## Recommended Starting Point

For manual calibration, use **`calib_2017_finland`** (original) as the starting point because:

1. **Best CO2 match** (24.5 vs 41.2 MtCO2) — CO2 is the most important calibration metric
2. **Best oil match** (70.4 vs 82.0 TWh) — Captures transport sector
3. **Good biomass** (66.9 vs 100.0 TWh) — Better than v9

While v9 has the lowest overall score, the original run has better representation of the Finnish energy mix structure.

---

## Reproducibility Recipe

### Step 1: Verify Baseline Exists

```bash
ls case_studies/FI/calib_2017_finland/outputs/
```

Expected files:
- `Year_balance.csv`
- `Resources.csv`
- `Gwp_breakdown.csv`
- `Solve_info.csv`

### Step 2: Generate Validation Plots

```bash
python scripts/plot_validate_2017.py --run-name calib_2017_finland
```

### Step 3: Review Current State

```bash
python scripts/score_calib_runs.py
```

### Step 4: Create Calibration Patch

Create a file `calibration/patches/v12_coal_fix.csv`:

```csv
file,parameter,technology_or_resource,value
Technologies.csv,fmin_perc,DHN_COGEN_COAL,0.2
Technologies.csv,fmin_perc,COAL_US,0.1
Resources.csv,avail_exterior,COAL,50000
```

### Step 5: Run With Patch

```bash
python scripts/run_calib_manual.py \
    --run-name v12_coal_fix \
    --from-baseline calib_2017_finland \
    --patch calibration/patches/v12_coal_fix.csv \
    --description "Force coal CHP to match 35 TWh coal reality"
```

### Step 6: Compare Results

```bash
python scripts/plot_validate_2017.py --run-name v12_coal_fix
python scripts/score_calib_runs.py
```

---

## Key Configuration Files (calib_2017_finland)

### Technologies.csv (FI/)

Current capacity bounds:
```
NUCLEAR: f_min=2.5, f_max=2.8
HYDRO_DAM: f_min=1.1, f_max=1.3
HYDRO_RIVER: f_min=1.9, f_max=2.1
WIND_ONSHORE: f_max=2.1
```

Market share constraints:
```
CAR_GASOLINE: fmin_perc=0.55, fmax_perc=0.65
CAR_DIESEL: fmin_perc=0.30, fmax_perc=0.40
TRUCK_DIESEL: fmin_perc=0.90, fmax_perc=1.00
DHN_COGEN_WOOD: fmin_perc=0.3
DHN_COGEN_COAL: fmin_perc=0.3
```

### Resources.csv (FI/)

Resource ceilings:
```
GAS: avail_exterior=28000 GWh
COAL: avail_exterior=50000 GWh
LFO: avail_exterior=20000 GWh
WOOD: avail_local=110805 GWh
```

### Misc.json (FI/)

Modal shares:
```json
{
  "share_heat_dhn_min": 0.449,
  "share_heat_dhn_max": 0.451,
  "share_mobility_public_min": 0.160,
  "share_mobility_public_max": 0.162
}
```

---

## Remaining Calibration Gaps

| Gap | Priority | Suggested Fix |
|-----|----------|---------------|
| CO2 too low (-41%) | HIGH | Force more coal/gas in heating |
| Coal zero (-100%) | HIGH | Set `fmin_perc > 0` for COAL_US, DHN_COGEN_COAL |
| Biomass low (-33%) | MEDIUM | Increase `fmin_perc` for wood boilers/CHP |
| Hydro high (+78%) | MEDIUM | Check HYDRO_RIVER f_max constraint |
| Wind high (+33%) | LOW | Tighten WIND_ONSHORE f_max |

---

## Version History

| Run | Date | Key Changes |
|-----|------|-------------|
| calib_2017_finland | 2024-01 | Original baseline |
| v1-v3 | 2024-01 | f_perc mode testing |
| v4_fixed | 2024-02 | Fixed technology errors |
| v5_fperc | 2024-02 | f_perc mode enabled |
| v6_block* | 2024-03 | Block-by-block calibration |
| v7 | 2024-03 | **Failed** (solve_result=299) |
| v8_no_coal_us | 2024-03 | Disabled COAL_US |
| v9 | 2024-04 | Tightened constraints |
| v10_oil_constr | 2024-04 | Oil constraints |
| v11_heat_fix | 2024-04 | Heat sector fixes |

---

## Next Steps

1. Start from `calib_2017_finland`
2. Create patch to force coal usage (target: 35 TWh)
3. Adjust biomass forcing (target: 100 TWh)
4. Re-check CO2 (should increase to ~35-40 MtCO2)
5. Fine-tune electricity mix

---

*See also: [manual_calibration_foundation.md](manual_calibration_foundation.md)*
