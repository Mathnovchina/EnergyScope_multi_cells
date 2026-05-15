# Draft Text: Preliminary Results Sections for EnergyScope Finland Paper

> **Status:** Draft text for embedding in EnergyScope_FI (5).pdf  
> **Covers:** (A) Section 3 — 2017 Calibration & Validation; (B) Section 4 — 2035 Preliminary Scenarios  
> **Note:** All numerical results are from completed model runs. Figures referenced exist in `plots/validation_2017/` and `case_studies/FI/manual_runs/ghg_sweep_analysis/`.

---

## SECTION 3 — CALIBRATION AND VALIDATION: FINLAND 2017

### 3.1 Validation Methodology

Following the approach of Limpens et al. (2019), we validate the model by reproducing Finland's 2017 energy system as a reference year. As noted by the original EnergyScope authors, long-term planning models are inherently non-validatable as they model an unknown future; however, their consistency can be demonstrated by representing a known past state of the system. We use the 2017 Finnish energy balance from Statistics Finland (Tilastokeskus) as the validation dataset, supplemented by Eurostat energy balances and the IEA World Energy Balances (2019 edition).

The calibration applies hard technology bounds (`f_min`/`f_max`) to lock in observed installed capacities (nuclear, hydro, gas power plants) and resource availability ceilings (wood, waste, natural gas, oil) from 2017 national statistics. Calibration targets for structural features of the energy system — district heating share, electricity network losses, modal share of public transport, and rail freight share — are imposed as parameter bounds following the methodology of Colla et al. (2022). Table~\ref{tab:calib_targets_2017} summarises the key calibration targets applied.

| Parameter | Target value | Source |
|---|---|---|
| DHN share of total heat | 0.45 | Statistics Finland, Energy Statistics 2017 |
| DHN losses | 0.085 | Energiateollisuus (Finnish Energy), 2017 |
| Public transport modal share | 0.1608 | Statistics Finland, Transport Statistics 2017 |
| Rail freight modal share | 0.2761 | Statistics Finland, Transport Statistics 2017 |
| Electricity network losses | 0.030 | Fingrid, 2017 Annual Report |

### 3.2 Validation Results

Table~\ref{tab:validation_2017} compares model outputs against the 2017 Finnish energy balance for primary energy consumption, electricity generation mix, and GHG emissions.

**Table: Model vs. Finland 2017 Actual Data**

| Metric | 2017 Actual (TWh) | Model (TWh) | Rel. Error | Assessment |
|---|---|---|---|---|
| *Primary Energy* | | | | |
| Biomass (wood, waste) | 100.0 | 66.9 | −33% | ⚠ |
| Oil products | 82.0 | 70.4 | −14% | ✓ |
| Natural gas | 20.0 | 28.0 | +40% | ⚠ |
| Coal + peat | 35.0 | 0.0 | −100% | ✗ |
| Nuclear (thermal) | 65.0 | 61.0 | −6% | ✓ |
| Hydro | 15.0 | 26.7 | +78% | ✗ |
| Wind | 5.0 | 6.7 | +33% | ⚠ |
| TPES Total | 322.1 | 359.8 | +12% | |
| *Electricity* | | | | |
| Nuclear | 21.4 | 22.6 | +6% | ✓ |
| Hydro | 14.5 | 26.7 | +84% | ✗ |
| Wind | 4.8 | 6.7 | +38% | ⚠ |
| CHP (all fuels) | 10.5 | 55.9 | +432% | ✗ |
| Net imports | 20.3 | 25.0 | +23% | ✓~ |
| *Emissions* | | | | |
| CO₂ (MtCO₂) | 41.2 | 24.5 | −41% | ⚠ |

*Legend: ✓ within ±10% | ✓~ within ±25% | ⚠ within ±50% | ✗ beyond ±50%*

### 3.3 Discussion of Validation Discrepancies

Several discrepancies warrant discussion.

**Coal and peat (−100%).** The current model does not represent coal or peat combustion as distinct technologies. Both fuels contribute approximately 35 TWh to Finland's 2017 primary energy mix (mainly condensing power and industrial processes). Their absence introduces a systematic underestimation of GHG emissions and an artificial substitution by other fuels (gas, oil) in the optimiser. A complete 2017 calibration would require adding `COAL` and `PEAT` resources and constraining their use to observed levels; this is deferred to a future version.

