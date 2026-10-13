# Overleaf snippets — paste-ready LaTeX for `main_certosa.tex`

**Target file:** `main_certosa.tex` · **Title:** *From Bioeconomy Promise to Biodiversity Ceiling: The Role of Forest Biomass in Finnish Decarbonisation* **Author-owned:** the `.tex` is never edited by the agent; paste from here. The issues, status and priorities that these snippets resolve are in [FLAGS.md](./FLAGS.md) (the review items A, B, C, E and the source map moved there on 2026-10-12; snippet IDs D1–D9 and G1–G4 are unchanged).

------------------------------------------------------------------------

## D. Paste-ready LaTeX snippets

> Keys used below (`blattertSectoralPoliciesCause2022`, `monkkonenEcologicallyEconomicallySustainable2024`, `reckaRoleBiomassDecarbonisation2023`, `collaOptimalUseLignocellulosic2022`, `moretStrategicEnergyPlanning2017`) are all **present** in `references.bib`.

**D1 — Fix undefined citation (A1).** In the `enduses_flow` caption, replace:

``` latex
Adapted from \citet{moret_strategic_2017}.
```

with:

``` latex
Adapted from \citet{moretStrategicEnergyPlanning2017}.
```

**D2 — Corrected S3 nuclear-sensitivity sentence (A2).**

``` latex
By contrast, S3 cannot expand further because its 40~TWh domestic ceiling is already
binding, making the nuclear phase-out markedly more costly (+0.34~bn~EUR/y, versus
+0.02 and +0.10~bn~EUR/y in S1 and S2). The sensitivity of system cost to nuclear
availability is therefore about three times larger than in S2 and an order of
magnitude larger than in S1: S3 does not make deep decarbonisation infeasible, but it
removes forest biomass as a flexible adjustment margin and becomes the highest-cost
configuration.
```

**D3 — Forest-sink / carbon-neutrality caveat (C1, C2).** Add to a Limitations block or at the end of §Results:

``` latex
\paragraph{Scope of the emissions constraint.}
A central boundary of the present model must be stated explicitly. The greenhouse-gas
constraint accounts for \emph{energy-system} emissions only: resource supply-chain GHG
(RED~II Annex~VI) plus technology construction impacts (Eq.~\ref{eq:gwp_total}). Biogenic
combustion CO$_2$ is treated as carbon-neutral \footnote{A strong assumption because the carbon neutrality of forest biomass for bioenergy remains contested, with growing literature challenging the assumption that biomass combustion yields net-zero emissions. \cite{selivanovCarbonNeutralityForest2023,ahamerWhyBiomassFuels2022,ahamerHowComputeWhether2024,feiwuStrategicUsesAncillary2023,boothNotCarbonNeutral2018} dissect this issue, exposing the complexities in biomass carbon accounting.}, and the model contains \emph{no}
representation of the forest carbon sink, land-use (LULUCF) flux, or harvested-wood-product
carbon. Consequently, the climate difference between intensive (S1) and conservation (S3)
harvesting is seen by the optimiser only through supply-chain GHG and cost, not through the
standing-stock and sink dynamics that dominate the real land--energy carbon balance
\citep{reckaRoleBiomassDecarbonisation2023}. This is deliberate for a first, energy-system
step, and it is precisely the gap that will be analysed in future research.
```

**D4 — Peat and `relax_co2` caveat (C3, C4).** Add near the 2017 validation discussion:

``` latex
Two modelling choices in the historical benchmark should be read as caveats rather than
results. First, Finnish peat is not represented as a distinct resource; its primary energy
and emissions are proxied through the \texttt{COAL} resource, so the ``coal + peat''
aggregate is reproduced by construction rather than independently. Because peat is more
emissions-intensive than coal, this proxy slightly flatters the realism of the CO$_2$
accounting. Second, the 2017 run relaxes the CO$_2$ cap to avoid a non-physical forced-CCS
artefact; the reported 2017 emissions are therefore a reproduction of the observed system,
not an optimisation outcome, and this relaxation is \emph{not} applied to the 2035 scenarios.
```

