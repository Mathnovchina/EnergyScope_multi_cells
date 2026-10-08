---
title: "Concept Note — Coupling G4M with EnergyScope Finland"
subtitle: "Forest-management and disturbance-driven biomass supply curves, and the forest carbon sink"
author: "Matthieu Bordenave"
institutions: "University of Pisa · IIASA (ForestNavigator / Biodiversity & Natural Resources) · UCLouvain"
date: "2026-10"
status: "Draft for discussion with IIASA"
supersedes: "Docs/strategy_IIASA_concept_note.md (FORTRAN-coupled version, April 2026)"
---

# Coupling the IIASA Global Forest Model (G4M) with EnergyScope Finland

> **Purpose of this note.** The original plan (April 2026) was to couple the ForestNavigator
> disturbance modules (FLAM, PICUS) to a Finnish stand-level forest simulator maintained by a
> partner team ("the FORTRAN model"). That coupling is now blocked because the partner team is no
> longer responsive. This note proposes an **alternative that stays entirely within the IIASA
> toolchain**: use the **Global Forest Model (G4M)**, for which Finnish data already exist, to
> generate the forest-management and disturbance-driven biomass supply curves that feed
> EnergyScope Finland. It also proposes to close the single most important methodological gap in
> the current working paper — the **absence of the forest carbon sink** — and opens a path toward a
> European extension with the **BeWhere** model.

---

## 1. Context and motivation

Forest biomass supplies roughly a quarter of Finland's primary energy and is the main domestic lever
for deep decarbonisation. But its availability is **not a fixed number**: it is shaped by forest
management choices, competing industrial uses (pulp, paper, sawnwood), ecological constraints on
residue and deadwood retention, and — increasingly — by natural disturbances amplified by climate
change (bark beetle, windstorm, wildfire).

Most whole-energy-system models treat wood as a single, homogeneous, unconstrained resource. Colla
et al. (2022) showed for Belgium that representing biomass instead as a **multi-step marginal-cost
supply curve** materially changes its optimal allocation, especially under deep decarbonisation. The
first working paper of this project applied and extended that idea to Finland — a structurally richer
and more policy-contested case — and is now essentially complete (Section 2).

The logical next step is to make the supply curves **endogenous to forest dynamics** rather than
read from a static database, so that (i) management intensity and (ii) physical disturbance shocks
propagate into the energy system through both the **quantity/cost of wood** and the **forest carbon
balance**. G4M is well suited to provide exactly these outputs for Finland.

---

## 2. State of the working paper (what is already done)

The first paper — *Forest-management biomass supply curves in a whole-energy-system model of
Finland* — is built and its results are stable. In short:

- **Calibrated 2017 baseline.** EnergyScope Finland reproduces the 2017 national energy balance to a
  weighted error of ~1.2% across 14 scored indicators (primary energy, electricity mix, CO₂ within
  0.1%). Reference run `case_studies/FI/manual_runs/20260323_173930__2017_baseline`
  (`relax_co2=true`, 12 typical days). See `Docs/finland_2017_validation_justifications.md`.
- **Stepwise Finnish wood supply curves (2035).** The single `WOOD` resource is replaced by four
  domestic steps plus an import backstop, dispatched in merit order:

  | Step | Interpretation | Marginal cost |
  |---|---|---|
  | `WOOD_FI1` | aggregate industrial by-products: black liquor, bark, sawdust (proxied by ENSPRESO `MINBIOWOOa`; flag T1) | 11 €/MWh |
  | `WOOD_FI2` | logging residues (branches, tops) | 22 €/MWh (26 in S3) |
  | `WOOD_FI3` | secondary woodchips / sawdust from processing | 27 €/MWh |
  | `WOOD_FI4` | direct fuelwood + landscape-care wood | 33 €/MWh |
  | `WOOD_FI5` | Baltic/Nordic import backstop | 70 €/MWh |

- **Three forest-management scenarios**, mapped from the Finnish policy literature
  (Blattert et al. 2022) and the ecological harvest ceiling (Mönkkönen et al. 2024), and
  parameterised from the EC/JRC **ENSPRESO** biomass database:
  - **S1 / BES** (Bioeconomy) — stylised high-mobilisation case, ~122 TWh domestic wood;
  - **S2 / NFS** (National Forest Strategy) — ENSPRESO-medium baseline, ~102 TWh;
  - **S3 / BDS** (Biodiversity) — conservative ceiling revised down to ~40 TWh after a three-way
    audit against LUKE 2024 observed use, the Mönkkönen ecological ceiling, and competing industrial
    roundwood demand.
