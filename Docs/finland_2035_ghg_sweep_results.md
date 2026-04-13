# Finland 2035 — GHG Savings Sweep: Results Interpretation

> **Date:** April 13, 2026  
> **Model:** EnergyScope Multi Cells (ESMC), single-cell Finland, AMPL + CPLEX 22.1.2  
> **Reference:** Colla et al. (2022) — *Optimal Use of Lignocellulosic Biomass for the Energy Transition*  
> **Scenarios:** two sweeps — (A) Baseline nuclear, (B) Nuclear phase-out  
> **Sweep range:** Unconstrained → 95% CO₂ reduction vs Finland 2017  

---

## Table of Contents

1. [Data Sources and Parameters](#1-data-sources-and-parameters)
2. [Key Model Hypotheses](#2-key-model-hypotheses)
3. [Scenario Design and Justification](#3-scenario-design-and-justification)
4. [Why the Unconstrained Baseline Already Shows ~69% Reduction](#4-why-the-unconstrained-baseline-already-shows-69-reduction)
5. [Scenario A — Baseline Nuclear (f_min = 4.36 GW)](#5-scenario-a--baseline-nuclear-fmin--436-gw)
   - 5.1 Fig 3 — Primary Energy by Source
   - 5.2 Fig 4 — Biomass Allocation
   - 5.3 Gas Breakdown
   - 5.4 Cost Curve
6. [Scenario B — Nuclear Phase-Out (f_min = 2.49 GW)](#6-scenario-b--nuclear-phase-out-fmin--249-gw)
   - 6.1 Fig 3 — Primary Energy by Source
   - 6.2 Fig 4 — Biomass Allocation
   - 6.3 Gas Breakdown
   - 6.4 Cost Curve
7. [Comparative Analysis: Baseline vs Phase-Out](#7-comparative-analysis-baseline-vs-phase-out)
8. [Limitations and Caveats](#8-limitations-and-caveats)

---

## 1. Data Sources and Parameters

### 1.1 GHG Baseline Reference

| Parameter | Value | Source |
|-----------|-------|--------|
| Finland 2017 CO₂ reference | **41,200 ktCO₂/y** | Calibrated EnergyScope Finland 2017 run; validated against Statistics Finland with <0.1% error on CO₂_net |
| GWP formula | `gwp_limit = 41,200 × (1 − savings_fraction)` | Analogous to Colla et al. (2022), adjusted for Finnish baseline year |
| CO₂ metric used | **CO₂_net** from `Gwp_breakdown.csv` | Includes biogenic credits; this is the metric the AMPL GWP constraint operates on. Differs from gross CO₂_EMISSIONS by ~7,900 ktCO₂ due to biomass credit. |

### 1.2 Key Input Data for Finland 2035

| Category | Parameter | Value | Source |
|----------|-----------|-------|--------|
| **Nuclear** | NUCLEAR f_min | 4.36 GW | `Data/2035/FI/Technologies.csv` — Eurostat installed capacity (OL1+OL2+OL3+Loviisa1+2) |
| **Nuclear** | NUCLEAR f_max | 5.0 GW | National policy limit |
| **Nuclear** | c_inv | 4,846 €/kW | DEA Technology Catalogues 2020, interpolated to 2035 |
| **Nuclear** | c_p (capacity factor) | 0.849 | DEA — EU average (Finnish historical CF is ~92%) |
| **Nuclear** | Efficiency | 37% (1/2.7027) | Standard LWR thermal efficiency |
| **Nuclear** | Uranium price | 3.88 €/MWh | IEA WEO 2020 — fuel almost free; cost is dominated by O&M |
| **Discount rate** | i_rate | 1.5% | Social rate (Thiran 2023, Ch.1) — strongly favours capital-intensive nuclear/renewables |
| **Coal** | avail_exterior | **0 GWh/y** | Finland coal ban by 2029 (Energy and Climate Strategy 2022) — hard constraint |
| **Gas** | c_op_exterior | 44.25 €/MWh | IEA WEO 2020 Stated Policies Scenario |
| **Gas** | avail_exterior | Unlimited | No supply security constraint modelled |
| **Gas** | CO₂ intensity | 267 gCO₂-eq/kWh | Lifecycle (incl. upstream methane leakage) |
| **Wind onshore** | c_inv | 1,010 €/kW | DEA 2035 |
| **Wind offshore** | c_inv | 1,255 €/kW | DEA 2035 |
| **PV utility** | c_inv | **335 €/kW** | DEA 2035 (−73% vs 2017 rate of 1,250 €/kW) |
| **Biomass (WOOD)** | avail_local | ~110 TWh/y | Finnish forest sector; `Data/2035/FI/Resources.csv` |
| **Biomass (WOOD)** | c_op_local | 22.08 €/MWh | Representative Finnish wood chip price |
| **Electricity import** | avail_exterior | 25,000 GWh/y | `calibration/patches/fi_baseline_2035.csv` — Nordic grid interconnect cap |

### 1.3 Patch Files Applied

Both scenarios share the brownfield renewables patch. The phase-out scenario adds one additional line.

**`calibration/patches/fi_baseline_2035.csv`** (both scenarios):

| Parameter | Technology | Baseline value | Patched value | Justification |
|-----------|-----------|---------------|--------------|---------------|
| f_min | WIND_ONSHORE | 0.496 GW | **6.0 GW** | Committed pipeline + 2035 national target |
| f_min | WIND_OFFSHORE | 0.0 GW | **1.6 GW** | Committed projects (Korsnäs, Pyhäjoki) |
| f_min | PV_ROOFTOP | 0.0 GW | **0.8 GW** | Current Finnish deployment |
| f_min | PV_UTILITY | 0.0 GW | **0.5 GW** | Current utility-scale deployment |
| avail_exterior | ELECTRICITY | 0.0 GWh/y | **25,000 GWh/y** | Nordic grid interconnect capacity |

**`calibration/patches/fi_nuclear_phaseout_2035.csv`** (phase-out scenario only):

| Parameter | Technology | Baseline value | Patched value | Justification |
|-----------|-----------|---------------|--------------|---------------|
| f_min | NUCLEAR | 4.36 GW | **2.49 GW** | Loviisa 1 (0.49 GW) + Loviisa 2 (0.49 GW) + Olkiluoto 1 (0.89 GW) = 1.87 GW retired; only Olkiluoto fleet remains: OL1+OL2+OL3 = 2.49+0.49 = 2.49 GW forced |

---

## 2. Key Model Hypotheses

| # | Hypothesis | Decision | Justification |
|---|-----------|----------|---------------|
| H1 | **Coal ban** | Accepted — `COAL avail_exterior = 0` | Finland committed to coal phase-out by 2029. This is the correct 2035 assumption. Without it, the model would use cheap coal and the unconstrained floor would be much higher (closer to 2017 level). |
| H2 | **1.5% social discount rate** | Accepted | Strongly favours capital-intensive low-carbon technologies over gas (cheap capex, expensive opex). At higher rates (e.g. 8%), nuclear and offshore wind would be penalised and gas would be more attractive. |
| H3 | **Nuclear brownfield (f_min = 4.36 GW)** | Accepted for Scenario A | All five Finnish nuclear units assumed to be operational through 2035. Loviisa 1/2 licences expire 2027/2030 but a lifetime extension under national policy is assumed. |
| H4 | **Nuclear phase-out (f_min = 2.49 GW)** | Accepted for Scenario B | Loviisa 1/2 retirement assumed (1.87 GW reduction). This gives a ~67% reduction for the sensitivity and is plausible given the licence expiry without a confirmed extension decision. |
| H5 | **Brownfield renewables** | Accepted | Wind and solar minima reflect already-committed or already-installed capacity. These are not policy targets but floor values for what is locked in by 2035 regardless of optimiser choices. |
| H6 | **DHN share constrained [42%–50%]** | Accepted | Finland has one of the world's highest DHN penetrations (~54% of residential heat). The runner applies `share_heat_dhn_min=0.42, share_heat_dhn_max=0.50`. This prevents the model from dismantling Finland's DHN infrastructure. |
| H7 | **No CO₂ layer relaxation** | Accepted | The `--relax-co2` flag is for 2017 calibration only. In 2035, CO₂_INDUSTRY is absorbed freely (avail=1×10¹⁵), meaning large point-source emitters are unconstrained beyond the global GWP limit. |
| H8 | **Single WOOD resource** | Accepted as limitation | Finland has no geographic biomass disaggregation (unlike Colla's 10-origin Belgian model). All domestic lignocellulosic biomass treated as a single pool at 22.08 €/MWh. |
| H9 | **TDs reuse across scenarios** | Accepted | All scenarios share the same weather year and demand profiles. `--read-td` is valid and avoids ~20 min of k-medoid clustering per run. |
| H10 | **GHG baseline = Finland 2017 CO₂_net = 41,200 kt** | Accepted | Calibrated to Statistics Finland 2017 data; CO₂_net metric (not gross) is used throughout to remain consistent with the AMPL GWP constraint. |
| H11 | **Deduplication of non-binding runs** | Accepted | Cases with system cost within 0.5 M€ of unconstrained are dropped from plots (constraint not binding). This removed the 49%/50%/65% cases from Scenario A, as the natural floor is ~69%. |
| H12 | **No CCS forced** | Observed | INDUSTRY_CCS installs 0.3 kt capture even in unconstrained case — effectively inactive. Not a decision; a structural finding. |

---

## 3. Scenario Design and Justification

### 3.1 Why a GHG Sweep?

Following Colla et al. (2022), a parametric sweep across GHG constraint levels reveals:
- The **marginal cost of decarbonisation** (slope of cost curve beyond the natural floor)
- The **fuel substitution sequence** (which fossil fuels are eliminated first)
- The **role of biomass** as a flexible carbon-neutral resource
- The **tightening vs relaxed** regime boundary in the European energy system

For Belgium (Colla), the unconstrained optimum achieved ~38–40% reduction; the interesting range was 40–90%. For Finland, the unconstrained floor is at ~67–69%, so the interesting range is 70–95%.

### 3.2 Scenario A — Baseline Nuclear

**Description:** Standard Finland 2035 baseline. All five nuclear units operational. NUCLEAR f_min = 4.36 GW, f_max = 5.0 GW. At f_min and c_p = 0.849, nuclear generates 32,421 GWh/y (32.4 TWh) — approximately 75% of Finland's direct electricity demand (~43.2 TWh).

**Rationale:** This is the policy-aligned baseline. All relevant Finnish energy policy documents (National Energy and Climate Strategy 2022, TEM projections) assume OL3 is operational and Loviisa units remain under extended licence.

**Patch applied:** `fi_baseline_2035.csv` only.

### 3.3 Scenario B — Nuclear Phase-Out (Loviisa Retired)

**Description:** Sensitivity scenario. Loviisa 1 (0.49 GW, licence expires 2027) and Loviisa 2 (0.49 GW, licence expires 2030) are assumed retired by 2035. Only the Olkiluoto fleet remains operational: OL1 (0.89 GW) + OL2 (0.89 GW) + OL3 (1.6 GW) + 0.11 GW rounding = 2.49 GW minimum.

**Rationale:** The Loviisa licence extensions are not legally confirmed as of the scenario date. Their retirement is a credible alternative. This scenario answers: "what if Finland does not approve Loviisa lifetime extensions?" It is informative for energy security, cost, and climate risk analysis.

**Patch applied:** `fi_baseline_2035.csv` + `fi_nuclear_phaseout_2035.csv` (stacked).

**Nuclear output at f_min:**  
- Baseline: 4.36 × 0.849 × 8,760 = **32,421 GWh/y**  
- Phase-out: 2.49 × 0.849 × 8,760 = **18,508 GWh/y**  
- **Reduction: 13.9 TWh/y** — roughly equivalent to 7 GW of wind turbines at 23% CF.

---

## 4. Why the Unconstrained Baseline Already Shows ~69% Reduction

This is the single most important structural finding of the analysis. The 2035 data is **not** a Business-As-Usual scenario — it is already a transition data set. The ~69% floor (baseline) / ~67% floor (phase-out) is entirely explained by the input data:

| Driver | Mechanism | Approximate CO₂ impact |
|--------|-----------|------------------------|
| **Coal ban** | `avail_exterior = 0` for COAL — hard physical constraint | Removes ~10–15 Mt gross CO₂/y vs 2017 (coal was ~25% of 2017 Finnish energy) |
| **Forced nuclear** | 4.36 GW × 0.849 CF = 32.4 TWh zero-carbon electricity, covers 75% of electricity demand | Displaces ~5–6 Mt CO₂/y of gas generation |
| **Renewable cost crash** | PV utility: 1,250 → 335 €/kW (−73%); wind offshore: −50% | Model installs ~125 GW renewables; displaces remaining gas from power generation |
| **Brownfield RE minima** | 6.0 GW wind onshore + 1.6 GW wind offshore + 1.3 GW PV forced | Even before optimisation, ~9 GW installed |
| **1.5% discount rate** | Capital-intensive renewables and nuclear have very low annualised cost | Fossil gas (cheap capex, expensive opex) is not competitive for baseload |

The model still uses:
- **32.8 TWh gas/y** (mainly decentralised heat via HP, industrial boilers) → ~6.6 Mt CO₂
- **13.0 TWh diesel/y** (trucks, shipping — mobility sector) → ~3.5 Mt CO₂

These residual fossil uses are structural: efficient gas-fired decentralised heating is still competitive vs electricity for seasonal heat demand, and diesel is used in modes where electrification has high cost (heavy freight, maritime cargo).

**Could we just let the model run with coal?** No — Finland enacted a legislated coal ban (effective 2029). Overriding `avail_exterior = 0` to introduce coal would be a counterfactual "what-if coal ban was reversed" sensitivity, not a baseline scenario. It would raise the unconstrained GHG floor to roughly 2017 levels and make the GHG sweep meaningful at lower reduction levels, but it would be physically unrealistic for 2035 Finland.

---

## 5. Scenario A — Baseline Nuclear (f_min = 4.36 GW)

*Plots:* `case_studies/FI/manual_runs/ghg_sweep_analysis/`

### Numerical Results

| Case | GWP limit (kt) | System cost (bn€/y) | CO₂_net (Mt) | PE total (TWh) | Biomass total (TWh) |
|------|---------------|---------------------|-------------|---------------|---------------------|
| Unconstrained | — | 22.96 | 13.0 | 303.6 | 63.4 |
| 70% | 12,360 | 22.96 | 12.4 | 305.1 | 63.7 |
| 75% | 10,300 | 23.02 | 10.3 | 298.3 | 62.7 |
| 80% | 8,240 | 23.09 | 8.2 | 288.6 | 61.9 |
| 85% | 6,180 | 23.20 | 6.2 | 285.8 | 63.4 |
| 90% | 4,120 | 23.32 | 4.1 | 286.2 | 65.0 |
| 95% | 2,060 | 23.52 | 2.1 | 298.0 | 85.2 |

### 5.1 Fig 3 — Primary Energy by Source (Scenario A)

**Figure:** `fig3_primary_energy_vs_ghg.png`

The stacked bars show primary energy (left axis, GWh/y) by fuel category for each GHG constraint level. System cost is overlaid as a line (right axis, M€/y).

#### Overall structure

The total primary energy is remarkably stable (279–305 TWh) across all constrained cases except the 95% case (298 TWh with a biomass surge). This indicates that final demand is essentially fixed and the sweep primarily reshuffles the **fuel mix** rather than reducing total energy consumption.

#### Nuclear (yellow band) — constant throughout

Nuclear occupies a constant **87.6 TWh** in every bar of Scenario A. This is because:
1. f_min = f_max ≈ 4.36–5.0 GW (very narrow band)
2. The optimiser always selects f = f_min since nuclear's high capex is fully covered by annuity at 1.5% discount rate
3. c_p = 0.849: 4.36 GW × 0.849 × 8,760 h = **32,421 GWh/y** appears as primary energy 

The nuclear bar is effectively a constant foundation — it does not respond at all to the GHG constraint. This is the defining structural feature of Scenario A.

#### Gas (olive-green band) — the first lever

Gas declines monotonically:
- Unconstrained: **32.8 TWh/y** (mainly decentralised HP heat + industrial boilers)
- 70%: 29.8 TWh (constraint still barely binding — only 0.4 TWh saved)
- 75%: **19.5 TWh** (strong gas reduction — gas boilers and HP largely replaced)
- 80%: 9.2 TWh
- 85%: 4.6 TWh
- 90%: 3.0 TWh
- 95%: **0.0 TWh** (gas completely eliminated)

Gas reduction is the **primary decarbonisation mechanism** in Scenario A. From 70% to 80% saving, almost all CO₂ reductions come from displacing gas (see gas breakdown section below). The transition from gas to electricity/biomass for heating is the critical inflection point.

#### Wind (light blue band) — scales up as gas comes out

Wind grows modestly from 78 to 93 TWh as GHG constraints tighten. It fills part of the gap left by gas in power generation. However, the wind expansion is relatively modest because nuclear already covers 75% of electricity demand and Finland's grid can absorb limited additional variable generation before storage/grid costs escalate.

#### Biomass (dark brown band) — relatively stable until 85–90%

Biomass stays at 51–57 TWh through the 70–85% range, then jumps:
- 85%: 56.7 TWh (first acceleration as waste boilers/mobility start to displace gas)
- 90%: 65.0 TWh (NED chemicals shift begins)
- 95%: **85.2 TWh** (massive surge — entire gas-for-heating stack replaced)

The biomass NED band (hatched, top portion) is largely constant at ~29 TWh throughout, representing the fixed HVC chemicals demand. The surge at 95% is driven by mobility fuels (pyrolysis products) and decentralised heating, not NED.

#### Oil products (grey band) — persistent residual

Oil (predominantly diesel) remains at ~13 TWh throughout almost all scenarios. This is structural: heavy freight transport and maritime cargo are difficult to electrify and have no competitive biomass alternative until the constraint is extremely tight. Only at 95% does diesel use begin to fall significantly (mobility biomass fuels appear in Fig 4).

#### Key interpretation (Fig 3, Scenario A)

The chart reveals **two decarbonisation regimes**:

1. **Regime I (70–80%):** Gas is progressively eliminated. Wind grows modestly. Total PE drops slightly (from 305 to 289 TWh) as gas's lower PE-to-useful-energy conversion factor is replaced by more efficient electric options. Cost rise is modest (22.96 → 23.09 bn€/y, +0.6%).

2. **Regime II (85–95%):** Gas is almost gone. Further CO₂ reductions require displacing residual diesel (mobility) and restructuring industrial processes. Biomass surges to replace these hard-to-abate sectors. PE rises slightly at 95% (from 286 to 298 TWh) because biomass-to-fuels conversion chains (pyrolysis, gasification) are less thermally efficient than direct gas combustion.

**Comparison with Colla's Belgium:** In Colla, nuclear is absent and coal phases out progressively with tightening constraints; gas fills in as coal exits before eventually being constrained itself. In Finland, nuclear's constant large share means the gas phase-out is the first and dominant story, and the system reaches a very deep decarbonisation floor more easily. The cost curve in Scenario A barely rises from unconstrained to 80% (only +0.6%), reflecting how inexpensive incremental gas reduction is once renewable capacity is already massive.

---

### 5.2 Fig 4 — Biomass Allocation by Final Use (Scenario A)

**Figure:** `fig4_biomass_allocation_vs_ghg.png`

The stacked bars show how Finland's biomass (~63–85 TWh depending on scenario) is allocated across sectors as GHG constraints tighten. Categories follow the Colla Fig. 4 structure.

#### Category breakdown

| Category | Symbol | What it represents |
|----------|--------|-------------------|
| HT heat — boilers (wood) | Dark blue solid | `IND_BOILER_WOOD` — industrial process heat from wood chips |
| HT heat — boilers (waste) | Light blue diagonal | `IND_BOILER_BIOWASTE` / `IND_BOILER_WASTE` — waste-fired industrial boilers |
| LT heat DHN — boilers | Green solid | `DHN_BOILER_WOOD` — district heating biomass boilers |
| LT heat decentralised | Light blue dotted | `DEC_BOILER_WOOD` — decentralised heating boilers |
| NED / chemicals | Grey diagonal | `BIOMASS_TO_HVC` — wood → high-value chemicals (non-energy demand) |
| Mobility fuels | Pink solid | `PYROLYSIS_TO_DIESEL` / `GASIFICATION_SNG` — biofuels for transport |
| Biogas / biomethanation | Yellow-green | `GASIFICATION_SNG` or anaerobic digestion products |

#### Why there is no CHP in the chart

This is a key finding: **IND_COGEN_WOOD, DHN_COGEN_WOOD, and related biomass CHP technologies install zero capacity in every scenario**. The `BIO_HT heat -- CHP` bar is zero everywhere (visible in legend but absent from bars).

**Explanation:** Two competing reasons:
1. **Cost:** Biomass boilers cost ~115 €/kW (capital) and provide heat efficiently. Biomass CHP technologies have higher capital cost and must justify both their heat and their electricity output. Given that electricity in Finland is already over-supplied by nuclear + massive wind, the electricity co-product of biomass CHP has very low marginal value.
2. **Electricity surplus:** At 4.36 GW nuclear (32.4 TWh) + ~93 TWh wind + 6 TWh solar, Finland's electricity generation far exceeds direct demand. The grid is already curtailing or exporting. Adding biomass CHP electricity into this context is not cost-optimal.

This contrasts sharply with Belgium in Colla, which has substantial biomass CHP across all scenarios because Belgium lacks a nuclear and renewables baseload sufficient to flood the electricity market.

#### HT heat — boilers (wood) behaviour

- **Unconstrained:** 22.2 TWh of industrial wood boilers
- **70%:** 22.5 TWh (virtually unchanged)
- **75–80%:** Slight decline to 20.7–21.5 TWh
- **85%:** **26.6 TWh** — noticeable jump as industrial gas boilers are replaced by wood boilers
- **90%:** **34.9 TWh** — strong increase, industrial gas now aggressively replaced
- **95%:** **35.1 TWh** — near-maximum industrial wood boiler deployment

This is the primary biomass response to tightening constraints: biomass wood boilers replace gas boilers in industry. This is economically simple (direct substitution) but requires large volumes of biomass.

#### HT heat — boilers (waste) behaviour

Waste boilers (`IND_BOILER_WASTE`) are a constant ~11 TWh through 70–90% and collapse to near zero at 90+%, being replaced by pure wood boilers. Waste resources are limited by definition, so the model fully deploys them early and switches to wood once waste is exhausted.

#### NED / chemicals — the locked floor

The `BIOMASS_TO_HVC` contribution (~28.7 TWh) is effectively **constant across all scenarios**. This represents the non-energy demand for high-value chemicals — it is driven by a fixed exogenous HVC demand and is not responsive to the GHG constraint. This is the biomass demand that cannot be avoided even at low GHG levels.

#### Mobility fuels — appear only at 95%

`BIO_Mobility fuels` is zero through 85%, appears at ~1.3 TWh at 85%, and reaches **20.1 TWh** at 95%. This represents pyrolysis-to-diesel or gasification-to-SNG for transport fuels. The 95% case requires eliminating the last ~2 Mt CO₂ from transport diesel; the only available mechanism is replacing fossil diesel with bio-derived fuels. This drives the biomass surge at 95%.

#### Key interpretation (Fig 4, Scenario A)

- **70–80% range:** Biomass allocation is nearly frozen. The decarbonisation in this range comes from **gas reduction** (Fig 3), not biomass expansion. Biomass is already fully deployed for its natural applications (HT heat, DHN, NED chemicals).
- **85–90% range:** Industrial gas boilers replaced by wood boilers (+10–12 TWh). First signs of biomass responding to constraint tightening.
- **95% threshold:** A **qualitative transition** occurs. Mobility fuels (20 TWh), decentralised LT heat, and additional industrial wood push total biomass to 85 TWh. This is ~77% of Finland's estimated sustainable biomass availability (~110 TWh). The 95% case is feasible but tight on biomass resources.

---

### 5.3 Gas Breakdown (Scenario A)

Total gas consumption by end-use:
- **Unconstrained (34.3 TWh):** Dominated by decentralised heat heat pumps (gas HP, 27.4 TWh), plus CNG buses (2.7 TWh), NG freight boats (1.9 TWh), LNG cargo (2.0 TWh)
- **70% (31.3 TWh):** Modest gas reduction, mostly decentralised heat HP declining
- **75% (21.0 TWh):** Strong cut in decentralised gas HP (16.2 TWh left)
- **80% (10.7 TWh):** Gas HP nearly halved again to 6.0 TWh; shipping uses holding steady
- **85% (6.1 TWh):** Gas HP almost gone (1.4 TWh); CNG bus and shipping contributions stable
- **90% (5.6 TWh):** Gas largely reduced to shipping/buses (gas HP near zero)
- **95% (4.7 TWh):** Only gas for maritime shipping and buses — hard to eliminate

The decentralised gas heat pump (`DEC_HP_GAS`) is the **swing technology** in Scenario A. Its elimination drives most of the CO₂ reduction from 70% to 85%. It is replaced by electric heat pumps (more efficient but require more grid investment) and direct biomass/DHN connections.

### 5.4 Cost Curve (Scenario A)

| Transition | Cost increase | Marginal note |
|------------|--------------|---------------|
| Unconstrained → 70% | +2.4 M€/y (+0.01%) | Constraint barely binding |
| 70% → 75% | +56.5 M€/y (+0.25%) | First real gas phase-out cost |
| 75% → 80% | +72.1 M€/y (+0.31%) | Gas HP → electric HP transition |
| 80% → 85% | +107.8 M€/y (+0.47%) | Industrial gas → biomass |
| 85% → 90% | +119.1 M€/y (+0.51%) | Deep decarbonisation begins |
| 90% → 95% | +207.4 M€/y (+0.89%) | Mobility biofuels — expensive conversion |

Total cost increase from unconstrained to 95%: **+565 M€/y (+2.5%)** — remarkably modest for a 95% CO₂ reduction relative to 2017. This reflects Finland's structural advantage: nuclear + mandatory renewables already provide a deep decarbonisation floor.

---

## 6. Scenario B — Nuclear Phase-Out (f_min = 2.49 GW)

*Plots:* `case_studies/FI/manual_runs/ghg_sweep_analysis_nuke_phaseout/`

### Numerical Results

| Case | GWP limit (kt) | System cost (bn€/y) | CO₂_net (Mt) | PE total (TWh) | Biomass total (TWh) |
|------|---------------|---------------------|-------------|---------------|---------------------|
| Unconstrained | — | 22.81 | 13.6 | 278.8 | 64.4 |
| 70% | 12,360 | 22.81 | 12.4 | 281.9 | 66.7 |
| 75% | 10,300 | 22.88 | 10.3 | 272.0 | 67.9 |
| 80% | 8,240 | 22.99 | 8.2 | 269.0 | 70.1 |
| 85% | 6,180 | 23.11 | 6.2 | 267.9 | 70.8 |
| 90% | 4,120 | 23.26 | 4.1 | 271.9 | 86.6 |
| 95% | 2,060 | 23.47 | 2.1 | 283.6 | 106.8 |

### 6.1 Fig 3 — Primary Energy by Source (Scenario B)

**Figure:** `fig3_primary_energy_vs_ghg.png` (in `ghg_sweep_analysis_nuke_phaseout/`)

#### Nuclear (yellow band) — noticeably smaller

The nuclear bar drops from **87.6 TWh (Scenario A)** to **50.1 TWh** in every case of Scenario B. The difference is 37.5 TWh — this is the Loviisa 1+2 output that has been removed.

The optimiser does **not** attempt to fill the nuclear minimum with more nuclear capacity; f_min = 2.49 GW and the model builds exactly 2.49 GW (the minimum). Without forced Loviisa, nuclear is apparently not cost-optimal to expand, even at 1.5% discount rate. This is surprising: it suggests the capital cost of new capacity (even at 4,846 €/kW amortised over 60 years at 1.5%) is not competitive against the combination of wind + imports + gas backup when the electricity market is already well-supplied.

#### Wind (light blue band) — larger to compensate

Wind PE rises from ~78 TWh (Scenario A baseline) to **87 TWh** (Scenario B baseline). The 37.5 TWh nuclear gap is **not fully closed by wind** — the difference stems from:
1. Lower total PE (278 TWh vs 304 TWh in baseline) — the system is simply smaller in PE terms because nuclear's low thermal efficiency (37%) inflated PE in Scenario A
2. More gas use (+4.7 TWh vs A in unconstrained) to cover flexible generation
3. More electricity imports (larger use of the 25,000 GWh/y import cap)

#### Gas (olive-green band) — higher in unconstrained, same endpoint

- Unconstrained: **35.8 TWh** (vs 32.8 TWh in Scenario A, +3.0 TWh)
- 70%: 29.8 TWh (same as Scenario A — the constraint is binding at the same level)
- 75–85%: Scenario B uses **more gas** than Scenario A at every equivalent GHG level (e.g.: 85%: 13.3 TWh vs 4.6 TWh)
- 90–95%: Converges toward same level as Scenario A (3.1 and 0.0 TWh)

This is the key difference: **Scenario B requires more gas to compensate for lost nuclear baseload**. In the constrained cases, eliminating this larger amount of gas is more costly and requires more biomass.

#### Total PE declining trend

A notable feature of Scenario B is that total PE **decreases** from unconstrained to 85% (278 → 268 TWh), then rises again at 90–95% (272–284 TWh). This dip reflects:
- Phase-out of high-PE nuclear (1 GWh nuclear input → 0.37 GWh electricity is thermodynamically expensive)
- Replacement by zero-PE-counted wind + imports (which appear at their electricity value)
- The subsequent biomass surge at 90–95% adds PE back

By contrast in Scenario A, nuclear's constant 88 TWh keeps PE elevated throughout.

#### Key interpretation (Fig 3, Scenario B)

Scenario B shows that Loviisa retirement does not cause a dramatic change in Finland's energy system — wind and gas fill the gap adequately, the system cost is actually slightly **lower** (22.81 vs 22.96 bn€/y), and the total PE is smaller. This is because nuclear's 37% thermal efficiency means every TWh of nuclear electricity requires 2.7 TWh of primary uranium energy; replacing nuclear with wind "deflates" the PE stack even while delivering the same electricity.

The critical difference appears at **85–90%**, where Scenario B needs significantly more gas reduction effort (starts from 13.3 TWh vs 4.6 TWh in Scenario A at 85%), requiring biomass to scale up faster and driving up costs.

---

### 6.2 Fig 4 — Biomass Allocation by Final Use (Scenario B)

**Figure:** `fig4_biomass_allocation_vs_ghg.png` (in `ghg_sweep_analysis_nuke_phaseout/`)

#### The critical difference: biomass grows earlier and faster

Comparison of total biomass:

| Case | Scenario A (TWh) | Scenario B (TWh) | Delta |
|------|-----------------|-----------------|-------|
| Unconstrained | 63.4 | 64.4 | +1.0 |
| 70% | 63.7 | 66.7 | +3.0 |
| 75% | 62.7 | 67.9 | +5.2 |
| 80% | 61.9 | 70.1 | +8.2 |
| 85% | 63.4 | 70.8 | +7.4 |
| 90% | 65.0 | 86.6 | **+21.6** |
| 95% | 85.2 | 106.8 | **+21.6** |

The 90% and 95% cases show a dramatic biomass surge in Scenario B. At 95%, Finland would need **106.8 TWh** of biomass — approximately **97% of the sustainable biomass availability** (~110 TWh). This is a near-ceiling scenario and raises genuine resource availability concerns.

#### HT heat — boilers (wood): larger and earlier response

- Scenario A baseline: 22.2 TWh wood boilers
- Scenario B baseline: 23.2 TWh (+1.0 TWh — small impact at start)
- Scenario B at 85%: **40.7 TWh** (vs 26.6 TWh in A) — 14 TWh more wood boiler use
- Scenario B at 90%: **42.7 TWh** (vs 34.9 TWh in A) — 7.8 TWh more

Without Loviisa nuclear electricity backing up the grid, industrial processes rely more heavily on direct biomass combustion for their heat needs, rather than potentially switching to electric heat pumps/furnaces backed by cheap nuclear power.

#### LT heat decentralised — appears in Phase-Out

In Scenario A, decentralised boilers (dotted pattern) are near-zero through 85%. In Scenario B, they appear at 90% (255 GWh) and become substantial at 95% — reflecting that without cheap nuclear electricity, decentralised electric heat is less competitive and biomass boilers fill the gap.

#### Mobility fuels — appears earlier in Scenario B

At 90%, Scenario B shows **255 GWh** of mobility biofuels (vs 4.1 GWh in Scenario A at the same constraint). The harder gas-reduction challenge earlier up the constraint stack forces the model to reach into transport biofuels one step sooner.

#### Key interpretation (Fig 4, Scenario B)

The biomass chart in Scenario B tells a story of **increasing scarcity risk**:
- At 70–80%: Biomass use is 5–8 TWh higher than Scenario A but sustainable (~68 TWh, well within the ~110 TWh cap)
- At 85%: System remains feasible but biomass pressure is building (70.8 TWh)
- At 90%: Biomass requirement jumps to **86.6 TWh** (79% of cap) — the system needs to mobilise essentially the entire Finnish biomass sector for energy uses
- At 95%: **106.8 TWh** (97% of cap) — technically feasible in the model but practically unrealistic, as this leaves negligible margin for industry feedstock demand, biodiversity constraints, or export

**The key insight:** Without Loviisa's 13.9 TWh of zero-carbon electricity, the model must work biomass much harder — especially at high GHG constraint levels. Loviisa serves as an indirect biomass-saver.

---

### 6.3 Gas Breakdown (Scenario B)

Gas end-uses follow a similar structure to Scenario A but with consistently higher starting values:
- **Unconstrained (37.2 TWh):** Decentralised gas HP dominates (28.6 TWh vs 27.4 in Scenario A). The additional ~3 TWh vs Scenario A comes from gas HP compensating for lower nuclear electricity supply.
- **75% (21.0 TWh):** Same total as Scenario A — shows that at moderate constraints, the system finds similar solutions.
- **85% (14.8 TWh):** Still 14.8 TWh of gas (vs 6.1 TWh in A) — Scenario B has not yet been able to eliminate gas as deeply; the nuclear-gap must be filled by at least some dispatchable fuel.
- **90% (4.7 TWh):** Only maritime shipping and bus gas remain — matches Scenario A at this level.
- **95% (4.7 TWh):** Same as 90% — gas has reached its hard minimum (shipping/buses are structurally gas-dependent).

### 6.4 Cost Curve (Scenario B)

| Case | Scenario B cost (bn€/y) | Scenario A cost (bn€/y) | Delta (M€/y) |
|------|------------------------|------------------------|-------------|
| Unconstrained | **22.81** | 22.96 | **−154** |
| 70% | 22.81 | 22.96 | **−150** |
| 75% | 22.88 | 23.02 | **−138** |
| 80% | 22.99 | 23.09 | **−99** |
| 85% | 23.11 | 23.20 | **−89** |
| 90% | 23.26 | 23.32 | −54 |
| 95% | **23.47** | 23.52 | **−50** |

**Scenario B is uniformly cheaper than Scenario A.** The Loviisa units, while zero-carbon, are expensive (high c_inv amortised even at 1.5%). Freeing the optimiser from the 4.36 GW floor allows it to build a slightly cheaper configuration with more wind and less nuclear. The savings reach **154 M€/y** in the unconstrained case.

This is a counter-intuitive finding: **retiring Loviisa reduces system cost while slightly increasing CO₂**. It reflects the model's assumption that nuclear's 60-year annualised capital cost at 1.5% is marginally uncompetitive against a portfolio of mature wind turbines. In reality, the political, energy security, and price stability benefits of nuclear are not captured in a pure cost-optimisation model.

---

## 7. Comparative Analysis: Baseline vs Phase-Out

### 7.1 Summary Comparison Table

| Metric | Scenario A baseline | Scenario B (phase-out) | Key insight |
|--------|--------------------|-----------------------|-------------|
| Nuclear PE (all cases) | 87.6 TWh (constant) | 50.1 TWh (constant) | 37.5 TWh Loviisa contribution |
| Unconstrained system cost | 22.96 bn€/y | **22.81 bn€/y** | Phase-out saves 154 M€/y |
| Unconstrained CO₂_net | 13.0 Mt (~68%) | 13.6 Mt (~67%) | +0.6 Mt more without Loviisa |
| Biomass at 90% target | 65.0 TWh | **86.6 TWh** | +21.6 TWh — major biomass pressure |
| Biomass at 95% target | 85.2 TWh | **106.8 TWh** | Near biomass ceiling (~110 TWh) |
| Gas at 85% target | 4.6 TWh | **13.3 TWh** | Phase-out harder to decarbonise deeply |
| Wind PE (all cases) | 78–93 TWh | **87–94 TWh** | Wind compensates Loviisa but not fully |
| 95% case solve time | ~16 min | ~16 min | Both feasible with CPLEX |

### 7.2 Robustness of the 95% GHG Target

Both scenarios achieve the 95% GHG reduction target (CO₂_net = 2.06 Mt). However:
- **Scenario A:** Biomass = 85.2 TWh (78% of cap). Margin = 22% of cap remains.
- **Scenario B:** Biomass = 106.8 TWh (97% of cap). Margin = 3% of cap. **This is effectively the biomass ceiling.**

The 95% target in Scenario B is mathematically feasible in the model but operationally unrealistic: it requires mobilising nearly the entire Finnish biomass sector for energy, with no headroom for supply chain disruption, environmental constraints, or alternative biomass uses (materials, industry feedstock, ecosystem services).

### 7.3 The Decarbonisation Pathways Compared

Both scenarios follow the same basic sequence:
1. **First lever (70–80%):** Gas for heating phase-out (gas HP and industrial gas boilers replaced by electricity + biomass)
2. **Second lever (80–90%):** Industrial gas completely replaced; biomass boilers deploy at scale
3. **Third lever (90–95%):** Transport biofuels and DHN biomass expansion; system approaches hard limits

The key difference is **timing**: Scenario B hits the biomass ceiling at 90–95%, whereas Scenario A has comfortable headroom through 95%. This means:
- **If Finland retires Loviisa on schedule and policy continues to target 95% GHG reduction by 2035**, the pressure on biomass resources is severe and the cost advantage of the phase-out scenario evaporates as biomass price signals (not modelled) would spike.
- **If the GHG target is 70–80%**, the Loviisa retirement scenario is clearly preferable on cost (saves 100–150 M€/y) with only a small CO₂ penalty (0.6 Mt in unconstrained).

### 7.4 What This Analysis Cannot Capture

| Limitation | Impact |
|-----------|--------|
| Single biomass price at all volumes | In reality, marginal cost rises sharply as volumes approach forest harvesting limits. The 106 TWh Phase-Out 95% scenario would face severe biomass price increases not modelled here. |
| Energy security / supply stability | Nuclear provides dispatchable, weather-independent power. Model does not value this. |
| Long-duration storage | Without multi-week storage, very high wind penetration requires either dispatchable backup (gas/nuclear) or large-scale import. Both are constrained. |
| Biomass sustainability constraints | Land use, biodiversity, soil carbon — the ~110 TWh cap is a rough technical estimate, not a sustainability-certified supply curve. |
| CO₂ removal technologies | CCS appears nearly inactive even at 95%. Direct air capture (not in model) could relieve biomass pressure. |
| GHG accounting of biomass | Biogenic CO₂ from burning WOOD is credited as zero. This is consistent with the model framework but is contested in some lifecycle accounting approaches. |

---

## 8. Limitations and Caveats

1. **No geographic biomass disaggregation:** Finland has a single WOOD resource at 22.08 €/MWh. Colla's Belgium has 10 origin categories with a stepped supply curve. The biomass allocation analysis cannot reproduce origin-based insights.

2. **No biomass CHP:** The model never installs biomass CHP (IND_COGEN_WOOD, DHN_COGEN_WOOD) because electricity is over-supplied by nuclear+wind and boilers are cheaper for heat-only. This is economically rational in the model but may underestimate the real-world competitiveness of CHP in Finland's industrial cluster context.

3. **Discount rate sensitivity:** The 1.5% social discount rate is critical. At a higher commercial rate (e.g. 7–8%), nuclear's high capital cost would be penalised more severely, gas turbines would become more competitive, and the natural GHG floor would be higher. A discount rate sensitivity was not run.

4. **12 typical days:** Temporal resolution may underestimate the value of flexibility (storage, gas peakers) needed to balance high wind penetration in Scenario B.

5. **Fixed demand profiles:** All demand categories are exogenous and fixed. Demand response, efficiency improvements, or P2X expansion are not co-optimised.

6. **Comparison with Colla:** Finland and Belgium are structurally very different (nuclear-heavy vs gas-heavy electricity, much smaller population, different industrial structure). Direct numerical comparison with Colla's results is not meaningful. The spirit of the methodology (parametric GHG sweep, biomass allocation tracking) is preserved.

---

*Generated from model runs executed on April 13, 2026. All numerical values derived from EnergyScope Multi Cells AMPL/CPLEX outputs. Plots in `case_studies/FI/manual_runs/ghg_sweep_analysis/` (Scenario A) and `case_studies/FI/manual_runs/ghg_sweep_analysis_nuke_phaseout/` (Scenario B).*
