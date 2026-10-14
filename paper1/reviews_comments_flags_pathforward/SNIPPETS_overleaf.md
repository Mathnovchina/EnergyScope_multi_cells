# Overleaf snippet tracker for `main_V1.tex`

**Target file:** [`main_V1.tex`](../Overleaf_working_paper/main_V1.tex) · **Title:** *From Bioeconomy Promise to Biodiversity Ceiling: The Role of Forest Biomass in Finnish Decarbonisation*. The author owns the `.tex`; snippets are suggestions only and are not pasted by the agent. `main_V0.tex` is the previous version. Issues, evidence and current status are in [FLAGS.md](./FLAGS.md).

**Snippet style:** avoid emphasis, paragraph-heading and typewriter-formatting commands. Use ordinary prose and paragraph flow, and keep identifiers in plain text or escaped LaTeX text.

------------------------------------------------------------------------

## How to use this file

Only items marked **PASTE NOW** require an edit in `main_V1.tex`. For each such item:

1. open the stated location;
2. search for the quoted anchor text;
3. perform the stated action (`REPLACE`, `INSERT AFTER`, or `DELETE`);
4. copy only the contents of the LaTeX block.

Items marked **DONE** are recorded for verification only. Items marked **HOLD — DO NOT
PASTE** are evidence or draft material awaiting an author decision.

### Current paste queue

| Order | Item | Status | Action in `main_V1.tex` |
|---:|---|---|---|
| 1 | D2 | **PASTE NOW** | Replace the one remaining incorrect S3-versus-S1 sentence |
| 2 | D3 | **PASTE NOW** | Delete the unwanted paragraph-style heading only |
| 3 | D4 | **PASTE NOW** | Replace the opening paragraph of the 2017 Validation subsection |
| 4 | D6 | **PASTE NOW** | Insert the demand-provenance paragraph after the Finland EUD calibration table |
| — | D1, D5, H1 | **DONE** | No paste required |
| — | D7–D9, G1–G4, H2–H3 | **HOLD — DO NOT PASTE** | Await the decisions stated below |

------------------------------------------------------------------------

## D. Detailed paste instructions

> Keys used below (`blattertSectoralPoliciesCause2022`, `monkkonenEcologicallyEconomicallySustainable2024`, `reckaRoleBiomassDecarbonisation2023`, `collaOptimalUseLignocellulosic2022`, `moretStrategicEnergyPlanning2017`) are all **present** in `references.bib`.

### D1 — DONE — citation key corrected (A1)

**No paste required.** Verified in the caption of Figure `enduses_flow`. It now uses:

```latex
Adapted from \citet{moretStrategicEnergyPlanning2017}.
```

### D2 — PASTE NOW — correct the remaining S3 cost comparison (A2)

**Where:** [`main_V1.tex`, biomass-allocation discussion](../Overleaf_working_paper/main_V1.tex).

**Find this exact sentence:**

```latex
The additional decarbonisation burden -- decentralised heat, synthetic gas -- must be absorbed entirely by non-biomass pathways, which is why the cost penalty for nuclear removal is nearly three times larger in S3 than in S1.
```

**Action:** `REPLACE` that sentence with:

```latex
The additional decarbonisation burden -- decentralised heat and synthetic gas -- must be
absorbed entirely by non-biomass pathways. The cost penalty for nuclear removal is therefore
about three times larger in S3 than in S2 and about seventeen times larger than in S1.
```

### D3 — PASTE NOW — remove the paragraph-style caveat heading (C1, C2)

**Where:** [`main_V1.tex`, immediately after the duplicated biomass-allocation
discussion](../Overleaf_working_paper/main_V1.tex).

**Find:** the standalone heading “Scope of the emissions constraint.” immediately before the
paragraph beginning “A central boundary of the present model...”.

**Action:** `DELETE` the entire LaTeX heading line. Do not replace it and do not delete the
caveat paragraph that follows.

### D4 — PASTE NOW — clarify the 2017 benchmark (C3, C4)

**Where:** [`main_V1.tex`, subsection “Finland 2017 Validation”](../Overleaf_working_paper/main_V1.tex).

**Find:** the first paragraph, beginning:

```latex
To establish model credibility before turning to forward-looking scenarios,
```

and ending:

```latex
with acceptable deviations.
```

**Action:** `REPLACE` that entire paragraph with:

```latex
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

### D5 — DONE — discount rate and lifetimes stated (C5)

**No paste required.** Verified immediately after the total-cost objective equation:

```latex
Investments are annualised with a discount rate of 1.5\% and technology-specific lifetimes \citep{DanishEnergyAgency2022}, consistent with the EnergyScope Multi-Cells original setting \citep{thiranExploringOptionsFossilfree2025}.
```

### D6 — PASTE NOW — document the 2035 demand method (C6, C9)

**Where:** [`main_V1.tex`, after Table `tab:fin_eud_params_2020`](../Overleaf_working_paper/main_V1.tex).

**Find this sequence:**

```latex
\end{threeparttable}
\end{table}

\subsubsection{Objective function: total annual cost (and emissions accounting)}
```

**Action:** `INSERT AFTER` `\end{table}` and before the Objective function subsubsection:

```latex
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

### D7 — HOLD — DO NOT PASTE — limitations structure

Deferred at the author's request. Revisit after deciding where the paper should consolidate
limitations and how to handle the 2017 weather/typical-day basis and the absence of
climate-adjusted weather and capacity factors.

### D8 — HOLD — DO NOT PASTE — optional 1.2% score footnote

