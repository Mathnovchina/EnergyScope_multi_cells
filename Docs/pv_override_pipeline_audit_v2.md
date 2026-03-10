# PV Override Pipeline Audit v2

## 1. Separation of Override Mechanisms

### A. Direct FI File Override Path
- **File:** Data/2017/FI/Technologies.csv
- **Load Function:** `Region.read_tech()` ([esmc/utils/region.py](esmc/utils/region.py#L120-L140))
  - Reads Technologies.csv for FI region at run start.
  - If `ref_region`, loads REF_REGION first, then updates with FI-specific rows.
- **Run Initialization:** At each model run, `Region` is re-initialized and reads the current disk state of Technologies.csv.

### B. In-Memory Patch Path
- **Patch Application Function:** `apply_patches()` ([scripts/run_calib_manual.py](scripts/run_calib_manual.py#L301-L400))
  - Applies CSV patch files to region DataFrames after initial load.
  - Only affects in-memory DataFrames, not disk files.
- **Patch Format:** CSV specifying file, parameter, technology/resource, and value.

## 2. Mechanism Used in Block 3a
- **Evidence:**
  - Prior runs showed direct edits to Data/2017/FI/Technologies.csv for NUCLEAR, WIND_ONSHORE, WIND_OFFSHORE propagated to merged input and model.
  - Block 3a instructions and audit focused on direct disk edits, not patch CSVs.
- **Conclusion:** Block 3a was based on direct edits to Data/2017/FI/Technologies.csv.
- **Patch mechanism:** Not used in Block 3a (no evidence of patch CSV or patch list).

## 3. PV Problem Reassessment
- **Disk edits are NOT ignored:** Proven by NUCLEAR/WIND propagation.
- **Classification:**
  - **D. Patch path and direct-file path were conflated in prior diagnosis.**
  - **A. Direct FI edit may not have been present on disk at run start (uncertain, needs disk snapshot evidence).**
  - **B. Row name mismatch possible (e.g., PV_UTILITY not matching DataFrame index).**
  - **C. FI override could have been overwritten later in pipeline (e.g., REF_REGION update or other transform).**
- **PV did not propagate:** Evidence from merged input/reg_technologies.dat and model output.

## 4. Concrete Evidence
- **region.py:**
  - [read_tech()](esmc/utils/region.py#L120-L140): Loads Technologies.csv for FI, updates from disk.
  - REF_REGION logic: Loads reference, then updates with FI-specific rows.
- **run_calib_manual.py:**
  - [apply_patches()](scripts/run_calib_manual.py#L301-L400): Patch system, not used in Block 3a.
- **NUCLEAR/WIND propagation:**
  - Direct disk edits to Technologies.csv changed merged input and model in prior runs.
- **PV did not propagate:**
  - Block 3a audit showed PV_UTILITY cap missing in merged input/reg_technologies.dat and model output.

## 5. Summary

### What is Proven
- Disk edits to Data/2017/FI/Technologies.csv are read at run start and propagate to merged input for NUCLEAR/WIND.
- Block 3a used direct FI file edits, not patch CSVs.
- PV_UTILITY override did not propagate in Block 3a.

### What is Likely
- Diagnosis previously conflated patch and direct-file mechanisms (classification D).
- PV issue may involve row name mismatch or later overwrite (classification B/C).

### What is Not Established
- Exact cause of PV_UTILITY override loss: whether due to disk state, row mismatch, or later overwrite.
- Whether direct FI edit was present on disk at run start (needs disk snapshot).

---
**No run, no patch, no file modification. Strict evidence-based audit.**