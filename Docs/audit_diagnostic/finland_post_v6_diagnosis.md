# Finland 2017 Post-v6 Calibration Diagnosis

**Created:** 2026-02-27  
**v6 Final Block:** Block 6 (ElecMix)  
**Objective:** 2.12e+07 MEUR  
**Solver Status:** solve_result_num=-1 (feasible with numerical issues)

---

## 1. Executive Summary

The v6 calibration made **significant progress** compared to v5_fperc, but several major mismatches remain. The model still has:

1. **URANIUM/Nuclear overconsumption** — 196K GWh vs 65K GWh target (+201% overshoot)
2. **Oil still too high** — 125K GWh vs 96K GWh target (+30% overshoot)
3. **Wood/Biomass still too low** — 51K GWh vs 105K GWh target (-52% gap)
4. **Constraint violations persist** — NUCLEAR at 5.93 GW vs f_max=2.8 GW (112% violation)
5. **Future technologies deployed** — H2_ELECTROLYSIS, POWER_TO_*, BIOWASTE_TO_* active despite being set to f_max=100 (meant to be disabled)

The core problem is **solver degeneracy has NOT been fully resolved** — technologies with f_max=100 are still deploying at near-100 GW because the barrier solver tolerances allow violations up to ~200 GW on bounds.

---

## 2. Main Remaining Mismatches

### 2.1 Primary Energy by Resource (GWh)

| Resource | Reality (2017) | v6 Block6 | Gap (GWh) | Gap (%) | Status |
|----------|---------------|-----------|-----------|---------|--------|
| **URANIUM** | 65,000 | 195,788 | +130,788 | **+201%** | **CRITICAL** |
| **WOOD** | 105,000 | 50,581 | -54,419 | **-52%** | **CRITICAL** |
| **TOTAL_OIL** | 96,000 | 125,172 | +29,172 | **+30%** | HIGH |
| LFO | ~50,000 | 78,806 | +28,806 | +58% | HIGH |
| DIESEL | ~25,000 | 24,981 | -19 | -0.1% | ✅ OK |
| GASOLINE | ~16,000 | 15,808 | -192 | -1% | ✅ OK |
| JET_FUEL | ~5,000 | 5,577 | +577 | +12% | OK |
| **GAS** | 25,000 | 22,002 | -2,998 | -12% | OK |
| **COAL** | 50,000 | 18,370 | -31,630 | **-63%** | HIGH |
| HYDRO | 15,000 | 15,395 | +395 | +3% | ✅ Excellent |
| WIND | 5,000 | 5,925 | +925 | +19% | OK |
| SOLAR | 100 | 5,145 | +5,045 | +5045% | HIGH |

### 2.2 Electricity Mix (TWh)

| Source | Reality (2017) | v6 Block6 | Gap (TWh) | Gap (%) | Status |
|--------|---------------|-----------|-----------|---------|--------|
| **Nuclear** | 21.6 | **72.4** | +50.8 | **+235%** | **CRITICAL** |
| Hydro | 14.6 | 15.4 | +0.8 | +5% | ✅ Excellent |
| Wind | 4.8 | 5.9 | +1.1 | +23% | OK |
| **Biomass CHP** | 11.0 | ~6.0 | -5.0 | **-45%** | HIGH |
| Coal CHP | 9.0 | ~0.1 | -8.9 | **-99%** | **CRITICAL** |
| Gas CCGT | 3.7 | ~3.0 | -0.7 | -19% | OK |
| **Solar** | 0.1 | 0.6 | +0.5 | +500% | HIGH |

### 2.3 Key Technology Deployments (GW)

| Technology | F (Model) | f_max (Input) | f_min (Input) | Violation |
|------------|-----------|---------------|---------------|-----------|
| **NUCLEAR** | 5.93 | 2.80 | 2.76 | **+112%** |
| WIND_ONSHORE | 2.18 | 1.70 | 1.50 | +28% |
| WIND_OFFSHORE | 0.15 | 0.03 | 0.00 | +389% |
| PV_ROOFTOP | 0.22 | 0.05 | 0.02 | +344% |
| PV_UTILITY | 0.06 | 0.02 | 0.00 | +178% |
| CCGT | 1.66 | 1.20 | 0.60 | +39% |
| COAL_US | 5.84 | 4.50 | 3.50 | +30% |
| HYDRO_DAM | 1.74 | 1.30 | 1.10 | +34% |
| HYDRO_RIVER | 2.90 | 2.10 | 1.90 | +38% |
| CARGO_FUELCELL_LH2 | 152.1 | 100.0 | 0.00 | +52% |