- **Completed 3 × 3 scenario matrix**: {S1, S2, S3} × {unconstrained, −95% GHG with nuclear, −95%
  GHG no-nuclear}. Runs in `case_studies/FI/forest_scenarios_2035/`. Headline findings: the 2035
  system is already ~70% below 2017 even unconstrained; under −95% the conservation scenario (S3)
  saturates its wood ceiling and becomes the most expensive configuration; removing nuclear sharply
  raises the value of biomass in S1/S2 but S3 cannot expand.

**Methodological audit — is this well grounded?** Yes, with two caveats that the paper already
states honestly, and one gap that this concept note is designed to close:

1. *Grounded:* the ENSPRESO→scenario mapping is fully traceable (`Docs/biomass_scenario_mapping.md`),
   the cost/GHG parameters follow Colla (2022) and RED II Annex VI, and the S1 (+20%) and S3 (40 TWh)
   values are explicitly flagged as stylised/revised rather than raw ENSPRESO.
2. *Caveat (static & exogenous):* the curves are read from ENSPRESO potentials, not from a forest
   model. Scenarios differ only in **availability and cost**, with no forest growth dynamics, age
   structure, or disturbance.
3. **Gap (the decisive one): the forest carbon sink is absent.** The binding climate constraint in
   the model (`ESMC_model_AMPL.mod`, `Minimum_GWP_reduction`) is

   $$\sum_{r \in \text{RESOURCES}} \text{CO2\_net}[r] \;\le\; \text{gwp\_limit},$$

   i.e. **energy-system combustion emissions only**. Biomass combustion is carbon-neutral by
   assumption, and there is **no term for the forest sink, LULUCF flux, or harvested-wood-product
   (HWP) carbon**. This is confirmed in the data provenance and hypothesis logs. Consequently the
   current model sees the climate difference between intensive (S1) and conservation (S3) harvest
   *only* through supply-chain GHG — it **cannot represent the dominant climate effect of harvest
   intensity**, namely that lower harvest raises standing stock and the sink, while intensive harvest
   depletes it. Finnish and EU literature treat this asymmetry as first-order (e.g. Blattert's
   per-scenario sinks: NFS ≈ 80, BES ≈ 28 MtCO₂ yr⁻¹; BDS largest). **Closing this gap is the core
   scientific motivation for the next phase.**

---

## 3. Research questions

- **RQ1 — Management.** How do contrasting forest-management regimes reshape the *dynamic* Finnish
  wood supply curve (quantity, quality, marginal cost, 2025–2060), when derived from a forest model
  (G4M) rather than a static potential database?
- **RQ2 — Sink coupling.** When the **forest carbon balance** (sink/source and HWP) is added to the
  national GHG budget, how does the optimal energy mix and the cost of deep decarbonisation change
  across management scenarios — and does the ranking of S1/S2/S3 on climate grounds change?
- **RQ3 — Shocks.** How does a compound physical disturbance (windstorm → bark-beetle, with wildfire
  sensitivity) propagate into the energy system — through a short calamity-wood pulse, a temporary
  price depression, a multi-year supply deficit, **and** a sink loss — and does it create stranded
  biomass-conversion assets or delay the transition?
- **RQ4 — Policy framing.** If the "neutral" baseline is replaced by a **sink-maximising / LULUCF
  net-zero** scenario, what does economy-wide net-zero (energy + land) imply for the energy system,
  versus energy-only net-zero?
- **RQ5 — Scaling (collaboration).** Can the same supply-curve representation be scaled to Europe and
  to competing end-uses (construction/HWP) with BeWhere, to study cross-sectoral biomass allocation?

---

## 4. State of knowledge / existing literature

**Supply-curve representation of biomass.** Colla et al. (2022) — origin- and quality-differentiated
wood supply steps in a whole-energy-system model; basis of the present approach.

