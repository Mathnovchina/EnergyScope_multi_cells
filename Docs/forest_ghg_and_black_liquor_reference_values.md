# Forest biomass reference values: GHG, black liquor and fuel conversions

**Purpose.** Collect reference values and their qualifications in one document: RED II (GHG factors), EUwood and Biomass Futures (black liquor and wood by-products), and VTT (LHV, density and moisture conversions). Published values and derived arithmetic are distinguished, with local copies and page references. **New reference files only; no calibrated input, model or run was changed.** Flags: [FLAGS.md](../paper1/reviews_comments_flags_pathforward/FLAGS.md); wider catalogue: [data_sources_register.md](./data_sources_register.md).

## 1. What is stored locally

| Folder | Files | Notes |
|---|---|---|
| [Data/exogenous_data/RED II/](../Data/exogenous_data/RED%20II) | Original OJ text (PDF, XHTML); consolidated 2023-11-20 (PDF) and 2024-07-16 (XHTML) | Retrieved 2026-10-12 from the Publications Office (Cellar); see its README |
| [Data/exogenous_data/EUwood_BiomassFutures/](../Data/exogenous_data/EUwood_BiomassFutures) | EUwood final report, EUwood methodology report, Biomass Futures D3.3 Atlas | Internet Archive captures of the original Commission/project sites; see its README |
| [Data/exogenous_data/Biomass_fuel_properties/](../Data/exogenous_data/Biomass_fuel_properties) | VTT Technology 272 (2016), reference-property CSV and retrieval README | Official Finnish fuel handbook; LHV, density and moisture bases detailed in §8 |

Citations (page numbers are printed pages unless stated):

- **RED II** — Directive (EU) 2018/2001 of the European Parliament and of the Council of 11 December 2018 on the promotion of the use of energy from renewable sources (recast), OJ L 328, 21.12.2018, pp. 82–209.
- **EUwood** — Mantau, U. et al. (2010). *EUwood – Real potential for changes in growth and use of EU forests. Final report.* 30 June 2010 (call TREN/D2/491-2008); and the companion *Methodology report* of the same date.
- **Biomass Futures D3.3** — Elbersen, B., Startisky [sic], I., Hengeveld, G., Schelhaas, M.-J., Naeff, H. (Alterra), Böttcher, H. (IIASA) (2012). *Atlas of EU biomass potentials. Deliverable 3.3*, Biomass Futures (IEE 08 653 SI2. 529 241), February 2012.
- **Also used:** JRC EUR 27575 (Ruiz Castello et al. 2015), local copy [biomass potentials in europe_web rev.pdf](./biomass%20potentials%20in%20europe_web%20rev.pdf); Colla et al. (2022), Front. Energy Res., local extract [_colla_extracted.txt](../Data/exogenous_data/Mypaper/_colla_extracted.txt).

Zotero status of these items is not verified (rule: cite only items present in the library).

## 2. RED II: what matters for this model

### 2.1 Rules (original text)

| Rule | Location | Content |
|---|---|---|
| Residue definition | Art. 2(43) | "a substance that is not the end product(s) that a production process directly seeks to produce" |
| Zero upstream for residues | Annex VI Part B, point 18 (OJ L 328/186 region) | "Wastes and residues, including tree tops and branches, straw, husks, cobs and nut shells, and residues from processing … shall be considered to have zero life-cycle greenhouse gas emissions up to the process of collection of those materials" |
| Fossil comparators for biomass fuels | Annex VI Part B, point 19 | electricity 183, heat 80 (124 where coal substitution is demonstrated), transport 94 g CO₂eq/MJ |
| Forest biomass sourcing | Art. 29(6), 29(7) | harvesting legality and sustainability criteria; LULUCF criteria (relevant to the missing forest-sink term, flag C1) |
| Values by pathway | Annex VI Part A (savings %), Part C (disaggregated), **Part D (total typical and default, g CO₂eq/MJ of fuel)** | Part D is on OJ L 328/195–196 |

### 2.2 Part D values relevant to wood (g CO₂eq/MJ of fuel, typical / default) and conversion

Conversion: 1 g/MJ = 3.6 tCO₂eq/GWh (the model unit `gwp_op_local` is ktCO₂/GWh, i.e. divide by 1000 again).

