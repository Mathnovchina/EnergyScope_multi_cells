# Meeting prep — G4M × EnergyScope Finland coupling (IIASA)

**Meeting date:** 2026-10-09 · **Base document:** `Docs/concept_note_G4M_forest_energy_finland_V1.docx`
**Companion briefing (IIASA models, fully cited):** `Docs/IIASA_Forest_Models_Briefing.md`
**Status:** preparation note (not paper evidence). Prepared 2026-10-08.

> Purpose: get you meeting-ready on three fronts — (1) present your own completed work
> confidently and accurately, (2) hold an informed conversation about the IIASA models
> (G4M, PICUS, FLAM, BeWhere, ForestNavigator D3.4), and (3) drive the meeting toward the
> concrete coupling decisions that actually need IIASA input. Everything below is traceable
> to the concept note, `paper_sections_draft.md`, the Zotero library, or the cited sources
> in the companion briefing.

---

## 0. Suggested meeting objective & agenda (30–45 min)

**One-line objective to open with:** *"I have a complete static Finnish biomass–energy study;
I want to replace the static, assumption-heavy supply curves with physically-grounded ones from
G4M, and to close the forest-sink gap. What can G4M deliver for Finland, and on what interface?"*

1. 2 min — where paper 1 stands (one slide: the 3×3 matrix result).
2. 5 min — the two methodological gaps you want to close (static curves; no sink).
3. 15 min — **the coupling questions** (Section 5 below) — this is the heart of the meeting.
4. 5 min — disturbance track (D3.4) and what's realistically available.
5. 5 min — BeWhere / European extension (Schipfer, Tiwari) — scope and timeline.
6. 3 min — next steps / data handshake.

---

## 1. Know your own work cold (paper 1 — your strongest card)

You should be able to state these without looking. Source: `Docs/paper_sections_draft.md`,
`paper1/results/`, `REPRODUCIBILITY.md`.

**Validation (2017 baseline).** EnergyScope Finland reproduces the 2017 balance to a weighted
**1.2%** error across 14 indicators; CO₂ to **+0.1%** (41.2 MtCO₂). Known residuals you must own
proactively (they *will* be asked): district heat **+43%** and gas-CHP **+37%**, both documented
as aggregation artefacts (`share_heat_dhn` applied to the full LT-heat pool; CHP co-production
arithmetic under a binding gas cap). Run uses `relax_co2=true` — historical reproduction only,
**not** carried into 2035.

**The 3×3 result matrix (2035)** — memorise the shape, not every digit:

| Scenario | Case | Cost | CO₂ | Reduction vs 2017 | Domestic wood used |
|---|---|---|---|---|---|
| S1 BES | Unconstrained | 22.40 bn€/y | 13.02 Mt | 68% | 54.5 TWh |
| S1 BES | −95% (nuclear) | 22.92 | 2.06 | 95% | 74.2 TWh |
| S1 BES | −95% (no nuke) | 22.94 | 2.06 | 95% | 100.4 TWh |
| S2 NFS | Unconstrained | 22.46 | 12.57 | 70% | 45.4 TWh |
| S2 NFS | −95% (nuclear) | 23.02 | 2.06 | 95% | 74.2 TWh |
| S2 NFS | −95% (no nuke) | 23.12 | 2.06 | 95% | 96.2 TWh |
| S3 BDS | Unconstrained | 22.62 | 13.10 | 68% | 32.0 TWh |
| S3 BDS | −95% (nuclear) | 23.56 | 2.06 | 95% | 40.0 TWh (ceiling) |
| S3 BDS | −95% (no nuke) | 23.90 | 2.06 | 95% | 40.0 TWh (ceiling) |

**Three headline messages:**
1. The 2035 system is already **~70% below 2017 even unconstrained** (structural floor: coal
   phase-out + brownfield renewables). The interesting question is the **70%→95% last mile**.
2. Under −95%, **S3 (conservation) saturates its 40 TWh wood ceiling** and becomes the most
   expensive configuration.
3. **Removing nuclear** sharply raises the value of biomass in S1/S2 (up to ~100 TWh) but
   **S3 physically cannot expand** — this is where the conservation/decarbonisation tension bites.

---

## 2. The three things to VERIFY or FIX in the concept note *before* the meeting

