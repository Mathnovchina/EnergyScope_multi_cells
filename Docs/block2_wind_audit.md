# Block 2 Wind Audit

**Date:** 2026-03-10
**Run:** `20260310_142104__block2_wind_from_block1`

## 1. Is the WIND_ONSHORE constraint really active?

**Yes.** The constraint is fully binding:

| Source | f_min | f_max |
|--------|-------|-------|
| FI Technologies.csv (disk) | 2.0 | 2.1 |
| reg_technologies.dat (AMPL input) | 2.0 | 2.1 |
| Assets.csv (optimizer result) | F = 2.100 (at f_max) |

The FI override was correctly merged into REF_REGION. The value
propagated through the full chain: CSV → DataFrame.update() →
.dat → AMPL → solve.

## 2. Is the reported 76.41 TWh wind figure correct?

**Yes**, but it is the sum of ONSHORE + OFFSHORE, not ONSHORE alone.

| Technology | Installed (GW) | F_year (GWh) | Effective CF |
|------------|---------------|-------------|-------------|
| WIND_ONSHORE | 2.100 | 4,252 | 23.1% |
| WIND_OFFSHORE | 23.870 | 72,159 | 34.5% |
| **Total** | **25.970** | **76,411** | |

The scoring code computes:
```
ELEC_WIND = elec(["WIND_ONSHORE", "WIND_OFFSHORE"])  # sum of both
PE_WIND   = RES_WIND resource total                    # also both
```

Both metrics aggregate onshore + offshore into one number.

## 3. How is 76.41 TWh physically possible with WIND_ONSHORE at 2.1 GW?

It is physically possible because **WIND_OFFSHORE is unconstrained**.

- WIND_OFFSHORE f_max = 25.0 GW (from frozen baseline, never touched)
- The optimizer installed 23.87 GW offshore to compensate for the
  loss of cheap onshore wind
- At 23.87 GW × 34.5% CF × 8760h = 72,159 GWh — within physical limits
- WIND_ONSHORE at 2.1 GW × 23.1% CF × 8760h = 4,252 GWh — also fine

**There is no physical inconsistency.** Each technology individually
produces less than its theoretical maximum.

## 4. Where was the interpretation mistake?

The earlier interpretation assumed "76.41 TWh from 2.1 GW" implied a
single technology. In fact:

- Block 1 (no wind constraint): 35.0 GW **onshore**, 0 GW offshore → 94.9 TWh
- Block 2 (onshore capped): 2.1 GW onshore, 23.9 GW **offshore** → 76.4 TWh

The optimizer simply substituted offshore for onshore. The total wind
dropped only ~18 TWh despite a 33 GW cut in onshore capacity. The
score improved mainly because the cost shift forced more oil and CHP
into the mix (closer to Finland reality), not because wind itself
was reduced enough.

## 5. Is Block 2 safe to keep as a calibration checkpoint?

**Yes.** The run is valid:
- Solve code 0 (optimal)
- WIND_ONSHORE constraint correctly active and binding
- All generation values are physically consistent
- Score improved 256.1% → 200.4%

However, the wind calibration is **incomplete**. WIND_OFFSHORE must
also be constrained (to ~0 GW for Finland 2017, which had essentially
no offshore wind) to achieve meaningful wind error reduction.

## Capacity factor inputs

| Technology | c_p (.dat) | Mean c_p_t | Min c_p_t | Max c_p_t |
|------------|-----------|-----------|----------|----------|
| WIND_ONSHORE | 1.0 | 0.407 | 0.057 | 0.883 |
| WIND_OFFSHORE | 1.0 | 0.433 | 0.066 | 0.966 |

With c_p = 1.0, the model uses F_t ≤ F × c_p_t directly. The time
series have 288 values (24 hours × 12 typical days). Values are
reasonable for Nordic wind profiles.

## Recommendation

Before proceeding to Block 3 (HYDRO), add WIND_OFFSHORE constraint
to the same block:

```
WIND_OFFSHORE: f_min=0.0, f_max=0.0
```

Finland had no offshore wind capacity in 2017. This should be added
as a Block 2b or folded into a revised Block 2.
