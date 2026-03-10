# Block 1 Checkpoint — NUCLEAR

**Run name:** `20260310_140633__block1_nuclear_v2`
**Date:** 2026-03-10

## Results

| Field | Value |
|-------|-------|
| solve_result_num | 0 (optimal) |
| score | 256.058% |
| objective | 36096.37 |

## Constraint change (from frozen baseline)

| Technology | Field | Frozen baseline | Block 1 |
|------------|-------|-----------------|---------|
| NUCLEAR | f_min | 0 | 2.7 |
| NUCLEAR | f_max | 5 | 2.835 |

No other rows changed. Stage A, REF_REGION, solver settings all unchanged.

## Rationale

Historical Finland 2017 nuclear capacity (~2.8 GW) added as a tight bound.
Feasible, ELEC_NUCLEAR error improved (6.2% → 2.4%), tiny global score
improvement (256.127% → 256.058%). Worth keeping as a foundation for further
blocks.

## File checksums

| File | Size | MD5 |
|------|------|-----|
| `Technologies.csv.frozen_baseline_20260310` | 426 | `cf915a9e5487e0ea1d6c0aaa584470f9` |
| `Technologies.csv.block1_nuclear_keep_20260310` | 427 | `6e0fd830a1a4940e1572a7fcb6a2c1da` |

## Status

**Frozen baseline remains unchanged.**
Block 1 is a kept working checkpoint built on top of it.
