# AGENTS.md â€” EnergyScope_multi_cells (Working Agreement & Project Tracker)

> Project-specific notes only. The **generic** working protocol (rules of engagement,
> scientific-production standards, backup/versioning, Zotero MCP) lives in the private
> `ai-config` repo (`global/AGENTS.global.md`) and is applied automatically from the user-level
> agent config. This file overrides the global protocol where they differ.
> (Renamed from `AGENT.md` on 2026-10-08; backup in `_backups/`.)

---

## 0. Repo-specific golden rules (on top of the global protocol)

1. **Never modify the model, data, or calibrated runs without explicit approval.** This includes
   `esmc/energy_model/*.mod`, anything under `Data/`, `calibration/patches/*`, and any run directory
   under `case_studies/`. Propose the change, show the diff, and **wait for a yes**.
2. **Never alter or delete a completed run.** Runs in `case_studies/FI/forest_scenarios_2035/` and
   `case_studies/FI/manual_runs/20260323_173930__2017_baseline/` are **paper evidence**. Treat them
   as read-only. Reorganise by **copying**, never moving/deleting, unless explicitly told.
3. **Traceability.** Any result that could enter the paper must be traceable to (a) a model
   version, (b) a data snapshot, (c) a run command, and (d) a run directory; otherwise flag it.

---

## 1. What this project is

Whole-energy-system optimisation of **Finland** with **EnergyScope Multi-Cells (ESMC)**, studying how
**forest-management scenarios** (and, next, **physical disturbance shocks** and the **forest carbon
sink**) reshape the optimal energy mix under different emission targets, with and without nuclear.

- **Paper 1 (near-complete):** static ENSPRESO-based wood supply curves (S1/S2/S3) Ã— GHG/nuclear
  matrix. See `Docs/paper_sections_draft.md`.
- **Paper 2 / next phase (proposed):** dynamic, G4M-derived supply curves + disturbance shocks +
  landâ€“energy coupled GHG budget. See `Docs/concept_note_G4M_forest_energy_finland.md`.

Model version: **`VERSION` = 2.0**. Python env: `environment.yml` / `.venv`.

---

## 2. Canonical artefacts (the things the paper depends on)

| What | Where | Status |
|---|---|---|
| Model (AMPL) | `esmc/energy_model/ESMC_model_AMPL.mod` (+ `ESMC_obj_TotalCost.mod`) | **Locked** for paper 1 |
| 2017 validation run | `case_studies/FI/manual_runs/20260323_173930__2017_baseline/` | **Canonical** (`relax_co2=true`, score ~1.2%) |
| 2035 scenario matrix | `case_studies/FI/forest_scenarios_2035/` ({S1,S2,S3}Ã—{unconstrained,ghg_95pct,ghg_95pct_nonuke}) | **Canonical** |
| Supply-curve data | `Data/2035/FI/Resources_S1_BES.csv`, `_S2_NFS.csv`, `_S3_BDS.csv` | **Locked** for paper 1 |
| Scenario mapping | `Docs/biomass_scenario_mapping.md`, `Docs/biomass_supply_curve_fi.md` | Reference |
| Paper figures | `plots/biomass_supply_curves_fi_2035.png`, `plots/forest_scenarios_2035_*.png`, `plots/validation_2017/` | Reference |
| Manuscript (LaTeX) | `Data/exogenous_data/Mypaper/` | Draft |
| Run index | `case_studies/FI/versions.json` | Keep updated |

> If any of the above is unverified or you can't reproduce it, **do not edit it** â€” report it.

---

## 3. How to reproduce (confirm commands against run logs before trusting)

```powershell
# activate env
.\.venv\Scripts\Activate.ps1

# 2017 calibrated baseline (historical reproduction, relax-co2)
python scripts/run_calib_manual.py --relax-co2   # see script --help for exact flags

# 2035 forward scenario (example; one forest scenario Ã— one GHG case)
python scripts/run_fi_baseline_future.py `
    --year 2035 --name ghg_95pct `
    --gwp-limit 2060 `
    --dhn-min 0.42 --dhn-max 0.50 `
    -p calibration/patches/fi_baseline_2035.csv `
    --read-td
