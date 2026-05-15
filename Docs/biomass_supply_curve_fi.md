# Biomass Wood Supply Curve for Finland 2035
## Design Document — EnergyScope FI Implementation

**Status**: Design complete; implementation in `Data/2035/` files.  
**Author**: derived from Colla et al. (2022) methodology, adapted for Finland.  
**Purpose**: Paper section justifying the stepped biomass supply curve replacing the single-price WOOD resource.

---

## 1. Colla et al. (2022) Methodology

### 1.1 Supply Curve Concept

Colla et al. (2022) — *"Optimal Use of Lignocellulosic Biomass in a Multi-Sector Energy System"* — disaggregates the single `WOOD` resource in EnergyScope into **10 origin-differentiated supply steps** (`WOOD1`–`WOOD10`), each representing a distinct biomass fraction with its own:
- **`avail`** (GWh/yr): techno-economic mobilisation potential from ENSPRESO
- **`c_op`** (€/kWh): marginal supply cost (collection + transport)
- **`gwp_op`** (ktCO₂/GWh): lifecycle GHG from harvesting/transport (not combustion)

The model then dispatches these steps in **merit order** (cheapest first), forming a step-wise supply curve. The WOOD layer's balance equation aggregates all steps:

$$\sum_{x=1}^{10} R_{t,\text{WOODx}}^{\text{local}} \cdot \underbrace{\text{layers\_in\_out}[\text{WOODx}, \text{WOOD}]}_{=1} \geq \sum_j F_{t,j} \cdot |\text{layers\_in\_out}[j, \text{WOOD}]|$$

The `WOOD1`–`WOOD10` resources are defined in the `BIOFUELS` set (= `NOT_LAYERS` in ESMC), meaning they **contribute to the WOOD layer balance** but do not generate their own layer balance equation.

### 1.2 Belgium Reference Data (from `0%_NED_constraints_naphtha_LFO_prices/ESTD_data.dat`)

| Resource | Avail (GWh) | c_op (€/kWh) | gwp_op (ktCO₂/GWh) | Description |
|----------|-------------|--------------|---------------------|-------------|
| WOOD3    | 11,037      | 0.01318      | 0.0144              | Black liquor / processing by-products (cheapest) |
| WOOD1    | 12,920      | 0.02220      | 0.0216              | Logging residues tier 1 |
| WOOD4    | 16,196      | 0.02562      | 0.0216              | Forest thinning |
| WOOD2    | 6,793       | 0.02939      | 0.0288              | Secondary residues |
| WOOD8    | 8,424       | 0.03126      | 0.0396              | Tertiary residues |
| WOOD9    | 4,125       | 0.03126      | 0.0468              | Fine residues |
| WOOD6    | 27,750      | 0.03599      | 0.0252              | Commercial forest harvest |
| WOOD5    | 8,380       | 0.03643      | 0.0360              | Landscape/energy crops |
| WOOD7    | 15,345      | 0.04233      | 0.0360              | High-cost residues |
| WOOD10   | 1,000,000   | 0.08147      | 0.0396              | Nordic imports (unlimited backstop) |

**Total domestic (WOOD1–9)**: ~110,970 GWh ≈ Belgium's ENSPRESO medium potential.

### 1.3 Sustainability Constraint (from `ESTD_model.mod`, lines 169–183)

Colla defines a qualitative split between lower-quality ("Low") and higher-quality ("High") wood to prevent over-reliance on wet, fine-particle by-products:

```ampl
var Low_wood >= 0;   # = sum(WOOD2+WOOD3+WOOD5+WOOD7+WOOD9)
var High_wood >= 0;  # = sum(WOOD1+WOOD4+WOOD6+WOOD8+WOOD10)
subject to low_to_high_limitation:
    Low_wood <= (0.4 / 0.6) * (18.7 / 20.1) * High_wood;
    # → Low_wood ≤ 0.621 × High_wood → low-quality ≤ 38.3% of total
```

The factor `(18.7/20.1) ≈ 0.930` converts between the lower heating values of wet vs. dry biomass (18.7 GJ/t for 50%-moisture residues vs. 20.1 GJ/t for drier wood).

### 1.4 Model Structure Differences: Colla vs. ESMC FI