These are factual/sourcing items that could undermine you if a forest modeller challenges them.

### 2.1 Blattert sink numbers: figures are right, the BDS ranking is not (CORRECTED)
*Correction note: an earlier version of this section wrongly called the NFS/BES numbers
mis-attributed. Re-reading Blattert et al. (2022, Zotero `SJ5WFJ39`, results on Fig. 8d) shows they are real.*
- **NFS:** carbon sink "highest ... at the end, with up to **80 MtCO2 per year** stored in the forest to the end of the simulation".
- **BES:** "slight decrease in the carbon sink, with **28 MtCO2 per year** ... at the end".
- **BDS:** "highest values at the beginning", but the sink "**collapsed during the second half of the simulation and became even negative**, which correlated with the harvest peak".
- So the concept note's **"BDS largest" is wrong/incomplete**, and it undercuts the simple story "conservation = biggest sink".
- Caveats to state: values are end-of-horizon (100-yr SIMO simulation), not 2035; RCP effects differ; the 27.88 MtCO2 figure is the NFS 2025 *target*, not a result.
- Also: concept note Section 4 says Blattert *and Mönkkönen* give per-scenario sink estimates; **Mönkkönen reports no sink values** (Blattert only).
- Paste-ready replacement text: `Docs/meeting_slides_outline_2026-10-09.md`, Part B.

### 2.2 The S3 (BDS) scaling chain — be ready to defend every step
Concept note 5.A lays out the hand-built chain: Mönkkönen **96%→58–60%** ceiling (Southern
Finland) → national harvest (78.2 Mm³ / 0.96 ≈ 81 → ×60% ≈ 49 Mm³) → residue fraction (15–20%)
→ conservation collection efficiency (30–40%) → **6 TWh logging-residue step → 40 TWh S3 total**.
Mönkkönen et al. (2024, Zotero `YQIETF2I`) confirms **58%** as the safe national level and **60%**
as the 2100 target vs **96%** realized — so the ceiling anchor is solid. **The weak link is
Stage 2** (residue fraction × collection efficiency), which you already flag as stylised.
- **Action:** have the two-stage derivation on one slide. Frame it as *"exactly the chain I want
  G4M to replace with a physically modelled, assortment-level harvest."* That turns a weakness
  into your central ask.

### 2.3 Document polish (quick, do before sending/screensharing)
- Section numbering is broken: Section 6 "Path forward" is followed by **"8. Open questions for
  IIASA"** (heading is empty; the actual Q1–Q7 are in Table 3). There is **no Section 7**. Renumber
  and move the Q-table under the heading.
- References list is **missing** several works cited in-text: Kärhä et al. 2018, di Fulvio et al.,
  and there is **no BeWhere citation** despite RQ5/5.D. Add them (see Section 6 list).
- Title says *"Coupling G4M, PICUS…"* but the body uses PICUS only once — see 4.2 below on how to
  talk about PICUS accurately so the title is defensible.

---

## 3. IIASA models — the minimum you must know (full detail in companion briefing)

Read the companion `Docs/IIASA_Forest_Models_Briefing.md` in full once. The essentials:

### 3.1 G4M (your main ask)
- **What:** geographically explicit, **NPV/economic** forest model (afforest/deforest/manage
  from wood prices vs land-use returns; rotations 5–140 yr). Boreal ecoregion → Finland.
- **Resolution:** native **0.5°×0.5°**; EU runs refine to 1 km biophysical data intersected with
  **country borders → Simulation Units**, so **Finland is resolved as a country**, but results in
  the literature are reported at **EU-27 aggregate**, not Finland-alone. **No dedicated "G4M
  Finland" paper exists** — ask whether a Finland breakout is available/producible.
- **Assortments:** G4M outputs biophysical harvest/stocks/costs; the **split into assortments
  (sawlogs, pulpwood, other ind. roundwood, fuelwood, logging residues = branches+stumps+losses)
  happens downstream in GLOBIOM**, not natively in G4M. *This directly shapes your mapping ask —
  you may be coupling to G4M+GLOBIOM, not G4M alone.*
- **Carbon pools:** living biomass, litter, soil (weak/qualitative), **HWP** (explicit).
  **Deadwood is NOT found as an explicit separate G4M output pool** in the accessible literature —
  important, because your sink coupling and the BDS deadwood narrative lean on it.
