# Woody biomass: how it is allocated, and how material (non-energy) uses are handled

**Questions.** (1) Where does woody biomass go in the model? (2) The model covers energy use and non-energy demand (NED: chemicals such as HVC, methanol, ammonia), but forests also supply sawn timber, panels, pulp and paper, and construction. Is that competing use taken into account when the wood availability is set?
Evidence: model files, the nine canonical runs, [Paolo Thiran's thesis](../Data/exogenous_data/Paolo_Thiran_Thesis-v2.3-final.pdf), the JRC report behind ENSPRESO ([EUR 27575](./biomass%20potentials%20in%20europe_web%20rev.pdf)), S2BIOM. Sources are catalogued in [data_sources_register.md](./data_sources_register.md); flags in [FLAGS.md](../paper1/reviews_comments_flags_pathforward/FLAGS.md).

## 1. Short answer

1. **The model has no material use of wood.** There is no demand for sawnwood, panels, pulp, paper or construction timber, and no flow to them. The only non-energy demand is chemical feedstock (HVC, methanol, ammonia).
2. **Material use is taken into account only inside the ENSPRESO data**, as fixed "competing use" percentages that are deducted *before* the energy availability is computed (about 50% of stemwood and 60% of primary and secondary residues do not go to energy in the Medium scenario, 2030–2050). The model and the thesis then use the net value as is; nothing in the optimisation can trade energy against material use.
3. **S2 (ENS_Med) inherits that treatment.** S1 (+20%) scales an already-net S2 baseline; S3 (40 TWh) revises source-derived ENS_Low ceilings. Both inherit source deductions in their starting data, but neither recalculates competing material use consistently with its revised harvest narrative.
4. **Black liquor, bark and sawdust** (by-products of material production) are the part where the model and ENSPRESO differ most; see §5.
5. **In every run the largest single wood use is chemical feedstock (NED): 28.7 TWh, 27–75% of the wood layer** (§4).

## 2. What the model contains

- Demands: energy end-uses plus `NON_ENERGY` ([ESMC_model_AMPL.mod](../esmc/energy_model/ESMC_model_AMPL.mod) L128–147, L285–290), split into HVC, AMMONIA, METHANOL by `share_ned` (Finland: 93.04% / 3.06% / 3.90% of 12,581 GWh in 2035, `Data/2035/FI/Misc.json`).
- Supply: current future-run inputs have `WOOD_FI1`…`FI6` and `ENERGY_CROPS_2` feeding the single `WOOD` layer (`layers_in_out` = 1 in [Layers_in_out.csv](../Data/2035/00_INDEP/Layers_in_out.csv)). The nine canonical runs predate FI6 and contain FI1–FI5 only. Thiran thesis, printed p. 65–66: "woody biomass and second generation energy crops supply both the wood layer".
- Wood-consuming technologies: industrial, district and decentralised boilers; cogeneration (never built); `BIOMASS_TO_POWER`; `BIOMASS_TO_HVC` (2.381 GWh wood per GWh HVC); `BIOMASS_TO_METHANOL`; biodiesel/jet/LFO/gasoline and biomethane.
- Ammonia uses hydrogen routes, not a direct WOOD input. An indirect biomass-to-hydrogen contribution cannot be ruled out from this wood-layer summary alone.
- Thesis, printed p. 52–53: NED is built as three chemical feedstocks (HVC, methanol, ammonia) from Eurostat balances, Prodcom and trade data. It covers fossil feedstock replacement, not wood products.

## 3. How availability was set, and what that implies for material use

**Source.** Thesis, Table 1.14 (printed p. 67): "woody biomass" = ENSPRESO codes `MINBIOWOO`, `MINBIOWOOa`, `MINBIOWOOW1`, `MINBIOWOOW1a`, `MINBIOFRSR1`, `MINBIOFRSR1a`, ENS_Med scenario, aggregated from NUTS2 to national level. The thesis states no separate correction for material use; the only discussion of competing use (p. 134–135) is conceptual (energy versus recycling/composting, land for energy crops).

**What ENSPRESO deducts** (JRC EUR 27575, §4.2.1, printed pp. 24–25 and 37, Table 3; percentages read from the extracted table and to be verified against the PDF layout):

| Stream | "Competing use, % NOT going to energy": High / Medium / Low |
|---|---|
| Stemwood (roundwood, thinnings) | 45% (2020) → 23% (2050) / 52% (2020), 50% (2030), 47% (2040), 42% (2050) / 55% |
| Primary residues (logging residues, stumps, early thinnings) | 0% / 50% (2020), 60% (2030–2050) / 50% (2020), 60% (2030–2050) |
| Secondary residues: woodchips, sawdust | 0% / 50% → 60% / 50% → 60% (sawdust Low 70% → 90%) |
| Black liquor | 0% (estimated, but "endogenous" in JRC-EU-TIMES; not an input) |

Material use of stemwood is "taken from the EFI-GTM calculations used in EFSOS", and "the stemwood and residues not used for material products are then available for energy" (p. 37). The report also says stemwood is "mainly used for non-energy purposes" in the Medium case. Our repo statement "ENSPRESO reports energy-available potentials after deducting competing demand" ([biomass_scenario_mapping.md](./biomass_scenario_mapping.md) §3.3) is therefore **supported by the JRC report** for ENS_Low/Med/High; what is *not* in the workbook is the wording itself (flag T9).

**By scenario in this project**

| Scenario | Availability | Material use accounted for? |
|---|---|---|
| S2/NFS | ENS_Med 2035 (mean of 2030 and 2040) | Yes, through ENSPRESO Medium competing-use percentages, tied to the EFSOS reference storyline (roughly today's material production) |
| S1/BES | S2 × 1.20 on every step | **Inherited, not recalculated.** A stylised scaling of already-net S2 energy availability. Blattert's BES yields *less* roundwood and about the same total energy wood as NFS, so +20% is not what BES produces (documented in the mapping doc) |
| S3/BDS | ENS_Low 2030 revised by hand to 40 TWh (FI1 32.0, FI2 6.0, FI3 1.5, FI4 0.5) | **Qualitatively.** Revision A (2026-05-15) argues "competing industrial roundwood demand absorbs all harvest at the BDS ceiling"; the residue fraction (15–20%) and collection efficiency (30–40%) are expert values (T4). The ENS_Low raw values already embed a 55% stemwood deduction |

So the answer is: **yes, exogenously in the source data; S2 uses that net baseline, while S1 and S3 modify it without consistently recalculating material competition.** None represents endogenous timber/pulp/construction competition.

## 4. Where the wood goes in the nine runs

Reproduce: `python scripts/summarise_wood_allocation.py` (reads `paper1/results/*/Year_balance.csv` and `Resources.csv`). TWh/y.

| Run | FI1 | FI2 | FI3 | FI4 | Energy crops | **Wood layer** | NED (HVC + methanol) | Industrial heat | Decentralised heat | Biofuels / biomethane |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S1 unconstrained | 54.5 | 0 | 0 | 0 | 0 | 54.5 | 28.7 | 25.9 | 0 | 0 |
| S1 −95% | 54.5 | 19.6 | 0 | 0 | 0 | 74.2 | 28.7 | 25.4 | 0 | 20.0 |
| S1 −95% no nuclear | 54.5 | 45.9 | 0 | 0 | 7.8 | 108.2 | 28.7 | 35.5 | 15.6 | 28.4 |
| S2 unconstrained | 45.4 | 0 | 0 | 0 | 0 | 45.4 | 28.7 | 16.8 | 0 | 0 |
| S2 −95% | 45.4 | 28.7 | 0 | 0 | 0 | 74.2 | 28.7 | 25.5 | 0 | 20.1 |
| S2 −95% no nuclear | 45.4 | 38.2 | 12.5 | 0 | 7.8 | 104.0 | 28.7 | 34.2 | 12.4 | 28.7 |
| S3 unconstrained | 32.0 | 0 | 0 | 0 | 6.4 | 38.4 | 28.7 | 9.8 | 0 | 0 |
| S3 −95% | 32.0 | 6.0 | 1.5 | 0.5 | 7.8 | 47.8 | 28.7 | 19.1 | 0 | 0 |
| S3 −95% no nuclear | 32.0 | 6.0 | 1.5 | 0.5 | 7.8 | 47.8 | 28.7 | 19.1 | 0 | 0 |

Observations:
- **NED takes 28.7 TWh in all nine runs** (27.9 for HVC, 0.8 for methanol): 63% of the wood in S2 unconstrained, 75% in S3 unconstrained. It is a mandatory demand met by the cheapest route (wood at 11–33 €/MWh against oil and gas). The same pattern is reported by Colla et al. for Belgium (NED needs 54–57% of biomass at 90% GHG savings).
- **The wood layer is larger than the "domestic wood used" figure** of the paper (54.5 / 74.2 / 100.4 / 45.4 / 74.2 / 96.2 / 32.0 / 40.0 / 40.0 TWh) because second-generation energy crops (`ENERGY_CROPS_2`, 7.75 TWh available) also feed the wood layer: up to 7.8 TWh.
- **This probably explains flag A3**: S3 unconstrained industrial heat is 9.8 TWh = 32.0 + 6.4 (crops) − 28.7, which is the figure the paper quotes. The paper's "wood used" column should then say that energy crops are included or excluded explicitly.
- No district-heat wood boilers, cogeneration or power-only use of any significance in any run (DHN wood boilers ≤ 0.01 TWh).
- FI5 imports are used at most approximately 0.02 **GWh** (0.00002 TWh; numerically negligible).

## 5. Consequences and open issues

| ID | Issue | Why it matters | Possible handling (no decision taken) |
|---|---|---|---|
| W-1 | **No endogenous material use.** Energy wood is capped by exogenous net potentials; the model cannot let energy and material uses compete or move together. | The S1/S3 contrast is about energy only; real harvest policy changes sawlog and pulpwood volumes too. | Keep as a stated limitation (draft snippet for D7); or link to G4M assortments later |
| W-2 | **Industry demand is fixed while harvest changes.** Pulp, paper and sawmill energy demand sits inside the exogenous industry demand (JRC-IDEES boundary issues documented), but in S3 the by-products shrink by up to 46%. | S3 may overstate scarcity: with lower harvest the pulp/sawmill output and its energy demand would fall. S1 the opposite. | A demand scaling or a sensitivity; needs your decision |
| W-3 | **NED wood is a fixed block of 28.7 TWh (27–75% of the wood layer).** All Finnish HVC is bio-based in every run, including unconstrained, because wood is cheap. | It dominates the biomass story and competes with industrial heat; actual 2035 feedstock is largely fossil. | A sensitivity with HVC capped or fossil-forced; present as model result, not forecast |
| W-4 | **Black liquor and by-products are tied to pulp/sawmill throughput.** ENSPRESO treats secondary residues with 50–60% competing use and black liquor outside the model (0% competing use, but endogenous in JRC-EU-TIMES); our FI1 proxy carries black liquor at 11 €/MWh while the industry demand it serves is exogenous. | Consistency of the FI1 decision (T1) with the industry demand and with S2BIOM (S2B-1). | Decide S2B-1; obtain the EUwood/Biomass Futures black-liquor figures cited by the JRC report |
| W-5 | **Wood layer includes energy crops.** Reported "wood used" differs from the layer total. | Paper accounting (A3). | State it in the table; re-extract A3 |
| W-6 | **ENSPRESO competing-use percentages are tied to EFSOS storylines** (Low/Med/High), not to Blattert's NFS/BES/BDS. | Mapping S1/S2/S3 onto ENS_High/Med/Low mixes two different scenario families. | Disclose; S2BIOM UD5/UD6 offers an independent material-use-subtracted value |

## 6. S2BIOM as an independent check on material use

S2BIOM base stemwood is 157 TWh/yr (30.5 Mt dry matter, no material use deducted). Subtracting FAO roundwood for material use (UD5) leaves **48.5 TWh**; excluding pulp/paper/board roundwood from the subtraction (UD6) leaves **103.6 TWh**. These bracket the ENSPRESO stemwood-chips figure (`WOOD_FI1` = 45.4 TWh in S2) and show how strongly the answer depends on whether pulp roundwood is regarded as a material use. LHV assumptions as in `scripts/analyse_s2biom_finland.py` (assumed, not from S2BIOM).

## 7. Change log

| Date | Task | Files | Backup | Description | Status |
|---|---|---|---|---|---|
| 2026-10-12 | Material-use and allocation note | this file, `scripts/summarise_wood_allocation.py` | – | Evidence only; no model, data or run changed | done (uncommitted) |