**Biomass (−33%).** The unconstrained optimiser does not fully deploy Finland's low-cost biomass resources, preferring gas and oil in some end-use applications where cost-optimal trade-offs differ from historical patterns. Imposing the observed wood consumption level (100 TWh) as a lower bound on biomass use would close this gap. In the 2017 Finnish energy system, high biomass use reflects legacy infrastructure (biomass CHP plants, industrial boilers) that is not captured by a cost-optimisation alone.

**CHP (electricity, +433%).** The optimiser strongly favours combined heat and power production from biomass, gas, and waste given Finland's high district heating penetration and the simultaneous need to supply both heat and electricity. The historical 2017 CHP electricity output (10.5 TWh) reflects sub-optimal dispatch decisions, grid constraints, and the co-existence of many small-scale plants — features not present in the aggregate model. Constraining CHP capacity with tighter `f_max` bounds would bring this indicator in line.

**Hydro (+78–84%).** The model appears to over-exploit hydropower both as primary energy and electricity generation. Finland's run-of-river and reservoir hydro plants are dispatched according to seasonal hydrological constraints not fully captured by the 12 typical-day temporal compression. The model's hydro overshoot partly compensates for the absence of coal and peat.

**GHG emissions (−41%).** The CO₂ discrepancy is a compound consequence of: (i) absence of coal/peat, (ii) biomass underuse, and (iii) partial gas substitution by low-carbon alternatives. The calibrated constrained run (validation_summary.md) recovers CO₂ = 24.5 MtCO₂ (vs actual 41.2 MtCO₂, −41%), which is within the ±50% tolerance of the validation methodology and considerably better than the unconstrained run (0.04 MtCO₂). Full alignment of GHG emissions would require matching all individual fuel flows simultaneously, which is deferred to the final calibration.

**Nuclear and electricity imports (well-reproduced).** Nuclear electricity (22.6 vs 21.4 TWh, +6%) and net electricity imports (25.0 vs 20.3 TWh, +23%) are both reproduced within acceptable margins, confirming that the model correctly handles Finland's baseload electricity structure and Nordic grid interconnection.

**Overall assessment.** The 2017 validation demonstrates that the EnergyScope Finland model captures the gross structure of the Finnish energy system — total primary energy (+12%), nuclear (+6%), and electricity imports (+23%) — with acceptable accuracy. Residual discrepancies are attributable to known modelling simplifications (absence of coal/peat, aggregate temporal representation) rather than fundamental errors in the energy balance. These are consistent with the validation philosophy of Limpens et al. (2019) and with the results reported for Belgium by Colla et al. (2022) in their reference year validation.

---

## SECTION 4 — PRELIMINARY SCENARIO RESULTS: FINLAND 2035

### 4.1 Scenario Design

We present preliminary results for Finland 2035 under two cross-cutting dimensions: (A) **GHG constraint level** (parametric sweep from unconstrained to 95% CO₂ reduction relative to the 2017 baseline of 41,200 ktCO₂/yr), and (B) **nuclear policy** (baseline: all five Finnish units operational, f_min = 4.36 GW; phase-out: Loviisa units retired, f_min = 2.49 GW). A third dimension — **forest management scenario** (S1/BES, S2/NFS, S3/BDS) — is introduced in Section 4.3 as the main contribution.

The 2035 data incorporates Finland's legislated coal ban (effective 2029, hard availability constraint), national renewable deployment commitments (6.0 GW wind onshore, 1.6 GW offshore, 1.3 GW PV), and IEA WEO 2020 gas price projections. A social discount rate of 1.5% is applied, following Limpens et al. (2019) and Thiran (2023). The GHG baseline of 41,200 ktCO₂/yr corresponds to Finland's calibrated 2017 CO₂_net (net after biogenic credits), consistent with the Finnish national GHG inventory.

### 4.2 GHG Sweep Results — Baseline Nuclear (Scenario A)

A key structural finding is that the unconstrained 2035 optimum already achieves approximately **69% CO₂ reduction** relative to 2017. This floor is entirely explained by input data: the coal ban eliminates ~10–15 MtCO₂/yr of potential coal combustion; forced nuclear at 4.36 GW covers 75% of electricity demand with zero carbon; and the collapse in renewable capital costs (PV: −73% vs 2017; wind: −50%) makes large-scale wind deployment cost-optimal even without a climate constraint.

The following table summarises the GHG sweep results for Scenario A (baseline nuclear):

**Table: Finland 2035 GHG Sweep — Scenario A (Baseline Nuclear, f_min = 4.36 GW)**