**D5 — Cost/discount-rate assumptions (C5).** Add after the objective-function equation:

``` latex
Investments are annualised with a discount rate of 1.5\% and technology-specific lifetimes \citep{DanishEnergyAgency2022}, consistent with the EnergyScope Multi-Cells original setting \citep{thiranExploringOptionsFossilfree2025}.
```

**D6 — 2035 demand / base-year clarification (C6, C9).** Fill the bracket with your actual method:

``` latex
The end-use split parameters in Table~\ref{tab:fin_eud_params_2020} (district-heating share,
modal shares, grid losses) are calibrated on 2019--2020 Finnish statistics and held fixed
across the 2017 validation and the 2035 scenarios, i.e. structural shares are assumed stable
over the horizon. Annual end-use demand \emph{levels} for 2035 are obtained by
[\textbf{TODO: state your projection — e.g. held at 2017 levels / scaled by a published
national demand projection / sector-specific growth factors}], which should be stated here
for reproducibility.
```

**D7 — Consolidated "Limitations" subsection (C7 + umbrella).** Drop in before `\section{Conclusion}`:

``` latex
\subsection{Limitations}
\label{sec:limitations}
Four limitations frame the interpretation of these results. (i) The emissions constraint is
energy-only: there is no forest carbon sink, LULUCF, or harvested-wood-product term, so the
model cannot represent the dominant climate effect of harvest intensity (see above).
(ii) Finland is represented as a single node, abstracting from intra-country transmission and
regional renewable heterogeneity; this is defensible given the southern concentration of
demand but omits internal congestion. (iii) The biomass ladder is static and exogenous: the
scenarios differ in availability and cost only, with no forest growth, age structure, or
disturbance dynamics, and S1/S3 are stylised/audited narratives rather than database values.
(iv) The typical-day LP abstracts from unit-commitment and short-term operational detail.
These boundaries motivate the disturbance-coupled, sink-aware extension outlined in
Section~\ref{sec:results}.
```

**D8 — Optional: strengthen the validation claim (B.1).** The headline calibration quality is currently undersold. In the abstract or §Validation you can state:

``` latex
Across the 14 scored indicators the calibrated 2017 benchmark reaches a weighted deviation
of about 1.2\%, with net CO$_2$ reproduced to within 0.1\%; the only large residuals are the
two structural aggregation artefacts discussed below (district heating and gas-CHP).
```

> ⚠️ Confirm "1.2% / 14 indicators" against your final run before using (source: `Docs/finland_2017_validation_justifications.md`).

**D9 — S3/BDS Mönkkönen scaling chain (new — adds transparency to the softest number in the paper).** *Where:* §Biomass, right after the sentence describing the three-way audit that revises S3 down to 40 TWh. *Why:* the paper states S3 was revised using Mönkkönen but never shows the scaling, which is the most-questioned input in the paper (it drives the headline result). *Keys (all in bib):* `monkkonenEcologicallyEconomicallySustainable2024`, `blattertSectoralPoliciesCause2022`, `lukeWoodEnergy2024`.

``` latex
The conservative S3/BDS ceiling is obtained by scaling the
\citet{monkkonenEcologicallyEconomicallySustainable2024} harvest ceiling, which is expressed
as a fraction of the maximum economically sustainable harvest for \emph{southern} Finland
(current harvest $\approx 96\%$; ecologically safe level $\approx 58$--$60\%$). The scaling
proceeds in two stages. First (percentage $\rightarrow$ national harvest), anchoring on the
2018 roundwood harvest of 78.2~Mm$^3$ \citep{blattertSectoralPoliciesCause2022} gives an
implied maximum sustainable harvest of $78.2/0.96 \approx 81$~Mm$^3$/yr, and the $60\%$
ecological ceiling yields $\approx 49$~Mm$^3$/yr (extrapolating the southern-Finland ratio to
the whole country, a deliberate simplification). Second (harvest $\rightarrow$ energy-available
residues), the logging-residue fraction of merchantable volume ($\approx 15$--$20\%$) implies
$\approx 8.6$~Mm$^3$ of technical potential, of which only $30$--$40\%$ is collectable under a
biodiversity-first regime that retains deadwood and dispersed residues, i.e.
$\approx 2.6$--$3.4$~Mm$^3 \approx 3.9$--$5.1$~TWh at 1.5~MWh/solid~m$^3$. The logging-residue
step \texttt{WOOD\_FI2} is set at 6~TWh, just above this range. Most of the reduction relative
to the ENSPRESO low potential therefore originates in the second stage (residue fraction and
collection efficiency) rather than in the harvest-ceiling scaling itself, and is corroborated
by observed Finnish residue use \citep{lukeWoodEnergy2024}.
```

