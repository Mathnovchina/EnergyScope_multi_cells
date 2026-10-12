# Data and database sources — register, qualification and availability

**Purpose.** One place that says where every input of the Finland ESMC model comes from, how reliable it is, whether it is available in the repo, and what it is relevant for. Built 2026-10-12 from: [FI_baseline_inputs_provenance_2035_2050.csv](../Data/exogenous_data/FI_baseline_inputs_provenance_2035_2050.csv) (parameter-level provenance for 2035), the Thiran thesis, the repo docs, and a read-only survey of the repo. Where the repo does not state something, this file says **not stated** rather than guessing. Flags raised here are tracked in [FLAGS.md](../paper1/reviews_comments_flags_pathforward/FLAGS.md).

**Scope note.** Forest/biomass sources are treated in depth (§4); the rest are catalogued so that nothing is orphaned. Companion: [woody_biomass_material_use_and_allocation.md](./woody_biomass_material_use_and_allocation.md).

## 0. How to read the qualification

| Field | Values |
|---|---|
| **Class** | **Stat** = observed official statistics · **DB** = modelled/peer-reviewed dataset · **Scen** = literature scenario study · **Cat** = technology/price catalogue · **Assum** = modelling assumption or expert judgement |
| **Trace** | ✅ file in repo and mapping to model inputs documented · ⚠️ partly (file in repo but mapping/values not fully verified, or values only reachable through an intermediate source) · ❌ not in repo / cannot be re-checked |
| **Access** | what the repo states about availability and licence. "Licence not stated" means *not stated in the repo*; it does not mean unrestricted. Check terms before redistributing data or publishing derived numbers. |

## 1. Parameter families at a glance

| Parameter family (model files) | Source(s) | Class | Trace |
|---|---|---|---|
| Framework: layers, technology structure, discount rate 1.5%, grid losses, mobility shares | Thiran thesis | DB/Assum | ✅ |
| Technology costs, lifetimes, efficiencies (`02_REF_REGION/Technologies.csv`) | DEA technology catalogues (via thesis [114]) | Cat | ⚠️ |
| Fossil and electricity import prices (`00_INDEP/Resources_indep.csv`) | IEA WEO 2020 (via thesis) | Scen | ⚠️ |
| End-use demands 2035 (`FI/Demands.csv`) | EU Reference Scenario 2020 + JRC-IDEES (Eurostat-based) | Scen/DB | ⚠️ |
| Non-energy demand and HVC/methanol/ammonia split (`FI/Misc.json`) | Eurostat energy balances, Prodcom, WITS, UNFCCC; method of Rixhon et al. (thesis [101]) | Stat | ⚠️ |
| Wind, solar, geothermal potentials, areas (`FI/Technologies.csv`, `Misc.json`) | ENSPRESO wind/solar (Ruiz et al. 2019) | DB | ✅ |
| Hydro capacities | Eurostat, JRC Hydropower database (thesis [169], [170]) | Stat/DB | ⚠️ |
| Nuclear fleet 4.36 GW, wind/PV minima, import cap 25 TWh (patch `fi_baseline_2035.csv`) | Eurostat; national pipeline; interconnection estimate | Stat/Assum | ⚠️ |
| **Wood availability FI1–FI4** (`FI/Resources_S1/S2/S3_*.csv`) | ENSPRESO biomass ENS_Med/ENS_Low; S1 = ×1.20 and S3 = 40 TWh by judgement | DB/Assum | ✅/⚠️ |
| **Wood cost FI1–FI5, GHG FI1–FI5** | Finnish Energy/Luke/IEA 2022 (not in repo); RED II Annex VI via Colla et al. 2022; judgement | Assum | ❌/⚠️ |
| Other biomass (wet, crops, biowaste, residues, waste) | ENSPRESO ENS_Med | DB | ✅ |
| Time series (wind, PV, heat demand shapes, CSP) | OPSD weather, Renewables.ninja, PVGIS/pvlib, csp-guru | DB | ⚠️ |
| 2017 calibration targets (`calibration/reality/finland_2017_reference.csv`) | Statistics Finland, IEA, IAEA, Fingrid, Finnish Energy, UNFCCC | Stat | ✅ |

## 2. Framework, technologies, prices, demands