| Feature | Colla (Belgium) | ESMC FI (Finland) |
|---------|----------------|------------------|
| NOT_LAYERS equivalent | `BIOFUELS` set | `NOT_LAYERS` parameter in `Misc_indep.json` |
| Resource→Layer link | `layers_in_out[WOODx, WOOD] = 1` | same mechanism |
| Regions | Single-region | Multi-region (`{c in REGIONS}`) |
| Sustainability constraint | `low_to_high_limitation` | see §4.2 (adaptation) |
| Data source | ENSPRESO Belgium | ENSPRESO Finland (ENS_Med 2035, interpolated) |

---

## 2. Finland Supply Curve Design

### 2.1 ENSPRESO Component Mapping

The total Finnish wood potential (WOOD = 110,806 GWh in ENS_Med 2050) decomposes exactly into **6 ENSPRESO energy-commodity codes**, grouped into **4 domestic supply steps** plus one **import backstop**:

| Step | Label | ENSPRESO codes | Physical description |
|------|-------|----------------|---------------------|
| WOOD_FI1 | Industrial by-products | `MINBIOWOOa` | Black liquor, bark, sawdust from pulp/paper/sawmill complexes |
| WOOD_FI2 | Logging residues | `MINBIOFRSR1` | Branches, tops, stumps left after commercial timber harvest |
| WOOD_FI3 | Secondary wood products | `MINBIOWOOW1` + `MINBIOWOOW1a` | Woodchips and sawdust from secondary wood processing |
| WOOD_FI4 | Direct fuelwood + landscape | `MINBIOWOO` + `MINBIOFRSR1a` | Roundwood cut for energy use; roadside/landscape care residues |
| WOOD_FI5 | Baltic/Nordic imports | Market (Baltic pellets, SE/EE chips) | High-cost import backstop — unlimited in principle |

### 2.2 Scenario-Specific Availability (GWh/yr)

Derived directly from ENSPRESO database (`ENSPRESO_BIOMASS.xlsx`, sheet `ENER - NUTS0 EnergyCom`):

| Step | S2/NFS (ENS_Med 2035) | S3/BDS (ENS_Low 2030) | S1/BES (ENS_Med 2035 × 1.20) |
|------|----------------------|----------------------|------------------------------|
| WOOD_FI1 | 45,442 | 43,188 | 54,530 |
| WOOD_FI2 | 38,214 | 20,690 | 45,857 |
| WOOD_FI3 | 12,543 | 6,272  | 15,052 |
| WOOD_FI4 | 5,420  | 4,071  | 6,504  |
| **Domestic total** | **101,619** | **74,221** | **121,943** |
| WOOD_FI5 | 1,000,000 | 1,000,000 | 1,000,000 |

**Consistency check**:
- S2/NFS domestic = 101,619 GWh (ENS_Med 2035 interpolated; see §2.5 for methodology) ✓
- S3/BDS domestic = 74,221 GWh (ENS_Low 2030, no interpolation needed) ✓
- S1/BES domestic = 121,943 GWh (ENS_Med 2035 × 1.20) ✓

> **S1/BES note**: The ENS_High scenarios for Finland are physically implausible (MINBIOFRSR1 > 120,000 GWh, >3× current harvest) due to an aggregation artefact in the ENSPRESO database. S1/BES is instead constructed as a **+20% uniform scale-up** of ENS_Med 2035, representing the maximum ecologically defensible mobilisation under a "best-effort" forest management scenario. This is a stylised approximation and is disclosed as such in the paper.

### 2.3 Cost Parameters

Cost estimates based on Finnish market data (Finnish Energy Industry, Luke, IEA 2022):

| Step | c_op_local (€/kWh) | Basis |
|------|-------------------|-------|
| WOOD_FI1 | **0.011** | Industrial by-products: handling only (bark ~10–15 €/MWh at mill gate; black liquor self-consumed at near-zero marginal cost) |
| WOOD_FI2 | **0.022** | Logging chips: collection + chipping + transport (~20–25 €/MWh, matches current calibrated flat price) |
| WOOD_FI3 | **0.027** | Secondary woodchips from processing: slightly higher mobilisation cost (~25–30 €/MWh) |
| WOOD_FI4 | **0.033** | Direct fuelwood (roundwood for energy) + landscape care: higher collection effort (~30–35 €/MWh) |
| WOOD_FI5 | **0.070** | Baltic wood pellets / Swedish chips imports: spot market 60–80 €/MWh (2022) + transport |

**Weighted average check (S2/NFS)**:

$$\bar{c}_{op} = \frac{45442 \times 0.011 + 38214 \times 0.022 + 12543 \times 0.027 + 5420 \times 0.033}{101619} \approx 0.0183 \text{ €/kWh}$$

