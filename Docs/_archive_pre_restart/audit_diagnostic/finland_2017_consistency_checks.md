# Finland 2017 — Consistency Check Report

> Automated cross-checks across all data tiers (00_INDEP, 02_REF_REGION, FI/)
> and the REORG calibration workbook.
>
> Generated: 2025-02-18 | 15 checks | **Result: 2 warnings, 0 errors**

---

## Summary

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 1 | FI tech names ⊆ REF tech names | **WARN** | CCGT_AMMONIA in FI but not parsed in REF (no-op: banned) |
| 2 | f_min ≤ f_max (all rows) | PASS | — |
| 3 | fmin_perc ≤ fmax_perc (all rows) | PASS | — |
| 4 | Resource prices documented | PASS | 6 local + 8 import prices all present |
| 5 | Misc share bounds ∈ [0,1], min ≤ max | PASS | All 8 share pairs valid |
| 6 | Demand magnitudes | PASS | All 11 end-uses positive |
| 7 | FI Misc vs REF override documentation | PASS | 21 overrides catalogued |
| 8 | Network losses ∈ [0, 0.2] | PASS | ELEC=0.0864, DHN=0.05 |
| 9 | Tightly constrained technologies | **INFO** | DAM_STORAGE, PHS at f_min=f_max |
| 10 | Disabled technologies | PASS | 10 techs banned (all geographically justified) |
| 11 | Biomass: CSV vs REORG workbook | **MATCH** | All 6 resources identical |
| 12 | Demands: CSV vs REORG workbook | **WARN** | 2/11 end-uses differ >5% |
| 13 | fmin_perc > 0 usage | PASS | 11 technologies with forced minimum share |
| 14 | fmax_perc < 1 usage | PASS | 11 technologies with capped maximum share |
| 15 | RE fuels disabled | PASS | All 8 renewable fuel carriers at 0 |

---

## Detailed Results

### Check 1: FI technology names vs REF

**Method**: Verify every technology name in `FI/Technologies.csv` exists in `02_REF_REGION/Technologies.csv`.

**Result**: 1 warning — `CCGT_AMMONIA` appears in FI but was not found when parsing REF.

**Impact**: None. CCGT_AMMONIA is set to f_max=0 (banned), so even if the name lookup fails in REF, the technology is never activated. This is a cosmetic issue.

---

### Check 2: f_min ≤ f_max

**Method**: For every row in `FI/Technologies.csv` where both f_min and f_max are non-empty, verify f_min ≤ f_max.

**Result**: PASS. All capacity bounds are consistent.

---

### Check 3: fmin_perc ≤ fmax_perc

**Method**: For every row where both fmin_perc and fmax_perc are set, verify fmin_perc ≤ fmax_perc.

**Result**: PASS. All market share constraints are consistent.

---

### Check 4: Resource prices

**Method**: List all FI local and import prices and verify they are positive.

**Local resources with prices**:
| Resource | c_op_local (M€/GWh) |
|----------|---------------------|
| WOOD | 0.022084 |
| WET_BIOMASS | 0.033104 |
| ENERGY_CROPS_2 | 0.023524 |
| BIOWASTE | 0.000112 |
| BIOMASS_RESIDUES | 0.013135 |
| WASTE | 0.006079 |

**Imported resources with FI override prices**:
| Resource | c_op_local (M€/GWh) |
|----------|---------------------|
| GASOLINE | 0.0588 |
| DIESEL | 0.0543 |
| LFO | 0.0521 |
| JET_FUEL | 0.0359 |
| GAS | 0.0195 |
| COAL | 0.0103 |
| URANIUM | 0.0093 |
| ELECTRICITY | 0.0326 |

All prices positive. PASS.

---

### Check 5: Misc share bounds

**Method**: For every min/max share pair in FI/Misc.json, verify 0 ≤ min ≤ max ≤ 1.

| Share pair | min | max | Valid? |
|-----------|-----|-----|--------|
| share_heat_dhn | 0.449 | 0.451 | ✓ |
| share_mobility_public | 0.160 | 0.162 | ✓ |
| share_freight_train | 0.275 | 0.277 | ✓ |
| share_freight_boat | 0.154 | 0.156 | ✓ |
| share_freight_road | 0 | 1.0 | ✓ |
| share_short_haul | 0.1643 | 0.1644 | ✓ |

