# Briefing: IIASA / Forest Models for Coupling to EnergyScope (Finland)

*Prepared for a meeting with IIASA on coupling forest models to an energy-system model (EnergyScope) for Finland. Compiled from peer-reviewed literature, IIASA model pages (via Wayback Machine where the live site blocked automated access), and ForestNavigator project deliverables (fetched directly from forestnavigator.eu). All claims are cited; unverifiable or uncertain points are explicitly flagged in **[GAP]** notes.*

---

## 1. G4M — Global Forest Model (IIASA) — ★ most important

### (a) What it is / what it models
G4M (originally **DIMA** – Dynamic Integrated model of Forestry and Alternative Land use) is a **geographically explicit, economic (net-present-value, NPV) model of global forest land-use change, forest management, and carbon/wood dynamics**, developed at IIASA by Georg Kindermann, Michael Obersteiner, Mykola Gusti and colleagues. It compares the income derivable from forestry against alternative land uses (agriculture, bioenergy crops) for each grid cell and simulates whether land is afforested, deforested, or actively managed as forest.

> "DIMA assesses land-use options in agriculture and forestry in 0.5°-grid cells across the globe. The model predicts deforestation in forests where land values are greater in agriculture than in forestry and, vice versa, afforestation of agricultural and grazing lands where forestry values exceed agricultural ones." — Kindermann et al. (2008), *PNAS* 105(30):10303, Methods.

G4M estimates productivity for **five forest types** (evergreen needleleaf, evergreen broadleaf, deciduous needleleaf, deciduous broadleaf, woody savannas) across **four ecoregions** (Tropical, Subtropical, Temperate, **Boreal** — Finland falls here) based on dynamic site variables (monthly temperature, precipitation, radiation, CO₂), semi-dynamic soil/nutrient variables, and static variables (IIASA model page, archived: `web.archive.org/web/20240102034147/https://iiasa.ac.at/models-tools-data/g4m`).