| Source | What it is | Used for | In repo | Vintage / geography | Access | Qualification and caveats |
|---|---|---|---|---|---|---|
| **Thiran, thesis** (EnergyScope Multi-Cells; file v2.3-final, cited "Thiran 2023" in the provenance CSV) | Original ESMC model and European dataset | Model structure, `Layers_in_out.csv`, defaults for REF region (DHN share 2–37%, public transport 19.9–50%, etc.) | [Paolo_Thiran_Thesis-v2.3-final.pdf](../Data/exogenous_data/Paolo_Thiran_Thesis-v2.3-final.pdf) | Europe, 2019–2050 | Licence not stated | Defaults are European/Belgian-type values, not Finnish: the provenance CSV itself marks the DHN share limits as REF defaults overridden at run time (`--dhn-min/--dhn-max`). Biomass: the thesis takes ENSPRESO ENS_Med as is (companion doc §3). Trace ✅ |
| **DEA technology catalogues** | Danish Energy Agency technology data (electricity and district heating; other catalogues cited by thesis [128],[129] for fuels/chemicals) | Capex, O&M, lifetime, capacity factor (`02_REF_REGION/Technologies.csv`, interpolated to 2035) | [DEA_Elec_Heat.xlsx](../Data/exogenous_data/DEA_Elec_Heat.xlsx), [technology_data_catalogue_for_el_and_dh.pdf](../Data/exogenous_data/technology_data_catalogue_for_el_and_dh.pdf) | EU-average costs, price year **not stated** | Public catalogue; licence not stated in repo | Provenance CSV: confidence "high". Not Finland-specific (e.g. nuclear capacity factor 84.9% vs Finnish ~92%). Price year not documented → see flag S-PY (§6). Trace ⚠️ (which sheet feeds which cell is not documented) |
| **IEA WEO 2020** (Stated Policies) | Energy price outlook | Gas 44.25, diesel 79.7, LFO 60.2, electricity import 84.3 €/MWh (`00_INDEP/Resources_indep.csv`) | ❌ report not in repo | 2035 | Licensed report | Pre-2022 price outlook; the provenance CSV notes gas is above Finnish pre-2022 prices. Electricity import price confidence "medium". Not re-checkable here |
| **EU Reference Scenario 2020** | EU energy/transport/climate projections | Growth rates for demands; mobility demands in `FI/Demands.csv` | ❌ not in repo | to 2050, country level | Public (European Commission) | Pre-war macro assumptions; demand-projection method for 2035 is **undocumented in the paper** (flag C6) |
| **JRC-IDEES** | Integrated database of the European energy sector (Eurostat-based) | 2015 base of sectoral end-use demand (electricity, heat, HT heat) | ⚠️ derived CSVs only | Country, 2015 | Public (JRC) | Boundary mismatch with Statistics Finland for pulp/paper/steel electricity documented in `Docs/finland2017_demand_boundary_audit.md`. Matters for wood: pulp-mill energy demand sits inside the industry demand |
| **Eurostat energy balances; Prodcom; WITS (World Bank); UNFCCC inventory; Indexmundi** | Statistics behind HVC, methanol, ammonia | Non-energy demand 12.6 TWh in 2035 and split HVC 93.0% / ammonia 3.1% / methanol 3.9% (`FI/Misc.json`) | ❌ no downloads in repo | 2019 base, grown with EU Ref | Public | Method adapted from Rixhon et al. (thesis [101]). Finnish HVC is based on current production sites (Neste, Borealis). NED covers **chemicals only** (see companion doc) |
| **Eurostat; JRC Hydropower; e-Highway; Gimeno-Gutiérrez** | Capacity and potential datasets | Hydro dam/river capacities, expansion limits | ❌ | EU | Public | Provenance CSV: high |
| **Statistics Finland** (StatFin 12vq and other tables) | Official Finnish energy statistics | 2017 calibration; black liquor 42,989 GWh and total wood fuels 100,783 GWh (2017) used in the FI1 decision | ⚠️ values quoted in docs; online table accessed 2026-10-08 | Finland, 2017 (series 2015–2024) | Public | Strongest observed source for wood energy. Trace ✅ for 2017 targets, ⚠️ for others |
| **EHK report** | Finnish energy report, 2018-12-11 | Calibration context | [ehk_2017_2018-12-11_en.pdf](../Data/exogenous_data/ehk_2017_2018-12-11_en.pdf) | 2017 | Licence not stated | The filename suggests a Statistics Finland energy publication; **exact parameter mapping not found** |

