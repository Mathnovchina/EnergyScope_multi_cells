# Forest supply-curve audit — flags tracker (T1–T14)

Tracks progress on the issues raised in [forest_supply_curve_methodology_traceability.md](./forest_supply_curve_methodology_traceability.md) (§10), plus T12–T14 which arose when T1 was resolved.
Re-run the evidence at any time: `python scripts/check_forest_supply_traceability.py` (add `--online` for the Statistics Finland test).
Rules in force ([AGENTS.md](../AGENTS.md)): no change to `.mod`, `Data/`, `calibration/patches/` or any run under `case_studies/` without explicit approval;
paper/Overleaf edits are author-owned, so corrections go to `paper1/Overleaf_working_paper/REVIEW_FLAGS.md` (section G) as paste-ready snippets.

**Status legend:** 🔴 open · 🟠 in progress · 🟡 awaiting your decision/approval · 🟢 done · ⚪ info only

## 1. Dashboard (updated 2026-10-08 — adopted by-product interpretation, §7)

| ID | Sev. | Issue (short) | Status | Done so far | Next step | Needs |
|---|---|---|---|---|---|---|
| **T1** | High | What is FI1 (`MINBIOWOOa`)? | 🟢 **Resolved by decision (§7): FI1 = aggregate industrial by-products (black liquor, bark, sawdust), ENSPRESO volume used as a documented proxy** | JRC evidence gathered; by-product interpretation adopted and justified; Docs, `Data/` comments, plot scripts, paper draft, concept note all updated; REVIEW_FLAGS G rewritten | Paste REVIEW_FLAGS G into Overleaf; add JRC report to Zotero | You |
| **T12** | Low | FI1/FI3 cost and GHG | 🟢 **Resolved by §7:** under the by-product reading, FI1 cost 11 and GHG 10 are defensible (captive, black-liquor-dominated; 11 is conservative vs a ~2–3 €/MWh blend). No re-run. Residual: FI3 at 27 vs ENSPRESO ~7 (minor, disclosed) | Cost/GHG hypothesis documented | Optional: lower FI3 in a future sensitivity | – |
| **T13** | 🟢 | S3 FI1 = 32 TWh | 🟢 **Resolved by §7:** the −26% S3 cut is valid under the by-product reading (BDS lowers pulp/sawmill throughput → less black liquor/bark/sawdust). No change | Logic restored and documented | – | – |
| **T14** | Med | Black liquor (43 TWh, 2017) not in ENSPRESO | 🟢 **Resolved by §7 (option C, keep-and-disclose):** FI1 is the documented proxy that carries black liquor; stated as a key assumption and flagged for IIASA | Sourced; proxy justified; magnitude match (45 vs 43 TWh) | Flag for IIASA; optional explicit resource later | – |
| T2 | Med | Costs are assumptions | 🟠 | FI1 cost now has a documented hypothesis (§7); FI2 = 22 matches observed chips; FI3/FI4 remain assumptions | Optional cost-source table / sensitivity | – |
| T3 | Med | Unconstrained results hinge on the FI1 ceiling only | 🟠 | Consistent with FI1 = cheap captive by-products | State in discussion; optional FI1 ±X% sensitivity | Decision on a run |
| T4 | Med | S3 FI2/FI3/FI4 cuts are judgement; FI2 = 6.0 TWh at the top of the grid | 🟠 | FI1 cut now justified (§7); FI2–FI4 still judgement | Document or replace by G4M | Decision |
| T5 | Med | Conversion factors disagree (1.5 vs ~1.96 MWh/m³) | 🔴 | – | One factor with moisture/LHV basis and source | Luke source file |
| T6 | Med | `BIOMASS_RESIDUES` 4,985 in all runs vs 6,600/4,985/3,400 in docs | 🔴 | – | Correct docs/paper, or a new run | Decision |
| T7 | Med | Stale docs and run labels | 🟠 | FI1-related text fixed | Fix the remaining stale tables | – |
| T8 | Low | Paper capacity totals should read 121.9/101.6 | 🟡 | Snippet G4 ready | Paste in Overleaf | You |
| T9 | Low | "After deducting industrial demand" quote; Luke figures | 🟠 | Quote **is supported by the JRC report** (§2.2 R5) | Add Luke source | Luke table/PDF |
| T10 | Low | Which model produces ENS_Low/Med/High forestry | 🟢 | JRC report §4.2.1 (printed p. 35–37): EFISCEN under EFSOS High/Medium/Low; material use from EFI-GTM; BaU = CBM + GFTM | – | – |
| T11 | Info | S3 uses 2030, S1/S2 use 2035 | 🔴 | – | Mention in methods | – |

