# Finland 2017 Calibration — Lever Map & Restoration Note

## 1. Source Identification

| Item | Value |
|------|-------|
| **Plots folder** | `plots/calibration_methodical_Feb14/` |
| **Case study** | `case_studies/FI/calib_2017_finland/` |
| **Git commit (inputs)** | `937940b` (Feb 12, "validation") |
| **Git commit (plots committed)** | `a20876d` (Feb 17, "Validation good prices") |
| **Proof** | SHA-256 match of `validation_sankey.html` between both folders |

### Files restored to actual Feb14 state

The working-tree state at the time of the Feb 16 run was never committed.
The exact inputs were **reverse-engineered** from `calib_2017_finland/reg_technologies.dat`
and `reg_resources.dat` by comparing against `02_REF_REGION` defaults.

| File | Status |
|------|--------|
| `Data/2017/FI/Technologies.csv` | ✅ Reconstructed from reg_technologies.dat (verified: PERFECT MATCH) |
| `Data/2017/FI/Resources.csv` | ✅ Reconstructed from reg_resources.dat (verified: PERFECT MATCH) |
| `Data/2017/FI/Demands.csv` | No change vs HEAD |
| `Data/2017/FI/Misc.json` | No change vs HEAD |
| `Data/2017/FI/Time_series.csv` | No change vs HEAD |
| `Data/2017/FI/Weights.csv` | No change vs HEAD |
| `Data/2017/FI/Storage_power_to_energy.csv` | No change vs HEAD |
| `Data/2017/00_INDEP/*` | No change vs HEAD |
| `Data/2017/02_REF_REGION/*` | No change vs HEAD |
| `esmc/**` | No change vs HEAD |

---

## 2. Data Pipeline (CSV → AMPL)

```
Data/2017/02_REF_REGION/Technologies.csv   (181 rows, 14 columns, reference defaults)
     │  read_tech() with header=[0], index_col=[3], skiprows=[1]
     │  → deepcopy into region.data['Technologies']
     ▼
Data/2017/FI/Technologies.csv              (63 rows, 3 data columns at 937940b)
     │  read_tech() with header=[0], index_col=[0]
     │  → .update() ONLY overwrites cells present in FI CSV
     ▼
esmc.py concat_reg_data()                   concatenates all regions
     │  → df.mask(df > 1e14, 'Infinity')    replaces huge numbers
     ▼
dat_print.py print_df()                     writes .dat files
     │
     ▼
case_studies/FI/calib_2017_finland/reg_technologies.dat    (AMPL-readable)
     │
     ▼
ESMC_model_AMPL.mod                         AMPL constraints consume the params
```

Same flow applies to Resources:
```
02_REF_REGION/Resources.csv  →  deepcopy  →  FI/Resources.csv .update()
     →  concat_reg_data()  →  reg_resources.dat  →  AMPL
```

---

## 3. Technology Lever Catalogue

### 3.1 Absolute Capacity Bounds (`f_min`, `f_max`)

**AMPL constraint** (line 338–339 of `ESMC_model_AMPL.mod`):
```
subject to size_limit {c in REGIONS, j in TECHNOLOGIES diff STORAGE_TECH}:
    f_min[c,j] <= F[c,j] <= f_max[c,j];
```

**Effect**: F[c,j] is the installed capacity in GW. `f_min` forces at least that much capacity;
`f_max` caps it. When `f_min = f_max = 0`, the technology is **banned**.

**Feb14 values** (from `Data/2017/FI/Technologies.csv` at 937940b):

