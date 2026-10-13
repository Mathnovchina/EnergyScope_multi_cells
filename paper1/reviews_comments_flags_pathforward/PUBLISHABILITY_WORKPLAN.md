# Paper 1 publishability workplan

**Target journal:** *Energy*  
**Prepared:** 2026-10-13  
**Purpose:** operational checklist for turning the current Finland forest-biomass study
into a defensible submission while waiting for the black-liquor expert response and before
launching the replacement run matrix.

This file is the action-oriented companion to [FLAGS.md](./FLAGS.md), which remains the
single source of truth for issue status and evidence. Paste-ready manuscript text remains
in [SNIPPETS_overleaf.md](./SNIPPETS_overleaf.md). Do not edit completed runs or interpret
the old nine-run matrix as if it used the corrected 2035 pools and new FI5/FI6 import tiers.

## 1. Current position

### Completed foundations

- [x] Frozen and indexed the original nine-run Paper 1 matrix and 2017 validation run.
- [x] Reconstructed the inherited Thiran biomass categories and source mapping.
- [x] Corrected the four retained non-wood biomass pools from 2050 to 2035 inputs.
- [x] Separated agricultural `BIOMASS_RESIDUES` from the forest ladder.
- [x] Retained legacy `WASTE` while documenting its unverified partition from `BIOWASTE`.
- [x] Audited ENSPRESO, S2BIOM, VTT, RED II, EUwood and Biomass Futures evidence.
- [x] Implemented finite Baltic/Nordic `WOOD_FI5` and unlimited stress `WOOD_FI6` in
  future-run inputs, with backups and a reproducible calculation.
- [x] Recorded David An's review as traceable flags P-0--P-14.
- [x] Prepared initial Overleaf snippets for known corrections and caveats.

### Current blocker

- [ ] **T18 / S2B-1 / W-4: decide the physical treatment of black liquor and therefore
  the identity of FI1.** Do not finalise the domestic wood ladder or launch the replacement
  matrix until this decision is made and documented.

### Work that can proceed now

Everything in Sections 3--6 below is useful before the expert replies and does not require
new optimisation runs. Most tasks are manuscript, evidence, accounting or submission work.

## 2. Critical path

1. **Now:** close evidence, methods, calibration, citation and presentation tasks that do
   not depend on the new results.
2. **Now:** make the remaining modelling decisions that are independent of black liquor.
3. **When the expert replies:** choose and implement one black-liquor/FI1 design.
4. **Before running:** freeze and validate one complete, internally consistent input set.
5. **Run:** execute a new timestamped core matrix, then only approved sensitivities.
6. **After running:** audit accounting, regenerate tables/figures and freeze a new evidence set.
7. **Last:** rewrite Results, Discussion, Abstract and Conclusion from the new outputs.
8. **Submission gate:** complete journal, reproducibility and reporting checks.

---

## 3. Priority A — do now while waiting for the expert

These are required for a publishable paper and should be completed before spending effort
on new results prose.

### A1. Freeze the manuscript baseline and working conventions

- [ ] Save the current Overleaf PDF and source snapshot with a date/version label.
- [ ] Record which PDF David An reviewed and retain it separately from the evolving draft.
- [ ] Confirm that `main_certosa.tex` is the only active manuscript source.
- [ ] Keep all agent-proposed LaTeX in [SNIPPETS_overleaf.md](./SNIPPETS_overleaf.md);
  paste and edit it manually in Overleaf.
- [ ] Create one manuscript change log: date, section, flag, action, source and status.
- [ ] Do not update results numbers until the replacement matrix has passed the post-run audit.

**Done when:** every future manuscript edit can be linked to a flag and a dated source version.

### A2. Restructure the Methods section

Addresses **P-1, P-2, P-3, P-7, P-9, E6**.

- [ ] Adopt the agreed three-part structure:
  1. Finnish stylised facts and time-series inputs;
  2. model formulation;
  3. data, calibration and scenario construction.
- [ ] Decide for each current Figure 1--4 whether it belongs in stylised facts, an appendix
  or the supplement.
