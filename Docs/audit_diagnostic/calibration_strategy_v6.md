# Calibration Strategy: Finland 2017 → Next Iteration (v6)

**Date:** 2025-02-27  
**Baseline:** v5_fperc restored inputs in `Data/2017/FI/`  
**Target:** Match Finland 2017 energy statistics  
**Levers:** `f_min`, `f_max`, `fmin_perc`, `fmax_perc`, `avail_local`, `avail_exterior`

---

## 1. How the Model Works (Key Mechanics)

### 1.1 What the Optimizer Does

ESMC minimizes **total system cost** $\sum_c \text{TotalCost}[c]$, where:

$$\text{TotalCost} = \sum_j \bigl(\tau_j \cdot c_{\text{inv},j} \cdot F_j + c_{\text{maint},j} \cdot F_j\bigr) + \sum_i C_{\text{op},i}$$

- **$F_j$** = installed capacity of technology $j$ [GW]
- **$\tau_j$** = annualization factor (function of `lifetime` and `i_rate`)
- **$C_{\text{op},i}$** = yearly resource cost = $\sum_t \bigl(c_{\text{op,local}} \cdot R_{t,\text{local}} + c_{\text{op,ext}} \cdot R_{t,\text{ext}}\bigr) \cdot t_{\text{op}}$

The model must **satisfy all end-use demands** (electricity, heat, mobility, shipping, cooling, non-energy) while respecting hourly dispatch, resource availability, and technology capacity constraints.

### 1.2 The Six Calibration Levers

| Lever | AMPL Parameter | What It Controls | Constraint |
|-------|---------------|------------------|------------|
| **f_min** | `f_min[c,j]` | Minimum installed capacity [GW] | $f_{\min} \le F_j \le f_{\max}$ (Eq. 9) |
| **f_max** | `f_max[c,j]` | Maximum installed capacity [GW] | Same as above |
| **fmin_perc** | `fmin_perc[c,j]` | Min market share [0–1] of sector output | $\sum_t F_{t,j} \ge$ `fmin_perc` $\times$ sector total (Eq. 38) |
| **fmax_perc** | `fmax_perc[c,j]` | Max market share [0–1] of sector output | $\sum_t F_{t,j} \le$ `fmax_perc` $\times$ sector total (Eq. 38) |
| **avail_local** | `avail_local[c,i]` | Max yearly local resource [GWh/y] | $\sum_t R_{t,\text{local}} \cdot t_{\text{op}} \le$ `avail_local` |
| **avail_exterior** | `avail_exterior[c,i]` | Max yearly import from outside [GWh/y] | $\sum_t R_{t,\text{ext}} \cdot t_{\text{op}} \le$ `avail_exterior` |

**Important:** `fmin_perc`/`fmax_perc` are only active when `f_perc=True` in the run config. With `f_perc=True`, the general constraints apply to **all** technologies in **all** end-use sectors (electricity, heat, mobility, etc.).

### 1.3 Sector Membership

The `fmin_perc`/`fmax_perc` constraints compare a technology's yearly output against the **total output of its end-use sector**. The sector is determined by `TECHNOLOGIES_OF_END_USES_TYPE[eut]`:

| Sector (end-use type) | Technologies |
|----------------------|--------------|
| ELECTRICITY | NUCLEAR, CCGT, CCGT_AMMONIA, COAL_US, COAL_IGCC, PV_ROOFTOP, PV_UTILITY, WIND_ONSHORE, WIND_OFFSHORE, HYDRO_DAM, HYDRO_RIVER, GEOTHERMAL, BIOMASS_TO_POWER, … |
| HEAT_HIGH_T | IND_COGEN_*, IND_BOILER_*, IND_DIRECT_ELEC |
| HEAT_LOW_T_DHN | DHN_COGEN_*, DHN_BOILER_*, DHN_HP_ELEC, DHN_DEEP_GEO, … |
| HEAT_LOW_T_DECEN | DEC_COGEN_*, DEC_BOILER_*, DEC_HP_ELEC, DEC_DIRECT_ELEC, DEC_SOLAR |
| MOB_PRIVATE | CAR_GASOLINE, CAR_DIESEL, CAR_NG, CAR_BEV, CAR_HEV, CAR_PHEV, CAR_FUEL_CELL, CAR_METHANOL |
| MOB_FREIGHT_ROAD | TRUCK_DIESEL, TRUCK_NG, TRUCK_ELEC, TRUCK_FUEL_CELL, TRUCK_METHANOL |
| MOB_FREIGHT_BOAT | BOAT_FREIGHT_* |
| SHIPPING | CARGO_* |
| MOB_PUBLIC | TRAMWAY_TROLLEY, BUS_COACH_*, TRAIN_PUB |
| AVIATION_SHORT_HAUL | PLANE_SHORT_HAUL, PLANE_H2_SHORT_HAUL |