- **Precedent:** **G4M→GLOBIOM→MESSAGE** is IIASA's existing forest→energy-system coupling chain.
  Cite this to show you're proposing something aligned with their toolchain, not exotic.

### 3.2 PICUS (and the Finland nuance)
- **What:** stand/patch model (10×10 m patches, individual trees; BOKU Vienna, Lexer). Has native
  bark-beetle/wind modules.
- **Two nuances to get right:** (i) in ForestNavigator's EU-wide run the **native PICUS disturbance
  modules were switched off**; D3.4 uses **PICUS-*derived* process algorithms coupled to G4M**, not
  a stand-level PICUS re-run. (ii) For **Northern Europe/Finland, the climate-sensitive growth model
  in ForestNavigator's regional partition is PREBAS, not PICUS.** → Ask IIASA explicitly *which
  model underlies any Finnish growth/disturbance projection.* (This also justifies softening the
  "Coupling … PICUS" title claim.)

### 3.3 FLAM (wildfire) & D3.4
- **FLAM:** process-based daily wildfire model; applied 0.25°→1 km². **No Finland application yet**
  (closest: Sweden 2022). Wildfire is a secondary risk for Finland — frame it as a sensitivity.
- **ForestNavigator D3.4** (Krasovskiy et al. 2025, GA 101056875, **public PDF**): integrates
  FLAM + G4M + PICUS-derived beetle/wind + a new fuel module, at **5 arc-min (~8 km²) over EU-27
  incl. Finland**. **Critical caveat for you:** *"disturbances are considered only as biomass loss
  and did not account for wood recovery from salvage logging."* → **The ready-made, salvage-aware,
  assortment-level disturbance supply curve you need does NOT yet exist** from IIASA. This is the
  single most important thing to confirm in the meeting (it decides whether your disturbance track
  is feasible now or needs a post-processing layer you build).

### 3.4 BeWhere (European/HWP extension)
- **What:** spatially explicit **MILP facility-siting** model (Leduc, Kraxner). Standard
  architecture: a biomass-supply model (G4M) feeds feedstock data into BeWhere siting.
- **Finland precedent exists:** Natarajan et al. (2014), *Renewable Energy* 62:319 (FT-biodiesel
  siting, Finland) — but paywalled, metadata only.
- **Gap:** **no Schipfer-authored BeWhere/HWP/construction-wood paper could be found.** Since 5.D
  names Schipfer/Tiwari, **ask them directly** what BeWhere-HWP capability exists and under what title.

---

## 4. The coupling decisions this meeting should settle (your real agenda)

Bring these as explicit decision points — each maps to an open question in the concept note.

| # | Decision | Why it matters / your position |
|---|---|---|
| D1 | **G4M alone or G4M+GLOBIOM?** | Assortment split lives in GLOBIOM. If you need sawlog/pulp/residue/fuelwood steps, you likely need the GLOBIOM layer. Clarify the interface. |
| D2 | **WOOD_FI1 = aggregate industrial by-products: black liquor, bark, sawdust (ENSPRESO `MINBIOWOOa` volume as proxy; tracker §7)** | FI1 carries pulp-mill **black liquor** (43 TWh, 2017) + bark + sawdust, which ENSPRESO omits. Ask G4M/BeWhere + industrial throughput to produce a physically grounded black-liquor / by-product / stemwood-chip split, and whether black liquor should be a **captive** resource (tied to pulp output, not dispatchable to DH/fuels). (concept note Q6) |
| D3 | **Industry-vs-energy split** | Energy-available residue = what remains **after** industrial roundwood demand. How does IIASA set the industrial-demand trajectory? (Q5) |
| D4 | **Ecological availability fractions** (deadwood/residue retention, set-aside) | Applied **inside** G4M per scenario, or must you post-apply them? (Q7) |
| D5 | **Sink coupling** (your 5.C) | One exogenous national parameter `S_forest(scenario, year)` added to `Minimum_GWP_reduction`. Confirm G4M can deliver net forest+HWP LULUCF flux per scenario-year. **Deadwood pool gap (3.1) is a risk here.** |
| D6 | **Disturbance salvage** | D3.4 gives biomass *loss* only, no salvage recovery. Can IIASA/BOKU provide salvage volumes, or do you build the salvage post-processing? (decides disturbance-track feasibility) |
| D7 | **Harvest denominator** | % of annual increment vs % of maximum sustainable — your Mönkkönen anchor uses "max economically sustainable." Align definitions with G4M. (Q4) |
| D8 | **Resolution** | 5 arc-min / SimU national — confirm Finland breakout is extractable and in what format. |

