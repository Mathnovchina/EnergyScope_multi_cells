---
created: 2026-04-28T09:50
updated: 2026-04-28T14:00
---

# Concept Note: Coupled Forest–Energy Modelling for Finland
## Biomass Supply Curves under Management Scenarios and Natural Disturbance Shocks

**Author:** Matthieu Bordenave  
**Institutions involved:** University of Pisa, IIASA (ForestNavigator / WP3), University of Jyväskylä (JYU), UCLouvain  
**Date:** April 2026  
**Status:** Draft for internal circulation

---

## 1. Background and Motivation

Biomass from forests plays a central role in Finland’s energy system, supplying around 25% of primary energy, largely through industrial wood residues, logging by-products, and district heat and CHP applications. Yet the available supply is not static: it is shaped by forest management choices, competing industrial uses (pulp, paper, sawnwood), ecological constraints, and increasingly by natural disturbances amplified by climate change.

Previous work by Colla et al. (2022) showed for Belgium that representing biomass as multi-step supply curves — differentiated by feedstock origin, quality, and marginal cost — significantly changes the optimal allocation of biomass in an energy system, particularly at high decarbonisation levels. The Finnish case is structurally richer and more policy-relevant: Finland has both a much larger domestic biomass endowment and a contested policy landscape (Blattert et al. 2022) where biodiversity, bioeconomy, and climate strategies set conflicting targets on harvest levels.

At the same time, the ForestNavigator project (IIASA WP3, D3.4) has demonstrated that natural disturbances — windstorms, bark beetle outbreaks, and wildfires — modelled through coupled FLAM, G4M, and PICUS algorithms, can substantially alter forest biomass trajectories across Europe, including in the boreal north. These disturbances create temporary calamity wood pulses and long-term reductions in forest growing stock, which have direct implications for the energy sector if biomass plays a major role in the energy mix.

This research proposes to couple the ForestNavigator disturbance modules (FLAM, PICUS) with the Finnish forest model developed by the University of Jyväskylä (JYU) research team — hereafter referred to as the FORTRAN model — which provides higher spatial and structural resolution for Finnish conditions than the pan-European G4M setup. The coupled model will generate scenario-specific annual biomass supply curves that are fed into EnergyScope Finland, enabling the study of both long-run management trade-offs and short-term disturbance shocks on the Finnish energy system.

---

## 2. Objectives

1. **Couple disturbance modules (FLAM, PICUS) with the Finnish forest model (FORTRAN)** to simulate biomass supply trajectories for Finland under contrasting management scenarios and climate pathways, with higher spatial resolution and Finnish-specific parameterisation than the pan-European G4M setup used in ForestNavigator D3.4.

2. **Construct annual biomass supply curves for Finland** for each management scenario and target year (2030–2050), differentiating feedstock by type, quality, and marginal cost, following the methodology developed by Colla et al. (2022) for Belgium.

3. **Integrate the supply curves into EnergyScope Finland** to optimise the energy mix under each forest management scenario and assess the effects on system cost, technology choice, and GHG performance across varying decarbonisation targets.

4. **Analyse the effect of a natural disturbance shock** (windstorm + bark beetle compound event) on the Finnish energy system by comparing a pre-shock (2030) and post-shock (2033) EnergyScope snapshot, with constrained energy system flexibility reflecting realistic investment lead times.

---

## 3. Research Partners and Roles

| Partner | Model / Tool | Role |
|---|---|---|
| **IIASA — ForestNavigator WP3** | FLAM (wildfire), PICUS (bark beetle, windstorm) | Provide / adapt disturbance modules for coupling with FORTRAN; provide EU-scale D3.4 context for scenario consistency |
| **JYU / Luke — Finnish research team** | FORTRAN (Finnish forest growth simulator, NFI-based) | Run stand-level forest simulations under management scenarios; provide harvested volume, residues, age structure, and deadwood trajectories |
| **UCLouvain (J. Borde)** | EnergyScope Finland (ESTD) | Build supply curves from coupled model outputs; run and analyse energy system optimisation; lead coordination |

**Note on coupling (key question for IIASA):** The IIASA supervisor has indicated that coupling FLAM/PICUS to FORTRAN is technically feasible. The purpose of this concept note is to clarify precisely what input data FORTRAN must provide for this coupling to be implemented. Section 6 details this.

---

## 4. Scenarios

