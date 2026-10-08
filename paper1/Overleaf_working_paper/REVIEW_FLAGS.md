# Working Paper — Review Flags, Caveats & Snippets

**Target file:** `main_certosa.tex` · **Title:** *From Bioeconomy Promise to Biodiversity Ceiling: The Role of Forest Biomass in Finnish Decarbonisation*
**Maintained by:** manual review tracker (not auto-generated). Last updated: 2026-10-02.

> **How to use this file.** Each item has a **priority tag**, a **location** in the paper, the **issue**, and where relevant a **paste-ready LaTeX snippet** (Section D). Tick items off as you resolve them. Numbers were cross-checked against the repository ground-truth files listed in Section F.

**Priority legend**
- 🔴 **MUST-FIX** — correctness/compile error or a number that is internally inconsistent. Fix before sharing.
- 🟠 **VERIFY** — a number/claim that must be confirmed against run outputs or a primary source.
- 🟡 **CAVEAT** — a limitation that should be disclosed so reviewers don't raise it first.
- 🔵 **STYLE** — consistency / polish, non-blocking.

---

## A. 🔴 Must-fix (correctness & compilation)

| # | Location | Issue | Action |
|---|---|---|---|
| A1 | Fig. `enduses_flow` caption (`\label{fig:enduses_flow}`) | Citation `\citet{moret_strategic_2017}` is **undefined** — the bib key is `moretStrategicEnergyPlanning2017` (underscore form does not exist). Will render as **[?]**. | Replace with `moretStrategicEnergyPlanning2017`. See snippet **D1**. |
| A2 | §Results 2035, matrix discussion ("sensitivity to nuclear availability roughly three times greater than in S1") **and** the later biomass-allocation paragraph ("cost penalty for nuclear removal is nearly three times larger in S3 than in S1") | **Numeric inconsistency.** Nuclear-removal cost penalties from Table `tab:fi_2035_matrix`: S1 = 22.94−22.92 = **0.02**; S2 = 23.12−23.02 = **0.10**; S3 = 23.90−23.56 = **0.34** bn€/y. So S3 is ~**3×** the **S2** penalty and ~**17×** the S1 penalty — *not* "three times greater than in S1". | Change comparator to **S2**, or restate as "an order of magnitude larger than in S1". Snippet **D2**. |
| A3 | §Results, biomass-allocation paragraph ("25.9 TWh in S1, 16.8 TWh in S2, and 9.8 TWh in S3") | **Accounting mismatch for S3 unconstrained.** With chemicals = 27.9 TWh + methanol = 0.8 TWh, residual industrial heat should equal *wood used − 28.7*. S1: 54.5−28.7 = 25.8 ✓; S2: 45.4−28.7 = 16.7 ✓; **S3: 32.0−28.7 = 3.3 TWh, not 9.8**. Either the "9.8" is wrong, or S3 unconstrained wood use ≠ 32.0, or chemicals is not a flat 27.9 across all nine cases. | Re-extract S3 unconstrained end-use split from the run; correct the number and/or soften "across all nine scenarios". |
| A4 | §Results, second paragraph beginning "Figure~\ref{fig:fi_2035_biomass_allocation} adds the end-use interpretation behind that aggregate picture." | **Duplicated paragraph** — this sentence/figure intro appears **twice** (once with "Three patterns stand out", once later "In S1/BES and S2/NFS, the no-nuclear variants redirect..."). Redundant. | Merge the two into one, or delete the second. |
| A5 | §Results validation text vs Table `tab:fi_validation_2017` | District-heating **model** value: paper table = **52.33 TWh (+43.4%)**, but `Docs/finland_2017_validation_justifications.md` reports **52.96 TWh (+45.1%)** for the canonical run. The two don't match → confirm which run/number is current and make text, table, and the justification doc agree. | Reconcile DHN model value & %. |

---

## B. 🟠 Numbers to verify

### B.1 — 2017 validation table (`tab:fi_validation_2017`)
All **"Actual 2017"** values match the reference file `calibration/reality/finland_2017_reference.csv` (confirmed via `Docs/finland_2017_reality_reference_audit.md`) **except two**:

| Indicator | Paper "Actual" | Reference CSV / audit | Status |
|---|---|---|---|
| Biomass / Oil / Gas / Coal+peat / Nuclear / Hydro / Wind (PE) | 100 / 82 / 20 / 35 / 65 / 15 / 5 | 100 / 82 / 20 / 35 / 65 / 15 / 5 | ✅ sourced |
| CO₂ | 41.2 (model 41.25, +0.1%) | 41.2 MtCO₂ | ✅ sourced |
| **Electricity — CHP** | **20.73** (model 20.49) | audit lists **ELEC_CHP = 25.0 TWh** | ⚠️ **reconcile** — different CHP definition or updated reference? |
| **Electricity — Imports** | **20.43** (model 19.54) | audit lists **20.3 TWh** | ⚠️ minor — align 20.43 vs 20.3 |
| Gas power | 3.2 (model 4.37, +36.7%) | ELEC_GAS actual 3.2 | ✅ (model value differs across docs: 4.34/4.37/4.38 — pick one) |
| DHN production | 36.5 (model 52.33, +43.4%) | 36.5; model 52.96 in justif. doc | ⚠️ see **A5** |

> **Note (peat):** "Coal + peat 35.0" is a **proxy** — the model has a `COAL` resource only; peat (historically ~15 TWh in Finland, and more emissions-intensive than coal) is lumped into it. The forced 0.0% error reflects calibration, not independent reproduction. → disclose as a caveat (**C3**).

### B.2 — 2035 matrix (`tab:fi_2035_matrix`) internal-consistency checks (all passed except A2/A3)
- Unconstrained CO₂ 12.57–13.10 Mt ⇒ **68.2–69.5%** below 41.2 → "**68–70%**" ✅ (figure caption says "roughly 70%", fine but loosen if you want precision).
- −95% target ⇒ 41.2 × 0.05 = **2.06 Mt** for all cases ✅.
- Wood-use additivity ✅: −95% S1 = 54.5(FI1)+19.6(FI2) = 74.1 ≈ 74.2; S2 = 45.4+28.7 = 74.1 ≈ 74.2; no-nuclear S1 = 54.5+45.9 = 100.4; S2 = 45.4+38.2+12.5 = 96.1 ≈ 96.2.
- **Still verify against the run CSVs** (not just internally): the per-case **Cost** (22.40–23.90 bn€/y), **CO₂ net**, **Wood used**, the "**fossil imports 46–47 → ~8 TWh (>80%)**" claim, and every allocation figure (19.6/28.7/45.9/12.5, 20.1 transport, 15.6/12.4 dec-heat, 10.1/8.8 ind-heat, 8.3–8.6 synthetic methane).

### B.3 — Literature numbers (confirm against the cited papers / repo report)
| Claim | Where | Check |
|---|---|---|
| Forests ≈ **75%** of land area; wood ≈ **25%** of primary energy | Abstract, Intro | Add Statistics Finland / Luke citation; 100/380 = 26% (say "~25%"). |
| Mönkkönen: current harvest ≈ **96%**, ecological ceiling ≈ **60%** | Intro, Lit | **Denominator fix:** repo says 96% of *maximum economically sustainable potential* (Southern Finland). Intro currently says "96% of the **mean annual increment**" — different denominator. Correct wording + keep "southern Finland" caveat. |
| Blattert BES = **75%** of max possible harvest | §Biomass | ✅ matches `Docs/biomass_scenario_mapping.md`. |
| EU BDS: roundwood −**48%**, **50–73%** import leakage | Lit | Verify against `fischerLeakageBiodiversityRisks2024` et al. |
| Czech: salvage **92%** of harvest, **25.5 Mm³** (2019), **€1.12 bn** loss | Lit | Verify vs `simunekNorwaySpruceForest2024`, `tothImpactsCalamityLogging2020`. |
| Beringer 2050 bioenergy **126–216 EJ** | Lit | Verify vs `beringerBioenergyProductionPotential2011`. |
| Colla: BE 2030 **30–90 TWh**; EU27+UK **2000–2500 TWh** | §Biomass | Verify vs `collaNavigatingBioenergyHorizons2024`. |
| Recka: renewable-share effect **<1.5 pp**, dissipates after 2030 | Lit | Verify vs `reckaRoleBiomassDecarbonisation2023`. |

---

## C. 🟡 Important caveats to add or strengthen