### 2.4 "Future" Technologies That Should Be Disabled (f_max=100 in v6)

Several technologies meant to be capped at negligible levels (f_max=100 GW as "disabled") are deploying at massive scale:

| Technology | F (GW) | F_year (GWh/y) | Problem |
|------------|--------|----------------|---------|
| CCGT_AMMONIA | 99.3 | 198 | Should be 0 |
| COAL_IGCC | 99.4 | 117 | Should be 0 |
| BIOMASS_TO_POWER | 99.4 | 68 | Should be 0 |
| DEC_ADVCOGEN_GAS | 99.3 | 12,485 | Should be 0 |
| DEC_ADVCOGEN_H2 | 99.8 | 46 | Should be 0 |
| H2_ELECTROLYSIS | 99.2 | 7,548 | Should be 0 |
| SYN_METHANATION | 99.2 | 14,832 | Should be 0 |
| POWER_TO_DIESEL | 99.5 | 9,935 | Should be 0 |
| All BIOMASS_TO_* | ~99 | ~60 each | Should be 0 |

**Root cause**: setting `f_max=100` does NOT disable a technology — it caps it at 100 GW, which the solver happily uses. Block 0 strategy said to set `f_max=0` for these, but the actual implementation set `f_max=100`.

---

## 3. Ranked Mismatches by Priority

| Rank | Issue | Quantitative Gap | System Impact | Ease of Fix | Score |
|------|-------|------------------|---------------|-------------|-------|
| 1 | **NUCLEAR/URANIUM overproduction** | +201% | Distorts entire electricity mix | Medium (solver issue) | **10/10** |
| 2 | **WOOD/Biomass gap** | -52% | Underestimates Finnish biomass | Medium (fmin_perc) | **9/10** |
| 3 | **Future techs not disabled** | 99 GW deployments | Creates unrealistic flows | Easy (f_max=0) | **9/10** |
| 4 | **COAL gap** | -63% | Underestimates Finnish CHP | Medium (fmin_perc) | **8/10** |
| 5 | **LFO/Oil overuse** | +30% | CO2 too high | Easy (avail cap) | **7/10** |
| 6 | **Solar overproduction** | +5000% | Minor energy impact | Easy (f_max) | **5/10** |
| 7 | **Wind overproduction** | +19% | Minor | Already tight | **3/10** |

---

## 4. Root Cause Analysis

### 4.1 NUCLEAR/URANIUM (+201%)

**Symptom**: NUCLEAR at 5.93 GW despite f_max=2.8 GW.

**Root cause**: **Solver tolerance violation**
- CPLEX barrier solver with `crossover=0` reports: "variable bounds MaxAbs 2E+02, MaxRel 1E+01"
- This means bounds can be violated by up to 200 units (GW)
- NUCLEAR is cheap (URANIUM=0.005 €/GWh) so the optimizer maximizes it

**Evidence**:
```
URANIUM avail_exterior = 62,000 GWh (input)
URANIUM R_year_exterior = 195,788 GWh (output) — 216% of cap!
```

**Fix options**:
1. **Enable crossover** (`crossover=1`) — forces exact feasibility but may take longer
2. **Add explicit penalty** for overproduction (not clean)
3. **Hard-code URANIUM avail_exterior even tighter** as a workaround

### 4.2 WOOD/Biomass (-52%)

**Symptom**: Only 50.6K GWh wood used vs 105K target.

**Root cause**: **Insufficient fmin_perc forcing**

Current fmin_perc values:
| Technology | fmin_perc | Effect |
|------------|-----------|--------|
| IND_BOILER_WOOD | 0.30 | 30% of industrial heat |
| IND_COGEN_WOOD | 0.15 | 15% of industrial heat |
| DHN_COGEN_WOOD | 0.30 | 30% of DHN heat |
| DEC_BOILER_WOOD | 0.15 | 15% of decentralized heat |

These are hitting their floors (technologies at ~f_max or near it), but the total sector demands multiply to only ~50K GWh wood. To reach 105K, either:
1. **Increase fmin_perc** further (risky — may cause infeasibility)
2. **Add more wood-consuming technologies** (e.g., DHN_BOILER_WOOD fmin_perc)
3. **Reduce competing fuels** (GAS, COAL caps already tight)

