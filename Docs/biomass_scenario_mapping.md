# Biomass Supply Scenarios: Forest Literature → EnergyScope Finland Parameters

> **Authors:** Matthieu Bordenave  
> **Date:** 2026-06 (revised after source audit and Blattert/Mönkkönen consistency check)  
> **Purpose:** Translate Blattert et al. (2022) policy scenarios and Mönkkönen et al. (2024) ecological ceiling into EnergyScope FI 2035 biomass resource parameters. Provides full traceability for paper Section 4 (scenario parameterisation). Companion files: `Data/2035/FI/Resources_S1_BES.csv`, `Resources_S2_NFS.csv`, `Resources_S3_BDS.csv`.

---

## 1. Forest Literature Synthesis

### 1.1 Blattert et al. (2022) — Three National Policy Scenarios

**Full citation:** Blattert C., Eyvindson K., Hartikainen M., Burgas D., Potterf M., Lukkarinen J., Snäll T., Toraño-Caicoya A., Mönkkönen M. (2022). Sectoral policies cause incoherence in forest management and ecosystem service provisioning. *Forest Policy and Economics* 136, 102689. https://doi.org/10.1016/j.forpol.2022.102689

Blattert et al. translate three Finnish national sectoral policy documents into quantitative management scenarios and simulate their long-term (2016–2116) effects on ecosystem services using the SIMO forest simulator on NFI data (39,445 representative stands, all Finland).

#### Scenario constraints and targets (Blattert Table 2)

| Criterion | **S1 — BES** (Bioeconomy Strategy) | **S2 — NFS** (National Forest Strategy 2015–2025) | **S3 — BDS** (Biodiversity Strategy 2012) |
|---|---|---|---|
| **Primary objective** | Maximize roundwood + bioenergy (even-flow), step 1 | Roundwood ≥ 80 Mm³ and increment ≥ 115 Mm³ (2025), ≥ 125 Mm³ (2050) — **hard constraints**, step 1 | Maximize wood production (even-flow) under biodiversity constraints, step 1 |
| **Bioenergy target** | Maximize even-flow under biodiversity constraints, step 2 | **≥ 6.5 Mm³/yr** from 2025 (hard constraint) | No target; harvest minimised by large set-aside |
| **Deadwood** | No decline allowed (constraint) | ≥ 8 m³/ha national average (2025, hard constraint) | **+60% vs 2020 level** by 2050 (hard constraint) |
| **Set-aside (SA)** | No explicit target | 4.5% conservation regimes in commercial forests | **17% strictly protected** (CBD target) |
| **Carbon sink** | Not targeted | ≥ 27.88 MtCO₂/yr (2025, hard constraint) | Not targeted (implied via protection) |
| **Management mix** | IBAU ~33%, SA ~36%, CCF ~19% | CCF dominant (~41%), IBAU, SA | SA ~50%, remainder split |

#### Simulated outcomes at ~2035 (Blattert Section 3.2 and Figure 7)

- **NFS**: Follows the 80 Mm³ roundwood and 6.5 Mm³ bioenergy hard targets from 2025 onwards. Carbon sink constraint met only under RCP 4.5.
- **BES**: "*Mobilized less roundwood and more biomass in comparison to NFS.*" Achieves only **75% of the maximum possible harvest** when biodiversity non-decline is simultaneously enforced (Blattert Fig. 6b text). BES roundwood is therefore **below NFS's 80 Mm³ hard target**, while bioenergy residues are higher.
- **BDS**: Lowest harvest levels; deadwood highest; large carbon sink.
- **Carbon sink (end-period)**: NFS ≈ 80 MtCO₂/yr; BES ≈ 28 MtCO₂/yr; BDS peaks then may go negative.

> **Critical implication for this study:** BES does NOT produce the highest total WOOD energy. BES substitutes roundwood (→ less black liquor/bark) for residues (→ more logging chips). The net total biomass energy under BES is approximately equivalent to NFS. The +20% assumption in S1 is therefore a **stylised upper bound**, not a direct Blattert simulation result. See §3.5 for full discussion.

#### Finnish forest baseline (Blattert)

| Parameter | Value | Source |
|---|---|---|
| Annual increment (Finland, NFI12) | **108 Mm³/yr** | Blattert §2.1, citing Peltola et al. (2019) |
| Total roundwood harvest (2018) | **78.2 Mm³/yr** (historic high) | Blattert §1 |
| Fraction under strict protection | ~11% | Blattert §2.1 |

### 1.2 Mönkkönen et al. (2024) — Ecological Harvest Ceiling

**Full citation:** Mönkkönen M., Blattert C., Cours J., Duflot R., Elo M., Eyvindson K., Kouki J., Triviño M., Burgas D. (2024/preprint). Ecologically and economically sustainable level of timber harvesting in boreal forests – defining the safe operating space for forest use. *bioRxiv* 2024.06.27.600997. https://doi.org/10.1101/2024.06.27.600997

Mönkkönen et al. use SIMO + multi-objective optimisation on **Southern Finland** (hemiboreal + south + middle boreal) to find the maximum harvest level compatible with achieving IUCN Favourable Reference Values (FRVs) for forest habitat types.

#### Geographic scope — critical caveat

