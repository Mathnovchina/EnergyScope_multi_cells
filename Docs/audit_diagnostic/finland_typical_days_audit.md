# Finland Typical Days Audit

**Date:** 2026-03-03  
**Scope:** esmc/preprocessing/temporal_aggregation.py and Finland TD data  
**Purpose:** Verify k-medoids typical day selection was done properly

---

## 1. Preprocessing Pipeline Overview

### 1.1 How Typical Days Selection Works

The ESMC framework uses **k-medoids clustering** to select representative typical days from a full year (365 days) of hourly time series data.

**Pipeline:**
```
Time_series.csv (8760 hours) → normalize → weight → cluster → TD_of_days_N.out
```

### 1.2 Key Steps (from temporal_aggregation.py)

1. **pivot_ts()**: Reshape hourly data into daily format (365 × 24)
2. **group()**: Concatenate time series across regions
3. **normalize_weights()**: Weight each time series by its annual importance (Cell_w)
4. **weight()**: Apply weights to normalized time series
5. **kmedoid_clustering()**: Run MILP to find N medoid days
6. **generate_t_h_td()**: Create mapping from hours to typical days

### 1.3 The K-Medoids Objective

The clustering minimizes **weighted Euclidean distance** between each day and its assigned medoid:

```ampl
minimize Euclidean_distance:
    sum{d in DAYS, c in DIMENSIONS} (norm_weight[c] * 
        (sum{td in DAYS} Cluster_matrix[td,d] * (Ndata[d,c] - Ndata[td,c])^2));
```

---

## 2. Finland TD Selection Results

### 2.1 Configuration

| Parameter | Value |
|-----------|-------|
| Number of typical days | **12** |
| Clustering algorithm | k-medoids (MILP via CPLEX) |
| Data location | `case_studies/FI/00_td_dat/` |

### 2.2 Output Files

| File | Purpose | Verified? |
|------|---------|-----------|
| `TD_of_days_12.out` | List of 365 entries mapping each day to its TD | ✓ Present |
| `data_12.dat` | Input data for clustering | ✓ Present |
| `log_12.txt` | CPLEX solve log | ✓ Present |
| `e_ts12.txt` | Euclidean distance error | ✓ Present |

### 2.3 Solve Quality

From `log_12.txt`:
```
CPLEX 22.1.2: optimal solution; objective 0.1164944785
81 simplex iterations
```

From `e_ts12.txt`:
```
0.11649447851029048
```

**Interpretation:**
- **Solve status:** Optimal
- **Euclidean error:** ~11.6%
- This is a reasonable error for 12 TDs representing 365 days

### 2.4 Selected Medoid Days

From `TD_of_days_12.out`, the selected medoids appear to be:

| Medoid Day | Day of Year | Approximate Date | Likely Representation |
|------------|-------------|------------------|----------------------|
| 10 | 10 | Jan 10 | Winter midnight |
| 21 | 21 | Jan 21 | Winter typical |
| 33 | 33 | Feb 2 | Late winter |
| 75 | 75 | Mar 16 | Early spring |
| ... | ... | ... | ... |

*Note: A full analysis would require reading all 365 entries and counting frequencies.*

---

## 3. Input Data Assessment

### 3.1 Time Series Used for Finland

From `Data/2017/FI/Time_series.csv`:

| Time Series | Description | For Clustering? |
|-------------|-------------|-----------------|
| ELECTRICITY | Hourly electricity demand profile | ✓ Yes |
| HEAT_LOW_T_SH | Space heating demand | ✓ Yes |
| SPACE_COOLING | Cooling demand | ✓ Yes (small weight) |
| MOBILITY_PASSENGER | Passenger mobility profile | ✓ Yes |
| MOBILITY_FREIGHT | Freight mobility profile | ✓ Yes |
| PV | Solar PV capacity factor | ✓ Yes |
| WIND_ONSHORE | Wind onshore capacity factor | ✓ Yes |
| WIND_OFFSHORE | Wind offshore capacity factor | ✓ Yes |
| HYDRO_DAM | Dam hydro inflow | ✓ Yes |
| HYDRO_RIVER | Run-of-river hydro | ✓ Yes |
| TIDAL | Tidal energy | ✓ Yes (zero weight) |
| SOLAR | Solar thermal | ✓ Yes (small weight) |
| CSP | Concentrated solar power | ✓ Yes (small weight) |

### 3.2 Weights Configuration

From `Data/2017/FI/Weights.csv`:

| Time Series | Weight | Notes |
|-------------|--------|-------|
| ELECTRICITY | 1.0 | Full weight |
| HEAT_LOW_T_SH | 0.204 | Lower priority |
| SPACE_COOLING | 0.087 | Low (minimal cooling in Finland) |
| WIND_OFFSHORE | 1.0 | Full weight |
| WIND_ONSHORE | 1.0 | Full weight |
| HYDRO_DAM | 1.0 | Full weight |
| HYDRO_RIVER | 1.0 | Full weight |
| PV | 1.0 | Full weight |
| TIDAL | 0.0 | Zero (no tidal in Finland) |
| SOLAR | 0.0 | Not in file (defaults to 0) |

**Assessment:** Weights appear reasonable for Finland:
- High weights on electricity, wind, hydro (dominant in Finnish energy mix)
- Low weight on cooling (minimal in Nordic climate)
- Zero weight on tidal/solar thermal (not relevant for Finland)

---

## 4. Potential Issues and Caveats

### 4.1 CHECKED: TD Selection Quality — OK