- [ ] Move the two Colla literature paragraphs from the model section to the literature review.
- [ ] Add an explicit statement that the Finland application uses single-cell ESMC, which
  reduces to the EnergyScope TD formulation.
- [ ] Add an “inherited / adapted / new in this study” table:
  - inherited: EnergyScope/ESMC optimisation structure, technologies and typical days;
  - adapted: Finland data, 2017 calibration and 2035 assumptions;
  - new: forest-scenario ladder, import split and scenario comparison.
- [ ] Add the resource-to-service chain: resource → common layer → conversion technology →
  end-use demand.
- [ ] Add the missing layer-balance, capacity and storage equations.
- [ ] State the optimisation decision variables.
- [ ] Define the investment, maintenance and operating-cost functions.
- [ ] Define the annualisation factor, 1.5% discount rate and technology lifetimes.
- [ ] Build a symbol table and define every symbol at first use.
- [ ] Define `Loss(Elec,t)` and `Loss(HeatLowTDhn,t)` with values and sources.
- [ ] Check that every displayed equation is referenced and explained in the text.
- [ ] Add page-level citations for equations or formulations taken from Moret and Thiran.

**Done when:** a reader can follow inputs to end-use demand and reproduce the objective
without guessing which elements are inherited or new.

### A3. Document the 2035 demand construction

Addresses **P-4, C6, C9**.

- [ ] Trace every 2035 demand series from source → transformation → `Demands.csv`.
- [ ] State whether each demand is held constant, interpolated, projected or externally imposed.
- [ ] Distinguish annual demand levels from structural shares based on 2019--2020 data.
- [ ] Explain why those shares are also used in the 2017 validation.
- [ ] Add the fixed-demand assumption to the limitations.
- [ ] Decide whether high/low demand sensitivity runs are required:
  - **minimum option:** documentation and limitation only;
  - **stronger option:** selected high/low 2035 demand sensitivities after the core matrix.
- [ ] If sensitivities are wanted, define their source, percentage or trajectory before running;
  do not choose an arbitrary range after seeing results.

**Done when:** another researcher can reconstruct the 2035 end-use demand vector and understands
what is exogenous.

### A4. Complete the calibration audit

Addresses **P-13, B.1, A5, E5, C3, C4**.

- [ ] Recompute the 1.2% weighted score directly from the canonical 2017 outputs.
- [ ] List the 14 scored indicators and their weights.
- [ ] Separately list the three weight-zero informational indicators.
- [ ] Explain that district heat and gas-fired electricity are large residuals excluded from
  the headline weighted score.
- [ ] List every calibrated parameter, original value, final value, unit and source.
- [ ] Separate fixed historical observations, calibrated parameters and model decisions.
- [ ] Reconcile:
  - CHP electricity: 20.73 versus 25.0 TWh;
  - electricity imports: 20.43 versus approximately 20.3 TWh;
  - gas power: 4.34/4.37/4.38 TWh;
  - district heat: 52.33 versus 52.96 TWh.
- [ ] Explain the district-heat aggregation artefact.
- [ ] Explain the gas-CHP co-production residual.
- [ ] State that peat is represented through `COAL`.
- [ ] State that `relax_co2=true` applies only to historical reproduction.
- [ ] Rewrite the validation claim so that “1.2%” is never reported without its scoring boundary.

**Done when:** the validation section is transparent about what was fitted, what was scored and
what remains structurally mismatched.

### A5. Finish the supply-curve evidence table

Addresses **T2, T4, T5, T11, S2B-3, S2B-4, S2B-6, W-6, S-PY**.

- [ ] Build one table for every biomass step with:
  - physical definition;
  - source code/category;
  - availability and year;
  - conversion factor and moisture/volume basis;
  - source cost and price year;
  - additions for transport, handling, stumpage or overhead;
  - final model cost and price year;
  - GHG factor and RED II pathway;
  - scenario dependence;
  - evidence class: observation, database estimate or author assumption.
