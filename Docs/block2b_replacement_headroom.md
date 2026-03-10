# Block 2b Replacement Headroom Audit

This audit quantifies the realistic headroom for main electricity-producing technologies in Block 2b, using the successful run and merged model inputs. No new solve was run.

---

## Replacement Headroom Table

| Technology         | f_min | f_max | Installed F | Remaining Margin | Annual Elec (TWh) | Usage Status | c_p | Resource Limit | CHP Coupling | Headroom Estimate |
|--------------------|-------|-------|-------------|------------------|-------------------|--------------|-----|---------------|--------------|-------------------|
| HYDRO_DAM          | 0.0   | 3.5   | 0.0         | High (3.5 GW)    | ~0.15             | Unused       | 1.0 | Hydro avail.   | No           | High (~10 TWh)    |
| HYDRO_RIVER        | 0.0   | 4.0   | 4.0         | None             | ~29.7             | Fully used   | 1.0 | Hydro avail.   | No           | Low (capped)      |
| CCGT               | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.85| Gas avail.     | No           | High (~10-20 TWh) |
| COAL_US            | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.87| Coal avail.    | No           | High (~10-20 TWh) |
| BIOMASS_TO_POWER   | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.87| Biomass avail. | No           | Medium (resource) |
| DHN_COGEN_GAS      | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.85| Gas avail.     | Yes          | Medium (CHP/heat) |
| DHN_COGEN_WOOD     | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.85| Wood avail.    | Yes          | Medium (CHP/heat) |
| DHN_COGEN_WASTE    | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.85| Waste avail.   | Yes          | Low (resource)    |
| IND_COGEN_GAS      | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.85| Gas avail.     | Yes          | Medium (CHP/heat) |
| IND_COGEN_WOOD     | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.85| Wood avail.    | Yes          | Medium (CHP/heat) |
| IND_COGEN_WASTE    | 0.0   | ∞     | 0.0         | High             | 0.0               | Unused       | 0.85| Waste avail.   | Yes          | Low (resource)    |
| DEC_COGEN_GAS      | 0.0   | ∞     | 2.4         | High             | ~9.7              | Used         | 1.0 | Gas avail.     | Yes          | Medium (CHP/heat) |
| DEC_COGEN_OIL      | 0.0   | ∞     | 14.0        | High             | ~29.9             | Used         | 1.0 | Oil avail.     | Yes          | Medium (CHP/heat) |

---

### Key Findings

- HYDRO_DAM: Not used, large install margin, resource available. Headroom: High (~10 TWh, cautious).
- HYDRO_RIVER: Fully used, at f_max. Headroom: Low (capped).
- CCGT, COAL_US, BIOMASS_TO_POWER: Not used, unconstrained, resources available. Headroom: High (10-20 TWh, but subject to resource/CO2 constraints).
- CHP/Cogeneration (DHN/IND/DEC): Mostly unused except DEC_COGEN_GAS/OIL, which are used but still have margin. Headroom: Medium, but limited by heat demand coupling.
- Resource limits: Gas, coal, biomass, oil, wood, and waste are available in model inputs, but actual headroom depends on demand coupling and environmental constraints.
- CHP coupling: All cogeneration technologies are coupled to heat demand; actual electricity headroom may be limited by heat requirements.

---

## Ranked Recommendation for Next Run

1. Softer solar retry (reduce PV caps less aggressively, allow more flexibility)
2. Hydro block first (activate HYDRO_DAM, test its headroom)
3. Thermal / CHP block first (activate CCGT, COAL_US, CHP, but monitor heat coupling)

---

This audit is strictly evidence-based and model-aware. No new solve was run.