---

## 5. Prioritised reading list before tomorrow

**Must-read (have open during the meeting):**
1. `Docs/IIASA_Forest_Models_Briefing.md` — the whole thing, once. Your model cheat-sheet.
2. **ForestNavigator D3.4** PDF (public): `forestnavigator.eu/wp-content/uploads/FN_D3.4_Disturbances-assessment.pdf`
   — read the §2 methods and the Conclusion caveats (salvage not modelled; stylised scenarios).
3. Your own `paper_sections_draft.md` results section + the 3×3 table above.

**Should-skim (Zotero — you own these):**
4. **Blattert et al. 2022** (`SJ5WFJ39`) — re-read the scenario definitions + **results figures for
   per-scenario carbon sink** (to fix item 2.1). This is the backbone of your S1/S2/S3 narrative.
5. **Mönkkönen et al. 2024** (`YQIETF2I`) — the 58/60/96% ceiling and the deadwood/old-growth FRVs
   (backs your S3 and the sink argument).
6. **Di Fulvio et al. 2025**, *Global Env. Change* (`MUUYAGID`) — IIASA GLOBIOM-Forest applied to EU
   biodiversity/protection scenarios; **closest existing analogue to your management-scenario→harvest
   mapping**, and co-authored by the G4M/GLOBIOM team (Lauri, Forsell, Di Fulvio) you'll likely meet.
7. **Booth & Giuntoli 2025**, *GCB Bioenergy* (`EKVL36HA`) — "Burning up the carbon sink"; states
   Finland has **lost its net forest sink** — strong framing ammunition for RQ2/RQ4.

**Optional context (Zotero):**
8. Colla et al. 2022 (`3HSSDKI8`) — your supply-curve method basis (you know it).
9. Venäläinen et al. 2020 (`IIF8ITXA`/`TADLZE8J`) — climate risks to Finnish forests (disturbance framing).
10. Your own `Docs/literature/forest_disturbance_timber_economics_report.md` — the disturbance
    price/salvage numbers (−20–70% prices; +10–64% salvage cost; 16% of EU harvest) for RQ3.

**External (one G4M methods paper, if you have 20 min):** Di Fulvio et al. (2016),
*Scand. J. For. Res.* — "roundwood and logging residues availability and costs for EU-28" (G4M-based,
Finland in the tables) — the single most relevant G4M output analogue to your supply curves.

---

## 6. Open questions to pose to IIASA (refined from concept note Q1–Q7 + research gaps)

Carry these verbatim. The first five are your concept-note questions, sharpened; the last three
come from gaps the model research surfaced.

1. **G4M for Finland:** can you deliver, for Finland 2025–2060 × (intensive/balanced/conservation)
   × (GWL2/GWL3): (a) harvestable wood **by assortment**, (b) ecologically-available fractions,
   (c) net forest+HWP carbon flux, (d) disturbance mortality/salvage? At what resolution/format,
   and **G4M alone or via GLOBIOM**?
2. **Deadwood pool:** does G4M output a separate, quantified **deadwood** carbon pool per scenario-
   year? (Needed for both the sink term and the BDS narrative.)
3. **FI1 by-products:** processing-yield bridge from G4M industrial roundwood, or keep from LUKE?
4. **Industry/energy split:** how do you endogenise it, and what industrial-roundwood-demand
   trajectory would we assume?
5. **Ecological fractions:** applied inside G4M per scenario, or post-applied to raw harvest?
6. **Growth model for Finland:** is Finnish growth/disturbance driven by **G4M, PREBAS, or PICUS**
   in your regional setup? (D3.3/D3.4 suggest PREBAS for the North.)
7. **Salvage recovery:** D3.4 models disturbance as biomass loss only — is a **salvage-wood
   recovery** extension available or planned, or do we build the post-processing?