- [ ] Show ENSPRESO and S2BIOM costs as benchmarks, not as if both were delivered plant-gate prices.
- [ ] State that S2BIOM roadside costs omit stumpage, profit, overhead and plant transport.
- [ ] Resolve the common monetary convention for the whole ladder. The import tiers are already
  EUR2015; the remaining domestic and inherited categories still mix source years.
- [ ] Choose matched LHV/moisture/solid-volume conventions for any quantity requiring conversion.
- [ ] Do not apply one universal m³-to-MWh factor across unmatched assortments.
- [ ] Decide whether the S1 upper bound remains the stylised +20% case or is benchmarked/replaced
  using S2BIOM HIGH.
- [ ] Decide whether the S3 40 TWh ceiling remains the Paper 1 conservation case.
- [ ] If retained, disclose that S3 is a hand-revised scenario, not raw ENSPRESO.
- [ ] Explain that S3 uses 2030 ENS_Low evidence while S1/S2 interpolate to 2035.
- [ ] Explain that the Blattert labels and ENSPRESO storylines are different scenario families.
- [ ] Document the residue fraction and collection-efficiency assumptions behind S3.
- [ ] Add the exact Mönkkönen denominator: maximum economically sustainable harvest in southern
  Finland, not mean annual increment.

**Done when:** every availability and cost can be traced to a source plus an explicit transformation,
and every judgement is labelled as such.

### A6. Correct biomass, waste and GHG documentation

Addresses **T6, T7, T15, T16, S-RED, W-5**.

- [ ] Correct all stale tables to the retained 2035 non-wood values.
- [ ] Ensure `BIOMASS_RESIDUES` is 4.985 TWh in future-run inputs and is described as agricultural
  waste, not forest residue.
- [ ] Remove stale 6.6/5.0/3.4 TWh scenario-specific residue claims unless a new scenario design
  is explicitly approved.
- [ ] Add Thiran Table 1.11 pinpoint citation: printed p. 60.
- [ ] Add the inherited biomass mapping based on Thiran Table 1.14, printed pp. 66--67.
- [ ] Add the legacy `WASTE`/`BIOWASTE` boundary disclosure.
- [ ] Correct every “RED II case 7a” label; that case does not exist.
- [ ] Distinguish FI5's deliberately conservative 40 tCO2e/GWh from Colla's lower neighbouring
  good-quality value.
- [ ] State that FI6's 40 tCO2e/GWh corresponds to Colla's good-quality RoW-II pathway.
- [ ] State explicitly whether reported “wood-layer use” includes `ENERGY_CROPS_2`.
- [ ] Keep canonical old-run values clearly separated from future-run input values.

**Done when:** the paper and supplement contain no stale biomass number or incorrect RED II label.

### A7. Verify literature claims and citations

Addresses **B.3, A1, E1, E3, E4, P-5, P-6, P-10**.

- [ ] Verify each quantitative literature claim against the original source:
  - Finnish forest cover and wood share of primary energy;
  - Mönkkönen harvest denominator and geographical scope;
  - EU biodiversity-scenario reduction and leakage;
  - Czech disturbance/salvage figures;
  - Beringer global biomass range;
  - Colla Belgian and EU potentials;
  - Rečka system-cost effect.
- [ ] Record page/table numbers for every long report or thesis.
- [ ] Add page locators to all Moret and Thiran thesis citations.
- [ ] Replace undefined `moret_strategic_2017` with the valid bibliography key.
- [ ] Resolve the two `moretCharacterizationInputUncertainties2017` entries.
- [ ] Decide whether the two Luke keys refer to distinct products or are duplicates.
- [ ] Use `\citet` rather than possessive `\cite{...}'s`.
- [ ] Check that the published *Energy Economics* version is used instead of the SSRN preprint
  for the stock-flow-consistent coupling article.
- [ ] Add the new EnergyScope multi-cell precedent to the literature positioning where relevant.
- [ ] Recompile references from scratch and verify alphabetical ordering.
- [ ] Add the exact Luke wood-consumption table or publication record to Zotero if still missing.

