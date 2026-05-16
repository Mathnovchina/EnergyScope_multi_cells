# Paper Sections Draft — Finland Validation, 2035 Scenarios, and Next Steps

Status: insertion-ready draft text based on the files currently present in the repository.

Scope of this draft:
- 2017 validation section built from the calibrated baseline run `case_studies/FI/manual_runs/20260323_173930__2017_baseline`
- 2035 scenario-design section built from the current forest biomass scenario files and documentation
- 2035 results section built from the completed `forest_scenarios_2035` run matrix and final plots
- future-work section on disturbance shocks built from `Docs/Coupled_Forest_Energy_Modelling_Finland_concept_note.docx`

Important manuscript corrections before insertion:
- The current PDF still mixes a 2050 framing with a 2035 scenario implementation. The sections below are written for the actual completed 2035 analysis.
- The sentence in the current abstract stating that “simulation results are currently under production” is no longer correct for the 3 x 3 forest-scenario matrix.
- The 2017 validation run uses `relax_co2 = true`; this is appropriate for historical reproduction, but it must not be presented as the operating assumption of the 2035 forward-looking runs.
- The old 80% GHG forest-scenario column and the original optimistic S3-BDS ENSPRESO values should not be used in the paper. The final matrix is `unconstrained`, `ghg_95pct`, and `ghg_95pct_nonuke`, with the revised conservative S3-BDS supply.

---

## Suggested Section — Finland 2017 Validation

### Validation objective and protocol

To establish model credibility before turning to forward-looking scenarios, the Finnish implementation of EnergyScope was calibrated against a historical baseline year. The validation run retained the observed 2017 demand structure and technology fleet and applied an 18-patch calibration chain to match the main Finnish energy-balance aggregates. The final reference run is `20260323_173930__2017_baseline` (`v37_solar` in the run notes), solved with 12 typical days and `relax_co2 = true` in order to avoid a non-physical forced-CCS artifact in the historical reproduction. In the calibration dashboard, this run reaches a weighted score of 1.2% over the 14 scored indicators documented in `Docs/finland_2017_validation_justifications.md`.

This validation strategy follows the standard EnergyScope logic: the model is not “validated” as a predictive tool for the future, but its internal consistency is tested by checking whether a constrained historical configuration reproduces a known national energy system with acceptable deviations.

### Main validation results

Table X compares the calibrated 2017 baseline to the Finnish statistical reference values stored in `case_studies/FI/manual_runs/20260323_173930__2017_baseline/validation_plots/validation_table.csv`.

| Category | Indicator | Actual 2017 | Model | Relative error |
|---|---:|---:|---:|---:|
| Primary energy | Biomass | 100.0 TWh | 96.8 TWh | -3.2% |
| Primary energy | Oil | 82.0 TWh | 80.9 TWh | -1.4% |
| Primary energy | Gas | 20.0 TWh | 20.0 TWh | 0.0% |
| Primary energy | Coal + peat | 35.0 TWh | 35.0 TWh | 0.0% |
| Primary energy | Nuclear | 65.0 TWh | 65.1 TWh | +0.1% |
| Primary energy | Hydro | 15.0 TWh | 14.6 TWh | -2.7% |
| Primary energy | Wind | 5.0 TWh | 4.8 TWh | -4.1% |
| Electricity | Nuclear | 21.6 TWh | 20.8 TWh | -3.6% |
| Electricity | Hydro | 14.6 TWh | 14.6 TWh | 0.0% |
| Electricity | Wind | 4.8 TWh | 4.8 TWh | -0.1% |
| Electricity | CHP (all) | 20.73 TWh | 20.49 TWh | -1.2% |
| Electricity | Condensation | 3.28 TWh | 3.29 TWh | +0.3% |
| Electricity | Gas power | 3.2 TWh | 4.37 TWh | +36.7% |
| Electricity | Imports | 20.43 TWh | 19.54 TWh | -4.4% |
| Heat | District heat production | 36.5 TWh | 52.33 TWh | +43.4% |
| Emissions | CO2 | 41.2 MtCO2 | 41.25 MtCO2 | +0.1% |

