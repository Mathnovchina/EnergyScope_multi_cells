# Block 3 Failure Reassessment v3

## 1. Disk Evidence
- Files present:
  - CONSTRAINT_DIFF.md
  - log.txt
  - log_fallback.txt
  - input_snapshot/reg_technologies.dat
- Files absent:
  - run_metadata.json
  - FAILURE_SUMMARY.md
  - outputs/
  - validation_plots/

## 2. Log Evidence
- Primary return code: Not explicitly shown, but log.txt indicates code likely 100 (numeric issues).
- Fallback started: log_fallback.txt exists.
- Fallback completed: log_fallback.txt contains solver output, but no explicit result code or completion message.
- Explicit infeasibility certificate: Not found.
- Explicit numeric-instability signal: log.txt shows tolerance violations and huge objective.
- Evidence of script failure before artifact writing: Absence of run_metadata.json and FAILURE_SUMMARY.md, despite fallback logs, suggests script failure or premature exit.

## 3. Electricity Technology Table (Block 3 reg_technologies.dat)

| Technology         | f_min | f_max   | Status         |
|--------------------|-------|---------|---------------|
| NUCLEAR            | 2.7   | 2.835   | capped        |
| WIND_ONSHORE       | 2.0   | 2.1     | capped        |
| WIND_OFFSHORE      | 0.0   | 0.0     | disabled      |
| PV_ROOFTOP         | 0.0   | 0.3     | capped        |
| PV_UTILITY         | 0.0   | 0.1     | capped        |
| HYDRO_DAM          | 0.0   | 3.5     | open          |
| HYDRO_RIVER        | 0.0   | 4.0     | open          |
| CCGT               | 0.0   | ∞       | open          |
| COAL_US            | 0.0   | ∞       | open          |
| BIOMASS_TO_POWER   | 0.0   | ∞       | open          |
| DHN_COGEN_GAS      | 0.0   | ∞       | open          |
| DHN_COGEN_WOOD     | 0.0   | ∞       | open          |
| DHN_COGEN_WASTE    | 0.0   | ∞       | open          |
| IND_COGEN_GAS      | 0.0   | ∞       | open          |
| IND_COGEN_WOOD     | 0.0   | ∞       | open          |
| IND_COGEN_WASTE    | 0.0   | ∞       | open          |
| DEC_COGEN_GAS      | 0.0   | ∞       | open          |
| DEC_COGEN_OIL      | 0.0   | ∞       | open          |

## 4. Diagnosis with Confidence Levels
- Proven:
  - Numeric instability occurred (log.txt warnings, code likely 100).
  - Fallback started (log_fallback.txt present).
  - Major electricity producers (CCGT, COAL_US, BIOMASS_TO_POWER, CHP) were not disabled.
- Likely:
  - Fallback did not complete successfully (no result code, no artifacts).
  - Script failed before artifact writing (missing run_metadata.json, FAILURE_SUMMARY.md).
- Possible:
  - No explicit infeasibility certificate; true infeasibility not established.
  - No compensating technologies disabled; most producers were open.
- Not established:
  - Exact fallback completion status.
  - Exact solver return code for fallback.

---

**Conclusion:**
Block 3 solar failure was most likely due to numeric instability, not proven infeasibility. Most major electricity producers remained open, with only solar and offshore wind capped/disabled. Artifact writing failed, likely due to script error after fallback.