### 1.4 Key Efficiencies (layers_in_out)

| Technology | Input → Output | Efficiency |
|-----------|---------------|------------|
| NUCLEAR | URANIUM → ELEC | 37.0% (1/2.7027) |
| CCGT | GAS → ELEC | 63.0% (1/1.5873) |
| COAL_US | COAL → ELEC | 49.0% (1/2.0408) |
| IND_BOILER_WOOD | WOOD → HEAT_HIGH_T | 86.4% (1/1.1568) |
| IND_COGEN_WOOD | WOOD → HEAT_HIGH_T + 0.34×ELEC | 53.0% thermal + 18.0% elec |
| DHN_COGEN_WOOD | WOOD → HEAT_LOW_T_DHN + 0.34×ELEC | 53.0% thermal + 18.0% elec |
| DEC_BOILER_WOOD | WOOD → HEAT_LOW_T_DECEN | 85.0% (1/1.1765) |
| DEC_HP_ELEC | ELEC → HEAT_LOW_T_DECEN | COP 3.0 (1/0.3333) |
| DHN_HP_ELEC | ELEC → HEAT_LOW_T_DHN | COP 4.0 (1/0.25) |
| CARGO_LFO | LFO → SHIPPING | 4.6% (1/0.0217) — very low efficiency per GW |

---

## 2. Gap Analysis: v5_fperc Rerun vs Reality

### 2.1 Primary Energy (TWh)

| Category | Model | Reality | Gap | Root Cause |
|----------|-------|---------|-----|------------|
| **WOOD** | 11 | **105** | −90% | Model has 110,806 GWh local wood available but only uses 6,319 → optimizer chooses cheaper fossil alternatives |
| **OIL** | 206 | **96** | +114% | LFO `avail_exterior`=150,000 GWh is the main sink (shipping CARGO_LFO consumes ~149k GWh). Also DIESEL/GASOLINE/JET_FUEL |
| **NUCLEAR** | 127 | **65** | +96% | NUCLEAR deploys at 5.68 GW despite `f_max`=2.8 (constraint violation due to solver degeneracy). Even at 2.8 GW: 2.8 × 0.849 × 8.76 = 20.8 TWh elec × 2.7 = 56 TWh thermal input ≈ OK |
| **COAL_PEAT** | 24 | **50** | −52% | COAL_US at 5.38 GW, but insufficient coal heating technology deployment |
| **GAS** | 28 | **25** | +12% | ≈ **OK**. Near `avail_exterior` cap of 28,000 GWh |
| **HYDRO** | 15.3 | **15** | +2% | ✅ **Excellent match** |
| **WIND** | 7.2 | **5** | +44% | Slightly high. WIND_ONSHORE at 2.67 GW vs `f_max`=2.1 (another constraint violation) |

### 2.2 Electricity (TWh)

| Source | Model | Reality | Gap | Root Cause |
|--------|-------|---------|-----|------------|
| Nuclear | 47.1 | **21.6** | +118% | Constraint violation: F=5.68 vs f_max=2.8 |
| Hydro | 15.3 | **14.6** | +5% | ✅ Excellent |
| Biomass | 0.2 | **11.0** | −98% | Wood/biomass CHP barely used for electricity. IND_COGEN_WOOD and DHN_COGEN_WOOD exist but produce mostly heat |
| Coal | 3.1 | **9.0** | −66% | COAL_US produces some, but coal CHP (IND_COGEN_COAL, DHN_COGEN_COAL) contribute little |
| Wind | 7.2 | **4.8** | +50% | Constraint violation on WIND_ONSHORE cap |
| Gas | 5.9 | **3.7** | +59% | CCGT + DHN_COGEN_GAS produce more than needed |
| Solar | 2.7 | **0.1** | ×27 | PV_ROOFTOP at 2.0 GW (near f_max=2.0) + PV_UTILITY at 1.0 GW. Way too much for 2017 Finland |

### 2.3 CO2 Emissions

| | Model | Reality |
|---|-------|---------|
| MtCO2 | 80.9 | **42** |

Model overshoots by 2× primarily because OIL consumption is 2× reality.

### 2.4 Root Cause: The Degeneracy Problem