| # | Caveat | Why it matters | Snippet |
|---|---|---|---|
| C1 | **No forest carbon sink / LULUCF in the GHG constraint.** The model's emission target counts **energy-system combustion CO₂ only**; biomass combustion is treated as carbon-neutral and there is **no sink / HWP / LULUCF term**. | This is the single biggest limitation and a reviewer magnet — especially since the paper *itself* criticises models that "wrongly treat biomass as carbon neutral", and cites Recka showing LULUCF dynamics dominate. Must be stated explicitly as a boundary of *this* model. | **D3** |
| C2 | **Biomass carbon-neutrality assumption.** Only supply-chain GHG (RED II Annex VI) is charged; biogenic combustion CO₂ = 0. | Directly shapes why S1/S3 differ only in cost, not in combustion emissions. | folded into **D3** |
| C3 | **Peat modelled as coal.** No separate peat resource; emissions and primary energy of peat are proxied by `COAL`. | Peat is higher-emitting than coal and non-trivial in Finland; affects CO₂ accounting realism. | **D4** |
| C4 | **2017 uses `relax_co2` (CO₂ cap relaxed).** Already mentioned once; make it an explicit, labelled caveat and state it is **not** carried into 2035. | Avoids the impression that 2017 emissions are an optimisation outcome. | **D4** |
| C5 | **Discount rate / annualisation not stated.** The objective uses τ(j) but the **social discount rate (1.5%)** and lifetimes aren't given. | 1.5% strongly favours capital-intensive nuclear/renewables → a load-bearing assumption worth one sentence + a sensitivity note. | **D5** |
| C6 | **2035 end-use demand projection is undocumented.** The EUD mapping table is calibrated to **2020** (with 2019 modal shares); how demands are scaled to **2035** is not described. | A methodological gap; reviewers will ask how 2035 demand levels were produced. | placeholder **D6** |
| C7 | **Single-node (no intra-Finland spatial detail).** Already argued as defensible — keep, but list it in the consolidated limitations block. | Pre-empts the standard critique. | folded into **D7** |
| C8 | **S1/BES (+20%) and S3/BDS (40 TWh) are stylised/audited, not raw ENSPRESO.** Disclosed in §Biomass — also echo it in the results discussion and the figure caption footnote. | Keeps the stylised status visible where the numbers are used. | — |
| C9 | **EUD split base-year mismatch (2020 params for a 2017 validation).** `tab:fin_eud_params_2020` is "baseline year 2020" but drives the 2017 reproduction. | Minor but a careful reviewer will notice; one clarifying sentence suffices. | **D6** |

---

## D. Paste-ready LaTeX snippets

> Keys used below (`blattertSectoralPoliciesCause2022`, `monkkonenEcologicallyEconomicallySustainable2024`, `reckaRoleBiomassDecarbonisation2023`, `collaOptimalUseLignocellulosic2022`, `moretStrategicEnergyPlanning2017`) are all **present** in `references.bib`.

**D1 — Fix undefined citation (A1).** In the `enduses_flow` caption, replace:
```latex
Adapted from \citet{moret_strategic_2017}.
```
with:
```latex
Adapted from \citet{moretStrategicEnergyPlanning2017}.
```

**D2 — Corrected S3 nuclear-sensitivity sentence (A2).**
```latex
By contrast, S3 cannot expand further because its 40~TWh domestic ceiling is already
binding, making the nuclear phase-out markedly more costly (+0.34~bn~EUR/y, versus
+0.02 and +0.10~bn~EUR/y in S1 and S2). The sensitivity of system cost to nuclear
availability is therefore about three times larger than in S2 and an order of
magnitude larger than in S1: S3 does not make deep decarbonisation infeasible, but it
removes forest biomass as a flexible adjustment margin and becomes the highest-cost
configuration.
```