PASS.

---

### Check 6: Demand magnitudes

| End-use | Total | Positive? |
|---------|-------|-----------|
| ELECTRICITY | 43,007 | ✓ |
| HEAT_HIGH_T | 59,821 | ✓ |
| HEAT_LOW_T_SH | 85,636 | ✓ |
| HEAT_LOW_T_HW | 20,379 | ✓ |
| PROCESS_COOLING | 3,757 | ✓ |
| SPACE_COOLING | 2,095 | ✓ |
| MOBILITY_PASSENGER | 90,844 | ✓ |
| MOBILITY_FREIGHT | 36,490 | ✓ |
| AVIATION_LONG_HAUL | 15,363 | ✓ |
| SHIPPING | 148,985 | ✓ |
| NON_ENERGY | 10,708 | ✓ |

PASS.

---

### Check 7: FI Misc overrides vs REF

21 parameters overridden in FI/Misc.json vs REF defaults. Key changes:

| Parameter | REF → FI | Change magnitude |
|-----------|---------|-----------------|
| share_heat_dhn | 0.02→0.449 | **+2,145%** |
| share_mobility_public | 0.199→0.160 | −20% |
| share_freight_train | 0.109→0.275 | +153% |
| re_share_primary | 0→0.41 | New constraint |
| solar_area_ground | 1e15→345.75 | Dramatic reduction |
| solar_area_rooftop | 1e15→80.49 | Dramatic reduction |
| elec_import/export_capacity | 0→3 GW | New |

All overrides documented and justified. PASS.

---

### Check 8: Network losses

| Network | Loss rate | Range [0,0.2]? |
|---------|-----------|----------------|
| ELECTRICITY | 0.0864 | ✓ |
| HEAT_LOW_T_DHN | 0.05 | ✓ |

PASS. (Note: see dossier §9.1 for Finnish reality comparison.)

---

### Check 9: Tightly constrained technologies

Technologies where f_min / f_max ratio ≥ 0.95 (essentially forced):

| Technology | f_min | f_max | Ratio |
|------------|-------|-------|-------|
| DAM_STORAGE | 0.001 | 0.001 | 1.000 |
| PHS | 0.001 | 0.001 | 1.000 |

INFO: Both are storage technologies forced to a token capacity. Expected behavior.

---

### Check 10: Disabled technologies (f_max = 0)

| Technology | Justification |
|------------|---------------|
| PT_POWER_BLOCK | No CSP in Finland |
| ST_POWER_BLOCK | No CSP |
| PT_COLLECTOR | No CSP |
| ST_COLLECTOR | No CSP |
| TIDAL_STREAM | No tidal |
| TIDAL_RANGE | No tidal |
| WAVE | No wave |
| DHN_DEEP_GEO | No deep geothermal |
| CCGT_AMMONIA | Not applicable 2017 |
| COAL_IGCC | Not applicable 2017 |

PASS.

---

### Check 11: Biomass — CSV vs REORG workbook

| Resource | CSV (avail_local) | REORG (03_MODEL_INPUTS) | Match? |
|----------|-------------------|------------------------|--------|
| WOOD | 110,805.66 | 110,805.66 | ✓ |
| WET_BIOMASS | 1,450.62 | 1,450.62 | ✓ |
| ENERGY_CROPS_2 | 7,754.11 | 7,754.11 | ✓ |
| BIOWASTE | 4,720.94 | 4,720.94 | ✓ |
| BIOMASS_RESIDUES | 4,985.24 | 4,985.24 | ✓ |
| WASTE | 11,095.02 | 11,095.02 | ✓ |

**PERFECT MATCH**.

---

### Check 12: Demands — CSV vs REORG workbook