| Pathway | Distance | Typical | Default | t/GWh typical | t/GWh default |
|---|---|---:|---:|---:|---:|
| Woodchips from forest residues | 1–500 km | 5 | 6 | 18.0 | 21.6 |
| | 500–2,500 km | 7 | 9 | 25.2 | 32.4 |
| | 2,500–10,000 km | 12 | 15 | 43.2 | 54.0 |
| | > 10,000 km | 22 | 27 | 79.2 | 97.2 |
| Woodchips from stemwood | 1–500 km | 5 | 6 | 18.0 | 21.6 |
| Woodchips from industry residues | 1–500 km | 4 | 5 | 14.4 | 18.0 |
| | 500–2,500 km | 6 | 7 | 21.6 | 25.2 |
| Wood briquettes/pellets from forest residues, **case 3a** | 1–500 km | 6 | 7 | **21.6** | 25.2 |
| | 500–2,500 km | 6 | 7 | 21.6 | 25.2 |
| | 2,500–10,000 km | 7 | 8 | 25.2 | 28.8 |
| | > 10,000 km | 11 | 13 | **39.6** | 46.8 |
| Pellets from short-rotation coppice, poplar fertilised, case 3a | 1–500 km | 8 | 9 | **28.8** | 32.4 |
| Agricultural residues, density > 0.2 t/m³ | 1–500 km | 4 | 4 | **14.4** | 14.4 |
| Pellets from forest residues, case 1 / case 2a | 1–500 km | 29 / 16 | 35 / 19 | 104.4 / 57.6 | 126 / 68.4 |

Cases 1, 2a, 3a differ in the process fuel of the pellet mill (case 1 natural gas boiler; 2a wood-chip boiler; 3a wood-chip CHP; descriptions in Part C). The wood rows of Part D are identical in the consolidated version of 2024-07-16 (checked).

### 2.3 Check of the repo's GHG factors against the Directive text

Colla et al. (2022), Table 2 and notes a–c (local extract), take their footprints from RED II. Re-reading Annex VI confirms the chain:

| Model value (t/GWh) | Repo documentation says | What the Directive says | Verdict |
|---|---|---|---|
| FI2 22 (21.6) | "case 3a, ≤ 500 km, forest residues" | Pellets from forest residues, case 3a, 1–500 km, typical 6 g/MJ = 21.6 | ✅ matches (a pellet value; woodchips from forest residues are 5 typical / 6 default = 18.0 / 21.6) |
| FI5 40 (39.6) | "Colla, rest of world, good quality" | Pellets, case 3a, > 10,000 km, typical 11 g/MJ = 39.6 | ✅ matches; it is a long-distance value, conservative for Baltic/Nordic imports (6–7 g/MJ = 21.6–25.2) |
| FI3 14 (14.4) | "case 7a" | **No "case 7a" exists in Annex VI.** Colla's note b gives 14.4 for "landscape care and other solid biodegradable waste" and maps it to the category "Agricultural residues" (4 g/MJ). The same number is the typical value for **woodchips from industry residues, 1–500 km** (4 g/MJ) | ⚠️ value fine; the "case 7a" label in `Docs/biomass_supply_curve_fi.md` and the traceability doc is wrong |
| FI4 19 (18.7) | 60/40 blend of 21.6 and 14.4 | Blend of the two values above | ✅ arithmetic; blend weights are an assumption |
| FI1 10 | "≈ 50% of forest-residue baseline (21.6 × 0.5)" | 10 t/GWh = 2.8 g/MJ. Not a Directive value. Closest: woodchips from industry residues 4 g/MJ typical (14.4); residues have zero upstream emissions to the point of collection (Part B point 18) | ⚠️ judgement; lies between zero and 14.4. Black liquor is not a named pathway in Part D |

**Reading for the model.** Biogenic combustion CO₂ is not counted in any of these factors (the model follows RED II here), and RED II does not treat the forest carbon stock (that is Art. 29(7) and the LULUCF framework). That is the sink gap already flagged (C1).

## 3. EUwood

### 3.1 What it provides

Wood Resource Balance for the EU-27 (potential supply and demand by assortment) for 2010, 2020, 2030, scenarios A1 and B2, in **million m³ solid wood equivalent** (Mm³ swe); forest supply from EFISCEN under high/medium/low mobilisation. The JRC report builds its secondary-residue potentials on it (JRC EUR 27575 §4.2.2).

