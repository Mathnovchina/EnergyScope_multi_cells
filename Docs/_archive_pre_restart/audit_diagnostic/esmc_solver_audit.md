# ESMC Framework & Solver Options Audit

**Date:** 2026-03-03  
**Scope:** esmc/utils/esmc.py, opti_probl.py, and solver configuration  
**Purpose:** Understand how to properly configure CPLEX and diagnose tolerance issues

---

## 1. ESMC Framework Overview

### 1.1 Main Classes

| Class | File | Purpose |
|-------|------|---------|
| `Esmc` | esmc/utils/esmc.py | Main orchestrator - data loading, model setup, solving |
| `OptiProbl` | esmc/utils/opti_probl.py | AMPL interface wrapper |
| `Region` | esmc/utils/region.py | Regional data loading with override support |
| `TemporalAggregation` | esmc/preprocessing/temporal_aggregation.py | Typical days clustering |

### 1.2 Execution Flow

```
Esmc.__init__(config, nbr_td)
    ├── read_data_indep()           # Read 00_INDEP data
    ├── init_regions()               # Read regional data with overrides
    ├── init_ta(algo='kmedoid')     # Cluster typical days
    ├── print_td_data()             # Generate TD .dat files
    ├── print_data(indep=True)      # Generate all .dat files
    │
    └── set_esom(ampl_options=...)  # Create OptiProbl, set solver
            ├── OptiProbl.__init__()  # Load AMPL, read .mod/.dat
            ├── Drop unused constraints (based on config)
            │       └── f_perc=True → drop specific constraints
            │       └── f_perc=False → drop general f_min_perc, f_max_perc
            │
            └── solve_esom()         # Run optimization
                    └── OptiProbl.run_ampl()
                            └── ampl.solve()
```

### 1.3 Key Configuration Parameters

| Parameter | Type | Effect |
|-----------|------|--------|
| `gwp_limit_overall` | None or float | GWP constraint activation |
| `re_share_primary` | None or dict | RE share constraint per region |
| `f_perc` | bool | **Critical**: enables/disables fmin_perc and fmax_perc constraints |
| `year` | int | Data year (2017, 2035, 2050) |
| `nbr_td` | int | Number of typical days (default 14, Finland uses 12) |

---

## 2. Solver Options: How They Are Set

### 2.1 Default Options in esmc.py (lines 679-693)

```python
cplex_options = ['baropt',           # Use barrier algorithm
                 'predual=-1',       # Let CPLEX choose primal/dual
                 'barstart=4',       # Starting point method
                 'comptol=1e-5',     # Complementarity tolerance
                 'crossover=0',      # Disable crossover
                 'timelimit 172800', # 48-hour limit
                 'bardisplay=1',     # Display level during barrier
                 'display=2']        # Overall display level
cplex_options_str = ' '.join(cplex_options)
ampl_options = {'show_stats': 3,
                'log_file': str(self.cs_dir / 'log.txt'),
                'presolve': 200,
                'times': 1,
                'gentimes': 1,
                'cplex_options': cplex_options_str}
```

### 2.2 How to Pass Custom Options

The `set_esom()` method accepts an `ampl_options` parameter:

```python
# Example: Custom CPLEX options
custom_cplex = ['baropt',
                'predual=-1',
                'barstart=4',
                'comptol=1e-4',     # Looser tolerance
                'crossover=1',      # Enable crossover
                'barconvtol=1e-6',  # Barrier convergence tolerance
                'timelimit 72000',
                'bardisplay=2',
                'display=2']
custom_options = {
    'show_stats': 3,
    'log_file': str(my_model.cs_dir / 'log.txt'),
    'presolve': 200,
    'times': 1,
    'gentimes': 1,
    'cplex_options': ' '.join(custom_cplex)
}
my_model.set_esom(ampl_options=custom_options)
```

### 2.3 Current run_calib_manual.py Problem

The script calls `set_esom()` **without** custom options:

```python
my_model.set_esom()  # Uses defaults
```

This means it uses the hardcoded defaults including:
- `comptol=1e-5` (tight)
- `crossover=0` (disabled)

---

## 3. CPLEX Options Analysis

### 3.1 Current Default Options

| Option | Value | Meaning | Relevance |
|--------|-------|---------|-----------|
| `baropt` | - | Use barrier (interior point) method | Primary algorithm |
| `predual=-1` | Auto | CPLEX chooses primal vs dual | OK |
| `barstart=4` | 4 | Advanced starting point | OK |
| `comptol=1e-5` | 0.00001 | Complementarity tolerance | **Tight** |
| `crossover=0` | Off | No simplex crossover | **Problematic** |
| `timelimit` | 172800s | 48 hours | OK |
| `bardisplay=1` | 1 | Barrier progress every iteration | OK |

### 3.2 The Crossover Problem

**What is crossover?**
The barrier method produces a solution in the interior of the feasible region. CPLEX's crossover phase pushes this to a vertex (basic solution), eliminating residual infeasibilities.