### (b) Spatial resolution / Finland-specific detail
- **Native/global resolution: 0.5°×0.5°** grid cells — stated consistently from the earliest papers (Kindermann et al. 2006, 2008) through later work (Gusti & Kindermann 2011; di Fulvio et al. 2016). At Finland's latitude (~60–70°N) a 0.5° cell is physically smaller than at the equator (grid is in degrees, not km).
- **EU-focused refinement**: for EU applications, a finer **1×1 km** biophysical dataset (soil, topography, climate at 25×25 km, forest-cover source map at 25×25 m aggregated to 1 km) is built, then **"intersected with a 0.5° grid and country borders"** to create homogeneous **Simulation Units (SimUs)** — clustered by Country × Elevation × Slope × Soil texture (Kindermann et al. 2013, *Carbon Balance and Management* 8:2; di Fulvio et al. 2016). This confirms **country identity (hence Finland) is an explicit SimU-delineation criterion**, even though the underlying grid is nominally global/0.5°.
- Kindermann et al. (2013) explicitly lists Finland as 1 of 27 EU member states in its dataset and is co-authored with the **Finnish Forest Research Institute (Metla), Vantaa**. However, **results are reported only at EU-27 aggregate level**, not broken out for Finland alone.
- **[GAP]** No dedicated "G4M Finland" or "G4M Nordic" paper was found despite targeted searching. Finland appears only as one of several resolved countries in EU/global-scale runs (e.g., Kindermann et al. 2013; di Fulvio et al. 2016, where Finland shows up in country-level result tables as a top producer of roundwood/logging residues). Detailed Finnish national forest-sector studies in the literature typically use domestic models (e.g., **MELA**) rather than G4M. It is possible more granular Finland/Nordic G4M runs exist in IIASA interim reports not indexed in academic databases (IIASA's PURE repository search interface was blocked by an anti-bot challenge during this research).

### (c) Management scenarios, harvest decisions, assortments, carbon pools

**Management-scenario categories** (two overlapping framings found in the literature):
- IIASA's own model page describes a selectable **"management regime (e.g. keep current stock, maximize harvests, maximize stock, no harvests)"**.
- Kindermann et al. (2013) compares **"maximise stocking biomass"** vs. **"maximise increments" (with/without change of species)** management scenarios, showing stem-carbon stocks reaching ~50 tC/ha by 2100 under biomass-maximizing management vs. ~20 tC/ha under increment-maximizing management.
- A baseline **"current management"** mode (used for coupling into GLOBIOM) "keeps the biomass stocks and increments constant over time" and "assumes all forests are normal forests where the oldest age class is either harvested or removed by natural mortality or natural disturbances" (Gusti 2010, as paraphrased in Lauri et al. 2017, p.4–5 — **[GAP]**: this description is second-hand; Gusti (2010) itself could not be retrieved, see §Key References).

**Harvest decision economics**: Harvest/afforestation/deforestation decisions are driven by **NPV comparison across land uses and across multiple forestry rotations**. Kindermann et al. (2006) formalizes: NPV of forestry over multiple rotations (Fᵢ) is built from the NPV of one rotation (fᵢ), accounting for planting costs at rotation start and harvested-wood income (price × volume) at rotation end; **rotation length ranges 5–140 years** depending on site productivity. The term "Faustmann" is never used explicitly in the primary sources accessed, but the logic is functionally Faustmann-type **[characterization, not a direct IIASA quote]**. Economic logic for harvest timing/intensity: "high harvest amounts will lower market prices of wood... an economic harvest decision will minimise harvesting costs and maximise timber prices by having high harvest amount" (Kindermann et al. 2013).

**Harvest-by-assortment**: G4M itself outputs biophysical wood-supply data (stocks, increments, harvest volumes, costs) per SimU/grid cell and country; the **detailed split into assortments is performed downstream, in GLOBIOM's forest-sector module**, not natively inside G4M. GLOBIOM's forest sector module (fed by G4M) includes:
> "**five primary products (pulplogs, sawlogs, other industrial roundwood, fuelwood, and logging residues)**. Pulplogs, sawlogs, other industrial roundwood and fuelwood are stemwood. **Logging residues are branches, stumps, and harvest losses** (= stemwood not suitable for material use)... If there is insufficient stemwood to cover the FAOSTAT fuelwood demand, then branches, stumps and harvest losses are allowed to be used for fuelwood." GLOBIOM also models **eight final products** (sawnwood, plywood, fibreboard, chemical pulp, mechanical pulp, etc.). — Lauri et al. (2017), *Forest Policy and Economics* 83:121–130, §2.2.

A separate, more detailed G4M-native harvesting-method algorithm exists for **shelterwood logging**: Gusti, Di Fulvio & Forsell (2020), describing simulation of shelterwood (partial, multi-entry) harvesting at the forest-stand scale within G4M (see Key References).

**Carbon/LULUCF pools** (cross-referenced across sources):

| Pool | Status in G4M literature |
|---|---|
| Living/standing biomass | Explicit core output (Kindermann et al. 2013; all G4M papers) |
| Litter | Explicit: "pricing of carbon stored in forest biomass, litter and soil alters forest NPV" (Gusti & Kindermann 2011) |
| Soil carbon | Modeled but largely qualitative/empirical — Kindermann et al. (2013) notes decomposing deadwood "will also increase the soil carbon," not reported as a separate quantified time series in that paper. Lauri et al. (2017) explicitly states G4M as of 2017 lacks a full process-based soil-carbon/decomposition sub-model and flags coupling to a dedicated soil-carbon model as **future work** (citing Kindermann et al. 2013; Zhou et al. 2013; Cherubini et al. 2016). |
| Harvested wood products (HWP) | Explicit named pool: "the harvested carbon is still stored in harvested wood products and will come back to atmosphere with a delay" — carbon is shared between short- and long-lived product pools (Kindermann et al. 2006). |
| Deadwood | **[GAP]** Not found as an explicitly separate/named output pool in the sources accessed; "damaged wood left in stands" is discussed qualitatively (Kindermann et al. 2013) but not reported as a distinct variable. May be documented in Gusti (2010) or IIASA Interim Reports not accessible here. |
| Net LULUCF flux | G4M+GLOBIOM combination used to generate national net LULUCF emissions/removals for UNFCCC INDC assessments (Forsell et al. 2016, *Carbon Balance and Management* 11:26) — e.g. reports Russia's LULUCF sector as a net sink of −651 Mt CO₂e/yr in 2010. |

### (d) Natural disturbances in G4M itself
G4M's own economic/growth core does **not** natively simulate bark beetle, windstorm, or wildfire processes — it treats the "oldest age class" as removed by harvest **or** "natural mortality or natural disturbances" generically in its "current management" baseline (Gusti 2010, via Lauri et al. 2017). Explicit **process-based bark-beetle/windstorm/fire coupling is a newer development** (ForestNavigator project, see §5) in which PICUS-derived disturbance algorithms and FLAM are coupled to an extended version of G4M called **"G4M-X."**

### (e) Relationship to GLOBIOM
G4M and GLOBIOM are **separate but tightly linked IIASA models**, solved recursively:
> "GLOBIOM... is a global spatially explicit agricultural and forest sector model, in which the world is divided into 30 economic regions and about 200,000 land-use units (Havlik et al. 2011, 2014). The model is solved recursively using biophysical data from the spatially explicit forest growth and management model, G4M... The linkage between GLOBIOM, G4M and MESSAGE works as follows. First, G4M is solved for a representative forest management called 'current management'... Second, the biomass stocks, increments and forest areas feed into GLOBIOM... Primary products come directly from the forests and their supply is based on the production costs and bio-physical data from G4M." — Lauri et al. (2017), §2.2.

In short: **G4M → supplies spatially explicit wood-supply curves (stocks/increments/costs) → GLOBIOM's forest-sector module → market-clears assortment allocation and downstream HWP processing across 30 world regions → optionally feeds into the MESSAGE integrated assessment/energy-system model.** This G4M→GLOBIOM→MESSAGE chain is the closest existing analogue, inside the IIASA toolkit, to a forest-model → energy-system-model coupling, and is directly relevant as a template/precedent for an EnergyScope-Finland coupling.

### Disturbance-aware, time-profiled biomass supply curves — can G4M/IIASA tooling produce these?
Yes, in principle, via the newer **G4M-X + PICUS-disturbance + FLAM** chain developed under ForestNavigator (see §5): salvage/disturbance-driven biomass losses and a fuel-accumulation module are now explicitly linked to G4M-simulated deadwood/litter stocks, and the system produces time-stepped (multi-decade, 5-arcmin grid) biomass/carbon outputs disaggregated by scenario (economic/conservation/societal management) that could in principle be converted into disturbance-aware, time-profiled biomass/salvage-wood supply curves. **Caveat** (explicitly stated by the D3.4 authors): in the current version, "disturbances are considered only as biomass loss and did not account for wood recovery from salvage logging" — i.e., the salvage-wood recovery and assortment-split logic needed for a true "disturbance → recovered biomass → energy system" supply curve is **not yet implemented**; this is an acknowledged limitation to raise directly with IIASA. **[GAP]** No published paper demonstrating a direct FLAM→G4M (as opposed to FLAM→GLOBIOM) data feed was found.

---

## 2. PICUS — forest patch/stand model (used in ForestNavigator for disturbances)

### (a) What it is
PICUS v1.5 (Lexer & Hönninger, 2001; Seidl et al., 2005; Irauschek et al., 2017a) is a **hybrid gap/patch model combined with process-based stand-level NPP algorithms** (Landsberg & Waring 1997 light-use-efficiency approach), developed at **BOKU Vienna**. Quoting ForestNavigator Deliverable D3.3 ("Climate Sensitive Models," §3.2, pp.29–30):
> "The spatial core structure of PICUS is an **array of 10×10 m patches with vertical crown cells of 5 m in height**. Interactions between patches are considered via a three-dimensional light model and spatially explicit seed dispersal. **The basic simulation unit is the individual tree.**... **Individual tree mortality depends on age and stress conditions. Spruce bark beetles, windstorms and ungulate browsing are disturbance factors that are explicitly considered.**"

It simulates tree growth (potential growth + environmental modifiers for temperature/water/nutrients/light), natural regeneration (seed production/dispersal, height-class seedling sub-model), individual-tree mortality, and an optional soil C–N decomposition sub-model. It is parameterized for **17 tree species** and includes a flexible silvicultural management module (clearcut+planting, shelterwood, irregular shelterwood, thinning, uneven-aged harvesting, **salvage logging after storm**). Outputs include tree/stand height, DBH, volume growth, basal area, biomass by compartment, and carbon pools (tree / deadwood / organic layer / soil).

### (b) Spatial level — stand/patch, not landscape-native
PICUS is explicitly a **stand-level model**: "trees are randomly assigned to the simulated **100 m² patches** of the simulated forest" (D3.3, §3.4.2). It is **not** natively spatially explicit at landscape/national scale. In ForestNavigator's EU-wide application it is **upscaled via stratified sampling + statistical emulation**: a subset of ~200 representative **5-arcminute grid cells** (each containing up to 100 1×1 km simulation units) was sampled across a broad environmental gradient within PICUS's assigned region (Central EU/Alpine areas — PREBAS handles Northern EU, 3D-CMCC-FEM handles Southern EU), and the simulated responses are used to calibrate **statistical emulators** that run cheaply over the full grid feeding an extended meta-model, "**G4M-X**." **Important caveat**: in this particular EU-wide D3.3 exercise, PICUS's native bark-beetle/windstorm disturbance routines were **switched off**: "natural disturbances occurrence was not included in the simulations" (D3.3) — they are documented/available in PICUS but not activated in that specific calibration run. For the explicit EU-wide disturbance (bark beetle/wind) simulation, see D3.4 (§5 below), which uses **PICUS-derived process algorithms** (not the full native PICUS stand model) coupled directly to the G4M-X grid.

**Note on PICUS vs. "PREBAS"**: for Northern Europe (including Finland), ForestNavigator's climate-sensitive forest growth modeling uses **PREBAS**, not PICUS — PICUS is assigned to Central EU/Alpine areas. This means for a Finland-specific coupling, PREBAS (not PICUS) is the relevant growth-model component in ForestNavigator's regional partition, though the **disturbance algorithms in D3.4 (bark beetle, windstorm) are applied EU-27-wide, including Finland** regardless of which growth model underlies a given region (see §5).

**Distinction from iLand**: PICUS should not be confused with **iLand** (Seidl, Rammer, Scheller, Spies 2012, *Ecological Modelling* 231:87–100), a related but distinct, more mechanistic, explicitly **landscape-scale** individual-based model from the same Vienna research lineage (same authors: Rammer, Seidl), engineered specifically to overcome PICUS's single-stand computational limits for spatially explicit landscape-to-regional disturbance simulation. **[inference, not an explicit IIASA "successor" statement — flagged]**.

### (c) Key papers
- Lexer, M.J., Hönninger, K. (2001) "A modified 3D-patch model for spatially explicit simulation of vegetation composition in heterogeneous landscapes." *Forest Ecology and Management* 144(1–3):43–65. DOI: 10.1016/S0378-1127(00)00386-8. (The actual founding PICUS paper.)
- Seidl, R., Lexer, M.J., Jäger, D., Hönninger, K. (2005) "Evaluating the accuracy and generality of a hybrid patch model." *Tree Physiology* 25(7):939–951. DOI: 10.1093/treephys/25.7.939. (Validation paper.)
- Irauschek, F., Rammer, W., Lexer, M.J. (2017) "Evaluating multifunctionality and adaptive capacity of mountain forest management alternatives under climate change in the Eastern Alps." *European Journal of Forest Research* 136:1051–1069. DOI: 10.1007/s10342-017-1051-6 (open access).
- Seidl, R., Rammer, W., Scheller, R.M., Spies, T.A. (2012) "An individual-based process model to simulate landscape-scale forest ecosystem dynamics" [**iLand**]. *Ecological Modelling* 231:87–100. DOI: 10.1016/j.ecolmodel.2012.02.015.
- Seidl, R., Rammer, W., Spies, T.A. (2014) "Disturbance legacies increase the resilience of forest ecosystem structure, composition, and functioning." *Ecological Applications* 24(8):2063–2077. DOI: 10.1890/14-0255.1 (open access via PMC4820056). (An **iLand**-based study, not PICUS.)

**[GAP]** Secondary citations named within D3.3 (Didion et al. 2009; Lexer et al. 2002; Maroschek et al. 2015; Pardos et al. 2015; Zlatanov et al. 2017; "Irauschek et al. 2017b" regeneration sub-model paper) could not be independently resolved to full bibliographic entries/DOIs within the time available.

---

## 3. FLAM — wildFire cLimate impacts and Adaptation Model (IIASA)

### (a) What it is / what it models
FLAM (formerly the "**Standalone Fire Model, SFM**") is IIASA's **process-based, daily-time-step wildfire model**, developed by Krasovskii, Khabarov, Kraxner, Obersteiner and colleagues, decoupled from Dynamic Global Vegetation Models for speed and calibration flexibility:
> "FLAM is a standalone fire model based on the **Arora and Boer [2005] algorithm**... The key features implemented in FLAM include **fuel moisture computation based on the Fine Fuel Moisture Code (FFMC) of the Canadian Fire Weather Index (FWI)** and a procedure to **calibrate regional fire suppression efficiency**." — Krasovskii et al. (2018), *Forests* 9(7):437, §2.

It computes three conditional daily fire-probability components: (1) **ignition probability** (natural — lightning climatology from LIS/OTD satellite data; and human — population-density-driven logistic function, with a simultaneous population-density-driven **suppression probability**); (2) **fuel availability** (aboveground biomass/litter/coarse woody debris maps); (3) **weather-driven probability** (FFMC-derived fuel moisture from reanalysis weather forcing — wind, humidity, temperature, precipitation). Fire spread rate and expected burned area follow from wind speed and the fire-weather index. Calibration against observed burned-area datasets (**GFED** globally, **EFFIS** in Europe, **MODIS FireCCI** regionally) is FLAM's signature innovation (spatially-calibrated suppression efficiency).

### (b) Spatial resolution and regions covered
FLAM has been applied at a range of resolutions depending on study:

| Study | Region | Resolution |
|---|---|---|
| Khabarov et al. 2016 / Krasovskii et al. 2016 | Europe (17 countries) | continental grid, EFFIS/GFED-matched |
| Krasovskii et al. 2018 | Indonesia | **0.25°** (~25–28 km, GFED v4-matched) |
| Jo et al. 2023 | South Korea | downscaled to **1 km²** |
| Cimdins, Krasovskiy & Kraxner 2022 | Sweden | **1×1 km²** (FFMC weather module at 0.125°, resampled) |
| Hammed et al. 2024 | Spain | **1 km²** |
| Corning, Boere, Krasovskiy et al. 2024 | Indonesia (+EU via trade) | grid-based, coupled to GLOBIOM |

So FLAM spans **coarse global/continental (≈25 km)** applications and **fine (1 km²) national** case studies (the latter typically add a random-forest ML layer on top of the core physical FFMC module).

### (c) Finland/Fennoscandia coverage
**No dedicated Finland FLAM application exists [confirmed gap, not just a retrieval failure — multiple convergent OpenAlex full-text searches found nothing].** The closest analogue: **Cimdins, Krasovskiy & Kraxner (2022)**, "Regional Variability and Driving Forces behind Forest Fires in Sweden," *Remote Sensing* 14(22):5826, DOI 10.3390/rs14225826 (open access) — lead author affiliated with the **University of Eastern Finland, Joensuu**, explicitly framed as boreal/Fennoscandian-relevant: "This research provides additional contributions to the existing forest fire knowledge about the situation in boreal forests of Northern Europe... also in Scandinavia" (Conclusions), and states "Our modeling approach can be extended to hotspot mapping in **other boreal regions**" (Abstract) — strongly suggesting Finland is a natural, as-yet-unpublished next FLAM application.

### (d) Integration with G4M/GLOBIOM
A direct, published **FLAM→GLOBIOM** model chain exists: Corning, Boere, Krasovskiy et al. (2024), "Flammable futures—storylines of climatic impacts on wildfire events and palm oil plantations in Indonesia," *Environmental Research Letters*, DOI 10.1088/1748-9326/ad7bcc (open access) — "a model chain consisting of CMIP6 climate modeling... FLAM to predict burned areas, whereas GLOBIOM... assesses competition for land use and provides resultant socio-economic consequences." **No published direct FLAM→G4M (as opposed to FLAM→GLOBIOM) coupling paper was found** as a standalone item, **but** ForestNavigator Deliverable **D3.4 (2025)** explicitly integrates FLAM alongside PICUS-derived bark-beetle/wind algorithms directly into the **G4M-X** meta-model via a newly-built **fuel module** linking G4M-simulated deadwood/litter to FLAM's fuel-availability input — this is the concrete FLAM–G4M coupling the user should discuss with IIASA (see §5 below).

---

## 4. BeWhere (IIASA)

### (a) What it is
BeWhere is a **spatially explicit Mixed-Integer Linear Programming (MILP) model** for siting biomass-based energy/industry supply chains, led by **Sylvain Leduc**, with long-standing involvement of **Florian Kraxner**. From IIASA's own model page (archived, live site blocks automated fetch): `web.archive.org/web/20240102034144/https://iiasa.ac.at/models-tools-data/bewhere`:
> "Second-generation biofuels using non-food crops or sources such as forestry residues, municipal waste, algae, biomass grown on non-arable land, or certified wood, are a more sustainable source of biofuel production. However, very large production plants are required to make production costs competitive... the optimal geographical location and size of the production plant with respect to feedstock and demand location needs to be determined, prior to plant investment and construction, and this can be done using BeWhere."

**Core methodology** (synthesized from paper abstracts/titles, since the IIASA page's technical "Method" section is JS-rendered and not capturable — **[GAP]**, flagged as inference not a direct spec quote): binary/integer facility-siting decision variables (open/not open a plant of a given technology/size at a given grid cell) + continuous feedstock/product flow variables; objective = minimize total system cost (feedstock + transport + conversion/investment + O&M) net of revenue, subject to feedstock-availability, transport-cost-by-distance, technology-capacity, and demand constraints.

### (b) Spatial resolution and inputs/outputs
Not uniform — customized per study: pan-European studies (country/regional aggregation); Sweden/Finland studies tied to national forest-inventory data (e.g., Tomppo/Metla inventory in the Finland case). **Typical inputs**: feedstock quantity/location (forest residues, wood, agricultural residues), feedstock costs, distance-based transport-cost functions, candidate technology options with investment/O&M costs and efficiencies, demand/offtake locations (including heat/power for CHP). **Typical outputs**: optimal plant locations/count, installed capacities, technology choice, feedstock flow allocation, total system cost/profit, co-product (heat/power/fuel) volumes.

### (c) Finland-specific application
> **Natarajan, K., Leduc, S., Pelkonen, P., Tomppo, E., Dotzauer, E. (2014)** "Optimal locations for second generation Fischer Tropsch biodiesel production in Finland." *Renewable Energy* 62:319–330. DOI: 10.1016/j.renene.2013.07.013.

Author team: Karthikeyan Natarajan (University of Eastern Finland, Joensuu, corresponding author), Sylvain Leduc (IIASA), Paavo Pelkonen (UEF), Erkki Tomppo (Finnish Forest Research Institute, Metla), Erik Dotzauer (Mälardalen University, Sweden). **[GAP]** No open-access copy exists (confirmed via Unpaywall: `is_oa: false`); only bibliographic metadata and reference-list context could be verified — not the internal methods/results (grid resolution used, number of candidate sites, cost results). A related, earlier Finland paper by the same group: Natarajan, Leduc, Pelkonen, Tomppo, Dotzauer, "Optimal Locations for Methanol and CHP Production in Eastern Finland," *Bioenergy Research*, DOI 10.1007/s12155-011-9152-4.

### (d) Other foundational / Nordic BeWhere papers
- Leduc, S., Schwab, D., Dotzauer, E., Schmid, E., Obersteiner, M. (2008) "Optimal location of wood gasification plants for methanol production with heat recovery." *International Journal of Energy Research* 32(12):1080–1091. DOI: 10.1002/er.1446.
- Leduc, S., Schmid, E., Obersteiner, M., Riahi, K. (2009) "Methanol production by gasification using a geographically explicit model." *Biomass and Bioenergy* 33(5). DOI: 10.1016/j.biombioe.2008.12.008.
- Leduc, S., Starfelt, F., Dotzauer, E., Kindermann, G., McCallum, I., Obersteiner, M., Lundgren, J. (2010) "Optimal location of lignocellulosic ethanol refineries with polygeneration in Sweden." *Energy* 35(6):2709–2716. DOI: 10.1016/j.energy.2009.07.018.
- Wetterlund, E., Leduc, S., Dotzauer, E., Kindermann, G. (2012) "Optimal localisation of biofuel production on a European scale." *Energy* 41(1):462–472. DOI: 10.1016/j.energy.2012.02.051.
- Leduc, S., Wetterlund, E., Dotzauer, E., Kindermann, G. (2012) "CHP or Biofuel Production in Europe?" *Energy Procedia* 20:40–49. DOI: 10.1016/j.egypro.2012.03.006 (open access, CC BY-NC-ND).
- Leduc, S., Kindermann, G., Forsell, N., Kraxner, F. (2015) "Bioenergy Potential from Forest Biomass." In *Handbook of Clean Energy Systems*, Wiley. DOI: 10.1002/9781118991978.hces101 — explicitly confirms the standard BeWhere architecture: a forest/biomass-supply model (G4M) feeding feedstock-availability data into the BeWhere techno-economic siting model.

### (e) HWP / construction-wood / Schipfer-authored BeWhere work
**[GAP — confirmed not located]**. Despite targeted searches (Crossref, Semantic Scholar, multiple web engines, author search for Fabian Schipfer), no Schipfer-authored BeWhere paper on harvested-wood-products/sawmill/construction-wood supply chains could be found or verified. The only Schipfer paper confirmed is unrelated: Schipfer, Kranzl, Olsson, Lamers (2020) "European residential wood pellet trade and prices dataset," *Data in Brief* 32:106254, DOI 10.1016/j.dib.2020.106254 — **not** a BeWhere/construction-wood paper; flagged so it is not mistaken for the requested reference. Recommend asking IIASA directly about this in the meeting.

---

## 5. ForestNavigator project & Deliverable D3.4 (Krasovskiy et al. 2025)

### Project overview
- **Full title**: "ForestNavigator: Navigating European forests and forest bioeconomy sustainably to EU climate neutrality."
- **Grant Agreement**: **101056875**; CORDIS page: `cordis.europa.eu/project/id/101056875`. **Call**: HORIZON-CL5-2021-D1-01 (Horizon Europe, Cluster 5 "Climate, Energy and Mobility," Destination 1, 2021 call).
- **Coordinator: IIASA** — confirmed via D3.4's approval signatures (Project coordinators Petr Havlík and Fulvio Di Fulvio, IIASA; Project Office Eleonora Tan, IIASA).
- **Confirmed consortium partners**: IIASA (coordinator; WP3 task lead Andrey Lessa Derci Augustynczik), **BOKU Vienna** (WP3 forest-disturbance-modeling lead, Manfred Lexer), **Wageningen Economic Research (WUR)** (leads WP5 "Green growth and green jobs" using the MAGNET model, and WP7 "EU forest sector in the global context" linking GLOBIOM/G4M-X to MAGNET/E3M). **[GAP]** Full consortium partner list, project start/end dates, and total EU budget could not be retrieved (CORDIS fact-sheet and the project's "who we are" page render this via client-side JavaScript not captured by static fetch).
- Objective (CORDIS): "ForestNavigator aims at assessing the climate mitigation potential of European forests and forest-based sectors through modelling of policy pathways, consistent with the best standards of LULUCF reporting, and informing public authorities on the most suitable approach to forest policy and bioeconomy."

### Deliverable D3.4
> **Krasovskiy, A., Jo, H.-W., Lexer, M., Johnstone, C., Park, E., Kraxner, F. (2025).** *D3.4 Assessment of natural disturbances and extreme events impact on forest mitigation potential.* ForestNavigator Deliverable, Grant Agreement 101056875, Work Package 3. Public deliverable, due 31/03/2025, approved 10–12/05/2025.
> URL: `https://www.forestnavigator.eu/wp-content/uploads/FN_D3.4_Disturbances-assessment.pdf` (fully public, no embargo — marked "Public, will be published on CORDIS" on its cover page).

**Disturbance modules integrated** (§2, pp.11–22):
1. **FLAM** ("Wildfire Climate Impacts and Adaptation Model") — process-based fire model (§2.1).
2. **G4M** — the core forest growth/management model (§2.2), simulating even-aged species cohorts per grid pixel (thinning, harvest, mortality, regeneration) (Kindermann et al. 2013).
3. **PICUS-derived bark-beetle and windstorm algorithms** (§2.3) — process-based modules originating in PICUS (Lexer & Hönninger 1998/2001; refined by Seidl et al. 2007; storm sub-module based on Pastor et al. 2014/2015). Bark-beetle damage probability/intensity driven by Norway spruce (*Picea abies*) share, crown closure, stand age, a soil-moisture drought index, and the prior 4 years' disturbance history. Wind-damage probability/intensity driven by daily maximum wind-gust speed, stand age/volume, frozen-soil state, and prior disturbance history.
4. **A newly developed fuel module** (§2.4/2.6) — dynamically links G4M-simulated deadwood/litter (coarse woody debris) to FLAM's fuel-availability input, closing the growth→fuel→harvest→disturbance feedback loop; described as the key methodological innovation of this deliverable.

**Geographic coverage**:
> "In this study, we focused on all EU forests land in the EU-27 countries. EU forests are represented in a uniform grid with a **resolution of 5 arc minutes, corresponding to approximately 8 square kilometers per pixel**." (§2.5, p.16)

**Finland is covered** as part of the EU-27 scope (Norway is excluded, not being an EU member). No Finland-specific numerical breakout is given, but "Northern Europe" is treated as a distinct bark-beetle/windstorm hotspot region throughout the Conclusion.

**Key findings** (Executive Summary / Conclusion, pp.7–8, 37–38):
> "The economic scenario resulted in the highest carbon sequestration — assuming harvested wood stores carbon indefinitely. However, it also led to increased damage from bark beetle outbreaks and windthrow in **Northern and parts of Central Europe**... due to the continued dominance of coniferous species under future climate scenarios, especially in GWL3 [+3°C]."
> "The conservation scenario resulted in the lowest carbon sequestration due to limited harvesting and lower increments. This scenario shifts towards broadleaf species, which reduces the impacts of bark beetles and windstorms in the North. However, it increases the risk of forest fires in Central and Southern Europe due to fuel accumulation from reduced harvesting."
> "The societal scenario resulted in the lowest combined damage from disturbances... but led to the lowest standing biomass."

Quantitative example (Table 4, conservation scenario, EU-27): historical (2001–2020) average annual burned area = 1,072.05 ± 195.76 thousand ha; bark-beetle & windstorm damage = 47.61 ± 9.76 million m³; living stem biomass = 6,186.34 ± 402.43 million tC. Projected **2051–2070 under GWL3/RCP8.5**: burned area rises to 1,816.03 ± 372.69 thousand ha; bark-beetle/windstorm damage falls to 36.87 ± 7.03 million m³ (reflecting the conservation scenario's broadleaf shift); living stem biomass rises to 9,173.58 ± 281.93 million tC.

**Explicit methodological caveats stated by the authors** (important for anyone using these figures to build EnergyScope supply curves):
> "In our assessment, harvest is considered to be a positive factor in computing the cumulative carbon sequestration... we assume that harvested biomass is fully allocated to carbon storage with indefinite duration, which may not accurately reflect real-world carbon dynamics... **disturbances are considered only as biomass loss and did not account for wood recovery from salvage logging**." Management scenarios are "intentionally stylized," and the 5-arcminute resolution "limits realistic representation of actual management behavior." The forest-structure input dataset used is from Pucher et al. (2022) because the updated database described in companion Deliverable **D3.3** was "still under publication embargo" at the time of writing.

**Related ForestNavigator deliverables** (discovered via site sitemap, useful adjacent resources): D3.1 "Alternative management systems," D3.2 "Model Prototype," D3.3 "Climate Sensitive Models" (PREBAS/PICUS/3D-CMCC-FEM report), D2.2 "Forest carbon status and change," D2.4 "Demo GHG Inventory," D4.4 "Forest Management costing," D4.5 "MESMER" (climate/fire-weather emulator), D6.1–D6.4 (Policy Modelling Toolbox), D7.4 "Pathways in global context," D8.1 "Policy coherence Reference Scenario," D9.2 "ForestNavigator Data Explorer." All at `https://www.forestnavigator.eu/wp-content/uploads/FN_D#.#_<slug>.pdf`.

**Potentially useful adjacent reference** (non-PICUS/FLAM, but directly combines Finnish forestry + energy + carbon neutrality modeling): Forsius, M., Holmberg, M., Junttila, V. et al. (2023) "Modelling the regional potential for reaching carbon neutrality in Finland: Sustainable forestry, energy use and biodiversity protection." *Ambio* 52:1757–1776. DOI: 10.1007/s13280-023-01860-1.

---

## 6. Disturbance-aware, time-profiled biomass supply curves — overall answer

**Partially yes, with an important limitation.** The G4M-X + PICUS-disturbance-algorithms + FLAM chain developed under ForestNavigator WP3 (culminating in D3.4) produces **time-stepped (multi-decade), 5-arcmin-gridded, scenario-differentiated outputs** of standing biomass, bark-beetle/windstorm damage volumes (m³), and burned area (ha) across EU-27 (including Finland) — in principle the raw material for disturbance-aware, time-profiled biomass supply curves. However, the deliverable explicitly states that **salvage-wood recovery from disturbances is not yet modeled** ("disturbances are considered only as biomass loss… did not account for wood recovery from salvage logging") — so the assortment-level, usable-biomass-after-disturbance supply curve an EnergyScope coupling would need is **not yet a direct, ready-made IIASA output**; it would require either (i) requesting unpublished/in-progress salvage-logging extensions from the IIASA/BOKU team, or (ii) the research team building its own salvage-recovery post-processing on top of D3.4's biomass-loss outputs. This is a concrete, well-grounded question to raise directly with the IIASA team in the meeting.

---

## Key References (consolidated)

**G4M**
- Kindermann, G.E., Obersteiner, M., Rametsteiner, E., McCallum, I. (2006). "Predicting the deforestation-trend under different carbon-prices." *Carbon Balance and Management* 1:15. DOI: 10.1186/1750-0680-1-15.
- Kindermann, G., Obersteiner, M., Sohngen, B., Sathaye, J., Andrasko, K., Rametsteiner, E., Schlamadinger, B., Wunder, S., Beach, R. (2008). "Global cost estimates of reducing carbon emissions through avoided deforestation." *PNAS* 105(30):10302–10307. DOI: 10.1073/pnas.0710616105.
- Gusti, M. (2010). "An algorithm for simulation of forest management decision in the global forest model." *Shtuchniy Intelekt (Artificial Intelligence)*, N4, pp.45–49. [No DOI; **not independently verified full-text** — cited via Lauri et al. 2017 bibliography — **GAP**.]
- Gusti, M., Kindermann, G. (2011). "An Approach to Modeling Landuse Change and Forest Management on a Global Scale." *Proc. 1st Int. Conf. on Simulation and Modeling Methodologies, Technologies and Applications (SIMULTECH 2011)*, pp.180–185. DOI: 10.5220/0003607501800185.
- Kindermann, G.E., Schörghuber, S., Linkosalo, T., Sanchez, A., Rammer, W., Seidl, R., Lexer, M.J. (2013). "Potential stocks and increments of woody biomass in the European Union under different management and climate scenarios." *Carbon Balance and Management* 8:2. DOI: 10.1186/1750-0680-8-2.
- Di Fulvio, F., Forsell, N., Lindroos, O., Korosuo, A., Gusti, M. (2016). "Spatially explicit assessment of roundwood and logging residues availability and costs for the EU 28." *Scandinavian Journal of Forest Research*. DOI: 10.1080/02827581.2016.1221128.
- Lauri, P., Havlík, P., Kindermann, G., Forsell, N., Böttcher, H., Obersteiner, M. (2014). "Woody biomass energy potential in 2050." *Energy Policy* 66:19–31. DOI: 10.1016/j.enpol.2013.11.033.
- Lauri, P., Forsell, N., Korosuo, A., Havlík, P., Obersteiner, M., Nordin, A. (2017). "Impact of the 2°C target on global woody biomass use." *Forest Policy and Economics* 83:121–130. DOI: 10.1016/j.forpol.2017.07.005.
- Forsell, N., Turkovska, O., Gusti, M., Obersteiner, M., den Elzen, M., Havlik, P. (2016). "Assessing the INDCs' land use, land use change, and forest emission projections." *Carbon Balance and Management* 11:26. DOI: 10.1186/s13021-016-0068-3.
- Gusti, M., Di Fulvio, F., Forsell, N. (2020). "An Algorithm for Simulation of Shelterwood Logging on the Forest Scale for the Global Forest Model (G4M)." 2020 IEEE 15th CSIT, pp.74–77. DOI: 10.1109/csit49958.2020.9322015. (Also as book chapter: DOI 10.1007/978-3-030-63270-0_50.)
- Havlík, P., Schneider, U.A., Schmid, E., et al. (2011). "Global land-use implications of first and second generation biofuel targets." *Energy Policy* 39(10):5690–5702. DOI: 10.1016/j.enpol.2010.03.030.
- Havlík, P., Valin, H., Herrero, M., et al. (2014). "Climate change mitigation through livestock system transitions." *PNAS* 111(10):3709–3714. DOI: 10.1073/pnas.1308044111.

**PICUS / iLand**
- Lexer, M.J., Hönninger, K. (2001). "A modified 3D-patch model for spatially explicit simulation of vegetation composition in heterogeneous landscapes." *Forest Ecology and Management* 144(1–3):43–65. DOI: 10.1016/S0378-1127(00)00386-8.
- Seidl, R., Lexer, M.J., Jäger, D., Hönninger, K. (2005). "Evaluating the accuracy and generality of a hybrid patch model." *Tree Physiology* 25(7):939–951. DOI: 10.1093/treephys/25.7.939.
- Irauschek, F., Rammer, W., Lexer, M.J. (2017). "Evaluating multifunctionality and adaptive capacity of mountain forest management alternatives under climate change in the Eastern Alps." *European Journal of Forest Research* 136:1051–1069. DOI: 10.1007/s10342-017-1051-6.
- Seidl, R., Rammer, W., Scheller, R.M., Spies, T.A. (2012). "An individual-based process model to simulate landscape-scale forest ecosystem dynamics" [iLand]. *Ecological Modelling* 231:87–100. DOI: 10.1016/j.ecolmodel.2012.02.015.
- Seidl, R., Rammer, W., Spies, T.A. (2014). "Disturbance legacies increase the resilience of forest ecosystem structure, composition, and functioning." *Ecological Applications* 24(8):2063–2077. DOI: 10.1890/14-0255.1.

**FLAM**
- Khabarov, N., Krasovskii, A., Obersteiner, M., Swart, R., Dosio, A., San-Miguel-Ayanz, J., Durrant, T., Camia, A., Migliavacca, M. (2016). "Forest fires and adaptation options in Europe." *Regional Environmental Change* 16:21–30. DOI: 10.1007/s10113-014-0621-0.
- Krasovskii, A., Khabarov, N., Migliavacca, M., Kraxner, F., Obersteiner, M. (2016). "Regional aspects of modelling burned areas in Europe." *International Journal of Wildland Fire* 25(8):811–818. DOI: 10.1071/WF15012.
- Krasovskii, A., Khabarov, N., Pirker, J., Kraxner, F., Yowargana, P., Schepaschenko, D., Obersteiner, M. (2018). "Modeling Burned Areas in Indonesia: The FLAM Approach." *Forests* 9(7):437. DOI: 10.3390/f9070437. (Note: user-recalled year 2020 is incorrect; actual year is 2018.)
- Cimdins, R., Krasovskiy, A., Kraxner, F. (2022). "Regional Variability and Driving Forces behind Forest Fires in Sweden." *Remote Sensing* 14(22):5826. DOI: 10.3390/rs14225826.
- Corning, S., Boere, E., Krasovskiy, A. et al. (2024). "Flammable futures — storylines of climatic impacts on wildfire events and palm oil plantations in Indonesia." *Environmental Research Letters*. DOI: 10.1088/1748-9326/ad7bcc.

**BeWhere**
- Leduc, S., Schwab, D., Dotzauer, E., Schmid, E., Obersteiner, M. (2008). "Optimal location of wood gasification plants for methanol production with heat recovery." *International Journal of Energy Research* 32(12):1080–1091. DOI: 10.1002/er.1446.
- Leduc, S., Schmid, E., Obersteiner, M., Riahi, K. (2009). "Methanol production by gasification using a geographically explicit model." *Biomass and Bioenergy* 33(5). DOI: 10.1016/j.biombioe.2008.12.008.
- Leduc, S., Starfelt, F., Dotzauer, E., Kindermann, G., McCallum, I., Obersteiner, M., Lundgren, J. (2010). "Optimal location of lignocellulosic ethanol refineries with polygeneration in Sweden." *Energy* 35(6):2709–2716. DOI: 10.1016/j.energy.2009.07.018.
- Wetterlund, E., Leduc, S., Dotzauer, E., Kindermann, G. (2012). "Optimal localisation of biofuel production on a European scale." *Energy* 41(1):462–472. DOI: 10.1016/j.energy.2012.02.051.
- Leduc, S., Wetterlund, E., Dotzauer, E., Kindermann, G. (2012). "CHP or Biofuel Production in Europe?" *Energy Procedia* 20:40–49. DOI: 10.1016/j.egypro.2012.03.006.
- Natarajan, K., Leduc, S., Pelkonen, P., Tomppo, E., Dotzauer, E. (2014). "Optimal locations for second generation Fischer Tropsch biodiesel production in Finland." *Renewable Energy* 62:319–330. DOI: 10.1016/j.renene.2013.07.013.
- Leduc, S., Kindermann, G., Forsell, N., Kraxner, F. (2015). "Bioenergy Potential from Forest Biomass." In *Handbook of Clean Energy Systems*. DOI: 10.1002/9781118991978.hces101.

**ForestNavigator**
- Krasovskiy, A., Jo, H.-W., Lexer, M., Johnstone, C., Park, E., Kraxner, F. (2025). *D3.4 Assessment of natural disturbances and extreme events impact on forest mitigation potential.* ForestNavigator Deliverable, Grant Agreement 101056875. `https://www.forestnavigator.eu/wp-content/uploads/FN_D3.4_Disturbances-assessment.pdf`.
- ForestNavigator Deliverable D3.3, "Climate Sensitive Models," `https://www.forestnavigator.eu/wp-content/uploads/FN_D3.3_Climate_Sensitive_Models.pdf`.
- CORDIS project page: `https://cordis.europa.eu/project/id/101056875`.
- Forsius, M., Holmberg, M., Junttila, V. et al. (2023). "Modelling the regional potential for reaching carbon neutrality in Finland: Sustainable forestry, energy use and biodiversity protection." *Ambio* 52:1757–1776. DOI: 10.1007/s13280-023-01860-1.

---

## Summary of flagged gaps / items to raise directly with IIASA
1. **Gusti (2010)** could not be retrieved in full text (non-indexed Ukrainian journal, no DOI) — its "current management" algorithm is known only second-hand via Lauri et al. (2017)'s paraphrase.
2. No **deadwood** carbon pool was found explicitly named as a separate G4M output variable in the accessible literature (may exist in inaccessible IIASA interim reports).
3. **No dedicated Finland-specific or Nordic-specific G4M study** was found; Finland is resolved as one of many EU/global countries, never as a sole subject.
4. **G4M↔GLOBIOM recursive-solving mechanics** (price feedback from GLOBIOM back into G4M harvest decisions) are described only at a high level in the accessible texts.
5. **PICUS's native bark-beetle/wind modules were switched off** in ForestNavigator's EU-wide D3.3 climate-sensitivity exercise; D3.4's disturbance algorithms are PICUS-*derived* process algorithms coupled to G4M-X, not a full re-run of the native stand-level PICUS model.
6. **For Northern Europe/Finland, PREBAS (not PICUS) is the climate-sensitive growth model** used in ForestNavigator's regional model partition — worth clarifying with IIASA which model underlies any Finland-specific growth projections.
7. **No FLAM application specific to Finland exists yet** (Sweden 2022 study is the closest proxy); no direct FLAM→G4M (vs. FLAM→GLOBIOM) coupling paper was found outside of D3.4's new fuel-module description.
8. **Salvage-wood recovery after disturbance is explicitly NOT modeled** in D3.4 — a key gap for anyone wanting ready-made disturbance-aware, assortment-level biomass supply curves.
9. A requested **Schipfer-authored BeWhere paper on HWP/construction-wood/sawmill supply chains could not be located or verified** — worth asking IIASA whether this exists under a different title/venue.
10. **Full ForestNavigator consortium list, start/end dates, and total budget** could not be retrieved (JavaScript-rendered pages); recommend checking `forestnavigator.eu/about/who-we-are/` and the CORDIS fact sheet directly in a browser.
11. Several institutional repositories/search engines (IIASA PURE's browse/search UI, Google/Bing/DuckDuckGo general search, MDPI direct access) were blocked by anti-bot protections during this research; direct PDF links (via Semantic Scholar/Unpaywall/OpenAlex open-access fields) were the reliable access route — some grey literature (IIASA interim reports, working papers) may therefore be under-represented above.