Conversion factors (EUwood final report, Table 1-1, p. 20): 1 Mm³ = 0.50 Modt = 8.72 PJ = 2.42 TWh. For **black liquor** the methodology report (§5.4.4, p. 141) gives a different energy density: 72 Mm³ = 432 PJ in the EU in 2005, i.e. **6.0 PJ/Mm³** (≈ 12 GJ per oven-dry tonne), with Finland about 144 PJ (≈ 40 TWh), Sweden 144 PJ, rest of Europe 144 PJ.

### 3.2 Finland fact sheet (Annex 1-13, p. 141), scenario A1, medium mobilisation (ME)

Million m³ swe; TWh at 2.42 TWh/Mm³ (generic factor), black liquor also at 1.67 TWh/Mm³ (6 PJ/Mm³).

| Potential supply | 2010 | 2020 | 2030 | TWh 2010 / 2020 / 2030 |
|---|---:|---:|---:|---|
| Stemwood, conifer (ME) | 51.6 | 50.6 | 46.9 | 125.0 / 122.6 / 113.6 |
| Stemwood, non-conifer (ME) | 9.3 | 11.9 | 14.4 | 22.5 / 28.8 / 34.9 |
| Forest residues C+NC (ME) | 13.2 | 14.0 | 14.1 | 32.0 / 33.9 / 34.2 |
| Bark C+NC (ME) | 2.6 | 2.7 | 2.6 | 6.3 / 6.5 / 6.3 |
| Landscape care wood | 2.1 | 2.4 | 2.7 | 5.1 / 5.8 / 6.5 |
| Sawmill by-products (POT) | 12.9 | 13.9 | 14.9 | 31.2 / 33.7 / 36.1 |
| Other industrial residues, reduced (POT) | 2.5 | 3.0 | 3.4 | 6.1 / 7.3 / 8.2 |
| **Black liquor (POT)** | **16.2** | **18.6** | **20.8** | **39.2 / 45.1 / 50.4** generic; **27.0 / 31.0 / 34.7** at 6 PJ/Mm³ |
| Solid wood fuels (POT) | 1.2 | 3.7 | 4.9 | 2.9 / 9.0 / 11.9 |
| Post-consumer wood (POT) | 1.2 | 1.3 | 1.5 | 2.9 / 3.1 / 3.6 |
| Total potential | 112.8 | 122.2 | 126.2 | |

| Demand | 2010 | 2020 | 2030 |
|---|---:|---:|---:|
| Sawmill industry | 25.9 | 27.8 | 29.8 |
| Veneer, plywood | 2.7 | 3.8 | 4.4 |
| Pulp industry | 38.8 | 45.0 | 51.1 |
| Panel industry | 0.9 | 0.9 | 0.9 |
| Other material uses | 0.2 | 0.2 | 0.3 |
| Producer of wood fuels | 1.2 | 3.7 | 4.9 |
| Forest-sector internal use | 18.4 | 20.9 | 23.2 |
| Biomass power plants | 10.2 | 8.9 | 13.5 |
| Households (pellets / other) | 0.5 / 5.4 | 1.5 / 5.7 | 1.7 / 5.2 |
| Liquid biofuels | 0.0 | 0.1 | 5.0 |
| Total | 104.1 | 118.5 | 140.0 |

Summary rows on the same sheet: forest woody biomass potential 77 / 79 / 78 Mm³ against material uses 68 / 78 / 86; other woody biomass 35 / 39 / 43 against energy uses 34 / 37 / 49 (2010 / 2020 / 2030). So in EUwood's Finland balance **material uses are about two-thirds of wood demand** (relevant to flag W-1).

### 3.3 Black liquor method (final report §5.5.4 p. 104; methodology §5.4.4 pp. 141–144)

- Black liquor [odt] = raw-material input − oven-dry pulp output, from FAOSTAT pulp production (2007 data), converted with Fonseca (2010) factors (chemical pulp 4.49, semi-chemical 2.67 m³/t), specific gravity 0.40–0.43 t/m³, pulp moisture 10%. Converted to Mm³ swe by dividing by specific gravity.
- "The entire volume is used internally in the pulp and paper industry"; "there is no unused black liquor as it arises and is used always within a single industrial process." EUwood therefore treats black liquor as **captive**, not as a freely dispatchable fuel.
- Finland shows about 8.0 Modt in 2010 (Biomass Futures Table 3.4, column "2010" taken from EUwood: 7,998 kt) = 16.0 Mm³ swe, consistent with the 16.2 Mm³ of the fact sheet.