> ⚠️ The residue-fraction (15–20%) and collection-efficiency (30–40%) are expert-audit values, not measured — confirm against `Docs/biomass_scenario_mapping.md` §3.5.1 before using.

------------------------------------------------------------------------

## G. Supply-curve audit (T1–T14) — paste-ready snippets

Status and decisions: [FLAGS.md](./FLAGS.md) (§3 decisions log) · evidence: [forest_supply_curve_methodology_traceability.md](../../Docs/forest_supply_curve_methodology_traceability.md) · re-run: `python scripts/check_forest_supply_traceability.py`. The `.tex` has **not** been edited. **Adopted decision (FLAGS.md §3, 2026-10-08):** `WOOD_FI1` represents Finland's captive industrial by-product stream (black liquor, bark, sawdust); its volume is the ENSPRESO `MINBIOWOOa` commodity, used as a documented proxy because black liquor is absent from ENSPRESO. All numbers are unchanged (no re-run). The snippets add the ENSPRESO-label caveat and keep the by-product wording. **Pending:** flag S2B-1 (S2BIOM stemwood cross-check) may change the G1–G2 wording; hold these until you decide.

**G1 — FI1 description** (Table `tab:fi_biomass_ladder`; the existing "black liquor, bark, sawdust" wording is retained, so you may only need the footnote G2).

``` latex
\texttt{WOOD\_FI1} & Aggregate industrial wood by-products: black liquor, bark and sawdust (volume from ENSPRESO \texttt{MINBIOWOOa})\footnotemark & 11 & 10 \\
```

**G2 — FI1 footnote (the key addition: the ENSPRESO-label caveat and the black-liquor rationale).**

``` latex
\footnotetext{Black liquor, bark and sawdust are the cheapest, largely captive wood-energy streams in Finland; black liquor alone reached 43~TWh in 2017, the single largest domestic wood-energy source \citep{statfin12vq}. Black liquor is not represented in the ENSPRESO database, so we take the volume of the cheapest ENSPRESO wood commodity, \texttt{MINBIOWOOa} (45~TWh, which ENSPRESO formally labels as stemwood chips and pellets \citep{ruizJRCEUTIMESModelBioenergy2015}), as a proxy for this by-product stream. The assigned cost (11~\euro/MWh) and embedded GHG (10~tCO$_2$eq/GWh) reflect captive mill-gate by-products; replacing this proxy with a physically grounded black-liquor/by-product split is left to forthcoming work coupling G4M and industrial-throughput data.}
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
  howpublished = {StatFin database, \texttt{pxdata.stat.fi/PxWeb/api/v1/en/StatFin/ehk/12vq.px}},
  note   = {Accessed 2026-10-08. Black liquor 42{,}989~GWh in 2017; total wood fuels 100{,}783~GWh}
}
```

**G4 — T8: capacity-table totals.** Change the *Domestic total* row to `121.9 & 101.6 & 40.0` (exact sums 121.943, 101.619, 40.000 GWh; the printed 122.0 and 101.5 are sums of rounded entries).

------------------------------------------------------------------------

## H. Thiran inheritance, retained biomass and waste boundary (T15–T16)

**H1 — Table 1.11 pinpoint and 2017 choice.** *Where:* after the existing Finland TD-input table. *Why:* its content already reproduces Thiran's source/processing table; only the page-level attribution and reference-year rationale are missing. *Key:* `thiranExploringOptionsFossilfree2025`.