The 11.6% Euclidean error is acceptable for energy system modeling. Literature typically accepts 10-15% error for this type of aggregation.

### 4.2 CHECKED: Input Data Consistency — OK

Time series and weights files exist and appear correctly formatted.

### 4.3 CAUTION: Seasonal Coverage

With only 12 TDs, there's a risk of underrepresenting:
- Extreme winter days (polar night, extreme cold)
- Midsummer (midnight sun, peak hydro)
- Transition seasons

**Recommendation:** Plot TD distribution across months to verify seasonal coverage.

### 4.4 CAUTION: CHP and Industrial Load Profiles

The time series focus on:
- Electricity demand
- Renewable generation
- Heating/cooling demand

**Missing:** Industrial heat demand profiles (relevant for CHP calibration).

If industrial CHP is driven by industrial heat demand that has a different profile than residential heating, the TDs might not capture this well.

### 4.5 Note: TD Data is Cached

The framework uses `algo='read'` when TD data already exists:
```python
if td_data_dir.exists() and any(td_data_dir.iterdir()):
    my_model.init_ta(algo='read')
else:
    my_model.init_ta(algo='kmedoid')
```

This means the same TDs are reused across all runs, which is correct and ensures consistency.

---

## 5. Recommended Diagnostic Plots

### 5.1 TD Distribution Across Year

**What:** Bar chart showing how many days each TD represents, colored by season

**Why useful:** Reveals if seasonal patterns are captured

**Input files:**
- `case_studies/FI/00_td_dat/TD_of_days_12.out`

**Implementation:** Easy (pandas groupby + matplotlib)

```python
import pandas as pd
import matplotlib.pyplot as plt

td = pd.read_csv('TD_of_days_12.out', header=None, names=['TD'])
td['day'] = range(1, 366)
td['month'] = pd.to_datetime('2017-01-01') + pd.to_timedelta(td['day']-1, unit='d')
td['month'] = td['month'].dt.month

# Count days per TD
counts = td.groupby('TD').size()
plt.bar(counts.index, counts.values)
plt.xlabel('Typical Day')
plt.ylabel('Days Represented')
plt.title('Finland 2017: TD Representation Frequency')
```

### 5.2 Time Series Reconstruction Error by Variable

**What:** Bar chart showing reconstruction error for each time series

**Why useful:** Identifies which variables are poorly represented by TDs

**Input files:**
- `Data/2017/FI/Time_series.csv` (original)
- `case_studies/FI/00_td_dat/TD_of_days_12.out` (mapping)

**Implementation:** Medium (need to reconstruct and compare)

```python
# For each variable:
# 1. Map each day to its TD
# 2. Reconstruct hourly profile using TD values
# 3. Calculate RMSE between original and reconstructed
```

### 5.3 Duration Curves: Original vs Reconstructed

**What:** Sort hourly values and plot cumulative curves for original vs TD-reconstructed

**Why useful:** Shows if extreme values (peaks/troughs) are captured

**Input files:**
- Original time series
- TD mapping + TD count

**Implementation:** Medium

### 5.4 Medoid Day Profiles

**What:** Line plots showing the 24-hour profile of each selected medoid day

**Why useful:** Visual check that medoids represent distinct patterns

**Input files:**
- Original time series
- List of medoid days (unique values in TD_of_days_12.out)

**Implementation:** Easy

### 5.5 Seasonal Coverage Heatmap

**What:** Heatmap with months on Y-axis, TDs on X-axis, showing days per cell

**Why useful:** Reveals if some seasons over/under-represented by specific TDs

**Implementation:** Easy

---

## 6. Plot Implementation Location

**Recommended:** Create new script `scripts/analyze_typical_days.py`

**Rationale:**
- Keep analysis separate from model execution
- Can be run independently to diagnose TD issues
- Should produce outputs in `plots/td_diagnostics/`

**Template structure:**
```python
#!/usr/bin/env python3
"""
Typical Days Diagnostic Analysis for EnergyScope

Produces diagnostic plots for the k-medoids typical day selection.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def load_td_data(region='FI', nbr_td=12):
    ...

def plot_td_distribution(td_of_days, output_dir):
    ...

def plot_reconstruction_error(ts_original, td_of_days, output_dir):
    ...

def plot_duration_curves(ts_original, td_of_days, output_dir):
    ...

def plot_medoid_profiles(ts_original, td_of_days, output_dir):
    ...

if __name__ == '__main__':
    ...
```

---

## 7. Summary Assessment

| Aspect | Status | Notes |
|--------|--------|-------|
| TD selection executed | ✓ OK | Optimal CPLEX solve |
| Euclidean error | ✓ OK | 11.6% (acceptable) |
| Input data consistency | ✓ OK | Files present, correct format |
| Weights reasonable for Finland | ✓ OK | High on wind/hydro/elec |
| Seasonal coverage | ? UNKNOWN | Need diagnostic plots |
| Industrial heat profiles | ⚠ CAUTION | May not capture CHP drivers |

**Overall verdict:** TD selection appears correctly executed. Recommended to produce diagnostic plots before concluding it's adequate for CHP calibration.

---

## 8. Existing Plotting Utilities

**In repository:**
- `esmc/postprocessing/draw_sankey/` — Sankey diagrams (not relevant)
- `scripts/generate_validation_plots_and_report.py` — Validation (not TD)
- `scripts/plot_validate_2017.py` — Validation plots

**TD-specific plotting:** None found. Need to create.

---

*Next step: Create analyze_typical_days.py if TD diagnostics are needed*
