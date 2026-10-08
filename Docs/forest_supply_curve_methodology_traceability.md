# Finnish wood supply steps (WOOD_FI1–FI5): methodology, mapping, numbers and traceability

**Status:** audit note, 2026-10-08. Nothing in the model, `Data/`, `calibration/patches/` or any run was modified.
**Scope:** how the wood availability per category, the costs and the GHG factors used in paper 1 were
built, converted to model units, assigned to scenarios S1/S2/S3, and applied in the 9 canonical runs.
**Verification script (read-only, re-runnable):** [`scripts/check_forest_supply_traceability.py`](../scripts/check_forest_supply_traceability.py)
(`python scripts/check_forest_supply_traceability.py`, last run: ALL PASS on the checks it performs).

Legend: ✅ re-derived from source by me and matches · ⚠️ matches but with a caveat · ❌ inconsistency found · ❓ could not be verified.

---

## 1. Pipeline at a glance

```
ENSPRESO_BIOMASS.xlsx            sheet "ENER - NUTS0 EnergyCom"   (Finland, PJ/yr, by energy-commodity code)
   │  1 PJ = 277.78 GWh (x 1000/3.6)                                        [no m³ involved]
   ▼
6 ENSPRESO codes ──grouped──► 4 domestic steps WOOD_FI1..FI4  (+ FI5 import backstop, not from ENSPRESO)
   │  S2: mean(ENS_Med 2030, 2040)   S1: S2 x 1.20   S3: ENS_Low 2030 then hand-revised
   ▼
Data/2035/FI/Resources.csv (= S2) ; calibration/patches/fi_forest_S1_BES.csv, fi_forest_S3_BDS.csv
   │  runs read Resources.csv + patch(es)   (NOT the Resources_S*.csv files, see issue T6)
   ▼
ESMC_model_AMPL.mod  avail_local [GWh/y]  →  Eq.12:  Σ_t,h (R_t_local · t_op) ≤ avail_local
   ▼
paper1/results/*/Resources.csv (R_year_local) → paper table "domestic wood used"
```

There is **no hourly availability**. The cap is annual (GWh/y); the optimiser decides the timing across typical days.

---

## 2. Units and conversion factors

| Quantity | Source unit | Model unit | Conversion | Status |
|---|---|---|---|---|
| Availability | ENSPRESO PJ/yr | `avail_local` GWh/y | 1 PJ = 277.78 GWh (TWh ×1000) | ✅ recomputed |
| Cost, ENSPRESO (cross-check only) | €2010/GJ | `c_op_local` M€/GWh (= €/kWh) | ×3.6 → €/MWh | ✅ |
| Model cost | – | `c_op_local` 0.011 = 11 €/MWh | 1 M€/GWh = 1 €/kWh | ✅ ([.mod](../esmc/energy_model/ESMC_model_AMPL.mod) L162) |
| GHG | RED II Annex VI via Colla 2022, tCO₂eq/GWh | `gwp_op_local` ktCO₂/GWh | ÷1000 (21.6 t/GWh = 0.0216 kt/GWh) | ✅ |
| Volume → energy | m³ | – | 2.0 MWh/m³ roundwood; 1.5 residues; 1.2 wet thinnings | ⚠️ see below |

**Where the volume→energy factors (Docs/biomass_scenario_mapping.md §3.2) are actually used:** *only* in
cross-checks and in the S3 revision. They do **not** enter S1/S2 (ENSPRESO is already energy). Source cited:
Luke "Finnish national statistics, ~50% moisture, LHV"; I could not verify it (no PDF/snapshot in Zotero item
`YGDLIPQH`, Luke site returned HTTP 406). ❓
**Inconsistency (T5):** the S3 chain uses **1.5 MWh/m³**, but the Luke numbers quoted in the same section imply
**1.96 MWh/m³** (2.6 Mm³ = 5.1 TWh) and **1.98** (10.1 Mm³ ≈ 20 TWh). The basis (solid vs loose m³, moisture, LHV
as received) is not stated.

---

## 3. Source mapping: ENSPRESO codes → steps

Repo mapping ([biomass_supply_curve_fi.md §2.1](./biomass_supply_curve_fi.md)) and what the ENSPRESO workbook's own
Glossary says (I read both):