## 3. Renewables, time series, calibration, GIS

| Source | Used for | In repo | Access and notes |
|---|---|---|---|
| **ENSPRESO wind and solar** (Ruiz et al. 2019, doi 10.1016/j.esr.2019.100379) | Wind onshore 30.77 GW, offshore 21.27 GW, rooftop 13.68 GW, utility PV 58.78 GW, areas, geothermal 0.3 GW | `Data/exogenous_data/ENSPRESO/ENSPRESO_SOLAR_PV_CSP.XLSX`, `…WIND_ONSHORE_OFFSHORE.XLSX` | Open database (title); licence not stated. Offshore wind potential updated with the Ostend Declaration for the North Sea (thesis [172]); thesis notes ENSPRESO wind is outdated for some countries |
| **Open Power System Data weather** (doi 10.25832/weather_data/2020-09-16) | Country-aggregated temperature, DNI, DHI | ❌ gitignored, not local | Open. Cannot be re-checked here |
| **Renewables.ninja** (via OPSD) | Wind and PV capacity-factor series | ❌ | Cited in thesis [181–184] |
| **PVGIS (JRC) and pvlib**; **oemof-thermal** | CSP time series (Spain-Portugal) | `Data/exogenous_data/csp/` | Documented in [README.md](../Data/exogenous_data/README.md) with visit dates (2023-04-05); not relevant for Finland (`solar_area_ground_high_irr` = 0) |
| **csp-guru 2022-07-01.02** (Zenodo 10.5281/zenodo.7112761) | Existing CSP plants | `Data/exogenous_data/csp/csp-guru-…` | Licence file included in the folder |
| **GIS**: Eurostat NUTS 2021 (GeoJSON), Natural Earth countries | Regional aggregation | `Data/exogenous_data/gis/` | Licence not summarised in repo |
| **Finland 2017 reference** | 14 validation indicators: Statistics Finland/IEA (energy mix), IAEA (nuclear), Fingrid (hydro/wind/solar), Finnish Energy (district heat), Statistics Finland/UNFCCC (CO₂ 41.2 Mt) | [finland_2017_reference.csv](../calibration/reality/finland_2017_reference.csv); audit [finland_2017_reality_reference_audit.md](./finland_2017_reality_reference_audit.md) | Caveats in the audit: peat lumped into COAL, CHP double-count risk, imports as exterior consumption. Open items A5 and B.1 in FLAGS.md |
| **Calibration workbooks** | Finland 2017 calibration trackers and templates | `Data/exogenous_data/Finland_*Calibration*.xlsx`, `EnergyScope_Finland_calibration_template_v4.xlsx` | Provenance partly embedded; sheet-to-file mapping **not fully documented** |
| **Not mapped to any input** | `eurogreen/Excel_new_origin.xlsx`; Heydenreich, *Ecological Macroeconomics* (PDF); `Mypaper/` literature | present | Active use in the model **not found** — probably reference material |

## 4. Biomass and forest sources (detailed)

### 4.1 What each source gives for the forest questions

Legend: ● provides it, ◐ partly or indirectly, ○ no.

