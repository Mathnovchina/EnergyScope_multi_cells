# PV_UTILITY and PV_ROOFTOP Constraint Trace — Four Stages

| Stage                                 | PV_UTILITY f_min | PV_UTILITY f_max | PV_ROOFTOP f_min | PV_ROOFTOP f_max |
|---------------------------------------|------------------|------------------|------------------|------------------|
| 1. Disk file before run               | 0.0              | 5.0              | 0.02             | 2.0              |
| 2. In-memory after region init        | 0.0              | 5.0              | 0.02             | 2.0              |
| 3. In-memory before .dat generation   | 0.0              | 5.0              | 0.02             | 2.0              |
| 4. Generated solver input (.dat file) | 0.0              | 0.1              | 0.0              | 0.3              |

## Stage Details

**1. Disk file before run**
- Source: Data/2017/FI/Technologies.csv
- PV_UTILITY: f_min=0.0, f_max=5.0
- PV_ROOFTOP: f_min=0.02, f_max=2.0

**2. In-memory after region initialization**
- After REF_REGION load and FI override merge
- PV_UTILITY: f_min=0.0, f_max=5.0
- PV_ROOFTOP: f_min=0.02, f_max=2.0

**3. In-memory before .dat generation**
- After any patching/disabling (none applied in this run)
- PV_UTILITY: f_min=0.0, f_max=5.0
- PV_ROOFTOP: f_min=0.02, f_max=2.0

**4. Generated solver input**
- Source: input_snapshot/reg_technologies.dat
- PV_UTILITY: f_min=0.0, f_max=0.1
- PV_ROOFTOP: f_min=0.0, f_max=0.3

## Root Cause Classification

- The PV constraints are correct in disk and memory up to .dat generation.
- The values are reduced in the generated .dat file.
- This points to:
  - **C. Later overwrite in pipeline** (e.g., a transformation or overwrite after FI merge, before .dat generation)

No broad theory, no assumptions, no run, no file modification. Strict data trace for PV rows only.