**Done when:** every quantitative claim and thesis citation has a verified locator and no duplicate
or undefined bibliography key remains.

### A8. Prepare the figures and tables without regenerating results yet

- [ ] Make a figure inventory: main text, appendix, supplement and obsolete.
- [ ] Define final figure dimensions, fonts, colour palette and file formats for *Energy*.
- [ ] Decide which stylised-facts figures move to the appendix.
- [ ] Prepare scripts—not manual edits—for every retained plot.
- [ ] Prepare a clean static export workflow for the 2017 Sankey.
- [ ] Shorten the biomass-ladder caption and move methodological detail into a `Note:`.
- [ ] Prepare table templates whose values will be populated only after the new runs:
  - scenario definition;
  - supply ladder;
  - 2017 validation;
  - core 2035 results;
  - biomass allocation;
  - robustness/sensitivity.
- [ ] Include units, scenario names and definitions in every caption.
- [ ] Ensure S1/S3 stylisation and the no-sink boundary appear in relevant captions.

**Done when:** rerunning the post-processing scripts can regenerate all final figures and tables
without manual number entry.

### A9. Prepare the supplement

- [ ] Model sets, variables, equations and complete symbol table.
- [ ] Technology and resource parameter tables with source years.
- [ ] Thiran inherited biomass-category mapping.
- [ ] Full supply-curve provenance and transformations.
- [ ] 2017 calibration targets, weights, parameter changes and residuals.
- [ ] Complete scenario and patch table.
- [ ] Additional allocation and sensitivity results.
- [ ] Waste-boundary note.
- [ ] Reproducibility commands and software/solver versions.
- [ ] Explicit list of assumptions that are author judgements.

**Done when:** the main article can stay focused while all information needed to reproduce the
study remains available.

---

## 4. Priority B — decisions to make before the expert reply if possible

Record each decision and rationale in [FLAGS.md](./FLAGS.md).

- [ ] **S1 bound:** retain +20%, use S2BIOM HIGH as a benchmark only, or redesign S1.
- [ ] **S3 bound:** retain 40 TWh or redesign after new forest evidence.
- [ ] **Price year:** adopt and document a common model monetary basis.
- [ ] **Material use (W-1):** disclosure only or an explicit consistency sensitivity.
- [ ] **Fixed industrial demand (W-2):** disclosure, scaling sensitivity or structural change.
- [ ] **Non-energy demand (W-3):** disclose the 28.7 TWh wood demand or add an HVC/NED sensitivity.
- [ ] **Demand uncertainty (P-4):** documentation only or high/low demand runs.
- [ ] **Discount rate:** disclose 1.5% only or include a sensitivity.
- [ ] **FI5 GHG:** retain the approved conservative 40 tCO2e/GWh in the core case; optionally
  test the neighbouring-country factor as a sensitivity.
- [ ] **Robustness budget:** choose the smallest scientifically useful sensitivity set before
  seeing the replacement results.

### Minimum defensible option

Keep the nine-run core matrix, disclose fixed demand/material use, and add only one or two
sensitivities that directly test the most load-bearing remaining assumptions.

### Stronger option

Add pre-specified demand, non-energy/material-use and biomass-cost/availability sensitivities.
This is stronger but expands the run and interpretation burden. Do not add sensitivities merely
to create more results.

---

## 5. Priority C — process the black-liquor expert response

### C1. Preserve and qualify the evidence

- [ ] Save the expert's exact answer, date, affiliation and context.
- [ ] Ask permission before quoting or naming the expert in the paper.
- [ ] Separate the expert's factual description from the modelling recommendation.
- [ ] Compare the response against S2BIOM, VTT, Statistics Finland and the current model pathways.
- [ ] Record any disagreement rather than smoothing it over.

### C2. Choose one FI1/black-liquor architecture

Evaluate the following options explicitly:

1. **Separate captive black liquor:** availability tied to pulp throughput, scenario-invariant
   when pulp output is fixed, restricted to recovery/industrial CHP.
