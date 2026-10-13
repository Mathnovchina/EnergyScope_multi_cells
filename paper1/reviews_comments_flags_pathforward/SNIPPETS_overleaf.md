# Overleaf snippet tracker for `main_V1.tex`

**Target file:** [`main_V1.tex`](../Overleaf_working_paper/main_V1.tex) · **Title:** *From Bioeconomy Promise to Biodiversity Ceiling: The Role of Forest Biomass in Finnish Decarbonisation*. The author owns the `.tex`; snippets are suggestions only and are not pasted by the agent. `main_V0.tex` is the previous version. Issues, evidence and current status are in [FLAGS.md](./FLAGS.md).

**Snippet style:** avoid emphasis, paragraph-heading and typewriter-formatting commands. Use ordinary prose and paragraph flow, and keep identifiers in plain text or escaped LaTeX text.

------------------------------------------------------------------------

## D. Snippets and status

> Keys used below (`blattertSectoralPoliciesCause2022`, `monkkonenEcologicallyEconomicallySustainable2024`, `reckaRoleBiomassDecarbonisation2023`, `collaOptimalUseLignocellulosic2022`, `moretStrategicEnergyPlanning2017`) are all **present** in `references.bib`.

**D1 — Applied in V1 (A1).** The `enduses_flow` caption now uses the defined key. The original replacement is retained for audit:

``` latex
Adapted from \citet{moret_strategic_2017}.
```

with:

``` latex
Adapted from \citet{moretStrategicEnergyPlanning2017}.
```

**D2 — Partly applied in V1 (A2).** The corrected comparison below appears in the scenario-matrix discussion, but a later paragraph still says the penalty is nearly three times larger in S3 than S1. That second occurrence needs the same correction; see [FLAGS.md](./FLAGS.md).

``` latex
By contrast, S3 cannot expand further because its 40~TWh domestic ceiling is already
binding, making the nuclear phase-out markedly more costly (+0.34~bn~EUR/y, versus
+0.02 and +0.10~bn~EUR/y in S1 and S2). The sensitivity of system cost to nuclear
availability is therefore about three times larger than in S2 and an order of
magnitude larger than in S1: S3 does not make deep decarbonisation infeasible, but it
removes forest biomass as a flexible adjustment margin and becomes the highest-cost
configuration.
```

**D3 — Applied in V1 (C1, C2).** The emissions-boundary caveat is present in V1. If you want to remove its paragraph-style heading, the following heading-free version is available:

``` latex
A central boundary of the present model must be stated explicitly. The greenhouse-gas
constraint accounts for energy-system emissions only: resource supply-chain GHG
(RED~II Annex~VI) plus technology construction impacts (Eq.~\ref{eq:gwp_total}). Biogenic
combustion CO$_2$ is treated as carbon-neutral \footnote{A strong assumption because the carbon neutrality of forest biomass for bioenergy remains contested, with growing literature challenging the assumption that biomass combustion yields net-zero emissions. \cite{selivanovCarbonNeutralityForest2023,ahamerWhyBiomassFuels2022,ahamerHowComputeWhether2024,feiwuStrategicUsesAncillary2023,boothNotCarbonNeutral2018} dissect this issue, exposing the complexities in biomass carbon accounting.}, and the model contains no
representation of the forest carbon sink, land-use (LULUCF) flux, or harvested-wood-product
carbon. Consequently, the climate difference between intensive (S1) and conservation (S3)
harvesting is seen by the optimiser only through supply-chain GHG and cost, not through the
standing-stock and sink dynamics that dominate the real land--energy carbon balance
\citep{reckaRoleBiomassDecarbonisation2023}. This is deliberate for a first, energy-system
step, and it is precisely the gap that will be analysed in future research.
```

**D4 — Revised evidence-based 2017 benchmark wording (C3, C4).** Suggested placement: the 2017 validation discussion. This describes the run as a constrained cost optimisation and makes clear why the coal-plus-peat match is not independent evidence:

``` latex
The 2017 benchmark is a least-cost optimisation subject to observed end-use demands,
resource-availability limits and technology-capacity constraints, rather than a direct
replay with every observed output fixed. In line with the historical system demonstration
in \citet[Section~3.1]{limpensEnergyScopeTDNovel2019}, it is interpreted as a constrained
reproduction of a past system, not as predictive validation of a future pathway. Finnish
peat is not represented as a separate resource: the model uses one COAL resource, and the
comparison target combines coal and peat. The 35~TWh COAL availability cap therefore
imposes the aggregate coal-plus-peat total; its exact match is not an independent model
prediction and does not validate separate coal and peat use. The 2017 run also relaxes the
CO$_2$ cap to avoid a forced-CCS artefact. This removes that emissions constraint only;
the run remains a cost optimisation subject to its other constraints. The relaxation is
not applied to the 2035 scenarios.
```

**D5 — Cost/discount-rate assumptions (C5).** Add after the objective-function equation:

``` latex
Investments are annualised with a discount rate of 1.5\% and technology-specific lifetimes \citep{DanishEnergyAgency2022}, consistent with the EnergyScope Multi-Cells original setting \citep{thiranExploringOptionsFossilfree2025}.
```

**D6 — 2035 demand / base-year clarification (C6, C9).** The source and disaggregation method can be stated as follows, based on Thiran's demand-method section and the Finland input provenance:

``` latex
The annual 2035 end-use demand levels are projected rather than carried forward unchanged
from 2017. Following the EnergyScope Multi-Cells demand framework described by
\citet[Section~1.2.2, pp.~51--53]{thiranExploringOptionsFossilfree2025}, the EU Reference
Scenario 2020 supplies the demand and activity trajectories, which are disaggregated into
model end uses using sector-specific sources: EUCalc for residential and tertiary demand,
2015 Heat Roadmap Europe shares for industrial end uses, and EU Reference Scenario activity
data for passenger mobility, freight and shipping. Non-energy demand follows the adapted
Rixhon method, using Eurostat energy balances, Prodcom, UNFCCC and WITS data and EU Reference
Scenario growth. In the Finland inputs, JRC-IDEES provides the 2015 sectoral electricity and
heat base data. These annual 2035 levels are held fixed across the forest and GHG scenarios;
the separate 2017 profiles describe temporal shapes, not annual 2035 demand levels.
The structural split parameters in Table~\ref{tab:fin_eud_params_2020} are calibrated from
Finnish statistics and reused across the 2017 and 2035 cases.
```

**D7 — Deferred at the author's request.** No subsection or paste-ready text for this item for now. Revisit after deciding where the paper should consolidate limitations and how to handle the 2017 weather/typical-day basis and the absence of climate-adjusted weather and capacity factors.

**D8 — On hold: explain the validation score before deciding whether to report it.** The 1.2% is the v37 run's weighted mean absolute percentage error across 14 scored targets, not a claim that every indicator is within 1.2% or that the fit is independent validation. Three additional dashboard metrics have zero weight. Some scored targets are materially shaped by imposed resource/capacity bounds, so any headline claim needs this qualification. A footnote is a better candidate than the abstract if you later choose to report the score. A possible footnote is:

``` latex
\footnote{The reported 1.2\% score is the weighted mean of the absolute percentage errors
against 14 calibration targets; three additional dashboard indicators are assigned zero
weight. It summarises calibration fit, not independent predictive validation: some target
values are partly imposed through resource-availability or technology-capacity constraints,
including the 35~TWh coal-plus-peat aggregate.}
```

The formula is implemented in `scripts/run_calib_manual.py` and the v37 count/score are
recorded in `Docs/finland_2017_validation_justifications.md`. Keep this item pending until
you decide whether and where to report the score.

