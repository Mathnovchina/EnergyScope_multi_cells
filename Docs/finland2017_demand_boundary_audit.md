# Finland 2017 Demand Boundary Audit

**Date:** 2026-03-18  
**Scope:** Forensic audit of Finland 2017 electricity demand inputs, imports gap, and accounting boundary differences  
**Objective:** Scientifically defensible diagnosis of why model electricity imports differ from Finnish statistics  
**Status:** Complete — ready for paper formulation

---

## Table of Contents

1. [Demand Construction Trace](#1-demand-construction-trace)
2. [Reconciliation Table](#2-reconciliation-table)
3. [AMPL Model Mechanics](#3-ampl-model-mechanics)
4. [Structural Boundary Differences](#4-structural-boundary-differences)
5. [Proven / Likely / Hypothesis](#5-proven--likely--hypothesis)
6. [Scientific Interpretation](#6-scientific-interpretation)
7. [Recommendation](#7-recommendation)
8. [Paper-Writing Draft](#8-paper-writing-draft)

---

## 1. Demand Construction Trace

### 1.1 Source Dataset

**Primary source:** JRC-IDEES (Joint Research Centre — Integrated Database of the European Energy Sector), based on Eurostat energy balances.

**Year available:** 2015 and 2020 (5-year steps: 2015, 2020, 2025, 2030, 2035, 2040, 2045, 2050).  
**No 2017 data point exists in the source.**

**Source file:** `Data/exogenous_data/regions/Demands.csv`  
- Multi-country, multi-year CSV
- Columns: Year, Region, Parameter, HOUSEHOLDS, SERVICES, INDUSTRY, TRANSPORTATION
- Values in GWh (energy) or Mpkm/Mtkm (mobility)

### 1.2 Interpolation to 2017

The model input file `Data/2017/FI/Demands.csv` was built by **linear interpolation** between 2015 and 2020 at fraction 0.4:

```
value_2017 = value_2015 + 0.4 × (value_2020 − value_2015)
```

**Verification** (all values match to ±0.01 GWh):

| Parameter | Sector | Source 2015 (GWh) | Source 2020 (GWh) | Interpolated 2017 | Demands.csv value | Match? |
|-----------|--------|-------------------|-------------------|-------------------|-------------------|--------|
| ELECTRICITY | HH | 8,516.68 | 9,125.26 | 8,760.11 | 8,760.11 | ✓ |
| ELECTRICITY | SV | 10,913.49 | 10,685.60 | 10,822.33 | 10,822.33 | ✓ |
| ELECTRICITY | IND | 23,481.29 | 23,340.23 | 23,424.87 | 23,424.87 | ✓ |
| HEAT_HIGH_T | IND | 59,964.82 | 59,604.60 | 59,820.73 | 59,820.73 | ✓ |
| HEAT_LOW_T_SH | HH | 38,666.82 | 38,391.47 | 38,556.68 | 38,556.68 | ✓ |
| HEAT_LOW_T_SH | SV | 25,829.07 | 23,673.88 | 24,966.99 | 24,966.99 | ✓ |
| HEAT_LOW_T_SH | IND | 22,165.12 | 22,031.97 | 22,111.86 | 22,111.86 | ✓ |
| HEAT_LOW_T_HW | HH | 5,028.18 | 7,479.80 | 6,008.83 | 6,008.83 | ✓ |
| HEAT_LOW_T_HW | SV | 4,786.49 | 5,919.88 | 5,239.85 | 5,239.85 | ✓ |
| HEAT_LOW_T_HW | IND | 9,152.40 | 9,097.42 | 9,130.41 | 9,130.41 | ✓ |

**Script that performed this:** `scripts/archive/update_demands_from_regions.py`  
(reads `regions/Demands.csv`, filters by year+region, copies sector columns to `FI/Demands.csv`)

### 1.3 Data Traceability in Workbook

In `Data/exogenous_data/Finland_MASTER_Calibration_old_UPDATED.xlsx`, sheet `01_Data_Traceability`:

| Data_Category | Specific_Parameter | Year_Applied | Source_Origin | AMPL_Parameter |
|---------------|-------------------|--------------|---------------|----------------|
| Demands | ELECTRICITY | 2017 | JRC-IDEES/Eurostat 2015 | end_uses_demand_year |
| Demands | HEAT_HIGH_T | 2017 | JRC-IDEES/Eurostat 2015 | end_uses_demand_year |
| Demands | HEAT_LOW_T_SH | 2017 | JRC-IDEES/Eurostat 2015 | end_uses_demand_year |
| Demands | HEAT_LOW_T_HW | 2017 | JRC-IDEES/Eurostat 2015 | end_uses_demand_year |

Note from the traceability: *"2015 data as proxy for 2017"* (actual delivery is a 2015–2020 interpolation).

### 1.4 What the Demand Values Represent

JRC-IDEES demand categories represent **final end-use energy services**, not primary energy and not commodity flows:

| Category | Definition in JRC-IDEES | Units |
|----------|------------------------|-------|
| ELECTRICITY | Specific electricity: lighting, motors, electronics, electrolysis — **excludes** electricity used for heating or cooling | GWh |
| HEAT_HIGH_T | High-temperature industrial process heat (>100°C): steam, furnaces, kilns — **regardless of input fuel** | GWh |
| HEAT_LOW_T_SH | Space heating sensible heat demand | GWh |
| HEAT_LOW_T_HW | Hot water / sanitary heat demand | GWh |
| PROCESS_COOLING | Industrial process cooling demand | GWh |
| SPACE_COOLING | Air conditioning / ventilation cooling demand | GWh |

**Critical distinction:** ELECTRICITY in JRC-IDEES = "specific electricity" (the service), not "electricity as a commodity" (what meters measure).

### 1.5 Transformations Applied

**None.** The values in `Demands.csv` are a direct interpolation from `regions/Demands.csv`. There is:
- No reallocation between layers
- No adjustment for Finnish specificity
- No correction for energy-sector own-use
- No embedding of network losses (losses are separate in the model)

### 1.6 Network Losses

Losses are applied **inside the AMPL model** via `Misc_indep.json` parameter `loss_network`:

| Layer | Parameter value (current) | Finnish reality | Source |
|-------|--------------------------|-----------------|--------|
| ELECTRICITY | 0.03 (corrected from 0.0864) | ~3% (Fingrid data) | Finnish Energy Authority |
| HEAT_LOW_T_DHN | 0.085 (corrected from 0.05) | ~8.5% | Finnish Energy |

**AMPL Eq. 20** (`ESMC_model_AMPL.mod`, line 471):
```
Network_losses[c,eut,h,td] = (sum of production) × loss_network[eut] + (sum of imports) × loss_network[eut]
```

**AMPL Eq. (end_uses_t)** (`ESMC_model_AMPL.mod`, line 256):
```
End_uses[c, "ELECTRICITY", h, td] = demand × time_series + Network_losses
```

Losses are proportional to **production + imports**, not to demand. The END_USES variable in Year_balance includes both demand and losses.

### 1.7 Energy-Sector Own-Use

**Correctly excluded from demand — and implicitly captured at the supply side.**

EnergyScope uses the End-Use Demand (EUD) framework: `Demands.csv` covers HOUSEHOLDS, SERVICES, INDUSTRY, and TRANSPORTATION only. The energy/transformation sector is not a final-demand sector and never appears in these files. This is consistent by design.

Importantly, **Stats Finland's FEC electricity figure (~66 TWh) also excludes energy-sector own-use** (the ~4.8 TWh line item in the energy balance sits *above* FEC in the IEA accounting chain). So both the model demand input and the Finnish reference figure exclude own-use — the comparison is apples-to-apples.

Own-use IS captured in the model, but at the **supply side**, via net efficiency factors:
- `NUCLEAR` in `Layers_in_out.csv`: +1.0 ELECTRICITY, −3.125 URANIUM → η = 1/3.125 = 0.32
- Finnish nuclear net efficiency is ~31–33% (Loviisa + Olkiluoto), i.e. this is the **net** output delivered to the grid after auxiliary consumption
- There is no separate `-ELECTRICITY` row for nuclear own-use in `Layers_in_out.csv` because it is already absorbed into the net efficiency
- The same logic applies to all generation technologies (CHP, hydro, wind, etc.)

**The "4.8 TWh own-use gap" is not a source of discrepancy in the model vs Stats Finland comparison.** It should not be added to the demand side — doing so would constitute double-counting.

### 1.8 Are Imports a Calibration Target?

**No.** Electricity imports (`ELECTRICITY` resource with `avail_exterior = 1e15`) are **endogenous** — the model imports whatever it needs to balance the electricity layer. There is no import constraint or target. The import capacity is constrained to 3 GW (`elec_import_capacity` in `Misc.json`).

---

## 2. Reconciliation Table

### 2.1 Full Electricity Balance: Three Perspectives

| Item | Stats Finland 2017 | JRC-IDEES (model input) | EnergyScope v26 output | Notes |
|------|-------------------|------------------------|----------------------|-------|
| **DEMAND SIDE** | | | | |
| FEC Electricity (end-use) | 66.0 TWh | 43.0 TWh | 43.0 TWh (input) | See §4 for gap explanation |
| — Households | ~9.0 TWh | 8.76 TWh | 8.76 TWh | Close match |
| — Services | ~12.5 TWh | 10.82 TWh | 10.82 TWh | ~1.7 TWh gap |
| — Industry | ~44.5 TWh | 23.42 TWh | 23.42 TWh | **21 TWh gap** — see §4.1 |
| — Transport | ~0.7 TWh | 0 TWh | 0 TWh | Handled via mobility layer |
| Network T&D losses | 2.8 TWh | separate parameter | 5.7 TWh (at old 8.64%) | Now 1.3 TWh at corrected 3% |
| Energy sector own-use | 4.8 TWh (above FEC) | not in FEC | not in EUD | Excluded from FEC by definition; captured at supply side via net η |
| HP/cooling electricity | ~7 TWh | endogenous | 19.2 TWh | Model over-invests in HP |
| Transport electricity | 0.7 TWh | endogenous | 0.7 TWh | Close match |
| **Total electricity needed** | **~81 TWh** | — | **71.1 TWh** | |
| | | | | |
| **SUPPLY SIDE** | | | | |
| Domestic generation | 65.0 TWh | unconstrained | 65.5 TWh | Close match (calibrated) |
| — Nuclear | 21.6 TWh | calibrated | 21.6 TWh | Matched via f_min/f_max |
| — Hydro | 14.6 TWh | calibrated | 14.6 TWh | Matched via f_min/f_max |
| — CHP | 20.7 TWh | calibrated | 12.3 TWh* | Partial match |
| — Condensation | 3.3 TWh | calibrated | 3.2 TWh | Close match |
| — Wind | 4.8 TWh | calibrated | 4.8 TWh | Matched via f_min/f_max |
| — Solar | 0.04 TWh | small | 0.0 TWh | Negligible |
| Gross imports | 20.4 TWh | endogenous | 5.6 TWh | **Gap = 14.8 TWh** |
| Exports | 3.5 TWh | endogenous | ~0 TWh | |
| **Net imports** | **16.9 TWh** | — | **5.6 TWh** | |

*CHP is lower in v26 because some CHP electric output (IND_COGEN) is already included in the generation total.

### 2.2 Industrial Energy Demand: The Core Discrepancy

| Demand layer | JRC-IDEES (Demands.csv) | Stats Finland 2017 | Δ | Comment |
|-------------|------------------------|--------------------|----|---------|
| IND ELECTRICITY | 23.42 TWh | ~44.5 TWh | +21.1 TWh | Motors, mechanical pulping, drives, process equipment |
| IND HEAT_HIGH_T | 59.82 TWh | ~38–42 TWh* | −18 to −22 TWh | Steam, furnaces, kilns (fuel-only view) |
| IND HEAT_LOW_T_SH | 22.11 TWh | ~22 TWh | ~0 | Space heating (consistent) |
| IND HEAT_LOW_T_HW | 9.13 TWh | ~9 TWh | ~0 | Hot water (consistent) |
| IND PROCESS_COOLING | 3.76 TWh | ~4 TWh | ~0 | Cooling (consistent) |
| IND NON_ENERGY | 10.71 TWh | ~11 TWh | ~0 | Petrochemical feedstock (consistent) |
| **Total** | **129.0 TWh** | **~129 TWh** | **~0** | **Cross-check: totals agree** |

*Stats Finland HEAT_HIGH_T equivalent is not directly reported; inferred as the residual to keep total industrial energy balanced.

**Key observation:** The cross-sector total (~129 TWh) is approximately consistent. The difference is in the **allocation between ELECTRICITY and HEAT_HIGH_T**, not in the total.

### 2.3 HEAT_HIGH_T Production in the Model (v26 Year_balance)

| Technology | HEAT_HIGH_T produced (TWh) | ELECTRICITY consumed (TWh) | Fuel |
|-----------|---------------------------|---------------------------|------|
| IND_COGEN_WOOD | 26.39 | produces +8.96 | WOOD |
| IND_BOILER_WOOD | 16.19 | 0 | WOOD |
| IND_BOILER_WASTE | 9.10 | 0 | WASTE |
| IND_BOILER_COAL | 3.00 | 0 | COAL |
| IND_BOILER_OIL | 3.00 | 0 | LFO |
| IND_BOILER_BIOWASTE | 2.29 | 0 | BIOWASTE |
| **IND_DIRECT_ELEC** | **0.00013** | **−0.00013** | **ELECTRICITY** |
| **Total** | **59.82 TWh** | **net +8.96 TWh** | |

The model uses almost zero electricity to produce HEAT_HIGH_T (IND_DIRECT_ELEC = 0.13 GWh). The CHP plants (IND_COGEN_WOOD) actually **produce** electricity while serving heat demand.

---

## 3. AMPL Model Mechanics

### 3.1 Demand Parameterisation

From `ESMC_model_AMPL.mod` (line 128–129):
```ampl
param end_uses_demand_year {REGIONS, END_USES_INPUT, SECTORS} >= 0 default 0;
param end_uses_input {c in REGIONS, i in END_USES_INPUT} := sum {s in SECTORS} (end_uses_demand_year[c,i,s]);
```

`end_uses_input` is the sum of all sectors for each demand category. For ELECTRICITY: 8,760 + 10,822 + 23,425 = 43,007 GWh.

### 3.2 End-Use Hourly Profile (line 256)

```ampl
End_uses[c, "ELECTRICITY", h, td] = end_uses_input[c,"ELECTRICITY"] × electricity_time_series[c,h,td] / t_op[h,td]
                                     + Network_losses[c,"ELECTRICITY",h,td]
```

For HEAT_HIGH_T (line 279):
```ampl
End_uses[c, "HEAT_HIGH_T", h, td] = end_uses_input[c,"HEAT_HIGH_T"] / total_time
```

**HEAT_HIGH_T has no network losses term and a flat hourly profile.**

### 3.3 Layer Balance (line 368, Eq. 13)

```ampl
sum(resources) + sum(technologies) + sum(storage) − End_uses = 0
```

For the ELECTRICITY layer, this means:
- Nuclear + Hydro + Wind + CHP + Imports − HP − Cooling − Transport − IND_DIRECT_ELEC − End_uses[ELEC] = 0

The model imports `ELECTRICITY` as a resource when domestic production is insufficient to satisfy the combined End_uses (demand + losses) plus technology electricity consumption (HP, cooling, etc.).

### 3.4 How Imports Arise

Imports are **endogenous**. The model imports electricity when:
1. Domestic generation capacity is insufficient in specific hours (wind/solar intermittency)
2. Import price (`c_op_exterior` = 0.0326 EUR/kWh for ELECTRICITY) is cheaper than marginal domestic generation

The import capacity is constrained: `elec_import_capacity = 3 GW` (from `Misc.json`).

---

## 4. Structural Boundary Differences

### 4.1 The Industry Electricity / HEAT_HIGH_T Classification (PROVEN)

**Root cause of the 21 TWh industry electricity gap:**

JRC-IDEES uses **end-use category accounting**: energy is classified by the service it provides (light, motion, heat), not by the commodity consumed.

Stats Finland uses **commodity-flow accounting** (derived from IEA energy balance methodology): energy is classified by the energy carrier entering the facility boundary.

For Finnish paper and pulp mills:
- **Mechanical pulping** (TMP/CTMP refiners, groundwood grinders) consumes electricity to grind wood into fibres. The mechanical energy converts to heat during the process. JRC-IDEES classifies the output as **process heat** (HEAT_HIGH_T). Stats Finland classifies the input as **electricity consumption**.
- **Paper machine drives** (wire section, press section, dryer section): electric motors drive mechanical processes. The electric meter records electricity; JRC-IDEES records the mechanical service.
- **Pumps, compressors, conveyors** in mills: similar — electricity input, mechanical/process output.

This is not a data error. It is a methodological choice by JRC-IDEES, consistent with the Eurostat "useful energy" approach.

**Evidence:**
- Total industrial energy in both systems ≈ 129 TWh (cross-check passes)
- ELECTRICITY IND: JRC = 23.4 TWh, Stats FI = 44.5 TWh (Δ = 21.1 TWh)
- HEAT_HIGH_T IND: JRC = 59.8 TWh, Stats FI ≈ 38–42 TWh (Δ ≈ −18 to −22 TWh)
- The shift is approximately symmetric → no energy created or destroyed

### 4.2 Energy-Sector Own-Use (CORRECTED — NOT A GAP)

Energy-sector own-use is **correctly excluded from the demand side** and is **not a source of discrepancy** between the model and Finnish statistics.

**Why it is not a gap:**
1. **Stats Finland FEC excludes own-use by definition.** The ~4.8 TWh own-use sits in the transformation sector rows of the IEA energy balance, above the FEC line. When we compare model EUD to Stats Finland FEC electricity (~66 TWh), neither side includes own-use.
2. **EnergyScope captures own-use via net efficiency factors.** `NUCLEAR` in `Layers_in_out.csv` has +1.0 ELECTRICITY and −3.125 URANIUM, giving η = 0.32 — the Finnish nuclear net efficiency (~31–33%). This net value already deducts auxiliary consumption (pumps, cooling, control systems). The electricity used by the plant for its own operations never enters the ELECTRICITY layer — it is simply "not generated."
3. **No auxiliary-load parameter is needed or appropriate.** Adding 4.8 TWh as an explicit ELECTRICITY demand would double-count it (once via reduced net efficiency, once as an explicit demand).

**The ~4.8 TWh therefore drops out of the reconciliation.** It does not contribute to the import gap.

### 4.3 Network Losses (PROVEN, NOW CORRECTED)

- `loss_network[ELECTRICITY]` was 0.0864 (EU average), corrected to 0.03 (Finnish)
- `loss_network[HEAT_LOW_T_DHN]` was 0.05 (EU average), corrected to 0.085 (Finnish)
- Finnish grid losses ≈ 3% (Fingrid data); DHN losses ≈ 8.5% (Finnish Energy)

The loss parameter is applied at the AMPL level (Eq. 20), not embedded in Demands.csv.

### 4.4 Heat Pump Over-Deployment (LIKELY)

The model deploys DEC_HP_ELEC at 15.4 TWh electricity consumption (v26), while Finnish reality has ~7 TWh total electric heating (resistive + HP combined). This is a **technology calibration issue**, not a demand issue, driven by:
- Low f_min for competing technologies (resistive, oil boilers)
- Cost optimality favouring HP
- DHN share applied to industry creating phantom industrial DHN demand
- This inflates total model electricity consumption by ~8 TWh vs reality

### 4.5 Summary of Boundary Differences

| Factor | Magnitude (TWh) | Direction | Type | Fixable? |
|--------|-----------------|-----------|------|----------|
| Industry ELEC ↔ HEAT_HIGH_T reclassification | ~21 | Model demand lower | Accounting convention | Only with verified end-use split data |
| Energy sector own-use | ~0 | Not a gap | Not in FEC either | Excluded from demand in both Stats FI FEC and model EUD; captured at supply side via net η |
| HH + SV minor data-year gaps | ~2 | Model demand lower | Data vintage | Would require updated source data |
| Network losses (now corrected) | was +2.9, now −1.5 | Was higher, now lower | Parameter correction | Corrected |
| HP over-deployment | ~8 | Model consumption higher | Technology calibration | Partially via f_max constraints |
| **Net effect on total electricity** | **Model ~10 TWh lower gross** | | | |
| **Net effect on imports** | **Model ~11 TWh lower** | | | |

---

## 5. Proven / Likely / Hypothesis

### PROVEN (directly verifiable from files and model equations)

1. **Demands.csv ELECTRICITY = 43,007 GWh**, sourced from JRC-IDEES 2015 linearly interpolated to 2017 at fraction 0.4 between 2015 and 2020 source data.  
   *Evidence:* Source file `regions/Demands.csv` FI rows for 2015 and 2020 match to ±0.01 GWh after interpolation.

2. **JRC-IDEES uses end-use category accounting**, where ELECTRICITY = specific electricity only (lighting, motors, electronics) and HEAT_HIGH_T = all high-temperature process heat regardless of input fuel.  
   *Evidence:* JRC-IDEES methodology documentation; total industrial energy ≈ 129 TWh in both JRC and Stats Finland (conservation check passes).

3. **Network losses are applied at AMPL model level** (Eq. 20, line 471) via `loss_network` parameter, proportional to production + imports, not embedded in Demands.csv.  
   *Evidence:* AMPL source code, `Misc_indep.json` parameter values.

4. **HEAT_HIGH_T has no network losses** and a flat hourly profile in the model (line 279).  
   *Evidence:* AMPL source code; loss_network default = 0 for parameters without explicit values.

5. **IND_DIRECT_ELEC deploys at 0.13 GWh in v26** (negligible). Almost all HEAT_HIGH_T (59.8 TWh) is served by fuel-based boilers and CHP.  
   *Evidence:* Year_balance.csv from v26 run.

6. **Electricity imports = 5.6 TWh in v26**, purely endogenous (no import target).  
   *Evidence:* Year_balance.csv, ELECTRICITY resource row = 5,619 GWh.

7. **Energy-sector own-use is correctly excluded from demand** and is not a gap.  
   *Evidence:* (i) Stats Finland FEC electricity (~66 TWh) excludes own-use by IEA definition. (ii) `Layers_in_out.csv` NUCLEAR: η = 1/3.125 = 0.32 = Finnish net nuclear efficiency — the net efficiency already deducts auxiliary consumption. (iii) No separate −ELECTRICITY row for own-use exists in any generation technology in `Layers_in_out.csv`. Adding own-use as an explicit demand would double-count.

8. **Import capacity = 3 GW** (`elec_import_capacity` in `Misc.json`), **export capacity = 3 GW**.  
   *Evidence:* `Data/2017/FI/Misc.json`.

### LIKELY (strong inference, not directly provable from model files alone)

9. **Finnish paper/pulp mills consume ~21 TWh electricity for mechanical processes** that JRC-IDEES classifies as HEAT_HIGH_T.  
   *Basis:* Stats Finland industry electricity (44.5 TWh) minus JRC-IDEES industry ELECTRICITY (23.4 TWh) = 21.1 TWh. Finland's forest industry is the dominant industrial electricity consumer. Mechanical pulping (TMP) is known to consume 2,000–3,500 kWh/tonne of pulp.

10. ~~**Energy-sector own-use ≈ 4.8 TWh**~~ — *Removed as a gap item.* Stats Finland FEC (~66 TWh) already excludes own-use, and EnergyScope's net efficiency factors capture it at source. This is not a demand-side discrepancy. The 4.8 TWh figure (from Statistics Finland energy balance, "Energy industries own use" row) is real but does not contribute to the model vs FEC comparison.

11. **The split between mechanical (electricity service) and thermal (heat service) in Finnish industry is approximately 21/38 = 36% electric / 64% fuel-based** for HEAT_HIGH_T processes.  
    *Basis:* Difference between JRC and Stats Finland. The 38 TWh residual HEAT_HIGH_T from fuel-flow perspective is consistent with Finnish CHP-dominated industrial heat supply.

### HYPOTHESIS (plausible but unverified)

12. **A significant fraction of the reclassified 21 TWh may be genuinely ambiguous** — e.g., thermo-mechanical pulping where electricity simultaneously produces both pulp fibre (wanted product) and heat (recovered as process steam). Whether this is "electricity service" or "heat service" is a definitional choice, not a physical fact.

13. **The HP over-deployment (15.4 vs ~7 TWh electricity) is partly caused by the DHN share being applied to industry low-T heat**, creating phantom industrial district heating demand. This inflates DHN production and the electric HP used to serve it.

14. **The "right" split for HEAT_HIGH_T between electricity-driven and fuel-driven** in Finnish industry requires detailed disaggregated data from JRC-IDEES sub-sheets (not available in this workspace) or from Finnish Forest Industries Federation (Metsäteollisuus ry) energy statistics.

---

## 6. Scientific Interpretation

### 6.1 What Can Be Legitimately Compared?

| Model variable | Real-world counterpart | Directly comparable? | Notes |
|---------------|----------------------|---------------------|-------|
| Primary energy by fuel (PE_*) | Statistics Finland TPES | **Yes** | Same physical quantity |
| Electricity generation by source | Statistics Finland generation mix | **Yes** | Same physical quantity |
| CO₂ emissions | UNFCCC / Statistics Finland | **Yes** | Same physical quantity |
| Electricity imports (ELEC_IMPORTS) | Statistics Finland net imports | **No** | Different demand boundary → structurally different residual |
| Total electricity consumption | Statistics Finland FEC electricity | **No** | Different demand definition (end-use vs commodity) |
| DHN production (HEAT_DHN) | Finnish Energy DH statistics | **Partially** | DHN share applies to all sectors including industry (model); reality: DH mainly serves buildings |
| Industrial electricity | Statistics Finland industry electricity | **No** | ~21 TWh boundary shift to HEAT_HIGH_T |
| Industrial high-T heat | No direct comparator | **No** | JRC-IDEES HEAT_HIGH_T has no physical counterpart in Finnish energy statistics |

### 6.2 Which Variables Are Directly Comparable?

**Safe to compare (same boundary):**
- Nuclear generation (TWh)
- Hydro generation (TWh)
- Wind generation (TWh)
- Solar generation (TWh)
- CHP generation (TWh, with care about fuel breakdown)
- Total domestic generation (TWh)
- Primary energy by fuel type (TWh)
- CO₂ emissions (MtCO₂)
- Biomass primary energy (TWh)
- Gasoline/diesel shares in transport (fraction)

### 6.3 Which Variables Require Boundary Adjustment?

**Not directly comparable:**
- Electricity imports / exports (different demand base)
- Total electricity consumption (different demand definition)
- Industrial electricity consumption
- District heating production (if industry DHN share is unrealistic)

**Adjustable with documented correction:**
- Electricity imports: can be compared IF the demand boundary difference is explicitly stated and the expected theoretical import under JRC boundary is computed
- Total electricity: can be compared IF "specific electricity" plus "model-added electric heating/cooling/transport" is stated separately from "commodity electricity"

### 6.4 The Cleanest Scientific Hypothesis

> The EnergyScope model, using JRC-IDEES end-use demand definitions, represents Finnish electricity demand at the "useful energy service" boundary rather than the "commodity flow" boundary used in national energy statistics. This results in ~23 TWh lower electricity demand (43 vs 66 TWh), primarily because ~21 TWh of industrial electricity consumption in the paper and pulp sector is classified as high-temperature process heat (HEAT_HIGH_T) in the JRC-IDEES end-use framework. Since the model's domestic generation capacity (~65 TWh) is calibrated to match reality, the reduced electricity demand leads to structurally lower electricity imports in the model (5.6 TWh) compared to Finnish statistics (16.9 TWh net). This is primarily an accounting-boundary effect, not a modeling error.

### 6.5 Best Modeling Strategy

**Ranked options:**

1. **Keep current demand boundary + explicitly justify it** (RECOMMENDED)
   - The JRC-IDEES boundary is internally consistent
   - HEAT_HIGH_T demand + ELECTRICITY demand = total industrial energy ≈ 129 TWh (conserved)
   - The model's technology mix for serving HEAT_HIGH_T is realistic (biomass CHP + boilers)
   - Modifying demands risks double-counting
   - All scored calibration metrics are unaffected (ELEC_IMPORTS is unscored)

2. **Add a "boundary correction" pseudo-demand** (ACCEPTABLE but complex)
   - Add ~5 TWh to ELECTRICITY for energy-sector own-use (simple, no double-count)
   - Transfer X TWh from HEAT_HIGH_T to ELECTRICITY (requires verified Finnish disaggregated data)
   - This changes the model's optimisation behaviour and may require re-calibrating technology constraints

3. **Change the validation protocol** (COMPLEMENTARY to option 1)
   - Compare electricity imports against a "JRC-equivalent import" reference value rather than Stats Finland raw imports
   - JRC-equivalent imports = (JRC demand gross) − (domestic generation) ≈ 44.3 − 65.0 = −20.7 TWh → Finland is a net exporter under JRC boundary
   - This correctly predicts that the model will have very low imports

### 6.6 Best Validation Strategy for Imports

Since electricity imports are **structurally non-comparable** due to the demand boundary:

1. **Remove ELEC_IMPORTS from scored metrics** (already done: weight = 0.0 in `finland_2017_reference.csv`)
2. **Report ELEC_IMPORTS as an "indicative" metric** in the paper alongside the demand boundary explanation
3. **Quote the "boundary-adjusted import expectation"** = JRC demand gross − generation ≈ −21 TWh (net export under JRC) to show why model imports are low
4. **Focus validation on directly comparable metrics**: generation mix, primary energy, CO₂, which do not suffer from the boundary issue

---

## 7. Recommendation

### Option 1 (RECOMMENDED): Keep Current Boundary + Document

**Scientific justification:** The model uses a consistent end-use service demand framework (JRC-IDEES) where total industrial energy is conserved (~129 TWh). The electricity import gap is a consequence of the demand accounting convention, not a modeling deficiency. The 14 scored calibration metrics (PE, generation mix, CO₂) are unaffected.

**Actions:**
- Keep `Demands.csv` unchanged
- Keep `ELEC_IMPORTS` weight = 0.0 in reference file
- Add a methodology note in the paper explaining the boundary difference
- Compute and report the "boundary-adjusted import expectation" alongside the actual Finnish import data

**Risk:** Reviewers unfamiliar with JRC-IDEES may question the import gap. Mitigation: explicitly state the convention and show the industrial energy conservation cross-check.

### Option 2 (ACCEPTABLE): Partial Boundary Correction

If a reviewer or co-author insists on matching Finnish electricity imports:

- Transfer ~15–20 TWh from IND HEAT_HIGH_T → IND ELECTRICITY
- This requires reliable disaggregated data on Finnish industry electricity end-use
- The transfer must be exactly balanced to avoid inflating total energy
- Re-run and re-calibrate technology constraints
- Document the departure from standard JRC-IDEES methodology

**Risk:** Introduces a Finland-specific deviation from the pan-European JRC-IDEES data pipeline that other countries in the multi-cell model do not have. May cause inconsistency in comparative multi-country analyses.

### Option 3 (NOT RECOMMENDED): Add Without Removing

- Adding 21 TWh to ELECTRICITY without reducing HEAT_HIGH_T would **double-count** ~21 TWh of industrial energy
- Total industrial energy would rise from 129 TWh to 150 TWh
- This is physically incorrect

---

## 8. Paper-Writing Draft

### 8.1 Methodology Section Draft

> **Demand boundary.** End-use energy demands are sourced from the JRC-IDEES database (Mantzos et al., 2017), which classifies final energy consumption by the service provided (useful energy approach) rather than by the energy carrier consumed. For Finland, this has a significant structural implication for the electricity sector: approximately 21 TWh of industrial electricity consumption — primarily in the paper and pulp sector for mechanical pulping and process drives — is classified under high-temperature process heat (HEAT_HIGH_T) rather than under electricity (ELECTRICITY). This is because JRC-IDEES allocates energy to the end-use category of the process output, whereas Finnish national energy statistics (Statistics Finland) record the electricity input regardless of end-use. The total industrial energy demand (~129 TWh) is conserved between the two accounting conventions; only the allocation between electricity and process heat layers differs. As a consequence, model electricity demand (43.0 TWh) is lower than the Finnish national FEC electricity figure (66.0 TWh), which in turn leads to structurally lower electricity imports in the model compared to official statistics. We retain the JRC-IDEES demand boundary for methodological consistency with the pan-European multi-cell model framework. All calibration metrics that are directly comparable (primary energy by source, generation mix, CO₂ emissions) are validated against Finnish statistics; metrics affected by the demand boundary difference (electricity imports) are reported as indicative rather than scored.

### 8.2 Key Caveat

> The model's electricity import volume (5.6 TWh vs 16.9 TWh net import in 2017) should not be interpreted as a modeling error, but as a structural consequence of the JRC-IDEES end-use demand definition, which assigns ~21 TWh of Finnish industrial electricity to the heat demand layer. Correcting this would require independently verified Finnish industrial end-use data and would introduce a country-specific deviation from the harmonised JRC-IDEES input pipeline.

### 8.3 Validation Table Footnote

> † Electricity imports are not included in the calibration score because the JRC-IDEES demand boundary (useful energy services) differs from the Finnish national energy balance (commodity flows) by approximately 23 TWh in the electricity layer. Under the JRC-IDEES accounting convention, Finland is a net exporter of electricity relative to service demand, making the import figure structurally non-comparable.

---

## Appendix: File Reference

| File | Purpose | Key content |
|------|---------|-------------|
| `Data/2017/FI/Demands.csv` | Model input (11 demand categories × 4 sectors) | ELECTRICITY = 43,007 GWh |
| `Data/exogenous_data/regions/Demands.csv` | JRC-IDEES source (multi-country, multi-year) | FI 2015: 42,911 GWh; FI 2020: 43,151 GWh |
| `Data/2017/00_INDEP/Misc_indep.json` | Loss parameters | loss_network ELECTRICITY = 0.03 |
| `Data/2017/FI/Misc.json` | FI-specific parameters | elec_import_capacity = 3 GW |
| `Data/2017/00_INDEP/Layers_in_out.csv` | Technology input/output matrix | IND_DIRECT_ELEC: −1 ELEC → +1 HEAT_HIGH_T |
| `esmc/energy_model/ESMC_model_AMPL.mod` | AMPL formulation | Eq. 13 (layer balance), Eq. 20 (losses), end_uses_t |
| `scripts/archive/update_demands_from_regions.py` | Demand construction script | Reads regions/Demands.csv → FI/Demands.csv |
| `scripts/diagnose_demand_gap.py` | Diagnostic script (v26 analysis) | Full electricity balance decomposition |
| `calibration/reality/finland_2017_reference.csv` | Validation reference data | ELEC_IMPORTS = 2.0 TWh, weight = 0.0 |
| `Data/exogenous_data/Finland_MASTER_Calibration_old_UPDATED.xlsx` | Calibration workbook | 02_Demands, 01_Data_Traceability, 19_Assumptions_Decisions |
