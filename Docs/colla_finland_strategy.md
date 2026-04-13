# Colla-Style Finland 2035 Analysis — Strategy Document

> **Date:** 2025-04-13  
> **Reference paper:** Colla et al. (2022) — *Optimal Use of Lignocellulosic Biomass for the Energy Transition, Including the Non-Energy Demand: The Case of the Belgian Energy System*  
> **Scope:** Finland 2035, EnergyScope Multi Cells (ESMC), single-cell  

---

## A. Repository Note — Relevant Files & Folders

### Data inputs

| Path | Purpose |
|------|---------|
| `Data/2035/00_INDEP/` | Technology-independent parameters (Layers_in_out, common time series) |
| `Data/2035/02_REF_REGION/` | Reference region defaults (Technologies.csv, Resources.csv) |
| `Data/2035/FI/` | Finland country overrides: `Technologies.csv`, `Resources.csv`, `Demands.csv`, `Time_series.csv`, `Weights.csv`, `Misc.json` |
| `Data/2050/FI/` | Same structure for 2050 |
| `Data/2017/FI/` | Calibration year data (used for baseline CO₂ reference only) |
| `calibration/patches/fi_baseline_2035.csv` | 5-line patch: WIND_ONSHORE f_min=6.0, WIND_OFFSHORE f_min=1.6, PV_ROOFTOP f_min=0.8, PV_UTILITY f_min=0.5, ELECTRICITY avail_exterior=25000 |
| `calibration/patches/fi_baseline_2050.csv` | Similar with higher brownfield minima |

### Runner & postprocessing scripts

| Path | Purpose |
|------|---------|
| `scripts/run_fi_baseline_future.py` | Main runner — CLI: `--year`, `--gwp-limit`, `--re-share`, `--name`, `--patch`, `--dhn-min/max`, `--kmedoid`/`--read-td`, `--dry-run` |
| `scripts/postprocess_future.py` | Reads ESMC outputs → `extract_primary_energy()`, `extract_electricity()`, `extract_heat()`, `extract_cost_by_sector()`, `extract_gwp_totals()` → per-run plots + cross-run comparison |
| `esmc/postprocessing/postprocessing.py` | Low-level multi-case pivot utilities (`get_var_cases`, `subgroup`) |
| `esmc/postprocessing/draw_sankey/` | Sankey diagram generation (Plotly) |

### Existing Finland manual runs

| Path | Year | GWP limit | Status | Objective |
|------|------|-----------|--------|-----------|
| `case_studies/FI/manual_runs/20260324_141200__national_plan_2035/` | 2035 | 21,000 ktCO₂ | Optimal | 22,959 M€/y |
| `case_studies/FI/manual_runs/20260324_142019__national_plan_2050/` | 2050 | 3,000 ktCO₂ | Optimal | 24,694 M€/y |
| `case_studies/FI/manual_runs/comparison_plots/` | — | — | Comparison charts (2035 vs 2050) | — |

### Output files per run (in `outputs/`)

| File | Columns | Units |
|------|---------|-------|
| `Resources.csv` | `Resources, avail_local, avail_exterior, R_year_local, R_year_exterior, R_year_import, R_year_export` | GWh/y |
| `Cost_breakdown.csv` | `Elements, C_inv, C_maint, C_op` | M€/y |
| `Gwp_breakdown.csv` | `Elements, GWP_constr, GWP_op, CO2_net` | ktCO₂-eq/y |
| `Year_balance.csv` | `Elements × 38 layers` (ELECTRICITY, WOOD, GAS, HVC, HEAT_HIGH_T, etc.) | GWh/y |
| `Assets.csv` | `Technologies, F, f_min, f_max, F_year` | GW or GWh |
| `Objective.csv` | `obj` | M€/y |
| `input2sankey_FI.csv` | Sankey flows | TWh |

### Key documentation

| File | Relevance |
|------|-----------|
| `Docs/fi_baseline_preflight_2035_2050.md` | GWP strategy, constraint design, biomass availability, DHN bounds, sensitivity variants |
| `Docs/fi_future_baseline_hypotheses.csv` | Decision log — 15 hypotheses (H01-H15), accepted/rejected/pending |
| `Docs/manual_run_fi.md` | Runner reference (calibration version, same architecture) |
| `Docs/session_20260324.md` | Work log for completed 2035/2050 baselines, postprocessing structure |
| `Docs/manual_calibration_foundation.md` | Data architecture, reality targets, model-to-reality mapping |
| `Docs/finland_2017_reality_reference_audit.md` | 26 metrics and mappings for 2017 baseline |
| `Docs/disabled_technologies_audit.md` | Which techs are disabled and why |

### Older Belgium model example

| Path | Purpose |
|------|---------|
| `0%_NED_constraints_naphtha_LFO_prices/` | One-shot ESTD (old architecture): monolithic `.dat` files, AMPL `printf` output, 0% GHG reduction scenario for Belgium |
| `0%_NED_constraints_naphtha_LFO_prices/output/` | TSV outputs: `assets.txt`, `cost_breakdown.txt`, `gwp_breakdown.txt`, `resources_breakdown.txt`, `year_balance.txt`, `input2sankey.csv`, `hourly_data/` |

---

## B. Comparison Table