## 4. Biomass Futures D3.3

### 4.1 Black liquor volumes (Table 3.4, printed p. 50)

Units as printed: tons (columns 1–3), and EUwood columns 4–6; final columns "Kton". Finland row:

| FAOSTAT | IIASA | Average (FAO, IIASA) | EUwood 2010 | EUwood 2020 | EUwood 2030 | Final 2020 | Final 2030 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 18,783 | 13,506 | 16,145 | 7,998 | 6,966 | 8,944 | 18,536 | 20,729 |

Text (p. 49): EUwood and IIASA "are generally underestimating the total black liquor production as estimated in the FAOSTAT"; the final potential is an average of IIASA and FAO, scaled with EUwood growth rates. Moisture/solids basis of the FAOSTAT tonnage is not stated.

### 4.2 Energy potentials (Table 3.5, printed p. 50, ktoe; 1 ktoe = 11.63 GWh), Finland

| Stream | 2010 | 2020 | 2030 | TWh 2010 / 2020 / 2030 |
|---|---:|---:|---:|---|
| Sawmill by-products (excl. sawdust) | 1,299 | 1,400 | 1,501 | 15.1 / 16.3 / 17.5 |
| Sawdust | 708 | 763 | 817 | 8.2 / 8.9 / 9.5 |
| Other industrial wood residues | 389 | 467 | 529 | 4.5 / 5.4 / 6.2 |
| **Black liquor** | **1,672** | **4,449** | **2,147** | **19.4 / 51.7 / 25.0** |

**Internal inconsistency in the source.** The implied energy density of black liquor is 4.3 GJ/t for 2010 and 2030 but 10.0 GJ/t for 2020 (ktoe divided by Table 3.4 kt), so the 2020 peak (and the EU-27 jump from 6,223 to 16,751 to 8,742 ktoe) looks like a unit or basis mix-up; the text says black liquor "is expected to decline towards 2030". Do not use the 2020 figure without checking.

### 4.3 Cost and GHG

- **Cost:** "Price assumed to be at 0 Euro/ton as BL is used immediately in pulp industry" (Annex 4, printed p. 87). Other prices for primary residues and roundwood derive from Lindner et al. (2005).
- **GHG (Annex 2, printed p. 81):** GEMIS 4.8 net upstream and downstream emissions per MJ of **heat output**: black liquor, liquid combustion, on-site process heat with flue-gas desulphurisation: 0.7 (2020) / 0.7 (2030) g CO₂eq/MJ = 2.5 t/GWh heat; primary forest residue chips in 1–5 MW heating plants 4.5–3.9; other industrial wood residues as pellets in small boilers 6.9–5.3. These are per MJ of heat, not per MJ of fuel, so they are not directly comparable with the RED II Part D values.

## 5. Synthesis: Finnish black liquor, all sources

| Source | Year | Value as published | TWh (my conversion) | Basis and caveat |
|---|---|---|---:|---|
| Statistics Finland 12vq | 2017 | 42,989 GWh | **43.0** | observed, energy statistics |
| EUwood methodology §5.4.4 | 2005 | 144 PJ | 40.0 | "about 144 PJ each" for Sweden, Finland, rest of Europe |
| EUwood fact sheet | 2010 / 2020 / 2030 | 16.2 / 18.6 / 20.8 Mm³ swe | 39 / 45 / 50 (generic 2.42 TWh/Mm³) or 27 / 31 / 35 (6 PJ/Mm³) | factor choice moves the result by 45%; the BL-specific 6 PJ/Mm³ is the one the report derives for black liquor |
| Biomass Futures Table 3.4 | 2010 / 2020 / 2030 | 16.1 / 18.5 / 20.7 Mt | 52 / 60 / 67 at 11.67 GJ/t (JRC Annex 5 LHV) | tonnage basis unstated; FAOSTAT alone 18.8 Mt (61 TWh), IIASA alone 13.5 Mt (44 TWh) |
| Biomass Futures Table 3.5 | 2010 / 2020 / 2030 | 1,672 / 4,449 / 2,147 ktoe | 19 / 52 / 25 | internally inconsistent (§4.2) |
| S2BIOM `4132` | 2012–2030 | 6.82 Mt dm | 24.6 at 13 GJ/t (assumed) | EUwood-like method (pulp × factor × 0.5) |
| ENSPRESO `MINBIOWOOa` (model `WOOD_FI1`) | 2030 / 2035 (S2) | 45.9 / 45.4 TWh | 45.4 | formally stemwood chips/pellets; excludes black liquor |

