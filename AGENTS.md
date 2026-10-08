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
  `paper1/Overleaf_working_paper/REVIEW_FLAGS.md`.

---

## 8. Working-document environment

- Preview `.md` in VS Code: `Ctrl+Shift+V` (GitHub styling and Mermaid extensions installed).
- Documents with executed data/figures: `.qmd` (Quarto + `.venv` Jupyter kernel). Template: `Docs/working_doc_example.qmd`.
- Render to self-contained HTML (also `-To pdf|docx`): `.\scripts\render_doc.ps1 Docs\<file>.qmd`.
- Rendered `.html` files are generated artefacts: regenerate, never edit by hand.

