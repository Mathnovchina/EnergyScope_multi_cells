# Manual Calibration Foundation

> Finland 2017 Energy System Calibration — Step-by-Step Guide  
> Last updated: 2024

This document provides a complete reference for manual calibration of the Finland 2017 energy system in EnergyScope Multi-Cells.

---

## Table of Contents

1. [Repository Structure](#1-repository-structure)
2. [Data Architecture](#2-data-architecture)
3. [Reality Targets (Finland 2017)](#3-reality-targets-finland-2017)
4. [Model-to-Reality Mapping](#4-model-to-reality-mapping)
5. [Key Levers for Calibration](#5-key-levers-for-calibration)
6. [Common Pitfalls](#6-common-pitfalls)
7. [Workflow Commands](#7-workflow-commands)
8. [Result Interpretation](#8-result-interpretation)

---

## 1. Repository Structure

```
EnergyScope_multi_cells/
├── Data/
│   └── 2017/
│       ├── 00_INDEP/           # Universal constants (efficiencies, global params)
│       │   ├── Layers_in_out.csv    # Technology conversion matrix (~175 rows)
│       │   ├── Resources_indep.csv  # Global resource definitions
│       │   └── Misc_indep.json      # Network losses, default shares
│       ├── 02_REF_REGION/      # Default technology data (170+ technologies)
│       │   └── Technologies.csv     # Base costs, capacities
│       └── FI/                 # Finland-specific overrides (HIGHEST PRIORITY)
│           ├── Technologies.csv     # f_min/f_max, fmin_perc/fmax_perc
│           ├── Resources.csv        # avail_local, avail_exterior, c_op
│           ├── Demands.csv          # End-use demands (11 categories)
│           ├── Misc.json            # DHN share, modal splits
│           └── Time_series.csv      # 8760h profiles
├── case_studies/
│   └── FI/
│       └── calib_2017_finland*/     # Run directories with outputs
├── calibration/
│   ├── reality/
│   │   └── finland_2017_reference.csv  # Reality targets
│   └── run_rankings.csv                # Scored run comparison
└── scripts/
    ├── run_calib_manual.py      # Manual calibration runner
    ├── plot_validate_2017.py    # Validation plot generator
    └── score_calib_runs.py      # Run scoring/ranking
```

### Override Priority

```
FI/ (highest) > 02_REF_REGION/ > 00_INDEP/ (lowest)
```

When calibrating, you typically modify files in `Data/2017/FI/`.

---

## 2. Data Architecture

### 2.1 Technologies.csv

Key columns for calibration:

| Column | Description | Calibration Use |
|--------|-------------|-----------------|
| `f_min` | Minimum installed capacity (GW) | Force existing capacity |
| `f_max` | Maximum installed capacity (GW) | Cap at 2017 real capacity |
| `fmin_perc` | Minimum output share (0-1) | Force technology to produce at least X% |
| `fmax_perc` | Maximum output share (0-1) | Cap technology at X% of its layer |
| `c_inv` | Investment cost (€/kW) | Affects economic ranking |
| `c_maint` | Maintenance cost (€/kW/yr) | Affects operating decisions |
| `lifetime` | Asset lifetime (years) | Affects annualized costs |
| `c_p` | Capacity factor (-) | Links installed to annual output |

### 2.2 Resources.csv

| Column | Description | Calibration Use |
|--------|-------------|-----------------|
| `avail_local` | Local resource availability (GWh) | Biomass, hydro, wind potential |
| `avail_exterior` | Import availability (GWh) | Caps on fossil fuel imports |
| `c_op_local` | Local extraction cost (€/kWh) | Usually 0 for renewables |
| `c_op_exterior` | Import cost (€/kWh) | Sets fuel prices |

### 2.3 Layers_in_out.csv (00_INDEP)

The conversion efficiency matrix. **Generally do not modify** — it defines technology physics.

Example: `NUCLEAR` row shows:
- ELECTRICITY output: +1.0 (produces 1 unit elec)
- URANIUM input: -2.7027 (consumes 2.7 units uranium per unit elec = 37% efficiency)

---

## 3. Reality Targets (Finland 2017)

Reference file: `calibration/reality/finland_2017_reference.csv`

### Primary Energy Supply (TWh)

| Category | Value | Source |
|----------|-------|--------|
| Biomass (wood + biowaste) | ~100 | Statistics Finland |
| Oil products | ~82 | IEA |
| Natural Gas | ~20 | IEA |
| Coal + Peat | ~35 | Statistics Finland |
| Nuclear (thermal) | ~65 | IAEA |
| Hydro | ~15 | Fingrid |
| Wind | ~5 | Fingrid |

### Electricity Generation (TWh)

| Technology | Generation | Share |
|------------|------------|-------|
| Nuclear | 21.6 | 33.1% |
| Hydro | 14.6 | 22.4% |
| Wind | 4.8 | 7.4% |
| CHP (all types) | 25.0 | 38.4% |
| Solar | 0.04 | 0.06% |
| **Total** | **65.1** | 100% |

### District Heating

- DH production: 36.5 TWh
- DH share of space heating: ~45%

### Emissions

- CO2: **41.2 MtCO2** (critical calibration target)

---

## 4. Model-to-Reality Mapping

### 4.1 Primary Energy to Resources

| Reality Metric | Model Resource(s) | Notes |
|----------------|-------------------|-------|
| Biomass | WOOD + WET_BIOMASS + BIOWASTE | Sum local consumption |
| Oil | GASOLINE + DIESEL + LFO + JET_FUEL | Exclude _RE variants (synthetic) |
| Gas | GAS | Exterior import |
| Coal | COAL | Exterior import |
| Nuclear | URANIUM | Thermal input (÷0.37 → elec) |
| Hydro | RES_HYDRO | Resource consumption |
| Wind | RES_WIND | Resource consumption |

### 4.2 Electricity to Technologies

| Reality Metric | Model Technology(ies) |
|----------------|----------------------|
| Nuclear elec | NUCLEAR (ELECTRICITY column in Year_balance) |
| Hydro elec | HYDRO_DAM + HYDRO_RIVER |
| Wind elec | WIND_ONSHORE + WIND_OFFSHORE |
| CHP | DHN_COGEN_* + IND_COGEN_* + DEC_COGEN_* |
| Solar | PV_ROOFTOP + PV_UTILITY |

### 4.3 CO2 Emissions

From `Gwp_breakdown.csv`: Sum of `CO2_net` column ÷ 1000 = MtCO2

---

## 5. Key Levers for Calibration

### 5.1 Forcing Existing Capacity (f_min/f_max)

```csv
# Technologies.csv (FI/)
Technologies,f_min,f_max,...
NUCLEAR,2.5,2.8,...       # Force 2.5-2.8 GW nuclear (actual: 2.77 GW)
HYDRO_DAM,1.1,1.3,...     # Force existing hydro capacity
```

### 5.2 Forcing Market Shares (fmin_perc/fmax_perc)

```csv
# Technologies.csv (FI/)
Technologies,fmin_perc,fmax_perc,...
CAR_GASOLINE,0.55,0.65,...     # Force 55-65% gasoline cars
DHN_COGEN_WOOD,0.3,1.0,...     # Force at least 30% wood CHP in DHN
```

### 5.3 Capping Resources (avail_exterior)

```csv
# Resources.csv (FI/)
Resources,avail_exterior,...
GAS,28000,...        # Cap gas at 28 TWh (actual: ~20-25 TWh)
COAL,50000,...       # Cap coal at 50 TWh
LFO,20000,...        # Cap light fuel oil
```

### 5.4 Adjusting Prices (c_op)

```csv
# Resources.csv (FI/)
Resources,c_op_exterior,...
GAS,0.025,...        # €0.025/kWh for gas
COAL,0.015,...       # €0.015/kWh for coal
```

---

## 6. Common Pitfalls

### 6.1 Nuclear Overproduction

**Symptom**: Nuclear produces way more than 22 TWh  
**Cause**: f_max too high or other generators too constrained  
**Fix**: Set `f_max = 2.8` GW for NUCLEAR, ensure CHP alternatives available

### 6.2 Oil Explosion

**Symptom**: LFO/LFO_RE consumption >> 100 TWh  
**Cause**: Model substitutes oil for constrained alternatives  
**Fix**: Reduce `avail_exterior` for LFO, check DEC heating diversification

### 6.3 Zero Coal Despite Reality

**Symptom**: COAL consumption = 0, reality = 35 TWh  
**Cause**: Coal technologies have `f_max = 0` or coal CHP not forced  
**Fix**: Set `fmin_perc > 0` for COAL_US or DHN_COGEN_COAL

### 6.4 CO2 Too Low

**Symptom**: Model CO2 << 41 MtCO2  
**Cause**: Too much electrification, not enough fossil  
**Fix**: Force fossil heating shares, increase fossil fuel availability

### 6.5 Solve Failures (result_num = 299)

**Symptom**: All outputs = 0, solve_result = 299  
**Cause**: Infeasible constraints (sum of fmin_perc > 1, contradictory bounds)  
**Fix**: Relax constraints, check fmin_perc sums per layer

---

## 7. Workflow Commands

### 7.1 Score Existing Runs

```bash
python scripts/score_calib_runs.py
```

Output: Weighted percentage error score for all runs, ranked best-to-worst.

### 7.2 Generate Validation Plots

```bash
python scripts/plot_validate_2017.py --run-name v9
```

Generates in `case_studies/FI/calib_2017_finland_v9/validation_plots/`:
- `pe_comparison.png` — Primary energy bar chart
- `elec_comparison.png` — Electricity mix bar chart
- `error_chart.png` — Error heatmap
- `validation_summary.md` — Tabular summary

### 7.3 Run Manual Calibration

```bash
# Clone baseline and run with default settings
python scripts/run_calib_manual.py --run-name v12_test --from-baseline calib_2017_finland_v9

# Apply patch file
python scripts/run_calib_manual.py --run-name v12_patch --patch patches/my_changes.csv

# Dry run (prepare but don't execute)
python scripts/run_calib_manual.py --run-name v12_test --dry-run
```

### 7.4 Patch File Format

```csv
file,parameter,technology_or_resource,value
Technologies.csv,f_max,NUCLEAR,2.8
Technologies.csv,fmin_perc,DHN_COGEN_COAL,0.2
Resources.csv,avail_exterior,COAL,40000
```

---

## 8. Result Interpretation

### 8.1 Output Files

| File | Contains |
|------|----------|
| `Year_balance.csv` | Annual flows per technology (columns = layers) |
| `Resources.csv` | Resource consumption (R_year_local + R_year_exterior) |
| `Gwp_breakdown.csv` | CO2 emissions by technology (CO2_net column) |
| `Assets.csv` | Installed capacities (F_Year column) |
| `Solve_info.csv` | Solver status (solve_result_num: 0=optimal, 100=warnings, 299=failed) |

### 8.2 Score Interpretation

| Score | Interpretation |
|-------|----------------|
| < 30% | Excellent — close to reality |
| 30-50% | Good — minor gaps remain |
| 50-100% | Acceptable — significant gaps |
| > 100% | Poor — major calibration issues |

### 8.3 Priority Metrics

1. **CO2 emissions** (weight 2.0) — Most important calibration target
2. **Biomass PE** (weight 1.5) — Finland biomass culture
3. **Oil PE** (weight 1.5) — Transport sector
4. **Coal PE** (weight 1.5) — CHP and industry
5. **Nuclear elec** (weight 1.5) — Baseload electricity

---

## References

- Statistics Finland: stat.fi/til/ehk/index_en.html
- Finnish Energy: energia.fi/en
- Fingrid: fingrid.fi/en
- IEA Finland Energy Balance: iea.org/data-and-statistics
- Excel workbook: `Data/exogenous_data/Finland_MASTER_Calibration_old_UPDATED.xlsx`

---

*Document generated by manual_calibration_foundation.md builder*