**Evidence versus interpretation.** Statistics Finland reports 43 TWh for 2017. EUwood describes captive use; Biomass Futures assumes 0 €/t at the mill, not a delivered market price. The other entries mix years, projected potentials, solid-wood equivalents, uncertain tonnage bases and assumed energy factors. They do **not** establish a validated 25–60 TWh range or a supply freely available to other technologies. In particular, the Table 3.4 conversions above are conditional arithmetic, not validated energy estimates: the mass unit and solids boundary remain uncertain. FI1's similar numerical magnitude does not validate its physical identity or cost. See §8.4 for the organic-mass versus total-solids distinction; S2B-1 remains an author decision.

## 6. Possible uses (proposals only; nothing applied)

| Option | Basis | Effect on the model | Needs |
|---|---|---|---|
| Keep FI1 as proxy; cite EUwood and Statistics Finland as supporting black-liquor magnitude, and RED II Part B point 18 for the zero-upstream treatment of residues | §3–§5 | none; footnote/snippet only | your approval of wording |
| Replace FI3's "case 7a" label by "RED II Annex VI, woodchips from industry residues (typical 4 g/MJ = 14.4 t/GWh)" | §2.3 | documentation only | – |
| Revisit FI1 GHG (10 t/GWh) with a matched fuel/pathway boundary | §2.3, §4.3 | new run | your decision; zero emissions up to collection does not mean zero total emissions, and 2.5 t/GWh heat is not a fuel-input factor |
| Explicit captive black-liquor resource (volume 43 TWh observed or EUwood-based, cost ≈ 0, captive-use restriction), with FI1 re-described as stemwood chips | §3–§5, S2B-1 | new runs, new patch files | your decision |
| Settle LHV and mass boundaries for each assortment, especially black liquor | §8 | none until applied | author selection; reconcile organic mass, total dry solids and firing moisture first |

## 7. Limitations of this note

- Page numbers for EUwood and Biomass Futures are printed pages from the Internet Archive PDFs; table values were read from extracted text and, for Biomass Futures Tables 3.4–3.5, checked against a rendering of the page.
- RED II Part D rows were read from the PDF text; the original and 2024 consolidated XHTML agree on the wood rows. Part C case descriptions were summarised, not re-tabulated.
- EUwood's detailed per-country black-liquor figure (Fig. 5-17) is a bar chart; only the table values above are quoted.
- Conversions are mine; factors used are named in each table.

## 8. LHV, density and moisture conversions: VTT Technology 272

### 8.1 Source qualification and reference values