**Finnish forest policy and ecological ceilings.** Blattert et al. (2022, *Forest Policy and
Economics*) translate three national strategies (BES/NFS/BDS) into quantitative management scenarios
with explicit roundwood, bioenergy, deadwood, set-aside and **carbon-sink** targets. Mönkkönen et al.
(2024) define the ecologically safe harvest ceiling (~58–60% of maximum sustainable for Southern
Finland). These anchor the S1/S2/S3 narratives and provide independent per-scenario sink estimates.

**Forest carbon sink, HWP and substitution.** A large literature (incl. the project's own
bibliography) shows that the sink reduction from increased harvest often exceeds, in the short-to-
medium term, the fossil substitution benefit of using the wood — the asymmetry the energy-only model
cannot currently represent. Motivates RQ2/RQ4.

**Physical disturbances and timber markets.** The project's review
(`Docs/literature/forest_disturbance_timber_economics_report.md`, 121 sources) documents that
disturbances now drive ~16% of European harvest (Patacca et al. 2023), depress prices 20–70%, and
raise salvage costs 10–64% (Kärhä et al. 2018, Finland); the Czech bark-beetle calamity
(Hlásny et al. 2021, *For. Ecol. Manage.* — `j.foreco.2021.119075`) is the reference compound-shock
case. Finland's direct impacts are so far limited but its vulnerability is rising
(Venäläinen et al. 2020).

**IIASA forest and bioenergy models (the proposed tools).**
- **G4M (Global Forest Model)** — IIASA's geographically explicit forest model (Kindermann et al.
  2008; Gusti 2010; Lauri, Forsell, di Fulvio et al.). It decides afforestation/deforestation and
  **optimises management** (rotation, thinning, species, harvest intensity) from wood prices and
  costs, and reports **harvestable wood by assortment** (sawlogs, pulpwood, residues, fuelwood)
  **and the full carbon account** (living biomass, deadwood, soil, HWP) and **net LULUCF CO₂ flux**.
  It is the forest module in ForestNavigator and is routinely run for Finland within pan-European
  setups. *(Exact Finnish resolution and I/O to be confirmed with the IIASA G4M team.)*
- **Disturbance modules** — ForestNavigator D3.4 (Krasovskiy et al. 2025) assess disturbance impacts
  on forest mitigation potential (FLAM for wildfire; bark-beetle and wind modules). We propose to use
  G4M's disturbance-aware outputs for Finland rather than re-implementing a stand-level coupling.
- **BeWhere** — IIASA's spatially explicit techno-economic optimisation (MILP) for biomass supply
  chains and plant siting, extended to forest-industry/construction uses (Leduc, Kraxner, Schipfer
  et al.). Candidate tool for the European, cross-sectoral extension (RQ5).

---

## 5. Methodology — possibilities

### 5.A  Management-scenario supply curves from G4M (replaces the FORTRAN coupling)

For each management scenario and climate pathway, run G4M for Finland over 2025–2060 and extract,
per year and (optionally) per sub-region (south / central / north):

- harvestable volume by assortment (sawlogs, pulpwood, logging residues, fuelwood, stumps);
- fractions ecologically available after deadwood/residue-retention rules (scenario-specific);
- the **net forest carbon flux** (growing-stock change + deadwood + soil + HWP), i.e. the LULUCF
  term — *this is the new output the ENSPRESO approach cannot provide.*

Convert assortments to the existing `WOOD_FI1…FI4` steps (volume→energy factors already defined in
`Docs/biomass_scenario_mapping.md`), with marginal costs from Finnish statistics (LUKE) and/or the
di Fulvio IIASA forest-management cost dataset. The result is a **dynamic, internally consistent**
replacement for the current static ENSPRESO curves, keeping the EnergyScope implementation unchanged
(steps remain `NOT_LAYERS` resources feeding the `WOOD` layer — no AMPL change needed for the curves
themselves).

Proposed scenarios (aligned with Blattert / Mönkkönen / ForestNavigator), each under RCP4.5 (GWL2)
and RCP8.5 (GWL3):

| Label | Management logic | Harvest level |
|---|---|---|
| **S1 Intensive** | maximise roundwood + energy residues; rotation forestry | ~96% of sustainable ceiling |
| **S2 Balanced** | NFS targets; moderate biodiversity measures; mixed rotation/CCF | ~80% |
| **S3 Conservation** | biodiversity-first; extended rotations, CCF, set-aside, deadwood retention | ~58–60% |
| **S0 Sink-max / net-zero** *(new — see 5.C)* | minimise harvest / maximise sink subject to meeting wood floors | lowest |