| Source | Availability by assortment | Harvest-level scenarios | Cost | GHG | Material-use treatment | Regional detail | In repo |
|---|---|---|---|---|---|---|---|
| **ENSPRESO biomass** (Ruiz et al. 2019; JRC EUR 27575) | ● 17 commodities; woody: stemwood chips/pellets, fuelwood, residues, secondary residues | ● ENS_Low/Med/High (EFSOS-based) × 2010–2050 | ● €2010/GJ per commodity | ○ | ● explicit competing-use percentages (§4.2) | ● NUTS0/NUTS2 | ✅ workbook + report |
| **S2BIOM** (D1.1, D1.6, D1.8, `data_FI.xlsx`) | ● kton dm by 40+ types incl. stemwood, residues, stumps, by-products, black liquor | ◐ potentials TECH/BASE/HIGH, UD1–UD8 (only 5–10% harvest cuts; UD5/UD6 = material use subtracted) | ◐ road-side cost forest only, EUR 2012, no stumpage | ○ | ● UD5–UD8 subtract FAO roundwood for material use | ● NUTS3 × 2012/2020/2030 | ✅ |
| **Colla et al. 2022** (Front. Energy Res.; Belgium) | ◐ method: origin × quality categories | ○ | ◐ feedstock + processing + transport + pre-treatment; RoW import 81.5 €/MWh | ● RED II-derived embedded GHG per category (Table 2) | ○ | ○ | ✅ [_colla_extracted.txt](../Data/exogenous_data/Mypaper/_colla_extracted.txt); Belgian `.dat` in `0%_NED_constraints_naphtha_LFO_prices/` |
| **RED II (Directive (EU) 2018/2001), Annex VI** | ○ | ○ | ○ | ● default supply-chain GHG by pathway and distance | ○ | ○ | ✅ original and consolidated texts in `Data/exogenous_data/RED II/` |
| **EUwood; Biomass Futures D3.3** | ◐ by-products and black liquor by country | ◐ A1/B2 scenarios; high/medium/low mobilisation | ◐ BL 0 €/t; other prices from Lindner et al. 2005 | ◐ GEMIS heat-output values | ● Wood Resource Balance: material vs energy demand | ◐ country | ✅ `Data/exogenous_data/EUwood_BiomassFutures/` |
| **VTT Technology 272 (2016)** | ○ fuel properties, not supply potentials | ○ | ○ | ○ | ○ | Finnish fuels; species/assortment detail | ✅ [Biomass_fuel_properties/](../Data/exogenous_data/Biomass_fuel_properties); dry LHV, density, moisture equations |
| **Blattert et al. 2022; Mönkkönen et al. 2024** | ◐ harvest levels, bioenergy targets | ● NFS/BES/BDS policy scenarios; ecological ceiling | ○ | ○ | ◐ roundwood targets (80 Mm³) | ◐ southern Finland | ✅ PDFs in `extra_model_artic/` |
| **Luke / Statistics Finland** | ● observed use (e.g. logging residues 5.1 TWh) | ○ | ◐ prices | ○ | ● observed | ● | ❌ Luke tables not in repo (T9) |
| **IIASA G4M** | ● expected by assortment | ● expected | ○ | ◐ sink | ● expected | ● expected | ❌ data not yet available |

### 4.2 How each source treats competing material use

- **ENSPRESO** (JRC EUR 27575, §4.2.1, printed pp. 24–25 and 37; Table 3 "Competing use (% not going to energy)"): the stemwood material use comes from EFI-GTM (EFSOS); "the stemwood and residues not used for material products are then available for energy." The percentages that I read from the table text are (verify against the PDF figure, extraction is flat): stemwood High 45% (2020) falling to 23% (2050), Medium 52% (2020) / 50% (2030) / 47% (2040) / 42% (2050), Low 55%; primary residues High 0%, Medium and Low 50% (2020) and 60% (2030–2050); secondary residues (woodchips, sawdust) High 0%, Medium 50%→60%, Low 50%→60% (sawdust Low 70%→90%); **black liquor 0%** (estimated, but "endogenous" in JRC-EU-TIMES and not an input).
- **S2BIOM**: base potentials ignore material use; UD5 subtracts FAO roundwood production for material use; UD6 excludes pulp/paper/board roundwood from that subtraction.
- **Thiran thesis**: no explicit treatment of material use; it takes ENS_Med as is (companion doc §3).
- **Model**: no wood-products demand or flow exists (companion doc §2).

### 4.3 Source cards

