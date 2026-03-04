# Data/2017_alt_from2035tech/

**Alternative Finland 2017 data preset using 2035 technology structure.**

## What this is

This directory is a copy of `Data/2017/` with two key replacements:
- `FI/Technologies.csv` → replaced with `Data/2035/FI/Technologies.csv`
- `02_REF_REGION/Technologies.csv` → replaced with `Data/2035/02_REF_REGION/Technologies.csv`

Everything else (demands, resources, time series, misc, INDEP data, exchange data) 
remains from 2017.

## Why

The original 2017/FI/Technologies.csv was created by copy-pasting from 2035 and
extensive hand-editing, accumulating:
- 166 rows (vs 20 in 2035 FI)
- fmin_perc/fmax_perc columns (not present in 2035)
- f_max = 1e15 values causing 15 orders of magnitude variable range
- Future technologies that don't belong in 2017

This preset provides a clean starting point with the simpler 2035 technology
structure. It's useful for testing whether the technology file is the source
of solver difficulties.

## How to use

To run with this data, you would need to either:
1. Temporarily rename `Data/2017/` and `Data/2017_alt_from2035tech/` to `Data/2017/`
2. Or modify the ESMC config to point to this directory

**Caution:** The 2035 technologies may not have appropriate f_min/f_max values
for 2017 Finland (e.g., NUCLEAR capacity should be ~2.5-2.8 GW for 2017, not
4.36-5.0 GW as in 2035). You will likely need patches to adjust key capacities.

## Created

2026-03-04, as part of the manual calibration workflow cleanup.