Three long-term scenarios are defined, aligned with the scenario families used in Blattert et al. (2022), Mönkkönen et al. (2024), and ForestNavigator D3.4, plus a transient disturbance-shock scenario.

| Scenario | Label | Forest management logic | Policy equivalent (Blattert) | G4M equivalent (D3.4) | Harvest level (Mönkkönen) |
|---|---|---|---|---|---|
| **Intensive** | S1 | Maximise roundwood + energy residues; standard rotation forestry; BAU/IBAU regimes | Bioeconomy Strategy (BES) | Economic | ~96% of MAI ceiling |
| **Balanced** | S2 | NFS targets; moderate biodiversity measures; mixed rotation + CCF | National Forest Strategy (NFS) | Societal | ~80% of MAI ceiling |
| **Conservation** | S3 | Biodiversity first; extended rotations, CCF, protected area expansion; deadwood retention per IUCN | Biodiversity Strategy (BDS) | Conservation | ~60% of MAI ceiling (safe operating space) |
| **Disturbance shock** | S4 | S1 or S2 pre-shock baseline, followed by compound windstorm + beetle event; constrained post-shock recovery | — | Economic + calamity | Temporary surplus then structural deficit |

Each of S1–S3 is run under two climate pathways: **RCP 4.5 (GWL2)** and **RCP 8.5 (GWL3)**, giving six forest trajectories. S4 is run under GWL2 as the primary shock case, with GWL3 as a sensitivity.

---

## 5. Methodology

### Phase A — Coupling FORTRAN with FLAM and PICUS

The core modelling innovation is running FLAM (wildfire) and the PICUS algorithms (bark beetle, windstorm) on top of the FORTRAN forest model rather than G4M, in order to exploit Finland-specific NFI data, stand-level forest structure, and Finnish boreal species parameterisation. The coupling follows the architecture described in D3.4 Section 2.4.

**Coupling architecture:**

```
FORSITEII climate dataset (Lehner et al. 2024)
   |  30×30 arcsec, daily: temperature, wind gust, precipitation,
   |  radiation, VPD — GWL<2.0 and GWL3.0 pathways
   v
FORTRAN (annual time-step, stand-level)
   |  outputs: litter/CWD density (gC/m²), leaf/stem/root biomass,
   |           forest cover fraction, broadleaf fraction,
   |           LAI, spruce share, basal area, stem volume,
   |           spruce tree count, age (stem-biomass-weighted)
   v
FLAM (wildfire risk and burned area)
PICUS-Bark Beetle (damage probability, stems killed/ha)
PICUS-Storm (windthrow volume, species × age × wind gust)
   |  outputs: disturbance-killed volume by type,
   |           post-disturbance fuel accumulation
   v
FORTRAN post-disturbance dynamics
   |  outputs: salvage harvest volume, regeneration trajectory,
   |           new age structure, long-term supply reduction
   v
Annual biomass supply curves (Phase B)
```

**Annual outputs required from the coupled model** (for each year 2025–2060, each scenario × climate pathway):
- Harvestable stemwood volume (m³/yr) by species (pine, spruce, birch)
- Logging residues available (branches, tops, m³/yr)
- Small-diameter and pre-commercial thinning volume (m³/yr)
- Stump/root biomass potential (m³/yr, scenario-dependent; excluded in S3)
- Disturbance-killed volume (m³/yr) by agent (beetle, wind, fire), tagged as salvageable vs. non-recoverable
- Minimum deadwood retention volume (m³/ha) by scenario — constraint on residue collection
- CWD/litter fuel load trajectories (input to FLAM for fire risk feedback)
- Post-disturbance regeneration area and timeline (affecting future supply)

### Phase B — Biomass Supply Curve Construction

For each scenario and target year, a step-wise marginal cost supply curve is constructed following Colla et al. (2022):

LineC_{supply}(Q) = C_{harvest}(Q) + C_{processing}(Q) + C_{transport}(Q, d)Line

**Feedstock categories (ordered by marginal cost):**

| Step | Category | Availability | Marginal cost range | Constraint |
|---|---|---|---|---|
| 1 | Logging residues — chips (branches, tops) | ~30–50% of residue volume; floored by deadwood retention rate | €10–20/MWh delivered | Ecological floor per scenario |
| 2 | Small-diameter energy wood / thinning biomass | FORTRAN thinning schedule output | €18–28/MWh | Industrial wood demand first |
| 3 | Stumps and roots | Site-type dependent; excluded in S3 | €25–35/MWh | Nutrient/ecological constraint |
| 4 | Import (EU pellets/chips) | ENSPRESO-derived, scenario-independent | €30–45/MWh | Supplementary only |
| 5 | Calamity wood — Q3 (S4 only) | PICUS output × salvage fraction; time-limited 18–24 months | €8–18/MWh | One-time pulse; quality-penalised |