| Source | Class | Vintage and geography | Qualification | Access |
|---|---|---|---|---|
| **ENSPRESO biomass workbook** `Data/exogenous_data/ENSPRESO/ENSPRESO_BIOMASS.xlsx` | DB | 2010–2050 in 10-year steps; Low/Med/High; NUTS0/NUTS2; costs €2010 | Peer-reviewed (Energy Strategy Reviews 26, 100379); official JRC provenance. **Known issues in this project:** ENS_High Finland FRSR1 = 124 TWh (implausible, rejected); `MINBIOWOOa` is formally stemwood chips/pellets (T1); black liquor absent; no 2035 point (interpolated 2030/2040); S3 uses 2030 (T11); sheet text on "net of industry" not verbatim in workbook (T9) | Open (per title); licence not stated |
| **JRC report EUR 27575** (Ruiz Castello et al. 2015) | DB/report | 2015 | Documents the methodology behind ENSPRESO values (EFISCEN/EFSOS for harvest, EFI-GTM for material use, CBM/GFTM for BaU); explains competing-use percentages | [biomass potentials in europe_web rev.pdf](./biomass%20potentials%20in%20europe_web%20rev.pdf); open JRC publication |
| **S2BIOM** | DB | 2012/2020/2030; NUTS3; kton dm | EU project; EFISCEN + 1 km constraint rasters; cost without stumpage/profit/overhead; **no LHV supplied**; black liquor crudely estimated (≈57% of Statistics Finland); no Finland validation found | Files in repo; terms of use not stated |
| **Colla et al. 2022** | Scen | Belgium, 2050; ENSPRESO reference/high | Provides method (supply-curve steps in merit order, low/high quality limit `Low ≤ 0.621 × High`) and the GHG table. The Belgian step labels in the `.dat` file (e.g. "black liquor") are annotations, not Colla's wording (correction recorded 2026-10-08). Finland values are an adaptation, **not** Colla data | Open article |
| **RED II Annex VI** | Cat | Directive 2018 | Used only for supply-chain GHG; combustion CO₂ = 0 (biogenic). **Text now in the repo and checked 2026-10-12** ([Data/exogenous_data/RED II/](../Data/exogenous_data/RED%20II)); chain to Colla Table 2 verified: FI2 22 and FI5 40 = pellets case 3a (typical 6 and 11 g/MJ), FI3 14 = 4 g/MJ (industry residue chips / agricultural residues; the repo label "case 7a" is wrong), FI4 a 60/40 blend, **FI1 10 t/GWh a judgement**. Details in [forest_ghg_and_black_liquor_reference_values.md](./forest_ghg_and_black_liquor_reference_values.md) | Public law; ✅ in repo |
| **EUwood** (Mantau et al. 2010) and **Biomass Futures D3.3** (Elbersen et al. 2012) | DB/Scen | 2010/2020/2030, EU-27 by country; Biomass Futures also NUTS-level potentials and cost-supply annexes | Basis of JRC secondary-residue potentials; black-liquor years, mass units and energy conventions differ, so no validated cross-source energy range. EUwood describes captive use; Biomass Futures assumes 0 €/t and its Table 3.5 is inconsistent for 2020 | Files in [Data/exogenous_data/EUwood_BiomassFutures/](../Data/exogenous_data/EUwood_BiomassFutures) (Internet Archive captures); terms not stated |
| **VTT Technology 272** (Alakangas, Hurskainen, Laatikainen-Luntama and Korhonen, 2016) | Technical reference | Finland; 2016 compilation of fuel-property studies | Explicit dry LHV ranges, species/assortment basic densities and wet-basis moisture equations. Black-liquor Chapter 5 tables report **HHV of total dry solids**, not directly applicable LHV of organic-only residues. Not a harvest database. Reference choices remain unapproved | [Local PDF, CSV and retrieval/hash record](../Data/exogenous_data/Biomass_fuel_properties/README.md); official VTT download; copyright VTT, redistribution licence and Zotero membership unverified |
| **Finnish cost basis** ("Finnish Energy Industry, Luke, IEA 2022") | Assum | 2022 | FI1 11, FI2 22 (26 in S3), FI3 27, FI4 33, FI5 70 €/MWh. FI2 matches the observed chip price used in calibration; the other steps are not linked to specific figures (T2). Price year not stated | ❌ sources not in repo |
| **Blattert et al. 2022; Mönkkönen et al. 2024** | Scen | Boreal Finland; 2022, 2024 | Used for scenario narrative and S3 cross-check (96% / 58–60% of maximum economically sustainable harvest, southern Finland), not as direct model data | PDFs in repo |
| **IIASA G4M** | Scen/DB (planned) | — | Would provide assortments, harvest levels, disturbance and sink; documents: concept note, IIASA briefing, strategy note | Pending |
| **Forest-disturbance literature** (FORSITE II, ForestNavigator, FLAM, `Docs/literature/…`) | Scen | — | Supports the next phase; no confirmed parameter feed | Files in repo |

## 5. Which source for which forest parameter (recommended roles, not yet decisions)