**120 technologies** have `f_max = 1e15` with no FI override. This creates:
1. **Solver numerical instability**: The LP has variables spanning 15 orders of magnitude, causing the barrier method to converge poorly. This explains why `f_max = 2.8` for NUCLEAR is violated (F = 5.68).
2. **Degenerate cost surface**: Many equivalent-cost solutions exist, making the solution non-unique and sensitive to solver parameters.
3. **Absurd capacity deployment**: 129 technologies deploy at >100 GW, with shipping/infrastructure techs at 10¹⁰–10¹¹ GW.

---

## 3. Calibration Strategy

### Priority 0: Fix Degeneracy (CRITICAL — Do This First)

**Problem:** 120 technologies with `f_max = 1e15` make the LP ill-conditioned.

**Action:** Set `f_max = 0` for all technologies that did not exist in Finland 2017. Set realistic `f_max` for the rest.

Technologies to disable (`f_max = 0`):

```
# Future/non-existent in Finland 2017
CCGT_AMMONIA, COAL_IGCC, BIOMASS_TO_POWER
DEC_ADVCOGEN_GAS, DEC_ADVCOGEN_H2, DEC_THHP_GAS
BUS_COACH_FC_HYBRIDH2 (already 0), CAR_FUEL_CELL (already 0), CAR_METHANOL (already 0)
TRUCK_ELEC (already 0), TRUCK_FUEL_CELL (already 0)
BUS_COACH_HYDIESEL, BUS_COACH_CNG_STOICH
PLANE_H2_SHORT_HAUL (if present)
BOAT_FREIGHT_NG, BOAT_FREIGHT_METHANOL
CARGO_LNG, CARGO_METHANOL, CARGO_AMMONIA, CARGO_FUELCELL_LH2
CARGO_FUELCELL_AMMONIA, CARGO_RETRO_METHANOL, CARGO_RETRO_AMMONIA
H2_ELECTROLYSIS, H2_NG, H2_BIOMASS
H2_RETROFITTED, H2_NEW, H2_SUBSEA_RETRO, H2_SUBSEA_NEW
BIOMASS_TO_METHANE, BIOWASTE_TO_METHANE, SYN_METHANATION
BIOMETHANATION_WET_BIOMASS, BIOMETHANATION_BIOWASTE
BIOMASS_TO_GASOLINE, BIOMASS_TO_DIESEL, BIOMASS_TO_JET_FUEL, BIOMASS_TO_LFO
BIOWASTE_TO_GASOLINE, BIOWASTE_TO_DIESEL, BIOWASTE_TO_JET_FUEL, BIOWASTE_TO_LFO
DIESEL_TO_JET_FUEL
ATM_CCS, INDUSTRY_CCS, CO2_STORAGE
SYN_METHANOLATION, METHANE_TO_METHANOL, BIOMASS_TO_METHANOL, BIOWASTE_TO_METHANOL
HABER_BOSCH
POWER_TO_GASOLINE, POWER_TO_DIESEL, POWER_TO_JET_FUEL, POWER_TO_LFO
H2_TO_GASOLINE, H2_TO_DIESEL, H2_TO_JET_FUEL, H2_TO_LFO
AMMONIA_TO_H2
OIL_TO_HVC, GAS_TO_HVC, BIOMASS_TO_HVC, METHANOL_TO_HVC
TRUCK_METHANOL, TRUCK_NG, CAR_NG
```

Technologies to cap at realistic levels:

```
# Heat - DHN (existing Finnish CHP/boiler fleet)
DHN_HP_ELEC:        f_max = 0.5      (small existing heat pump capacity)
DHN_BOILER_GAS:     f_max = 2.0      (gas boilers in Finnish DHN)
DHN_BOILER_WOOD:    f_max = 5.0      (wood boilers in Finnish DHN)
DHN_COGEN_WASTE:    f_max = 1.0      (waste incineration CHP)

# Heat - Decentralised
DEC_HP_ELEC:        f_max = 5.0      (heat pumps growing but limited in 2017)
DEC_COGEN_GAS:      f_max = 0.5      (small CHP units)
DEC_COGEN_OIL:      f_max = 0.5      (oil CHP rare)
DEC_BOILER_GAS:     f_max = 5.0      (gas boilers in buildings)
DEC_BOILER_WOOD:    f_max = 10.0     (wood/pellet stoves common in Finland)
DEC_BOILER_OIL:     f_max = 8.0      (oil heating still significant in 2017)
DEC_ELEC_COLD:      f_max = 5.0      (electric cooling)

# Industry
IND_COGEN_GAS:      f_max = 2.0
IND_COGEN_WASTE:    f_max = 1.0
IND_COGEN_COAL:     f_max = 2.0
IND_BOILER_BIOWASTE: f_max = 1.0
IND_BOILER_WASTE:   f_max = 1.0
IND_DIRECT_ELEC:    f_max = 5.0      (electric arc furnaces, etc.)

# Transport
BUS_COACH_DIESEL:   f_max = 100000   (keep, it's the 2017 bus fleet)
TRAMWAY_TROLLEY:    f_max = 100000   (keep for Helsinki metro/tram)
TRAIN_PUB:          f_max = 100000   (keep for VR rail)
PLANE_SHORT_HAUL:   f_max = 100000   (keep for domestic aviation)
PLANE_LONG_HAUL:    already bounded by demand
TRAIN_FREIGHT:      f_max = 100000
BOAT_FREIGHT_DIESEL: f_max = 100000
CARGO_LFO:          f_max = 100000   (this is the dominant shipping tech)

# Storage (set to realistic levels)
BATT_LI:            f_max = 1.0      (negligible in 2017)
CAES:               f_max = 0.0      (none in Finland)
GAS_STORAGE:        f_max = 100      (small gas storage)
H2_STORAGE:         f_max = 0.0
DIESEL_STORAGE:     f_max = 100
JET_FUEL_STORAGE:   f_max = 100
GASOLINE_STORAGE:   f_max = 100
LFO_STORAGE:        f_max = 100
AMMONIA_STORAGE:    f_max = 0.0
METHANOL_STORAGE:   f_max = 0.0
```

**Expected impact:** Eliminates numerical instability. The LP should converge cleanly with variables spanning only ~5 orders of magnitude instead of 15.

---

### Priority 1: Fix OIL Overconsumption (206 → 96 TWh)

**Root cause:** SHIPPING demand = 148,985 Mtkm uses CARGO_LFO (efficiency = 1/0.0217 = 46 GWh per GW-capacity) which absorbs ~149,000 GWh of LFO from the 150,000 GWh cap.

**Actions:**

| Lever | Current | Proposed | Rationale |
|-------|---------|----------|-----------|
| LFO `avail_exterior` | 150,000 | **80,000** | Finland's total oil consumption was ~96 TWh primary. LFO is the largest share (shipping fuel) but not all 150k. Reduce to force the model to match reality. |
| DIESEL `avail_exterior` | 25,000 | **25,000** | Keep — aligns with ~25 TWh diesel consumption |
| GASOLINE `avail_exterior` | 15,000 | **16,000** | Keep — aligns with ~16 TWh gasoline |
| JET_FUEL `avail_exterior` | 15,000 | **5,000** | Finland's aviation fuel ~5 TWh in 2017. Current cap is 3× too high. |

**Alternative approach (finer-grained):** Instead of cutting LFO globally, tighten `fmax_perc` on CARGO_LFO in SHIPPING to limit its market share from 1.0 to something like 0.6. But this requires understanding the SHIPPING sector composition, which is complex. The resource cap is simpler and more direct.

---

### Priority 2: Force Wood/Biomass Usage (11 → 105 TWh)

**Root cause:** Wood (c_op_local = 0.022 M€/GWh) is more expensive than coal (0.015), gas (0.02), and the model has no reason to prefer it when fossil fuels are cheaper. Even though `avail_local` = 110,806 GWh, the optimizer only uses 6,319 GWh.

**Actions — Two complementary approaches:**

#### Approach A: Force biomass techs via fmin_perc (market share floors)

| Technology | Sector | Current fmin_perc | Proposed | Effect |
|-----------|--------|------------------|----------|--------|
| IND_BOILER_WOOD | HEAT_HIGH_T | 0.0 | **0.30** | Forces wood boilers to supply ≥30% of industrial heat → consumes ~18 TWh wood |
| IND_COGEN_WOOD | HEAT_HIGH_T | 0.0 | **0.15** | Forces wood CHP for ≥15% of industrial heat → consumes ~11 TWh wood + generates ~4 TWh electricity |
| DHN_COGEN_WOOD | HEAT_LOW_T_DHN | 0.0 | **0.30** | Forces wood CHP for ≥30% of DHN heat → consumes ~16 TWh wood + 5 TWh electricity |
| DEC_BOILER_WOOD | HEAT_LOW_T_DECEN | 0.0 | **0.15** | Forces wood pellet stoves for ≥15% of decentralised heat → consumes ~15 TWh wood |

**Estimated total wood consumption:** ~60 TWh (closer to 105 TWh target but may need further tuning)