| Analytical Item | Colla et al. (Belgium 2035) | Older Belgium Model (`0%_NED…`) | Current Finland Manual Runs | Status for Finland Reproduction | Comments / Caveats |
|---|---|---|---|---|---|
| **GHG savings sweep** | 10% steps: unconstrained → −90%, parametric on `gwp_limit` | Single scenario (0% reduction, gwp_limit≈154,000 kt) | **Only 2 scenarios**: 2035 @21,000 kt (≈49%), 2050 @3,000 kt (≈93%) | **New runs needed** for 10% sweep | Runner CLI supports `--gwp-limit N`; feasible to script sweep |
| **GHG baseline reference** | 2015 Belgian emissions (incl. NED feedstock CO₂) | gwp_limit=153,945 kt (≈2015 level) | 2017 Finnish CO₂: **41,200 ktCO₂** (calibrated, validated <0.1%) | **Available** | GHG savings = `1 − (gwp_limit / 41200)` |
| **System cost per scenario** | Total system cost (bn€/y) annotated on Figure 3 | 42,764 MCHF/y | **Available**: `Objective.csv` → M€/y | **Directly available** | Units: M€/y (ESMC) vs bn€/y (Colla) |
| **Primary energy by fuel** | Stacked bar: local RES/imported RES/nuclear/gas/oil/biomass/… | `resources_breakdown.txt` (Used, Potential) | `Resources.csv` → `extract_primary_energy()` in postprocess_future.py | **Directly available** | Categories: Biomass/Waste/Nuclear/Wind/Hydro/Solar/Gas/Oil/H₂ |
| **Biomass supply categories** | 10 origin categories (local, neighbours, other EU, RoW I, RoW II) × 2 quality classes (good/low) | WOOD (single aggregate) | **Single WOOD resource** (110.8 TWh avail) + WET_BIOMASS + BIOWASTE + BIOMASS_RESIDUES + ENERGY_CROPS_2 | **Not comparable** — no geographic disaggregation of biomass supply | Finland WOOD = all lignocellulosic domestic; no import origin breakdown; no explicit quality-class constraint |
| **Biomass final use / allocation** | Figure 4: LT heat (boiler, dec/DHN), HT heat (boiler, CHP), electricity (CHP, dedicated), NED (gasification→SNG/pyrolysis→SLF), mobility (diesel/SNG) | `year_balance.txt`: tech × layer matrix | `Year_balance.csv`: same structure, rows=techs consuming WOOD/biomass, columns=output layers | **Available but requires aggregation** | Must: (1) identify all techs with negative WOOD/WET_BIOMASS/BIOWASTE/BIOMASS_RESIDUES column in Year_balance, (2) map each to final-use category (HT heat, LT heat DHN, LT heat dec, electricity, NED/HVC, mobility) |
| **NED / Non-energy demand** | Explicit: NED_LFO + NED_SNG + NED_METHANOL; 15.8% share_NG_NED constraint; NED = 102,332 GWh/y | `share_NG_NED = 0.158` in data.dat | HVC layer in Year_balance.csv; BIOMASS_TO_HVC, OIL_TO_HVC, GAS_TO_HVC techs | **Partially comparable** | Finland HVC = 11,705 GWh (2035 run). Belgium NED much larger (102 TWh). No explicit NED_LFO/NED_SNG split in ESMC — but METHANOL layer exists. Finnish NED structure is narrower. |
| **Biomass conversion technologies** | 14 techs: boilers (3), CHP (3), gasification→SNG, pyrolysis→SLF/diesel, direct combustion elec | Belgium example: same tech set via ESTD | ESMC Finland: IND_BOILER_WOOD, DHN_BOILER_WOOD, DEC_BOILER_WOOD, IND_COGEN_WOOD, DHN_COGEN_WOOD, DEC_COGEN_WOOD, DEC_ADVCOGEN_WOOD, BIOMASS_TO_HVC, BIOMASS_TO_METHANOL, PYROLYSIS_TO_LFO, PYROLYSIS_TO_DIESEL, GASIFICATION_SNG | **Broadly comparable** — similar conversion routes | ESMC has slightly different tech naming; no dedicated biomass electricity plant (wood CHP produces co-electricity); HVC replaces NED_LFO as output |
| **Cost breakdown by sector** | Reported but not focus of paper | `cost_breakdown.txt`: per-tech C_inv/C_maint/C_op | `Cost_breakdown.csv` → `extract_cost_by_sector()` using SECTOR_MAP | **Directly available** | Sectors: Power, Heat-DHN, Heat-DEC, Industry, Transport, H₂/Synfuels, Storage, Other |
| **Biomass embedded GHG** | Per-origin carbon footprint (21–47 tCO₂/GWh) from RED II | Single gwp_op per resource | `Gwp_breakdown.csv`: WOOD gwp_op=1,010 kt for 41 TWh ≈ 24.5 tCO₂/GWh | **Available** — single aggregate | No origin-differentiated carbon footprint |
| **Biomass supply curve** | Price vs. quantity stepped curve (Figure 1), 10 categories | Single WOOD cost | Single `c_op_local` = 22.08 €/MWh for WOOD | **Not comparable** — single price point | Cannot reproduce Colla's supply-curve analysis |
| **Biomass quality constraint** | Max 40% low-quality (ash content limit) | Not visible in single-run data | **No quality constraint** in Finland model | **Not reproducible** | Would need model modification |
| **Sensitivity: with/without NED** | Figures 6–7: system with and without NED at 90% GHG savings | Not applicable | Could run with HVC demand zeroed out (requires Demands.csv patch) | **Possible with new run** | Set HVC demand to 0 via patch |
| **Hourly dispatch** | Not a focus (12 TDs used) | `hourly_data/layer_*.txt` | `outputs/hourly_results/` (F_t.csv, R_t_*.csv, Storage_*.csv, Curt.csv) | **Available** for detailed analysis | Same temporal resolution (12 TDs) |
| **Sankey diagram** | Not in paper | `input2sankey.csv` | `input2sankey_FI.csv` + `generated_sankey_FI.html` | **Directly available** | Interactive Plotly HTML |
| **Plotting code** | Custom (not part of ESTD distribution) | `printf` in AMPL run file | `postprocess_future.py`: 5 chart types + comparison mode | **Partially available** — needs extension for multi-scenario sweep plots | Current code compares 2 years; needs adaptation for N scenarios at same year |