2. **Literal FI1 stemwood:** describe `MINBIOWOOa` as stemwood chips/pellets and add black liquor
   separately or exclude it from the explicit ladder.
3. **Transparent aggregate proxy:** retain FI1 as an acknowledged proxy, with strong limitations
   and no claim that ENSPRESO supplies black-liquor data.

For the selected option, define:

- [ ] physical resource identity;
- [ ] availability source, year and conversion;
- [ ] relation to pulp production and forest scenario;
- [ ] mill-gate or opportunity cost;
- [ ] GHG factor;
- [ ] allowed conversion technologies/end uses;
- [ ] double-counting control with primary wood and industrial residues;
- [ ] scenario response under S1/S2/S3;
- [ ] manuscript wording and limitations.

### C3. Implement only after explicit approval

- [ ] Back up every affected model/data file.
- [ ] Add new resources/layers or technology restrictions consistently across all data surfaces.
- [ ] Update plotting, post-processing and traceability scripts.
- [ ] Update the source register, ladder methodology and flags.
- [ ] Run structural checks before optimisation.
- [ ] Do not edit any completed run.

**Gate C:** no replacement matrix until the black-liquor design and all dependent domestic ladder
parameters are frozen.

---

## 6. Priority D — pre-run readiness gate

### D1. Freeze inputs

- [ ] All FI1--FI6 definitions, availabilities, costs and GHG factors approved.
- [ ] Corrected 2035 non-wood pools present in all scenario tables.
- [ ] S1/S2/S3 definitions consistent across baseline files and patches.
- [ ] Nuclear phase-out patch unchanged or explicitly reapproved.
- [ ] GHG constraint boundary verified and documented.
- [ ] 2035 demand construction documented and frozen.
- [ ] Typical-day files and `--read-td` choice verified.
- [ ] No old output directory will be overwritten.

### D2. Freeze the run plan

Core matrix:

- [ ] S1 × unconstrained.
- [ ] S1 × 95% GHG.
- [ ] S1 × 95% GHG, no nuclear.
- [ ] S2 × unconstrained.
- [ ] S2 × 95% GHG.
- [ ] S2 × 95% GHG, no nuclear.
- [ ] S3 × unconstrained.
- [ ] S3 × 95% GHG.
- [ ] S3 × 95% GHG, no nuclear.

For every approved sensitivity, specify before running:

- [ ] research question;
- [ ] exact parameter change and source;
- [ ] cases to run;
- [ ] expected diagnostic;
- [ ] output directory naming;
- [ ] rule for interpreting a null or contradictory result.

### D3. Reproducibility preflight

- [ ] Create a new branch/commit for the final input version.
- [ ] Record model version, git commit and data hashes.
- [ ] Run all input and traceability checks.
- [ ] Run one timestamped smoke case.
- [ ] Verify resource registration, feasibility, solver status and objective scale.
- [ ] Verify FI5 and FI6 are available with the intended cost/GHG values.
- [ ] Verify black liquor follows the selected physical restriction.
- [ ] Confirm 2017 evidence remains untouched.
- [ ] Archive the exact commands in a machine-readable manifest.

**Gate D:** proceed only when the smoke run is clean and the input snapshot is recoverable.

---

## 7. Priority E — replacement runs and post-processing

### E1. Execute the matrix

- [ ] Use new timestamped directories.
- [ ] Preserve logs, solver version, solve status, objective and runtime.
- [ ] Stop and diagnose any infeasible, non-optimal or materially anomalous case.
- [ ] Never substitute a failed run with a success-shaped fallback.
- [ ] Run approved sensitivities only after the core matrix passes.

### E2. Audit every run before using it

- [ ] Optimal/acceptable solver status.
- [ ] Correct patches and input hashes.
- [ ] Correct GHG limit and nuclear setting.
- [ ] Energy balances close.
- [ ] Resource use does not exceed availability.
- [ ] S1/S2/S3 ceilings behave as intended.
- [ ] FI5/FI6 use is plausible and separately reported.
- [ ] Black-liquor use respects the selected boundary.
- [ ] Wood-layer totals distinguish energy crops and wood imports.
- [ ] Cost and GHG decompositions reconcile with totals.
- [ ] No unexpected carry-over of `relax_co2`.