**D9 — Not paste-ready: S3/BDS scaling chain needs qualification.** The proposed chain is not established by the cited sources as written. It transfers a southern-Finland harvest ratio to a national harvest figure, and the 15--20\% residue fraction and 30--40\% collection share remain assumptions. The stated central calculation gives 3.9--5.1~TWh; a separate full-grid audit puts 6~TWh at the upper edge of the assumed range when using 1.5~MWh/m$^3$ (about 5.9~TWh before rounding), and within the grid under a different 1.96~MWh/m$^3$ conversion. Those conversions are not interchangeable without matching moisture and volume bases. Thus 6~TWh may be retained as an explicit high-end scenario assumption, but it should not be presented as a direct consequence of the Mönkkönen ratio. Reconcile the conversion basis and label the assumptions before drafting.

------------------------------------------------------------------------

## G. Supply-curve audit (T1–T14) — snippets on hold

All G snippets are held pending the author's black-liquor decision and the S2BIOM/FI1 boundary decision. The earlier decision in [FLAGS.md](./FLAGS.md) records the previous proxy choice; it is not an instruction to paste these snippets now. No source data, inputs, runs or author-owned `.tex` files are changed by this tracker update. Evidence: [forest_supply_curve_methodology_traceability.md](../../Docs/forest_supply_curve_methodology_traceability.md).

**G1 — FI1 description** (Table `tab:fi_biomass_ladder`; the existing "black liquor, bark, sawdust" wording is retained, so you may only need the footnote G2).

``` latex
WOOD\_FI1 & Aggregate industrial wood by-products: black liquor, bark and sawdust (volume from ENSPRESO MINBIOWOOa)\footnotemark & 11 & 10 \\
```

**G2 — FI1 footnote (the key addition: the ENSPRESO-label caveat and the black-liquor rationale).**

``` latex
\footnotetext{Black liquor, bark and sawdust are the cheapest, largely captive wood-energy streams in Finland; black liquor alone reached 43~TWh in 2017, the single largest domestic wood-energy source \citep{statfin12vq}. Black liquor is not represented in the ENSPRESO database, so we take the volume of the cheapest ENSPRESO wood commodity, MINBIOWOOa (45~TWh, which ENSPRESO formally labels as stemwood chips and pellets \citep{ruizJRCEUTIMESModelBioenergy2015}), as a proxy for this by-product stream. The assigned cost (11~\euro/MWh) and embedded GHG (10~tCO$_2$eq/GWh) reflect captive mill-gate by-products; replacing this proxy with a physically grounded black-liquor/by-product split is left to forthcoming work coupling G4M and industrial-throughput data.}
```

*Check before pasting:* `\euro` availability; and that `\footnotemark`/`\footnotetext` sit correctly inside the table (or convert to a normal `\footnote` placed just after the table).

**G3 — bib entries** (add both to Zotero/`references.bib`).

``` bibtex
@techreport{ruizJRCEUTIMESModelBioenergy2015,
  author      = {Ruiz Castello, Pablo and Sgobbi, Alessandra and Nijs, Wouter and Thiel, Christian and Dalla Longa, Francesco and Kober, Tom and Elbersen, Berien and Hengeveld, Geerten},
  title       = {The {JRC-EU-TIMES} model. Bioenergy potentials for {EU} and neighbouring countries},
  institution = {Publications Office of the European Union},
  address     = {Luxembourg},
  year        = {2015},
  number      = {EUR 27575 EN},
  doi         = {10.2790/39014}
}
@misc{statfin12vq,
  author = {{Statistics Finland}},
  title  = {Total energy consumption by energy source (all categories), table 12vq},
  howpublished = {StatFin database, \url{pxdata.stat.fi/PxWeb/api/v1/en/StatFin/ehk/12vq.px}},
  note   = {Accessed 2026-10-08. Black liquor 42{,}989~GWh in 2017; total wood fuels 100{,}783~GWh}
}
```

**G4 — T8: capacity-table totals.** Change the *Domestic total* row to `121.9 & 101.6 & 40.0` (exact sums 121.943, 101.619, 40.000 GWh; the printed 122.0 and 101.5 are sums of rounded entries).

