# Disabled Technologies Audit — Finland 2017

**Created**: 2026-03-11  
**Purpose**: Inventory of all technologies disabled or constrained at each layer, with justification analysis.

---

## Layer Architecture

Technologies are constrained at three levels, applied in order:

1. **REF_REGION** (`Data/2017/02_REF_REGION/Technologies.csv`) — Universal defaults. Most techs: f_min=0, f_max=1e15.
2. **FI override** (`Data/2017/FI/Technologies.csv`) — Country-specific overrides via `pandas.update()`.
3. **run_calib_manual.py** — NO in-memory disabling logic found (confirmed by code audit).

---

## A. Technologies Disabled at REF_REGION Level (f_max=0)

These are globally disabled — cannot be enabled by FI override alone.

| Technology | f_min | f_max | Justification |
|---|---|---|---|
| NUCLEAR | 0 | 0 | Default for countries without nuclear; FI **must** override |
| NUCLEAR_SMR | 0 | 0 | Not available in 2017 timeframe |
| PLANE_H2_SHORT_HAUL | 0 | 0 | Future technology, not available in 2017 |
| DEC_THHP_GAS_COLD | 0 | 0 | Cooling technology, marginal in Finland climate |

**Impact**: NUCLEAR must be overridden to non-zero in FI/Technologies.csv for Finland. All others are correctly disabled for 2017.

---

## B. Technologies Disabled in Current FI/Technologies.csv (f_max=0)

Current file (block3c state, 20 rows):

| Technology | f_min | f_max | Also disabled in REF? | Justified for FI 2017? |
|---|---|---|---|---|
| PT_POWER_BLOCK | 0 | 0 | No | **Yes** — no parabolic trough CSP in Finland |
| ST_POWER_BLOCK | 0 | 0 | No | **Yes** — no solar tower CSP in Finland |
| PT_COLLECTOR | 0 | 0 | No | **Yes** — CSP collector, not applicable |
| ST_COLLECTOR | 0 | 0 | No | **Yes** — CSP collector, not applicable |
| WIND_OFFSHORE | 0 | 0 | No | **Debatable** — FI had 0 GW in 2017, but some capacity was planned. Disable is defensible for historical calibration. |
| TIDAL_STREAM | 0 | 0 | No | **Yes** — no tidal energy in Finland |
| TIDAL_RANGE | 0 | 0 | No | **Yes** — no tidal energy in Finland |
| WAVE | 0 | 0 | No | **Yes** — no wave energy in Finland |
| DHN_DEEP_GEO | 0 | 0 | No | **Yes** — no deep geothermal DHN in 2017 Finland |

**All 9 disablings are justified** for a 2017 historical calibration.

---

## C. Technologies Constrained (non-default) in Current FI/Technologies.csv

| Technology | f_min | f_max | v10 reference | Reality 2017 | Assessment |
|---|---|---|---|---|---|
| NUCLEAR | 2.7 | 2.835 | 2.5 / 2.8 | 2.764 | Current f_min=2.7 very tight. v10 used 2.5. |
| PV_ROOFTOP | 0 | 4 | 0.02 / 2.0 | ~0.02 | Current f_max=4 is block3c residue. v10 used 0.02/2.0. |
| PV_UTILITY | 0 | 15 | 0.0 / 1.0 | ~0.02 | Current f_max=15 is block3c residue. v10 used 0/1.0. |
| WIND_ONSHORE | 2 | 2.1 | 2.0 / 2.1 | 2.04 | **Matches v10**. Tight and correct. |
| HYDRO_DAM | 0 | 3.5 | 1.1 / 1.3 | ~1.2 | Current has no f_min. v10 had f_min=1.1. |
| HYDRO_RIVER | 0 | 4 | 1.9 / 2.1 | ~2.0 | Current has no f_min. v10 had f_min=1.9. |
| GEOTHERMAL | 0 | 0.3 | 0 / 0.3 | ~0 | **Matches v10**. |
| DHN_SOLAR | 0 | 60 | (not in v10) | small | Wide open, harmless. |
| DEC_SOLAR | 0 | 60 | (not in v10) | small | Wide open, harmless. |
| DAM_STORAGE | 0 | 0.1 | (not in v10) | small | Reasonable cap. |
| PHS | 0 | 0.1 | (not in v10) | small | Reasonable cap. |