---

## 2. T1 dossier — what is `WOOD_FI1` / `MINBIOWOOa`?

### 2.1 Answer (formal label vs modelling decision)
Two distinct things:
- **Formally (ENSPRESO/JRC):** `MINBIOWOOa` (commodity `C&P_RW`) is woodchips and pellets from additionally harvestable stemwood, net of material use. It is *not* labelled as by-products, and black liquor is excluded from ENSPRESO. Evidence R1–R8 below.
- **In this model (adopted decision, §7):** `WOOD_FI1` is used as a **documented proxy for Finland's captive industrial by-product stream (black liquor, bark, sawdust)**, taking the ENSPRESO `MINBIOWOOa` *volume* because black liquor — the largest Finnish wood-energy source — is absent from ENSPRESO. The ENSPRESO label mismatch is the caveat, carried openly and flagged for IIASA.

So the evidence in §2.2 is **why the caveat exists**, not a reason to abandon the by-product interpretation; §7 explains why the proxy is nonetheless the right modelling choice for Finland.

### 2.2 Evidence

| # | Finding | Source |
|---|---|---|
| R1 | Definition table: "Stemwood production → Additionally harvestable stemwood → **Woodchips and pellets, `MINBIOWOOa`**" (the table also lists the wood-like fuel `MINBIOWOO`) | JRC report EUR 27575 (Ruiz Castello et al. 2015), printed p. 17 (`Docs/biomass potentials in europe_web rev.pdf`, PDF p. 19) |
| R2 | The cost table (Table 14) has columns "Roundwood fuelwood", "**Roundwood Chips & Pellets**", "Forest residues (chips and pellets, energy residues)". Finland: 5.7/4.8/4.0, **12.1/10.1/8.3**, 7.1/6.0/4.9 €2010/GJ for 2010/2030/2050. The workbook's FI costs for `MINBIOWOO`, `MINBIOWOOa`, `MINBIOFRSR1` (Med 2030: 4.84, **10.12**, 5.97) match. So `C&P_RW` = Chips & Pellets from RoundWood and `C&P_Res` = from residues | same, printed p. 56 (PDF p. 58); workbook sheet *COST - NUTS0 EnergyCom* |
| R3 | Secondary residues of the wood industry (sawmill chips, saw dust, black liquor) are `MINBIOWOO1`/`MINBIOWOO1a` (= workbook `MINBIOWOOW1`/`W1a`, your **FI3**) | same, printed p. 17; §4.2.2 printed p. 39 |
| R4 | Black liquor potentials are estimated in the study but are **not an input**: "the availability of black liquor is endogenous" in JRC-EU-TIMES. No black-liquor commodity exists in the workbook | same, footnote 6, printed p. 15; table printed p. 17 |
| R5 | Competing use is handled: material use of roundwood comes from EFI-GTM (EFSOS); "the stemwood and residues not used for material products are then available for energy"; residue material use is a fixed percentage per scenario | same, printed p. 25 and 37 |
| R6 | Chips and pellets are a conversion route: "stemwood and residues available for energy can be used flexibly either as traditional fuelwood, or in the form of chips and pellets" | same, printed p. 37 |
| R7 | Workbook Glossary: `MINBIOWOOa` = "C&P_RW – Chips and Pellets (part of MINBIOWOO in BaU)"; NUTS2 sheet: `MINBIOWOOa` is the single commodity `C&P_RW` (FI, ENS_Med 2030: 45,944 GWh); no commodity named liquor, bark, pulp | `ENSPRESO_BIOMASS.xlsx`; script §8 |
| R8 | The "C&P = chemical and physical" expansion, and the "WOOD3 = black liquor" label of the Belgian table, are not in the sources (Belgian WOOD2+WOOD3 = Colla's local low-quality class: landscape care, agricultural residues, biowaste) | Colla et al. 2022, Tables 1–2 |

### 2.3 The magnitude argument (reinstated in §7 as justification, not proof of identity)
FI1 (45.4 TWh in S2) is close to Statistics Finland's black liquor consumption (43.0 TWh in 2017; 39–47 TWh in 2015–2024). This does **not** prove `MINBIOWOOa` *is* black liquor (ENSPRESO computed it for stemwood chips). But it is exactly why `MINBIOWOOa` is a usable **volume proxy** for the black-liquor-dominated by-product stream the model must represent (§7, point 2).

### 2.4 What has been changed (Docs only; no model, data, patch or run touched)

| File | Change |
|---|---|
| `Docs/biomass_scenario_mapping.md` | `MINBIOWOOa` definition rewritten with the JRC evidence; column header, WOOD mapping row and composition row corrected; the FI1 black-liquor statements in the Luke bullet and the S3 revision table marked **superseded** |
| `Docs/biomass_supply_curve_fi.md` | Belgian WOOD3 label corrected (R8); FI1 mapping, cost, GHG and glossary rows rewritten |
| `scripts/check_forest_supply_traceability.py` | §8 commodity composition; optional §9 `--online` Statistics Finland (kept as context only) |
| `paper1/Overleaf_working_paper/REVIEW_FLAGS.md` | Section G: paste-ready LaTeX for the corrected wording (snippet only; `.tex` untouched) |

### 2.5 Corrected wording for the paper
> *Woodchips and pellets from additionally harvestable stemwood (ENSPRESO `MINBIOWOOa`, commodity `C&P_RW`; net of material use)*, and for FI3: *Wood-industry by-products: secondary woodchips and sawdust (ENSPRESO `MINBIOWOOW1` + `W1a`)*. Black liquor is excluded from ENSPRESO.

### 2.6 Propagation of the corrected wording (approved and done 2026-10-08)

| File | Change | Verified |
|---|---|---|
| `Data/2035/00_INDEP/Resources_indep.csv` (FI1, FI3 comment cells) | Comment text only | All non-comment cells identical to git HEAD (script check: shape, columns, values) |
| `Data/2035/02_REF_REGION/Resources.csv` (FI1, FI3 comment cells) | Comment text only | same |
| `plots/plot_biomass_supply_curves.py` | `STEP_LABELS` for steps 1 and 3 | The figure **does not display these labels** (the variable is never used), so regenerating changed only file metadata; I **restored the original figure files** from backup. The published figure is unchanged. |
| `plots/make_old_biomass_table_docx.py` | WOOD definition string | text only |
| `Docs/paper_sections_draft.md`, `Docs/concept_note_G4M_forest_energy_finland.md` | FI1 and FI3 rows | text only |

Backups: `_backups/*_20261008_before_T1_wording.csv` and the original figure files (git HEAD also clean beforehand).
**Not touched (yours):** Overleaf `main_certosa.tex` (use REVIEW_FLAGS G1–G3), the older copies under `Data/exogenous_data/Mypaper/`, and your Drive concept note.

---

## 3. Consequences of T1 (new flags) — SUPERSEDED by §7 (kept for the record)

> These were written for the *literal stemwood* reading. The adopted decision (§7) is the by-product interpretation, under which T12/T13/T14 are resolved without a re-run. Read §7 for the governing position.

### T12 — costs and GHG of FI1 and FI3 were assigned on the wrong reading
| Step | True content (JRC) | Model cost | ENSPRESO cost (Med 2035, €2010/MWh) | Model GHG (t/GWh) | Comment |
|---|---|---:|---:|---:|---|
| FI1 | Stemwood chips & pellets | **11** | **34.7** | **10** | Cost about 3× too low; GHG below the residue factor (21.6) although stemwood chips/pellets add harvest and conversion |
| FI3 | Wood-industry by-products (sawmill chips, sawdust) | **27** | **7.7 / 6.1** | 14 | The genuinely cheap by-product block is priced 3.5–4.4× above ENSPRESO |
In the model the merit order is FI1 < FI2 < FI3 < FI4. On ENSPRESO's costs it would be FI3 < FI4 < FI2 < FI1. FI1 is fully used in every unconstrained run, so the unconstrained cost ranking and the S1/S2/S3 comparison may change materially. **This cannot be judged without new runs.**

**How reliable are the ENSPRESO cost levels? (re-checked 2026-10-08 after your question)**
- **Robust:** the *ordering*. The JRC report gives by-products the lowest prices (Table 15: Finland sawmill woodchips 2.2 and sawdust 1.7 €2010/GJ in 2030, i.e. about 6–8 €/MWh) and chips and pellets from roundwood the highest (Table 14: 10.1 €2010/GJ). The workbook reproduces both tables exactly. So **your intuition is right: by-products are the cheapest.** The error was that the cheap slot was given to FI1, which is not a by-product; the true by-product block is FI3 (12.5 TWh in S2), not 45 TWh.
- **Not robust:** the *levels*. (i) The 10.1 €/GJ for chips and pellets is a delivered pellet-grade price (the report says pellet prices apply only after a conversion factor), so for wood-chip use the true cost may be lower: Statistics Finland's delivered forest-chip price was 20.6 €/MWh in 2017. (ii) The by-product prices cannot be reproduced from the report's own input: it cites an Austrian sawmill-residue price of €82 (unit not stated), which at the report's 13.55 GJ/t would be about 6.0 €/GJ, while Table 15 shows 2.8 €/GJ for Austria. So 6–8 €/MWh for by-products may be too low.
- **Colla's approach (read from his paper):** he did **not** build a feedstock-by-feedstock forestry ladder. His categories are origin (local, neighbouring, other EU, RoW) × quality (good = all forest/wood including industry residues; low = crops, agricultural residues, landscape care, biowaste). His costs come from ENSPRESO plus processing (briquetting when not already included) and transport. Test: Belgium's ENSPRESO forest codes sum to 13,124 GWh (ENS_Med 2030) against his local good quality of 12,920 GWh, with a volume-weighted ENSPRESO cost of 19.0 €/MWh against his 22.2. His cheapest Belgian step (11,037 GWh, 13.2 €/MWh) belongs to the local low-quality class, not to by-products. **The Finnish four-step split is therefore your extension of Colla, and its costs were assumptions.**

### T13 — S3 FI1 contradicts the repo's own audit
Under the BDS ceiling the audit (mapping doc §3.5.1, Evidence 3) says about 0–5 Mm³ remain for direct energy wood. But FI1 is stemwood for energy, and S3 keeps **32 TWh ≈ 16.0 Mm³ (2.0 MWh/m³) to 21.3 Mm³ (1.5 MWh/m³)**. For comparison S2 uses 22.7–30.3 Mm³ and S1 27.3–36.4 Mm³. The −26% was justified by by-product logic that no longer applies. Meanwhile FI3 (the real by-products) is cut by 76% in S3, which is the opposite of what the by-product logic implied.

### T14 — black liquor is outside ENSPRESO (upgraded to High)
**Facts (all sourced):**
- Statistics Finland (table 12vq): black liquor **42,989 GWh in 2017** (47,151 in 2019; 39,239–39,569 in 2022–24), **43% of the 100,783 GWh of wood fuels** and 11.4% of total energy consumption. You are right that it is a very large part of Finnish wood energy.
- JRC report (EUR 27575): black liquor potentials were estimated, but black liquor is **not an input of ENSPRESO**; it is endogenous in JRC-EU-TIMES (output of the paper-industry model, "amount of residue/residue ratio", competing use 0% in all scenarios, printed pp. 15, 17, 25). It has a price (Biomass Futures) and a heating value of 11.67 GJ/t, but no commodity in the workbook.
- Your model: the wood supply (`WOOD_FI1–5`) comes only from ENSPRESO, so it contains **no black liquor**. But the 2017 calibration target "biomass 100 TWh" (`finland_2017_reality_reference_audit.md`) is Statistics Finland's wood fuels, i.e. including 43 TWh of black liquor, and the demand boundary (JRC-IDEES useful energy, ~129 TWh industry, unchanged) still contains the heat and power that black liquor supplies in pulp mills. I found no place where black liquor is represented or netted out.
- Consequence: in 2017 the model's generic wood supply **stands in for black liquor**. In 2035 the cheap FI1 block (45 TWh, 11 €/MWh) may be playing that role by accident, which is a different thing from "stemwood chips".

**What this implies physically:** black liquor is captive (burned in pulp-mill recovery boilers, tied to pulp output, about constant, near-zero marginal cost, not available for district heat or fuels), whereas the model treats all wood as a fungible, dispatchable commodity. This affects every wood allocation result in the paper (e.g. "biomass to district heat").

**Options (all need your decision; each changes model inputs or structure):**

| Option | What it means | Effort / risk |
|---|---|---|
| A. Explicit captive resource | New resource of about 39–47 TWh (Statistics Finland), cost near zero, usable only by industrial CHP/boilers | Model-structure change (resource and layer restrictions); needs approval and re-validation of 2017 |
| B. Net it from demand | Reduce industrial heat/power demand by the black-liquor-supplied part | Data change; needs the industry fuel split (Metsäteollisuus statistics, not in the workspace) |
| C. Keep and disclose | State that wood supply in 2017/2035 is a generic wood pool that implicitly includes black-liquor-like energy | No runs; weakest, but honest |

---

## 4. What I need from you
**Resolved 2026-10-08 (see §7):** you chose the by-product interpretation, so §3 and §6 below are superseded (kept for the record). Remaining asks:
1. **Paste REVIEW_FLAGS section G** into the Overleaf `.tex` (FI1 wording, FI1 footnote, JRC bib, T8 totals). The `.tex` is yours; I did not edit it.
2. **Zotero:** add the JRC report (EUR 27575) so it is citable. A bib entry is in REVIEW_FLAGS section G.
3. **Optional** (no re-run needed for the adopted path): if you later want the FI3 cost lowered to the ENSPRESO level, or an explicit captive black-liquor resource, that becomes a new timestamped run — ask and I will plan it.
4. Tomorrow with Paul: *"ENSPRESO excludes black liquor; we proxy it through the cheapest ENSPRESO wood step — how would you represent pulp-mill black liquor and the by-product split in G4M/BeWhere?"*

---

## 5. Change log

| Date | Task | Files | Backup | Description | Status |
|---|---|---|---|---|---|
| 2026-10-08 | T1 evidence and doc corrections | `Docs/biomass_scenario_mapping.md`, `Docs/biomass_supply_curve_fi.md` | git HEAD (files were clean) | Replaced the unsupported FI1 description by the JRC definition; marked dependent statements superseded | done |
| 2026-10-08 | T1 reproducible evidence | `scripts/check_forest_supply_traceability.py` | new file section | Added §8 and optional §9 | done |
| 2026-10-08 | Tracker created and rewritten after JRC report | `Docs/forest_supply_flags_tracker.md` | – | Added T12–T14; T10 closed | done |
| 2026-10-08 | T1 paper snippet | `paper1/Overleaf_working_paper/REVIEW_FLAGS.md` | git HEAD | Section G (snippet only; `.tex` untouched), rewritten to the JRC wording | done |
| 2026-10-08 | T1 propagation (approved) | `Data/2035/00_INDEP/Resources_indep.csv`, `Data/2035/02_REF_REGION/Resources.csv`, `plots/plot_biomass_supply_curves.py`, `plots/make_old_biomass_table_docx.py`, `Docs/paper_sections_draft.md`, `Docs/concept_note_G4M_forest_energy_finland.md` | `_backups/*_20261008_before_T1_*` + clean git HEAD | Comment/label text only; numeric cells verified identical; regenerated figure restored (labels not shown in the figure) | done |
| 2026-10-08 | T12/T13 plan drafted | this file §6 | – | Options and run design; nothing decided or run | awaiting decisions |
| 2026-10-08 | T1/T12/T13/T14 resolved by decision (§7): FI1 = industrial by-product proxy | `Docs/biomass_scenario_mapping.md`, `Docs/biomass_supply_curve_fi.md`, `Docs/paper_sections_draft.md`, `Docs/concept_note_G4M_forest_energy_finland.md`, `Data/2035/00_INDEP/Resources_indep.csv`, `Data/2035/02_REF_REGION/Resources.csv`, `plots/*.py`, `paper1/Overleaf_working_paper/REVIEW_FLAGS.md`, `Docs/meeting_prep_2026-10-09_G4M_coupling.md` | `_backups/*_20261008_before_T1_*` | Adopted by-product interpretation with documented cost/GHG hypotheses and the ENSPRESO-label caveat; no numeric value or run changed | done |

---

## 6. T12/T13 plan — SUPERSEDED by §7 (kept for the record; this was the re-run alternative, not adopted)

### 6.1 Cost evidence available (€/MWh)

| Step | True content | Model today | ENSPRESO Med 2035 (€2010, volume-weighted) | ENSPRESO Low 2030 (€2010) | Anchored on FI2 = 20.6 |
|---|---|---:|---:|---:|---:|
| FI1 | Stemwood chips and pellets | 11 | **34.7** | 39.9 | 34.8 |
| FI2 | Logging residues (chips) | 22 | 20.5 | 23.5 | 20.6 |
| FI3 | Wood-industry by-products | 27 | **7.2** | 8.1 | 7.2 |
| FI4 | Fuelwood roundwood + landscape care | 33 | 14.5 | 17.3 | 14.6 |

Independent anchor: Statistics Finland (open API, table 12gb) **forest chips delivered**, nominal: 20.3 (2018), 20.6 (2017), 20.9 (2019), 22.2 (2020), 25.3 (2022), 30.9 (2023), 36.2 (2024), 39.0 (2025). FI2 = 22 matches the 2017–2020 level. An FI1 of 11 €/MWh is below every observed delivered forest-chip price.
Note ENSPRESO costs are in €2010; the model's price year is not stated anywhere I found (FI2 = 22 was set from the 2017 "calibrated flat price").
**Reliability (see §3, T12):** the ENSPRESO *ordering* is robust (by-products cheapest, chips and pellets from roundwood dearest), the *levels* are not. FI1's 34.7 is a pellet-grade delivered price, so a plausible FI1 range is roughly **21 (observed forest-chip price, 2017) to 35 (ENSPRESO)**; FI3's 7.2 comes from 2010 market prices that the report itself does not reconcile, so treat 7–20 as an open range. Only a Finnish price source for sawmill chips would narrow it (not in the workspace).

### 6.2 S3 FI1 from the harvest ceiling (T13)
National ceiling 48.9 Mm³ (60% × 81.5, Mönkkönen) minus industrial roundwood demand D leaves energy stemwood:

| D (Mm³) | Energy stemwood | FI1 at 1.5 MWh/m³ | FI1 at 2.0 MWh/m³ |
|---:|---:|---:|---:|
| 40 | 8.9 Mm³ | 13.3 TWh | 17.8 TWh |
| 44 | 4.9 Mm³ | 7.3 TWh | 9.8 TWh |
| 48 | 0.9 Mm³ | 1.3 TWh | 1.8 TWh |

versus 32.0 TWh today. **D = 48 Mm³ is the repo's Luke figure, which I could not verify** (T9). Consistency check supporting FI1 = stemwood: S2 FI1 (22.7–30.3 Mm³) plus 48 Mm³ industrial gives 70.7–78.3 Mm³, which brackets the 2018 harvest (78.2 Mm³) and the NFS target (80 Mm³).

| S3 option | FI1 (TWh) | Comment |
|---|---:|---|
| a. Keep | 32.0 | Contradicts the repo's own audit; not recommended |
| b. Raw JRC low scenario (ENS_Low 2030) | 43.2 | Ignores the Mönkkönen ceiling |
| c. Ceiling-derived | 1.3–17.8 | Needs D and one conversion factor (T5); my recommendation is to carry the range as S3 and a mid case |
| d. Scale ENS_Low by 60/96 | 27.0 | Arbitrary proportional rule |

### 6.3 Candidate corrected parameter set (for discussion)

| Parameter | Option 1 (ENSPRESO levels) | Option 2 (anchored on observed prices) | Option 3 (status quo + disclosure) |
|---|---|---|---|
| Costs FI1–FI4 | 34.7 / 20.5 / 7.2 / 14.5 | FI2 stays 22; FI1 = 21–35 (run both ends); FI3 and FI4 as an explicit range pending a Finnish source | keep 11 / 22 / 27 / 33 and present as assumptions |
| FI1 GHG | 21.6 (Colla/RED II local good quality, same as FI2) | same | keep 10 |
| FI3 GHG | keep 14 (landscape-care proxy, flagged) | same | same |
| S3 FI1 | per §6.2, option c (low / mid) | same | 32.0 |
| S1 | S2 × 1.2 on all steps (unchanged rule) | same | same |

I no longer recommend a single option: the cost levels are uncertain (§6.1). What I do recommend is (i) fixing the **ordering** (by-products FI3 cheapest, FI1 not), (ii) running FI1 at both ends of its range as a sensitivity rather than choosing one number, and (iii) deciding T14 first, because black liquor changes what the cheap block is for.
Expected direction (not a prediction): a higher FI1 cost makes wood less attractive in the unconstrained cases and raises costs of all scenarios, with S1/S2 differences shrinking if FI1 stops being a free cheap block; a smaller S3 FI1 makes S3 tighter than in the paper. Only runs can tell.

### 6.4 Decisions needed

| ID | Question | Options |
|---|---|---|
| D-A | Cost source for FI1–FI4 | Option 1 / 2 / 3 above |
| D-B | Price year | keep as is (model year unstated), or index €2010 to a stated year (needs an index source) |
| D-C | FI1 GHG | 21.6 (recommended) / keep 10 |
| D-D | S3 FI1 | §6.2 a–d |
| D-E | Source for industrial roundwood demand D | Luke table (please add the file), or a range 40–48 Mm³ |
| D-F | Timing and T14 | decide the black-liquor treatment (T14 options A/B/C) **first**, then run the new batch |

### 6.5 Run design once decided (needs your approval before any file is created)
- **New patch files** in `calibration/patches/` named `fi_forest_S{1,2,3}_v2.csv` (S2 needs one too, because the baseline `Resources.csv` carries the old costs). Existing patches and `Resources.csv` stay untouched.
- **Same matrix and flags as the canonical batch:** {S1,S2,S3} × {unconstrained, −95%, −95% no nuclear}, `--read-td`, 12 typical days, `--dhn-min 0.42 --dhn-max 0.50`, same baseline and nuclear patches.
- **New output folder** `case_studies/FI/forest_scenarios_2035_v2/` with timestamped run directories; record model version, data snapshot, command and path in `case_studies/FI/versions.json`. Canonical runs remain read-only paper evidence.
- **Cost:** the canonical batch ran from 18:05 to 20:31 on 2026-05-18 (about 2.5 h).
- **Comparison table** of v1 vs v2 for cost, CO₂, wood used per step, and the S3 saturation result, written to `Docs/` and reproducible from the run directories.

---

## 7. ADOPTED RESOLUTION (decision 2026-10-08) — FI1 as an aggregate industrial by-product proxy

**Decision.** `WOOD_FI1` is modelled as **Finland's captive industrial wood by-product stream — black liquor (dominant), bark and sawdust**. Its volume is taken from the ENSPRESO commodity `MINBIOWOOa` (S1/S2/S3 = 54.5 / 45.4 / 32.0 TWh). Cost = 11 EUR/MWh and supply-chain GHG = 10 tCO2eq/GWh are retained as **documented hypotheses** (below). **No model, data value, patch or run changes; the 9 canonical runs stay valid.**

**Why this is sound (not a fudge).**
1. **Physical necessity.** Black liquor is the single largest Finnish wood-energy source (**43.0 TWh in 2017**, 43% of wood fuels, Statistics Finland table 12vq). ENSPRESO **excludes** it (it is endogenous in JRC-EU-TIMES). The validated 2017 run reproduces biomass to within 3.2% using a generic WOOD pool that **already carries black liquor**. So a 2035 ladder built from ENSPRESO must let some step represent it, or it silently loses Finland's dominant wood-energy stream.
2. **Magnitude match.** `MINBIOWOOa` is the cheapest, highest-volume ENSPRESO wood commodity, and its size (45.4 TWh in S2) matches black liquor (43.0 TWh). Script check: `MINBIOWOOa` S2 = 45,442 GWh vs black liquor 42,989 GWh (2017).
3. **Internal consistency.** The by-product reading keeps the low cost (11), the low GHG (10) and the S3 reduction (−26%, less pulp/sawmill throughput under BDS) all physically meaningful — the same logic across volume, cost, GHG and scenario response.
4. **Conservative.** A black-liquor-weighted cost blend is ~2–3 EUR/MWh; the model's 11 EUR/MWh is **higher**, so biomass is not made artificially cheap.

**The one caveat, stated openly (flag T1).** ENSPRESO *formally* labels `MINBIOWOOa` as "woodchips and pellets from additionally harvestable stemwood" (JRC EUR 27575, Ruiz Castello et al. 2015, printed p. 17; cost column "Roundwood Chips & Pellets"). We **re-purpose** that volume as a by-product proxy; we do not claim ENSPRESO calls it a by-product. The genuine ENSPRESO by-product codes (sawmill chips, sawdust) are `MINBIOWOOW1`/`W1a` = `WOOD_FI3`, which are smaller (12.5 TWh) and cannot carry the 43 TWh of black liquor.

**Cost hypothesis (FI1 = 11 EUR/MWh).** Black liquor is captive, self-consumed in Kraft recovery boilers, tied to pulp output, ~0 EUR/MWh marginal cost; bark and sawdust ~6–12 EUR/MWh at the mill gate. The black-liquor-weighted blend is ~2–3 EUR/MWh, so 11 is a conservative upper value, retained from the prior calibrated flat WOOD price (22 EUR/MWh) of which FI1 was the cheapest step. **Refine with IIASA** using pulp/sawmill throughput and Finnish by-product prices.

**GHG hypothesis (FI1 = 10 tCO2eq/GWh).** Supply-chain only (biogenic combustion = 0). Captive mill-gate streams have no in-forest collection/forwarding, so ~half the RED II forest-residue value (21.6). Defensible for by-products.

**Flag for the IIASA collaboration (carry verbatim).**
> *EnergyScope-Finland represents Finland's largest wood-energy stream — pulp-mill black liquor (~43 TWh) — through the cheapest ENSPRESO wood step (`MINBIOWOOa`), which ENSPRESO formally labels as stemwood chips. Black liquor is absent from ENSPRESO. In the next phase, G4M + pulp/sawmill industrial throughput should replace this proxy with a physically grounded black-liquor / bark / sawdust / stemwood-chip split, including a captive-use restriction (black liquor is not freely dispatchable to district heat or fuels).*

**What this closes:** T1 (interpretation chosen and justified), T12 (cost/GHG defensible, no re-run), T13 (S3 cut valid), T14 (black liquor represented and disclosed, option C). **Residual, minor:** FI3 cost 27 vs ENSPRESO ~7 (disclosed; optional future sensitivity); the "stemwood chips" literal reading is recorded as the caveat, not the model's position.

**Superseded:** §3 (T12–T14 "consequences") and §6 (T12/T13 run plan) were written for the *literal stemwood* reading and the alternative of re-running the matrix. They are kept below for the record but are **not the adopted path**; §7 governs.
