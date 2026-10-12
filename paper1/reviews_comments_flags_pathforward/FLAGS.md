# Flags register — Paper 1 review, forest supply audit and path forward

**Single source of truth for every open or closed flag.** Consolidated 2026-10-12 from three overlapping documents (see §7). Paste-ready LaTeX lives in [SNIPPETS_overleaf.md](./SNIPPETS_overleaf.md) (author-owned Overleaf rule, [AGENTS.md](../../AGENTS.md) §7). Evidence and derivations stay in their topic files and are linked, not copied.

**Rules in force:** no change to `.mod`, `Data/`, `calibration/patches/` or any run under `case_studies/` without explicit approval; `.tex` files are never edited by the agent.
**IDs are unchanged** from the earlier documents (A, B, C, E = paper review; T = supply-curve audit) so that old references still resolve. New flags from the S2BIOM benchmark are `S2B-n`.

**Status:** 🔴 open · 🟠 in progress · 🟡 awaiting your decision/action · 🟢 closed · ⚪ info
**Severity:** H high · M medium · L low

---

## 1. Dashboard — everything still open, by area

### 1.1 Supply curve and forest data (model inputs)

| ID | Sev | Status | Issue | Next step | Needs |
|---|---|---|---|---|---|
| **S2B-1** | H | 🟡 | S2BIOM gives an independent energy-available stemwood figure (UD5, material use subtracted) of **≈48.5 TWh**, close to `WOOD_FI1` = 45.4 TWh (S2). That matches the literal ENSPRESO label (stemwood chips) and is consistent with the [§3 decision](#3-decisions-log) only if FI1 is explained as a proxy for by-products *and* stemwood. S2BIOM by-products are a separate **58 TWh** (black liquor 24.6, sawmill 21.2, bark 9.0, panels 3.2; LHV assumed). | Decide whether the T1 wording stays as is, or FI1 is described as stemwood chips with black liquor/by-products carried elsewhere (see [§5](#5-path-forward)) | You |
| **S2B-2** | M | 🟠 | Black liquor: S2BIOM 6.8 Mt dm gives **24.6 TWh only under the assumed 13 GJ/t**; Statistics Finland reports **43 TWh** in 2017. S2BIOM uses pulp × roundwood factor × 0.5 (D1.6 p110), with cost assumed zero at mill gate (p118). VTT's derived LHV illustrations concern total liquor solids, not necessarily S2BIOM's organic-only estimate. | Reconcile mass/energy boundaries and years before treating S2BIOM as a lower benchmark; see S2B-6/W-4 | Source-boundary check and decision |
| **S2B-3** | M | 🟠 | Residues + stumps: S2BIOM BASE **21.6 TWh** (≈ ENSPRESO ENS_Low FI2 20.7), HIGH **68.9 TWh**, TECH **97.2 TWh**. S2BIOM HIGH is a sourced, much tighter upper bound than ENS_High (124 TWh, rejected) and could replace the stylised +20% of S1 (FI2 45.9). | Decide whether to use S2BIOM as the S1 upper bound / S3 floor benchmark | You |
| **S2B-4** | M | 🟠 | Costs: S2BIOM road-side cost (harvest + chipping, EUR 2012, **no stumpage, profit, overhead or transport**) is ≈6.6–7.5 EUR/MWh stemwood final felling, 13–16 thinnings, 5–10.6 residues, 9.7–10.6 stumps (LHV assumed). It is a floor, not a delivered cost; it adds a thinning-vs-felling gradient the model lacks. | Use as lower bound/shape in the cost-source table of T2 | – |
| **S2B-5** | M | 🔴 | S2BIOM cannot benchmark S3 (−46%) or S1: stemwood is identical in TECH/BASE/HIGH, and the harvest-reduction options UD1–UD4 cut only 5–10%. Deep conservation cuts remain judgement (T4) until G4M data arrive. | Keep T4 open; ask IIASA for harvest-intensity scenarios | IIASA data |
| **S2B-6** | L | 🟠 | **Reference evidence obtained:** VTT Technology 272 gives dry chip LHV 18.5–20 MJ/kg, assortment/species differences, density and moisture equations; see [reference-values note §8](../../Docs/forest_ghg_and_black_liquor_reference_values.md#8-lhv-density-and-moisture-conversions-vtt-technology-272). Existing script constants unchanged. Recovered wood 16 is not validated by VTT; black-liquor tables give HHV of total solids, while S2BIOM's organic-mass basis needs reconciliation. | Approve assortment-specific energy/mass/moisture conventions before regenerating S2BIOM energy and cost outputs; T5 stays open | Decision |
| **W-1** | H | 🟡 | No endogenous material wood use; ENSPRESO deducts competing uses exogenously. S2 inherits this; S1 scales that already-net baseline, and S3 revises source-derived ceilings, without recalculating material competition consistently. Neither means competing use was absent from the starting data. | State as limitation (D7 snippet); decide if material-use consistency needs a sensitivity. See [woody_biomass_material_use_and_allocation.md](../../Docs/woody_biomass_material_use_and_allocation.md) | You |
| **W-2** | M | 🟡 | Industry (pulp, sawmill) energy demand is fixed across scenarios while by-product supply changes with harvest (S3 −46%, S1 +20%). | Decide: demand scaling, sensitivity, or disclose | You |
| **W-3** | M | 🟡 | NED takes 28.7 TWh of wood in all nine runs (27–75% of the wood layer); all HVC is bio-based even unconstrained. | Sensitivity (HVC capped/fossil) or disclose as model result | You |
| **W-4** | M | 🟠 | Black liquor/by-products tied to pulp throughput. EUwood/Biomass Futures figures obtained; observed 43 TWh in 2017. Their differing years, uncertain mass bases and conversion conventions do not establish a validated 25–60 TWh range. EUwood describes captive use; Biomass Futures assumes 0 €/t, with Table 3.5 inconsistent for 2020. VTT distinguishes total liquor solids from organic residue. Details in [reference-values note](../../Docs/forest_ghg_and_black_liquor_reference_values.md) §5/§8.4. | Reconcile denominators; decide S2B-1 and FI1 options (§6) | You |
| **W-5** | L | 🟠 | The WOOD layer includes `ENERGY_CROPS_2` (up to 7.8 TWh), so layer totals (e.g. S3 −95% 47.8) exceed the paper's "domestic wood used" (40.0). | State in the paper's table | – |
| **W-6** | L | 🟠 | ENSPRESO Low/Med/High (EFSOS storylines) are mapped onto Blattert NFS/BES/BDS: two scenario families mixed. | Disclose | – |
| **S-PY** | M | 🔴 | Price years mixed and undocumented (IEA WEO 2020, DEA catalogue, ENSPRESO €2010, S2BIOM €2012, "IEA 2022"). | Choose a base year and document | You |
| **S-RED** | L | 🟠 | RED II text is now in the repo (`Data/exogenous_data/RED II/`). Chain verified against Annex VI Part D: FI2 21.6 and FI5 39.6 = pellets case 3a (typical 6 and 11 g/MJ); FI3 14.4 = industry-residue woodchips / agricultural residues (4 g/MJ). **Wrong label:** "case 7a" does not exist. FI1 (10 t/GWh = 2.8 g/MJ) is a judgement; residues have zero upstream emissions to collection (Part B pt 18). See [forest_ghg_and_black_liquor_reference_values.md](../../Docs/forest_ghg_and_black_liquor_reference_values.md) | Correct the "case 7a" wording in docs; decide FI1 GHG (options in that doc §6) | You |
| **S2B-7** | L | ⚪ | Data limits: early thinnings (1115, 1121/1122) are absent from the Finnish sheet; industrial streams have identical TECH/BASE; forest costs are held constant 2012–2030; UD5 can go negative elsewhere (not Finland); D1.6 and D1.8 disagree on UD2. | Carry as caveats | – |
| **S2B-8** | ⚪ | ⚪ | Opportunity: 19 NUTS3 regions × 2012/2020/2030 would support a regional split (multi-cell) and a benchmark for the G4M output. | Decide with the G4M coupling plan | You |
| T2 | M | 🟠 | Costs are modelling assumptions without traceable sources (FI1 11 vs ENSPRESO 34.7; FI3 27 vs ~7; FI4 33 vs ~12–17). FI2 22 matches the observed chip price. | Cost-source table with price year; optional sensitivity; add S2B-4 | – |
| T3 | M | 🟠 | Unconstrained results hinge on the FI1 ceiling alone. | State in discussion; optional FI1 ±X% sensitivity | Decision on a run |
| T4 | M | 🟠 | S3 FI1/FI3/FI4 cuts are judgement (FI1 −26% vs harvest −37%); FI2 = 6.0 TWh sits at the top of the sensitivity grid; residue fraction (15–20%) and collection efficiency (30–40%) lack sources. | Document the grid or replace by G4M (see S2B-5) | Decision |
| T5 | M | 🟠 | VTT now provides sourced conversion equations, LHV and density references. Historical 1.5 vs ~1.96–1.98 MWh/m³ factors still lack matched moisture, assortment and solid/loose-volume bases. No universal conversion factor is justified. | Record G4M volume boundary and approve matched species/assortment/moisture inputs (S2B-6) | Decision / G4M metadata |
| T6 | M | 🔴 | `BIOMASS_RESIDUES` is 4,985 GWh in all 9 runs vs 6,600/4,985/3,400 in docs and CSVs. | Correct docs/paper, or a new timestamped run | Decision |
| T7 | M | 🟠 | Stale docs and run labels (old GHG in `biomass_supply_curve_fi.md` §4, +20% cap 132.97 vs 121.9, run descriptions "Biodiversity Enhancement"). `run_metadata.json` is read-only evidence. | Fix the remaining stale tables | – |
| T9 | L | 🟠 | Quote "after deducting industrial demand" is supported by JRC EUR 27575 (printed p. 25, 37); Luke figures still unsourced. | Add Luke table/PDF to Zotero | Luke file |
| T11 | ⚪ | 🔴 | S3 uses 2030, S1/S2 use 2035. | Mention in methods | – |

### 1.2 Paper numbers and text (author-owned `.tex`)

| ID | Sev | Status | Issue | Next step |
|---|---|---|---|---|
| A1 | H | 🔴 | `\citet{moret_strategic_2017}` undefined; correct key `moretStrategicEnergyPlanning2017`. | Snippet D1 |
| A2 | H | 🔴 | "Three times greater than in S1" is wrong. Nuclear-removal penalties: S1 0.02, S2 0.10, S3 0.34 bn€/y → S3 ≈3× S2, ≈17× S1. Two occurrences. | Snippet D2 |
| A3 | H | 🟠 | S3 unconstrained residual industrial heat: wood 32.0 − 28.7 = 3.3 TWh, not 9.8. **Probable explanation (2026-10-12):** the WOOD layer also takes 6.4 TWh of `ENERGY_CROPS_2` in that run, so the run gives 32.0 + 6.4 − 28.7 = 9.8 and the paper's figure is right; see W-5. | Confirm and state "including energy crops" in the table/text |
| A4 | M | 🔴 | Duplicated paragraph introducing Fig. `fi_2035_biomass_allocation`. | Merge or delete one |
| A5 | M | 🔴 | DHN model value: paper 52.33 TWh (+43.4%) vs justification doc 52.96 TWh (+45.1%). | Reconcile run/number |
| B.1 | M | 🔴 | 2017 table: CHP 20.73 vs audit 25.0; imports 20.43 vs 20.3; gas power model 4.34/4.37/4.38; DHN see A5. | Reconcile |
| B.2 | M | 🔴 | Re-check every 2035 matrix and allocation number against the run CSVs (cost 22.40–23.90, CO₂, wood used, fossil imports 46–47 → ~8 TWh, allocation figures). Internal consistency passed except A2/A3. | Re-extract |
| B.3 | M | 🔴 | Literature numbers to confirm: forests 75% / wood 25% of primary energy; Mönkkönen 96% **denominator** (max economically sustainable harvest, not mean annual increment) and "southern Finland"; EU BDS −48% and 50–73% leakage; Czech salvage 92%, 25.5 Mm³, €1.12 bn; Beringer 126–216 EJ; Colla BE 30–90 TWh and EU27+UK 2000–2500 TWh; Recka <1.5 pp. | Verify against Zotero items |
| T8 | L | 🟡 | Capacity table totals should read 121.9 / 101.6 / 40.0. | Snippet G4 |

### 1.3 Caveats to add to the paper

| ID | Caveat | Snippet |
|---|---|---|
| C1 | No forest sink/LULUCF/HWP in the GHG constraint (energy combustion CO₂ only). Biggest limitation. | D3 |
| C2 | Biogenic combustion CO₂ = 0; only supply-chain GHG (RED II) charged. | D3 |
| C3 | Peat modelled as coal. | D4 |
| C4 | 2017 uses `relax_co2`; not carried into 2035. | D4 |
| C5 | Discount rate (1.5%) and lifetimes not stated. | D5 |
| C6 | 2035 demand projection method undocumented. | D6 (TODO) |
| C7 | Single node (no intra-Finland spatial detail). | D7 |
| C8 | S1 (+20%) and S3 (40 TWh) are stylised/audited: repeat in results and figure footnotes. | – |
| C9 | EUD parameters are 2020-based but drive the 2017 validation. | D6 |
| T1 caveat | ENSPRESO formally labels `MINBIOWOOa` as stemwood chips/pellets; black liquor absent from ENSPRESO. | G1–G3 |

Also add: D7 limitations subsection, D8 validation-strength sentence (confirm 1.2%/14 indicators), D9 S3 scaling chain.

### 1.4 Style and consistency

| ID | Issue |
|---|---|
| E1 | Two Luke keys: `Luke2025ForestTrade` (figure) vs `lukeWoodEnergy2024` (table): intentional? |
| E2 | CO₂ notation mixed (`\ce{CO2}` vs `CO$_2$`). |
| E3 | `\cite{...}'s` constructions: use `\citet`. |
| E4 | `moretCharacterizationInputUncertainties2017` and `...2017a` both in bib: duplicate? |
| E5 | Cite the 1.2% weighted validation figure so it is not buried (D8). |
| E6 | Say that single-cell ESMC reduces to the EnergyScope TD formulation. |

### 1.5 Closed

| ID | Resolution |
|---|---|
| T1 | 🟢 by decision 2026-10-08 (see §3). **Re-examined by S2B-1.** |
| T10 | 🟢 ENS_Low/Med/High forestry = EFISCEN under EFSOS High/Medium/Low, material use from EFI-GTM; BaU = CBM + GFTM (JRC EUR 27575 §4.2.1, printed pp. 35–37). |
| T12 | 🟢 under the by-product reading FI1 cost 11 and GHG 10 are defensible; residual FI3 27 vs ENSPRESO ~7 (disclosed). |
| T13 | 🟢 S3 FI1 −26% valid under the by-product reading. |
| T14 | 🟢 black liquor carried by the FI1 proxy, kept and disclosed (option C). Strengthened by S2B-2 context. |

---

## 2. Reference tables (stable facts used by the flags)

**Model ladder (canonical runs; `Data/2035/FI/Resources_S*.csv`).**

| Step | ENSPRESO code | S1 / S2 / S3 (GWh) | Cost €/MWh | GHG t/GWh |
|---|---|---|---:|---:|
| FI1 | `MINBIOWOOa` | 54,530 / 45,442 / 32,000 | 11 | 10 |
| FI2 | `MINBIOFRSR1` | 45,857 / 38,214 / 6,000 | 22 (26 in S3) | 22 |
| FI3 | `MINBIOWOOW1` + `W1a` | 15,052 / 12,543 / 1,500 | 27 | 14 |
| FI4 | `MINBIOWOO` + `MINBIOFRSR1a` | 6,504 / 5,420 / 500 | 33 | 19 |
| FI5 | market import | unlimited, never used | 70 | 40 |

Full derivation: [forest_supply_curve_methodology_traceability.md](../../Docs/forest_supply_curve_methodology_traceability.md). Re-run the audit: `python scripts/check_forest_supply_traceability.py`.

**S2BIOM national totals, Finland, 2020, TWh/yr (LHV assumed: wood 18.5, bark 19, black liquor 13 GJ/t dm).** Reproduce: `python scripts/analyse_s2biom_finland.py`.

| Stream | TECH | BASE | HIGH | UD5 (material use subtracted) |
|---|---:|---:|---:|---:|
| Stemwood (final fellings + thinnings) | 157.0 | 157.0 | 157.0 | 48.5 |
| Logging residues | 54.3 | 12.2 | 47.0 | 12.2 |
| Stumps | 42.9 | 9.4 | 21.9 | 9.4 |
| Sawmill residues | 21.2 | 21.2 | – | – |
| Panel / further processing residues | 3.2 | 3.2 | – | – |
| Bark | 9.0 | 9.0 | – | – |
| Black liquor | 24.6 | 24.6 | – | – |
| Post-consumer wood | 2.7 | 1.5 | – | – |

Potential definitions, modelling basis (EFISCEN, 50-year rolling maximum, FAWS, LPJmL climate scaling), cost basis and by-product method are summarised from D1.6/D1.8 in [§4](#4-s2biom-data-set-what-it-is).

---

## 3. Decisions log

| Date | Decision | Consequence |
|---|---|---|
| 2026-10-08 | **T1 — `WOOD_FI1` kept as an aggregate industrial by-product proxy** (black liquor, bark, sawdust) with the ENSPRESO `MINBIOWOOa` volume; ENSPRESO-label caveat disclosed; cost 11 €/MWh and GHG 10 t/GWh retained as documented hypotheses; no re-run. | Closes T1/T12/T13/T14. Reasons: black liquor (43 TWh, 2017) is Finland's largest wood-energy source and absent from ENSPRESO; FI1 volume ≈ black liquor magnitude; cost, GHG and S3 response are consistent under that reading; 11 €/MWh is conservative vs a ~2–3 €/MWh blend. FI3 (12.5 TWh) is the literal ENSPRESO by-product code and cannot carry black liquor. Carry to IIASA: *replace the proxy with a physically grounded black-liquor/bark/sawdust/stemwood-chip split, including a captive-use restriction.* |
| 2026-10-08 | ENS_High rejected for S1 (FI2 = 124 TWh, ~5× plausible); S1 = S2 × 1.20 as a stylised upper-bound sensitivity. | S2B-3 offers a sourced alternative (S2BIOM HIGH 68.9 TWh). |
| 2026-05-15 | S3 hand-revised from ENS_Low 2030 (74.2 TWh) to 40.0 TWh (three-way audit: Luke 2024, Mönkkönen ceiling, competing demand). | Judgement (T4); S2B-5. |

**T1 evidence (JRC EUR 27575, Ruiz Castello et al. 2015).** `MINBIOWOOa` = "Woodchips and pellets" from additionally harvestable stemwood (printed p. 17; cost column "Roundwood Chips & Pellets", p. 56); sawmill chips and sawdust are `MINBIOWOOW1`/`W1a` = FI3 (p. 17, 39); black liquor is not an input, "endogenous in JRC-EU-TIMES" (footnote 6, p. 15); material use is deducted before energy availability (pp. 25, 37). Full dossier and the superseded alternative (T12/T13 run plan) are retained in the earlier tracker, [forest_supply_flags_tracker.md](../../Docs/forest_supply_flags_tracker.md), now a pointer plus that history.

---

## 4. S2BIOM data set — what it is

Files in `Data/exogenous_data/S2biom/` (read-only inputs): `data_FI.xlsx` (Finland country file), D1.1 roadmap, D1.6 methods and data sources, D1.8 atlas of regional cost-supply.

- **Content:** supply in kton dry matter by NUTS3 (19 Finnish regions) for 2012/2020/2030 and potentials TECH, BASE, HIGH, UD01–UD08; road-side cost (EUR/t dm, base potential only) for primary forest and agricultural types. Codes: 1111–1114 stemwood (final fellings/thinnings, non-conifer/conifer), 1211–1214 logging residues, 1221–1222 stumps, 4111–4122 sawmill/panel residues, 4131 bark, 4132 black liquor, 5211–5212 post-consumer wood.
- **Potentials:** TECH = maximum stemwood harvested annually over 50-year periods on forest available for wood supply (protected areas excluded), residues limited only by recovery rate; HIGH = TECH with less stringent residue/stump constraints; BASE = site-productivity, soil, water, biodiversity (Natura 2000) and bearing-capacity constraints on residues and stumps (logging-residue recovery 70%; stumps conifer only, 33% on poor soils); stemwood is identical in TECH/BASE/HIGH. UD1 FAWS −5%; UD2 adds retained trees +5%; UD3 no stumps; UD4 = UD2 + UD3; UD5 subtracts FAO roundwood for material use from BASE; UD6 as UD5 but excluding pulp/paper/board roundwood; UD7/UD8 apply UD5/UD6 to UD4. Residues unchanged in UD5–UD8.
- **Forest supply model:** EFISCEN (v3.1.3/4.1), National Forest Inventory (Finland 2004–2008), FAWS static to 2030, LPJmL net-primary-production scaling of increment (SRES A1b), harvest reduced in 2.5% steps until feasible; disaggregated to NUTS3 with species maps (D1.6 pp77–81). 2012/2020/2030 differ only slightly (BASE −2.1% to 2030, D1.8 p36).
- **Cost basis:** activity-based; harvester + forwarder + roadside chipper (stemwood, residues), excavator + forwarder + grinder (stumps); Finnish machine and labour costs; EUR 2012; **excludes wood production (stumpage), profit, overheads and transport to the plant**; held constant to 2030 (D1.6 pp22–25, 83–94). The `rs_cost` sheet's EUR/t dm is consistent with the atlas maps in EUR/m³ (38.6 EUR/t × 0.415 t/m³ ≈ 16 EUR/m³).
- **By-products:** production × recovery ratios (FAOSTAT 2010–2014); black liquor = pulp × roundwood factor (chemical 4.49 m³/t) × 0.5; bark 10% of roundwood × 80.1% forest share (FI/SE); cost zero at mill gate; TECH = BASE (D1.6 pp97–118).
- **Finland totals (D1.8):** stemwood 30.2/30.6/29.9 Mt dm (2012/2020/2030), 70.7 Mm³ in 2012; residues + stumps 4.0/4.2/4.4 Mt dm; wood industry 13.2 Mt dm.
- **Limits stated by the authors:** one chain and productivity model per assortment; labour costs from Eurostat sector averages; no Finland-specific validation found; pulp-and-paper validation shows "a huge difference" (D1.6 pp116–117).

---

## 5. Path forward

Backlog from [AGENTS.md](../../AGENTS.md) (all need approval before model/data edits): `co2_forest_sink` prototype, S0 sink-max scenario, G4M → `WOOD_FI1…FI4` mapping, disturbance-shock scenario.

**Decisions needed from the S2BIOM benchmark** (none applied):

1. **FI1 identity (S2B-1).** (a) keep the by-product proxy wording as adopted, adding the S2BIOM cross-check as a footnote-level benchmark; (b) re-describe FI1 as stemwood chips (UD5 supports the volume) and give black liquor/by-products a separate explicit resource later (needs new runs); (c) defer to IIASA/G4M.
2. **Upper/lower bounds for FI2 (S2B-3).** keep S1 = S2 × 1.20; or cite S2BIOM HIGH as a sourced bound in the paper without changing runs; or a new S1 variant (new run, new patch file).
3. **LHV basis (S2B-6, T5).** choose and source one dry-basis LHV set and moisture convention.
4. **Cost table (T2, S2B-4).** build a cost-source table (model vs ENSPRESO vs S2BIOM road-side) for the paper or supplement.
5. **Regionalisation (S2B-8).** whether NUTS3 S2BIOM data should feed the multi-cell or G4M comparison.

---

## 6. Source map (claim → repository ground truth)

| Paper element | Verify against |
|---|---|
| 2017 "Actual" column | `calibration/reality/finland_2017_reference.csv`; `Docs/finland_2017_reality_reference_audit.md` |
| 2017 model values, 1.2% / 14 metrics, DHN and gas-CHP residuals | `Docs/finland_2017_validation_justifications.md` |
| 41,200 ktCO₂ baseline, −95% = 2.06 Mt, "~69%" | `Docs/finland_2035_ghg_sweep_results.md` |
| Biomass ladder costs/GHG | `Data/2035/FI/Resources_S{1,2,3}_*.csv`; `Docs/biomass_supply_curve_fi.md` |
| Step capacities (121.9 / 101.6 / 40.0 TWh) | same CSVs; `Docs/biomass_scenario_mapping.md` |
| S3 three-way audit (74.2 → 40 TWh) | `Docs/biomass_scenario_mapping.md` §3.5.1 |
| Mönkkönen 96% / 58–60% (Southern Finland) | `Docs/biomass_scenario_mapping.md` §1.2 |
| 2035 matrix (cost / CO₂ / wood / allocation) | run outputs under `case_studies/FI/forest_scenarios_2035/` |
| Disturbance literature figures | `Docs/literature/forest_disturbance_timber_economics_report.md` |
| No-sink / LULUCF gap | `AGENTS.md` §5; `Docs/concept_note_G4M_forest_energy_finland.md` §2 |
| S2BIOM numbers | `scripts/analyse_s2biom_finland.py` on `Data/exogenous_data/S2biom/data_FI.xlsx`; PDFs D1.6, D1.8 as cited |
| Source catalogue and qualification | [data_sources_register.md](../../Docs/data_sources_register.md) |
| RED II values, EUwood and Biomass Futures black liquor | [forest_ghg_and_black_liquor_reference_values.md](../../Docs/forest_ghg_and_black_liquor_reference_values.md); files in `Data/exogenous_data/RED II/` and `Data/exogenous_data/EUwood_BiomassFutures/` |
| Dry LHV, density and moisture conversion evidence | [reference-values note §8](../../Docs/forest_ghg_and_black_liquor_reference_values.md#8-lhv-density-and-moisture-conversions-vtt-technology-272); [VTT PDF/CSV retrieval record](../../Data/exogenous_data/Biomass_fuel_properties/README.md) |
| Wood allocation in the 9 runs; material-use handling | `scripts/summarise_wood_allocation.py` on `paper1/results/`; [woody_biomass_material_use_and_allocation.md](../../Docs/woody_biomass_material_use_and_allocation.md) |

---

## 7. What was consolidated, and change log

| Earlier document | Role before | Now |
|---|---|---|
| `paper1/…/REVIEW_FLAGS.md` (A–G) | Paper review items **and** snippets | Review items → §1.2–1.4 here; snippets (D, G) → [SNIPPETS_overleaf.md](./SNIPPETS_overleaf.md) |
| `Docs/forest_supply_flags_tracker.md` (T1–T14) | Supply audit status and T1 dossier | Status → §1.1/1.5 and decisions → §3; file kept as history with a pointer |
| `Docs/forest_supply_curve_methodology_traceability.md` §10 | Duplicate issue register | §10 replaced by a pointer; the file remains the evidence/derivation document |

| Date | Task | Files | Backup | Description | Status |
|---|---|---|---|---|---|
| 2026-10-12 | Flags consolidated; S2BIOM benchmark flags S2B-1…8 added | this file, `SNIPPETS_overleaf.md`, tracker and traceability pointers, `scripts/analyse_s2biom_finland.py` | git HEAD | Structure only; no numeric value, data, model or run changed | done (uncommitted) |
| 2026-10-12 | Source register and material-use/allocation note; flags W-1…W-6, S-PY, S-RED; A3 explained | `Docs/data_sources_register.md`, `Docs/woody_biomass_material_use_and_allocation.md`, `scripts/summarise_wood_allocation.py`, this file | – | Evidence and documentation only | done (uncommitted) |
| 2026-10-12 | RED II, EUwood, Biomass Futures retrieved; S-RED and W-4 updated | `Data/exogenous_data/RED II/*`, `Data/exogenous_data/EUwood_BiomassFutures/*`, `Docs/forest_ghg_and_black_liquor_reference_values.md`, this file | – | New reference files and documentation; no model, patch or run changed | done (uncommitted) |
| 2026-10-12 | VTT fuel-property evidence; T5/S2B-6 updated | `Data/exogenous_data/Biomass_fuel_properties/*`, source register, reference-values note, this file | New reference files; notes uncommitted | Sourced ranges/equations; black-liquor boundaries qualified; no numerical assumptions adopted | done (uncommitted) |