---

## D. Key Technologies Missing from Current FI Override (using REF defaults = unconstrained)

These technologies are NOT in the current FI/Technologies.csv, so they inherit REF_REGION defaults (f_min=0, f_max=1e15).

**v10 had explicit FI overrides for these — they are MISSING and should be added:**

| Technology | REF default | v10 override | Reality 2017 | Priority |
|---|---|---|---|---|
| CCGT | 0 / 1e15 | 0.6 / 1.5 | ~0.9 | **CRITICAL** — without constraint, model may over/under-invest |
| COAL_US | 0 / 1e15 | 3.5 / 4.5 | ~3.8 | **CRITICAL** — Finland's coal backbone |
| DHN_COGEN_GAS | 0 / 1e15 | 0.6 / 1.5 | ~0.8 | **HIGH** — gas CHP |
| DHN_BOILER_OIL | 0 / 1e15 | 0.4 / 1.0 | ~0.5 | **HIGH** — oil heating |
| IND_BOILER_OIL | 0 / 1e15 | 0.2 / 1.0 | ~0.3 | **HIGH** — industrial oil |
| DHN_COGEN_WOOD | 0 / 1e15 | (bak: 2.5/15) | ~3 | **MEDIUM** — biomass CHP |
| DHN_COGEN_COAL | 0 / 1e15 | (bak: 0.5/10) | ~1.5 | **MEDIUM** — coal CHP |
| IND_BOILER_WOOD | 0 / 1e15 | (bak: 5/20) | ~7 | **MEDIUM** — industrial biomass |
| IND_COGEN_COAL | 0 / 1e15 | (bak: 0/5) | ~1 | **LOW** — small coal CHP |

---

## E. Technologies Disabled in v10-era Backup (bak_20260308) but Not in Current FI File

The v10-era 4-column backup disabled 13 technologies. 4 of those are also disabled in the current file. Additional disablings in that backup:

| Technology | Status in bak | In current FI? | Should disable for 2017? |
|---|---|---|---|
| BUS_COACH_FC_HYBRIDH2 | 0/0 | No | Yes — no hydrogen buses in 2017 FI |
| CAR_FUEL_CELL | 0/0 | No | Yes — no fuel cell cars in 2017 FI |
| CAR_METHANOL | 0/0 | No | Yes — no methanol cars in 2017 FI |
| TRUCK_ELEC | 0/0 | No | Yes — no electric trucks in 2017 FI |
| TRUCK_FUEL_CELL | 0/0 | No | Yes — no hydrogen trucks in 2017 FI |

These are future transport technologies. Not disabling them allows the optimizer to potentially invest in them, distorting the 2017 result.

---

## F. Recommendations for Restart

### Immediate (restore to v10-like state):
1. Add CCGT, COAL_US, DHN_COGEN_GAS, DHN_BOILER_OIL, IND_BOILER_OIL with v10-era f_min/f_max
2. Tighten HYDRO_DAM (add f_min=1.1) and HYDRO_RIVER (add f_min=1.9)
3. Adjust PV_ROOFTOP to 0.02/2.0 and PV_UTILITY to 0/1.0 (v10 values)
4. Relax NUCLEAR f_min from 2.7 to 2.5 (v10 value)

### Consider adding:
5. Disable future transport: BUS_COACH_FC_HYBRIDH2, CAR_FUEL_CELL, CAR_METHANOL, TRUCK_ELEC, TRUCK_FUEL_CELL
6. Add DHN_COGEN_WOOD, DHN_COGEN_COAL, IND_BOILER_WOOD with moderate ranges

### Keep as-is:
7. All CSP/tidal/wave/DHN_DEEP_GEO disablings (correctly disabled)
8. WIND_ONSHORE 2.0/2.1 (correct)
9. GEOTHERMAL 0/0.3 (correct)