The key result is that the model reproduces the main 2017 Finnish system aggregates very closely. All major primary-energy indicators except solar fall within about ±5%, the electricity balance is well matched, and CO2 emissions are reproduced almost exactly. The strongest remaining discrepancies are district heat production and gas-fired electricity.

### Interpretation and scientific caveats

Two residual mismatches should be discussed explicitly in the paper.

First, district heat production is overestimated by 43.4%. This is not primarily a calibration failure but a structural aggregation artifact. In the current EnergyScope formulation, `share_heat_dhn` is applied to the full low-temperature heat pool, including industrial low-temperature demand. In Finnish statistics, however, the reported district-heating output mainly corresponds to residential and service-sector network heat. As documented in `Docs/finland_2017_validation_justifications.md`, the 45% district-heating share is physically consistent when applied only to residential and service heat, but it becomes too large when imposed on the aggregate low-temperature demand used by the model.

Second, gas-fired electricity remains 36.7% above the statistical reference. The same justification file shows that this residual comes from CHP co-production arithmetic rather than a simple tuning issue: under a binding gas cap, any gas routed through district-heating CHP produces electricity as an unavoidable by-product. Sensitivity tests on CHP bounds reduced model realism elsewhere without solving the problem.

These limitations do not invalidate the historical benchmark. On the contrary, the 2017 baseline shows that the calibrated Finnish model is able to reproduce the overall energy balance, electricity structure, and CO2 level of the real system with high fidelity, while making the remaining structural aggregation issues transparent.

### Validation figures to insert

Recommended main-text figures:
- `case_studies/FI/manual_runs/20260323_173930__2017_baseline/validation_plots/pe_comparison.png`
- `case_studies/FI/manual_runs/20260323_173930__2017_baseline/validation_plots/elec_comparison.png`
- `case_studies/FI/manual_runs/20260323_173930__2017_baseline/validation_plots/error_chart.png`

Sankey recommendation:
- Use `plots/validation_2017/validation_sankey.html` as the authoritative Sankey asset.
- A clean publication-quality static export is still needed from the original plotting workflow. The browser screenshots produced during this session are useful for inspection but are not yet good enough for a final paper figure.

Suggested caption language for the Sankey:

> Figure X. Sankey diagram of the calibrated Finland 2017 energy system. The figure is used as a structural consistency check rather than as a statistical validation metric: it shows that the calibrated model reproduces the main conversion chains between imported fuels, domestic biomass, electricity generation, district heating, and final energy services.

---

## Suggested Section — Finland 2035 Scenario Design

### Scenario matrix used in the paper

The forward-looking analysis is now built around a 3 x 3 scenario matrix rather than the earlier generic GHG sweep. The two scenario dimensions are:

1. Forest biomass supply scenario: `S1_BES`, `S2_NFS`, `S3_BDS`
2. GHG / nuclear configuration: `unconstrained`, `ghg_95pct`, `ghg_95pct_nonuke`

The GHG baseline is Finland 2017 `CO2_net = 41.2 MtCO2/y`, so the 95% target corresponds to a binding limit of 2.06 MtCO2/y. The `ghg_95pct_nonuke` case applies the patch `fi_nuclear_phaseout_strong_2035.csv`, which sets `NUCLEAR f_min = 0` and `f_max = 0`, i.e. a strong no-nuclear counterfactual.

The earlier 80% GHG column should be dropped from the paper. It has been superseded by the stronger and more policy-relevant `ghg_95pct_nonuke` counterfactual.

### Biomass supply-curve construction

The Finnish biomass representation follows the stepwise supply-curve logic introduced by Colla et al. for Belgium, but adapted to Finnish data and policy debates. Instead of a single homogeneous `WOOD` resource, the model uses four domestic steps plus an import backstop:

| Resource step | Interpretation | Marginal cost |
|---|---|---:|
| `WOOD_FI1` | industrial by-products (black liquor, bark, sawdust) | 11 €/MWh |
| `WOOD_FI2` | logging residues | 22 €/MWh in S1/S2, 26 €/MWh in S3 |
| `WOOD_FI3` | secondary woodchips and sawdust streams | 27 €/MWh |
| `WOOD_FI4` | direct fuelwood and landscape-care wood | 33 €/MWh |
| `WOOD_FI5` | Baltic/Nordic import backstop | 70 €/MWh |

This structure makes the biomass constraint visible as a rising marginal-cost ladder rather than an implicit single-price pool.

### Forest scenarios and their parameterisation

The three forest scenarios are derived from the Finnish forest-policy literature and then translated into EnergyScope parameters through the workflow documented in `Docs/biomass_scenario_mapping.md` and `Docs/biomass_supply_curve_fi.md`.

| Scenario | Narrative | `WOOD_FI1` | `WOOD_FI2` | `WOOD_FI3` | `WOOD_FI4` | Domestic forest wood total |
|---|---|---:|---:|---:|---:|---:|
| S1 / BES | stylised high-mobilisation bioeconomy case | 54.53 TWh | 45.86 TWh | 15.05 TWh | 6.50 TWh | 121.94 TWh |
| S2 / NFS | reference / national forest strategy baseline | 45.44 TWh | 38.21 TWh | 12.54 TWh | 5.42 TWh | 101.62 TWh |
| S3 / BDS | biodiversity-first conservative case | 32.00 TWh | 6.00 TWh | 1.50 TWh | 0.50 TWh | 40.00 TWh |

Scientific interpretation of the three cases:
- `S1_BES` is a stylised high-biomass sensitivity case, not a literal one-to-one transcription of the Blattert et al. BES simulation.
- `S2_NFS` is the neutral reference built from ENSPRESO medium potentials for 2035.
- `S3_BDS` is the conservative biodiversity case. It is not the original ENSPRESO ENS_Low 2030 value of 74.2 TWh anymore. That initial value was revised downward after a three-way audit using LUKE 2024 observed biomass use, Mönkkönen et al. ecological harvest ceilings, and competing industrial roundwood demand. The revised domestic forest-biomass ceiling is 40 TWh.

This conservative S3 revision is essential for scientific honesty. The paper should state explicitly that the original ENSPRESO low case was judged too optimistic for a genuine biodiversity-constrained Finnish forest system.

### Figure to insert

Main supply-curve figure:
- `plots/biomass_supply_curves_fi_2035.png`

Suggested caption language:

> Figure X. Stepwise Finnish wood biomass supply curves used in the 2035 scenario matrix. S1 represents a stylised high-mobilisation case, S2 the ENSPRESO medium baseline, and S3 a conservative biodiversity-constrained supply after revision with LUKE 2024 and Mönkkönen et al. (2024). The vertical markers indicate the domestic forest-biomass ceilings; the import backstop is represented by the high-cost final step.

---

## Suggested Section — Finland 2035 Results Under Forest and Emissions Scenarios

### Why the unconstrained 2035 cases are already deeply decarbonised

Across the three forest cases, the unconstrained 2035 optimum already yields `CO2_net` values between 12.6 and 13.1 MtCO2/y, corresponding to a 68–70% reduction relative to the 2017 baseline. This is not a paradox. The 2035 dataset already embeds a strong structural decarbonisation floor through coal phase-out, brownfield renewable deployment, and the rest of the Finnish 2035 technology assumptions. The policy-relevant question is therefore not whether the unconstrained 2035 system decarbonises, but how the system reaches the last part of the path from roughly 70% to 95% under different forest constraints and with or without nuclear.

### Main results table

Table Y summarises the final 3 x 3 matrix using the latest completed run for each forest x GHG case in `case_studies/FI/forest_scenarios_2035/`.