8. **BeWhere-HWP:** does a Schipfer/Tiwari BeWhere capability for construction/HWP supply chains
   exist (title/venue?), and on what timeline for a joint European extension?

---

*Temp extraction files used to build this note were deleted after compilation. The two Zotero
full texts (Blattert, Mönkkönen) remain in your library; item keys are cited inline for re-opening.*

---

## 7. Addendum — EU-CBM-HAT (JRC) and Paul Rougieux (added 2026-10-08)

Why this matters: Paul Rougieux sits on your individual monitoring committee, and the JRC model he
maintains is an **open, Python, reproducible alternative/complement to G4M for the sink term** (RQ2/RQ4).
Nothing below changes the model or data; it is input to a decision for you (see 7.4).

### 7.1 What the resource is (verified)
- **Dataset:** "EU CBM data", JRC Data Catalogue, DOI 10.2905/JRC.VR7ARNG, **CC BY 4.0**. Backed by the open
  repo `gitlab.com/bioeconomy/eu_cbm/eu_cbm_data_open` (last activity 2026-10-06; build 2026-07-27).
- **Content:** the *input data* of **EU-CBM-HAT** (inventory, growth curves, disturbance events), filtered to the
  `reference` scenario; 25 countries **including FI**. README says to cite Pilli, Blujdea, Rougieux, Grassi &
  Mubareka (2024), *The calibration of the JRC EU Forest Carbon Model within the historical period 2010-2020*,
  doi:10.2760/222407. **Not read by me; it is the document that tells you how well FI is calibrated.**
- **Model:** EU-CBM-HAT = libcbm (C++ rewrite of CBM-CFS3, Canadian Forest Service) + COMBO (scenario
  combination) + HAT (harvest allocation tool). Description report already in your Zotero: `AWYI52HG`
  (Blujdea, Rougieux, Pilli, Grassi, Mubareka, Morken, Kurz 2022; doi:10.2760/244051).
- **Finland in the data (read from the files):** forest types Scots pine / Spruce / Other broadleaved; regions
  FI_N and FI_S; even/uneven-aged; 4 climate units; status "available / not available for wood supply";
  disturbance types include thinnings, clearcut, wildfire, **"Insects with salvage logging (calibration)"** and
  **"Fire with salvage logging (calibration)"**; `domestic_harvest/` holds IRW, FW, total roundwood and
  `hwp_expected_*` series. The repo also ships a **CBM <-> TiMBA coupling** combo (EU25 -> 2040).

### 7.2 How it differs from G4M (the key point for the meeting)
| | G4M (IIASA) | EU-CBM-HAT (JRC) |
|---|---|---|
| Logic | Economic: harvest from prices/NPV | Stock-change, IPCC-style; **harvest is an exogenous input** (IRW and FW time series) allocated by rules to stands |
| Open/reproducible | Not confirmed for Finland-only | Open source, CC BY 4.0, scripted |
| Finland resolution | Country-level SimUs inside EU runs | Country, 2 regions x 3 species x 4 climate units |
| Carbon pools | Biomass, litter, soil, HWP (no explicit deadwood found) | CBM-CFS3 pools: living biomass, dead organic matter (snags, deadwood), soil. **HWP is NOT inside EU-CBM-HAT**: computed afterwards with the IPCC Production Approach (Rougieux et al. 2024, §4.2) |
| Salvage logging | **Not modelled in D3.4** | **Explicit** (report §4.2: same-year or multi-year salvage via snag pools) |
| Link to energy models | G4M->GLOBIOM->MESSAGE | Report names **POTEnCIA** (fuelwood demand fed to the forestry model) as a design goal |

**Implication (an option, not a decision):** G4M answers "how much wood will be harvested under a regime";
EU-CBM-HAT answers "given a harvest trajectory, what is the sink". EnergyScope's wood demand could in
principle drive `fw_harvest`, and the resulting sink feed `S_forest`. This is an alternative route if G4M
sink output (esp. deadwood) is unavailable, and a cross-check if both exist.