**D3 — Forest-sink / carbon-neutrality caveat (C1, C2).** Add to a Limitations block or at the end of §Results:
```latex
\paragraph{Scope of the emissions constraint.}
A central boundary of the present model must be stated explicitly. The greenhouse-gas
constraint accounts for \emph{energy-system} emissions only: resource supply-chain GHG
(RED~II Annex~VI) plus technology construction impacts (Eq.~\ref{eq:gwp_total}). Biogenic
combustion CO$_2$ is treated as carbon-neutral, and the model contains \emph{no}
representation of the forest carbon sink, land-use (LULUCF) flux, or harvested-wood-product
carbon. Consequently, the climate difference between intensive (S1) and conservation (S3)
harvesting is seen by the optimiser only through supply-chain GHG and cost, not through the
standing-stock and sink dynamics that dominate the real land--energy carbon balance
\citep{reckaRoleBiomassDecarbonisation2023}. This is deliberate for a first, energy-system
step, and it is precisely the gap that the planned forest-disturbance and sink-coupling
extension is designed to close.
```

**D4 — Peat and `relax_co2` caveat (C3, C4).** Add near the 2017 validation discussion:
```latex
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
```latex
Unless stated otherwise, investments are annualised with a social discount rate of 1.5\%
and technology-specific lifetimes, consistent with the EnergyScope Multi-Cells Finnish
dataset \citep{thiranExploringOptionsFossilfree2025}. A low discount rate favours
capital-intensive low-carbon assets (nuclear, renewables) relative to fuel-based options
and is therefore a load-bearing assumption; its sensitivity is a natural robustness check.
```

**D6 — 2035 demand / base-year clarification (C6, C9).** Fill the bracket with your actual method:
```latex
The end-use split parameters in Table~\ref{tab:fin_eud_params_2020} (district-heating share,
modal shares, grid losses) are calibrated on 2019--2020 Finnish statistics and held fixed
across the 2017 validation and the 2035 scenarios, i.e. structural shares are assumed stable
over the horizon. Annual end-use demand \emph{levels} for 2035 are obtained by
[\textbf{TODO: state your projection — e.g. held at 2017 levels / scaled by a published
national demand projection / sector-specific growth factors}], which should be stated here
for reproducibility.
```

**D7 — Consolidated "Limitations" subsection (C7 + umbrella).** Drop in before `\section{Conclusion}`:
```latex
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
```latex
Across the 14 scored indicators the calibrated 2017 benchmark reaches a weighted deviation
of about 1.2\%, with net CO$_2$ reproduced to within 0.1\%; the only large residuals are the
two structural aggregation artefacts discussed below (district heating and gas-CHP).
```
> ⚠️ Confirm "1.2% / 14 indicators" against your final run before using (source: `Docs/finland_2017_validation_justifications.md`).

