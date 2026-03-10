# Model Mechanics Short Note

- Demands are enforced via `end_uses_t`: hourly demand for each layer is strictly required, mapped from annual values and time series.
- Electricity and heat balances are enforced via `layer_balance`: for each layer and hour, the sum of technology outputs, resource flows, storage, and demand must be zero.
- `F` (installed capacity), `F_t` (hourly operation), `c_p` (annual capacity factor), `c_p_t` (hourly capacity factor), `f_min`, `f_max` interact to strictly bound both annual and hourly production.
- CHP coupling: technologies with positive `layers_in_out` for both electricity and heat co-produce both, and their minimum/maximum capacities are enforced for both outputs.
- Annual production is constrained by `capacity_factor` (sum of F_t over the year ≤ F × c_p × total_time); hourly production is constrained by `capacity_factor_t` (F_t ≤ F × c_p_t).
- Strict enforcement means any infeasibility in supply or demand (e.g., solar caps with unchanged demand) leads directly to solver failure.
- This changes interpretation of the solar failure: it is not a soft constraint or slack, but a hard infeasibility when supply cannot meet demand under the imposed caps.