**Alakangas, E., Hurskainen, M., Laatikainen-Luntama, J. and Korhonen, J. (2016).** *Properties of indigenous fuels in Finland*. VTT Technology 272, electronic ISBN 978-951-38-8455-0. [Official PDF](https://publications.vtt.fi/pdf/technology/2016/T272.pdf); [local collection and retrieval/hash record](../Data/exogenous_data/Biomass_fuel_properties/README.md); [machine-readable reference values](../Data/exogenous_data/Biomass_fuel_properties/VTT_272_reference_properties.csv).

This is a Finnish technical reference compilation, not a new harvest-potential database or a validation of S2BIOM. Printed page numbers below are followed by PDF page numbers where helpful. The values are reference ranges, **not adopted model parameters**. Bibliography checked locally; Zotero membership and redistribution licence remain unverified.

| Assortment | Dry-basis LHV (MJ/kg = GJ/t dm) | MWh/t dm (calculated) | Reference |
|---|---:|---:|---|
| Stemwood chips, whole-tree chips, logging-residue chips | 18.5–20.0 | 5.14–5.56 | Table 12.2, p. 195 (PDF 196) |
| Stump hog fuel | 17.2–20.9 | 4.78–5.81 | Table 12.2 |
| Sawdust | 19.0–19.2 | 5.28–5.33 | Table 12.2; Table 4.15, p. 62, also lists 18.9 for general sawdust and 19.0 for debarked pine |
| Plywood hog fuel | 19.0–19.2 | 5.28–5.33 | Table 12.2; not a blanket factor for all panel residues |
| Softwood bark | 18.5–20.0 | 5.14–5.56 | Table 12.2 |
| Birch bark | 21.0–23.0 | 5.83–6.39 | Table 12.2 |
| Wood pellets | 18.9–19.5 | 5.25–5.42 | Table 12.2 |
| Recovered wood | 18.6–20.7 | 5.17–5.75 | Table 4.59, p. 111 (PDF 112); quality/contamination dependent |
| Black liquor | **Not tabulated as LHV in the inspected Chapter 5 tables** | See §8.4 | Tables 5.2–5.3 report HHV, not LHV |

Dry basis here includes ash, unlike **dry ash-free** basis. The wet LHVs and energy densities in Table 12.2 are independently reported ranges, not pairs of matching endpoints. Some as-received entries appear anomalous (e.g. wood pellets 7.0–18.2 MJ/kg despite 6–9% moisture); use the explicit equation with matched inputs rather than importing every summary-table cell.

### 8.2 Solid volume, loose volume and basic density

VTT Table 4.17, p. 63 (PDF 64), gives oven-dry mass per green **solid** volume:

| Material | Basic density (kg dm/m³ solid) |
|---|---:|
| Pine / spruce / birch pulpwood with bark | 390 / 380 / 490 |
| Softwood sawing residue with bark | 415 |
| Pine / spruce stumps and roots | 475 / 435 |

S2BIOM D1.6's generic conifer/non-conifer factors (415/542 kg dm/m³) are separate aggregation conventions, not contradicted or replaced by these species-specific factors. Check whether future G4M volumes are over/under bark, green solid volume, dry volume or solid-wood equivalent.

Loose chip volume includes voids. VTT Table 4.28, p. 80 (PDF 81), reports whole-tree chip solid/loose ratios varying by species, chipper and season (for example pine 0.41–0.50, birch 0.38–0.50). These are observations for those chip categories, not a universal packing factor. Table 12.2 gives stemwood/logging-residue chip energy densities of 0.7–0.9 MWh/**loose** m³ at the reported moisture ranges. They cannot be compared directly to 1.5–2 MWh/**solid** m³.

### 8.3 Equations and checked examples

VTT §2.3.4, equation (2.5), p. 28 (PDF 29), uses wet-basis moisture **M in percent**:

```text
q_ar = q_d * (1 - M/100) - 0.02443 * M
```

Here `q_d` is dry LHV and `q_ar` is as-received LHV, both MJ/kg on their respective mass bases. With `w = M/100`, the same expression is `q_ar = q_d*(1-w) - 2.443*w`. Dry-basis moisture (water/dry mass) is different: convert it to wet basis before using this equation.

```text
Dry-reference energy (MWh) = dry tonnes * q_d / 3.6
Dry-reference energy (TWh) = kton dm * q_d / 3600
As-received energy (MWh) = wet tonnes * q_ar / 3.6
As-received energy (TWh) = kton dm * [q_d - 2.443*w/(1-w)] / 3600
Solid-volume energy (MWh) = m3 solid * rho_dm * [q_d - 2.443*w/(1-w)] / 3600
Cost (EUR/MWh) = cost (EUR/t dm) / energy (MWh/t dm on the same basis)
```

`rho_dm` is kg dry matter per m³ solid; the solid-volume equation is VTT equation (2.6), p. 29, combined with (2.5). Loose volume additionally needs a matched solid/loose ratio, or use measured wet bulk density with `q_ar`. These are fuel-input energies, not useful heat; conversion efficiency is a separate step.

**Illustrative arithmetic, not parameter selections:**

- 1,000 kton dm at 19 GJ/t dm = **5.278 TWh dry-reference energy**.
- The same dry mass at 50% wet-basis moisture has `q_ar = 8.2785 MJ/kg wet`, 2 tonnes wet per tonne dry, and **4.599 MWh/t dm** after moisture evaporation.
- At 415 kg dm/m³ solid, these inputs give **2.190 MWh/m³** on the dry-reference basis, or **1.909 MWh/m³** with 50% moisture. At an illustrative packing ratio 0.45, the latter is **0.859 MWh/m³ loose**.
- A hypothetical 40 EUR/t dm cost becomes **7.58 EUR/MWh** on the dry-reference basis or **8.70 EUR/MWh** on the wet-fuel energy basis. The cost boundary remains road-side if the original cost is road-side.

Thus T5 cannot be closed by selecting one universal MWh/m³ factor: species, assortment, moisture and volume basis must be recorded.

### 8.4 Black liquor: HHV is not LHV; organic residue is not total dry solids

VTT Table 5.2, p. 114 (PDF 115), reports **gross** calorific values of total dry liquor solids: softwood typical 14.2, range 13.3–14.8 MJ/kg; hardwood typical 13.5, range 13.0–14.3. The fired liquor has approximately 75–85% dry solids in modern Finnish recovery boilers (p. 113). Do not enter these HHVs directly into an LHV-based resource balance.

For a transparent **derived illustration**, applying VTT equation (2.4), p. 27, to Table 5.2's typical HHVs and Table 5.4's typical elemental compositions (p. 115) gives:

```text
q_d = HHV_d - [212.2*H_d + 0.8*(O_d + N_d)]/1000
Pine: 14.2 - [212.2*3.6 + 0.8*(33.9+0.1)]/1000 = 13.409 MJ/kg dry solids
Birch: 13.5 - [212.2*3.3 + 0.8*(35.5+0.2)]/1000 = 12.771 MJ/kg dry solids
```

Element contents are weight percentages. These are calculations from typical values, not measured LHV values or a calibrated uncertainty interval. Recovery-boiler chemical reactions and the chosen energy-accounting convention warrant checking before adoption.

More importantly, Chapter 5 distinguishes wood-derived organic matter from cooking chemicals. Table 5.1 gives typical organic/inorganic mass shares 67/33%; Tables 5.2 and Figure 5.1 instead describe approximately 50% ash-forming solids. **Ash yield is not interchangeable with the initial inorganic fraction.** Neither fraction should be used as an automatic correction factor for another database.

EUwood estimates organic oven-dry residue from roundwood input minus pulp output; S2BIOM's pulp/wood-factor method likewise needs its dry-mass boundary checked. Multiplying an organic-only residue estimate by an LHV per tonne of **total** liquor solids would mix denominators. The JRC 11.67 GJ/t and EUwood equivalent-volume factors do not resolve that discrepancy. A Finnish observed energy series can benchmark magnitude, but cannot alone establish a tonnes-to-energy conversion.

### 8.5 Implications for the existing S2BIOM script

The constants in [analyse_s2biom_finland.py](../scripts/analyse_s2biom_finland.py) remain **unchanged**: wood 18.5, bark 19, black liquor 13, recovered wood 16 GJ/t dm. No model CSV, patch or run has been regenerated.

- 18.5 for chips is at the lower end of VTT's range; it is not a validated single factor for sawdust, panel residues and stumps.
- 19 for bark fits softwood references, but not birch bark; species mix is needed.
- 13 for black liquor is numerically close to the derived illustrations above, but its compatibility with S2BIOM's mass denominator remains unresolved.
- 16 for recovered wood is below VTT Table 4.59's range and is **not validated by this source**.

The existing S2BIOM TWh and EUR/MWh outputs therefore remain provisional. Adoption of assortment-specific values, firing moisture or sensitivity ranges requires author approval. Availability already published in energy units by ENSPRESO should not be converted a second time.

## 9. Change log

| Date | Task | Files | Backup | Description | Status |
|---|---|---|---|---|---|
| 2026-10-12 | RED II and EUwood/Biomass Futures retrieved and summarised | `Data/exogenous_data/RED II/*`, `Data/exogenous_data/EUwood_BiomassFutures/*`, this file | – | New reference files only; no model, patch or run changed | done (uncommitted) |
| 2026-10-12 | LHV/density/moisture evidence | `Data/exogenous_data/Biomass_fuel_properties/*`, this file | New reference files; existing note uncommitted | VTT source and qualified CSV; equations checked; black-liquor HHV/mass-boundary caveats; no numerical assumptions adopted | done (uncommitted) |