| Technology | f_min (GW) | f_max (GW) | Interpretation |
|------------|-----------|-----------|----------------|
| NUCLEAR | 2.484 | 3.036 | Loviisa + Olkiluoto range |
| HYDRO_RIVER | 2.940 | 3.590 | Large run-of-river fleet |
| HYDRO_DAM | 1.210 | 2.383 | Reservoir hydro |
| WIND_ONSHORE | 1.350 | 2.100 | Growing onshore wind |
| WIND_OFFSHORE | 0.000 | 0.100 | Nearly banned |
| PV_ROOFTOP | 0.020 | 2.000 | Small base, room to grow |
| PV_UTILITY | 0.000 | 1.000 | Up to 1 GW |
| COAL_US | 3.500 | 4.500 | Coal condensation forced high |
| CCGT | 0.600 | 1.500 | 0.6–1.5 GW gas CCGT |
| CCGT_AMMONIA | 0.000 | 0.000 | Banned |
| COAL_IGCC | 0.000 | 0.000 | Banned |
| DHN_COGEN_GAS | 0.600 | 1.500 | 0.6–1.5 GW district cogen gas |
| DHN_BOILER_OIL | 0.400 | 500.0 | Oil boiler DHN (high cap) |
| DHN_BOILER_GAS | 0.000 | 500.0 | Gas boiler DHN (high cap) |
| DHN_BOILER_WOOD | 0.000 | 500.0 | Wood boiler DHN (high cap) |
| IND_BOILER_OIL | 0.200 | 500.0 | Oil boiler industry (high cap) |
| IND_BOILER_GAS | 0.000 | 500.0 | Gas boiler industry (high cap) |
| IND_BOILER_WOOD | 0.000 | 500.0 | Wood boiler industry (high cap) |
| IND_BOILER_COAL | 0.000 | 500.0 | Coal boiler industry (high cap) |
| CAR_PHEV | 0.000 | 0.020 | Nearly banned |
| CAR_BEV | 0.000 | 0.020 | Nearly banned |
| DAM_STORAGE | 0.001 | 0.001 | Fixed |
| PHS | 0.001 | 0.001 | Fixed |
| DHN_SOLAR | 0.000 | 56.345 | Solar thermal area |
| DEC_SOLAR | 0.000 | 56.345 | Dec solar thermal area |
| DHN_DEEP_GEO | 0.000 | 0.000 | Banned |
| GEOTHERMAL | 0.000 | 0.300 | Small geothermal cap |

**Banned technologies** (f_min = f_max = 0 in FI override):
PT_POWER_BLOCK, ST_POWER_BLOCK, PT_COLLECTOR, ST_COLLECTOR, TIDAL_STREAM,
TIDEL_RANGE, WAVE, DHN_DEEP_GEO, CCGT_AMMONIA, COAL_IGCC

**Near-banned** (f_max very small):
CAR_BEV (0.02), CAR_PHEV (0.02), WIND_OFFSHORE (0.1)

**Not overridden** (use REF defaults, most have f_max = 1e15 = unconstrained):
All transport, all decentralized heat, IND_COGEN_*, DHN_COGEN_WOOD/WASTE,
BIOMASS_TO_POWER, SMR, CCS techs, synthetic fuel techs

### 3.2 Market Share Bounds (`fmin_perc`, `fmax_perc`)

**AMPL constraints** (lines 651–657):
```
subject to f_max_perc {c in REGIONS, j in TECHNOLOGIES}:
    sum{...} F_t[c,j,h,td]*t_op[h,td] <= fmax_perc[c,j] * sum{...over same sector} ...

subject to f_min_perc {c in REGIONS, j in TECHNOLOGIES}:
    sum{...} F_t[c,j,h,td]*t_op[h,td] >= fmin_perc[c,j] * sum{...over same sector} ...
```

**Effect**: Fraction of yearly output relative to all technologies serving the same end-use layer.
Activated when config `f_perc: True` (which it is).

**Feb14 actual values** (reconstructed from reg_technologies.dat):

All `fmin_perc` and `fmax_perc` values use **REF_REGION defaults** (fmin_perc=0.0, fmax_perc=1.0).
The FI Technologies.csv had **NO fmin_perc or fmax_perc overrides** in the actual Feb14 run.

**Key insight**: The Feb14 run used **NO market share constraints at all**.
Transport, heat, and all other technologies had completely unconstrained shares.
The optimizer was free to choose any technology mix within absolute capacity bounds.
This explains why later versions (v8+) added fmin_perc/fmax_perc for transport and heat.