### 5.B  Disturbance-shock supply curves from G4M + disturbance modules

Use G4M's disturbance-aware runs (or G4M + FLAM/bark-beetle/wind outputs from ForestNavigator) to
build **time-profiled** supply curves around a compound event, rather than a single lower ceiling.
A disturbance scenario produces three superimposed effects on the curve:

1. **Calamity-wood pulse (Q3):** a large, cheap, time-limited (≈18–24 month) salvage volume, quality-
   penalised (blue-stain, moisture 20–55%, LHV −10…−25%), usable in direct combustion only.
2. **Structural supply deficit:** reduced `WOOD_FI1/FI2` availability for 10–15 years from depleted
   cohorts and damaged area out of rotation.
3. **Sink loss:** an immediate LULUCF emission from killed biomass and foregone future growth.

Energy-system response is studied as a **pre-shock → post-shock** pair with *constrained
re-optimisation* (investment lead times lock part of the pre-shock fleet via inherited lower bounds
on installed capacity), to expose stranded-asset and transition-delay risks (RQ3).

### 5.C  Coupling the forest carbon sink into EnergyScope (the key upgrade)

Make the national climate target a **land–energy coupled budget**. Replace the energy-only constraint

$$\sum_{r} \text{CO2\_net}[r] \le \text{gwp\_limit}$$

with

$$\sum_{r} \text{CO2\_net}[r] \;-\; \underbrace{S_{\text{forest}}(\text{scenario}, \text{year}, \text{disturbance})}_{\text{net sink from G4M, }<0\text{ when a sink}} \;\le\; \text{gwp\_limit},$$

where $S_{\text{forest}}$ is an **exogenous, scenario-dependent net forest/HWP CO₂ flux** supplied by
G4M (a single national parameter per scenario-year, extendable to sub-regions). This is a small,
transparent AMPL change (one parameter + one term in `Minimum_GWP_reduction`) and it makes harvest
intensity and disturbances act on the energy system through the sink, not only through wood
availability. It enables:

- **RQ2:** does deep decarbonisation become *cheaper* under conservation (large sink "credit") or
  does the energy-only penalty dominate?
- **RQ4 / new S0 scenario:** define net-zero over **energy + land** (require
  $\sum_r \text{CO2\_net} \le S_{\text{forest}}$), i.e. a **sink-maximising / LULUCF-net-zero**
  baseline that replaces the current "neutral" S2 framing. This directly answers the user intent to
  "maximise the sink or ensure net zero."

*Scope control:* $S_{\text{forest}}$ is treated as an **exogenous input from G4M**, not endogenised —
EnergyScope does not optimise forest management, it responds to it. This keeps the coupling one-way
and tractable for a first paper, consistent with the open-question Q6 (LULUCF accounting treatment)
carried over from the previous note.

### 5.D  European, cross-sectoral extension with BeWhere (collaboration track)

As a parallel/follow-on track with **Fabian Schipfer** and **Shubham Tiwari** (IIASA), the
quality-and-cost-differentiated supply-curve representation can be scaled from Finland to Europe and
from energy to **competing end-uses (construction / engineered wood / HWP)** using **BeWhere**. The
Finnish EnergyScope study would provide the national, energy-system-optimisation "deep dive"; BeWhere
would provide the spatially explicit, multi-sector, European allocation view. The shared object — a
transferable, disturbance- and management-sensitive biomass supply curve — is the natural bridge
between the two models and the basis for a joint proposal.

---

## 6. Partners and roles

| Partner | Tool | Role |
|---|---|---|
| **IIASA — ForestNavigator / BNR (G4M team; A. Krasovskiy, F. di Fulvio, P. Lauri)** | G4M (+ FLAM / beetle / wind) | Provide Finnish G4M management & disturbance runs; net carbon/LULUCF flux; assortment-level harvest; management-cost data |
| **IIASA — F. Schipfer, S. Tiwari** | BeWhere | European, cross-sectoral extension (energy vs. construction/HWP); joint proposal |
| **J. Bordenave (Pisa / UCLouvain)** | EnergyScope Finland (ESMC) | Build supply curves from G4M outputs; implement sink coupling; run & analyse scenario/shock matrix; coordinate |
| **JYU / LUKE (if re-engaged)** | NFI data, salvage/cost statistics | Finnish ground-truth for calibration and salvage parameters |