This is lower than the previous flat price of 0.02208 €/kWh, reflecting the large share of cheap industrial by-products (WOOD_FI1 = 44.7% of total domestic supply in ENS_Med 2035). Compared to the earlier ENS_Med 2050 calculation (0.0178 €/kWh), the weighted average is slightly higher because WOOD_FI1's share shrank from 48.5% to 44.7% (MINBIOWOOa grows more slowly between 2030–2035 than 2035–2050). The supply curve still gives the model access to WOOD_FI1 at 11 €/MWh (well below the previous calibrated flat price) and WOOD_FI2 at 22 €/MWh (equal to previous calibration).

### 2.4 GHG Emission Factors

Lifecycle GHG from supply (harvesting + transport, excluding combustion CO₂ which is considered carbon-neutral):

| Step | gwp_op_local (ktCO₂/GWh) | Basis |
|------|--------------------------|-------|
| WOOD_FI1 | 0.020 | Very short transport (on-site by-products); lower than WOOD average |
| WOOD_FI2 | 0.022 | Medium-distance truck transport from logging sites (~50 km average) |
| WOOD_FI3 | 0.024 | Secondary processing step + transport |
| WOOD_FI4 | 0.026 | Collection from dispersed sites; slightly higher fuel use |
| WOOD_FI5 | 0.040 | Maritime + inland transport from Baltic; comparable to Colla WOOD10 |

Reference: current WOOD gwp_op_local in `02_REF_REGION/Resources.csv` = 0.02456 ktCO₂/GWh (intermediate between WOOD_FI2 and WOOD_FI3 — consistent).

### 2.5 ENSPRESO Time-Horizon Choice and Interpolation Methodology

The ENSPRESO database provides potentials for Finland at years **2010, 2020, 2030, 2040, and 2050**. There is no native 2035 data point. For consistency with the modelled year (2035), the **ENS_Med 2035 values are obtained by linear interpolation** between ENS_Med 2030 and ENS_Med 2040:

$$X_{2035} = \frac{X_{2030} + X_{2040}}{2}$$

This is exact since 2035 is the midpoint. The interpolation was applied per ENSPRESO energy-commodity code before aggregation into supply steps:

| Code | ENS_Med 2030 (GWh) | ENS_Med 2040 (GWh) | ENS_Med 2035 (GWh) |
|------|-------------------|--------------------|--------------------|
| MINBIOWOOa | 45,952 | 44,933 | **45,442** |
| MINBIOFRSR1 | 41,380 | 35,047 | **38,214** |
| MINBIOWOOW1+a | 12,543 | 12,543 | **12,543** |
| MINBIOWOO+FRSR1a | 5,454 | 5,386 | **5,420** |
| **Total domestic** | **105,329** | **97,909** | **101,619** |

For S3/BDS, ENS_Low **2030** is used directly (no interpolation). The 2030 timestamp is appropriate for BDS because it represents a scenario where biodiversity constraints are already binding in the near term, forestry mobilisation infrastructure develops more slowly, and harvest intensity is lower.

### 2.6 BDS Supply Curve Shape: Why It Differs from NFS and BES

The BDS (Biodiversity) curve has a distinctly different shape from NFS and BES — visually "bimodal" rather than progressive. Three compounding factors explain this:

**Factor 1 — WOOD_FI2 (logging residues, MINBIOFRSR1) is radically smaller in BDS**: 20,690 GWh vs 38,214 GWh in NFS (only 54%). `MINBIOFRSR1` is the ENSPRESO code most sensitive to biodiversity constraints. Under ENS_Low scenarios, EU RED II and Finland's national forest law require leaving large fractions of branches, tops, and stumps in the forest to maintain soil carbon stocks, deadwood habitat, and saproxylic species diversity. In ENS_Med/High scenarios, most logging residues are assumed harvestable.

**Factor 2 — WOOD_FI2 costs more in BDS**: c_op = 26 €/MWh vs 22 €/MWh for NFS/BES. When ecological constraints exclude the most accessible (low-cost) residue fractions, only remote or dispersed residues remain — raising the marginal collection and transport cost.

**Factor 3 — Earlier time horizon (2030 vs 2035)**: Less accumulated harvesting infrastructure. All steps are smaller, but WOOD_FI2 is most affected because residue collection capacity is particularly sensitive to the degree of forest mechanisation at a given time.