| Step | ENSPRESO code(s) | Repo/paper interpretation | ENSPRESO Glossary text (workbook) | Status |
|---|---|---|---|---|
| FI1 | `MINBIOWOOa` | **Model uses it as a by-product proxy** (black liquor, bark, sawdust); ENSPRESO *formally* labels it stemwood chips/pellets | JRC EUR 27575: "additionally harvestable stemwood → woodchips and pellets"; Glossary "C&P_RW – Chips and Pellets" | ⚠️ **T1 decision (tracker §7):** by-product proxy adopted, ENSPRESO-label mismatch disclosed |
| FI2 | `MINBIOFRSR1` | Logging residues (branches, tops, stumps) | "Fuelwood residues; *not used in BaU forestry scenarios*" | ✅ plausible |
| FI3 | `MINBIOWOOW1` + `W1a` | Secondary woodchips + sawdust | "Secondary forestry residues – woodchips" / "Sawdust"; *from GFTM in BaU* | ✅ |
| FI4 | `MINBIOWOO` + `MINBIOFRSR1a` | Direct fuelwood + landscape-care wood | "FuelwoodRW; *from CBM in BaU (stem and other wood from harvesting)*" / "Residues from landscape care" | ✅ |
| FI5 | – (market) | Baltic/Nordic import backstop | not from ENSPRESO | – |
| `BIOMASS_RESIDUES` | `MINBIOAGRW1` | Agricultural waste (not forest) | "Agricultural waste" | ✅ |