| Need | Best current source | Cross-check / complement | Gap |
|---|---|---|---|
| Availability of energy wood, net of material use | ENSPRESO ENS_Med/Low (as used) | S2BIOM UD5 (stemwood 48.5 TWh), BASE/HIGH residues (21.6 / 68.9 TWh) | S1 and S3 are not source-derived (T3, T4) |
| Industrial by-products (sawmill, bark, black liquor) | ENSPRESO `W1`/`W1a` (FI3) + proxy FI1 | S2BIOM 4111–4132 (58 TWh incl. black liquor 24.6, LHV assumed), Statistics Finland (black liquor 43 TWh) | EUwood/Biomass Futures now obtained; black liquor not separable in ENSPRESO; reconcile organic residue mass and total dry solids before conversion |
| Cost by assortment | Model assumptions | ENSPRESO €2010/GJ; S2BIOM road-side (floor) | Delivered cost incl. stumpage per assortment (Luke/Finnish Energy) |
| GHG by assortment | Colla Table 2 (RED II) | Official Directive now checked; reference-values note §2 | FI1 judgement; source/pathway and fuel-input versus heat-output boundaries |
| Harvest-intensity scenarios | Blattert/Mönkkönen (narrative); ENSPRESO Low/Med/High | S2BIOM UD1–UD4 (small cuts) | Deep conservation cuts and dynamics → G4M |
| Regional distribution | ENSPRESO NUTS2 | S2BIOM NUTS3 (19 regions) | Not used yet (single Finnish node) |
| Conversion dry tonnes / m³ ↔ MWh | **VTT Technology 272**: dry chip LHV 18.5–20 MJ/kg, species-specific density, moisture equations | S2BIOM conifer/non-conifer densities 415/542 kg dm/m³; JRC Annex 5 Table 26 pp. 94: sawdust 14.71, stemwood 14.15, residues 15.89 (dry 19.19), sawmill 13.55, other industrial 16.04, black liquor 11.67, recovered wood 15.66 GJ/t (moisture basis unclear) | Reference gap partly filled, **parameter selection still open** (T5/S2B-6): record solid/loose volume, species, moisture, dry-total/organic mass. Existing script assumptions unchanged. [Values and equations](./forest_ghg_and_black_liquor_reference_values.md#8-lhv-density-and-moisture-conversions-vtt-technology-272) |

## 6. Cautions and open points

| ID | Point |
|---|---|
| S-PY | **Price years are mixed and undocumented:** IEA WEO 2020 prices, DEA catalogue (year not stated), ENSPRESO €2010, S2BIOM €2012, Finnish biomass costs "IEA 2022". No single base year is stated in the paper. |
| S-LIC | Licences/terms are **not stated** in the repo for most datasets (ENSPRESO, S2BIOM, DEA, Statistics Finland tables, JRC-IDEES). Check before redistributing data files or releasing the repository. |
| S-MISS | Not in repo and therefore not re-checkable: IEA WEO 2020, EU Reference Scenario 2020, JRC-IDEES raw, Eurostat downloads, Luke tables, OPSD weather. (RED II, EUwood and Biomass Futures were added on 2026-10-12.) |
| S-MAP | Sheet-to-cell mapping is not documented for the DEA workbook and the Finland calibration workbooks. |
| S-RED | Resolved in part (2026-10-12): the Directive text is in the repo and the chain Annex VI → Colla Table 2 → model is verified (FI1 remains a judgement, "case 7a" label wrong). See [forest_ghg_and_black_liquor_reference_values.md](./forest_ghg_and_black_liquor_reference_values.md). |

## 7. Change log

| Date | Task | Files | Backup | Description | Status |
|---|---|---|---|---|---|
| 2026-10-12 | Data-source register created | this file | – | Compiled from provenance CSV, thesis, docs and repo survey; no data, model or run changed | done (uncommitted) |
| 2026-10-12 | RED II, EUwood, Biomass Futures added | §4.1, §4.3, §6 | – | Local copies retrieved; see forest_ghg_and_black_liquor_reference_values.md | done (uncommitted) |
| 2026-10-12 | LHV/density/moisture source added | §4–5; `Data/exogenous_data/Biomass_fuel_properties/*`; reference-values note §8 | New reference files; register uncommitted | Qualified VTT ranges and CSV; no assumption or model input changed | done (uncommitted) |