**Net result**: BDS has a wide flat Step 1 (~43 TWh at 11 €/MWh), followed by only ~31 TWh of affordable domestic supply (Steps 2–4), before the backstop at 70 €/MWh is reached at 74 TWh. The system has very little affordable middle ground — it either uses cheap by-products or imports. NFS/BES by contrast have a more gradual cost ramp through ~56–68 TWh of mid-price steps.

### 2.7 Figure Color Convention

The supply curve figure (`plots/biomass_supply_curves_fi_2035.png`) uses the following color scheme, chosen to convey ecological intensity:

| Scenario | Color | Rationale |
|----------|-------|-----------|
| S3-BDS (Biodiversity) | **Green** (#27ae60) | Nature conservation — most restrictive, forest protection |
| S2-NFS (Neutral Forest) | **Grey** (#7f8c8d) | Neutral baseline — no strong ecological or economic bias |
| S1-BES (Bioeconomy) | **Red** (#c0392b) | Most intensive harvest — maximum economic mobilisation |

---

## 3. EnergyScope FI Implementation

### 3.1 Files Modified

The supply curve implementation requires changes to **6 files** in `Data/2035/`:

| File | Change |
|------|--------|
| `00_INDEP/Resources_indep.csv` | Add 5 rows (WOOD_FI1–5) with Category='Renewable', Subcategory='Biomass' |
| `00_INDEP/Layers_in_out.csv` | Add 5 rows with `layers_in_out[WOOD_FIx, WOOD] = 1.0` |
| `00_INDEP/Misc_indep.json` | Add WOOD_FI1–5 to `NOT_LAYERS` list |
| `02_REF_REGION/Resources.csv` | Add 5 rows with default avail_local=0, scenario-specific gwp/c_op |
| `FI/Resources.csv` | Replace WOOD (avail=110,806) with WOOD=0 + WOOD_FI1–4 + WOOD_FI5 |
| `FI/Resources_S1_BES.csv` / `_S2_NFS.csv` / `_S3_BDS.csv` | Same substitution with scenario-specific avail_local |

**`ESMC_model_AMPL.mod`** does **not** require changes for the basic supply curve (the `layer_balance` constraint automatically handles new NOT_LAYERS resources). The optional sustainability constraint (§3.3) would require AMPL modifications.

### 3.2 Mechanism in ESMC (No AMPL Changes Required)

The key insight from the `layer_balance` constraint in `ESMC_model_AMPL.mod` (line ~370):

```ampl
subject to layer_balance {c in REGIONS, l in LAYERS, h in HOURS, td in TYPICAL_DAYS}:
    sum {i in RESOURCES} (layers_in_out[i, l] * (R_t_local[c,i,h,td] + ...))
    + sum {k in TECHNOLOGIES diff STORAGE_TECH} (layers_in_out[k,l] * F_t[c,k,h,td])
    + ...
    = 0;
```

The sum over `i in RESOURCES` includes ALL resources, including those in `NOT_LAYERS`. So when WOOD_FI1–4 are added to `NOT_LAYERS` with `layers_in_out[WOOD_FIx, WOOD] = 1`:
- WOOD_FI1–4 contribute to the **WOOD layer balance equation** (l = WOOD)
- Each has its own `resource_availability_local` constraint limiting annual consumption
- The optimizer dispatches them in merit order (cheapest first, WOOD_FI1 at 11 €/MWh first)
- Setting `avail_local[WOOD] = 0` prevents direct generic WOOD import

This is identical to the Colla BIOFUELS mechanism — no AMPL model changes needed.

### 3.3 Optional Sustainability Constraint (Future Work)

Analogous to Colla's `low_to_high_limitation`, a Finland-specific constraint could limit over-reliance on industrial by-products and imports:

```ampl
# Sustainability constraint for Finnish wood supply (adapted from Colla 2022)
# "High quality" = logging residues + fuelwood (managed forest origin)
# "Low quality"  = industrial by-products + secondary chips + imports
var Low_wood_FI {c in REGIONS} >= 0;
var High_wood_FI {c in REGIONS} >= 0;

subject to def_low_wood_FI {c in REGIONS}:
    Low_wood_FI[c] = sum {t,h,td} (
        (R_t_local[c,'WOOD_FI1',h,td] + R_t_local[c,'WOOD_FI3',h,td]
         + R_t_local[c,'WOOD_FI5',h,td]) * t_op[h,td]);

subject to def_high_wood_FI {c in REGIONS}:
    High_wood_FI[c] = sum {t,h,td} (
        (R_t_local[c,'WOOD_FI2',h,td] + R_t_local[c,'WOOD_FI4',h,td])
        * t_op[h,td]);

subject to wood_sustainability_FI {c in REGIONS}:
    Low_wood_FI[c] <= (0.4 / 0.6) * High_wood_FI[c];
    # → Low_wood ≤ 66.7% of High_wood → by-products ≤ 40% of total
```

**Note**: This constraint is not implemented in the current version. It would be most meaningful for sensitivity analysis of industrial wood availability shocks (e.g., pulp sector contraction under S3/BDS).

---

## 4. Scenario Parameterisation Summary

Full table with all parameters per scenario per step:

### S2/NFS — Neutral Forest Scenario (ENS_Med 2035, interpolated)

| Resource | avail_local (GWh) | c_op_local (€/kWh) | gwp_op_local (ktCO₂/GWh) |
|----------|------------------|---------------------|---------------------------|
| WOOD     | 0                | 0.000               | 0.025 |
| WOOD_FI1 | 45,442           | 0.011               | 0.020 |
| WOOD_FI2 | 38,214           | 0.022               | 0.022 |
| WOOD_FI3 | 12,543           | 0.027               | 0.024 |
| WOOD_FI4 | 5,420            | 0.033               | 0.026 |
| WOOD_FI5 | 1,000,000        | 0.070               | 0.040 |

### S3/BDS — Biodiversity-Driven Scenario (ENS_Low 2030)

| Resource | avail_local (GWh) | c_op_local (€/kWh) | gwp_op_local (ktCO₂/GWh) |
|----------|------------------|---------------------|--------------------------|
| WOOD     | 0                | 0.000               | 0.025 |
| WOOD_FI1 | 43,188           | 0.011               | 0.020 |
| WOOD_FI2 | 20,690           | 0.026               | 0.022 |
| WOOD_FI3 | 6,272            | 0.027               | 0.024 |
| WOOD_FI4 | 4,071            | 0.033               | 0.026 |
| WOOD_FI5 | 1,000,000        | 0.070               | 0.040 |

> **Note on WOOD_FI2 cost in S3/BDS**: The c_op is increased from 0.022 to 0.026 €/kWh to reflect that the BDS constraint on harvest intensity forces collection of more dispersed/remote residues (the accessible low-cost fraction is smaller under stricter ecological constraints).

### S1/BES — Bioeconomy Scenario (ENS_Med 2035 × 1.20, stylised)

| Resource | avail_local (GWh) | c_op_local (€/kWh) | gwp_op_local (ktCO₂/GWh) |
|----------|------------------|---------------------|---------------------------|
| WOOD     | 0                | 0.000               | 0.025 |
| WOOD_FI1 | 54,530           | 0.011               | 0.020 |
| WOOD_FI2 | 45,857           | 0.022               | 0.022 |
| WOOD_FI3 | 15,052           | 0.027               | 0.024 |
| WOOD_FI4 | 6,504            | 0.033               | 0.026 |
| WOOD_FI5 | 1,000,000        | 0.070               | 0.040 |

---

## 5. ENSPRESO Component Glossary

| Code | Description | Model step |
|------|-------------|------------|
| `MINBIOWOOa` | Industrial wood residues from primary processing (black liquor, bark, sawdust) | WOOD_FI1 |
| `MINBIOFRSR1` | Forest sector residues tier 1 (logging residues: branches, tops, stumps) | WOOD_FI2 |
| `MINBIOWOOW1` | Wood waste from wood processing industry (coarse chips) | WOOD_FI3 (part 1) |
| `MINBIOWOOW1a` | Wood waste from wood processing industry (sawdust, shavings) | WOOD_FI3 (part 2) |
| `MINBIOWOO` | Energy fuelwood (roundwood harvested primarily for energy) | WOOD_FI4 (part 1) |
| `MINBIOFRSR1a` | Forest sector residues from landscape care (roadside, urban trees) | WOOD_FI4 (part 2) |

---

## 6. References

- Colla, M., Larrea-Gallegos, G., Maréchal, F., & Dewulf, J. (2022). Optimal Use of Lignocellulosic Biomass in a Multi-Sector Energy System. *Energy*.
- ENSPRESO database: `Data/exogenous_data/ENSPRESO/ENSPRESO_BIOMASS.xlsx`
- Finnish Energy Industry (Energiateollisuus): Wood chip and biomass price statistics 2022.
- IEA Bioenergy (2023): Wood pellet import price Baltic/Nordic corridor.
- `Docs/biomass_scenario_mapping.md`: Full scenario-mapping justification with Blattert and Mönkkönen cross-validation.