---

## C. Proposed Finland 2035 Strategy

### C.1 GHG Savings Case Design

**Baseline reference:** Finland 2017 CO₂ = 41,200 ktCO₂/y  

**Approach:** systematic sweep via `--gwp-limit`, analogous to Colla's 10% steps.

| Case label | GHG savings | `gwp_limit` (ktCO₂/y) | Notes |
|---|---|---|---|
| `unconstrained` | (cost-optimal floor) | `None` (drop gwp constraint) | Reveals economic optimum without climate target |
| `ghg_10pct` | 10% | 37,080 | Very permissive |
| `ghg_20pct` | 20% | 32,960 | |
| `ghg_30pct` | 30% | 28,840 | |
| `ghg_40pct` | 40% | 24,720 | |
| `ghg_50pct` | 50% | 20,600 | Close to existing 2035 run (21,000) |
| `ghg_60pct` | 60% | 16,480 | |
| `ghg_70pct` | 70% | 12,360 | |
| `ghg_80pct` | 80% | 8,240 | |
| `ghg_90pct` | 90% | 4,120 | |
| `ghg_95pct` | 95% | 2,060 | Optional — test near-zero feasibility |

**Formula:** `gwp_limit = 41200 × (1 − savings_fraction)`

**Note:** Colla uses 2015 Belgian emissions as baseline. We use 2017 Finnish as this is the only calibrated year. The meaning of "X% GHG savings" is therefore **relative to Finland 2017** — not same baseline as Colla.

**Colla's unconstrained case already gave ≈38-40% reduction** (cost-optimal 2035 Belgian system); the Finnish unconstrained case will likely also yield a natural floor. If the floor is >10%, the first few constrained cases will be identical to unconstrained.

### C.2 Run Commands (Template)

All runs share the same base:
```bash
python scripts/run_fi_baseline_future.py \
    --year 2035 \
    --name ghg_<XX>pct \
    --gwp-limit <VALUE> \
    --dhn-min 0.42 --dhn-max 0.50 \
    -p calibration/patches/fi_baseline_2035.csv \
    --read-td
```

For `unconstrained` case: omit `--gwp-limit` (passes `None` → constraint dropped).

**`--read-td`** reuses frozen TDs from the existing kmedoid run, avoiding redundant clustering. This is valid because all scenarios share the same weather year and demand profiles.

### C.3 Required Data & Output Files

Per scenario, from `outputs/`:

| File | Extracted metric | Aggregation needed |
|------|------------------|--------------------|
| `Objective.csv` | System cost (M€/y) | None |
| `Resources.csv` | Primary energy by fuel group | `extract_primary_energy()` already implements this |
| `Year_balance.csv` | Biomass allocation by final use | **New aggregation needed** (see C.4) |
| `Gwp_breakdown.csv` | Actual CO₂ emissions, lifecycle GWP | `extract_gwp_totals()` already implements this |
| `Cost_breakdown.csv` | Cost by sector | `extract_cost_by_sector()` already implements this |
| `Assets.csv` | Installed capacities | `extract_capacity()` already implements this |

### C.4 Required New Aggregations

#### Biomass allocation by final use (≈Colla Figure 4)

**Logic:** From `Year_balance.csv`, identify every technology that **consumes** biomass (negative value in WOOD, WET_BIOMASS, BIOWASTE, BIOMASS_RESIDUES, or ENERGY_CROPS_2 columns). For each such tech, compute `biomass_input = −(WOOD + WET_BIOMASS + BIOWASTE + BIOMASS_RESIDUES + ENERGY_CROPS_2)` and map to a final-use category.

**Proposed category mapping:**

| Final-use category (Colla-equivalent) | ESMC technologies (pattern) |
|---|---|
| **HT heat — boilers** | `IND_BOILER_WOOD`, `IND_BOILER_WASTE` |
| **HT heat — CHP** | `IND_COGEN_WOOD`, `IND_COGEN_WASTE` |
| **LT heat DHN — boilers** | `DHN_BOILER_WOOD` |
| **LT heat DHN — CHP** | `DHN_COGEN_WOOD`, `DHN_COGEN_WASTE`, `DHN_COGEN_WET_BIOMASS` |
| **LT heat decentralised** | `DEC_BOILER_WOOD`, `DEC_COGEN_WOOD`, `DEC_ADVCOGEN_WOOD` |
| **Electricity (dedicated)** | unlikely to appear (no `WOOD_POWER_PLANT` in ESMC) |
| **NED / chemicals** | `BIOMASS_TO_HVC`, `BIOMASS_TO_METHANOL` |
| **Mobility fuels** | `PYROLYSIS_TO_LFO`, `PYROLYSIS_TO_DIESEL`, `GASIFICATION_SNG` |

**This mapping must be validated** against actual `Year_balance.csv` row names once all runs are available.

#### Primary energy stacked bar with cost annotation (≈Colla Figure 3)