> ⚠️ **The Mönkkönen (2024) ceiling applies to Southern Finland only.** The northern boreal zone (28% of Finland's heath forests) is excluded because less than 5% of harvested timber originates there. The 96% / 58–60% figures are therefore for Southern Finland and should not be applied without adjustment to national statistics.

#### Key quantitative findings

| Indicator | Value | Location |
|---|---|---|
| Current harvest (Southern FI, 2016–2021 average) | **96% of maximum economically sustainable potential** | Fig. 4b |
| Ecological ceiling (FRV by 2100) | **58–60% of maximum economically sustainable potential** | Results text |
| Limiting criterion | Proportion of old-growth forest (most constrained variable) | Fig. 3 |

#### Favourable Reference Values (FRVs) used to define the ceiling (Mönkkönen Table 1)

| Indicator | Site type | FRV target (50% of 1750 ref) | Current |
|---|---|---|---|
| Deadwood (m³/ha) | Herb-rich forests | **28** | 4.9 |
| Deadwood (m³/ha) | Mesic forests | **19** | 4.7 |
| Old-growth forest (% cover) | Mesic | **12.5%** | 0.1% |

Required management mix to reach FRVs: >1/3 set-aside + 40% intensive + 25% extensive.

### 1.3 Key Limitations for Energy System Modelling

1. **Geographic scope mismatch**: Blattert (2022) covers all Finland; Mönkkönen (2024) covers only Southern Finland. ENSPRESO covers Finland at NUTS0 (national) level.
2. **Time resolution**: Blattert simulates 2016–2116 in 5-year steps. EnergyScope uses a 2035 snapshot where scenarios have not yet diverged substantially; differences widen considerably by 2050–2100.
3. **No WOOD composition modelling**: EnergyScope aggregates all forest biomass (black liquor, bark, chips, logging residues) into a single WOOD resource. Blattert distinguishes roundwood, residues, and stumps. The scenario mapping captures the total energy ceiling but not the composition shift (less roundwood, more residues under BES).

---

## 2. Scenario Labelling and Cross-Reference

The three scenarios used in this study are aligned across Blattert (2022), Mönkkönen (2024), the IIASA concept note, and EnergyScope:

| This study label | IIASA label | Blattert (2022) | Mönkkönen (2024) harvest level | Primary EnergyScope change |
|---|---|---|---|---|
| **S1 / BES** | Intensive | BES — Bioeconomy Strategy | ~96% of max sustainable (current intensity) | WOOD +20% above ENS_Med (*stylised upper bound*) |
| **S2 / NFS** | Balanced | NFS — National Forest Strategy 2015–2025 | ~80% of max sustainable | WOOD = ENS_Med 2050 (current baseline, unchanged) |
| **S3 / BDS** | Conservation | BDS — Biodiversity Strategy 2012 | ~58–60% of max sustainable (FRV ceiling) | WOOD = ENS_Low 2030 (−33% vs baseline) |

> **Note on S1/BES:** Blattert finds BES achieves less roundwood than NFS (75% of max possible harvest under biodiversity constraints) while mobilising more residues. The net total WOOD energy under BES is approximately neutral vs NFS — not +20% higher. The S1/BES parameterisation is therefore a **stylised high-biomass sensitivity scenario**, not a direct representation of Blattert's simulated BES harvest. The paper should state this explicitly.

---

## 3. Quantitative Parameter Derivation

### 3.1 Finnish forest data (confirmed sources)

| Parameter | Value | Source |
|---|---|---|
| Finland annual increment (NFI12) | **108 Mm³/yr** | Blattert (2022) §2.1, citing Peltola et al. (2019) |
| 2018 total roundwood harvest | **78.2 Mm³/yr** | Blattert (2022) §1 |
| Southern FI current harvest vs max sustainable | **96%** | Mönkkönen (2024) Fig. 4b |
| Max economically sustainable harvest (back-calc.) | **~81 Mm³/yr** | 78.2 / 0.96 |
| S3 FRV ceiling (Southern Finland, year 2100) | **58–60% of max sustainable** | Mönkkönen (2024) Results |
| S3 implied Finland-wide ceiling (indicative only) | **~49 Mm³/yr** | 60% × 81 Mm³; note: derived from Southern FI data |
| NFS bioenergy target (hard constraint) | **≥ 6.5 Mm³/yr** | Blattert (2022) Table 2 |
| NFS roundwood target (hard constraint) | **≥ 80 Mm³/yr** | Blattert (2022) Table 2 |
| BES harvest level under biodiversity constraints | **75% of max possible** | Blattert (2022) Fig. 6b |
| BDS deadwood target | **+60% by 2050** | Blattert (2022) Table 2 |

### 3.2 Volume-to-energy conversion factors

| Biomass category | Factor | Unit | Basis |
|---|---|---|---|
| Roundwood (primary log) | 2.0 | MWh/solid m³ | Finnish national statistics (Luke); ~50% moisture, LHV |
| Forest residues (branches, tops) | 1.5 | MWh/solid m³ | Standard Finnish energy accounting |
| Energy wood thinnings (wet) | 1.2 | MWh/solid m³ | Higher moisture, shorter chips |

> **Reconciliation note:** Blattert's NFS bioenergy minimum (6.5 Mm³ × 1.5 MWh/m³ = **9.75 TWh**) is a policy-minimum floor constraint, not a maximum potential. ENSPRESO ENS_Med 2050 reports the total mobilisable fuelwood residue potential (MINBIOFRSR1) as **38.5 TWh** for Finland. Both are consistent: Blattert constrains the system to mobilise at least 6.5 Mm³; the physical ceiling reported by ENSPRESO is ~25.7 Mm³ (38.5 / 1.5 MWh/m³), which is well above the policy minimum.

### 3.3 Primary data source: ENSPRESO (EC/JRC Biomass Potentials)

**Dataset:** ENSPRESO (ENergy System Potentials for RENewable Supply Options), European Commission / JRC. File: `Data/exogenous_data/ENSPRESO/ENSPRESO_BIOMASS.xlsx`.

All 2035 baseline biomass values in `Data/2035/FI/Resources.csv` are sourced from **ENSPRESO ENS_Med**. This is confirmed in `Data/exogenous_data/FI_baseline_inputs_provenance_2035_2050.csv`.

ENSPRESO provides three mobilisation scenarios:

| ENSPRESO scenario | Mobilisation level | Analogue (this study) |
|---|---|---|
| **ENS_High** | Maximum technical potential; aggressive residue extraction | S1 / BES (capped — see §3.5) |
| **ENS_Med** | Moderate mobilisation | S2 / NFS = current model baseline |
| **ENS_Low** | Minimum mobilisation; residue retention | S3 / BDS |

#### Competing uses: already handled by ENSPRESO

ENSPRESO reports *energy-available* potentials **after** deducting industrial competing demand. Specifically:
- **`MINBIOWOOa` ("C&P_RW")**: Energy from *by-products* of chemical and physical wood processing (black liquor, bark, sawdust from pulp/paper/sawmills). The raw industrial roundwood is excluded.
- **`MINBIOFRSR1` ("Fuelwood residues")**: Logging branches and tops net of the roundwood extracted for industry.

No additional correction for industrial competing uses is needed in EnergyScope.

#### Complete ENSPRESO Finland forestry data (extracted directly from `ENER - NUTS0 EnergyCom` sheet)

All values confirmed by direct Python extraction from `ENSPRESO_BIOMASS.xlsx`. Units: TWh/yr. Conversion: 1 PJ = 0.27778 TWh.

| Scenario | Year | MINBIOWOOa (C&P by-prod.) | MINBIOFRSR1 (Fuel.resid.) | MINBIOWOOW1 (Woodchips) | MINBIOWOOW1a (Sawdust) | MINBIOWOO (Fuelwood) | MINBIOFRSR1a (Landsc.care) | **WOOD TOTAL** |
|---|---|---|---|---|---|---|---|---|
| ENS_Low | 2030 | 43.2 | 20.7 | 4.4 | 1.8 | 2.9 | 1.2 | **74.22** |
| ENS_Low | 2050 | 46.8 | 9.6 | 2.2 | 0.9 | 3.1 | 0.6 | 63.28 |
| ENS_Med | 2030 | 45.9 | 41.4 | 8.9 | 3.7 | 3.1 | 2.4 | 105.33 |
| **ENS_Med** | **2050** | **53.8** | **38.5** | **8.9** | **3.7** | **3.6** | **2.4** | **110.81** ← model baseline |
| ENS_High | 2030 | 52.2 | 124.3 | 22.1 | 9.2 | 3.5 | 6.0 | 217.34 |
| ENS_High | 2050 | 64.7 | 120.2 | 22.1 | 9.2 | 4.3 | 6.0 | 226.59 |

**Baseline verification:** ENS_Med 2050 = 110.81 TWh = 110,810 GWh ≈ model WOOD baseline **110,806 GWh** ✓ (4 GWh rounding only).

### 3.4 EnergyScope resource category definitions (ENSPRESO glossary, confirmed)

The EnergyScope resources map to ENSPRESO as follows (confirmed from `Glossary` sheet of `ENSPRESO_BIOMASS.xlsx`):

| EnergyScope resource | ENSPRESO commodity codes | Description | Forest-management-sensitive? |
|---|---|---|---|
| **`WOOD`** | MINBIOWOOa + MINBIOFRSR1 + MINBIOWOOW1 + MINBIOWOOW1a + MINBIOWOO + MINBIOFRSR1a | Industrial by-products (black liquor, bark) + logging residues (branches/tops) + secondary woodchips + sawdust + direct fuelwood + landscape care residues | **YES — primary scenario lever** |
| **`BIOMASS_RESIDUES`** | MINBIOAGRW1 | **"Agricultural waste"** (straw, stover) — **NOT** forest residues | Marginal; varies with agricultural scenario |
| **`WET_BIOMASS`** | MINBIOSLU1 (+ possibly biogas fraction) | **"Sludge"** — NOT energy wood; utility/population driven | No |
| `ENERGY_CROPS_2` | MINBIOCRP31 + MINBIOCRP41 | Miscanthus, switchgrass, willow | No |
| `BIOWASTE` | MINBIOMUN1 | Municipal waste | No |

> **Critical mapping note:** Blattert's "bioenergy biomass" (logging residues, NFS target ≥ 6.5 Mm³/yr) corresponds to `MINBIOFRSR1` inside the **WOOD** resource, **not** to `BIOMASS_RESIDUES`. The `BIOMASS_RESIDUES` resource is agricultural straw/stover (MINBIOAGRW1). All forest management effects act through **WOOD only**.

#### WOOD composition at ENS_Med 2050 (= model baseline, 110.81 TWh)

| Component | TWh | % of WOOD | Sensitivity to forest management |
|---|---|---|---|
| MINBIOWOOa — C&P by-products (black liquor, bark, sawdust) | 53.8 | 48.5% | Scales with industrial roundwood processing volume |
| MINBIOFRSR1 — Fuelwood residues (logging branches/tops) | 38.5 | 34.7% | **Most sensitive** — reduced by deadwood retention, residue harvest intensity |
| MINBIOWOOW1 — Secondary woodchips | 8.9 | 8.0% | Scales with sawmill/chip production |
| MINBIOWOOW1a — Sawdust | 3.7 | 3.3% | Scales with sawnwood production |
| MINBIOWOO — Direct fuelwood | 3.6 | 3.2% | Relatively independent |
| MINBIOFRSR1a — Landscape care residues | 2.4 | 2.2% | Relatively independent |

### 3.5 WOOD resource: scenario parameterisation and consistency checks

#### S2 / NFS: current model baseline (unchanged)

**Value: 110,806 GWh (110.81 TWh)**

ENSPRESO ENS_Med 2050 = 110.81 TWh = 110,810 GWh, matching the model baseline to within 4 GWh (rounding). The NFS scenario in Blattert targets 80 Mm³ roundwood (≈ current harvest of 78.2 Mm³) — ENS_Med is the natural ENSPRESO analogue for this harvest intensity level.

*No change from baseline required.*

#### S3 / BDS: ENS_Low 2030

**Value: 74,200 GWh (74.22 TWh = ENSPRESO ENS_Low 2030)**

**Primary source:** Direct extraction from `ENSPRESO_BIOMASS.xlsx`, NUTS0 Finland, ENS_Low, year 2030.

**Consistency with Blattert BDS:** The dominant driver of the WOOD reduction is `MINBIOFRSR1` (logging residues): from **38.5 TWh** (ENS_Med 2050) → **20.7 TWh** (ENS_Low 2030), a **−46% reduction**. This directly reflects the BDS deadwood target (+60% by 2050): achieving this requires leaving most logging residues in the forest rather than harvesting them. Additionally, MINBIOWOOa (industrial by-products) drops from 53.8 → 43.2 TWh (−20%), consistent with BDS having the lowest roundwood production (Blattert Fig. 7a).

**Consistency with Mönkkönen (2024):** Mönkkönen's FRV ceiling = 58–60% of max sustainable ≈ 60/96 × 110.81 TWh = **69.3 TWh**. The ENS_Low 2030 value (74.22 TWh = 67% of ENS_Med 2050) is slightly above this ceiling (difference: 7%); this is within scenario uncertainty, and ENS_Low is more conservative than Mönkkönen's national-level implication because: (a) Mönkkönen covers Southern Finland only — northern forests are less intensively managed; (b) ENS_Low year 2030 uses a more near-term (hence conservative) mobilisation projection.

**Comparison of derivation methods:**

| Derivation method | WOOD value (TWh) | Source |
|---|---|---|
| ENSPRESO ENS_Low 2030 (direct) | **74.22** ← used | `ENSPRESO_BIOMASS.xlsx` |
| Mönkkönen 60% ceiling applied to ENS_Med 2050 | 69.3 | Mönkkönen (2024) Fig. 4b |
| Blattert: 49 Mm³ × 2.0 MWh/m³ (roundwood) + residues | ~65–70 | Blattert (2022) + Luke conversions |

ENS_Low 2030 = 74.22 TWh was the initial choice because it is a direct ENSPRESO data point and broadly consistent with both alternative derivations.

> ⚠️ **Revision (May 2026):** A post-ENSPRESO cross-check against LUKE 2024 statistics and Mönkkönen (2024) harvest-ceiling calculations revealed that ENS_Low 2030 overestimates the biomass available under a genuine biodiversity-constrained scenario by approximately a factor of 2. The S3-BDS supply has been revised downward to conservative literature-based values. See §3.5.1 below and §11 (Revision History).

#### 3.5.1 LUKE 2024 cross-check and S3-BDS revision (May 2026)

**Problem identified:** The ENSPRESO ENS_Low 2030 supply total (74.22 TWh) does not account for two interacting constraints specific to the BDS scenario:
1. The Mönkkönen (2024) ecological harvest ceiling being simultaneously binding with industrial roundwood demand;
2. ENSPRESO's "energy-available after industrial deduction" assumption using a fixed industrial demand that does not scale down when total harvest is capped.

Three independent lines of evidence support a downward revision:

**Evidence 1 — LUKE 2024 observed data (Finnish national wood energy statistics):**
- Logging residues (MINBIOFRSR1 proxy) actually used for energy in Finland in 2024: **2.6 million m³ = ~5.1 TWh**. This is under the *current intensive harvest regime* (~75 Mm³/yr). The S3-BDS model WOOD_FI2 = 20.7 TWh is **4× the current observed utilisation**, yet S3-BDS represents a *lower*-harvest scenario.
- Forest industry wood by-products at solid fuels CHP+heat plants: **10.1 Mm³ = ~20 TWh from solid streams** (black liquor reported separately by Statistics Finland). The WOOD_FI1 = 43 TWh includes black liquor, but a proportional reduction in industrial processing will reduce by-product availability.
- Source: LUKE (2024) *Wood in energy generation 2024*, Natural Resources Institute Finland.

**Evidence 2 — Mönkkönen (2024) harvest ceiling + residue calculation:**
- Biodiversity-safe FRV ceiling at national level: ~49 Mm³/yr (from 60% × 81 Mm³ max sustainable, adjusted for Northern Finland not covered by Mönkkönen).
- Logging residue fraction of merchantable volume: ~15–20% → technical potential at FRV ceiling = 49 × 0.175 = **~8.6 Mm³ technical**.
- Collection efficiency in low-harvest, conservation-priority regime: **30–40%** (dispersed, hard-to-access, leaving deadwood for habitat) → **collectable logging residues ≈ 2.6–3.4 Mm³ = 3.9–5.1 TWh**.
- ENSPRESO ENS_Low 2030 WOOD_FI2 = 20.7 TWh is **4–5× this literature estimate**.

**Evidence 3 — Competing industrial roundwood demand:**
- Finnish forest industry roundwood consumption (LUKE 2024): **~48 Mm³/yr** (sawlogs + pulpwood for domestic use).
- Under a BDS harvest ceiling of ~49 Mm³/yr, essentially all harvestable roundwood is consumed by industry, leaving **~0–5 Mm³** for direct energy wood (WOOD_FI3 + WOOD_FI4).
- ENSPRESO's deduction for industrial competing uses is calibrated on a fixed assumption that does not account for the BDS harvest ceiling simultaneously binding with industrial demand. The interaction is not captured by simply using ENS_Low.

**ENSPRESO disclaimer:** ENSPRESO documents that its potentials represent "energy-available quantities after deducting traditional industrial wood demand." However, this deduction uses a *fixed reference* industrial demand trajectory. In the BDS scenario, total harvest is simultaneously capped at ~49 Mm³/yr — a level close to industrial roundwood demand alone. The "residual for energy" is therefore near-zero for WOOD_FI3/FI4, and significantly lower than ENSPRESO's fixed-deduction implies for WOOD_FI2.

**Decision (May 15, 2026):** Apply conservative S3-BDS supply values based on the three-line-of-evidence audit. Values are set deliberately above the lower bound of each estimate to avoid over-correction, while remaining conservative relative to ENSPRESO ENS_Low 2030:

| Tier | ENSPRESO ENS_Low 2030 | Conservative revision | Change | Rationale |
|---|---:|---:|---:|---|
| WOOD_FI1 (industrial by-products) | 43,188 GWh | **32,000 GWh** | −26% | BDS reduces roundwood processing → less bark/sawdust/black liquor; proportional to ↓ harvest vs baseline |
| WOOD_FI2 (logging residues) | 20,690 GWh | **6,000 GWh** | −71% | Literature ceiling: 3.9–5.1 TWh at FRV harvest; 6 TWh allows modest 2035 collection efficiency improvement |
| WOOD_FI3 (secondary woodchips) | 6,272 GWh | **1,500 GWh** | −76% | Industry-competing; with harvest capped, secondary wood goes to industry; small remainder |
| WOOD_FI4 (fuelwood/landscape) | 4,071 GWh | **500 GWh** | −88% | BDS 17% set-aside (Blattert); conservation areas dominate; fuelwood marginalised |
| **Total domestic (FI1–FI4)** | **74,221 GWh** | **40,000 GWh** | **−46%** | Consistent with literature estimates; factor-of-2 correction |

**Patch files:**
- Active: `calibration/patches/fi_forest_S3_BDS.csv` — updated to conservative values
- Archive: `calibration/patches/fi_forest_S3_BDS_enspreso_low2030.csv` — original ENSPRESO ENS_Low 2030 values preserved for reproducibility
- Data: `Data/2035/FI/Resources_S3_BDS.csv` — updated to match conservative values

**Runs using original values:** All 9 runs completed before this revision (3 forest × 3 GHG: unconstrained, 80%, 95%) plus 3 nuclear phase-out runs launched 2026-05-15 before this revision. These S3-BDS runs are **archived but should not be used for final analysis**; re-runs with conservative values are required (see §11).

#### S1 / BES: stylised high-biomass scenario

**Value: 132,967 GWh = ENS_Med 2050 × 1.20**

**Why ENS_High cannot be used directly:** ENS_High 2030 reports `MINBIOFRSR1` = 447.6 PJ = **124.3 TWh of fuelwood residues alone** for Finland. This is physically impossible: at current harvest levels (~78 Mm³/yr) and a maximum residue fraction of ~30% of merchantable volume, total available residues are approximately 20–25 TWh. The ENS_High figure (5× the plausible ceiling) is an aggregation artefact in ENSPRESO. ENS_High is therefore unusable directly for Finland.

**Rationale for +20%:** Blattert's BES maximises bioenergy residues as a step-2 objective and the political orientation of BES favours maximum biomass mobilisation. Assuming aggressive residue extraction ~5 Mm³/yr above the NFS minimum (additional 7.5 TWh at 1.5 MWh/m³) yields WOOD ≈ 118–120 TWh. The +20% cap (132.97 TWh) is a conservative upper bound providing a clearly distinct scenario, while the choice of +20% is stylised.

> **Honest caveat for the paper:** The S1/BES value (132,967 GWh) is a **stylised upper-bound sensitivity scenario**, not a direct derivation from Blattert's simulation. Blattert finds BES achieves only **75% of maximum possible harvest** under biodiversity constraints, and BES produces *less roundwood* than NFS (no 80 Mm³ hard target). The net total WOOD energy under BES in Blattert's model is approximately equal to (or slightly below) NFS, not +20% above it. The +20% assumption therefore represents what would happen if a BES-oriented policy succeeded in maximising residue mobilisation beyond the NFS minimum — it should not be presented as a direct Blattert result.

| Scenario | WOOD avail_local (GWh/yr) | c_op_local (€/kWh) | Source and status |
|---|---|---|---|
| **S1 / BES** | **132,967** | 0.02208 | ENS_Med 2050 × 1.20; stylised high-biomass sensitivity |
| **S2 / NFS** | **110,806** | 0.02208 | ENSPRESO ENS_Med 2050; directly confirmed; unchanged |
| **S3 / BDS** | **74,200** | 0.02600 | ENSPRESO ENS_Low 2030; directly confirmed; consistent with Mönkkönen |

*S3 c_op raised +18% (0.02208 → 0.02600 €/kWh) to reflect harder-to-access, more dispersed residue resources under conservation management.*

### 3.6 BIOMASS_RESIDUES: agricultural waste (MINBIOAGRW1)

`BIOMASS_RESIDUES` maps to `MINBIOAGRW1` = "Agricultural waste" in ENSPRESO (confirmed from `Glossary` sheet). This is agricultural straw and stover — **not** forest logging residues. It varies across ENSPRESO scenarios but is **not affected by forest management policy**.

ENSPRESO Finland values for MINBIOAGRW1 (extracted from `ENSPRESO_BIOMASS.xlsx`):

| Scenario | Year | PJ | TWh | Notes |
|---|---|---|---|---|
| ENS_Low | 2030 | 12.22 | **3.40** | Used for S3/BDS |
| ENS_Med | 2030 | 17.94 | **4.98** | = current model baseline (4,985 GWh) ✓ |
| ENS_High | 2030 | 23.77 | **6.60** | Used for S1/BES |

**Verification:** ENS_Med 2030 = 4.984 TWh matches model baseline `BIOMASS_RESIDUES = 4,985.24 GWh` ✓ (confirming the MINBIOAGRW1 mapping).

The variation (3.4–6.6 TWh, ±32% of baseline) is modest relative to WOOD (74–133 TWh) and has second-order effects on overall system behaviour.

| Scenario | BIOMASS_RESIDUES (GWh/yr) | c_op (€/kWh) | Source |
|---|---|---|---|
| **S1 / BES** | **6,600** | 0.01313 | ENSPRESO ENS_High 2030 = 6.60 TWh |
| **S2 / NFS** | **4,985** | 0.01313 | ENSPRESO ENS_Med 2030 = 4.98 TWh (baseline) |
| **S3 / BDS** | **3,400** | 0.01313 | ENSPRESO ENS_Low 2030 = 3.40 TWh |

### 3.7 WET_BIOMASS: sewage sludge (MINBIOSLU1) — unchanged across scenarios

`WET_BIOMASS` maps primarily to `MINBIOSLU1` = "Sludge" in ENSPRESO (confirmed from `Glossary` sheet). This resource is completely unrelated to forest management policy.

ENSPRESO Finland values for MINBIOSLU1 (extracted from `ENSPRESO_BIOMASS.xlsx`):

| Scenario | Year | PJ | TWh |
|---|---|---|---|
| ENS_Low | 2030 | 2.236 | 0.621 |
| ENS_Med | 2030 | 3.036 | 0.843 |
| ENS_Med | 2050 | 4.065 | 1.129 |
| ENS_High | 2030 | 3.674 | 1.020 |
| ENS_High | 2050 | 5.366 | 1.490 |

> **Note on WET_BIOMASS calibration:** The model value `WET_BIOMASS = 1,451 GWh` does not match any single ENSPRESO MINBIOSLU1 entry exactly (nearest: ENS_High 2050 = 1.49 TWh). The provenance CSV describes it as "sewage sludge food waste," suggesting it aggregates sludge with biogas from food/organic waste from a Finnish national statistics source rather than ENSPRESO alone. This uncertainty does not affect scenario parameterisation since WET_BIOMASS is held constant across all forest scenarios.

**All scenarios: WET_BIOMASS = 1,451 GWh (unchanged)**

### 3.8 Non-forest resources (unchanged across all scenarios)

`ENERGY_CROPS_2`, `BIOWASTE`, and `WASTE` are independent of forest management policy.

| Resource | GWh/yr | c_op (€/kWh) | Note |
|---|---|---|---|
| WET_BIOMASS | 1,451 | 0.03310 | Unchanged |
| ENERGY_CROPS_2 | 7,754 | 0.02352 | Unchanged |
| BIOWASTE | 4,721 | 0.000112 | Unchanged |
| WASTE | 11,095 | 0.006079 | Unchanged |

---

## 4. Consistency Check: ENSPRESO Values vs Blattert and Mönkkönen

### 4.1 S2/NFS: strong consistency

| Check | Result |
|---|---|
| ENS_Med 2050 = 110.81 TWh vs model baseline 110,806 GWh | ✓ Exact match (4 GWh rounding) |
| NFS roundwood target (80 Mm³) ≈ 2018 actual harvest (78.2 Mm³) | ✓ ENS_Med represents the NFS-equivalent harvest intensity |
| NFS bioenergy floor (6.5 Mm³ × 1.5 MWh/m³ = 9.75 TWh) vs FRSR1 ceiling (38.5 TWh) | ✓ Consistent: 9.75 TWh is the policy minimum; 38.5 TWh is the total mobilisable ceiling |
| BIOMASS_RESIDUES baseline (4,985 GWh) vs MINBIOAGRW1 ENS_Med 2030 (4,984 GWh) | ✓ Exact match |

**S2/NFS is the strongest and most directly confirmed of the three scenarios.**

### 4.2 S3/BDS: revised after LUKE 2024 cross-check

> **Status (May 2026):** The initial ENSPRESO ENS_Low 2030 values have been revised downward following a LUKE 2024 statistical cross-check and competing-use analysis. See §3.5.1 for full rationale.

**Original ENSPRESO consistency (maintained for documentation):**

| Check | Result |
|---|---|
| ENS_Low 2030 = 74.22 TWh vs Mönkkönen 60% ceiling = 69.3 TWh | ✓ Consistent within 7%; small difference attributed to Mönkkönen covering Southern FI only |
| MINBIOFRSR1: ENS_Med 2050 (38.5 TWh) → ENS_Low 2030 (20.7 TWh) = −46% | ✓ Directly reflects BDS deadwood +60% constraint requiring residue retention in-forest |
| MINBIOWOOa: 53.8 → 43.2 TWh = −20% | ✓ Consistent with BDS having lowest roundwood production (Blattert Fig. 7a) |
| BIOMASS_RESIDUES ENS_Low 2030 (3.40 TWh) below baseline | ✓ Consistent |
| Geographic scope: Mönkkönen = Southern FI only; ENSPRESO = all Finland | ⚠️ The Mönkkönen 60% ceiling is slightly stricter than what a national-level application would yield; ENS_Low 2030 is therefore slightly more conservative than Mönkkönen |

**Post-revision checks (conservative values FI1=32,000, FI2=6,000, FI3=1,500, FI4=500 GWh):**

| Check | Result |
|---|---|
| Revised total (40.0 TWh) vs Mönkkönen harvest-ceiling-based estimate (37.8–39.6 TWh) | ✓ Conservative revision ≈ literature estimate; 40 TWh allows modest upside for 2035 collection efficiency improvement |
| WOOD_FI2 revised (6.0 TWh) vs LUKE 2024 actual logging residues (5.1 TWh) | ✓ ~20% above observed 2024 level; consistent with some improvement by 2035 |
| WOOD_FI1 revised (32.0 TWh) vs proportional reduction: 43.2 × (49 Mm³ / 65 Mm³ baseline) | ✓ 43.2 × 0.75 ≈ 32.4 TWh; 32.0 GWh is consistent |
| WOOD_FI3+FI4 revised (2.0 TWh total) vs competing-use analysis (~0–5 Mm³ left for energy) | ✓ Plausible given industry demand absorbs most of available harvest |
| BIOMASS_RESIDUES (3.40 TWh from MINBIOAGRW1 ENS_Low 2030) | ✓ Unchanged; agricultural waste unaffected by forest harvest constraints |

**S3/BDS revised values are grounded in LUKE 2024 observed data and Mönkkönen (2024) ceiling. Confidence: Moderate-to-Good (was: Good).**

### 4.3 S1/BES: weaker grounding — acknowledged as stylised

| Check | Result |
|---|---|
| Blattert finding: BES achieves 75% of max possible harvest; less roundwood than NFS | ⚠️ In strict Blattert terms, total WOOD energy under BES ≈ NFS, NOT +20% above it |
| BES: more bioenergy residues, less roundwood → net effect ≈ neutral on WOOD total | ⚠️ The +20% assumption overstates BES vs NFS in total WOOD energy |
| ENS_High 2030 = 217 TWh: FRSR1 = 124 TWh alone (5× plausible maximum) | ✗ ENS_High is unusable directly for Finland (aggregation artefact) |
| +20% above ENS_Med = 132.97 TWh: reasonable stylised upper bound | ✓ Defensible as sensitivity analysis; not a direct Blattert derivation |
| BIOMASS_RESIDUES ENS_High 2030 = 6.60 TWh | ✓ Directly confirmed from ENSPRESO |

**S1/BES must be framed in the paper as a stylised high-biomass sensitivity scenario consistent with a BES political orientation, not as a direct simulation of Blattert's BES outcomes.**

### 4.4 Hierarchy of scenario confidence

| Scenario | WOOD grounding | BIOMASS_RESIDUES grounding | Overall confidence |
|---|---|---|---|
| S2 / NFS | **Strong** — exact ENSPRESO match; consistent with Blattert NFS harvest targets | **Strong** — exact ENSPRESO match | **High** |
| S3 / BDS | **Moderate-to-Good** — conservative values revised May 2026 from ENSPRESO ENS_Low 2030 after LUKE 2024 cross-check; three independent lines of evidence; values are literature-anchored but carry ~±30% uncertainty on FI2–FI4 | **Good** — direct ENSPRESO ENS_Low | **Moderate-to-Good** |
| S1 / BES | **Weak** — stylised +20%; Blattert simulation shows BES total WOOD ≈ NFS, not +20% above | **Good** — direct ENSPRESO ENS_High | **Moderate — must disclose in paper** |
| S2 / NFS | **Strong** — exact ENSPRESO match; consistent with Blattert NFS harvest targets | **Strong** — exact ENSPRESO match | **High** |
| S3 / BDS | **Good** — direct ENSPRESO ENS_Low 2030; consistent with Blattert BDS (lowest harvest) and Mönkkönen ceiling within 7% | **Good** — direct ENSPRESO ENS_Low | **Good** |
| S1 / BES | **Weak** — stylised +20%; Blattert simulation shows BES total WOOD ≈ NFS, not +20% above | **Good** — direct ENSPRESO ENS_High | **Moderate — must disclose in paper** |

---

## 5. Summary: EnergyScope Parameter Table by Scenario

> All values confirmed against ENSPRESO `ENSPRESO_BIOMASS.xlsx`. Provenance: `Data/exogenous_data/FI_baseline_inputs_provenance_2035_2050.csv`. CSV files: `Data/2035/FI/Resources_S*.csv`. ‡ S3/BDS revised May 2026 (see §3.5.1).

| Resource | **2035 Baseline (S2-NFS)** | **S1 / BES** | **S2 / NFS** | **S3 / BDS** ‡ | S1 vs base | S3 vs base |
|---|---|---|---|---|---|---|
| WOOD_FI1 (GWh/yr) | 45,442 | **54,530** | **45,442** | **32,000** | +20% | −30% |
| WOOD_FI2 (GWh/yr) | 38,214 | **45,857** | **38,214** | **6,000** | +20% | −84% |
| WOOD_FI3 (GWh/yr) | 12,543 | **15,052** | **12,543** | **1,500** | +20% | −88% |
| WOOD_FI4 (GWh/yr) | 5,420 | **6,504** | **5,420** | **500** | +20% | −91% |
| **WOOD total domestic** | **101,619** | **121,943** | **101,619** | **40,000** | **+20%** | **−61%** |
| BIOMASS_RESIDUES (GWh/yr) | 4,985 | **6,600** | **4,985** | **3,400** | +32% | −32% |
| WET_BIOMASS (GWh/yr) | 1,451 | 1,451 | 1,451 | 1,451 | 0% | 0% |
| ENERGY_CROPS_2 (GWh/yr) | 7,754 | 7,754 | 7,754 | 7,754 | 0% | 0% |
| BIOWASTE (GWh/yr) | 4,721 | 4,721 | 4,721 | 4,721 | 0% | 0% |
| WASTE (GWh/yr) | 11,095 | 11,095 | 11,095 | 11,095 | 0% | 0% |
| **Total domestic biomass ceiling** | **125,625** | **152,063** | **125,625** | **67,470** | **+21%** | **−46%** |
| WOOD_FI2 c_op (€/kWh) | 0.022 | 0.022 | 0.022 | **0.026** | — | +18% |

**Notes:**
- **WOOD (FI1–FI4)**: Only resource significantly affected by forest management. S2/NFS = ENSPRESO ENS_Med 2035 (interpolated); S1/BES = ENS_Med 2035 × 1.20 (stylised upper bound — see §3.5 and §4.3); **S3/BDS = conservative values revised May 2026** ‡.
- **BIOMASS_RESIDUES**: Agricultural waste (ENSPRESO MINBIOAGRW1), NOT forest logging residues. Varies ±32% across scenarios but absolute magnitude is small relative to WOOD.
- **WET_BIOMASS**: Sewage sludge / biogas from organic waste. Independent of forest management; unchanged across all scenarios.
- **WOOD_FI2 c_op S3**: 0.026 €/kWh — dispersed residue collection premium maintained from original ENS_Low assumption.

‡ **S3/BDS revised May 2026.** Original ENSPRESO ENS_Low 2030 values: FI1=43,188, FI2=20,690, FI3=6,272, FI4=4,071 GWh (total 74,221 GWh). Conservative revision based on LUKE 2024 + Mönkkönen 2024 competing-use analysis. Archive patch: `calibration/patches/fi_forest_S3_BDS_enspreso_low2030.csv`.

---

## 6. Expected Model Behaviour under Forest Scenarios

Based on the GHG sweep results from `Docs/finland_2035_ghg_sweep_results.md` (Scenario A, baseline nuclear), total biomass demand at different GHG reduction levels:

| GHG savings | Demand (TWh) | % of S1 ceiling (165 TWh) | % of S2/base ceiling (141 TWh) | % of S3 ceiling (113 TWh) |
|---|---|---|---|---|
| Unconstrained | 63.4 | 38% | 45% | 56% |
| 70% | 63.7 | 39% | 45% | 56% |
| 80% | 61.9 | 38% | 44% | 55% |
| 90% | 65.0 | 39% | 46% | 58% |
| **95%** | **85.2** | **52%** | **60%** | **76%** |

All three scenarios are technically feasible across all GHG reduction levels tested (maximum 76% of ceiling reached under S3 at 95% GHG savings). The binding constraint is cost, not volume: S3 imposes a higher WOOD c_op (+18%), making deep decarbonisation more expensive even when the ceiling is not approached. Running the GHG sweep independently under each scenario would quantify this cost penalty.

**Core scenario message:**
- **S2/NFS → S3/BDS**: WOOD ceiling −33%, total biomass ceiling −20%. Does not make any GHG target infeasible, but shifts the cost-optimal system toward more electrification and higher overall cost.
- **S2/NFS → S1/BES**: WOOD ceiling +20%, total biomass ceiling +17%. Provides additional flexibility, especially at 95% GHG reduction (demand reaches 60% of baseline ceiling but only 52% of S1 ceiling).

---

## 7. Caveats and Limitations

1. **S1/BES is a stylised scenario.** Blattert (2022) Fig. 6b shows BES achieves only 75% of maximum possible harvest under biodiversity constraints, and BES produces less roundwood (→ less black liquor/bark energy) than NFS. The net total WOOD energy under BES is approximately equal to NFS in Blattert's model, not +20% above. S1 should be presented as a sensitivity for high biomass availability, not a direct BES simulation result.

2. **Geographic scope mismatch.** Mönkkönen (2024) covers Southern Finland only (hemiboreal, south and middle boreal). Northern boreal forests are excluded. The 58–60% FRV ceiling is therefore stricter than a strict national-level equivalent. ENS_Low 2030 (74.22 TWh = 67% of ENS_Med) is slightly more conservative than a strict national-level interpretation of Mönkkönen's ceiling (69.3 TWh = 62.5% of ENS_Med), but within scenario uncertainty.

3. **No LULUCF / forest carbon accounting.** Blattert finds NFS produces a ~80 MtCO₂/yr carbon sink while BES produces only ~28 MtCO₂/yr and BDS produces the largest sink. These LULUCF effects are not captured in EnergyScope's GHG constraint (which covers energy system emissions only). Including forest carbon would substantially penalise S1/BES and potentially reward S3/BDS.

4. **Single aggregate WOOD resource (no supply curve).** EnergyScope does not distinguish black liquor (constant, tied to pulp industry) from variable energy chips and logging residues. A more accurate representation would use a stepped supply curve separating black liquor, logging residues, and commercial energy chips at different costs. This decomposition is planned for future versions.

5. **2035 snapshot — scenarios not yet fully diverged.** Blattert's scenarios diverge most dramatically by 2050–2100. At 2035, forest stocks and management outcomes are still relatively close to the current state; the scenario differences would be much larger at 2050.

6. **ENS_High unusable for S1/BES.** ENSPRESO ENS_High 2030 gives MINBIOFRSR1 = 124 TWh (5× the plausible physical upper bound for Finland). This is an aggregation artefact. ENS_High is not used.

7. **WET_BIOMASS provenance uncertainty.** Model value (1,451 GWh) does not match any single ENSPRESO category exactly. Likely aggregates sludge (MINBIOSLU1) with biogas from food/organic waste from Finnish national statistics. Does not affect forest scenario parameterisation (WET_BIOMASS is held constant).

---

## 8. Data Files

| File | Description |
|---|---|
| `Data/2035/FI/Resources_S1_BES.csv` | S1/BES stepped supply: FI1=54,530, FI2=45,857, FI3=15,052, FI4=6,504 GWh; BIOMASS_RESIDUES=6,600 GWh |
| `Data/2035/FI/Resources_S2_NFS.csv` | S2/NFS stepped supply: FI1=45,442, FI2=38,214, FI3=12,543, FI4=5,420 GWh; BIOMASS_RESIDUES=4,985 GWh |
| `Data/2035/FI/Resources_S3_BDS.csv` | S3/BDS stepped supply (**conservative, revised May 2026**): FI1=32,000, FI2=6,000, FI3=1,500, FI4=500 GWh; BIOMASS_RESIDUES=3,400 GWh |
| `calibration/patches/fi_forest_S1_BES.csv` | Patch applying S1-BES WOOD_FI1–FI4 values over baseline |
| `calibration/patches/fi_forest_S3_BDS.csv` | Patch applying **conservative** S3-BDS WOOD_FI1–FI4 values (updated May 2026) |
| `calibration/patches/fi_forest_S3_BDS_enspreso_low2030.csv` | **Archive** — original ENSPRESO ENS_Low 2030 values before revision: FI1=43,188, FI2=20,690, FI3=6,272, FI4=4,071 GWh |
| `calibration/patches/fi_nuclear_phaseout_strong_2035.csv` | Nuclear phase-out: NUCLEAR f_min=0, f_max=0; applied for `ghg_95pct_nonuke` runs |
| `Data/exogenous_data/ENSPRESO/ENSPRESO_BIOMASS.xlsx` | Primary ENSPRESO source |
| `Data/exogenous_data/FI_baseline_inputs_provenance_2035_2050.csv` | Full provenance for 2035 baseline |

---

## 9. References

- **Blattert et al. (2022)**: Sectoral policies cause incoherence in forest management and ecosystem service provisioning. *Forest Policy and Economics* 136, 102689. https://doi.org/10.1016/j.forpol.2022.102689
- **Mönkkönen et al. (2024/preprint)**: Ecologically and economically sustainable level of timber harvesting in boreal forests. *bioRxiv* 2024.06.27.600997. https://doi.org/10.1101/2024.06.27.600997
- **ENSPRESO**: Ruiz P., Nijs W., Tarvydas D., Sgobbi A., Zucker A., Pilli R., Jonsson R., Camia A., Thiel C., Hoyer-Klick C., Dalla Longa F., Kober T., Badger J., Volker P., Elbersen B., Brosowski A., Thrän D. (2019). ENSPRESO - an open, EU-28 wide, transparent and coherent database of wind, solar and biomass energy potentials. *Energy Strategy Reviews* 26, 100379.
- **Colla et al. (2022)**: Optimal use of lignocellulosic biomass for the energy transition. *Applied Energy* 313, 118783.
- **LUKE (2022)**: Wood Energy Statistics 2022. Natural Resources Institute Finland (Luke), Helsinki.
- **LUKE (2024)**: Wood in energy generation 2024. Natural Resources Institute Finland (Luke), Helsinki. [Accessed May 2026 — statistics on logging residues (2.6 Mm³ = 5.1 TWh), forest industry by-products (10.1 Mm³ = ~20 TWh solid fuels), and total solid wood fuel consumption (43.1 TWh at CHP+heat plants).]

---

## 10. Run Matrix and GHG Scenario Design

### 10.1 Forest × GHG run matrix

All model runs are stored under `case_studies/FI/forest_scenarios_2035/<timestamp>__<SCEN>__<GHG>/`. The complete run matrix (as of May 2026 revision) is **3 forest scenarios × 4 GHG configurations = 12 runs**. Orchestration script: `scripts/run_forest_scenarios_2035.py`.

| GHG target key | Label | GWP limit (ktCO₂/yr) | Savings vs 2017 | Extra patch | Notes |
|---|---|---:|---:|---|---|
| `unconstrained` | Unconstrained | none | 0% | — | Cost-optimal baseline; no climate constraint |
| `ghg_95pct` | −95% GHG (with nuclear) | **2,060** | 95% | — | Nuclear baseline: f_min=4.36 GW, f_max=5.0 GW |
| `ghg_95pct_nonuke` | −95% GHG (nuclear phase-out) | **2,060** | 95% | `fi_nuclear_phaseout_strong_2035.csv` | NUCLEAR f_min=0, f_max=0; see §10.2 |

**GHG baseline: Finland 2017 total energy-system GHG = 41,200 ktCO₂/yr.**

> **Why the 80% target was dropped:** An initial matrix included `ghg_80pct` (GWP limit = 8,240 ktCO₂/yr, 80% savings). This was replaced by `ghg_95pct_nonuke` because: (a) the 80% constraint is near-trivially satisfied in most forest scenarios — cost-optimal electrification already approaches 80% GHG reduction; (b) the `ghg_95pct_nonuke` column provides more policy-relevant information by isolating the nuclear contribution to deep decarbonisation feasibility. Old 80% runs remain archived in `case_studies/FI/forest_scenarios_2035/`.

### 10.2 Nuclear phase-out patch design

**Rationale:** Finland's 2035 nuclear baseline assumes continued operation of all existing units plus Olkiluoto 3 (OL3, 1.6 GW, commercial since 2023) and the currently existing Loviisa 1+2 (2×1.0 GW) and Olkiluoto 1+2 (2×0.88 GW). Total installed capacity: ~5.36 GW; model baseline: f_min=4.36 GW (committed base-load dispatch), f_max=5.0 GW. Hanhikivi-1 (1.2 GW) was cancelled in 2022.

The nuclear phase-out scenario (`ghg_95pct_nonuke`) tests whether Finland can achieve −95% GHG without nuclear, addressing the policy debate on long-term nuclear dependence.

**Patch** (`calibration/patches/fi_nuclear_phaseout_strong_2035.csv`):
```
file,parameter,technology_or_resource,value
Technologies.csv,f_min,NUCLEAR,0.0
Technologies.csv,f_max,NUCLEAR,0.0
```
Setting both `f_min = 0` and `f_max = 0` fully excludes nuclear from the optimised 2035 system ("strong" phase-out).

**Confirmed in solver output:**
```
PATCH FI.Technologies[NUCLEAR].f_min: 4.36 -> 0.0
PATCH FI.Technologies[NUCLEAR].f_max: 5.0  -> 0.0
```

**Run orchestration:** The `run_forest_scenarios_2035.py` `GHG_TARGETS` dict triggers automatic patch application for the `95nuke` key:
```python
"95nuke": {
    "label":       "ghg_95pct_nonuke",
    "gwp_limit":   2060,
    "savings_pct": 95,
    "extra_patches": ["calibration/patches/fi_nuclear_phaseout_strong_2035.csv"],
}
```

### 10.3 Visualisation columns

`scripts/plot_forest_scenarios.py` configuration (as of May 2026 revision):
```python
GHG_TARGETS = ["unconstrained", "ghg_95pct_nonuke", "ghg_95pct"]
GHG_LABELS  = ["Unconstrained", "−95% GHG\n(nuclear phase-out)", "−95% GHG\n(with nuclear)"]
```

---

## 11. Revision History

| Date | Revision | Decision | Affected files |
|---|---|---|---|
| Initial (pre-May 2026) | 9-run matrix (3 forest × 3 GHG: unconstrained, 80%, 95%); S3-BDS uses ENSPRESO ENS_Low 2030 (FI1=43,188, FI2=20,690, FI3=6,272, FI4=4,071 GWh = 74,221 GWh total) | — | `fi_forest_S3_BDS.csv`, `Resources_S3_BDS.csv` |
| 2026-05-15 — Revision A | **S3-BDS conservative supply revision.** Original ENSPRESO ENS_Low 2030 values overestimated FI2–FI4 by ~3–4× based on: (1) LUKE 2024 actual logging residue use = 5.1 TWh; (2) Mönkkönen 2024 FRV harvest ceiling → collectable residues 3.9–5.1 TWh; (3) competing industrial roundwood demand absorbs all harvest at BDS ceiling. New values: FI1=32,000, FI2=6,000, FI3=1,500, FI4=500 GWh (total 40,000 GWh, −46%). | User confirmed "yes ok for conservative" | `fi_forest_S3_BDS.csv`, `Resources_S3_BDS.csv`, `biomass_scenario_mapping.md` |
| 2026-05-15 — Revision B | **80% GHG target replaced by `ghg_95pct_nonuke`.** Nuclear phase-out patch created (NUCLEAR f_min=f_max=0). Run script updated with `extra_patches` support. 3 new runs launched (S1-BES, S2-NFS, S3-BDS × `ghg_95pct_nonuke`). | User request | `run_forest_scenarios_2035.py`, `fi_nuclear_phaseout_strong_2035.csv`, `plot_forest_scenarios.py` |
| 2026-05-15 — Revision C | **Supply curve plot updated** with over-estimation zone annotation (green shaded region 40–74 TWh, citation to Mönkkönen 2024 + LUKE 2024). Archive: `fi_forest_S3_BDS_enspreso_low2030.csv`. | — | `plots/plot_biomass_supply_curves.py`, `calibration/patches/fi_forest_S3_BDS_enspreso_low2030.csv` |
| 2026-05-15 — Revision D | **Conservative S3-BDS re-runs completed.** All 3 GHG targets re-run with updated patch (FI1=32 k, FI2=6 k, FI3=1.5 k, FI4=0.5 k GWh). Directories: `20260515_184611__S3_BDS__unconstrained` (obj=22615), `20260515_191047__S3_BDS__ghg_95pct` (obj=23561), `20260515_193120__S3_BDS__ghg_95pct_nonuke` (obj=23902). Note: `20260515_183056__S3_BDS__ghg_95pct_nonuke` also used conservative values (patch read after file update). `find_run()` updated to return most-recent completed run. Energy matrix and biomass allocation plots regenerated. | — | All `case_studies/FI/forest_scenarios_2035/2026051518*__S3_BDS__*`, `scripts/plot_forest_scenarios.py`, `plots/forest_scenarios_2035_energy_matrix.png`, `plots/forest_scenarios_2035_biomass_allocation.png` |