| Forest scenario | GHG case | System cost | `CO2_net` | Reduction vs 2017 | Finnish forest wood used |
|---|---|---:|---:|---:|---:|
| S1_BES | Unconstrained | 22.40 bn€/y | 13.02 MtCO2/y | 68.4% | 54.5 TWh |
| S1_BES | -95% GHG (with nuclear) | 22.92 bn€/y | 2.06 MtCO2/y | 95.0% | 74.2 TWh |
| S1_BES | -95% GHG (no nuclear) | 22.94 bn€/y | 2.06 MtCO2/y | 95.0% | 100.4 TWh |
| S2_NFS | Unconstrained | 22.46 bn€/y | 12.57 MtCO2/y | 69.5% | 45.4 TWh |
| S2_NFS | -95% GHG (with nuclear) | 23.02 bn€/y | 2.06 MtCO2/y | 95.0% | 74.2 TWh |
| S2_NFS | -95% GHG (no nuclear) | 23.12 bn€/y | 2.06 MtCO2/y | 95.0% | 96.2 TWh |
| S3_BDS | Unconstrained | 22.62 bn€/y | 13.10 MtCO2/y | 68.2% | 32.0 TWh |
| S3_BDS | -95% GHG (with nuclear) | 23.56 bn€/y | 2.06 MtCO2/y | 95.0% | 40.0 TWh |
| S3_BDS | -95% GHG (no nuclear) | 23.90 bn€/y | 2.06 MtCO2/y | 95.0% | 40.0 TWh |

Note on units:
- “System cost” is the annualised `TotalCost.csv` value.
- “Finnish forest wood used” sums `WOOD_FI1` to `WOOD_FI5` from `Resources.csv` and therefore measures use of the forest-wood ladder only, not all other biomass resources.

### Interpretation of the matrix

Three results deserve emphasis.

First, the unconstrained cases are relatively close in cost, but not identical in biomass use. S3-BDS is already more constrained than S1 and S2 even without a climate target: the unconstrained optimiser uses about 54.5 TWh of forest wood in S1, 45.4 TWh in S2, but only 32.0 TWh in S3, while total `CO2_net` remains around 13 MtCO2/y in all three cases.

Second, the -95% GHG case with nuclear does not exhaust the S1 or S2 resource ceilings, but it fully saturates S3. With nuclear available, the model uses 74.2 TWh of forest wood in both S1 and S2, which corresponds to about 61% of the S1 ceiling and 73% of the S2 ceiling. In S3-BDS, however, the model immediately hits the 40 TWh ceiling. This is the cleanest expression of the biodiversity constraint in the current results: the 95% system remains feasible in the optimisation, but only at higher cost and with no forest-biomass margin left.

Third, removing nuclear sharply increases the value of biomass in S1 and S2, but S3 cannot expand further. In the no-nuclear case, forest wood use rises from 74.2 to 100.4 TWh in S1 and from 74.2 to 96.2 TWh in S2. In S3-BDS it remains stuck at 40 TWh because the scenario ceiling is binding in both 95% cases. This is why the no-nuclear cost penalty is smallest in S1 and largest in S3: the model can replace lost nuclear electricity partly with additional forest biomass in S1 and S2, but not in S3.

The correct interpretation is therefore not that S3 makes -95% impossible in the model, but that S3 removes forest biomass as a flexible adjustment margin. Deep decarbonisation remains feasible in the optimiser because it can still rely on electrification, wind, hydro, non-forest biomass, and imported carriers. However, the biodiversity-constrained scenario becomes the most expensive configuration and uses all domestic forest wood steps already under the 95% target.

### Figures to insert

Main 2035 result figures:
- `plots/forest_scenarios_2035_energy_matrix.png`
- `plots/forest_scenarios_2035_biomass_allocation.png`

Suggested caption language for the matrix figure:

> Figure X. Finland 2035 scenario matrix across three forest-management cases and three GHG configurations. The top row shows the primary-energy mix, while the bottom row shows the use of the Finnish forest-wood supply ladder. The unconstrained cases already reach roughly a 70% reduction versus 2017. The biodiversity-constrained S3 case is distinguished by early saturation of the domestic wood ceiling, especially under the -95% target.

Suggested caption language for the biomass-allocation figure:

> Figure X. Biomass allocation by final use in Finland 2035. The figure highlights how the no-nuclear cases increase pressure on biomass in S1 and S2, whereas S3-BDS remains capped by its conservative forest-biomass ceiling and therefore relies more heavily on non-biomass adjustments elsewhere in the system.

---

## Suggested Final Section — Next Step: Disturbance Shocks and Dynamic Biomass Supply

The present paper should end by making a sharp distinction between what is already implemented and what remains a research extension.

What is already implemented in the current version:
- a calibrated 2017 Finnish baseline
- a 2035 multi-step biomass supply curve
- three forest-management narratives translated into EnergyScope parameters
- a completed 3 x 3 scenario matrix crossing forest management with GHG ambition and nuclear availability

What is not yet implemented, and should be presented strictly as future work:
- dynamic annual forest trajectories under windstorm, bark-beetle, and wildfire disturbance
- endogenous post-disturbance biomass price shocks
- quality-differentiated calamity wood flows
- constrained short-run energy-system re-optimisation after a disturbance event

### Insertion-ready future-work text

The next stage of the research is to move from static scenario shifts to disturbance-driven biomass trajectories. Following the concept note in `Docs/Coupled_Forest_Energy_Modelling_Finland_concept_note.docx`, the planned extension is to couple the Finnish forest simulator used by the Jyvaskyla/Luke team with the FLAM and PICUS disturbance modules developed in the ForestNavigator framework. The purpose of this coupling is to generate annual biomass supply curves for Finland under contrasting management regimes and climate pathways, while explicitly representing wildfire risk, bark-beetle outbreaks, windthrow, salvageable calamity wood, and the subsequent reduction in standing stock.

In EnergyScope terms, this would allow the biomass ladder to evolve over time instead of remaining fixed for a single target year. The disturbance case is not simply a lower biomass ceiling. It is expected to generate a time profile with three distinct effects: a short-lived pulse of salvage wood, a temporary price depression for low-quality biomass, and a longer-lived structural reduction in future availability after damaged stands are harvested or lost. Methodologically, the concept note proposes a pre-shock 2030 snapshot, followed by a post-shock 2035 snapshot in which supply curves are updated and the energy system cannot fully re-optimise because investment lead times and inherited infrastructure lock in part of the pre-shock fleet.

This future extension is scientifically important because it would connect biodiversity policy, forest risk, and energy-system resilience in a single framework. However, the current paper should not claim disturbance results yet. At this stage, the disturbance module is best presented as the logical continuation of the present work: the current article establishes the calibrated national baseline and the static management-scenario framework; the next article or next project phase would add dynamic disturbance shocks and price effects on top of that validated foundation.

### Practical paper-safe closing sentence

> A natural extension of the present work is to replace the static 2035 biomass ladders with annually updated supply curves derived from coupled forest-growth and disturbance models, thereby allowing windstorm, bark-beetle, and wildfire shocks to affect not only the quantity of biomass available to the energy system but also its timing, quality, and marginal cost.

---

## Asset Checklist for the Paper

Validation 2017:
- `case_studies/FI/manual_runs/20260323_173930__2017_baseline/validation_plots/pe_comparison.png`
- `case_studies/FI/manual_runs/20260323_173930__2017_baseline/validation_plots/elec_comparison.png`
- `case_studies/FI/manual_runs/20260323_173930__2017_baseline/validation_plots/error_chart.png`
- `plots/validation_2017/validation_table.csv`
- `plots/validation_2017/validation_sankey.html` (interactive supplementary asset; static export still needs cleanup)

Scenario design 2035:
- `plots/biomass_supply_curves_fi_2035.png`
- `Docs/biomass_scenario_mapping.md`
- `Docs/biomass_supply_curve_fi.md`

Scenario results 2035:
- `plots/forest_scenarios_2035_energy_matrix.png`
- `plots/forest_scenarios_2035_biomass_allocation.png`
- `case_studies/FI/forest_scenarios_2035/` latest run directories for S1, S2, S3 under the three retained GHG cases

Future work:
- `Docs/Coupled_Forest_Energy_Modelling_Finland_concept_note.docx`
