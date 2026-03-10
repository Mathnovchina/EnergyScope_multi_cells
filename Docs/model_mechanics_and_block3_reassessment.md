# Model Mechanics and Block 3 Reassessment

## Evidence-Based Answers to Six Model Questions

---

### 1. Demand Enforcement (end_uses_t)
- Hourly demand for each layer is strictly enforced via the `end_uses_t` constraint.
- Electricity demand (annual: 43.0 TWh) is mapped to hourly values using `electricity_time_series`.
- No relaxation or softening: demand must be met every hour.

### 2. Layer Balance
- The `layer_balance` constraint ensures that, for each layer and hour, the sum of technology outputs, resource flows, storage in/out, and demand is exactly zero.
- Strict equality: any infeasibility in supply or demand propagates directly to solver failure.

### 3. F, F_t, c_p, c_p_t
- `F`: Installed capacity (GW), bounded by `f_min` and `f_max`.
- `F_t`: Hourly operation (GW), bounded by `capacity_factor_t` (hourly) and `capacity_factor` (annual).
- `c_p`, `c_p_t`: Capacity factors (annual/hourly), controlling maximum output.
- Block 3 PV constraints: PV_ROOFTOP f_max=0.3, PV_UTILITY f_max=0.1, strictly enforced.

### 4. Generation Limits
- `size_limit` enforces f_min/f_max for each technology.
- `capacity_factor_t` and `capacity_factor` enforce hourly and annual adequacy.
- `f_max_perc` and `f_min_perc` enforce share-of-output constraints for each technology.

### 5. Annual vs Hourly Adequacy
- Hourly adequacy: demand must be met every hour (no slack).
- Annual adequacy: total output cannot exceed annual capacity factor times installed capacity.
- Both are enforced simultaneously; failure in either leads to infeasibility.

### 6. Failure Mechanism
- Diagnostic run failed due to strict PV caps (f_max=0.1/0.3) and unchanged demand, with no compensating technologies enabled.
- Automatic infeasibility diagnostics show available electricity producers are limited, but demand remains unchanged.
- Solver (CPLEX barrier) failed to find a feasible solution, as evidenced by FAILURE_SUMMARY.md and CONSTRAINT_DIFF.md: 153 technology constraints differ from baseline, PV caps are much lower, and nuclear is capped.
- No evidence of model drift or uncontrolled file edits; all constraints are enforced as written.

---

**Conclusion:**
Block 3 solar failure is a direct result of strict PV caps and unchanged demand, with no compensating supply. All constraints are rigorously enforced, and the failure is fully evidenced by model files and run artifacts.