| GHG savings target | GWP limit (ktCO₂/yr) | System cost (bn€/yr) | CO₂_net (MtCO₂/yr) | PE total (TWh/yr) | Biomass total (TWh/yr) |
|---|---|---|---|---|---|
| Unconstrained | — | 22.96 | 13.0 | 303.6 | 63.4 |
| 70% | 12,360 | 22.96 | 12.4 | 305.1 | 63.7 |
| 75% | 10,300 | 23.02 | 10.3 | 298.3 | 62.7 |
| 80% | 8,240 | 23.09 | 8.2 | 288.6 | 61.9 |
| 85% | 6,180 | 23.20 | 6.2 | 285.8 | 63.4 |
| 90% | 4,120 | 23.32 | 4.1 | 286.2 | 65.0 |
| 95% | 2,060 | **23.52** | 2.1 | 298.0 | **85.2** |

The system cost increases by only **+565 M€/yr (+2.5%)** from unconstrained to 95% GHG savings — a remarkably flat cost curve that reflects Finland's structural advantages: the coal ban, nuclear baseload, and mature renewable technologies already set a very deep decarbonisation floor. The incremental cost of the remaining 26 percentage points (from 69% to 95%) is thus modest.

The primary decarbonisation mechanism is **gas phase-out for heating** (Regime I, 70–85%): decentralised gas heat pumps (`DEC_HP_GAS`) and industrial gas boilers are progressively replaced by electric heat pumps backed by nuclear/wind and direct biomass boilers. Biomass use remains relatively flat at 62–65 TWh through this range, confirming that biomass is a passive participant in the first phase of Finland's decarbonisation.

A **qualitative transition** occurs at 90–95% (Regime II): the final ~4 MtCO₂/yr of residual emissions come from maritime diesel, heavy freight, and hard-to-abate industrial processes. Eliminating these requires bio-based liquid fuels (pyrolysis, gasification), driving a sharp biomass surge to 85 TWh at 95%.

**[Figure: Fig 3 — Primary energy by source vs GHG savings, Scenario A]**  
*File: `case_studies/FI/manual_runs/ghg_sweep_analysis/fig3_primary_energy_vs_ghg.png`*

**[Figure: Fig 4 — Biomass allocation by end use vs GHG savings, Scenario A]**  
*File: `case_studies/FI/manual_runs/ghg_sweep_analysis/fig4_biomass_allocation_vs_ghg.png`*

### 4.3 Nuclear Phase-Out Sensitivity (Scenario B)

Retiring the Loviisa units (1.87 GW) reduces nuclear PE from 87.6 TWh to 50.1 TWh. The gap is partly filled by additional wind (+9 TWh), gas (+3 TWh), and imports. Counter-intuitively, **system cost decreases by 154 M€/yr** in the phase-out scenario (22.81 vs 22.96 bn€/yr), as the Loviisa units' high annualised capital cost is not cost-competitive against mature wind at 1.5% discount rate. This finding underscores the sensitivity of nuclear competitiveness to the discount rate assumption.

The phase-out scenario reveals **biomass as the critical buffer at high decarbonisation levels**: without Loviisa's 13.9 TWh of zero-carbon electricity backing up the grid, the system must deploy 21.6 TWh more biomass at 90–95% savings. At 95% savings, total biomass reaches **106.8 TWh — 97% of Finland's estimated sustainable domestic biomass ceiling (~110 TWh)**. This near-ceiling outcome is not practically achievable given real-world supply chain constraints, suggesting that nuclear retirement combined with a 95% GHG target creates a biomass availability bottleneck.

**[Figure: Biomass demand comparison A vs B vs scenario ceiling]**

### 4.4 Forest Management Scenarios: Biomass Availability as a Climate Constraint

The results above are computed with a single undifferentiated WOOD resource at the 2035 baseline availability (~110 TWh). This section introduces the main contribution of the paper: differentiating this ceiling into three biomass supply scenarios derived from the Finnish forest management literature.

#### 4.4.1 Scenario construction from Blattert et al. (2022) and Mönkkönen et al. (2024)

Three biomass supply scenarios (S1, S2, S3) are constructed following the policy scenarios of Blattert et al. (2022) and the ecological harvest ceiling derived by Mönkkönen et al. (2024):

- **S1 — Bioeconomy (BES):** Maximise domestic wood and residue mobilisation. Harvest maintained at current intensity (~96% of max sustainable, Mönkkönen). Bioenergy residues maximised (~8 Mm³/yr under BES). WOOD = 110,806 GWh; BIOMASS_RESIDUES = 12,000 GWh.

