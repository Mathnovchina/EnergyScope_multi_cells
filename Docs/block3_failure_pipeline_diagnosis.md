# Block 3 failure-handling pipeline diagnosis

## Context

The `block3_solar_from_block2b` run (2026-03-10 15:12) produced:
- `log.txt` with `solve_result_num = 100`
- `log_fallback.txt` truncated at model compilation (213 lines)
- **No** `outputs/`, `run_metadata.json`, or `FAILURE_SUMMARY.md`

## Control-flow trace

### 1. Primary solve (barrier)

In `_solve_with_fallback()` (line 1029):

```
model.set_esom(…)        # sets up AMPL model
model.solve_esom()       # runs CPLEX barrier
model.esom.get_solve_info()  # reads [elapsed, solve_time, solve_result_num]
code = int(model.esom.t[2])  # -> code = 100
```

Code 100 means "uncertain (optimality not guaranteed)". The solve technically returned — CPLEX reported "feasible or optimal but numeric issue" with objective 5.23e+17 and severe tolerance violations (algebraic constraint violations up to 6E+05).

Since `code != 0`, execution continues to the fallback branch.

### 2. Fallback trigger (line 1053)

```python
if args.solver != "simplex" and (code == -1 or 100 <= code < 200):
```

Condition is True (solver="barrier", code=100), so fallback executes.

### 3. Fallback execution (lines 1058–1071)

```python
model.esom.ampl.close()    # close primary AMPL instance — may throw
model.set_esom(…)          # re-create AMPL instance with dual simplex opts
model.solve_esom()         # run dual simplex — 1800s time limit
model.esom.get_solve_info()
code = int(model.esom.t[2])
```

The `log_fallback.txt` has 213 lines ending at model generation (`## 402 … impose_hydro_dams_inflow`). CPLEX dual simplex solve output is **absent**. This means either:
- **A)** `model.solve_esom()` raised an exception during the dual simplex solve (e.g., CPLEX internal error, memory error, timeout handled as exception)
- **B)** `model.set_esom()` failed partway through (model compilation wrote genmod lines but crashed before solve)

Either way, an **unhandled exception** propagated out of `_solve_with_fallback`.

### 4. Exception propagation

Since `_solve_with_fallback` has **no try/except** around the fallback solve, the exception propagates to `main()`:

```python
# line 1259
solve_result_num = _solve_with_fallback(my_model, args, ampl_path, log_path)
```

This line raises the exception. Execution **never reaches** the `solve_result_num != 0` check at line 1264.

### 5. What was never called

Because the exception killed `main()` before the status check:

| Function | Called? | Why not |
|---|---|---|
| `save_metadata(…, solve_info={"status": "FAILED", …})` | **NO** | Exception before line 1271 |
| `_write_failure_summary(…)` | **NO** | Exception before line 1281 |
| `my_model.get_year_results()` | **NO** | Only reached on code=0 |
| `my_model.prints_esom(…)` | **NO** | Only reached on code=0 |
| `sys.exit(1)` | **NO** | Exception before line 1283 |

### 6. Process exit

Python's default exception handler printed a traceback to stderr and exited with code 1. However, the terminal output was truncated at ~16KB so the traceback was not visible. The terminal's `$LASTEXITCODE` may have been overwritten by subsequent commands.

## Root cause

**The fallback solve block in `_solve_with_fallback` has no exception handling.** If the fallback fails for any reason (CPLEX crash, memory, timeout-as-exception, AMPL API error), the entire run exits without writing metadata or failure summary.

## Exact failure point

The exception most likely occurred at one of:
1. `model.set_esom()` during fallback (line 1065) — model re-compilation
2. `model.solve_esom()` during fallback (line 1067) — dual simplex execution
3. `model.esom.get_solve_info()` during fallback (line 1068) — if solve never completed

The truncated `log_fallback.txt` (ending at genmod line 402/~450+) suggests the model was being generated but the AMPL process may have crashed or been killed during presolve/solve for the dual simplex attempt.

## Fix required

1. Wrap the fallback block in try/except
2. Wrap the entire solve section in `main()` with a top-level try/except
3. Ensure `save_metadata` and `_write_failure_summary` are called in all failure paths