### 4.3 Future Technologies Still Active

**Symptom**: Technologies set to `f_max=100` deploy at 99+ GW.

**Root cause**: Block 0 strategy said to set `f_max=0`, but implementation set `f_max=100` (typo or misunderstanding). The solver interprets 100 as "100 GW cap" and deploys up to that.

**Evidence** (from reg_technologies.dat):
```
FI  H2_ELECTROLYSIS  ...  f_max  100.0
FI  SYN_METHANATION  ...  f_max  100.0
FI  CCGT_AMMONIA     ...  f_max  100.0
```

These should all be `f_max=0.0` for 2017 Finland.

### 4.4 COAL Gap (-63%)

**Symptom**: Only 18.4K GWh coal used vs 50K target.

**Root cause**: 
- COAL_US at 5.84 GW produces electricity, not heat
- Coal CHP (DHN_COGEN_COAL, IND_COGEN_COAL) have fmin_perc=0.2 and 0.0
- Most coal in Finland 2017 was used for **CHP** (both heat and electricity), not pure power

**Fix**: Increase `fmin_perc` for DHN_COGEN_COAL and IND_COGEN_COAL.

### 4.5 LFO/Oil Overuse (+30%)

**Symptom**: 78.8K GWh LFO used (cap is 80K).

**Root cause**: CARGO_LFO dominates shipping (1.63M GWh output for 149K Mtkm demand). The LFO cap of 80K is still too generous.

**Evidence**:
- SHIPPING demand = 148,985 Mtkm
- CARGO_LFO efficiency = 0.02 (uses 46 GWh LFO per GW of capacity)
- Model uses 35.4K GWh LFO just for shipping

---

## 5. Proposed Next Calibration Blocks

Based on the diagnosis, the next calibration iteration (v7) should be split into the following blocks:

### Block A: Fix Future Technology Disabling (CRITICAL)

**Goal**: Set f_max=0 for all technologies that did not exist in Finland 2017.

**Files to modify**: `Data/2017/FI/Technologies.csv`

**Changes**:
| Technology | Current f_max | New f_max | Rationale |
|------------|---------------|-----------|-----------|
| CCGT_AMMONIA | 100 | 0 | Not operational in 2017 |
| COAL_IGCC | 100 | 0 | Not operational in 2017 |
| BIOMASS_TO_POWER | 100 | 0 | Not operational in 2017 |
| H2_ELECTROLYSIS | 100 | 0 | H2 electrolysis negligible in 2017 |
| H2_NG | 100 | 0 | Not operational in 2017 |
| H2_BIOMASS | 100 | 0 | Not operational in 2017 |
| SYN_METHANATION | 100 | 0 | Not operational in 2017 |
| BIOMETHANATION_* | 100 | 0 | Not operational in 2017 |
| BIOMASS_TO_METHANE | 100 | 0 | Not operational in 2017 |
| BIOWASTE_TO_METHANE | 100 | 0 | Not operational in 2017 |
| BIOMASS_TO_GASOLINE/DIESEL/JET_FUEL/LFO | 100 | 0 | Not operational in 2017 |
| BIOWASTE_TO_GASOLINE/DIESEL/JET_FUEL/LFO | 100 | 0 | Not operational in 2017 |
| DIESEL_TO_JET_FUEL | 100 | 0 | Not operational in 2017 |
| ATM_CCS | 100 | 0 | Not operational in 2017 |
| INDUSTRY_CCS | 100 | 0 | Not operational in 2017 |
| SYN_METHANOLATION | 100 | 0 | Not operational in 2017 |
| METHANE_TO_METHANOL | 100 | 0 | Not operational in 2017 |
| BIOMASS_TO_METHANOL | 100 | 0 | Not operational in 2017 |
| BIOWASTE_TO_METHANOL | 100 | 0 | Not operational in 2017 |
| HABER_BOSCH | 100 | 0 | Not operational in 2017 |
| POWER_TO_GASOLINE/DIESEL/JET_FUEL/LFO | 100 | 0 | Not operational in 2017 |
| H2_TO_GASOLINE/DIESEL/JET_FUEL/LFO | 100 | 0 | Not operational in 2017 |
| AMMONIA_TO_H2 | 100 | 0 | Not operational in 2017 |
| GAS_TO_HVC | 100 | 0 | Not operational in 2017 |
| BIOMASS_TO_HVC | 100 | 0 | Not operational in 2017 |
| METHANOL_TO_HVC | 100 | 0 | Not operational in 2017 |
| DEC_ADVCOGEN_GAS | 100 | 0 | Future technology |
| DEC_ADVCOGEN_H2 | 100 | 0 | Future technology |
| DEC_THHP_GAS | 100 | 0 | Future technology (keep for now, produces heat) |
| CAES | 100 | 0 | No CAES in Finland 2017 |
| GAS_PIPELINE | 100 | 0 | Single-region model |
| GAS_SUBSEA | 100 | 0 | Single-region model |
| H2_RETROFITTED | 100 | 0 | Future technology |
| H2_NEW | 100 | 0 | Future technology |
| H2_SUBSEA_RETRO | 100 | 0 | Future technology |
| H2_SUBSEA_NEW | 100 | 0 | Future technology |
| CARGO_LNG | 100 | 0 | Minimal in 2017 |
| CARGO_METHANOL | 100 | 0 | Not operational in 2017 |
| CARGO_AMMONIA | 100 | 0 | Not operational in 2017 |
| CARGO_FUELCELL_LH2 | 100 | 0 | Not operational in 2017 |
| CARGO_FUELCELL_AMMONIA | 100 | 0 | Not operational in 2017 |
| CARGO_RETRO_METHANOL | 100 | 0 | Not operational in 2017 |
| CARGO_RETRO_AMMONIA | 100 | 0 | Not operational in 2017 |
| BOAT_FREIGHT_NG | 100 | 0 | Negligible in 2017 |
| BOAT_FREIGHT_METHANOL | 100 | 0 | Not operational in 2017 |
| BUS_COACH_HYDIESEL | 100 | 0 | Negligible in 2017 |
| BUS_COACH_CNG_STOICH | 100 | 0 | Negligible in 2017 |
| CAR_NG | 100 | 0 | Negligible in 2017 |
| TRUCK_METHANOL | 50000 | 0 | Not operational in 2017 |
| TRUCK_NG | 50000 | 0 | Negligible in 2017 |