#### Approach B: Tighten fossil alternatives via resource caps

| Resource | Current `avail_exterior` | Proposed | Rationale |
|----------|------------------------|----------|-----------|
| GAS | 28,000 | **22,000** | Finland actually consumed ~25 TWh gas. Reducing the cap forces substitution to wood/biomass |
| COAL | 50,000 | **35,000** | Finland consumed ~35 TWh coal+peat/thermal basis. Cap closer to actual |

#### Approach C: Make wood cheaper or raise fossil costs

This is a **last resort** — modifying `c_op_local` for wood or `c_op_exterior` for coal/gas is not recommended for calibration because these are supposed to reflect actual market prices. But if approaches A+B aren't sufficient:

| Resource | Current c_op_local | Possible adjustment |
|----------|-------------------|---------------------|
| WOOD | 0.022 | Could lower to 0.018 (reflecting subsidized biomass) |
| COAL | 0.015 (exterior) | Could raise to 0.020 (reflecting carbon tax) |

---

### Priority 3: Tighten Nuclear (127 → 65 TWh thermal / 21.6 TWh electricity)

**Root cause:** Constraint violation (F = 5.68 GW vs f_max = 2.8 GW) due to numerical instability.

**Actions:**

| Lever | Current | Proposed | Rationale |
|-------|---------|----------|-----------|
| NUCLEAR `f_min` | 2.7 | **2.76** | Olkiluoto 1+2 (2× 0.89 GW) + Loviisa 1+2 (2× 0.49 GW) = 2.76 GW |
| NUCLEAR `f_max` | 2.8 | **2.80** | Keep tight (Olkiluoto 3 not yet online in 2017) |
| URANIUM `avail_exterior` | 100,000 | **62,000** | 2.8 GW × 0.849 × 8,760h = 20,823 GWh elec × 2.7027 = 56,278 GWh thermal. Cap at 62k provides ~10% headroom |

**Expected result:** After Priority 0 fixes the degeneracy, the f_max constraint should bind properly. The URANIUM cap provides a safety net.

---

### Priority 4: Fix Solar Overdeployment (2.7 → 0.1 TWh)

**Root cause:** PV_ROOFTOP f_max = 2.0 GW, PV_UTILITY f_max = 1.0 GW — far too high for 2017 Finland (actual installed ~0.07 GW).

| Lever | Current | Proposed | Rationale |
|-------|---------|----------|-----------|
| PV_ROOFTOP `f_max` | 2.0 | **0.05** | Finland had ~50 MW solar in 2017 |
| PV_UTILITY `f_max` | 1.0 | **0.02** | Utility solar was negligible in 2017 |

---

### Priority 5: Fix Coal/Peat Balance (24 → 50 TWh)

**Root cause:** COAL_US at 5.38 GW produces mostly electricity; coal CHP and industrial coal are underrepresented.

| Lever | Current | Proposed | Rationale |
|-------|---------|----------|-----------|
| IND_BOILER_COAL `fmin_perc` | 0.10 | **0.15** | Force more coal in industrial heat |
| DHN_COGEN_COAL `fmin_perc` | 0.15 | **0.20** | Finland had significant coal CHP in 2017 |
| COAL `avail_exterior` | 50,000 | **40,000** | Slightly reduce cap, let fmin_perc drive allocation |

**Note on peat:** Peat is not modeled as a separate resource. It's implicitly included in COAL (REF_REGION treats coal+peat as one resource). This is a known limitation.

---

### Priority 6: Fix Electricity Mix Composition

After Priorities 0–5, the electricity mix should improve significantly. Additional fine-tuning:

| Lever | Current | Proposed | Rationale |
|-------|---------|----------|-----------|
| CCGT `f_max` | 1.5 | **1.2** | Limit gas electricity to ~3.7 TWh target |
| WIND_ONSHORE `f_max` | 2.1 | **1.6** | Finland had ~1.5–2.0 GW wind in 2017. Tighter cap = ~4.8 TWh |
| WIND_OFFSHORE `f_max` | 0.1 | **0.03** | Very little offshore wind in 2017 |

---

## 4. Implementation Plan

### Step 1: Create `Data/2017/FI/Technologies_v6.csv`

Add all 120+ previously unconstrained technologies with `f_max = 0` or realistic caps. This is the single most impactful change.

### Step 2: Create `Data/2017/FI/Resources_v6.csv`

Adjust resource caps:
- LFO: 150,000 → 80,000
- JET_FUEL: 15,000 → 5,000
- URANIUM: 100,000 → 62,000
- GAS: 28,000 → 22,000