**Wood quality classes** (determining which conversion technologies can use each fraction):
- **Q1 — Forest primary** (dry conifer/birch stemwood, logging chips): suitable for all thermochemical routes (boiler, CHP, gasification, pellets)
- **Q2 — Mixed residual** (stumps, bark, contaminated biomass): higher ash/moisture; capped share in gasification/pyrolysis
- **Q3 — Calamity wood** (beetle-killed or windthrown spruce, blue-stain fungal contamination, variable moisture 20–55%): direct combustion in boilers/CHP only; LHV penalty of −10 to −25% vs. Q1; share of total input capped

**Deadwood constraint:** Each scenario defines a minimum CWD volume (m³/ha) from the Mönkkönen ecological ceiling framework. This translates to a deadwood_retention_rate(scenario) parameter that caps the recovery fraction of logging residues, directly limiting Q1/Q2 supply.

### Phase C — EnergyScope Finland: Long-run Scenario Analysis

EnergyScope Finland (ESTD) is run as a **static snapshot** for target years 2030 and 2040 for each of S1, S2, S3 × GWL2/GWL3.

Supply curves are implemented as multiple parallel biomass resource entries, each with a fixed availability (vail_local, TWh/yr) and marginal cost (c_op, €/MWh):

`
WOOD_FI_Q1_A  -->  avail_local = V1,  c_op = p1   [cheapest residues]
WOOD_FI_Q1_B  -->  avail_local = V2,  c_op = p2
WOOD_FI_Q1_C  -->  avail_local = V3,  c_op = p3
WOOD_FI_Q2    -->  avail_local = V4,  c_op = p4
WOOD_FI_IMPORT-->  avail_local = V5,  c_op = p5   [EU pellets]
`

All feed the WOOD layer consumed by existing technologies (IND_BOILER_WOOD, DHN_COGEN_WOOD, DHN_BOILER_WOOD, BIOMASS_TO_HVC, etc.). Quality constraints are enforced as fractional upper bounds on Q2 input per technology.

**Key questions addressed:**
- How much of the supply curve does the optimised energy system use, and at which price steps?
- How does restricting the harvest to the ecological ceiling (S3 vs. S1) affect total system cost and GHG performance?
- Across a GHG reduction sweep (0–80%), which technologies activate when cheap biomass is exhausted?
- Does the ecologically constrained scenario (S3) force substitution toward other renewables, or does it primarily raise system cost?

### Phase D — Disturbance Shock Analysis

**Step 1 — Pre-shock baseline (2030):** Run EnergyScope under S2-Balanced + GWL2 to obtain the optimal installed capacity vector ^*_{2030}(tech)$. This represents the energy fleet that an informed planner would build before any disturbance.

**Step 2 — Simulated calamity event (2031):** Using the coupled FORTRAN + PICUS model, simulate a compound disturbance in 2031 (major windstorm over southern/central Finland followed by bark beetle outbreak in 2031–2032 driven by warmer summers under GWL2). The PICUS output provides:
- Total volume of windthrown and beetle-killed trees (m³)
- Salvageable fraction by terrain accessibility (~50–75%)
- Post-salvage trajectory: reduced harvestable stock for 10–15 years due to depleted cohorts; species shift in replanting toward pine/birch

**Step 3 — Post-shock supply curve for 2033:** The 2033 supply curve differs from the baseline in three ways:
1. **Calamity wood pulse (Q3):** Large one-time availability at low price (urgent salvage), available in 2033 run only
2. **Reduced Q1/Q2 long-term availability:** Lower vail_local reflecting damaged forest area out of productive rotation
3. **Elevated moisture / LHV penalty** on salvage fractions delivered to direct-combustion boilers

**Step 4 — Post-shock EnergyScope 2033 with limited flexibility:** Energy system investment lead times (3–7 years for biomass CHP, DHN extensions) prevent free re-optimisation. This is implemented by imposing lower bounds on installed capacity inherited from the 2030 run:

