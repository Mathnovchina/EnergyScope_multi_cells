# Block 3a PV_UTILITY Cap Effect Audit

## 1. Disk Input Verification

**Data/2017/FI/Technologies.csv** rows:
- NUCLEAR: f_min=2.7, f_max=2.835
- WIND_ONSHORE: f_min=2.0, f_max=2.1
- WIND_OFFSHORE: f_min=0.0, f_max=0.0
- PV_UTILITY: f_min=0.0, f_max=5.0
- PV_ROOFTOP: f_min=0.02, f_max=2.0

## 2. Merged Model Input Verification

**Block 3a input_snapshot/reg_technologies.dat:**
- PV_UTILITY: f_min=0.0, f_max=60.0
- PV_ROOFTOP: f_min=0.0, f_max=15.0
- NUCLEAR: f_min=2.7, f_max=2.835
- WIND_ONSHORE: f_min=2.0, f_max=2.1
- WIND_OFFSHORE: f_min=0.0, f_max=0.0

**Block 2b input_snapshot/reg_technologies.dat:**
- PV_UTILITY: f_min=0.0, f_max=60.0
- PV_ROOFTOP: f_min=0.0, f_max=15.0
- NUCLEAR: f_min=2.7, f_max=2.835
- WIND_ONSHORE: f_min=2.0, f_max=2.1
- WIND_OFFSHORE: f_min=0.0, f_max=0.0

## 3. Technology-Level Capacities

**Block 3a outputs/Assets.csv:**
- PV_UTILITY: F=29.39, f_min=0.0, f_max=60.0, F_year=23660.92
- PV_ROOFTOP: F=6.84, f_min=0.0, f_max=15.0, F_year=5503.10
- WIND_ONSHORE: F=2.10, f_min=2.0, f_max=2.1, F_year=6325.01
- WIND_OFFSHORE: F=0.0, f_min=0.0, f_max=0.0, F_year=0.0

**Block 2b outputs/Assets.csv:**
- PV_UTILITY: F=29.39, f_min=0.0, f_max=60.0, F_year=23660.92
- PV_ROOFTOP: F=6.84, f_min=0.0, f_max=15.0, F_year=5503.10
- WIND_ONSHORE: F=2.10, f_min=2.0, f_max=2.1, F_year=6325.01
- WIND_OFFSHORE: F=0.0, f_min=0.0, f_max=0.0, F_year=0.0

## 4. Technology-Level Generation

**Block 3a outputs/Year_balance.csv:**
- PV_UTILITY: 23660.92 TWh
- PV_ROOFTOP: 5503.10 TWh
- WIND_ONSHORE: 6325.01 TWh
- WIND_OFFSHORE: 0.0 TWh
- NUCLEAR: 21084.58 TWh

**Block 2b outputs/Year_balance.csv:**
- PV_UTILITY: 23660.92 TWh
- PV_ROOFTOP: 5503.10 TWh
- WIND_ONSHORE: 6325.01 TWh
- WIND_OFFSHORE: 0.0 TWh
- NUCLEAR: 21084.58 TWh

## 5. Run-Level Outcomes

**Block 3a outputs/TotalCost.csv:**
- Objective: 49471.81

**Block 2b outputs/TotalCost.csv:**
- Objective: 49471.81

**validation_table.csv (plots/validation_2017/validation_table.csv):**
- CO2 (Model): 0.04 MtCO2

## 6. CO2 Reassessment

- Model CO2 is 0.04 MtCO2 (from validation_table.csv), not 0.00.

## 7. Interpretation

- The PV_UTILITY cap in Technologies.csv was set to f_max=5.0, but merged model input and outputs show f_max=60.0 and F=29.39, unchanged from Block 2b.
- No change in PV_UTILITY, PV_ROOFTOP, wind, or nuclear between Block 3a and Block 2b.
- CO2 is not zero, but extremely low (0.04 MtCO2).
- Therefore, Block 3a falls under:

**A. cap not applied**

## 8. Evidence Summary

- No new run was performed.
- No file modification or patch.
- All claims are strictly evidence-based.

---

This audit confirms that the PV_UTILITY cap was not actually applied in the merged model input for Block 3a. The model outputs and technology-level results are identical to Block 2b.