**D9 — S3/BDS Mönkkönen scaling chain (new — adds transparency to the softest number in the paper).**
*Where:* §Biomass, right after the sentence describing the three-way audit that revises S3 down to 40 TWh. *Why:* the paper states S3 was revised using Mönkkönen but never shows the scaling, which is the most-questioned input in the paper (it drives the headline result). *Keys (all in bib):* `monkkonenEcologicallyEconomicallySustainable2024`, `blattertSectoralPoliciesCause2022`, `lukeWoodEnergy2024`.
```latex
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

---

## E. 🔵 Style & consistency

| # | Location | Issue | Suggested fix |
|---|---|---|---|
| E1 | Supply-curve figure caption vs Table `tab:fi_biomass_capacities` | Two different LUKE keys: figure uses `Luke2025ForestTrade`, table uses `lukeWoodEnergy2024`. Both exist in the bib. | Confirm they are **intentionally different** sources (2025 forest-trade vs 2024 wood-energy stats); otherwise unify. |
| E2 | Throughout | **CO₂ notation is mixed**: `\ce{CO2}` (mhchem) in a few places, `CO$_2$` elsewhere. | Pick one (recommend `CO$_2$` for prose) and apply consistently. |
| E3 | Lit review | `\cite{reckaRoleBiomassDecarbonisation2023}'s study` and `The \cite{...}'s` read awkwardly with `natbib`. | Use `\citet{...}` or `\citeauthor{...}`'s. |
| E4 | `moretCharacterizationInputUncertainties2017` **and** `...2017a` both in bib | Possible duplicate entry. | Check which one is the intended Moret uncertainty paper; remove the stray. |
| E5 | §Results | "within approximately 5\%" (abstract) vs per-indicator errors | Fine, but consider citing the 1.2% weighted figure (D8) so the strong result isn't buried. |
| E6 | Model naming | Paper says "EnergyScope TD"; the runs use EnergyScope **Multi-Cells** (single-cell Finland). | One sentence noting the single-cell ESMC reduces to the TD formulation used here. |

---

## F. Source map (claim → repository ground-truth)

| Paper element | Verify against |
|---|---|
| 2017 "Actual" column | `calibration/reality/finland_2017_reference.csv`; audit `Docs/finland_2017_reality_reference_audit.md` |
| 2017 model values, 1.2% / 14 metrics, DHN & gas-CHP residuals | `Docs/finland_2017_validation_justifications.md` |
| 41,200 ktCO₂ baseline, −95% = 2.06 Mt, "~69%" | `Docs/finland_2035_ghg_sweep_results.md` |
| Biomass ladder costs/GHG (11/22[26]/27/33/70; 10/22/14/19/40) | `Data/2035/FI/Resources_S{1,2,3}_*.csv`; `Docs/biomass_supply_curve_fi.md` |
| Step capacities (122.0 / 101.5 / 40.0 TWh) | same CSVs; `Docs/biomass_scenario_mapping.md` |
| S3 three-way audit (74.2 → 40 TWh) | `Docs/biomass_scenario_mapping.md` §3.5.1 |
| Mönkkönen 96% / 58–60% (Southern Finland) | `Docs/biomass_scenario_mapping.md` §1.2 |
| 2035 matrix (cost / CO₂ / wood / allocation) | run outputs under `case_studies/FI/forest_scenarios_2035/` |
| Disturbance literature figures | `Docs/literature/forest_disturbance_timber_economics_report.md` |
| No-sink / LULUCF gap | `AGENT.md` §5; `Docs/concept_note_G4M_forest_energy_finland.md` §2 |

---

## G. Supply-curve audit (T1–T14) — paste-ready snippets

Tracker: `Docs/forest_supply_flags_tracker.md` (§7 is the adopted resolution) · evidence: `Docs/forest_supply_curve_methodology_traceability.md` · re-run: `python scripts/check_forest_supply_traceability.py`.
The `.tex` has **not** been edited. **Adopted decision (tracker §7):** `WOOD_FI1` represents Finland's captive industrial by-product stream (black liquor, bark, sawdust); its volume is the ENSPRESO `MINBIOWOOa` commodity, used as a documented proxy because black liquor is absent from ENSPRESO. All numbers are unchanged (no re-run). The snippets add the ENSPRESO-label caveat and keep the by-product wording.

**G1 — FI1 description** (Table `tab:fi_biomass_ladder`; the existing "black liquor, bark, sawdust" wording is retained, so you may only need the footnote G2).
```latex
\texttt{WOOD\_FI1} & Aggregate industrial wood by-products: black liquor, bark and sawdust (volume from ENSPRESO \texttt{MINBIOWOOa})\footnotemark & 11 & 10 \\
```

**G2 — FI1 footnote (the key addition: the ENSPRESO-label caveat and the black-liquor rationale).**
```latex
\footnotetext{Black liquor, bark and sawdust are the cheapest, largely captive wood-energy streams in Finland; black liquor alone reached 43~TWh in 2017, the single largest domestic wood-energy source \citep{statfin12vq}. Black liquor is not represented in the ENSPRESO database, so we take the volume of the cheapest ENSPRESO wood commodity, \texttt{MINBIOWOOa} (45~TWh, which ENSPRESO formally labels as stemwood chips and pellets \citep{ruizJRCEUTIMESModelBioenergy2015}), as a proxy for this by-product stream. The assigned cost (11~\euro/MWh) and embedded GHG (10~tCO$_2$eq/GWh) reflect captive mill-gate by-products; replacing this proxy with a physically grounded black-liquor/by-product split is left to forthcoming work coupling G4M and industrial-throughput data.}
```
*Check before pasting:* `\euro` availability; and that `\footnotemark`/`\footnotetext` sit correctly inside the table (or convert to a normal `\footnote` placed just after the table).

**G3 — bib entries** (add both to Zotero/`references.bib`).
```bibtex
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

---

### Quick checklist
- [ ] G1–G3 T1 corrected wording and JRC reference (needs your approval of the tracker §2.6 items; numbers pending T12/T13)
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
- [ ] E1–E6 style passes