Linef_{min}(tech, 2033) = \alpha \cdot f^*_{2030}(tech), \quad \alpha \in [0.85, 1.0]Line

where $\alpha$ depends on technology lifetime and construction lead time. Technologies with lead times $\geq 3$ years cannot be newly commissioned in 2033, constraining {max}$ upward accordingly.

---

## 6. Data and Variables Required

### 6.1 From IIASA — ForestNavigator team (FLAM / PICUS coupling)

This section is the **primary request to the IIASA team**: what data and interface specifications are needed from FORTRAN for the disturbance modules to run at Finnish scale?

All inputs are required as georeferenced raster data (GeoTIFF, 30×30 arcsec grid), consistent with the FORSITEII climate dataset resolution (Lehner et al. 2024).

**Climate inputs — provided by the existing FORSITEII dataset (not from FORTRAN)**

The FORSITEII dataset (Lehner et al. 2024) already provides all climate drivers at 30×30 arcsec resolution for GWL<2.0 (≈ RCP 4.5) and GWL3.0 (≈ RCP 8.5) scenario pathways. These do **not** need to be derived from FORTRAN.

| Variable | Unit | Temporal resolution | Source |
|---|---|---|---|
| Daily maximum temperature | °C | Daily | FORSITEII / CHELSA-W5E5 bias-adjusted |
| Mean wind speed | km/min | Daily | FORSITEII / CHELSA V2.1 |
| Daily maximum wind gust | km/min | Daily | FORSITEII / ERA5 Random Forest downscaling |
| Relative humidity / VPD | %, — | Daily | FORSITEII |
| Precipitation | mm/day | Daily | FORSITEII |
| Global radiation | W/m² | Daily | FORSITEII |
| Lightning frequency | flashes/month/km² | Monthly | Existing dataset (D3.4) |

**Forest structure and fuel load inputs — required from FORTRAN (for FLAM wildfire module)**

| Variable | Unit | Temporal resolution | Notes |
|---|---|---|---|
| Litter surface density | gC/m² | Yearly | Dead fuel input; drives fire weather moisture code |
| Coarse woody debris (CWD) density | gC/m² | Yearly | Dead fuel input; accumulates post-disturbance |
| Leaf biomass | gC/m² | Yearly | Living fuel; drives canopy fire spread |
| Stem biomass | gC/m² | Yearly | Living fuel; by species group |
| Root biomass | gC/m² | Yearly | Living fuel |
| Forest cover fraction | 0–1 | Yearly | Delineates forested pixels |
| Broadleaf fraction | 0–1 | Yearly or constant | Affects fire spread rate and fuel moisture |

**Additional forest structure inputs — required from FORTRAN (for PICUS bark beetle and windstorm modules)**

The PICUS modules share all the fuel-load inputs above and additionally require the following stand structural variables:

| Variable | Unit | Temporal resolution | Notes |
|---|---|---|---|
| Leaf Area Index (LAI) | m²/m² | Yearly or constant | Canopy structure for beetle pressure and storm resistance |
| Spruce share fraction (*Picea abies*) | 0–1 | Yearly or constant | Primary predictor of bark beetle susceptibility |
| Total basal area | m²/ha | Yearly or constant | Stand density; affects both beetle and windthrow probability |
| Stem volume | m³/ha | Yearly or constant | Stand-level growing stock |
| Number of spruce trees per ha | stems/ha | Yearly or constant | Used directly in beetle damage probability calculation |
| Mean stand age (weighted by stem biomass) | years | Yearly or constant | Older stands are more susceptible to both agents |

**Outputs that IIASA will return to this project (from coupled FORTRAN + FLAM/PICUS):**

| Variable | Unit | Notes |
|---|---|---|
| Annual wildfire burned area | ha/yr | By sub-region (south/central/north Finland) |
| Annual bark beetle damage volume | m³/yr | By species; split recoverable vs. total |
| Annual windstorm damage volume | m³/yr | By species; split recoverable vs. total |
| Post-disturbance living biomass trajectory | tC/ha/yr | For supply curve recovery timeline |
| Disturbance damage by GWL × management scenario | — | Full 6-scenario matrix |

### 6.2 From the Finnish research team (FORTRAN)