### 3.3 Config Flag: `f_perc`

| Value | Effect |
|-------|--------|
| `True` | Generic `f_max_perc`/`f_min_perc` constraints are ACTIVE for all technologies |
| `False` | Only `size_limit` (f_min/f_max) constraints apply |

At Feb14: **`f_perc = True`** — confirmed from `calib_2017_finland` reg_technologies.dat output.

---

## 4. Resource Lever Catalogue

### 4.1 Availability bounds

**AMPL constraints** (lines 353–357):
```
subject to resource_availability_local {c in REGIONS, i in RESOURCES}:
    sum{...} R_t_local[c,i,h,td]*t_op[h,td] <= avail_local[c,i];

subject to resource_availability_exterior {c in REGIONS, i in RESOURCES}:
    sum{...} R_t_exterior[c,i,h,td]*t_op[h,td] <= avail_exterior[c,i];
```

**Effect**: `avail_local` = maximum local production (GWh/y); `avail_exterior` = maximum imports (GWh/y).
In REF_REGION, most fossil fuels have `avail_exterior = 1e15` (AMPL Infinity = unlimited).
The regional FI override **caps** specific resources.

### 4.2 Feb14 resource bounds (reconstructed from reg_resources.dat)

| Resource | avail_local (GWh/y) | c_op_local (€/GWh) | avail_exterior (GWh/y) | Interpretation |
|----------|--------------------|--------------------|----------------------|----------------|
| **WOOD** | 110,806 | 0.022084 | 0 | Local only (no import) |
| WET_BIOMASS | 1,451 | 0.033 | 0 | Local only |
| ENERGY_CROPS_2 | 7,754 | 0.024 | 0 | Local only |
| BIOWASTE | 4,721 | 0.000112 | 0 | Near-free disposal |
| BIOMASS_RESIDUES | 4,985 | 0.013 | 0 | Local only |
| WASTE | 11,095 | 0.006 | 0 | Large local |
| **ELECTRICITY** | 0 | 0.050 | 25,000 | Electricity import capped |
| **GAS** | 0 | 0.020 | 28,000 | Import only, capped |
| **COAL** | 0 | 0.015 | 50,000 | Import only, capped |
| **GASOLINE** | 0 | 0.060 | 15,000 | Import only, capped |
| **DIESEL** | 0 | 0.050 | 25,000 | Import only, capped |
| **LFO** | 0 | 0.050 | **150,000** | Import only, HIGH cap |
| **JET_FUEL** | 0 | 0.050 | 15,000 | Import only, capped |
| **URANIUM** | 0 | 0.005 | 100,000 | Import only, capped |
| H2 | 0 | 0 | 0 | **Disabled** |
| H2_RE | 0 | 0 | 0 | **Disabled** |
| AMMONIA | 0 | 0 | 0 | **Disabled** |
| AMMONIA_RE | 0 | 0 | 0 | **Disabled** |
| METHANOL | 0 | 0 | 0 | **Disabled** |
| METHANOL_RE | 0 | 0 | 0 | **Disabled** |
| GASOLINE_RE | 0 | 0.06 | 0 | **Disabled** |
| DIESEL_RE | 0 | 0.05 | 0 | **Disabled** |
| LFO_RE | 0 | 0.05 | 0 | **Disabled** |
| JET_FUEL_RE | 0 | 0.05 | 0 | **Disabled** |
| GAS_RE | 0 | 0.02 | 0 | **Disabled** |

**Resources NOT overridden** (use REF_REGION defaults = 1e15):
ELECTRICITY (import/export capacity controlled by Misc.json `elec_import_capacity`/`elec_export_capacity`),
RES_WIND, RES_SOLAR, RES_HYDRO, RES_GEO (potentials from Time_series.csv capacity factors).

### 4.3 Local resource prices (`c_op_local`)