### Step 3: Apply biomass market share floors

Set `fmin_perc` for wood technologies in Technologies_v6.csv.

### Step 4: Run and evaluate

```bash
python scripts/run_calib_case.py --case v6_constrained --year 2017
```

### Step 5: Iterate

If wood consumption is still too low, increase `fmin_perc` for wood technologies.
If OIL is still too high, further reduce LFO `avail_exterior`.
If nuclear violates bounds, the degeneracy fix (Step 1) should have resolved it.

---

## 5. Expected Outcome After v6

| Category | v5 Model | Proposed v6 Target | Reality |
|----------|----------|--------------------|---------|
| WOOD (TWh) | 11 | 60–80 | 105 |
| OIL (TWh) | 206 | 90–100 | 96 |
| NUCLEAR (TWh) | 127 | 55–65 | 65 |
| COAL (TWh) | 24 | 35–45 | 50 |
| GAS (TWh) | 28 | 20–25 | 25 |
| HYDRO (TWh) | 15 | 15 | 15 |
| WIND (TWh) | 7 | 4–5 | 5 |
| **CO2 (MtCO2)** | 81 | 40–50 | 42 |

Wood may not reach 105 TWh in v6 — achieving the remaining gap (80→105) may require examining the demand structure or introducing peat as a separate resource.

---

## 6. Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Infeasibility after tightening bounds | Medium | Start conservative (looser caps), tighten iteratively |
| Wood still too low despite fmin_perc | High | May need to lower `c_op_local` for wood or raise fossil costs |
| Solver still violates bounds | Low (after Priority 0) | Check solve_result_num and tolerance; consider simplex instead of barrier |
| Industrial heat demand too rigid | Medium | Verify HEAT_HIGH_T demand value (59,821 GWh) matches Finnish statistics |

---

## 7. Quick Reference: Current vs Proposed FI Technologies.csv Changes

### Technologies to ADD (not currently in FI overrides):