| Variable | Unit | Source |
|---|---|---|
| Annual harvestable stemwood by species | m³/yr | FORTRAN output per scenario |
| Logging residue volume by scenario | m³/yr | FORTRAN, by management regime |
| Age structure evolution (2025–2060) | ha by age class | FORTRAN |
| Per-scenario minimum deadwood retention | m³/ha | Mönkkönen ecological ceiling thresholds |
| Thinning schedule and volumes | m³/yr | FORTRAN (BAU, CCF, IBAU regimes) |

### 6.3 From Finnish national statistics / literature (J. Borde)

| Variable | Unit | Source |
|---|---|---|
| Harvesting cost by terrain class | €/m³ | Luke forestry cost statistics |
| Chipping / processing cost | €/MWh | VTT / Finnish Energy |
| Transport cost by distance class | €/MWh | Luke / biomass terminal data |
| Industrial wood demand (pulp/paper) | Mm³/yr | UPM, Metsä, Stora Enso annual reports; Luke |
| Calamity wood: salvage rate, LHV penalty, moisture | — | VTT; Luke post-storm reports (2001 Pyry, 2010) |
| Forest industry absorption capacity at calamity peak | Mm³/yr | Luke market analyses; Central European reference |
| EnergyScope Finland technology parameters (2030) | — | Existing ESTD dataset (interpolation 2017→2035) |

### 6.4 From IIASA — forest management economics data (F. di Fulvio)

Fulvio di Fulvio (IIASA) has developed pan-European datasets on forest management costs, labour inputs, and capital requirements for various silvicultural operations. These data could complement or partially substitute for the Luke national statistics in Section 6.3 for the supply curve cost steps, and may already contain Finland-specific or Nordic breakdowns at regional resolution. The JYU team may also find them useful for calibrating management cost assumptions in FORTRAN scenario runs.

| Variable | Unit | Notes |
|---|---|---|
| Harvesting cost by operation type (clear-cut, thinning) | €/m³ | Pan-European; verify Finnish coverage and data vintage |
| Labour input per silvicultural operation | person-days/ha | Relevant for CCF vs. rotation forestry cost differential |
| Capital cost of harvesting machinery | €/m³ | Mechanised vs. manual; affects terrain-class cost steps |
| Forest road / transport infrastructure cost | €/m³ | Remote stand access component of supply curve |
| Silvicultural investment (planting, tending) | €/ha | Relevant for post-disturbance regeneration cost in S4 |

**Note:** If di Fulvio's dataset covers Finland at sub-national resolution (south / central / north), it could directly parameterise the harvesting cost steps in Phase B, reducing reliance on Luke point estimates. A cross-validation between the two sources is recommended before adopting either.

---

## 7. Expected Results

Inspired by Colla et al. (2022) for Belgium, and adapted to Finland’s specific context:

**A. Supply curve shape and scenario divergence**
- S1 (Intensive) will produce a flat, wide supply curve with cheap residues available at large volume; S3 (Conservation) will produce a shorter, steeper curve with a hard cliff at the ecological ceiling. The gap between S1 and S3 supply curves quantifies the biodiversity–energy trade-off.
- The absolute supply volumes will be much larger than Belgium’s (~26 Mha productive forest vs. ~0.7 Mha), making domestic biomass structurally dominant in Finland’s energy mix.

**B. EnergyScope allocation across GHG targets**
- At low GHG reduction targets, cheap logging residues (Q1 step 1) are sufficient; industrial boilers and district heat CHP dominate.
- At high reduction targets (>50–60%), cheaper domestic steps are exhausted and the model faces a choice between expensive imports, electrification, or accepting higher system cost under S3.
- Under S3, the ecological ceiling will constrain biomass availability below the level needed for purely biomass-based deep decarbonisation, forcing broader deployment of wind, heat pumps, and potentially biogas pathways.

**C. Disturbance shock effects**
- The calamity wood pulse in 2033 will temporarily lower marginal biomass cost (cheap, abundant salvage wood), but will be absorbed primarily by direct combustion (boilers, CHP) due to quality constraints.
- The post-shock supply deficit will reveal **stranded asset risk**: biomass CHP plants sized for S1 supply levels may be underutilised under the post-shock supply curve.
- The energy system will substitute toward gas/peat imports or accelerated wind deployment to compensate, depending on which flexibility options are unlocked.
- A key policy finding: the calamity wood pulse risks delaying the energy transition by temporarily improving the economics of direct combustion, while the structural supply deficit that follows may accelerate the push toward non-biomass renewables.