### E3. Compare old and new evidence

- [ ] Produce a machine-readable old-versus-new table.
- [ ] Attribute changes separately to:
  - 2035 non-wood corrections;
  - import-tier redesign;
  - black-liquor/FI1 redesign;
  - any domestic cost/availability changes;
  - any demand or material-use sensitivity.
- [ ] Identify whether headline conclusions change.
- [ ] Report contradictory outcomes rather than preserving the old narrative.
- [ ] Decide whether the original nine runs remain a historical robustness comparison or are
  simply superseded.

### E4. Regenerate persistent artefacts

- [ ] Copy audited result tables into a new versioned `paper1/results` snapshot.
- [ ] Regenerate all figures from scripts.
- [ ] Regenerate all manuscript tables from data.
- [ ] Update the run index and manifests.
- [ ] Update [REPRODUCIBILITY.md](../../REPRODUCIBILITY.md).
- [ ] Create a new release/tag only after all checks pass.
- [ ] Archive run directories externally because `case_studies/` is gitignored.
- [ ] Retain the old Paper 1 freeze and tag unchanged.

---

## 8. Priority F — rewrite the paper from the audited replacement results

### F1. Results

- [ ] Replace every old matrix value, allocation and capacity total.
- [ ] Report absolute effects and differences, not only signs or rankings.
- [ ] Explain which constraints bind in each scenario.
- [ ] Explain the mechanism linking forest availability, nuclear availability and system cost.
- [ ] Separate domestic wood, imports, energy crops and other biomass.
- [ ] State whether FI5 or FI6 is used and for which end uses.
- [ ] Decompose the 2017-to-2035 primary-energy change.
- [ ] Remove duplicated biomass-allocation prose.
- [ ] Avoid causal language unsupported by the model design.

### F2. Discussion

- [ ] Lead with the contribution: constraint interaction and allocation mechanisms under
  transparent biomass supply assumptions.
- [ ] Compare results with Finnish and European literature using verified quantities.
- [ ] Discuss why the results differ from Colla and other EnergyScope studies.
- [ ] Discuss the role of fixed demand and non-energy wood use.
- [ ] Discuss dependence on S1/S3 judgements and FI1 treatment.
- [ ] State clearly that the model excludes the forest carbon sink, LULUCF and harvested-wood products.
- [ ] Do not present energy-system GHG differences as full climate impacts.
- [ ] Separate Paper 1 findings from the planned G4M/disturbance/sink extension.

### F3. Limitations

At minimum include:

- [ ] no forest sink/LULUCF/HWP;
- [ ] carbon-neutral biogenic combustion convention;
- [ ] static exogenous biomass ladder;
- [ ] fixed exogenous end-use demand;
- [ ] fixed material-use/industrial-demand treatment;
- [ ] single Finnish node;
- [ ] typical-day and linear-programming abstraction;
- [ ] stylised S1 and S3 boundaries;
- [ ] mixed evidence vintages and remaining price uncertainty;
- [ ] legacy waste boundary;
- [ ] any expert-dependent black-liquor approximation.

### F4. Abstract and conclusion — do last

- [ ] One clear research question and contribution.
- [ ] Correct model identity and Finland/2035 scope.
- [ ] Quantified central effects from the final runs.
- [ ] Mechanism, not only scenario ranking.
- [ ] No claim that the forest sink is represented.
- [ ] No stale “results under production” language.
- [ ] Conclusion answers the research question without introducing new evidence.

---

## 9. Priority G — final publication and submission package

### G1. Internal reviewer test

Read once as a sceptical *Energy* reviewer and answer:

- [ ] What is new relative to EnergyScope TD/ESMC and Colla?
- [ ] Why Finland, 2035 and these three forest scenarios?
- [ ] Can every ladder step be traced and justified?
- [ ] Are assumptions separated from observations?
- [ ] Is the calibration credible despite using the reference year?
- [ ] Can the equations be followed without consulting the code?
- [ ] Are the headline conclusions robust to the most important assumptions?
- [ ] Are forest-climate claims bounded by the missing sink?
- [ ] Can all reported numbers be reproduced?
- [ ] Would changing FI1 or fixed demand overturn the main contribution?

### G2. Journal requirements

- [ ] Re-check the current *Energy* Guide for Authors immediately before submission.
- [ ] Confirm article type, word limit, abstract length and keyword limit.
- [ ] Confirm figure resolution, accepted formats and colour requirements.
- [ ] Confirm reference style and whether numbered highlights are required.
- [ ] Prepare highlights and graphical abstract if required.
- [ ] Prepare CRediT author-contribution statement.
- [ ] Prepare funding, conflicts-of-interest and acknowledgements statements.
- [ ] Prepare data/code availability statement consistent with what can actually be shared.
- [ ] Check licences before redistributing ENSPRESO, S2BIOM or other source files.
- [ ] Prepare supplementary material as a separate reproducible file.
- [ ] Prepare a concise cover letter stating contribution, journal fit and main result.
- [ ] Obtain co-author approval of the final manuscript and declarations.

### G3. Final technical checks

- [ ] Fresh compile with no warnings affecting references, figures or equations.
- [ ] All citations resolve; references are alphabetical and deduplicated.
- [ ] Tables and figures are cited in order.
- [ ] Units and significant figures are consistent.
- [ ] CO₂ notation is consistent.
- [ ] Scenario names are consistent everywhere.
- [ ] All old 2050, 80%-GHG, old FI5 and superseded S3 language is removed where inappropriate.
- [ ] No tracked secret, local absolute path or temporary artefact is included.
- [ ] Repository status and final diff reviewed.
- [ ] Final code/data commit and immutable tag created.
- [ ] Run archive copied to durable external storage.

---

## 10. Minimum publication package versus optional extensions

### Required for Paper 1 submission

- Black-liquor/FI1 decision and internally consistent ladder.
- New audited nine-run matrix using all corrected inputs.
- Transparent calibration subsection.
- Complete model equations and attribution of inherited/new elements.
- Reconciled numbers, citations and scenario definitions.
- Supply-curve provenance and common price-year explanation.
- Explicit no-sink, fixed-demand, material-use and single-node limitations.
- Reproducible result tables, figures, manifests and archived runs.
- Clean *Energy* submission package.

### Recommended robustness, subject to an explicit run budget

- One black-liquor/FI1 alternative.
- High/low 2035 demand.
- NED/HVC or material-use sensitivity.
- FI5 neighbouring-country GHG sensitivity.
- Biomass cost/availability or discount-rate sensitivity.

### Keep for Paper 2 / future work unless essential to a reviewer response

- Dynamic G4M coupling.
- Endogenous forest carbon sink/LULUCF budget.
- Disturbance-shock dynamics.
- NUTS3/multi-cell Finland.
- Endogenous material-production and forest-industry feedbacks.
- Full stock-flow-consistent land-energy coupling.

These extensions would strengthen the research programme but are not prerequisites for a
transparent, bounded and publishable Paper 1.

## 11. Immediate next actions

While waiting for the expert, the most efficient order is:

1. [ ] Document the 2035 demand construction.
2. [ ] Complete the calibration audit and reconcile the 2017 numbers.
3. [ ] Draft the inherited/adapted/new table and Methods section skeleton.
4. [ ] Build the complete biomass cost/source/price-year table.
5. [ ] Correct RED II labels, stale biomass tables and waste documentation.
6. [ ] Verify literature numbers and thesis page citations.
7. [ ] Decide the S1/S3 bounds and minimum sensitivity budget.
8. [ ] Prepare figure/table scripts and supplement structure.
9. [ ] Process the black-liquor answer using Section 5.
10. [ ] Pass the pre-run gate before launching any replacement run.

