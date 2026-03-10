# Finland 2017 — FI/Technologies.csv Override Audit

**Date**: 2026-03-10  
**Baseline run**: `20260310_095416__stageA_verify` (code=0, optimal, score=256.1%)

## Why the 20-row FI file works

The working `Data/2017/FI/Technologies.csv` contains only 20 rows with two columns
(`f_min`, `f_max`).  All `f_min` values are zero — nothing is forced.  The `f_max`
values impose generous upper bounds (e.g. WIND_ONSHORE ≤ 35 GW, NUCLEAR ≤ 5 GW)
and disable a handful of techs irrelevant for Finland (PT/ST solar, tidal, wave,
deep geothermal).

This file works because it gives the optimizer maximum freedom.  Combined with
Stage A in-memory disabling (34 future techs set to `f_min=0, f_max=0`), the
model has enough supply-side flexibility to satisfy all demand and layer balance
constraints without conflict.

## Why larger FI restorations failed

Three attempts to inject tighter 2017-realistic bounds all caused solver
infeasibility (CPLEX code 200):

| Attempt | Rows | Forced f_min | Outcome |
|---------|------|-------------|---------|
| pre2035 backup (166 rows) | 166 | ~28 GW across all sectors | INFEASIBLE |
| FI_937940b full bounds (58 rows) | 58 | ~8 GW (elec forced, heat relaxed) | INFEASIBLE |
| Incremental (49 rows) | 49 | 8 GW (elec gen + disable + caps) | INFEASIBLE |

Root causes:

1. **Over-constrained supply**.  Forcing minimum capacities simultaneously across
   electricity, heat, and transport sectors locks in more GW than the model's
   demand and resource constraints can absorb under 12 typical days.
2. **Disabled techs remove flexibility**.  Setting 22+ future techs to zero while
   also forcing large minimums leaves no slack for the optimizer.
3. **Data mismatch**.  FI_937940b bounds were calibrated under a different
   REF_REGION cost structure and possibly different demand data.  They are not
   directly transferable without adjustment.

## Why we must proceed one constraint block at a time

Adding many capacity constraints simultaneously makes it impossible to identify
which specific bound caused infeasibility.  The methodical approach is:

1. Start from the working 20-row baseline (score ≈ 256%).
2. Add **one coherent group** of constraints (e.g. NUCLEAR bounds only).
3. Run the model and confirm code=0.
4. If infeasible, that group is the culprit — relax or remove it.
5. If feasible, record the new score and add the next group.

This bisection approach converges on the tightest feasible configuration.

## FI must remain a small override over REF_REGION

The data loading chain works as follows:

```
REF_REGION/Technologies.csv   (full: ~173 techs, all columns)
         |
    deepcopy to FI region
         |
FI/Technologies.csv            (small: overrides only)
    → pandas .update()         (overwrites only non-NaN cells)
         |
Stage A in-memory disabling    (34 techs → f_min=0, f_max=0)
         |
.dat file written to AMPL
```

**Critical**: `DataFrame.update()` never adds new index entries.  Any technology
name in FI that is *not* in REF_REGION is **silently ignored**.  FI should
therefore only list technologies that exist in REF_REGION and only override the
columns that need to differ from the reference.

The REF_REGION provides costs (`c_inv`, `c_maint`), lifetimes, efficiency (`c_p`),
and default `f_min=0 / f_max=Infinity` for most techs.  FI overrides only
capacity bounds to reflect Finnish installed capacity.

## Verified .dat values (stageA_verify run)

From `input_snapshot/reg_technologies.dat`:

| Technology | f_min | f_max | Source |
|-----------|-------|-------|--------|
| NUCLEAR | 0.0 | 5.0 | FI override |
| WIND_ONSHORE | 0.0 | 35.0 | FI override |
| HYDRO_DAM | 0.0 | 3.5 | FI override |
| HYDRO_RIVER | 0.0 | 4.0 | FI override |
| COAL_US | 0.0 | Infinity | REF_REGION default (no FI override) |
| CCGT | 0.0 | Infinity | REF_REGION default (no FI override) |
| DHN_COGEN_GAS | 0.0 | Infinity | REF_REGION default (no FI override) |
| NUCLEAR_SMR | 0.0 | 0.0 | Stage A disabled |
| CCGT_AMMONIA | 0.0 | 0.0 | Stage A disabled |
| COAL_IGCC | 0.0 | 0.0 | Stage A disabled |

**Note**: COAL_US, CCGT, and DHN_COGEN_GAS have no FI override — the optimizer
is free to use [0, Infinity].  This is why the score is 256%: the model picks
the cheapest feasible mix, not the real Finnish mix.  Future constraint blocks
will tighten these bounds toward reality.
