# Finland 2017 Model Validation Analysis

## 1. Primary Energy Comparison (TWh)
| Resource | Real (2017) | Model (Unconstrained) | Diff (%) | Status |
|---|---|---|---|---|
| Oil | 97.0 | 0.0 | -100.0% | **LOW** |
| Coal | 32.0 | 0.0 | -100.0% | **LOW** |
| Gas | 22.0 | 113.3 | +415.1% | **HIGH** |
| Nuclear | 65.0 | 61.0 | -6.1% | OK |
| Hydro | 14.6 | 26.7 | +82.8% | **HIGH** |
| Wind | 4.8 | 15.1 | +214.1% | **HIGH** |
| Biomass/Waste | 105.0 | 11.1 | -89.4% | **LOW** |
| Net Import Elec | 20.4 | 0.0 | -100.0% | **LOW** |
| Hydrogen Import | 0.0 | 59.4 | +Inf% | **MODEL ARTIFACT** |

## 2. Electricity Generation Mix (TWh)
| Source | Real (2017) | Model (Unconstrained) | Diff (%) | Status |
|---|---|---|---|---|
| Nuclear | 21.6 | 22.6 | +4.5% | OK |
| Hydro | 14.6 | 26.7 | +82.8% | **HIGH** |
| Wind | 4.8 | 15.1 | +214.1% | **HIGH** |
| Biomass | 11.0 | 0.0 | -100.0% | **LOW** |
| Coal | 6.0 | 0.0 | -100.0% | **LOW** |
| Gas | 4.0 | 0.1 | -98.3% | **LOW** |

## 3. Analysis & Conclusions
The unconstrained model run shows significant deviations from the 2017 validation year:
1. **Fuel Switch (Gas vs Wood):** The model massively prefers Natural Gas (>113 TWh) over Biomass (~0 TWh), whereas reality is the opposite. This is driven by cost optimization without 'Limpens-style' historical constraints. In 2017, legacy infrastructure and policy drove biomass use.
2. **Wind Overbuild:** The model installs ~15 TWh of Wind (economically optimal), triple the actual 2017 level (4.8 TWh).
3. **Hydrogen Import:** The model imports ~60 TWh of H2, likely to replace fossil fuels or for heavy transport/industry, which did not exist in 2017.
4. **Hydro:** Model estimates 31 TWh vs 14.6 TWh actual. This suggests availability factors or capacity inputs need checking.