------------------------------------------------------------------------

## H. Thiran inheritance, retained biomass and waste boundary (T15–T16)

**H1 — Applied in V1.** The page pinpoint and 2017 profile-year rationale now follow the Finland TD-input table.

``` latex
The source mapping and preprocessing follow \citet[p.~60, Table~1.11]{thiranExploringOptionsFossilfree2025}.
All profiles use 2017 because it was the common historical year with the fewest missing
hours, preserving synchronicity between demand and weather-dependent series.
```

**H2 — On hold pending the S2BIOM decision.** The optional supplementary mapping is retained below for later consideration; it is not a current paste recommendation.

``` latex
\begin{table}[ht]
\centering
\caption{Inherited EnergyScope Multi-Cells biomass categories and their ENSPRESO mapping
\citep[pp.~66--67, Table~1.14]{thiranExploringOptionsFossilfree2025}. The present study
replaces only the aggregate woody-biomass resource with the Finland-specific ladder.}
\label{tab:inherited_biomass_mapping}
\begin{tabular}{lll}
\toprule
Category & Model layer & ENSPRESO commodities \\
\midrule
Woody biomass & WOOD & MINBIOWOO, MINBIOWOOa,
MINBIOWOOW1, MINBIOWOOW1a, MINBIOFRSR1,
MINBIOFRSR1a \\
Second-generation energy crops & WOOD & MINBIOCRP31,
MINBIOCRP41, MINBIOCRP41a \\
Wet biomass & WET\_BIOMASS & MINBIOGAS1, MINBIOSLU1 \\
Biowaste & BIOWASTE & MINBIOMUN1 \\
Biomass residues (agricultural waste) & BIOWASTE & MINBIOAGRW1 \\
\bottomrule
\end{tabular}
\end{table}
```

**H3 — Removed at the author's request.** No waste-boundary snippet is proposed. The underlying evidence question remains open in T16; removing H3 does not resolve or close that flag.

> Do not paste numerical 2035 corrections into the paper until T17 has been implemented in a new input version and the scenario matrix has been rerun.

------------------------------------------------------------------------

### Paste checklist (priority and status of each item: [FLAGS.md](./FLAGS.md))

- [ ] G1–G3 T1 wording and JRC reference (hold pending the black-liquor decision)
- [ ] G4 T8 totals corrected
- [x] A1 undefined citation fixed in V1
- [ ] A2 S3 comparator corrected in both occurrences (one incorrect S3-versus-S1 sentence remains in V1)
- [ ] A3 S3 unconstrained allocation re-extracted (9.8 TWh?)
- [ ] A4 duplicated biomass-allocation paragraph removed
- [ ] A5 DHN model value reconciled (52.33 vs 52.96)
- [ ] B.1 CHP (20.73 vs 25.0) and imports (20.43 vs 20.3) reconciled
- [ ] B.2 all 2035 matrix/allocation numbers re-checked vs run CSVs
- [ ] B.3 Mönkkönen denominator wording fixed; lit numbers confirmed
- [x] C1/C2 forest-sink and emissions-boundary caveat added (D3; heading style remains the author's choice)
- [ ] C3/C4 2017 benchmark wording revised (D4)
- [ ] C5 discount-rate sentence added (D5)
- [ ] D8 1.2% score explanation decided; footnote option only (not approved to paste)
- [ ] D9 S3/Mönkkönen scaling assumptions verified; current text is not paste-ready
- [ ] C6 2035 demand-projection method prepared in D6; not yet pasted into V1
- [ ] D7 limitations treatment revisited with the author
- [x] H1 Thiran Table 1.11 pinpoint and 2017 rationale added in V1
- [ ] H2 inherited biomass mapping held pending the S2BIOM decision
- [ ] H3 withdrawn; T16 remains unresolved
- [ ] E1–E6 style passes