``` latex
The source mapping and preprocessing follow \citet[p.~60, Table~1.11]{thiranExploringOptionsFossilfree2025}.
All profiles use 2017 because it was the common historical year with the fewest missing
hours, preserving synchronicity between demand and weather-dependent series.
```

**H2 — Suggested supplementary table based on Thiran Table 1.14.** *Where:* supplementary methods, immediately before the Finland-specific `WOOD_FI1`–`WOOD_FI5` extension. *Why:* distinguishes the inherited five-category biomass structure from this paper's new forest ladder. *Key:* `thiranExploringOptionsFossilfree2025`.

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
Woody biomass & WOOD & \texttt{MINBIOWOO}, \texttt{MINBIOWOOa},
\texttt{MINBIOWOOW1}, \texttt{MINBIOWOOW1a}, \texttt{MINBIOFRSR1},
\texttt{MINBIOFRSR1a} \\
Second-generation energy crops & WOOD & \texttt{MINBIOCRP31},
\texttt{MINBIOCRP41}, \texttt{MINBIOCRP41a} \\
Wet biomass & WET\_BIOMASS & \texttt{MINBIOGAS1}, \texttt{MINBIOSLU1} \\
Biowaste & BIOWASTE & \texttt{MINBIOMUN1} \\
Biomass residues (agricultural waste) & BIOWASTE & \texttt{MINBIOAGRW1} \\
\bottomrule
\end{tabular}
\end{table}
```

**H3 — Legacy waste disclosure.** *Where:* note below H2 or in data limitations. *Why:* prevents an unsupported claim that the retained `WASTE` and ENSPRESO `BIOWASTE` pools form a verified physical partition.

``` latex
\paragraph{Waste boundary.}
The model also retains the legacy non-renewable \texttt{WASTE} resource used in the
original EnergyScope Multi-Cells database. Its potential is attributed by
\citet[pp.~63--67]{thiranExploringOptionsFossilfree2025} to Elbersen et al. using the
Dommisse--Tychon method, whereas \texttt{BIOWASTE} is the ENSPRESO municipal-waste
commodity \texttt{MINBIOMUN1}. We preserve this setting
with the parent dataset, but the available calculation does not demonstrate an explicit
biogenic/non-biogenic partition between the two pools. Results involving waste should
therefore be interpreted with this boundary caveat.
```

> Do not paste numerical 2035 corrections into the paper until T17 has been implemented in a new input version and the scenario matrix has been rerun.

------------------------------------------------------------------------

### Paste checklist (priority and status of each item: [FLAGS.md](./FLAGS.md))

- [ ] G1–G3 T1 corrected wording and JRC reference (hold until S2B-1 is decided)
- [ ] G4 T8 totals corrected
- [ ] A1 undefined citation fixed
- [ ] A2 S3 "three times" comparator corrected (×2 occurrences)
- [ ] A3 S3 unconstrained allocation re-extracted (9.8 TWh?)
- [ ] A4 duplicated biomass-allocation paragraph removed
- [ ] A5 DHN model value reconciled (52.33 vs 52.96)
- [ ] B.1 CHP (20.73 vs 25.0) and imports (20.43 vs 20.3) reconciled
- [ ] B.2 all 2035 matrix/allocation numbers re-checked vs run CSVs
- [ ] B.3 Mönkkönen denominator wording fixed; lit numbers confirmed
- [ ] C1 forest-sink caveat added (D3)
- [ ] C3/C4 peat + relax_co2 caveat added (D4)
- [ ] C5 discount-rate sentence added (D5)
- [ ] D9 S3 Mönkkönen scaling chain added to §Biomass
- [ ] C6 2035 demand-projection method documented (D6)
- [ ] D7 limitations subsection inserted
- [ ] H1 Thiran Table 1.11 pinpoint and 2017 rationale added
- [ ] H2 inherited biomass mapping (Thiran Table 1.14) added to supplement
- [ ] H3 legacy `WASTE`/`BIOWASTE` boundary disclosed
- [ ] E1–E6 style passes