Nothing in the Glossary mentions black liquor or bark, and the JRC report (EUR 27575) confirms that black liquor is **not** an ENSPRESO input (T1, resolved).
The quoted "energy-available quantities after deducting traditional industrial wood demand" is not in the workbook or the ENSPRESO paper, but **the
JRC report supports the substance**: material use is deducted before energy availability ("the stemwood and residues not used for material products are then
available for energy", printed p. 37; competing-use table p. 25). So that part of T9 is closed; the Luke figures remain unverified ❓.
**Model provenance (T10, closed):** per the JRC report §4.2.1 (printed pp. 35–37) EFISCEN gives the potentially harvestable stemwood under the
EFSOS-based High/Medium/Low scenarios, with material use from EFI-GTM; the BaU scenario is separate (JRC CBM + GFTM, ENSPRESO paper).

Step weight: FI1 = 44.7% of S2 domestic supply (45,442 / 101,619).

---

## 4. Availability by step and scenario (GWh/yr) — derivation and verification

Raw ENSPRESO Finland values, recomputed from the workbook (GWh/yr):

| Step (codes) | ENS_Med 2030 | ENS_Med 2040 | ENS_Med 2035 (mean) | ENS_Low 2030 | ENS_Med 2050 | ENS_High 2030 |
|---|---:|---:|---:|---:|---:|---:|
| FI1 `MINBIOWOOa` | 45,952 | 44,933 | 45,442 | 43,188 | 53,776 | – |
| FI2 `MINBIOFRSR1` | 41,380 | 35,047 | 38,214 | 20,690 | 38,512 | 124.3 TWh (see §4.2) |
| FI3 `W1`+`W1a` | 12,543 | 12,543 | 12,543 | 6,271 | 12,543 | – |
| FI4 `WOO`+`FRSR1a` | 5,454 | 5,386 | 5,420 | 4,071 | 5,974 | – |
| **Domestic total** | **105,329** | **97,909** | **101,619** | **74,220** | **110,805** | 217.3 TWh |

### 4.1 Final values used, by scenario

| Step | **S2/NFS** | **S1/BES** | **S3/BDS** | S3 raw ENS_Low 2030 | S3 change |
|---|---:|---:|---:|---:|---:|
| FI1 | 45,442 | 54,530 | **32,000** | 43,188 | −25.9% |
| FI2 | 38,214 | 45,857 | **6,000** | 20,690 | −71.0% |
| FI3 | 12,543 | 15,052 | **1,500** | 6,271 | −76.1% |
| FI4 | 5,420 | 6,504 | **500** | 4,071 | −87.7% |
| FI5 | 1,000,000 | 1,000,000 | 1,000,000 | – | unlimited, never used in any run |
| **Domestic total** | **101,619** | **121,943** | **40,000** | 74,220 | −46.1% |

| Scenario | Rule | Hypothesis / justification (as documented) | Status |
|---|---|---|---|
| S2 NFS | ENS_Med; linear mean of 2030 and 2040 per code, then aggregated | No native 2035 point; 2035 is the midpoint. "Neutral" reference. | ✅ exact (±1 GWh) |
| S1 BES | S2 × 1.20 on all four steps | ENS_High unusable (FI2 = 124 TWh, 5× plausible) so a stylised +20% upper-bound sensitivity; Blattert: BES reaches only 75% of max harvest. | ✅ arithmetic; ⚠️ **stylised, not derived** |
| S3 BDS | ENS_Low **2030** (74.2 TWh) then **hand-revised** to 40.0 TWh on 2026-05-15 | Three-way audit: Luke 2024 observed use, Mönkkönen ceiling, competing industrial demand (§5). | ⚠️ judgement (T4) |

### 4.2 ENS_High rejection
ENS_High 2030 `MINBIOFRSR1` = 124.3 TWh ✅ (workbook). The argument that this is implausible (>3× current harvest-derived
residues) rests on Blattert's 78.2 Mm³ harvest ✅ (Blattert 2022, intro) and an assumed ≤30% residue fraction (assumption).

### 4.3 What the paper tables say vs the data
Paper Table (capacities): S1 54.5 / 45.9 / 15.1 / 6.5 → total printed **122.0**; S2 45.4 / 38.2 / 12.5 / 5.4 → printed **101.5**;
S3 32.0 / 6.0 / 1.5 / 0.5 → **40.0**. Exact sums are 121.943, 101.619, 40.000 → should read **121.9, 101.6, 40.0**
(printed totals are sums of rounded entries) ❌ minor (T8).

---

## 5. S3/BDS revision: numbers re-computed

Documented chain (`biomass_scenario_mapping.md` §3.5.1), all arithmetic re-run:

| Step | Input | Value | Source | Status |
|---|---|---|---|---|
| a | 2018 roundwood harvest | 78.2 Mm³ | Blattert 2022 | ✅ found in text |
| b | Harvest vs max sustainable (S. Finland) | 96% | Mönkkönen 2024 | ✅ |
| c | Max sustainable = a/b | 81.5 Mm³ | derived | ✅ |
| d | Ecological ceiling | 58–60% (60% used) | Mönkkönen 2024 | ✅ ; ⚠️ Southern Finland only, extrapolated nationally |
| e | National ceiling = c × 60% | 48.9 Mm³ | derived | ✅ |
| f | Residue fraction of merchantable volume | 15–20% | assumption | ❓ no source |
| g | Collection efficiency, conservation regime | 30–40% | assumption | ❓ no source |
| h | Collectable residues | see grid | derived | ✅ |

Grid (Mm³ → TWh), residue fraction f × efficiency g:

| f \ g | 0.30 | 0.40 |
|---|---|---|
| 0.15 | 2.20 Mm³ → 3.30 TWh (1.5) / 4.31 (1.96) | 2.93 → 4.40 / 5.75 |
| 0.175 | 2.57 → 3.85 / 5.03 | 3.42 → 5.13 / 6.71 |
| 0.20 | 2.93 → 4.40 / 5.75 | 3.91 → 5.87 / 7.66 |

(MWh/m³ shown as "1.5 / 1.96".) The documented range "3.9–5.1 TWh" is the f = 0.175 row at 1.5 MWh/m³. The adopted
**FI2 = 6.0 TWh sits at the top of the full grid (5.9) at 1.5 MWh/m³**, and inside it at 1.96. ⚠️ (T4/T5)

**What the chain does and does not support:** it addresses **FI2 only**. FI1 (−26%), FI3 (−76%), FI4 (−88%) are justified
qualitatively ("proportional to ↓ harvest", "industry-competing", "17% set-aside"), not derived. For FI1 the harvest ceiling
falls −37% (48.9 vs 78.2 Mm³), not −26%; no formula links the two. ⚠️ (T4)

Other literature inputs checked: Blattert NFS roundwood target 80 Mm³ and bioenergy 6.5 Mm³ ✅; BES "only 75% of max
harvest" ✅; BDS deadwood +60% and 17% protected area ✅; increment 108 Mm³ ✅. Luke: 2.6 Mm³ logging residues = 5.1 TWh;
10.1 Mm³ by-products ≈ 20 TWh; 43.1 TWh solid wood fuel at CHP/heat ❓ unverified.

---

## 6. Costs by step and scenario

| Step | Model `c_op_local` (€/MWh) | S1 | S2 | S3 | Documented basis | ENSPRESO cost, same code(s) (€2010/MWh, Med 2035 / Low 2030) |
|---|---:|---|---|---|---|---|
| FI1 | 11 | 11 | 11 | 11 | "handling only; bark ~10–15 €/MWh mill gate, black liquor ≈ 0" — **consistent with the adopted by-product proxy (tracker §7)**; the ENSPRESO stemwood-chip cost (34.7) applies only to the literal label, not the model's interpretation | **34.7 / 39.9** |
| FI2 | 22 (26 in S3) | 22 | 22 | **26** | 20–25 €/MWh, "matches current calibrated flat price" 0.02208 | 20.5 / 23.5 |
| FI3 | 27 | 27 | 27 | 27 | "slightly higher mobilisation cost, ~25–30" | 7.7 (`W1`), 6.1 (`W1a`) |
| FI4 | 33 | 33 | 33 | 33 | "higher collection effort, ~30–35" | 16.6 (`WOO`), 11.8 (`FRSR1a`) |
| FI5 | 70 | 70 | 70 | 70 | Baltic pellets / Swedish chips, 60–80 €/MWh (2022) + transport | – |

Weighted average domestic cost (recomputed): S2 and S1 **18.3 €/MWh** (same shares), S3 **14.1 €/MWh**.

Findings:
- **Costs are modelling assumptions, not ENSPRESO values.** The stated sources (Finnish Energy Industry, Luke, IEA 2022) are not
  linked to specific numbers anywhere I could find. ❓ (T2)
- Against ENSPRESO's own cost sheet only **FI2 is close**; FI1 is ~3× lower in the model, FI3 ~3.5–4.5× higher, FI4 ~2–3× higher.
  ENSPRESO costs are in €2010 and may not be delivered-to-plant; the model's price year is not stated. Not necessarily an error, but
  it should be disclosed and tested in a sensitivity. ⚠️
- **Merit order is a modelling choice**: FI1 < FI2 < FI3 < FI4 < FI5 by cost, whereas ENSPRESO costs would order FI3 < FI4 < FI2 < FI1.
- The S3 FI2 premium (22 → 26, +18%) is acknowledged in the paper as an explicit assumption; the **other costs are equally assumptions** but
  the paper text presents only that one as such. (ENSPRESO ENS_Low 2030 FI2 is 23.5, +15% over Med 2035 20.5, vs +18% used.)

---

## 7. GHG factors (supply chain only; biogenic combustion excluded)

| Step | tCO₂eq/GWh | Basis | Verified |
|---|---:|---|---|
| FI1 | 10 | "≈ 50% of forest-residue baseline" (50% × 21.6 = 10.8, set to 10) | ⚠️ judgement, not a RED II value |
| FI2 | 22 | Colla 2022 table, local, forest residues (case 3a) = **21.6** | ✅ in Colla PDF |
| FI3 | 14 | "case 7a" **14.4** | ⚠️ in Colla, but 14.4 is Colla's value for *landscape care and other solid biodegradable waste*, used here as a proxy for mill residues |
| FI4 | 19 | 60/40 blend of 21.6 and 14.4 = 18.7 → 19 | ✅ arithmetic; ⚠️ blend weights are an assumption |
| FI5 | 40 | Colla, rest of world, good quality = **39.6** | ✅ in Colla PDF |

Values live in `Data/2035/02_REF_REGION/Resources.csv` (units ktCO₂/GWh: 0.010 / 0.022 / 0.014 / 0.019 / 0.040).
**Applied in the runs ✅:** GWP_op / consumption in run outputs gives 10, 22, 14, 19 tCO₂/GWh exactly. FI5 factor cannot be verified from outputs
because FI5 is never used. Colla's 21.6 refers to *briquettes or pellets from forest residues*, so it implicitly includes pelletising for chips (⚠️).
GHG are the same in all scenarios (no scenario-specific GHG). Documented materiality: the 2026-05 revision of FI1/FI3/FI4 factors lowers supply-chain
GHG by ~600–750 ktCO₂/y at full ceilings, ~25–35% of the −95% budget (2,060 kt) (doc statement, not re-derived).

---

## 8. What the 9 canonical runs actually applied (from `run_metadata.json` and result tables)

| Run | Patches | FI1 / FI2 / FI3 / FI4 used (GWh) | Domestic wood used | `BIOMASS_RESIDUES` avail |
|---|---|---|---:|---:|
| S1 unconstrained | baseline, S1 | 54,530 / 0 / 0 / 0 | 54.5 TWh | 4,985 |
| S1 −95% | baseline, S1 | 54,530 / 19,630 / 0 / 0 | 74.2 | 4,985 |
| S1 −95% no nuclear | + nuclear phase-out | 54,530 / 45,857 / 13 / 0 | 100.4 | 4,985 |
| S2 unconstrained | baseline | 45,442 / 1 / 0 / 0 | 45.4 | 4,985 |
| S2 −95% | baseline | 45,442 / 28,732 / 0 / 0 | 74.2 | 4,985 |
| S2 −95% no nuclear | + nuclear phase-out | 45,442 / 38,214 / 12,543 / 1 | 96.2 | 4,985 |
| S3 unconstrained | baseline, S3 | 32,000 / 1 / 0 / 0 | 32.0 | 4,985 |
| S3 −95% | baseline, S3 | 32,000 / 6,000 / 1,500 / 500 | 40.0 | 4,985 |
| S3 −95% no nuclear | + nuclear phase-out | 32,000 / 6,000 / 1,500 / 500 | 40.0 | 4,985 |

✅ Applied availabilities equal the CSVs/patches in all 9 runs; the paper's "domestic wood used" column (54.5, 74.2, 100.4, 45.4, 74.2, 96.2, 32.0, 40.0, 40.0)
matches the outputs exactly. Runs: 2026-05-18, `td_mode=read`, 12 typical days, `dhn` 0.42–0.50, `gwp_limit` 2,060 kt for −95%.

Observations (from the outputs, not from the docs):
1. **Only FI1 is used in the unconstrained runs, and it is fully used in all three** (54.5 / 45.4 / 32.0 TWh). The unconstrained cost differences
   (22.40 / 22.46 / 22.62 bn€/y) therefore come from the **FI1 ceiling alone**, i.e. from the stylised +20% (S1) and the hand-set −26% (S3).
2. Under −95% with nuclear, S1 and S2 both use **74.2 TWh**; only S3 hits a ceiling (40.0). Without nuclear, S1 uses all of FI1+FI2, S2 all of FI1+FI2+FI3.
3. **FI5 imports are zero in every run**, so cost 70 €/MWh and GHG 40 t/GWh never influenced a result.
4. S3 ceilings are binding in both −95% runs, so S3 results are directly sensitive to the S3 availability judgements.

---

## 9. Other biomass resources (not forest-policy dependent)

| Resource | Code | In scenario CSVs (GWh) | Applied in canonical runs | Status |
|---|---|---|---|---|
| `BIOMASS_RESIDUES` | `MINBIOAGRW1` | S1 6,600 · S2 4,985 · S3 3,400 (= ENS_High 2030 6,602 / Med 4,984 / Low 3,395) | **4,985 in all 9** | ❌ **T6** |
| `ENERGY_CROPS_2`, `BIOWASTE`, `WASTE`, `WET_BIOMASS` | various | identical across scenarios | identical | ✅ |

---

## 10. Issue register (nothing fixed; all need your decision)

| ID | Severity | Issue | Evidence | Suggested action (for your approval) |
|---|---|---|---|---|
| **T1** | **High** | FI1 (`MINBIOWOOa`): the model treats it as an aggregate industrial by-product block (black liquor, bark, sawdust), whereas ENSPRESO *formally* labels it stemwood chips/pellets (JRC EUR 27575). **Resolved by decision 2026-10-08 (tracker §7):** keep the by-product interpretation with the ENSPRESO `MINBIOWOOa` volume as a documented proxy, because black liquor — Finland's largest wood-energy source (43 TWh, 2017) — is absent from ENSPRESO; cost/GHG hypotheses documented; no re-run. Also resolves T12/T13/T14. | JRC EUR 27575 printed pp. 15, 17, 37, 39, 56; Glossary and NUTS2 sheets; Statistics Finland 12vq | Paste REVIEW_FLAGS section G into Overleaf; add JRC report to Zotero; flag for IIASA. |
| **T2** | High | Costs are assumptions without a traceable source; ENSPRESO costs differ strongly (FI1 34.7 vs 11, FI3 ~7 vs 27, FI4 ~12–17 vs 33). | §6 | Add a cost-source table with exact references and price year; consider a cost sensitivity. |
| **T3** | Medium | Unconstrained results hinge on the FI1 ceiling only. | §8 obs. 1 | State this in the discussion; add FI1 ±X% sensitivity. |
| **T4** | Medium | S3 FI1/FI3/FI4 cuts are judgement; FI1 −26% vs harvest −37%; FI2 = 6.0 TWh is the top of the sensitivity grid; residue fraction and efficiency lack sources. | §5 | Document as judgement; show the grid; or replace by G4M output. |
| **T5** | Medium | Conversion factor inconsistency: 1.5 vs ~1.96–1.98 MWh/m³; basis unstated. | §2, §5 | Fix one factor with moisture/LHV basis and a source. Needed anyway for G4M m³ output. |
| **T6** | Medium | Docs/CSVs define scenario-specific `BIOMASS_RESIDUES` (6,600 / 4,985 / 3,400); canonical runs used 4,985 for all. `Resources_S*.csv` are not what the runs read. | §9, run metadata | Correct the docs and paper text; or run a **new** timestamped run if you want the documented values (do not overwrite). |
| **T7** | Medium | Stale documentation: `biomass_supply_curve_fi.md` §4 tables show old GHG (0.020/0.024/0.026) and raw ENS_Low for S3; mapping doc cites a +20% cap of 132.97 TWh (2050 base) vs 121.9 used; run descriptions say "Biodiversity *Enhancement* Scenario" (S1) and "Biodiversity Default… ENS_Low 2030, strict constraints" (S3) although S1 is Bioeconomy and S3 is the revised 40 TWh case. | docs; run_metadata.json | Update docs. Treat run_metadata labels as read-only evidence; note the correct meaning in the paper/REPRODUCIBILITY. |
| **T8** | Low | Paper capacity table totals 122.0 / 101.5 vs exact 121.9 / 101.6. | §4.3 | Correct in the Overleaf snippet (REVIEW_FLAGS). |
| **T9** | Low | "After deducting traditional industrial demand" ENSPRESO quote not found; Luke figures unverifiable (no source file). | §3, §5 | Add the Luke table/PDF to Zotero; cite the exact page. |
| **T10** | Low | Which model (EFISCEN vs CBM/GFTM) produces ENS_Low/Med/High MINBIO* values is unclear. | §3 | Clarify via the ENSPRESO/JRC-EU-TIMES biomass report. |
| **T11** | Info | S3 uses 2030 while S1/S2 use 2035; justified qualitatively, but a timing inconsistency. | §4.1 | Mention in the methods. |

---

## 11. Implications for the G4M coupling (meeting 2026-10-09)

- Your current S1/S2 numbers never needed a m³→energy factor. G4M output in m³ **will**; T5 must be solved first.
- T1 (decided, tracker §7) matters for decision D2: FI1 is modelled as the captive by-product block (black liquor, bark, sawdust); the ENSPRESO
  `MINBIOWOOa` volume proxies it because black liquor is absent from ENSPRESO (T14). Ask G4M/BeWhere for a physically grounded by-product/stemwood split.
- Cost steps (T2) are not provided by G4M either; you will still need an explicit cost basis per assortment.
- The ENSPRESO forestry data are linked to JRC CBM/GFTM (paper §4.1.2); EU-CBM-HAT (Paul Rougieux) is the open successor of that CBM branch.

## 12. Traceability matrix

| Parameter | Value(s) | Source | File | Run evidence | Status |
|---|---|---|---|---|---|
| Availability FI1–FI4 S2 | 45,442 / 38,214 / 12,543 / 5,420 | ENSPRESO ENS_Med 2030/2040 | `Data/2035/FI/Resources.csv` | S2 runs | ✅ |
| Availability S1 | ×1.2 | stylised | `calibration/patches/fi_forest_S1_BES.csv` | S1 runs | ✅ / ⚠️ |
| Availability S3 | 32,000 / 6,000 / 1,500 / 500 | judgement (Blattert, Mönkkönen, Luke) | `calibration/patches/fi_forest_S3_BDS.csv` | S3 runs | ✅ / ⚠️ |
| Raw S3 (superseded) | 43,188 / 20,690 / 6,272 / 4,071 | ENSPRESO ENS_Low 2030 | `fi_forest_S3_BDS_enspreso_low2030.csv` | not used in canonical runs | ✅ |
| Cost | 11 / 22 (26 S3) / 27 / 33 / 70 €/MWh | assumption | Resources CSVs | applied via `c_op_local` | ❓ source |
| GHG | 10 / 22 / 14 / 19 / 40 t/GWh | Colla 2022 (RED II) + judgement | `02_REF_REGION/Resources.csv` | implied factors match | ✅ / ⚠️ |
| Conversion | 1 PJ = 277.78 GWh | definition | – | – | ✅ |
| Cap definition | annual, Eq.12 | model | `ESMC_model_AMPL.mod` L352–354 | – | ✅ |
| Model / data version | `VERSION` 2.0; tag `paper1-finland-forest-v1.0` | repo | `REPRODUCIBILITY.md` | run date 2026-05-18 | ✅ |

**Command to reproduce this audit:** `python scripts/check_forest_supply_traceability.py` (needs `openpyxl`, `pandas`; reads only).