| Technology | f_min | f_max | fmin_perc | fmax_perc | Note |
|-----------|-------|-------|-----------|-----------|------|
| CCGT_AMMONIA | 0 | 0 | 0 | 1 | Disable |
| COAL_IGCC | 0 | 0 | 0 | 1 | Disable |
| BIOMASS_TO_POWER | 0 | 0 | 0 | 1 | Disable |
| IND_COGEN_GAS | 0 | 2 | 0 | 1 | Cap |
| IND_COGEN_WASTE | 0 | 1 | 0 | 1 | Cap |
| IND_COGEN_COAL | 0 | 2 | 0 | 1 | Cap |
| IND_BOILER_BIOWASTE | 0 | 1 | 0 | 1 | Cap |
| IND_BOILER_WASTE | 0 | 1 | 0 | 1 | Cap |
| IND_DIRECT_ELEC | 0 | 5 | 0 | 1 | Cap |
| DHN_HP_ELEC | 0 | 0.5 | 0 | 1 | Cap |
| DHN_COGEN_WASTE | 0 | 1 | 0 | 1 | Cap |
| DHN_BOILER_GAS | 0 | 2 | 0 | 1 | Cap |
| DHN_BOILER_WOOD | 0 | 5 | 0 | 1 | Cap |
| DEC_HP_ELEC | 0 | 5 | 0 | 1 | Cap |
| DEC_COGEN_GAS | 0 | 0.5 | 0 | 1 | Cap |
| DEC_COGEN_OIL | 0 | 0.5 | 0 | 1 | Cap |
| DEC_BOILER_GAS | 0 | 5 | 0 | 1 | Cap |
| DEC_BOILER_WOOD | 0 | 10 | 0 | 1 | Cap |
| DEC_BOILER_OIL | 0 | 8 | 0 | 1 | Cap |
| DEC_ELEC_COLD | 0 | 5 | 0 | 1 | Cap |
| IND_ELEC_COLD | 0 | 5 | 0 | 1 | Cap |
| DEC_ADVCOGEN_GAS | 0 | 0 | 0 | 1 | Disable |
| DEC_ADVCOGEN_H2 | 0 | 0 | 0 | 1 | Disable |
| DEC_THHP_GAS | 0 | 0 | 0 | 1 | Disable |
| BUS_COACH_DIESEL | 0 | 100000 | 0.5 | 1 | Keep, force share |
| BUS_COACH_HYDIESEL | 0 | 0 | 0 | 1 | Disable |
| BUS_COACH_CNG_STOICH | 0 | 0 | 0 | 1 | Disable |
| TRAMWAY_TROLLEY | 0 | 100000 | 0 | 0.5 | Cap share |
| TRAIN_PUB | 0 | 100000 | 0 | 1 | Keep |
| PLANE_SHORT_HAUL | 0 | 100000 | 0 | 1 | Keep |
| CAR_NG | 0 | 0 | 0 | 1 | Disable |
| TRAIN_FREIGHT | 0 | 100000 | 0 | 1 | Keep |
| BOAT_FREIGHT_DIESEL | 0 | 100000 | 0.9 | 1 | Force dominant share |
| BOAT_FREIGHT_NG | 0 | 0 | 0 | 1 | Disable |
| BOAT_FREIGHT_METHANOL | 0 | 0 | 0 | 1 | Disable |
| CARGO_LFO | 0 | 100000 | 0.9 | 1 | Force dominant share |
| CARGO_LNG | 0 | 0 | 0 | 1 | Disable |
| CARGO_METHANOL | 0 | 0 | 0 | 1 | Disable |
| CARGO_AMMONIA | 0 | 0 | 0 | 1 | Disable |
| CARGO_FUELCELL_LH2 | 0 | 0 | 0 | 1 | Disable |
| CARGO_FUELCELL_AMMONIA | 0 | 0 | 0 | 1 | Disable |
| CARGO_RETRO_METHANOL | 0 | 0 | 0 | 1 | Disable |
| CARGO_RETRO_AMMONIA | 0 | 0 | 0 | 1 | Disable |
| TRUCK_METHANOL | 0 | 0 | 0 | 1 | Disable |
| TRUCK_NG | 0 | 0 | 0 | 1 | Disable |
| H2_ELECTROLYSIS | 0 | 0 | 0 | 1 | Disable |
| H2_NG | 0 | 0 | 0 | 1 | Disable |
| H2_BIOMASS | 0 | 0 | 0 | 1 | Disable |
| H2_RETROFITTED | 0 | 0 | 0 | 1 | Disable |
| H2_NEW | 0 | 0 | 0 | 1 | Disable |
| H2_SUBSEA_RETRO | 0 | 0 | 0 | 1 | Disable |
| H2_SUBSEA_NEW | 0 | 0 | 0 | 1 | Disable |
| GAS_PIPELINE | 0 | 0 | 0 | 1 | Disable (single-region) |
| GAS_SUBSEA | 0 | 0 | 0 | 1 | Disable (single-region) |
| BIOMASS_TO_METHANE | 0 | 0 | 0 | 1 | Disable |
| BIOWASTE_TO_METHANE | 0 | 0 | 0 | 1 | Disable |
| SYN_METHANATION | 0 | 0 | 0 | 1 | Disable |
| BIOMETHANATION_WET_BIOMASS | 0 | 0 | 0 | 1 | Disable |
| BIOMETHANATION_BIOWASTE | 0 | 0 | 0 | 1 | Disable |
| BIOMASS_TO_GASOLINE | 0 | 0 | 0 | 1 | Disable |
| BIOMASS_TO_DIESEL | 0 | 0 | 0 | 1 | Disable |
| BIOMASS_TO_JET_FUEL | 0 | 0 | 0 | 1 | Disable |
| BIOMASS_TO_LFO | 0 | 0 | 0 | 1 | Disable |
| BIOWASTE_TO_GASOLINE | 0 | 0 | 0 | 1 | Disable |
| BIOWASTE_TO_DIESEL | 0 | 0 | 0 | 1 | Disable |
| BIOWASTE_TO_JET_FUEL | 0 | 0 | 0 | 1 | Disable |
| BIOWASTE_TO_LFO | 0 | 0 | 0 | 1 | Disable |
| DIESEL_TO_JET_FUEL | 0 | 0 | 0 | 1 | Disable |
| ATM_CCS | 0 | 0 | 0 | 1 | Disable |
| INDUSTRY_CCS | 0 | 0 | 0 | 1 | Disable |
| CO2_STORAGE | 0 | 0 | 0 | 1 | Disable |
| SYN_METHANOLATION | 0 | 0 | 0 | 1 | Disable |
| METHANE_TO_METHANOL | 0 | 0 | 0 | 1 | Disable |
| BIOMASS_TO_METHANOL | 0 | 0 | 0 | 1 | Disable |
| BIOWASTE_TO_METHANOL | 0 | 0 | 0 | 1 | Disable |
| HABER_BOSCH | 0 | 0 | 0 | 1 | Disable |
| POWER_TO_GASOLINE | 0 | 0 | 0 | 1 | Disable |
| POWER_TO_DIESEL | 0 | 0 | 0 | 1 | Disable |
| POWER_TO_JET_FUEL | 0 | 0 | 0 | 1 | Disable |
| POWER_TO_LFO | 0 | 0 | 0 | 1 | Disable |
| H2_TO_GASOLINE | 0 | 0 | 0 | 1 | Disable |
| H2_TO_DIESEL | 0 | 0 | 0 | 1 | Disable |
| H2_TO_JET_FUEL | 0 | 0 | 0 | 1 | Disable |
| H2_TO_LFO | 0 | 0 | 0 | 1 | Disable |
| AMMONIA_TO_H2 | 0 | 0 | 0 | 1 | Disable |
| OIL_TO_HVC | 0 | 100000 | 0.9 | 1 | Keep (petrochemicals), force share |
| GAS_TO_HVC | 0 | 0 | 0 | 1 | Disable |
| BIOMASS_TO_HVC | 0 | 0 | 0 | 1 | Disable |
| METHANOL_TO_HVC | 0 | 0 | 0 | 1 | Disable |
| BATT_LI | 0 | 1 | 0 | 1 | Cap small |
| CAES | 0 | 0 | 0 | 1 | Disable |