---

## 7. Path forward

1. **[IIASA — G4M team]** Confirm that G4M can deliver, for Finland (2025–2060, by management
   scenario × GWL2/GWL3): (a) harvestable wood by assortment, (b) ecologically available fractions,
   (c) **net forest + HWP carbon flux**, and (d) disturbance-driven mortality/salvage. Confirm spatial
   resolution (national vs. south/central/north) and output format.
2. **[J. Bordenave]** Freeze and tag the working-paper model + runs (reproducibility, Section of
   AGENT.md); prototype the **sink-coupling AMPL term** (5.C) against the existing 2035 matrix using
   *literature* sink values (Blattert) as a placeholder, to demonstrate the mechanism before G4M data
   arrive.
3. **[J. Bordenave + IIASA]** Map G4M assortments → `WOOD_FI1…FI4`; adopt di Fulvio cost data where
   Finland coverage is sufficient, cross-validated against LUKE.
4. **[All]** Agree scenario definitions (incl. the new **S0 sink-max/net-zero**) and the disturbance
   event design (compound windstorm → beetle, GWL2 primary).
5. **[IIASA — Schipfer/Tiwari]** Scope the BeWhere European extension as a follow-on; identify the
   shared supply-curve interface and a target joint output (paper / proposal).

---

## 8. Open questions for IIASA

| # | Question | For |
|---|---|---|
| Q1 | Does G4M already run for Finland at a resolution usable for national supply curves, and can it output assortment-level harvest **and** net carbon/HWP flux per management scenario? | G4M team |
| Q2 | Can G4M provide **disturbance-driven** trajectories (beetle/wind/fire) for Finland, or must disturbance come from FLAM/PICUS outputs layered on G4M? | G4M / ForestNavigator |
| Q3 | Is the di Fulvio forest-management cost dataset resolved enough for Finland (south/central/north) to parameterise supply-curve cost steps? | F. di Fulvio |
| Q4 | How should disturbance-related mortality be treated in Finland's LULUCF / forest reference level — i.e. should calamity-wood carbon be charged to the coupled GHG budget? | G4M team / SYKE |
| Q5 | Are Schipfer and Tiwari interested in a BeWhere-based European/construction extension built on the same supply-curve object, and on what timeline? | Schipfer / Tiwari |

---

## References (indicative)

- Blattert, C. et al. (2022). Sectoral policies cause incoherence in forest management and ecosystem
  service provisioning. *Forest Policy and Economics* 136, 102689.
- Colla, M. et al. (2022). Optimal Use of Lignocellulosic Biomass in a Multi-Sector Energy System.
- Gusti, M. (2010). An algorithm for simulation of forest management decisions in the global forest
  model (G4M).
- Hlásny, T. et al. (2021). Devastating outbreak of bark beetles in the Czech Republic. *For. Ecol.
  Manage.* (`j.foreco.2021.119075`).
- Kärhä, K. et al. (2018). Salvage logging productivity and costs in windthrown Norway spruce. *Forests* 9(5), 280.
- Kindermann, G. et al. (2008). A global forest growing stock, biomass and carbon map based on FAO
  statistics (G4M basis).
- Krasovskiy, A. et al. (2025). ForestNavigator D3.4 — natural disturbances and extreme events impact
  on forest mitigation potential.
- Lauri, P., Forsell, N., di Fulvio, F. et al. — G4M applications in GLOBIOM/ForestNavigator.
- Leduc, S., Kraxner, F., Schipfer, F. et al. — BeWhere model and bioenergy/forest-industry siting.
- Mönkkönen, M. et al. (2024). Ecologically and economically sustainable level of timber harvesting
  in boreal forests. *bioRxiv* 2024.06.27.600997.
- Patacca, M. et al. (2023). Significant increase in natural disturbance impacts on European forests
  since 1950. *Global Change Biology* 29(5).
- Venäläinen, A. et al. (2020). Climate change induces multiple risks to boreal forests and forestry
  in Finland. *Global Change Biology* 26(8).

*Project literature base: `Docs/literature/forest_disturbance_timber_economics_report.md`;
scenario mapping: `Docs/biomass_scenario_mapping.md`; supply-curve design:
`Docs/biomass_supply_curve_fi.md`.*