The 1.2% is the v37 run's weighted mean absolute percentage error across 14 scored targets,
not a claim that every indicator is within 1.2% or that the fit is independent validation.
Three additional dashboard metrics have zero weight. Some scored targets are materially
shaped by imposed resource/capacity bounds. If the author later decides to report the score,
the preferred location is a footnote attached to the first sentence that reports it in the
2017 Validation subsection:

```latex
\footnote{The reported 1.2\% score is the weighted mean of the absolute percentage errors
against 14 calibration targets; three additional dashboard indicators are assigned zero
weight. It summarises calibration fit, not independent predictive validation: some target
values are partly imposed through resource-availability or technology-capacity constraints,
including the 35~TWh coal-plus-peat aggregate.}
```

The formula is implemented in `scripts/run_calib_manual.py` and the v37 count/score are
recorded in `Docs/finland_2017_validation_justifications.md`. Keep this item pending until
you decide whether and where to report the score.

### D9 — HOLD — DO NOT PASTE — S3/BDS scaling chain

The proposed chain is not established by the cited sources as written. It transfers a
southern-Finland harvest ratio to a national harvest figure, and the 15--20\% residue
fraction and 30--40\% collection share remain assumptions. The stated central calculation
gives 3.9--5.1~TWh; a separate full-grid audit puts 6~TWh at the upper edge of the assumed
range when using 1.5~MWh/m$^3$ (about 5.9~TWh before rounding), and within the grid under a
different 1.96~MWh/m$^3$ conversion. Those conversions are not interchangeable without
matching moisture and volume bases. Thus 6~TWh may be retained as an explicit high-end
scenario assumption, but it should not be presented as a direct consequence of the
Mönkkönen ratio. Reconcile the conversion basis and label the assumptions before drafting.

------------------------------------------------------------------------

## G. HOLD — DO NOT PASTE — supply-curve audit (T1–T14)

All G snippets are held pending the author's black-liquor decision and the S2BIOM/FI1 boundary decision. The earlier decision in [FLAGS.md](./FLAGS.md) records the previous proxy choice; it is not an instruction to paste these snippets now. No source data, inputs, runs or author-owned `.tex` files are changed by this tracker update. Evidence: [forest_supply_curve_methodology_traceability.md](../../Docs/forest_supply_curve_methodology_traceability.md).

The blocks below are retained as an archive of the previous proposal. None belongs in the
current paste queue.

**G1 — Held FI1 description.** Possible future replacement in Table
`tab:fi_biomass_ladder`.

``` latex
WOOD\_FI1 & Aggregate industrial wood by-products: black liquor, bark and sawdust (volume from ENSPRESO MINBIOWOOa)\footnotemark & 11 & 10 \\
```

**G2 — Held FI1 footnote.** Possible future table note.

``` latex
\footnotetext{Black liquor, bark and sawdust are the cheapest, largely captive wood-energy streams in Finland; black liquor alone reached 43~TWh in 2017, the single largest domestic wood-energy source \citep{statfin12vq}. Black liquor is not represented in the ENSPRESO database, so we take the volume of the cheapest ENSPRESO wood commodity, MINBIOWOOa (45~TWh, which ENSPRESO formally labels as stemwood chips and pellets \citep{ruizJRCEUTIMESModelBioenergy2015}), as a proxy for this by-product stream. The assigned cost (11~\euro/MWh) and embedded GHG (10~tCO$_2$eq/GWh) reflect captive mill-gate by-products; replacing this proxy with a physically grounded black-liquor/by-product split is left to forthcoming work coupling G4M and industrial-throughput data.}
```

*If reactivated:* check `\euro` availability and footnote placement inside the table.

**G3 — Held bibliography entries.**

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

**G4 — Held T8 capacity-table totals.** If reactivated, change the *Domestic total* row to
`121.9 & 101.6 & 40.0` (exact sums 121.943, 101.619, 40.000 GWh; the printed 122.0 and
101.5 are sums of rounded entries).

------------------------------------------------------------------------

## H. Thiran inheritance, retained biomass and waste boundary (T15–T16)

### H1 — DONE — Thiran pinpoint and profile-year rationale

**No paste required.** Verified after the Finland TD-input table:

``` latex
The source mapping and preprocessing follow \citet[p.~60, Table~1.11]{thiranExploringOptionsFossilfree2025}.
All profiles use 2017 because it was the common historical year with the fewest missing
hours, preserving synchronicity between demand and weather-dependent series.
```

### H2 — HOLD — DO NOT PASTE — inherited biomass mapping

Pending the S2BIOM decision. If later approved, this would be inserted in the Supplementary
Material, not in the current main-text flow:

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

### H3 — HOLD — DO NOT PASTE — withdrawn

Removed at the author's request. No waste-boundary snippet is proposed. The underlying
evidence question remains open in T16; removing H3 does not resolve or close that flag.

> Do not paste numerical 2035 corrections into the paper until T17 has been implemented in a new input version and the scenario matrix has been rerun.

------------------------------------------------------------------------

### Wider manuscript checklist

This list includes unresolved manuscript issues that do not yet have approved paste blocks.
It is not the paste queue; use the queue at the top of this file for the current Overleaf
edits. Priority and status are maintained in [FLAGS.md](./FLAGS.md).

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
- [x] C5 discount-rate sentence added (D5)
- [ ] D8 1.2% score explanation decided; footnote option only (not approved to paste)
- [ ] D9 S3/Mönkkönen scaling assumptions verified; current text is not paste-ready
- [ ] C6 2035 demand-projection method prepared in D6; not yet pasted into V1
- [ ] D7 limitations treatment revisited with the author
- [x] H1 Thiran Table 1.11 pinpoint and 2017 rationale added in V1
- [ ] H2 inherited biomass mapping held pending the S2BIOM decision
- [ ] H3 withdrawn; T16 remains unresolved
- [ ] E1–E6 style passes