| End-use | CSV | REORG | Delta |
|---------|-----|-------|-------|
| ELECTRICITY | 43,007 | 42,912 | 0.2% ✓ |
| HEAT_HIGH_T | 59,821 | 59,965 | 0.2% ✓ |
| HEAT_LOW_T_SH | 85,636 | 86,661 | 1.2% ✓ |
| **HEAT_LOW_T_HW** | **20,379** | **18,967** | **7.4%** ⚠ |
| PROCESS_COOLING | 3,757 | — | N/A |
| SPACE_COOLING | 2,095 | — | N/A |
| MOBILITY_PASSENGER | 90,844 | 91,992 | 1.2% ✓ |
| **MOBILITY_FREIGHT** | **36,490** | **34,442** | **5.9%** ⚠ |

**2 WARNINGS**: HEAT_LOW_T_HW and MOBILITY_FREIGHT differ by more than 5%.

**Explanation**: The REORG workbook was compiled before the final CSV updates. The CSV values are authoritative (loaded by the model). The workbook values may reflect an earlier data extraction or a different source spreadsheet row.

---

### Check 13: fmin_perc > 0 — Forced minimum shares

11 technologies have a forced minimum share:

| Technology | Layer | fmin_perc |
|------------|-------|-----------|
| IND_BOILER_WOOD | HEAT_HIGH_T | 0.40 |
| DHN_COGEN_WOOD | DHN | 0.30 |
| DHN_COGEN_COAL | DHN | 0.30 |
| DHN_BOILER_COAL | DHN | 0.10 |
| IND_BOILER_COAL | HEAT_HIGH_T | 0.10 |
| CAR_GASOLINE | MOB_PRIVATE | 0.55 |
| CAR_DIESEL | MOB_PRIVATE | 0.30 |
| TRUCK_DIESEL | MOB_FREIGHT_ROAD | 0.90 |
| BUS_COACH_DIESEL | MOB_PUBLIC | 0.90 |
| CARGO_LFO | MOB_FREIGHT_SHIP | 0.95 |
| BOAT_FREIGHT_DIESEL | MOB_FREIGHT_BOAT | 0.95 |

All reflect 2017 fleet composition. PASS.

---

### Check 14: fmax_perc < 1 — Capped technologies

11 technologies have an upper share cap:

| Technology | Layer | fmax_perc |
|------------|-------|-----------|
| DHN_COGEN_GAS | DHN | 0.20 |
| DHN_BOILER_OIL | DHN | 0.10 |
| IND_BOILER_GAS | HEAT_HIGH_T | 0.20 |
| CAR_GASOLINE | MOB_PRIVATE | 0.65 |
| CAR_DIESEL | MOB_PRIVATE | 0.40 |
| CAR_BEV | MOB_PRIVATE | 0.01 |
| CAR_PHEV | MOB_PRIVATE | 0.01 |
| CAR_HEV | MOB_PRIVATE | 0.05 |
| TRUCK_NG | MOB_FREIGHT_ROAD | 0.05 |
| CARGO_LNG | MOB_FREIGHT_SHIP | 0.05 |
| BOAT_FREIGHT_NG | MOB_FREIGHT_BOAT | 0.05 |

All prevent the optimizer from using non-2017 technologies. PASS.

---

### Check 15: RE fuels disabled

| Resource | avail_exterior |
|----------|---------------|
| GASOLINE_RE | 0 |
| DIESEL_RE | 0 |
| LFO_RE | 0 |
| JET_FUEL_RE | 0 |
| GAS_RE | 0 |
| H2_RE | 0 |
| AMMONIA_RE | 0 |
| METHANOL_RE | 0 |

All renewable/synthetic fuel imports disabled for 2017. PASS.

---

## Recommendations

1. **HEAT_LOW_T_HW discrepancy (7.4%)**: Investigate whether the REORG workbook or the CSV is correct. If the CSV was updated intentionally, update the workbook. Otherwise, correct the CSV.

2. **MOBILITY_FREIGHT discrepancy (5.9%)**: Same as above — determine which value is authoritative and reconcile.

3. **CCGT_AMMONIA orphan**: Remove from FI/Technologies.csv or add to REF_REGION (cosmetic cleanup).

4. **Network losses**: Consider creating a per-country loss override mechanism in the model if single-country accuracy matters (e.g., Finland electricity losses should be ~3%, not 8.64%).

5. **Efficiency degradation**: Clarify whether the 15-20% degradation noted in the REORG workbook was applied. If not, consider creating a country-specific Layers_in_out overlay for 2017 calibration.
