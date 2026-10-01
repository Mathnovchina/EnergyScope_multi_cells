# Paper 1 — index

Navigation hub for *Forest-management biomass supply curves in a whole-energy-system model of
Finland*. Full technical pin: [../REPRODUCIBILITY.md](../REPRODUCIBILITY.md).

## Contents

- **`results/`** — saved result tables for the 9 canonical 2035 runs (one folder per
  scenario × GHG case): `run_metadata.json`, `TotalCost.csv`, `Gwp_breakdown.csv`, `Resources.csv`,
  `Assets.csv`, `Year_balance.csv`. These are committed copies (the source runs live under the
  gitignored `case_studies/`).

## Where the rest lives

| Artefact | Location |
|---|---|
| Model | `esmc/energy_model/ESMC_model_AMPL.mod` (`VERSION` 2.0) |
| Canonical runs (full, incl. hourly) | `case_studies/FI/forest_scenarios_2035/20260518_*` **(gitignored — archive separately)** |
| 2017 baseline run | `case_studies/FI/manual_runs/20260323_173930__2017_baseline/` **(gitignored)** |
| Data + scenario patches | `Data/2035/FI/`, `calibration/patches/fi_forest_*.csv`, `fi_baseline_2035.csv` |
| Figures | `plots/biomass_supply_curves_fi_2035.*`, `plots/forest_scenarios_2035_*.*`, `plots/validation_2017/` |
| Scenario derivation | `Docs/biomass_scenario_mapping.md`, `Docs/biomass_supply_curve_fi.md` |
| Draft text | `Docs/paper_sections_draft.md`; manuscript `Data/exogenous_data/Mypaper/` |
| Next phase (concept note) | `Docs/concept_note_G4M_forest_energy_finland.md` |

## Scenario × GHG matrix → run directory

See the table in [../REPRODUCIBILITY.md](../REPRODUCIBILITY.md#2035-forest--ghg-matrix-study-group-forest_scenarios_2035-batch-20260518_). Pin: git tag `paper1-finland-forest-v1.0`.