The FI override sets custom local prices for biomass and fossil fuels.
The `02_REF_REGION/Resources.csv` sets different default prices.
**The override mechanism**: FI values replace REF values cell-by-cell via `.update()`.

### 4.4 Exterior resource prices & emissions

Set in `Data/2017/00_INDEP/Resources_indep.csv` (globally, not per-region):
- `c_op_exterior`: import cost per GWh
- `gwp_op_exterior`: lifecycle GHG emissions per GWh imported
- `co2_net`: direct combustion CO2 per GWh

These are **NOT overrideable** per region in the current pipeline.

---

## 5. Other Levers (Misc.json)

| Parameter | Value | Effect |
|-----------|-------|--------|
| `elec_export_capacity` | 3 GW | Max electricity export |
| `elec_import_capacity` | 3 GW | Max electricity import |
| `import_capacity` | 4.5 GW | Max total import capacity |
| `re_share_primary` | 0.41 | Min renewable share in primary energy |
| `solar_area_ground` | 345.75 km² | Ground-mounted solar area |
| `solar_area_rooftop` | 80.49 km² | Rooftop solar area |
| `share_freight_boat_min/max` | 0.154–0.156 | Inland water freight share |
| `share_freight_train_max` | 0.277 | Rail freight share cap |

---

## 6. Observed Outputs (from `calib_2017_finland/outputs/`)

### Key Year_balance results:
| Technology | Output (GWh) |
|------------|-------------|
| NUCLEAR | 22,579 |
| HYDRO_RIVER | 26,681 |
| WIND_ONSHORE | 6,331 |
| PV (combined) | 2,416 |
| COAL_US | ~8,000–10,000 |
| CCGT | ~3,000–5,000 |

### Key Resource consumption:
| Resource | Local used (GWh) | Exterior used (GWh) |
|----------|-----------------|-------------------|
| WOOD | 66,865 | — |
| GASOLINE | — | ~15,000 |
| DIESEL | — | ~25,000 |
| LFO | — | ~20,000 |
| LFO_RE | — | ~95,000 (!) |
| GAS | — | ~28,000 |

**LFO_RE anomaly**: ~95,000 GWh of renewable LFO consumed — this is a known artifact
from not capping `LFO_RE` exterior availability (it inherited the REF default of 1e15).

---

## 7. What Was Changed After Feb14 (937940b → a20876d)

The diff between commits shows the subsequent v8-v11 calibration iterations added:
1. **`fmax_perc` column** — to constrain market shares of gas, oil, transport techs
2. **Transport constraints** — CAR_GASOLINE 0.55–0.65, CAR_DIESEL 0.3–0.4, TRUCK_DIESEL 0.9–1.0
3. **Heat sector caps** — DHN_COGEN_GAS fmax_perc=0.2, IND_BOILER_GAS fmax_perc=0.2
4. **Tighter coal** — COAL_US f_min raised to 3.5–4.5 GW
5. **Resource simplification** — Removed fossil fuel caps (back to 1e15), removed H2/AMMONIA/METHANOL overrides

---

## 8. Calibration Lever Priority (for future runs)

### High-impact (change model output structure):
1. **fmin_perc / fmax_perc on transport** — force realistic modal shares
2. **Resource exterior caps** (GAS, COAL, GASOLINE, DIESEL, LFO) — prevent unrealistic imports
3. **f_min on key generators** (NUCLEAR, HYDRO, WIND) — lock existing installed capacity

### Medium-impact (refine sector balance):
4. **fmin_perc on heat** (IND_BOILER_WOOD, DHN_COGEN_WOOD) — force biomass use in heat
5. **fmax_perc on gas/oil heat** — prevent optimizer from over-using cheap gas
6. **WOOD avail_local** — most impactful biomass lever

### Low-impact (fine-tuning):
7. **c_op_local prices** — marginal cost tweaks
8. **solar_area_ground** in Misc.json — solar potential cap
9. **elec_import/export capacity** — interconnection limits