# unconstrained case: omit --gwp-limit ; no-nuclear case: add the nuclear-phaseout patch

# postprocess / compare
python scripts/postprocess_future.py   # see --help
```

- `gwp_limit = 41200 Ã— (1 âˆ’ savings)`; 2017 baseline COâ‚‚ = 41,200 ktCOâ‚‚/y.
- `--read-td` reuses frozen typical days (valid across scenarios sharing weather/demand).
- Exact per-run flags are recorded alongside each run and in `case_studies/FI/versions.json`.

---

## 4. Change protocol (for any model/data edit)

1. **Isolate:** new scenarios go in **new** `Resources_*.csv` / patch files, not by editing baselines.
2. **Record:** note the change in the relevant `Docs/*.md` and in Section 6 below.
3. **Re-run:** never overwrite a prior run directory; create a new timestamped one, and record
   model version + data snapshot + command + output path.

Propose / approve / backup steps follow the global protocol. Always require explicit approval for:
deleting/moving run directories or data; editing `.mod` files; force-overwriting outputs;
bulk file reorganisation.

---

## 5. Known gaps & caveats (carry into every analysis)

- **No forest carbon sink / LULUCF in the model.** The binding GHG constraint
  (`ESMC_model_AMPL.mod` â†’ `Minimum_GWP_reduction`) counts **energy-system combustion COâ‚‚ only**.
  Harvest intensity and disturbances do **not** yet affect the sink. This is the headline item for
  the next phase (see concept note Â§5.C). Do not present scenario climate comparisons as if the sink
  were included.
- **S1 (+20%) and S3 (40 TWh)** supply ceilings are **stylised/revised**, not raw ENSPRESO â€” keep the
  disclosure in any figure/table.
- **2017 uses `relax_co2=true`** (historical reproduction only); never carry that assumption into
  forward-looking 2035/2050 runs.
- **Structural residuals** in 2017: district-heat overestimate (+43%) and gas-CHP (+37%) are
  aggregation artefacts, documented in `Docs/finland_2017_validation_justifications.md`.

---

## 6. Advancement tracker

Update this section as work progresses (newest first).

- **2026-10-14** — Reorganised `paper1/reviews_comments_flags_pathforward/SNIPPETS_overleaf.md` into an explicit Overleaf paste workflow. Added a current paste queue and standard `PASTE NOW` / `DONE` / `HOLD — DO NOT PASTE` statuses; each active item now identifies the target location, exact anchor text and required action before a copy-only LaTeX block. Corrected D5 to done because the sentence is already in `main_V1.tex`, and narrowed D2 to replacement of the one remaining incorrect sentence. No `.tex`, model, data, patch or run changed. Done, uncommitted.
- **2026-10-13** — Reconciled the Overleaf snippet tracker with author-owned `paper1/Overleaf_working_paper/main_V1.tex` (previous main version retained as `main_V0.tex`): D1, D3 and H1 are present; D2 is only partly applied, with one incorrect S3-versus-S1 comparison remaining. Updated D4/D6 evidence notes from the EnergyScope TD 2019 demonstration and Thiran thesis; explained the 1.2% score formula and constrained-target caveat; deferred D7, held G/H2 pending author decisions, removed H3 per author request, and marked the D9 scaling chain not paste-ready pending evidence. Added snippet-format preference below. No `.tex`, model, data, patch or run changed. Done, uncommitted.
- **2026-10-13** — Added `paper1/reviews_comments_flags_pathforward/PUBLISHABILITY_WORKPLAN.md`, an exhaustive ordered checklist from the current evidence state to an *Energy* submission. It separates work possible while waiting for the black-liquor expert, decisions and the T18 gate, pre-run input/reproducibility gates, the replacement 3×3 matrix, post-run auditing, manuscript restructuring, supplement, robustness options and submission requirements. It explicitly distinguishes the minimum Paper 1 package from optional sensitivities and Paper 2 G4M/sink/disturbance work. `FLAGS.md` remains the status source and now links to the workplan. Documentation only; no model, data, patch, run or `.tex` changed. Done, uncommitted.
- **2026-10-13** — Resolved and implemented the approved two-tier Finnish biomass import design for future runs. Reproducible evidence gives finite `WOOD_FI5` = 2.259 TWh/y at 36.661 EUR2015/MWh (`c_op=0.03666 M EUR/GWh`); observed high/downside checks are 2.573/1.850 TWh/y. Inputs: 2022–2024 mean 0.722 Mm³ energy-use chips plus 0.1736 Mt net pellets; Luke 2.0 MWh/solid m³ and 4.7 MWh/t; Comtrade/ECB CIF 32.193 EUR2015/MWh; Luke transport 4.212; HaminaKotka port due 0.256. Added unlimited `WOOD_FI6` at the author-approved 81.5 EUR2015/MWh explicit Colla-inspired stress value. Both use 0.040 ktCO2e/GWh by author decision. Wired shared resources, WOOD layer, `NOT_LAYERS`, reference region, all four Finland resource tables and related scripts; eight input backups use `_20261013_before_import_tiers`. Updated the source register, supply-curve design and T19. No AMPL `.mod`, patch, completed run or `.tex` changed; rerun deferred until T18/domestic ladder is settled. Done, uncommitted.
- **2026-10-13** — Completed the black-liquor classification and model-path audit: full ENSPRESO workbook search found no black-liquor entry and confirmed `MINBIOWOOa` is stemwood chips/pellets; S2BIOM explicitly carries `4132 Black liquor`; VTT pp. 112–113 confirms the captive recovery-boiler route (chemical recovery plus steam for mill processes/electricity). Enumerated all 14 technologies reachable through the shared `WOOD` layer and documented why pooled results cannot assign an FI1 end use. Replaced the long questionnaire with a short Teams-ready BeWhere question in `FLAGS.md` §5.1. Added a conservative 2035 import rule based on holding the completed 2022–2024 Luke mean constant (0.722 Mm³ energy-use chips + 0.1736 Mt net pellets), with the completed-period maximum as a finite high sensitivity; no parameter was adopted pending the now-completed conversion and delivery checks. Documentation only; no model, resource input, patch or completed run changed. Done, uncommitted.
- **2026-10-13** — Advanced the approved import-ladder evidence without changing model parameters. UN Comtrade 2024 partner/product queries show Estonia/Latvia/Lithuania/Sweden supplied 98.8% of Finland's coniferous-chip imports, 82.6% of non-coniferous chips and 75.0% of pellets. Combined with the ECB 2024 exchange rate and explicit provisional VTT-style moisture/LHV conversions, those regional flows equal 3.11–4.04 TWh at 35.8–46.4 EUR2024/MWh CIF before Finnish handling/inland transport; the total includes forest-industry chips and is not a 2035 energy-market potential. This preliminary range is superseded by the official-factor benchmark in the newer tracker entry above. Query/derived CSVs remain session artefacts; no import value, wood input, patch, run or `.tex` changed. Done, uncommitted.
- **2026-10-13** — With explicit approval, corrected the inherited non-wood biomass pools in `Data/2035/FI/Resources.csv` and the S1/S2/S3 reference tables from Paolo's retained ENSPRESO 2050 values to commodity-level `ENS_Med` 2030–2040 interpolations for 2035: wet biomass 1.313 TWh / 33.945 EUR2010/MWh, energy crops 5.388 / 24.207, biowaste 3.650 / 0.148, agricultural waste 4.985 / 15.134. Preserved the four pre-change files under `_backups/*_20261013_before_2035_biomass_year_correction.csv`; added `scripts/check_fi_legacy_biomass_2035.py` to reproduce and verify the calculation. All `WOOD_FI*` rows and legacy `WASTE` remained unchanged; no patch, model `.mod`, completed run or manuscript `.tex` changed. T17 input correction done; rerun deferred until the black-liquor/import/domestic-ladder design is complete. Added a ready-to-send black-liquor expert diagnosis and five-part question to `FLAGS.md` §5.1. Done, uncommitted.
- **2026-10-13** — Completed the read-only Thiran inheritance/year/import audit requested before rebuilding the biomass ladder. Verified that thesis Table 1.11 (printed p. 60) is already substantively represented by the paper's TD-input table but needs a pinpoint citation/2017 rationale; Table 1.14 (pp. 66–67) is absent as an inherited-category table, so paste-ready supplementary text was added. Reconstructed Paolo's four retained ENSPRESO pools at 2035 by commodity-level 2030–2040 interpolation: wet biomass 1.313 TWh, energy crops 5.388, biowaste 3.650, agricultural waste 4.985; costs 33.945, 24.207, 0.148 and 15.134 EUR2010/MWh. Confirmed black liquor is a captive pulp-mill by-product whose availability follows pulp throughput, not directly the harvest scenario, and recorded S2BIOM's primary/secondary double-count warning. Queried official Luke/StatFin APIs: chip and pellet import volumes, domestic energy-wood prices, municipal-waste treatment. Added flags T15–T19, snippets H1–H3, and full provenance/evidence boundaries to `Docs/data_sources_register.md`. Author direction recorded: retain Paolo's non-wood pools and legacy `WASTE`, correct the year, rebuild a traceable wood ladder, then rerun 2035 after explicit design approval. No model, data, patch, run or `.tex` changed; API extracts and the reconstruction CSV remain session artefacts. Done, uncommitted.
- **2026-10-12** — Colleague review (David An, Pontignano annual meeting, 10 June 2026) ingested as a traceable flag set: verbatim text extraction `paper1/reviews_comments_flags_pathforward/Pontignano_discussion__Bordenave__M__extracted.txt` (new file; PDF untouched) and flags **P-0…P-14** in `FLAGS.md` §1.5, each grounded in `main_certosa.tex` line numbers plus repository evidence, classed blocker/correction/robustness/future-work, cross-referenced to existing IDs (E6, C1/C2, C5, C6/C9, A1–A5, B.1/B.2, E4/E5, S-RED, T3, W-5) with explicit closure checks. Added `FLAGS.md` §5.1 work order: Block A (seven read-only evidence→snippet tasks, no approval needed), Block B (author-owned `.tex` restructuring), Block C (decisions). Verified the reviewer's references: Table 4 is the biomass-ladder table whose caption carries the mislabelled RED II "case 7a" (S-RED); `Loss(Elec,t)` is used but never defined; Eq. (3) names undefined cost functions; Fig. 10's "missing FI-5" is a result (0.014–0.045 GWh/yr in all nine runs), not an omission. Also recorded the two newly added Zotero items — the Colombia work is in the library as the **published** *Energy Economics* 160:109401 article, not the SSRN preprint. Nothing applied; no model, data, patch, run or `.tex` changed. P-4(b) (high/low 2035 demand scenarios) flagged as requiring new runs and approval. Done, uncommitted.
- **2026-10-12** — Completed the first Zotero-led Paper 1 benchmark and read-only canonical/frozen-result checks; detailed report, generated audit CSV/model-input hashes and local DOCX extraction kept in session artefacts, not the repo. Author selected **Energy**, approved constraint-interaction/allocation framing with transparent supply provenance and the application-centred outline. Decisions recorded in `paper1/reviews_comments_flags_pathforward/FLAGS.md` §3; next approved batch is accounting/evidence reconciliation and justified Overleaf snippets. Files changed: this tracker and FLAGS decision log; backup: existing git history (prior dirty edits preserved). No flag closed, T1 unchanged, no manuscript/model/data/patch/run changed or new sensitivity approved. Benchmark done; next batch approved, not yet implemented; logs uncommitted.
- **2026-10-12** — Updated `Docs/data_sources_register.md` with the full local ENSPRESO inventory, stable source IDs, exact biomass workbook sheets/filters, source-to-input-to-result chains and human/LLM navigation. Distinguished file presence, verified mapping and unapproved assumptions; no source data, model, patch or run changed. Done, uncommitted.
- **2026-10-12** — Added official VTT Technology 272 fuel handbook and qualified reference CSV in `Data/exogenous_data/Biomass_fuel_properties/`; extended `Docs/forest_ghg_and_black_liquor_reference_values.md` §8 with dry LHV, solid/loose density, moisture equations and checked examples. Source register and flags T5/S2B-6 updated; black-liquor HHV/organic-versus-total-solids caveats retained. Corrected this session's material-use inheritance wording, indirect-ammonia caveat and tiny FI5 flow unit in the allocation note. New reference files, no overwrite; no model/input/run or script assumption changed. Done, uncommitted.
- **2026-10-01** â€” Reproducibility freeze **done**: tagged `paper1-finland-forest-v1.0`; added
  `REPRODUCIBILITY.md` + `paper1/` (result tables for the 9 canonical runs); fixed the corrupted
  `.gitignore`. Decluttered the repo by **moving** (not deleting) ~38 scratch logs, 7 solver dumps,
  superseded run batches (`20260515_*`, old GHG sweep, `national_plan_*`, old calib folders) and the
  root debug-script folders into `_archive_20261001/`. Paper evidence untouched. **Next:** Plan B â€”
  landâ€“energy sink-coupling prototype.
- **2026-10** â€” Added G4M-pivot concept note (`Docs/concept_note_G4M_forest_energy_finland.md`) and
  this AGENT.md. Confirmed the forest-sink gap in the GHG constraint.
- **2026-10-08** â€” `AGENT.md` migrated to `AGENTS.md` (generic rules replaced by a pointer to the
  global protocol; backup `_backups/AGENT_20261008_before_agents_migration.md`). Added `CLAUDE.md`
  (`@AGENTS.md`). Started Quarto / Markdown-preview document environment (see Â§8).
- **2026-10-08** â€” Forest supply-curve traceability audit (read-only): added
  `Docs/forest_supply_curve_methodology_traceability.md` and `scripts/check_forest_supply_traceability.py`;
  meeting-prep notes `Docs/meeting_prep_2026-10-09_G4M_coupling.md`, `Docs/meeting_slides_outline_2026-10-09.md`,
  `Docs/IIASA_Forest_Models_Briefing.md`. No model/data/run changed. Flags T1â€“T14 tracked in `Docs/forest_supply_flags_tracker.md`: T1 **resolved by decision** (tracker Â§7): `WOOD_FI1` kept as an aggregate industrial by-product proxy (black liquor, bark, sawdust) using the ENSPRESO `MINBIOWOOa` volume, because black liquor â€” Finland's largest wood-energy source (43 TWh, 2017) â€” is absent from ENSPRESO; documented cost/GHG hypotheses, ENSPRESO-label caveat carried openly, flagged for IIASA. No numeric value or run changed; this also resolves T12 (cost defensible), T13 (S3 cut valid), T14 (black liquor represented, keep-and-disclose). Docs, `Data/` comments, plot scripts, paper draft, REVIEW_FLAGS (section G) all updated. Remaining flags T2â€“T11 unchanged.
- **2026-10-08** — Built meeting-opener deck `Docs/Finland_forest_IIASA_meeting_2026-10-09.pptx` (18 slides: context, Paper 1 method/results, gaps, RQs, IIASA proposals A-D, model landscape, path forward, open questions; generator `scripts/make_iiasa_meeting_deck.py`). In the spirit of the old `Finland_forest_bordenave` deck. Carries the adopted FI1/black-liquor flag.
- **2026-10-12** — Flag documents consolidated into `paper1/reviews_comments_flags_pathforward/FLAGS.md` (single register: dashboard, decisions log, path forward) and `SNIPPETS_overleaf.md` (paste-ready LaTeX, formerly `REVIEW_FLAGS.md`); `Docs/forest_supply_flags_tracker.md` kept as history; issue register in the traceability doc replaced by a pointer. New S2BIOM benchmark (`Data/exogenous_data/S2biom/`, `scripts/analyse_s2biom_finland.py`) added as flags S2B-1…8. No model, data or run changed; nothing committed.
- **2026-10-12** — Added `Docs/data_sources_register.md` (all data/database sources, qualification, availability) and `Docs/woody_biomass_material_use_and_allocation.md` (wood allocation in the 9 runs; material-use handling), plus `scripts/summarise_wood_allocation.py`; new flags W-1…W-6, S-PY, S-RED in FLAGS.md. No model, data or run changed.
- **2026-10-12** — Retrieved RED II Directive text (`Data/exogenous_data/RED II/`) and EUwood + Biomass Futures reports (`Data/exogenous_data/EUwood_BiomassFutures/`); added `Docs/forest_ghg_and_black_liquor_reference_values.md` (values, conversions, page references, black-liquor synthesis). New reference files only; no model, patch or run changed.
- *(add entries here)*

### Backlog / proposed (not started â€” require approval before model/data edits)
- [x] Reproducibility freeze: tagged `paper1-finland-forest-v1.0` + `REPRODUCIBILITY.md` + `paper1/` (done 2026-10-01).
- [ ] Prototype exogenous `co2_forest_sink` term in `Minimum_GWP_reduction` (concept note Â§5.C).
- [ ] New **S0 sink-max / net-zero** scenario definition.
- [ ] G4M â†’ `WOOD_FI1â€¦FI4` assortment mapping once IIASA data arrive.
- [ ] Disturbance-shock (pre/post, constrained re-optimisation) scenario.

---

## 7. Conventions

- Prefer **new files** over editing locked ones; keep scenario variants as separate CSVs/patches.
- Runs are **timestamped, append-only**; never overwrite.
- Document decisions in `Docs/` (one topic per file) and log them in Section 6.
- **Paper / Overleaf edits are author-owned.** Do **not** edit `paper1/Overleaf_working_paper/*.tex`
  directly â€” the author syncs Overleaf manually. Instead, put well-organised, justified,
  paste-ready LaTeX snippets (grouped by target section, each with a one-line justification and
  the exact `references.bib` keys to use) into the ad-hoc tracker
  `paper1/reviews_comments_flags_pathforward/SNIPPETS_overleaf.md`; issues, status and decisions are tracked in `paper1/reviews_comments_flags_pathforward/FLAGS.md` (consolidated 2026-10-12; `REVIEW_FLAGS.md` no longer exists).
- **Snippet style preference:** in this author's Overleaf snippets, avoid LaTeX emphasis,
  paragraph-heading and typewriter-formatting commands. Use ordinary prose and paragraph flow;
  write identifiers in plain text or escaped LaTeX text.
- **Snippet instruction format:** every active Overleaf snippet must state a clear status, the
  target location, exact anchor text, and one action (`REPLACE`, `INSERT AFTER`, or `DELETE`)
  immediately before the copy-only LaTeX block. Keep held evidence outside the active paste queue
  and label it `HOLD — DO NOT PASTE`.

---

## 8. Working-document environment

- Preview `.md` in VS Code: `Ctrl+Shift+V` (GitHub styling and Mermaid extensions installed).
- Documents with executed data/figures: `.qmd` (Quarto + `.venv` Jupyter kernel). Template: `Docs/working_doc_example.qmd`.
- Render to self-contained HTML (also `-To pdf|docx`): `.\scripts\render_doc.ps1 Docs\<file>.qmd`.
- Rendered `.html` files are generated artefacts: regenerate, never edit by hand.