**Classification**: Numerical stabilization + Historical realism

**Expected effect**:
- Eliminate 99-GW phantom deployments
- Reduce artificial H2 production/consumption
- More realistic fuel balance

**Risks**: Low — these technologies contribute nothing to 2017 operations.

---

### Block B: Nuclear/Uranium Hard Cap (CRITICAL)

**Goal**: Force NUCLEAR to stay within bounds by tightening URANIUM constraint.

**Files to modify**: `Data/2017/FI/Resources.csv`

**Changes**:
| Resource | Current avail_exterior | New avail_exterior | Rationale |
|----------|------------------------|-------------------|-----------|
| URANIUM | 62,000 | **56,000** | 2.8 GW × 0.849 cf × 8760h = 20.8 TWh elec × 2.7 = 56 TWh thermal |

**Alternative**: Enable crossover in solver options (`crossover=1`).

**Classification**: Historical realism

**Expected effect**:
- NUCLEAR electricity drops from 72 TWh to ~21 TWh
- URANIUM consumption drops from 196K to ~56K GWh
- Other electricity sources must compensate

**Risks**: Medium — may stress other electricity techs.

---

### Block C: Biomass Forcing Increase (HIGH)

**Goal**: Push wood consumption closer to 105K GWh target.

**Files to modify**: `Data/2017/FI/Technologies.csv`

**Changes**:
| Technology | Current fmin_perc | New fmin_perc | Expected Wood (GWh) |
|------------|-------------------|---------------|---------------------|
| IND_BOILER_WOOD | 0.30 | **0.40** | +4,000 |
| IND_COGEN_WOOD | 0.15 | **0.25** | +3,500 |
| DHN_COGEN_WOOD | 0.30 | **0.45** | +5,000 |
| DHN_BOILER_WOOD | 0.00 | **0.15** | +2,000 |
| DEC_BOILER_WOOD | 0.15 | **0.30** | +5,000 |

**Estimated total additional wood**: ~20,000 GWh → brings total to ~70K GWh

**Classification**: Calibration forcing

**Expected effect**:
- Wood consumption increases to ~70K GWh
- Still ~35K gap to 105K target (may need further iteration or demand review)

**Risks**: Medium — may create sector infeasibility if demands are incompatible.

---

### Block D: Coal CHP Rebalancing (HIGH)