### 7.3 The two papers you added to Zotero (read 2026-10-08)
**A. Rougieux, Pilli, Blujdea, Korosuo, Mansuy, Grassi, Mubareka (2024), "Pruning the wood economy or intensifying
harvest on a smaller area to increase the EU forest carbon sink"** (Zotero `FRI6YHQR`; SSRN 5027118; submitted to
*Forest Policy and Economics*; **preprint, not peer reviewed**).
- **Design:** economic model **GFPMx** (harvest demand) coupled to biophysical **EU-CBM-HAT** (what the forests can
  deliver and the resulting sink). 6 scenarios = {SSP2 high demand, "Fair" low demand} x {high / BAU / low removals of
  "other wood components" (OWC = logging residues, branches, snags)}. EU-27 level, to 2070.
- **2020 baseline:** growth 914 Mm3/yr, harvest 577 Mm3/yr, sink -334 MtCO2e (incl. HWP). Scenario sinks 158-647 Mt to 2070.
- **Main messages:** harvest demand is the main driver of the sink; harvesting the same wood over a **smaller area**
  (removing more residues per hectare) gives a bigger sink at equal harvest, enough to hit the 2030 LULUCF target
  (-416 Mt) under high demand, but the sink then deteriorates; only reduced demand ("Fair") keeps it above target to 2050+.
- **HWP vs forest sink (YOUR QUESTION), derived by me from the paper's Tables 6-7, 2030 values, MtCO2e removals:**

| Scenario (2030) | Forest-land sink | incl. HWP | HWP part | HWP as % of forest-land sink |
|---|---|---|---|---|
| Historical 2020 | 298.5 | 334.3 | 35.8 | 12% |
| SSP2, high residue removal | 406.7 | 458.0 | 51.3 | 13% |
| SSP2, BAU | 348.5 | 399.8 | 51.3 | 15% |
| SSP2, low residue removal | 259.6 | 310.9 | 51.3 | 20% |
| Fair, high / BAU / low | 553.2 / 505.1 / 432.1 | 581.1 / 532.9 / 459.9 | 27.9 | 5-6% |

  So HWP is roughly **5-20% of the forest-land sink**, it depends on **demand**, not on residue management, and
  higher demand raises the HWP sink but **not enough to offset the loss of forest-land sink** (paper, §Results,
  Fig. 12). Longer product half-lives raise it. (Per-capita Table 2 gives the same picture: 0.67 -> 0.75 tCO2e/cap in 2020.)
  *These are my differences of published table values, not figures the authors state as a ratio. Check the tables.*
- **Directly useful for your design:**
  1. **Logging-residue removal is a sink lever:** low-removal ("OWC_L", residues only after disturbance) forces more area
     to be cut for the same fuelwood, which *lowers* the 2030 sink (-259.6 vs -406.7). This is EU-level and under fixed
     demand. It shows that your S3 "lower residue collection" is not obviously climate-positive, which complicates
     the intuitive "conservation = bigger sink" story and echoes the Blattert BDS result.
  2. **Fuelwood demand is an input** that is met first from non-merchantable components, then from stems. This is where an
     energy model could plug in.
  3. **HWP accounting follows IPCC:** fuelwood carbon is treated as emitted at harvest. **My inference, to check:** if
     the forest sink you add to `Minimum_GWP_reduction` is net of harvest (LULUCF convention), the energy side must keep
     biomass combustion CO2 at zero, otherwise emissions are double counted.
  4. **Limits the authors state:** harvest never exceeds increment because of silvicultural constraints, so scenarios
     cannot "overharvest"; natural disturbances are only partly represented (they note stochastic events could shift
     biomass to dead organic matter and disrupt the market model); decay half-lives are exogenous.
- **Not extractable as text:** the by-country sink figure (Fig. 12, tC/ha, appears to include Finland). Look at it directly.