**Why `crossover=0` causes issues:**
- Without crossover, the barrier solution may have small constraint violations
- For v9 (simple constraints): violations ~1E-02 (acceptable)
- For p13 (fmin_perc constraints): violations ~1E+05 (unacceptable)

**The fmin_perc structure is harder:**
```ampl
F_t[j] >= fmin_perc[j] * (sum_j2 F_t[j2] + sum_r R_t[r])
```
This involves comparing one technology's output to the **total sector output**, which can be 1E+05 GWh. A 0.01% error at that scale = 10 GWh violation.

### 3.3 Recommended Options to Test

| Option | Current | Recommended | Effect | Risk |
|--------|---------|-------------|--------|------|
| **crossover** | 0 | 1 or 2 | Enable simplex crossover | +Solve time |
| **comptol** | 1e-5 | 1e-4 | Looser complementarity | Minor |
| **barconvtol** | default | 1e-6 or 1e-7 | Tighter barrier convergence | +Solve time |
| **scale** | default | 1 | Enable scaling | Minor |
| **numericalemphasis** | default | 1 | Numerical stability priority | +Solve time |

---

## 4. Recommended CPLEX Strategies for Finland 2017

### Strategy A: Enable Crossover (First Try)

**Rationale:** Crossover is the missing step that converts barrier interior solution to a vertex solution.

```python
cplex_options = ['baropt',
                 'predual=-1',
                 'barstart=4',
                 'comptol=1e-5',
                 'crossover=1',      # CHANGED: Enable crossover
                 'timelimit 172800',
                 'bardisplay=1',
                 'display=2']
```

**Risk:** Solve time may increase by 50-200%  
**Should test:** YES, first priority

### Strategy B: Enable Crossover + Looser Tolerances

**Rationale:** If crossover alone doesn't help, loosen tolerances.

```python
cplex_options = ['baropt',
                 'predual=-1',
                 'barstart=4',
                 'comptol=1e-4',     # CHANGED: 10x looser
                 'barconvtol=1e-6',  # NEW: tighter barrier convergence
                 'crossover=1',      # CHANGED: Enable crossover
                 'timelimit 172800',
                 'bardisplay=1',
                 'display=2']
```

**Risk:** May accept slightly less optimal solutions  
**Should test:** YES, if A fails

### Strategy C: Add Numerical Emphasis

**Rationale:** For difficult numerical problems, CPLEX has a "numerical emphasis" mode.

```python
cplex_options = ['baropt',
                 'predual=-1',
                 'barstart=4',
                 'comptol=1e-4',
                 'crossover=1',
                 'numericalemphasis=1',  # NEW: Prioritize numerical stability
                 'timelimit 172800',
                 'bardisplay=2',
                 'display=2']
```

**Risk:** Slower, but may find feasible solutions  
**Should test:** YES, if A+B fail

### Strategy D: Switch to Dual Simplex (Last Resort)

**Rationale:** If barrier fundamentally struggles with fmin_perc structure, try simplex.

```python
cplex_options = ['dualsimplex',      # CHANGED: Use dual simplex
                 'timelimit 172800',
                 'display=2']
```

**Risk:** Much slower for large LPs, but guaranteed basic solution  
**Should test:** Only if everything else fails

---

## 5. Implementation in run_calib_manual.py

### Current Code (Problem)

```python
my_model.set_esom()  # No custom options
```

### Recommended Fix

```python
# Custom CPLEX options to improve numerical stability
cplex_options = ['baropt',
                 'predual=-1',
                 'barstart=4',
                 'comptol=1e-5',
                 'crossover=1',      # Enable crossover for vertex solution
                 'timelimit 172800',
                 'bardisplay=1',
                 'display=2']

ampl_options = {
    'show_stats': 3,
    'log_file': str(run_dir / 'log.txt'),
    'presolve': 200,
    'times': 1,
    'gentimes': 1,
    'cplex_options': ' '.join(cplex_options)
}

my_model.set_esom(ampl_options=ampl_options)
```

---

## 6. Bypassing the Framework?

### Question: Do our scripts bypass ESMC?

**Answer:** Partially, but not harmfully.

| Script | Uses Esmc class? | Uses proper flow? | Issue? |
|--------|------------------|-------------------|--------|
| run_calib_manual.py | ✓ Yes | ✓ Yes | Uses defaults |
| run_calib_case.py | ✓ Yes | ✓ Yes | OK |
| run_calib_2017.py | ✗ No (patches data directly) | ⚠ | Different approach |

The `run_calib_manual.py` and `run_calib_case.py` scripts correctly use the Esmc framework. The issue is they don't pass custom CPLEX options.

---

## 7. Summary: Solver Configuration Checklist

- [ ] Enable `crossover=1` in CPLEX options
- [ ] Pass custom options via `set_esom(ampl_options=...)`
- [ ] Consider `comptol=1e-4` if tolerance violations persist
- [ ] Add `numericalemphasis=1` for difficult cases
- [ ] Update `run_calib_manual.py` to use custom options
- [ ] Fix contradictory comment on line 305

---

*Next step: Run test with crossover=1 enabled*