**Goal**: Push coal use toward CHP (not just COAL_US power).

**Files to modify**: `Data/2017/FI/Technologies.csv`

**Changes**:
| Technology | Current fmin_perc | New fmin_perc | Rationale |
|------------|-------------------|---------------|-----------|
| DHN_COGEN_COAL | 0.20 | **0.35** | More coal CHP for DHN |
| IND_COGEN_COAL | 0.00 | **0.15** | Some coal CHP for industry |

**Classification**: Calibration forcing

**Expected effect**:
- COAL consumption increases via CHP
- Some electricity from coal CHP instead of pure coal power
- Better match to Finnish 2017 coal structure

**Risks**: Low — coal CHP is well-documented in Finland history.

---

### Block E: LFO/Shipping Cap Tightening (MEDIUM)

**Goal**: Reduce LFO overuse in shipping.

**Files to modify**: `Data/2017/FI/Resources.csv`

**Changes**:
| Resource | Current avail_exterior | New avail_exterior | Rationale |
|----------|------------------------|-------------------|-----------|
| LFO | 80,000 | **50,000** | Finland total oil ~96K, LFO should be ~50K |

**Classification**: Historical realism

**Expected effect**:
- LFO consumption drops to ~50K GWh
- Total oil closer to 96K target

**Risks**: Medium — may stress shipping demand satisfaction.

---

### Block F: Solar Cap Tightening (LOW)

**Goal**: Reduce solar overproduction.

**Files to modify**: `Data/2017/FI/Technologies.csv`

**Changes**:
| Technology | Current f_max | New f_max | Rationale |
|------------|---------------|-----------|-----------|
| PV_ROOFTOP | 0.05 | **0.04** | Still allows ~50 MW |
| PV_UTILITY | 0.02 | **0.01** | Reduce utility solar |

Note: The solver violates these bounds anyway (PV_ROOFTOP at 0.22 vs 0.05 f_max), so this may have limited effect until solver tolerance is fixed.

**Classification**: Historical realism

**Expected effect**: Minor — depends on solver tolerance fix.

---

## 6. Recommended First Block to Test

**Recommendation: Block A (Fix Future Technology Disabling)**

**Rationale**:
1. **Highest certainty of improvement** — these are clearly wrong (99 GW of H2 electrolysis in 2017 Finland is absurd)
2. **No risk of infeasibility** — removing future techs just shifts load to existing ones
3. **Required foundation** — without disabling future techs, other calibration is meaningless
4. **Easy to implement** — just change f_max from 100 to 0
5. **Quick to validate** — check that F=0 for all disabled techs

**Expected outcomes**:
- No deployment of H2, ammonia, methanol production
- No synthetic fuel production
- Shipping relies only on CARGO_LFO (as it should for 2017)
- Clearer view of remaining calibration gaps

---

## 7. Secondary Recommendation: Solver Tolerance Fix

After Block A, the **solver tolerance issue** should be addressed. Options:

1. **Enable crossover** (`crossover=1`) — forces simplex cleanup after barrier, ensuring exact feasibility
2. **Tighten barrier tolerance** (`comptol=1e-8`) — may help but not guaranteed
3. **Switch to simplex** (`alg:simplex`) — exact but potentially slower

This should be tested alongside Block A to see if constraint violations disappear.

---

## 8. Appendix: Reality Targets (Finland 2017)

| Category | Value | Unit | Source |
|----------|-------|------|--------|
| Total Primary Energy | ~1,350 | PJ | Statistics Finland |
| Wood/Biomass | 105 | TWh | IEA / Statistics Finland |
| Oil Products | 96 | TWh | IEA |
| Natural Gas | 25 | TWh | IEA |
| Coal + Peat | 50 | TWh | IEA (includes peat) |
| Nuclear (thermal) | 65 | TWh | IAEA (Olkiluoto 1+2, Loviisa 1+2) |
| Hydro | 15 | TWh | Fingrid |
| Wind | 5 | TWh | Fingrid |
| Solar | 0.1 | TWh | Fingrid |
| Net Electricity Import | 20 | TWh | Fingrid |
| CO2 Emissions | 42 | MtCO2 | UNFCCC |

---

**Next steps**:
1. Apply Block A (disable future technologies)
2. Run model
3. Compare vs v6 and reality
4. Report on remaining gaps
5. Decide on Block B (Nuclear cap) or Block C (Biomass forcing)