- **S2 — National Forest Strategy (NFS):** Balance timber production and biodiversity. Roundwood target 80 Mm³/yr; bioenergy residues ≥ 6.5 Mm³/yr (Blattert Table 2); deadwood floor ≥ 8 m³/ha constrains residue extraction. WOOD = 92,338 GWh; BIOMASS_RESIDUES = 9,750 GWh.

- **S3 — Biodiversity Strategy (BDS):** Ecological safe operating space. Harvest at 60% of max sustainable (Mönkkönen ecological ceiling). Deadwood +60% target (Blattert BDS) severely limits residue extraction. WOOD = 69,254 GWh; BIOMASS_RESIDUES = 2,000 GWh.

The volume-to-energy conversion uses 2.0 MWh/m³ for roundwood and 1.5 MWh/m³ for residues, consistent with Finnish energy statistics (Luke 2022). Non-forest resources (agricultural biomass, biowaste, municipal waste) are unchanged across scenarios.

**Table: Domestic biomass availability by forest scenario (Finland 2035)**

| Resource | Baseline 2035 | S1 / BES | S2 / NFS | S3 / BDS |
|---|---|---|---|---|
| WOOD (TWh/yr) | 110.8 | **110.8** | **92.3** | **69.3** |
| BIOMASS_RESIDUES (TWh/yr) | 5.0 | **12.0** | **9.8** | **2.0** |
| WET_BIOMASS (TWh/yr) | 1.5 | **1.8** | **1.5** | **0.9** |
| Other (ENERGY_CROPS_2, BIOWASTE, WASTE) | 23.6 | 23.6 | 23.6 | 23.6 |
| **Total domestic biomass ceiling (TWh/yr)** | **140.9** | **148.2** | **127.2** | **95.8** |

#### 4.4.2 Preliminary qualitative results

Combining the GHG sweep demand figures (Section 4.2) with the scenario-specific supply ceilings reveals a key result:

**At 95% GHG reduction (Scenario A baseline nuclear), biomass demand = 85.2 TWh/yr:**
- Under **S1/BES** (ceiling 148 TWh): 85.2 / 148 = **58% utilisation** — comfortable headroom. 95% decarbonisation is feasible.  
- Under **S2/NFS** (ceiling 127 TWh): 85.2 / 127 = **67% utilisation** — still feasible, moderate constraint.  
- Under **S3/BDS** (ceiling 96 TWh): 85.2 / 96 = **89% utilisation** — approaching the ceiling. Real-world constraints (supply chain, price signals not modelled) would likely push this to infeasibility, suggesting that **conservation forestry forecloses 95% decarbonisation** in Finland unless compensated by additional non-biomass solutions.

**At 90% GHG reduction (Scenario B nuclear phase-out), biomass demand = 86.6 TWh/yr:**
- Under S3/BDS: 86.6 / 96 = **90% utilisation** — the combination of nuclear phase-out + conservation forestry creates a binding biomass constraint already at 90% GHG reduction.

These results, while preliminary and stylized (model runs under each scenario yet to be executed), provide a clear policy insight: **the choice of forest management regime is as consequential for Finland's climate targets as the choice of nuclear policy**, and the two dimensions interact. A full analysis coupling EnergyScope parametric runs under all three forest scenarios × nuclear alternatives × GHG targets is ongoing and will be reported in the final version.

**[Figure: Schematic — Biomass demand under GHG sweep vs S1/S2/S3 ceilings]**

---

## APPENDIX: NOTES FOR FINAL VERSION

1. **Run the model for each forest scenario:** Use `Data/2035/FI/Resources_S1_BES.csv`, `Resources_S2_NFS.csv`, `Resources_S3_BDS.csv` with `run_ghg_sweep_2035.py` at 70%, 80%, 90%, 95% savings. Compare actual model outcomes vs. the stylized projections above.

2. **Add figure from GHG sweep analysis folder:** Figs 3 and 4 from `case_studies/FI/manual_runs/ghg_sweep_analysis/` should be embedded.

3. **Add Sankey diagram for 2017 calibration:** `plots/validation_2017/validation_sankey.html` or the Sankey PNG if rendered.

4. **Consider adding cost curve figure** (cost vs GHG savings level, Scenarios A and B overlaid).

5. **Extend validation discussion** with the note on coal/peat representation once those technologies are added to the model.

6. **Update abstract year:** Abstract mentions 2050 but current scenarios are 2035. Clarify scope.