### Technologies to MODIFY (already in FI overrides):

| Technology | Current f_min/f_max | Proposed f_min/f_max | fmin_perc | fmax_perc |
|-----------|--------------------|--------------------|-----------|-----------|
| NUCLEAR | 2.7 / 2.8 | 2.76 / 2.80 | 0 | 1 |
| PV_ROOFTOP | 0.02 / 2.0 | 0.02 / 0.05 | 0 | 1 |
| PV_UTILITY | 0.0 / 1.0 | 0.0 / 0.02 | 0 | 1 |
| WIND_ONSHORE | 2.0 / 2.1 | 1.5 / 1.7 | 0 | 1 |
| WIND_OFFSHORE | 0.0 / 0.1 | 0.0 / 0.03 | 0 | 1 |
| CCGT | 0.6 / 1.5 | 0.6 / 1.2 | 0 | 1 |
| IND_BOILER_WOOD | 5.0 / 100000 | 5.0 / 15 | **0.30** | 1 |
| IND_COGEN_WOOD | 1.0 / 100000 | 1.0 / 8 | **0.15** | 1 |
| DHN_COGEN_WOOD | 2.5 / 100000 | 2.5 / 10 | **0.30** | 1 |
| DHN_COGEN_COAL | 0.5 / 100000 | 0.5 / 5 | **0.20** | 1 |
| IND_BOILER_COAL | 0.5 / 100000 | 0.5 / 5 | **0.15** | 1 |
| DEC_DIRECT_ELEC | 0 / 100000 | 0 / 5 | 0.10 | 0.30 |

### Resources to MODIFY:

| Resource | Current avail_exterior | Proposed |
|----------|----------------------|----------|
| LFO | 150,000 | **80,000** |
| JET_FUEL | 15,000 | **5,000** |
| URANIUM | 100,000 | **62,000** |
| GAS | 28,000 | **22,000** |
| COAL | 50,000 | **35,000** |

---

## 8. Calibration Workflow Diagram

```
┌─────────────────────────────────────────┐
│         Priority 0: Fix Degeneracy      │
│    Set f_max=0 for 70+ future techs     │
│    Set realistic f_max for 30+ others   │
│    Expected: Clean solver convergence   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│    Priority 1: Fix OIL (206→96 TWh)    │
│    LFO cap: 150k → 80k                 │
│    JET_FUEL cap: 15k → 5k              │
│    Expected: Oil drops to ~100 TWh      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Priority 2: Force Biomass (11→105 TWh) │
│   fmin_perc on IND/DHN/DEC wood techs  │
│   Lower GAS/COAL exterior caps          │
│   Expected: Wood rises to 60-80 TWh     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│   Priority 3: Nuclear (127→65 TWh)      │
│   URANIUM cap: 100k → 62k              │
│   f_min/f_max: 2.76/2.80               │
│   Expected: Fixed by Priority 0        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│   Priorities 4-6: Fine-tuning           │
│   Solar: PV caps → 0.05/0.02 GW        │
│   Coal CHP shares via fmin_perc         │
│   Electricity mix rebalancing           │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│         Run → Compare → Iterate         │
│    Target: ≤20% error on all metrics    │
│    If wood still low: last resort       │
│    (lower c_op_local for WOOD)          │
└─────────────────────────────────────────┘
```
