# Reproducibility Manifest — Paper 1 (Finland forest-management biomass supply curves)

> Pin of the model, data, and runs behind *Forest-management biomass supply curves in a
> whole-energy-system model of Finland*. Keep this file in sync with any change to the canonical
> artefacts. Companion: [paper1/README.md](paper1/README.md), [AGENT.md](AGENT.md).

## ⚠️ Read first — what is and isn't in git

- **`case_studies/` is gitignored.** The paper's run directories (model snapshot + inputs + outputs)
  live on disk only and are **not** version-controlled. Reproducibility therefore relies on:
  (a) the committed **model + data + patches**, (b) the **regeneration commands** below, and
  (c) the **saved result tables** copied into `paper1/results/` (tracked).
- **Recommended:** archive the 9 canonical 2035 run dirs + the 2017 baseline dir as a compressed
  bundle (e.g. `paper1_runs_v1.0.zip`) stored outside git (release asset / backup), since they are
  the primary evidence and are not in version control.

## Environment

| Item | Value |
|---|---|
| Model | EnergyScope Multi-Cells (ESMC), `VERSION` = **2.0** |
| Model file | [esmc/energy_model/ESMC_model_AMPL.mod](esmc/energy_model/ESMC_model_AMPL.mod) (+ `ESMC_obj_TotalCost.mod`) |
| Python env | `environment.yml` / `.venv` (Python 3.11) |
| Solver | AMPL (see each run's `log.txt` / `Solve_info.csv` for solver + version) |
| Git | branch `Finland`; pin commit at tag **`paper1-finland-forest-v1.0`** |
| Time resolution | 12 typical days (`--read-td`, frozen TDs shared across scenarios) |
| GHG baseline | Finland 2017 = **41,200 ktCO₂/y**; −95% ⇒ `gwp_limit` = **2,060 ktCO₂/y** |

## Canonical runs

### 2017 validation baseline
- Dir: `case_studies/FI/manual_runs/20260323_173930__2017_baseline/` (`relax_co2=true`, `v37_solar`).
- Role: historical benchmark (weighted error ≈1.2%). Exact invocation in that dir's
  `run_metadata.json` / `run_notes.md`. Justifications: [Docs/finland_2017_validation_justifications.md](Docs/finland_2017_validation_justifications.md).

### 2035 forest × GHG matrix (study group `forest_scenarios_2035`, batch `20260518_*`)
Forest scenario applied via patch (`S2_NFS` = default baseline, no forest patch). Verified: S1_BES
unconstrained reproduces paper values exactly (`TotalCost` 22,397 M€ = 22.40 bn€; `WOOD_FI1` 54,530
GWh = 54.5 TWh). Superseded duplicate batch `20260515_*` and the `ghg_80pct` column are **not** used.

| Scenario | GHG case | Run directory (`case_studies/FI/forest_scenarios_2035/`) | `gwp_limit` | Forest / nuke patch |
|---|---|---|---|---|
| S1_BES | unconstrained | `20260518_184521__S1_BES__unconstrained` | — | `fi_forest_S1_BES` |
| S1_BES | −95% (nuclear) | `20260518_190317__S1_BES__ghg_95pct` | 2060 | `fi_forest_S1_BES` |
| S1_BES | −95% (no nuclear) | `20260518_201837__S1_BES__ghg_95pct_nonuke` | 2060 | `fi_forest_S1_BES` + `fi_nuclear_phaseout_strong_2035` |
| S2_NFS | unconstrained | `20260518_180514__S2_NFS__unconstrained` | — | (default) |
| S2_NFS | −95% (nuclear) | `20260518_183044__S2_NFS__ghg_95pct` | 2060 | (default) |
| S2_NFS | −95% (no nuclear) | `20260518_200234__S2_NFS__ghg_95pct_nonuke` | 2060 | `fi_nuclear_phaseout_strong_2035` |
| S3_BDS | unconstrained | `20260518_192038__S3_BDS__unconstrained` | — | `fi_forest_S3_BDS` |
| S3_BDS | −95% (nuclear) | `20260518_195829__S3_BDS__ghg_95pct` | 2060 | `fi_forest_S3_BDS` |
| S3_BDS | −95% (no nuclear) | `20260518_203116__S3_BDS__ghg_95pct_nonuke` | 2060 | `fi_forest_S3_BDS` + `fi_nuclear_phaseout_strong_2035` |

Run manifests (exact commands + exit codes): `forest_scenarios_2035/sweep_manifest_20260518_202319.json`
(unconstrained + 95pct, with-nuclear) and `sweep_manifest_20260518_203951.json` (no-nuclear).

### Headline results (from the runs above; see `paper1/results/`)

| Scenario | GHG case | System cost (bn€/y) | CO₂_net (MtCO₂/y) | FI forest wood used (TWh) |
|---|---|---:|---:|---:|
| S1_BES | Unconstrained | 22.40 | 13.02 | 54.5 |
| S1_BES | −95% (nuclear) | 22.92 | 2.06 | 74.2 |
| S1_BES | −95% (no nuclear) | 22.94 | 2.06 | 100.4 |
| S2_NFS | Unconstrained | 22.46 | 12.57 | 45.4 |
| S2_NFS | −95% (nuclear) | 23.02 | 2.06 | 74.2 |
| S2_NFS | −95% (no nuclear) | 23.12 | 2.06 | 96.2 |
| S3_BDS | Unconstrained | 22.62 | 13.10 | 32.0 |
| S3_BDS | −95% (nuclear) | 23.56 | 2.06 | 40.0 |
| S3_BDS | −95% (no nuclear) | 23.90 | 2.06 | 40.0 |

## Data snapshot (committed)

| Role | Path |
|---|---|
| 2035 FI baseline resources (S2, with `WOOD_FI1–5` steps) | `Data/2035/FI/Resources.csv` |
| Brownfield renewable minima | `calibration/patches/fi_baseline_2035.csv` |
| S1 Bioeconomy supply (patch) | `calibration/patches/fi_forest_S1_BES.csv` |
| S3 Biodiversity supply (patch) | `calibration/patches/fi_forest_S3_BDS.csv` |
| Nuclear phase-out (no-nuke cases) | `calibration/patches/fi_nuclear_phaseout_strong_2035.csv` |
| Scenario derivation | [Docs/biomass_scenario_mapping.md](Docs/biomass_scenario_mapping.md), [Docs/biomass_supply_curve_fi.md](Docs/biomass_supply_curve_fi.md) |

## Regenerate a 2035 run

```powershell
.\.venv\Scripts\Activate.ps1
# template (S1_BES, −95%, with nuclear):
python scripts/run_fi_baseline_future.py `
    --year 2035 --name S1_BES__ghg_95pct --study-group forest_scenarios_2035 `
    --dhn-min 0.42 --dhn-max 0.5 `
    -p calibration/patches/fi_baseline_2035.csv `
    -p calibration/patches/fi_forest_S1_BES.csv `
    --gwp-limit 2060 --read-td
#  unconstrained: drop --gwp-limit ;  S2: drop the forest patch ;
#  no-nuclear: add -p calibration/patches/fi_nuclear_phaseout_strong_2035.csv
```
Each run writes a new timestamped dir with a full model snapshot, `run_metadata.json`, and `outputs/`.
**Never overwrite an existing run dir.**

## Figures (paper)

- `plots/biomass_supply_curves_fi_2035.png` (+ `.pdf`)
- `plots/forest_scenarios_2035_energy_matrix.png` (+ `.pdf`)
- `plots/forest_scenarios_2035_biomass_allocation.png` (+ `.pdf`)
- `plots/validation_2017/` (2017 validation plots, table, Sankey)

## Known caveats (carry into the paper)

- No forest carbon sink / LULUCF in the model (combustion-only GHG budget). See [AGENT.md](AGENT.md) §5
  and the phase-2 concept note [Docs/concept_note_G4M_forest_energy_finland.md](Docs/concept_note_G4M_forest_energy_finland.md) §5.C.
- S1 (+20%) and S3 (40 TWh) ceilings are stylised/revised, not raw ENSPRESO.
- 2017 uses `relax_co2=true` (historical reproduction only).