**D. Deadwood and biodiversity co-benefits**
- S3 will show that the energy cost premium of the conservation scenario is quantifiable (system cost difference vs. S1), providing a monetary value for the biodiversity co-benefit of not extracting the full biomass potential.
- Post-shock deadwood accumulation from unharvested beetle-killed material under S3 will be explicitly tracked as a co-benefit metric.

---

## 8. Open Questions and Pending Items

| # | Question | Addressed by |
|---|---|---|
| Q1 | What forest structural variables does FORTRAN currently output at what spatial/temporal resolution, and what pre-processing is needed to match PICUS/FLAM pixel grid? | **IIASA + JYU joint scoping** |
| Q2 | Is FORTRAN already spatially explicit at pixel level, or does it operate at stand/regional level requiring upscaling? | JYU team |
| Q3 | What climate inputs are already used in FORTRAN, and are they consistent with the RCP 4.5/8.5 scenarios used in D3.4? | JYU + IIASA |
| Q4 | How is industrial roundwood demand treated — as an exogenous cap on energy-available fractions, or endogenously? A simple exogenous approach (Luke statistics) is preferred for a first version. | J. Borde + JYU |
| Q5 | What is Finland’s empirical basis for calamity wood salvage rates and quality degradation (2001 Pyry storm)? Does Luke or VTT have suitable data? | JYU / Luke |
| Q6 | How does Finland’s LULUCF accounting treat disturbance-related mortality — is it excluded from the forest reference level? This affects whether calamity wood carbon should be charged to the EnergyScope GHG constraint. | JYU / Finnish SYKE |
| Q7 | Should supply curves be spatially disaggregated (south / central / north Finland)? The EnergyScope multi-cell architecture supports this. | J. Borde — decision on scope |
| Q8 | Can IIASA provide Finland-disaggregated D3.4 outputs as a benchmark for the FORTRAN-coupled results? | **IIASA team** |
| Q9 | Does F. di Fulvio's IIASA forest management cost dataset cover Finland at sufficient spatial disaggregation to validate or replace Luke harvesting cost statistics in the supply curve? Is it publicly accessible or does it require direct collaboration? | **IIASA — F. di Fulvio** |

---

## 9. Proposed Next Steps

1. **[IIASA — ForestNavigator]** Confirm feasibility of coupling FLAM/PICUS to FORTRAN; identify any gaps in the required input variables listed in Section 6.1; propose data transfer protocol and timeline.

2. **[JYU Finnish team]** Confirm FORTRAN output variables available per scenario; share per-scenario deadwood/residue retention parameters from the Mönkkönen ecological ceiling framework; confirm climate scenario consistency.

3. **[J. Borde + IIASA]** Enquire with F. di Fulvio (IIASA) whether his forest management cost dataset covers Finland; if so, use as primary cost input for supply curve steps and cross-validate against Luke statistics. Gather any remaining cost items (chipping, transport, calamity salvage) from Luke/VTT and construct prototype supply curves as a placeholder pending coupled model outputs.

4. **[J. Borde]** Build EnergyScope Finland 2030 dataset (interpolation from existing 2017/2035 inputs); implement multi-step biomass resource structure in AMPL model; test with synthetic supply curve.

5. **[All]** Agree on scenario definitions (S1–S3 harvest parameters, climate pathways) and the spatial resolution of model coupling (national vs. three regional zones).

---

## References

- Blattert, C. et al. (2022). Sectoral policies cause incoherence in forest management and ecosystem service provisioning. *Forest Policy and Economics*, 136, 102689.
- Colla, M., Blondeau, J., Jeanmart, H. (2022). Optimal Use of Lignocellulosic Biomass for the Energy Transition, Including the Non-Energy Demand. *Frontiers in Energy Research*.
- Krasovskiy, A. et al. (2025). D3.4 Assessment of natural disturbances and extreme events impact on forest mitigation potential. ForestNavigator, HORIZON-101056875.
- Lehner, F., Klisho, T., Maier, P. (2024). Daily climate data for Europe — Short documentation (README). FORSITE II / Institute of Meteorology and Climatology, January 2024. [FORSITEII climate dataset, 30×30 arcsec, GWL<2.0/3.0/4.0 scenarios, 1950–2100.]
- Mönkkönen, M. et al. (2024). Ecologically and economically sustainable level of timber harvesting in boreal forests — defining the safe operating space for forest use. *bioRxiv*, doi:10.1101/2024.06.27.600997.