**Logic:** For each GHG case, extract:
1. Primary energy by fuel group (from `extract_primary_energy()`)
2. System cost (from `Objective.csv`)
3. Actual GHG emissions (from `CO2_EMISSIONS` row in `Resources.csv` or `CO2_net` sum in `Gwp_breakdown.csv`)

**Plot:** X-axis = GHG savings cases. Stacked bars = PE by fuel. Annotate system cost above each bar.

### C.5 Likely Obstacles

| Issue | Severity | Mitigation |
|---|---|---|
| **Infeasibility at high GHG savings** | High | At ~90-95%, model may become infeasible — CCGT/gas may be needed as anchor. Test 90% first; if infeasible, lower to 85%. |
| **Solve time** | Medium | Each 2035 run takes ~4 min. Full 11-case sweep ≈ 45 min. Parallelize if multiple AMPL licenses available. |
| **TDs reuse validity** | Low | All scenarios share demand profiles and capacity factors. `--read-td` is valid. |
| **Unconstrained case may be unusual** | Medium | Without gwp_limit, model may over-import gas or make counter-intuitive choices. This IS informative (like Colla's result showing 38-40% floor). |
| **No biomass supply disaggregation** | Structural | Finland has single WOOD resource. Cannot reproduce Colla's origin-based supply curve. Accept this as a model difference. |
| **NED scope difference** | Structural | Colla's Belgium NED = 102 TWh (15% of PE). Finland HVC = 11.7 TWh. The NED narrative will be less prominent for Finland. |
| **No dedicated biomass electricity tech** | Minor | ESMC does not have a standalone biomass power plant. Biomass electricity comes from CHP co-production. This is actually more realistic. |
| **Crossover=0 in current runner** | Known | Documented pre-existing issue. Current runs succeeded. Monitor for new failures at extreme GHG cases. |

### C.6 What Is Directly Reproducible

1. **Primary energy by fuel vs GHG savings** (≈Figure 3 spirit) — fully reproducible using `Resources.csv` from each scenario
2. **System cost vs GHG savings** — fully reproducible from `Objective.csv`
3. **Biomass allocation by final use vs GHG savings** (≈Figure 4 spirit) — reproducible via `Year_balance.csv` aggregation (new script needed)
4. **Total GHG emissions vs constraint** — reproducible from `Gwp_breakdown.csv`
5. **Installed capacities across scenarios** — reproducible from `Assets.csv`

### C.7 What Is Only Approximately Reproducible

1. **Biomass supply curve / origin analysis** (≈Figure 5) — cannot disaggregate WOOD by geographic origin; can only show total biomass consumed vs available
2. **NED impact analysis** (≈Figures 6-7) — possible by running with/without HVC demand, but Finnish NED is much smaller than Belgian → less dramatic effect
3. **Technology-level cost evolution** — available but Finland's tech mix and costs differ from Belgium

### C.8 What Would Need Model Changes

1. **Multi-origin biomass supply** — would require splitting WOOD into subcategories (local, EU, RoW) with different prices and carbon footprints in `Resources.csv` + `Layers_in_out.csv`
2. **Biomass quality constraint** — would need adding a constraint limiting low-quality share (new model equation)
3. **NED fuel-share constraint** — Belgium has `share_NG_NED=0.158`; Finland model has no equivalent explicit constraint
4. **2015 as reference year** — using 2017 instead; no practical way to calibrate Finnish 2015 without additional work

---

## D. Concrete Next-Step Plan

### Phase 1: Validate & extract existing runs (no new solves)

| Step | Action | Output |
|------|--------|--------|
| 1.1 | Run `postprocess_future.py --auto` on both existing runs to confirm plots generate | Validation that extraction pipeline works |
| 1.2 | Write `extract_biomass_allocation(year_balance)` function | Returns dict: `{final_use_category: GWh}` for one run |
| 1.3 | Validate biomass allocation mapping against 2035 Year_balance.csv (check which techs actually consume WOOD/biomass) | Confirmed category mapping |
| 1.4 | Extract and tabulate: PE, cost, GWP, biomass allocation for both existing scenarios (2035 @49%, 2050 @93%) | Baseline data table |

### Phase 2: Build sweep infrastructure

| Step | Action | Output |
|------|--------|--------|
| 2.1 | Create `scripts/run_ghg_sweep_2035.py` — batch script that loops over GHG cases, calls `run_fi_baseline_future.py` for each | Automation script |
| 2.2 | Create `scripts/analyse_ghg_sweep.py` — reads all scenario outputs, builds comparison DataFrames, generates plots | Analysis + plotting script |
| 2.3 | Design plot templates: (a) PE stacked bar + cost, (b) biomass allocation stacked bar, (c) cost vs GHG curve | Plot specifications |

### Phase 3: Test run (2-3 scenarios, not full sweep)

| Step | Action | Output |
|------|--------|--------|
| 3.1 | Run `unconstrained` case → check natural GHG floor | Baseline cost-optimal emissions level |
| 3.2 | Run `ghg_70pct` (12,360 kt) → test intermediate case | Intermediate result |
| 3.3 | Run `ghg_90pct` (4,120 kt) → test near-zero feasibility | Feasibility check |
| 3.4 | Compare 3 test cases → validate extraction pipeline, check plot quality | Preliminary Figure 3 / Figure 4 drafts |

### Phase 4: Validate category consistency

| Step | Action | Output |
|------|--------|--------|
| 4.1 | For each test case, verify biomass allocation categories are exhaustive (no unclassified techs consuming biomass) | Mapping validation |
| 4.2 | Cross-check: sum of biomass allocation = total biomass in Resources.csv | Conservation check |
| 4.3 | Verify cost decomposition is consistent across scenarios | Cost validation |
| 4.4 | Document any unexpected behaviour (e.g., technologies appearing only at extreme GHG levels) | Anomaly log |

### Phase 5: Full sweep

| Step | Action | Output |
|------|--------|--------|
| 5.1 | Run all 11 GHG cases (unconstrained + 10% steps) | 11 output directories |
| 5.2 | Generate full comparison dataset | Master CSV with columns: case, PE_biomass, PE_gas, ..., cost, co2_actual, biomass_to_HT, biomass_to_NED, ... |
| 5.3 | Generate publication-quality plots | Figure 3, Figure 4 analogues |
| 5.4 | Write interpretation notes | Analysis document |

### Phase 6 (optional): Extensions

| Step | Action | Output |
|------|--------|--------|
| 6.1 | Run NED sensitivity (with/without HVC) at 2-3 GHG cases | NED impact assessment |
| 6.2 | Run 2050 sweep (subset of cases) | 2050 comparison |
| 6.3 | Compare 2035 vs 2050 GHG-cost frontier | Marginal abatement curve |

---

## E. Hypothesis & Decision Log

All decisions underlying the sweep design are tracked here. Each hypothesis has a status: **accepted** (used in sweep), **rejected** (considered and dropped), **deferred** (to test later).

| ID | Category | Status | Hypothesis / Decision | Rationale |
|---|---|---|---|---|
| S01 | GHG baseline | **accepted** | Use Finland 2017 CO₂ = 41,200 ktCO₂ as 100% reference | Only calibrated year; validated <0.1% error |
| S02 | GHG steps | **revised** | Redesigned: unconstrained + 50/65/70/75/80/85/90/95%. Not uniform 10% steps. | Natural optimum at ~69% makes 10-60% cases redundant (all slack). Focused on binding range. |
| S03 | GHG formula | **accepted** | `gwp_limit = 41200 × (1 − savings)` | Direct, unambiguous; GWP = co2_net-based |
| S04 | Year | **accepted** | Start with 2035 only, defer 2050 | Colla paper is 2035; faster solves; more room to explore |
| S05 | Brownfield | **accepted** | Keep fi_baseline_2035.csv patch (wind/PV f_min, elec import 25 TWh) | Consistency with existing national_plan_2035 run |
| S06 | DHN bounds | **accepted** | 42–50% (same as baseline run) | Finnish reality ~46%; consistent with preflight doc H12 |
| S07 | f_perc | **accepted** | Disabled (`--f-perc` not passed) | Same as baseline; avoids infeasibility from percentage constraints |
| S08 | TD reuse | **accepted** | `--read-td` (reuse frozen kmedoid TDs from baseline run) | Same weather/demand year; avoids redundant clustering |
| S09 | 95% case | **accepted** | 95% savings case included and solved successfully | No infeasibility; cost = 23.52 bn€/y (+565 M€ vs unconstrained) |
| S10 | NED sensitivity | **deferred** | Run with/without HVC demand at select cases | Secondary analysis; requires Demands.csv patch |
| S11 | Biomass supply disaggregation | **rejected** | Do not split WOOD into sub-categories | Would require Layers_in_out + Resources changes; not needed for first pass |
| S12 | Biomass quality constraint | **rejected** | Do not add quality-class constraint | Not in current ESMC; model modification out of scope |
| S13 | 2050 sweep | **deferred** | Run 2050 sweep after 2035 validated | Sequential approach; 2035 first |
| S14 | Existing run reuse | **accepted** | Include national_plan_2035 (gwp=21000) as ~49% reference point | **Warning:** this run used OLD code (GWP not injected) — results are equivalent to unconstrained. Still useful as validation reference. |
| S15 | GHG accounting scope | **revised** | Use CO2_net from Gwp_breakdown.csv (NOT gross CO2_EMISSIONS from Resources.csv) | CO2_net is the metric used in the AMPL GWP constraint. Gross CO2_EMISSIONS differs by ~7,900 kt due to biogenic credits. |
| S16 | BAU baseline | **discussed** | 2035 data is a transition scenario (coal=0, DEA projected costs, EU Ref demands), not BAU. -69% floor is structural. | Colla's Belgium at -38% still has coal. Could add coal-available sensitivity, but Finland's coal ban is realistic for 2035. Accept as-is. |
| S17 | --relax-co2 | **rejected for 2035** | CO2 layer relaxation is for 2017 calibration only. CO2_EMISSIONS absorbs all CO2_INDUSTRY freely (avail=1e15); CCS is not forced. | Verified: INDUSTRY_CCS captures only 0.3 kt in unconstrained 2035. |
| S18 | Nuclear phase-out scenario | **proposed** | Add sensitivity run with NUCLEAR f_min=2.49 GW (Olkiluoto fleet only, Loviisa 1+2 retired). Current baseline has f_min=4.36 GW forcing 32.4 TWh nuclear output (~75% of direct electricity demand). | Loviisa 1/2 licences expire 2027/2030; retirement before 2035 is plausible. Phase-out forces more wind/solar/gas, raises costs, and changes GHG floor. Implement as patch: `Technologies FI NUCLEAR f_min 2.49`. |

## F. Data Provenance & Baseline Interpretation

### F.1 Why the 2035 "Unconstrained" Baseline Is Already a Transition Pathway

The unconstrained cost-optimal 2035 solution achieves ~69% CO₂_net reduction vs 2017
without any GHG constraint. **This is not a model bug — it reflects the data.**

The 2035 dataset is inherently a transition scenario, not a Business-As-Usual (BAU):

| Factor | Effect | Source |
|--------|--------|--------|
| **Coal = 0** | `avail_exterior = 0` in `Data/2035/02_REF_REGION/Resources.csv` — coal phase-out is baked in | EU policy; Finnish coal ban 2029 |
| **DEA 2035 tech costs** | Wind ≈30 €/MWh, PV ≈25, HP COP~3.5 — renewables/HPs are cost-competitive vs fossil | Danish Energy Agency Technology Catalogues (2020 vintage) |
| **EU Reference Scenario 2020 demands** | Efficiency gains in space heating, electricity; already lower than today | European Commission, 2020 |
| **Nuclear fleet** | 88 TWh/y at 3.9 €/MWh (URANIUM) — OL3 + existing units | Fixed in data; Finnish fleet reality |
| **Biomass undercuts gas** | WOOD = 22 €/MWh vs GAS = 44 €/MWh | `Data/2035/02_REF_REGION/Resources.csv` |
| **Discount rate = 1.5%** | Strongly favors capital-intensive clean technologies (wind, nuclear, HP) | Thiran thesis (Ch. 3), central public investor perspective |
| **Brownfield patch** | WIND_ONSHORE f_min=6 GW, WIND_OFFSHORE f_min=1.6 GW, PV f_min≈1.3 GW | `calibration/patches/fi_baseline_2035.csv` |

**Contrast with Colla (Belgium):**
- Colla's unconstrained Belgian 2035 has a natural floor at **-38%** (not -69%)
- Belgium still has coal available at -38% (visible in Colla Fig. 3A, grey at bottom)
- Belgium has 2 GW nuclear cap (vs Finland's ~5 GW fleet + OL3)
- Belgian NED = 102 TWh (large fossil feedstock demand) vs Finnish HVC = 12 TWh
- Belgian system is structurally more carbon-intensive to start with

**Conclusion:** The -69% floor is a genuine structural result — Finland's combination of
nuclear baseload, abundant cheap biomass, and coal phase-out means the cost-optimal 2035
system is already highly decarbonized. The policy-relevant range starts at 70%.

### F.2 Data Sources (Thiran Thesis, Ch. 3)

| Data category | Source | Details |
|---|---|---|
| **Technology costs & efficiency** | Danish Energy Agency (DEA) Technology Catalogues | 3 reports: electricity/DH, storage, renewable fuels. Point estimates for 2035 (no learning curves — just projected costs) |
| **Renewable potentials** | JRC ENSPRESO database | Wind, solar, biomass by country. Biomass regrouped: 17 ENSPRESO commodities → 5 ESMC categories (WOOD, WET_BIOMASS, BIOWASTE, BIOMASS_RESIDUES, ENERGY_CROPS_2) |
| **Demand projections** | EU Reference Scenario 2020 | Residential/tertiary split via EUCalc; industrial split via HRE4; NED from Rixhon et al. |
| **Hydro potentials** | JRC Hydropower Plants + e-Highway + JRC PHS | Country-level existing + expansion potential |
| **Fuel prices** | DEA + literature | Gas=44 €/MWh, Diesel=80 €/MWh, WOOD=22 €/MWh (local FI), URANIUM=3.9 €/MWh |
| **Transport demands** | EU Ref 2020 + EUROCONTROL (aviation) | Mobility by mode |
| **NED (feedstock)** | Eurostat (HVC), Prodcom (methanol), UNFCCC NIS (ammonia) | HVC demand = 11,705 GWh for Finland |

### F.3 CO₂ Layer Architecture — Not a Constraint

The CO2_INDUSTRY layer in `Data/2035/00_INDEP/Layers_in_out.csv` has 42 technologies
with non-zero entries (all combustion techs produce CO2_INDUSTRY). However:

- `CO2_EMISSIONS` resource absorbs CO2_INDUSTRY freely (coefficient = -1.0, availability = 1e15)
- INDUSTRY_CCS captures only 0.3 kt in the unconstrained case (economically suboptimal)
- **The CO2 layer is NOT forcing CCS** — it just tracks carbon mass balance

The `--relax-co2` option in `run_calib_manual.py` is for 2017 calibration only (historical
year where CCS didn't exist). It is **not needed and should not be used for 2035 runs**.

### F.4 Why the Constraint Only Bites at 70%

The remaining 13 Mt CO₂_net in the unconstrained case comes from:

| Source | GAS consumed (GWh/y) | CO₂_net contribution | Notes |
|--------|---------------------|---------------------|-------|
| DEC_THHP_GAS (decentralised gas heat) | 27,424 | ~5.9 Mt | **Main source** — gas heat pumps |
| Diesel-to-jet-fuel pathway | 12,963 | ~4.0 Mt | Aviation — no biomass alternative below 95% |
| BUS_COACH_CNG_STOICH | 2,737 | ~0.7 Mt | CNG buses |
| CARGO_LNG | 1,985 | ~0.5 Mt | LNG cargo |
| BOAT_FREIGHT_NG | 1,913 | ~0.5 Mt | NG freight boats |
| Other (H2_NG, minor) | ~200 | ~0.05 Mt | Negligible |

**Decarbonization pathway across the sweep:**

| Scenario | DEC_THHP_GAS (GWh) | Replacement mechanism |
|----------|--------------------|-----------------------|
| Unconstrained | 27,424 | — |
| 75% | 16,189 | Electrification (HPs replace gas HPs) |
| 90% | 968 | Nearly fully electrified |
| 95% | 43 | Gone; + bio-diesel/jet-fuel for transport |

At 70%, the model starts trimming DEC_THHP_GAS. At 95%, it must also decarbonize
aviation (bio-jet-fuel) and shipping, which requires biomass-to-liquid pathways.

### F.5 Why Biomass Allocation Stays Flat (50-90%)

The biomass allocation stability is **genuine model behavior**, explained by fixed demands:

| Consumer | Unconstr. (GWh) | 75% | 95% | Explanation |
|----------|-----------------|-----|-----|-------------|
| BIOMASS_TO_HVC | 27,869 | 27,869 | 27,869 | **Fixed demand** — HVC production is inflexible |
| IND_BOILER_WOOD | 12,446 | 11,788 | 25,369 | HT heat — only major variable |
| IND_BOILER_WASTE | 11,094 | 11,094 | 0 | **Disappears at 95%** — replaced by more WOOD |
| IND_BOILER_BIOWASTE | 9,704 | 9,704 | 9,705 | Stable — uses all available biowaste |
| BIOMETHANATION_WET | 1,450 | 1,450 | 1,450 | Stable — uses all available wet biomass |
| BIOMASS_TO_METHANOL | 789 | 790 | 791 | Stable — fixed methanol demand |
| BIOMASS_TO_DIESEL | 0 | 0 | 11,276 | **NEW at 95%** — transport decarbonization |
| BIOMASS_TO_JET_FUEL | 0 | 0 | 8,777 | **NEW at 95%** — aviation decarbonization |
| **Total** | **63,360** | **62,703** | **85,242** | +35% only at 95% |

**Key insight:** 44% of biomass goes to HVC (fixed demand), and biowaste/wet_biomass
are fully consumed regardless of GHG target (cheapest resource, fully used). The only
"free" variable is how much additional WOOD goes to industrial heat vs mobility fuels.
Colla's Belgium is fundamentally different: NED = 102 TWh creates a large biomass
competition between NED/heat/mobility that shifts visibly across GHG scenarios. In
Finland, HVC = 28 TWh is too small to create that competition.

---


### F.1 Sweep Configuration

**Cases run:** unconstrained + 50% + 65% + 70% + 75% + 80% + 85% + 90% + 95%  
**Existing reference:** national_plan_2035 (~49%)  
**All 9 cases solved successfully.** Solver: CPLEX 22.1 barrier (crossover=0).

> **Critical bug fixed during this work:** `run_fi_baseline_future.py` was not injecting the user-specified `gwp_limit` value into the AMPL data. The config's `gwp_limit_overall` only controlled whether the AMPL constraint was dropped, but the param stayed at `Infinity` in the `.dat` file. Fixed by adding `model.data_indep['Misc_indep']['gwp_limit_overall'] = args.gwp_limit` before `print_data()`.

> **CO₂ metric distinction:** The GWP constraint uses `CO2_net` (net of biogenic carbon credits), NOT gross `CO2_EMISSIONS` from Resources.csv. In the unconstrained case: CO2_net = 12,960 kt vs gross = 20,877 kt — a ~7,900 kt difference from biogenic credits.

### G.2 Summary Table

| Case | GWP limit (kt) | Cost (bn€/y) | CO₂ net (Mt) | CO₂ gross (Mt) | PE (TWh) | Biomass (TWh) | Marginal cost vs uncon. |
|------|----------------|---------------|---------------|-----------------|----------|---------------|------------------------|
| unconstrained | — | 22.96 | 13.0 | 20.9 | 304 | 63.4 | — |
| national_plan (~49%) | 21,000 | 22.96 | 13.0 | 20.9 | 304 | 63.4 | +0 (SLACK) |
| 50% | 20,600 | 22.96 | 13.0 | 20.9 | 304 | 63.4 | +0 (SLACK) |
| 65% | 14,420 | 22.96 | 13.0 | 20.9 | 304 | 63.4 | +0 (SLACK) |
| 70% | 12,360 | 22.96 | 12.4 | 21.0 | 305 | 63.7 | +2 M€ (barely binding) |
| 75% | 10,300 | 23.02 | 10.3 | 20.6 | 298 | 62.7 | +59 M€ |
| 80% | 8,240 | 23.09 | 8.2 | 20.3 | 289 | 61.9 | +131 M€ |
| 85% | 6,180 | 23.20 | 6.2 | 21.5 | 286 | 63.4 | +239 M€ |
| 90% | 4,120 | 23.32 | 4.1 | 22.7 | 286 | 65.0 | +358 M€ |
| 95% | 2,060 | 23.52 | 2.1 | 27.1 | 298 | 85.2 | +565 M€ |

### G.3 Key Findings

1. **Natural CO₂ floor at ~69% savings.** The unconstrained 2035 optimal already achieves CO₂_net = 12,960 kt (vs 41,200 baseline). This means Finland's cost-optimal 2035 system *naturally* decarbonizes ~69% without any GHG constraint — driven by nuclear fleet, biomass CHP, and cheap wind.

2. **Constraint binds only above ~69%.** Cases at 50% and 65% are identical to unconstrained (slack). The 70% case is barely binding (+2 M€).

3. **Moderate marginal abatement costs.** Going from 69% to 95% savings costs only +565 M€/y (+2.5% of system cost). The curve steepens above 90%.

4. **Biomass role transformation at 95%.** Total biomass jumps from ~63 TWh to 85 TWh only at 95% savings. The Fig. 4 plot reveals this is driven by **mobility fuels** (pink bar) — the model switches to pyrolysis/gasification for transport decarbonization.

5. **Gross CO₂ paradox.** Gross CO₂ emissions *increase* from 20.3 Mt (80%) to 27.1 Mt (95%) — because aggressive use of biogenic resources increases combustion emissions that are offset by biogenic carbon credits in the CO₂_net accounting. This is a Colla-relevant finding about biogenic carbon accounting.

6. **Primary energy shifts.** From the stacked bar:
   - Gas (red) shrinks progressively from unconstrained → 95%
   - Oil products (grey base) remain constant (~88 TWh) until 95% where they shrink
   - Wind (blue) grows modestly from 75% onwards
   - Biomass (green) stable at ~30 TWh until 95% jump

7. **Biomass allocation stability.** The biomass allocation by final use is remarkably stable across 50-90% cases: HT heat boilers (~20 GWh), NED/chemicals (~30 GWh), biogas (~2 GWh). Only at 95% does the structure change.

### G.4 Colla Comparison

| Finding | Colla (Belgium) | Finland 2035 sweep |
|---------|-----------------|-------------------|
| Natural GHG floor | ~38-40% savings | **~69% savings** (much higher, due to nuclear + biomass) |
| GHG-cost shape | Convex, steepening above 70% | Convex, steepening above 90% |
| Biomass dominates at high savings | Yes — supply becomes bottleneck | Yes, but later (95% vs 70-80% for Colla) |
| NED competes for biomass | Major effect (102 TWh NED) | Minor effect (HVC only 11.7 TWh) |
| Biomass geographic origin matters | Key driver of supply curve shape | **Not modelled** (single WOOD resource) |

### G.5 Run Directories

All in `case_studies/FI/manual_runs/`:
- `20260413_133551__sweep_unconstrained`
- `20260324_141200__national_plan_2035`
- `20260413_133810__sweep_ghg_50pct`
- `20260413_134109__sweep_ghg_65pct`
- `20260413_134404__sweep_ghg_70pct`
- `20260413_134726__sweep_ghg_75pct`
- `20260413_135021__sweep_ghg_80pct`
- `20260413_135303__sweep_ghg_85pct`
- `20260413_135617__sweep_ghg_90pct`
- `20260413_140053__sweep_ghg_95pct`

Analysis outputs in `case_studies/FI/manual_runs/ghg_sweep_analysis/`:
- `ghg_sweep_2035_master.csv` — all metrics
- `fig3_primary_energy_vs_ghg.png` — Colla Fig. 3 analogue
- `fig4_biomass_allocation_vs_ghg.png` — Colla Fig. 4 analogue
- `cost_vs_ghg_savings.png` — system cost curve
- `co2_actual_vs_limit.png` — CO₂ net vs constraint

## H. Scripts Inventory

| Script | Purpose | Status |
|---|---|---|
| `scripts/run_ghg_sweep_2035.py` | Batch runner — loops over GHG cases, calls run_fi_baseline_future.py | Created, tested |
| `scripts/analyse_ghg_sweep.py` | Post-processing — builds master CSV, Colla-style plots (Fig 3, 4), cost curve | Created, tested, 3 bugs fixed |
| `scripts/run_fi_baseline_future.py` | Single-case runner (existing) | **Modified** — GWP limit injection fix |
| `scripts/postprocess_future.py` | Per-run plots + comparison (existing) | Used as-is |

---

## Appendix: Key Model Differences — Finland ESMC vs Colla Belgium ESTD

| Dimension | Belgium (Colla) | Finland (ESMC) | Impact |
|---|---|---|---|
| **Model version** | EnergyScope TD (single monolithic) | EnergyScope Multi Cells (modular Python + AMPL) | Different data pipeline; same core LP structure |
| **Year** | 2035 | 2035 (primary), 2050 (secondary) | Comparable |
| **Biomass resources** | 10 WOOD categories (origin × quality) + WET_BIOMASS + WASTE | 1 WOOD + WET_BIOMASS + BIOWASTE + BIOMASS_RESIDUES + ENERGY_CROPS_2 + WASTE | No geographic/quality disaggregation |
| **Biomass availability** | ~100-160 TWh (depending on scenario) | Wood: 110.8 TWh + minor categories ≈ 130 TWh total | Comparable scale relative to system size |
| **NED size** | 102 TWh (15% of PE) | HVC: 11.7 TWh (much smaller share) | NED less prominent in Finnish system |
| **NED constraint** | share_NG_NED = 15.8%, 84.2% as LFO | No explicit NED fuel-share constraint | NED pathway less constrained |
| **Nuclear** | 2 GW cap | 4.36-5.0 GW (Finnish fleet: OL3 + existing) | Finland nuclear-heavy |
| **DHN** | 2-37% | 42-50% (overridden to match Finnish reality) | Finland DHN-heavy |
| **Discount rate** | 1.5% | Inherited from REF_REGION (likely same) | Comparable |
| **Currency** | MCHF | M€ | Unit difference |
| **CO₂ baseline** | 2015 Belgian (incl. NED emission) | 2017 Finnish = 41,200 ktCO₂ (excl. lifecycle) | Different baseline year and accounting scope |
| **GHG accounting** | 100% of NED carbon included in GHG | CO₂_net column in Gwp_breakdown (direct combustion) | May undercount NED emissions in Finnish model |
| **Solver** | CPLEX 12.9 MIP | CPLEX 22.1 LP barrier | More modern solver |
| **Typical days** | 12 | 12 | Same |