**B. Rougieux, Pilli, Blujdea, Mansuy, Mubareka (2024), "Simulating future wood consumption and the impacts on Europe's
forest sink to 2070"** (JRC136526, doi:10.2760/17191; Zotero `IZAXNCBM`). Technical-report version of the same work.
Same scenarios; EU-level; **contains no Finland text**; HWP explicitly **excluded** ("not accounted within the present
study"), whereas the preprint adds it. Reports the Fair scenario reaching -505 Mt (2030) and -547 Mt (2050) vs the
-420 Mt EU target. Notes that exceptional 2019 salvage logging was factored out of the baseline harvest (useful
context for your disturbance track). Cite the preprint for HWP, the report for the EU-CBM-HAT set-up.

### 7.4 What to bring up with Paul / use in the meeting
1. **FI calibration quality:** how closely does EU-CBM-HAT reproduce Finland's NFI/GHG-inventory sink (Pilli et al. 2024)?
   Booth & Giuntoli (2025) say Finland has lost its net forest sink; check consistency.
2. **Driving harvest from an energy model:** can `fw_harvest`/`irw_harvest` be fed by EnergyScope output, and has
   the POTEnCIA/TiMBA coupling been documented enough to copy?
3. **HWP:** HWP is computed outside EU-CBM-HAT (Production Approach, exogenous half-lives). What is the Finland-specific
   HWP-to-forest-sink ratio (the EU-level ratio is ~5-20%, see 7.3), and which `hwp_expected_*` series would you use?
4. **Assortments:** HAT allocates IRW and FW stem volume; are logging residues/stumps (your WOOD_FI2) an output
   or a post-processing assumption?
5. **Scenario/disturbance design:** can a windstorm-then-beetle event with multi-year salvage (§4.2) be set up
   for Finland, rather than the calibration-only disturbance types?
6. **Resolution trade-off:** 2 regions x 3 species is coarse vs G4M SimUs; is that adequate for national S_forest?

### 7.5 Suggested reading order for this addendum
1. Pilli et al. 2024 calibration report (doi:10.2760/222407): FI section only.
2. EU-CBM-HAT description (Zotero `AWYI52HG`): §4.2 salvage, §4.3 IRW/FW allocation, and the interoperability intro.
3. Rougieux et al. preprint (Zotero `FRI6YHQR`): Table 1, Tables 6-7, §4.2 (HWP), §4.3 (limits); then skim JRC136526 (`IZAXNCBM`). Fig. 12 for Finland.


---

## 8. Addendum — supply-curve traceability audit (added 2026-10-08)

Full audit: [forest_supply_curve_methodology_traceability.md](./forest_supply_curve_methodology_traceability.md)
(re-runnable check: `python scripts/check_forest_supply_traceability.py`). All availabilities, patches, run inputs and
GHG factors reproduce. Points that matter tomorrow:
1. **FI1 definition (T1) — RESOLVED by decision (tracker §7):** `WOOD_FI1` is modelled as Finland's captive industrial by-product stream
   (**black liquor, bark, sawdust**), with the ENSPRESO `MINBIOWOOa` *volume* used as a documented proxy. Why: black liquor is Finland's largest
   wood-energy source (43 TWh in 2017) but is **absent from ENSPRESO**, while the validated 2017 run already carries it; `MINBIOWOOa` (45 TWh) matches
   its magnitude. Caveat carried openly: ENSPRESO *formally* labels `MINBIOWOOa` as stemwood chips/pellets (JRC EUR 27575). Cost 11 €/MWh and GHG 10
   are documented hypotheses (black liquor captive ≈ 0, bark/sawdust low; 11 is conservative). **No numbers or runs change.** This also resolves T12
   (cost defensible) and T13 (S3 −26% valid: BDS lowers pulp/sawmill throughput → fewer by-products). Paper wording: REVIEW_FLAGS section G (footnote).
   **For Paul (now a flag, not a question):** *we proxy pulp-mill black liquor through the cheapest ENSPRESO wood step; how would G4M/BeWhere give a
   physically grounded black-liquor / by-product / stemwood split, with a captive-use restriction?*
2. **Unconstrained results hinge on FI1 only (T3):** FI1 is the only step used and it is fully used in all three scenarios.
3. **Conversion factors (T5):** 1.5 MWh/m3 in the S3 chain vs ~1.96 implied by the Luke figures. G4M gives m3, so fix this first.
4. **Costs (T2):** FI1 now has a documented hypothesis (captive by-products, 11 €/MWh, conservative); FI2 = 22 matches observed Finnish forest-chip prices; FI3/FI4 remain assumptions.
5. **S3 FI1/FI3/FI4 cuts are judgement (T4)**; the Moenkkoenen chain only supports FI2.
6. `BIOMASS_RESIDUES` is 4,985 GWh in all 9 runs, although the docs/CSVs define 6,600 / 4,985 / 3,400 (T6).
