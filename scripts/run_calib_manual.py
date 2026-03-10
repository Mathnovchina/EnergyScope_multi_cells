#!/usr/bin/env python3
"""
==========================================================================
  Manual Calibration Runner — Finland 2017 (ESMC Framework)
==========================================================================

ONE command to run the EnergyScope model for Finland 2017, score it, and
generate validation plots.  Follows the style of run_esmc_simple_3c 1.py.

Pipeline:
  1. Initialize ESMC with config
  2. Read data  (from standard Data/2017  or --data-dir override)
  3. Apply patches in-memory  (Data/ CSV files are NEVER touched)
  4. Temporal aggregation  (algo='read': reuse frozen TDs)
  5. Generate .dat files + snapshot them to run_dir/input_snapshot/
  6. Solve  (barrier+crossover=1, auto-fallback to dual simplex)
  7. Extract results, score, validate plots, metadata

Usage examples:
  # Vanilla baseline — no patches
  python scripts/run_calib_manual.py -n baseline

  # With a patch file
  python scripts/run_calib_manual.py -n test_nuclear \\
      -p calibration/patches/nuclear_cap.csv

  # Dry-run — show patch effects without solving
  python scripts/run_calib_manual.py -n test_nuclear \\
      -p calibration/patches/nuclear_cap.csv --dry-run

  # Disable fmin_perc / fmax_perc constraints
  python scripts/run_calib_manual.py -n test_no_fperc --no-fperc

  # Alternative data directory
  python scripts/run_calib_manual.py -n test_alt \\
      --data-dir Data/2017_alt_from2035tech

  # Force dual simplex (clearer infeasibility diagnosis)
  python scripts/run_calib_manual.py -n diag_simplex --solver simplex

Patch CSV format (one change per row):
  file,parameter,technology_or_resource,value
  Technologies.csv,f_max,NUCLEAR,8000
  Resources.csv,avail_local,COAL,50000

Output:
  case_studies/FI/manual_runs/<YYYYMMDD_HHMMSS>__<run_name>/
    outputs/          — standard ESMC outputs
    input_snapshot/   — frozen copy of every .dat fed to AMPL
    validation_plots/ — PE, Elec, CO2, error charts + markdown report
    run_metadata.json — full reproducibility record
    log.txt           — AMPL/CPLEX log

Data safety:
  Data/2017/ is NEVER modified.  All patches are applied to in-memory
  DataFrames after init_regions().  The .dat files are generated from
  those DataFrames, snapshotted, and only then fed to AMPL.

Solver strategy:
  Default uses CPLEX barrier with crossover=1 (not crossover=0 which was
  the old ESMC default and caused solve_result_num=-1 with fmin_perc).
  If barrier+crossover fails, automatically retries with dual simplex to
  provide a clear infeasibility certificate.
"""

import argparse
import copy
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from esmc import Esmc
from esmc.common import CSV_SEPARATOR
from esmc.utils.region import Region

CALIBRATION_DIR = REPO_ROOT / "calibration"
RANKINGS_CSV = CALIBRATION_DIR / "run_rankings.csv"
REALITY_REF = CALIBRATION_DIR / "reality" / "finland_2017_reference.csv"

# ---------------------------------------------------------------------------
# Reality targets for scoring  (14 metrics, same as score_all_fi_runs.py)
# Keys  =  metric name
# Values = (reality_value_TWh_or_MtCO2, weight)
# ---------------------------------------------------------------------------
REALITY_TARGETS = {
    "PE_BIOMASS":        (100.0, 1.5),
    "PE_OIL":            (82.0,  1.5),
    "PE_GAS":            (20.0,  1.0),
    "PE_COAL":           (35.0,  1.5),
    "PE_NUCLEAR":        (65.0,  1.0),
    "PE_HYDRO":          (15.0,  0.8),
    "PE_WIND":           (5.0,   0.8),
    "ELEC_NUCLEAR":      (21.6,  1.5),
    "ELEC_HYDRO":        (14.6,  1.2),
    "ELEC_WIND":         (4.8,   1.0),
    "ELEC_CHP":          (20.735, 1.2),
    "ELEC_CONDENSATION": (3.284, 0.8),
    "ELEC_SOLAR":        (0.044, 0.3),
    "CO2":               (41.2,  2.0),
}


# =========================================================================
# Finland 2017 technology disabling (validated baseline)
# =========================================================================
# These technologies were disabled after Layers_in_out dependency analysis
# to remove post-2017 pathways while preserving solver feasibility.
# Implemented on 2026-03-10.
#
# Strategy:
#   - Stage A: validated and applied permanently (34 techs)
#   - Stage B/C: kept for future experiments, commented out by default
#
# DO NOT remove without re-checking layer dependencies.
# =========================================================================

DISABLED_TECH_STAGE_A = [
    # --- Synthetic fuel routes (16) ---
    "H2_TO_GASOLINE", "H2_TO_DIESEL", "H2_TO_JET_FUEL", "H2_TO_LFO",
    "POWER_TO_GASOLINE", "POWER_TO_DIESEL", "POWER_TO_JET_FUEL", "POWER_TO_LFO",
    "BIOMASS_TO_GASOLINE", "BIOMASS_TO_DIESEL", "BIOMASS_TO_JET_FUEL", "BIOMASS_TO_LFO",
    "BIOWASTE_TO_GASOLINE", "BIOWASTE_TO_DIESEL", "BIOWASTE_TO_JET_FUEL", "BIOWASTE_TO_LFO",
    # --- Future power generation (3) ---
    "NUCLEAR_SMR", "CCGT_AMMONIA", "COAL_IGCC",
    # --- Future transport (6) ---
    "PLANE_H2_SHORT_HAUL",
    "CARGO_FUELCELL_LH2", "CARGO_FUELCELL_AMMONIA",
    "CARGO_RETRO_METHANOL", "CARGO_RETRO_AMMONIA",
    "TRUCK_METHANOL",
    # --- Future heat (2) ---
    "DEC_ADVCOGEN_H2", "DEC_ADVCOGEN_GAS",
    # --- Storage without consumers (5) ---
    "CAES", "H2_STORAGE", "AMMONIA_STORAGE", "METHANOL_STORAGE", "CO2_STORAGE",
    # --- CCS (2) ---
    "ATM_CCS", "INDUSTRY_CCS",
]

# Stage B — Low risk, closes intermediate chains (not applied by default)
# DISABLED_TECH_STAGE_B = [
#     # Chemical / fuel intermediates
#     "SYN_METHANOLATION", "METHANE_TO_METHANOL",
#     "BIOMASS_TO_METHANOL", "BIOWASTE_TO_METHANOL",
#     "HABER_BOSCH", "AMMONIA_TO_H2",
#     # Synthetic gas
#     "SYN_METHANATION", "BIOMETHANATION_WET_BIOMASS",
#     "BIOMETHANATION_BIOWASTE", "BIOMASS_TO_METHANE", "BIOWASTE_TO_METHANE",
#     # H2 production
#     "H2_ELECTROLYSIS", "H2_NG", "H2_BIOMASS",
#     # HVC alternatives (OIL_TO_HVC must stay — sole conventional)
#     "GAS_TO_HVC", "BIOMASS_TO_HVC", "METHANOL_TO_HVC",
#     # Marginal 2017 transport
#     "BUS_COACH_HYDIESEL", "BUS_COACH_CNG_STOICH", "CAR_NG",
#     # Refinery
#     "DIESEL_TO_JET_FUEL",
# ]

# Stage C — Multi-cell infrastructure (irrelevant in single-cell FI run)
# DISABLED_TECH_STAGE_C = [
#     "GAS_PIPELINE", "GAS_SUBSEA", "HVDC_SUBSEA",
#     "H2_RETROFITTED", "H2_NEW", "H2_SUBSEA_RETRO", "H2_SUBSEA_NEW",
# ]


# ===================================================================
# SOLVER OPTIONS
# ===================================================================

def _barrier_crossover_opts(log_path: Path) -> dict:
    """Strategy A: barrier — stock ESMC CPLEX options from esmc.py.

    Uses crossover=0 (the ESMC default).  Both calib_2017_finland and
    ref_2017_finland solved to code=0 with these exact options.
    """
    cplex_options = [
        'baropt',
        'predual=-1',
        'barstart=4',
        'comptol=1e-5',
        'crossover=0',          # stock ESMC default (esmc.py)
        'timelimit 172800',
        'bardisplay=1',
        'display=2',
    ]
    return {
        'show_stats': 3,
        'log_file': str(log_path),
        'presolve': 200,
        'times': 1,
        'gentimes': 1,
        'cplex_options': ' '.join(cplex_options),
    }


def _dual_simplex_opts(log_path: Path) -> dict:
    """Fallback: dual simplex — gives a clear infeasibility certificate
    if the model is truly infeasible.
    """
    cplex_options = [
        'dual',                 # CPLEX dual simplex
        'predual=-1',
        'timelimit 1800',       # 30 min cap — don't burn hours
        'display=2',
    ]
    return {
        'show_stats': 3,
        'log_file': str(log_path),
        'presolve': 200,
        'times': 1,
        'gentimes': 1,
        'cplex_options': ' '.join(cplex_options),
    }


# ===================================================================
# CLI
# ===================================================================

def parse_args():
    p = argparse.ArgumentParser(
        description="Manual calibration runner — Finland 2017",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See script header for detailed usage examples.",
    )
    p.add_argument("-n", "--run-name", required=True,
                   help="Short name for this run (e.g. baseline, test_nuclear)")
    p.add_argument("-p", "--patch", action="append", default=[],
                   help="CSV patch file(s) to apply in-memory (repeatable)")
    p.add_argument("-d", "--description", default="",
                   help="Human-readable description of this run")
    p.add_argument("--dry-run", action="store_true",
                   help="Show patch effects without running the model")
    p.add_argument("--no-fperc", action="store_true",
                   help="Set f_perc=False (disables fmin_perc/fmax_perc constraints)")
    p.add_argument("--gwp-limit", type=float, default=None,
                   help="GWP limit in ktCO2/y (default: None = no limit)")
    p.add_argument("--re-share", type=float, default=None,
                   help="Minimum RE share of primary energy (default: None)")
    p.add_argument("--nbr-td", type=int, default=12,
                   help="Number of typical days (default: 12)")
    p.add_argument("--data-dir", default=None,
                   help="Override data directory (relative to repo root, "
                        "e.g. Data/2017_alt_from2035tech)")
    p.add_argument("--ampl-path", default=None,
                   help="Path to ampl executable (default: use PATH)")
    p.add_argument("--kmedoid", action="store_true",
                   help="Run kmedoid TD clustering instead of reading frozen TDs")
    p.add_argument("--skip-plots", action="store_true",
                   help="Skip validation plots (still scores)")
    p.add_argument("--solver", default="barrier",
                   choices=["barrier", "simplex"],
                   help="Primary solver strategy (default: barrier+crossover)")
    return p.parse_args()


# ===================================================================
# PATCH APPLICATION  (in-memory — Data/ is NEVER modified)
# ===================================================================

# Map from CSV filename to region.data dict key
_FILE_MAP = {
    "Technologies.csv": "Technologies",
    "Resources.csv":    "Resources",
    "Demands.csv":      "Demands",
    "Misc.csv":         "Misc",
}


def resolve_patch_files(raw_paths: list) -> list:
    """Resolve patch file paths — try absolute, repo-relative,
    then calibration/patches/."""
    resolved = []
    for pf in raw_paths:
        p = Path(pf)
        if not p.is_absolute():
            p = REPO_ROOT / pf
        if not p.exists():
            p = CALIBRATION_DIR / "patches" / pf
        if p.exists():
            resolved.append(p)
        else:
            print(f"  ERROR: patch not found: {pf}")
            print(f"         Tried: {REPO_ROOT / pf}")
            print(f"         Tried: {CALIBRATION_DIR / 'patches' / pf}")
            sys.exit(1)
    return resolved


def apply_patches(model, patch_files, run_dir, dry_run=False):
    """Apply CSV patches to region DataFrames in-memory.

    Returns a list of patch-log dicts for metadata.
    Also saves copies + diff summary to run_dir/patch_applied/.
    """
    logs = []
    if not dry_run and patch_files:
        patch_out = run_dir / "patch_applied"
        patch_out.mkdir(parents=True, exist_ok=True)
        diff_lines = []

    for patch_path in patch_files:
        log = {"file": str(patch_path), "changes": []}
        df = pd.read_csv(patch_path)
        print(f"\n  Patch: {patch_path.name} ({len(df)} changes)")

        # Save a copy of the patch file
        if not dry_run:
            shutil.copy2(patch_path, patch_out / patch_path.name)
            diff_lines.append(f"# {patch_path.name} ({len(df)} changes)")
            diff_lines.append("")

        for _, row in df.iterrows():
            target_file = row["file"].strip()
            param = row["parameter"].strip()
            entity = str(row["technology_or_resource"]).strip()
            new_val = row["value"]

            if target_file not in _FILE_MAP:
                print(f"    SKIP: unknown file {target_file}")
                continue

            data_key = _FILE_MAP[target_file]

            for r_code, region in model.regions.items():
                if data_key not in region.data or region.data[data_key] is None:
                    print(f"    SKIP: {data_key} not in region {r_code}")
                    continue

                rdf = region.data[data_key]
                if entity not in rdf.index:
                    print(f"    SKIP: {entity} not in {r_code}/{data_key}")
                    continue
                if param not in rdf.columns:
                    print(f"    SKIP: column {param} not in {r_code}/{data_key}")
                    continue

                old_val = rdf.loc[entity, param]
                if not dry_run:
                    rdf.loc[entity, param] = new_val

                prefix = "[DRY] " if dry_run else ""
                print(f"    {prefix}{r_code}/{entity}.{param}: "
                      f"{old_val} -> {new_val}")
                if not dry_run:
                    diff_lines.append(
                        f"  {r_code}/{entity}.{param}: {old_val} -> {new_val}"
                    )
                log["changes"].append({
                    "region": r_code, "data_key": data_key,
                    "entity": entity, "parameter": param,
                    "old_value": str(old_val), "new_value": str(new_val),
                })
        logs.append(log)

    if not dry_run and patch_files:
        with open(patch_out / "diff_summary.txt", "w") as f:
            f.write("\n".join(diff_lines))
        print(f"  Diff summary -> {patch_out / 'diff_summary.txt'}")

    return logs


# ===================================================================
# FINLAND 2017 TECHNOLOGY DISABLING  (in-memory, CSVs untouched)
# ===================================================================

def apply_fi2017_disabling(model, tech_list=None):
    """Fully disable technologies: f_min=0, f_max=0, fmin_perc=0, fmax_perc=0.

    Operates on in-memory DataFrames only — base CSV files are NEVER modified.
    Zeroing fmin_perc/fmax_perc ensures no percentage constraint can force
    non-zero capacity on a disabled tech (belt-and-suspenders with --no-fperc).
    Returns the count of technologies actually disabled.
    """
    if tech_list is None:
        tech_list = DISABLED_TECH_STAGE_A

    disabled_count = 0
    skipped = []
    for r_code, region in model.regions.items():
        rdf = region.data.get("Technologies")
        if rdf is None:
            continue
        for tech in tech_list:
            if tech in rdf.index:
                rdf.loc[tech, "f_min"] = 0
                rdf.loc[tech, "f_max"] = 0
                # Zero percentage constraints too (defence-in-depth)
                if "fmin_perc" in rdf.columns:
                    rdf.loc[tech, "fmin_perc"] = 0
                if "fmax_perc" in rdf.columns:
                    rdf.loc[tech, "fmax_perc"] = 0
                disabled_count += 1
            else:
                if r_code not in [s[0] for s in skipped]:
                    skipped.append((r_code, tech))

    print(f"  [Stage A] Disabled {len(tech_list)} technologies "
          f"({disabled_count} entries zeroed across regions).")
    if skipped:
        missing = [t for _, t in skipped]
        print(f"  [Stage A] {len(missing)} tech(s) not in index (OK if not in REF_REGION).")
    return disabled_count


# ===================================================================
# INPUT SNAPSHOT — freeze a copy of every .dat file fed to AMPL
# ===================================================================

def snapshot_inputs(cs_dir: Path, run_dir: Path):
    """Copy all .dat files from cs_dir into run_dir/input_snapshot/.

    This guarantees that even if Data/2017 CSVs change later,
    the exact .dat inputs for this run are preserved.
    """
    snap_dir = run_dir / "input_snapshot"
    snap_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for dat in cs_dir.glob("*.dat"):
        shutil.copy2(dat, snap_dir / dat.name)
        count += 1
    print(f"  Input snapshot: {count} .dat files -> {snap_dir}")
    return snap_dir


# ===================================================================
# CONSTRAINT DIFF — compare current run vs frozen baseline (STEP 1)
# ===================================================================

# Path to frozen baseline input snapshot (stageA_verify, 2026-03-10)
FROZEN_BASELINE_DAT = (
    REPO_ROOT / "case_studies" / "FI" / "manual_runs"
    / "20260310_095416__stageA_verify" / "input_snapshot"
    / "reg_technologies.dat"
)

CONSTRAINT_COLS = ["f_min", "f_max", "fmin_perc", "fmax_perc"]


def _parse_dat_technologies(dat_path: Path) -> pd.DataFrame:
    """Parse reg_technologies.dat into a DataFrame indexed by (region, tech).

    Returns columns: c_inv, c_maint, gwp_constr, lifetime, c_p,
                     fmin_perc, fmax_perc, f_min, f_max
    """
    cols = ["region", "tech", "c_inv", "c_maint", "gwp_constr",
            "lifetime", "c_p", "fmin_perc", "fmax_perc", "f_min", "f_max"]
    rows = []
    with open(dat_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("param") or line.startswith(";") or not line:
                continue
            parts = line.split()
            if len(parts) >= 11:
                row = {}
                row["region"] = parts[0]
                row["tech"] = parts[1]
                for i, col in enumerate(cols[2:], start=2):
                    val = parts[i]
                    if val.lower() == "infinity":
                        row[col] = float("inf")
                    else:
                        try:
                            row[col] = float(val)
                        except ValueError:
                            row[col] = val
                rows.append(row)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.set_index(["region", "tech"])
    return df


def generate_constraint_diff(model, run_dir: Path) -> str:
    """Compare current Technologies constraints against the frozen baseline.

    Writes CONSTRAINT_DIFF.md to run_dir and returns a short summary string.
    """
    # --- Load frozen baseline ---
    if not FROZEN_BASELINE_DAT.exists():
        msg = "Frozen baseline .dat not found — skipping constraint diff."
        (run_dir / "CONSTRAINT_DIFF.md").write_text(
            f"# Constraint Diff\n\n{msg}\n", encoding="utf-8")
        return msg

    baseline = _parse_dat_technologies(FROZEN_BASELINE_DAT)

    # --- Build current merged Technologies table ---
    lines = ["# CONSTRAINT_DIFF.md", "",
             "Comparison of current run vs frozen baseline "
             "(`stageA_verify`, 2026-03-10).", "",
             "Only technologies whose constraint columns differ are listed.", ""]

    diff_count = 0
    for r_code, region in model.regions.items():
        tech_df = region.data.get("Technologies")
        if tech_df is None:
            continue
        for tech in tech_df.index:
            current = {}
            for col in CONSTRAINT_COLS:
                if col in tech_df.columns:
                    v = tech_df.loc[tech, col]
                    current[col] = float(v) if pd.notna(v) else 0.0
                else:
                    current[col] = 0.0 if col == "fmin_perc" else 1.0

            # Get baseline values
            base = {}
            if (r_code, tech) in baseline.index:
                brow = baseline.loc[(r_code, tech)]
                for col in CONSTRAINT_COLS:
                    v = brow.get(col, 0.0)
                    base[col] = float(v) if pd.notna(v) else 0.0
            else:
                # Tech not in baseline → it was added
                base = {"f_min": 0.0, "f_max": float("inf"),
                        "fmin_perc": 0.0, "fmax_perc": 1.0}

            # Compare
            changed = False
            for col in CONSTRAINT_COLS:
                bv, cv = base.get(col, 0.0), current.get(col, 0.0)
                if abs(bv - cv) > 1e-9:
                    changed = True
                    break

            if changed:
                diff_count += 1

                def _fmt(v):
                    if v == float("inf"):
                        return "inf"
                    if v == float("-inf"):
                        return "-inf"
                    if v == int(v):
                        return str(int(v))
                    return f"{v:.6g}"

                lines.append(f"### {tech}")
                b_str = ", ".join(f"{c}={_fmt(base.get(c, 0))}" for c in CONSTRAINT_COLS)
                c_str = ", ".join(f"{c}={_fmt(current.get(c, 0))}" for c in CONSTRAINT_COLS)
                lines.append(f"- baseline: {b_str}")
                lines.append(f"- current : {c_str}")
                lines.append("")

    if diff_count == 0:
        lines.append("No technology constraints differ from frozen baseline.")
        lines.append("")

    summary = f"{diff_count} technology constraint(s) differ from frozen baseline."
    lines.insert(3, f"**Summary:** {summary}")
    lines.insert(4, "")

    (run_dir / "CONSTRAINT_DIFF.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


# ===================================================================
# INFEASIBILITY DIAGNOSTICS (STEP 2)
# ===================================================================

def _build_infeasibility_diagnostics(model) -> str:
    """Build diagnostic text for infeasibility analysis.

    Aligned with ESMC model equations:
    - layer_balance (hourly hard equalities, no unmet-demand slack)
    - capacity_factor_t (c_p_t hourly profiles for variable RES)
    - CHP coupling (electricity + heat co-production)
    - Resource feasibility
    - Constraint summary (inherited vs new)

    Uses in-memory model data: Technologies, Demands, Resources, Layers_in_out,
    Time_series / ts_td (typical-day time series).
    Returns markdown text to append to FAILURE_SUMMARY.md.
    """
    import numpy as np

    sections = []

    region = model.regions.get("FI")
    if region is None:
        return "\n## Diagnostics\n\nNo FI region found in model.\n"

    tech_df = region.data.get("Technologies")
    demands = region.data.get("Demands")
    resources = region.data.get("Resources")
    lio = model.data_indep.get("Layers_in_out")

    if tech_df is None or lio is None:
        return "\n## Diagnostics\n\nTechnologies or Layers_in_out data unavailable.\n"

    # Clean indices
    lio.columns = lio.columns.str.strip()
    lio.index = lio.index.str.strip()

    # ---- Resolve time_series_mapping for c_p_t ----
    ts_mapping = None
    try:
        ts_mapping = model.data_indep["Misc_indep"]["time_series_mapping"]
    except (KeyError, TypeError):
        pass

    # Build tech -> ts_name mapping for variable RES
    # res_params: {'PV': 'PV', 'WIND_OFFSHORE': 'WIND_OFFSHORE', ...}
    # res_mult_params: {'SOLAR': ['DHN_SOLAR', 'DEC_SOLAR', ...], ...}
    tech_to_ts = {}  # tech_name -> ts_column_name
    if ts_mapping:
        for ts_name, tech_name in ts_mapping.get("res_params", {}).items():
            tech_to_ts[tech_name] = ts_name
        for ts_name, tech_list in ts_mapping.get("res_mult_params", {}).items():
            for tech_name in tech_list:
                tech_to_ts[tech_name] = ts_name

    # Get ts_td (typical-day time series) if available
    ts_td = getattr(region, "ts_td", None)  # MultiIndex (ts_name, hour) x TD_number

    # Helper: get f_min/f_max/c_p for a tech
    def _tech_bounds(t):
        fmin = float(tech_df.loc[t, "f_min"]) if "f_min" in tech_df.columns else 0.0
        fmax = float(tech_df.loc[t, "f_max"]) if "f_max" in tech_df.columns else float("inf")
        cp = float(tech_df.loc[t, "c_p"]) if "c_p" in tech_df.columns else 1.0
        return fmin, fmax, cp

    def _demand_twh(demand_name):
        """Get total demand in TWh."""
        if demands is None or demand_name not in demands.index:
            return None
        sector_cols = ["HOUSEHOLDS", "SERVICES", "INDUSTRY", "TRANSPORTATION"]
        cols = [c for c in sector_cols if c in demands.columns]
        return demands.loc[demand_name, cols].sum() / 1000  # GWh -> TWh

    def _demand_gwh(demand_name):
        """Get total demand in GWh."""
        if demands is None or demand_name not in demands.index:
            return None
        sector_cols = ["HOUSEHOLDS", "SERVICES", "INDUSTRY", "TRANSPORTATION"]
        cols = [c for c in sector_cols if c in demands.columns]
        return demands.loc[demand_name, cols].sum()

    # Helper: get c_p_t profile for a tech from ts_td
    def _get_cpt_profile(tech_name):
        """Return c_p_t DataFrame (24 rows x N_TD cols) for a variable RES tech, or None."""
        if ts_td is None or tech_name not in tech_to_ts:
            return None
        ts_name = tech_to_ts[tech_name]
        try:
            profile = ts_td.loc[(ts_name, slice(None)), :].droplevel(level=0)
            return profile
        except KeyError:
            return None

    # ---- A. Electricity Balance — Annual + Hourly Adequacy ----
    sections.append("## A. Electricity Balance Feasibility\n")

    elec_demand_twh = _demand_twh("ELECTRICITY")
    elec_demand_gwh = _demand_gwh("ELECTRICITY")

    if elec_demand_twh is not None:
        sections.append(f"- Total annual electricity demand: **{elec_demand_twh:.1f} TWh** "
                        f"({elec_demand_gwh:.0f} GWh)")
    else:
        sections.append("- Total annual electricity demand: **unknown**")

    # Collect all electricity producers with f_max > 0
    elec_producers = []
    if "ELECTRICITY" in lio.columns:
        for t in lio.index[lio["ELECTRICITY"] > 0]:
            if t not in tech_df.index:
                continue
            fmin, fmax, cp = _tech_bounds(t)
            if fmax <= 0:
                continue
            eff = float(lio.loc[t, "ELECTRICITY"])
            is_variable = t in tech_to_ts
            cpt_profile = _get_cpt_profile(t) if is_variable else None
            elec_producers.append({
                "tech": t, "fmin": fmin, "fmax": fmax, "cp": cp,
                "eff": eff, "is_variable": is_variable,
                "cpt": cpt_profile,
            })

    # Annual capacity summary
    total_annual_max = 0.0
    sections.append("")
    sections.append("### Available electricity producers (f_max > 0):\n")
    sections.append("| Tech | f_min | f_max | c_p | lio_eff | Variable? | Max annual (TWh) |")
    sections.append("|------|-------|-------|-----|---------|-----------|-----------------|")
    for p in sorted(elec_producers, key=lambda x: -x["fmax"] * x["eff"]):
        t = p["tech"]
        fmax_s = f"{p['fmax']:.2f}" if p["fmax"] < 1e14 else "∞"
        ann_max_twh = p["fmax"] * p["cp"] * p["eff"] * 8760 / 1000 if p["fmax"] < 1e14 else float("inf")
        ann_s = f"{ann_max_twh:.1f}" if ann_max_twh != float("inf") else "∞"
        total_annual_max += ann_max_twh if ann_max_twh != float("inf") else 0
        sections.append(f"| {t} | {p['fmin']:.2f} | {fmax_s} | {p['cp']:.3f} | "
                        f"{p['eff']:.3f} | {'YES' if p['is_variable'] else 'no'} | {ann_s} |")

    if total_annual_max > 0:
        sections.append(f"\n- Sum of max annual generation (finite f_max only): "
                        f"**{total_annual_max:.1f} TWh**")
    if elec_demand_twh is not None and total_annual_max > 0:
        if total_annual_max < elec_demand_twh:
            sections.append(f"- **ANNUAL SHORTFALL**: Max generation {total_annual_max:.1f} TWh "
                            f"< demand {elec_demand_twh:.1f} TWh")
        else:
            sections.append(f"- Annual headroom: {total_annual_max - elec_demand_twh:.1f} TWh "
                            f"({total_annual_max/elec_demand_twh*100:.0f}% of demand)")

    # ---- Hourly adequacy check (288 time steps) ----
    sections.append("")
    sections.append("### Hourly Adequacy Check (layer_balance must hold at every h,td)\n")

    if ts_td is not None and elec_demand_gwh is not None:
        # Get electricity demand profile from ts_td
        elec_ts = None
        try:
            elec_ts = ts_td.loc[("ELECTRICITY", slice(None)), :].droplevel(level=0)
        except KeyError:
            pass

        if elec_ts is not None:
            n_hours = len(elec_ts.index)  # typically 24
            n_tds = len(elec_ts.columns)  # typically 12

            # For each (h, td), compute:
            #   demand_level = elec_ts(h, td)  [proportional to demand at that hour]
            #   max_supply = sum over techs of: f_max * c_p_t(h,td) * lio_eff
            # We compare ratios: supply/demand at each time step

            # Build max-supply array: shape (24, N_TD)
            max_supply = np.zeros((n_hours, n_tds))
            dispatchable_cap = 0.0  # GW of always-available supply

            for p in elec_producers:
                fmax = p["fmax"] if p["fmax"] < 1e14 else 0  # skip unbounded
                eff = p["eff"]
                if p["is_variable"] and p["cpt"] is not None:
                    # Variable RES: contribution varies by (h, td)
                    cpt_vals = p["cpt"].values  # shape (24, N_TD)
                    max_supply += fmax * cpt_vals * eff
                else:
                    # Dispatchable: c_p_t = 1 at all hours
                    dispatchable_cap += fmax * eff
                    max_supply += fmax * 1.0 * eff

            demand_vals = elec_ts.values  # shape (24, N_TD), proportional to GW demand

            # Compute ratio at each time step
            # Both max_supply and demand_vals are in proportional units
            # max_supply is in GW (absolute), demand_vals is in rescaled TS units
            # We need to normalize demand to GW. The ts_td values sum over
            # the synthetic year to equal the annual total of the original TS.
            # But demand_vals are not directly in GW — they are normalized TS values.
            # For a relative comparison, we just need the ratio.
            # Skip exact GW calculation — report the shape of the problem.

            sections.append(f"- Dispatchable capacity (c_p_t=1.0): **{dispatchable_cap:.2f} GW_e**")
            sections.append(f"- Time steps analyzed: {n_hours} hours × {n_tds} TDs = "
                            f"{n_hours * n_tds} cells")
            sections.append("")

            # Show variable RES c_p_t statistics
            for p in elec_producers:
                if p["is_variable"] and p["cpt"] is not None:
                    cpt_vals = p["cpt"].values.flatten()
                    sections.append(
                        f"- **{p['tech']}** c_p_t: min={cpt_vals.min():.4f}, "
                        f"mean={cpt_vals.mean():.4f}, max={cpt_vals.max():.4f}, "
                        f"f_max={p['fmax']:.2f} → peak GW_e={p['fmax']*cpt_vals.max()*p['eff']:.2f}, "
                        f"trough GW_e={p['fmax']*cpt_vals.min()*p['eff']:.3f}"
                    )

            sections.append("")

            # Identify worst-case hours: where max_supply is lowest
            # Also check where demand is highest
            supply_flat = max_supply.flatten()
            demand_flat = demand_vals.flatten()

            # Find hours where supply is at minimum
            worst_supply_idx = np.argsort(supply_flat)[:5]
            sections.append("**Worst supply hours** (lowest max possible supply in GW_e):")
            for idx in worst_supply_idx:
                h_idx = idx // n_tds
                td_idx = idx % n_tds
                h = elec_ts.index[h_idx]
                td = elec_ts.columns[td_idx]
                s = supply_flat[idx]
                d = demand_flat[idx]
                sections.append(f"  - h={h}, td={td}: max_supply={s:.3f} GW_e, "
                                f"demand_ts_value={d:.4f}")

            # Find hours where demand is at maximum
            worst_demand_idx = np.argsort(-demand_flat)[:5]
            sections.append("")
            sections.append("**Peak demand hours** (highest demand time-series value):")
            for idx in worst_demand_idx:
                h_idx = idx // n_tds
                td_idx = idx % n_tds
                h = elec_ts.index[h_idx]
                td = elec_ts.columns[td_idx]
                s = supply_flat[idx]
                d = demand_flat[idx]
                sections.append(f"  - h={h}, td={td}: demand_ts={d:.4f}, "
                                f"max_supply={s:.3f} GW_e")

            # Check if there exist hours where supply could be zero
            zero_supply_hours = int(np.sum(supply_flat < 0.001))
            if zero_supply_hours > 0:
                sections.append(f"\n**CRITICAL**: {zero_supply_hours} of {len(supply_flat)} "
                                f"time steps have near-zero supply capacity (<0.001 GW).")
                sections.append("This means the layer_balance constraint CANNOT be "
                                "satisfied at those hours — the model is **infeasible**.")
        else:
            sections.append("ELECTRICITY time series not found in ts_td — "
                            "cannot perform hourly adequacy check.")
    else:
        if ts_td is None:
            sections.append("ts_td not available (temporal aggregation may not have completed) — "
                            "cannot perform hourly adequacy check.")
        else:
            sections.append("Electricity demand unknown — cannot perform hourly adequacy check.")
    sections.append("")

    # ---- B. Heat sector feasibility ----
    sections.append("## B. Heat Sector Feasibility\n")

    # Low-temperature heat
    heat_sh = _demand_twh("HEAT_LOW_T_SH")
    heat_hw = _demand_twh("HEAT_LOW_T_HW")
    heat_low_total = (heat_sh or 0) + (heat_hw or 0)
    sections.append(f"- Low-temp heat demand SH: **{heat_sh:.1f} TWh**" if heat_sh else
                    "- Low-temp heat demand SH: **unknown**")
    sections.append(f"- Low-temp heat demand HW: **{heat_hw:.1f} TWh**" if heat_hw else
                    "- Low-temp heat demand HW: **unknown**")
    sections.append(f"- Total low-temp heat (SH+HW): **{heat_low_total:.1f} TWh**")
    sections.append(f"  (DHN/DEC split decided by model variable Share_heat_dhn, "
                    f"bounded by share_heat_dhn_min/max)")

    # Peak SH factor
    peak_sh = getattr(region, "peak_sh_factor", None)
    if peak_sh is not None:
        sections.append(f"- peak_sh_factor (yr_peak/td_peak): **{peak_sh:.3f}**")
        if peak_sh > 1.5:
            sections.append(f"  ⚠ High peak_sh_factor means the worst SH hour is "
                            f"{peak_sh:.1f}× the worst TD hour — "
                            f"size_limit may bind tightly.")
    sections.append("")

    # DHN producers
    sections.append("### DHN heat producers:")
    dhn_total_max_gw = 0.0
    if "HEAT_LOW_T_DHN" in lio.columns:
        dhn_prods = lio.index[lio["HEAT_LOW_T_DHN"] > 0]
        for t in sorted(dhn_prods):
            if t not in tech_df.index:
                continue
            fmin, fmax, cp = _tech_bounds(t)
            if fmax <= 0:
                continue
            eff = float(lio.loc[t, "HEAT_LOW_T_DHN"])
            fmax_s = f"{fmax:.2f}" if fmax < 1e14 else "∞"
            sections.append(f"  - {t}: f_min={fmin:.2f}, f_max={fmax_s}, "
                            f"c_p={cp:.3f}, eff_heat={eff:.3f}")
            if fmax < 1e14:
                dhn_total_max_gw += fmax * eff
    sections.append(f"  - Total max DHN supply (finite f_max): **{dhn_total_max_gw:.2f} GW_th**")
    sections.append("")

    # DEC producers
    sections.append("### Decentralised heat producers:")
    dec_total_max_gw = 0.0
    if "HEAT_LOW_T_DECEN" in lio.columns:
        dec_prods = lio.index[lio["HEAT_LOW_T_DECEN"] > 0]
        for t in sorted(dec_prods):
            if t not in tech_df.index:
                continue
            fmin, fmax, cp = _tech_bounds(t)
            if fmax <= 0:
                continue
            eff = float(lio.loc[t, "HEAT_LOW_T_DECEN"])
            fmax_s = f"{fmax:.2f}" if fmax < 1e14 else "∞"
            sections.append(f"  - {t}: f_min={fmin:.2f}, f_max={fmax_s}, "
                            f"c_p={cp:.3f}, eff_heat={eff:.3f}")
            if fmax < 1e14:
                dec_total_max_gw += fmax * eff
    sections.append(f"  - Total max DEC supply (finite f_max): **{dec_total_max_gw:.2f} GW_th**")
    sections.append("")

    # Industrial heat
    heat_ht = _demand_twh("HEAT_HIGH_T")
    sections.append(f"### Industrial high-temp heat: demand = "
                    f"**{heat_ht:.1f} TWh**" if heat_ht else
                    "### Industrial high-temp heat: demand = **unknown**")
    if "HEAT_HIGH_T" in lio.columns:
        ind_prods = lio.index[lio["HEAT_HIGH_T"] > 0]
        for t in sorted(ind_prods):
            if t not in tech_df.index:
                continue
            fmin, fmax, cp = _tech_bounds(t)
            if fmax <= 0:
                continue
            eff = float(lio.loc[t, "HEAT_HIGH_T"])
            fmax_s = f"{fmax:.2f}" if fmax < 1e14 else "∞"
            sections.append(f"  - {t}: f_min={fmin:.2f}, f_max={fmax_s}, "
                            f"c_p={cp:.3f}, eff={eff:.3f}")
    sections.append("")

    # ---- C. Resource Feasibility ----
    sections.append("## C. Resource Feasibility\n")

    check_resources = ["WOOD", "COAL", "GAS", "URANIUM", "WASTE",
                       "WET_BIOMASS", "DIESEL", "GASOLINE", "LFO", "ELECTRICITY"]
    if resources is not None:
        for res_name in check_resources:
            if res_name not in resources.index:
                continue
            avail_local = float(resources.loc[res_name, "avail_local"]) if "avail_local" in resources.columns else 0
            avail_ext = float(resources.loc[res_name, "avail_exterior"]) if "avail_exterior" in resources.columns else 0
            total_avail = avail_local + avail_ext  # GWh

            if total_avail <= 0 and res_name not in ["ELECTRICITY"]:
                continue  # skip zero-availability resources unless it's ELECTRICITY

            # Estimate minimum use from forced techs
            res_layer = res_name
            min_use = 0.0
            res_details = []
            if res_layer in lio.columns:
                consumers = lio.index[lio[res_layer] < 0].tolist()
                for t in consumers:
                    if t not in tech_df.index:
                        continue
                    fmin, fmax, cp = _tech_bounds(t)
                    if fmin <= 0:
                        continue
                    intake = abs(float(lio.loc[t, res_layer]))
                    use = fmin * cp * intake * 8760  # GWh/yr
                    min_use += use
                    res_details.append((t, fmin, cp, intake, use))

            sections.append(f"### {res_name}")
            sections.append(f"- Available: {total_avail:.0f} GWh/yr "
                          f"(local={avail_local:.0f}, exterior={avail_ext:.0f})")
            sections.append(f"- Min implied use from forced techs: {min_use:.0f} GWh/yr")

            if res_details:
                for t, fmin, cp, intake, use in res_details:
                    sections.append(f"  - {t}: f_min={fmin:.2f} × c_p={cp:.3f} × "
                                    f"intake={intake:.3f} × 8760h = {use:.0f} GWh/yr")

            if total_avail > 0 and min_use > total_avail:
                sections.append(f"\n**WARNING**: Min use ({min_use:.0f} GWh) EXCEEDS "
                              f"available ({total_avail:.0f} GWh).")
            elif total_avail > 0 and min_use > total_avail * 0.8:
                sections.append(f"\nCaution: Min use = "
                              f"{min_use/total_avail*100:.0f}% of available.")
            sections.append("")
    else:
        sections.append("Resources data unavailable.\n")

    # ---- D. CHP Coupling Warning ----
    sections.append("## D. CHP Coupling Warning\n")

    chp_warnings = []
    for heat_layer in ["HEAT_LOW_T_DHN", "HEAT_HIGH_T"]:
        if "ELECTRICITY" not in lio.columns or heat_layer not in lio.columns:
            continue
        label = "DHN" if "DHN" in heat_layer else "IND"
        cogens = lio.index[(lio["ELECTRICITY"] > 0) & (lio[heat_layer] > 0)]
        for t in cogens:
            if t not in tech_df.index:
                continue
            fmin, fmax, cp = _tech_bounds(t)
            if fmin > 0:
                e = float(lio.loc[t, "ELECTRICITY"])
                h_eff = float(lio.loc[t, heat_layer])
                chp_warnings.append(
                    f"- **{t}**: f_min={fmin:.2f} GW → co-produces "
                    f"{fmin*e:.2f} GW_elec + {fmin*h_eff:.2f} GW_{label}_heat. "
                    f"Both must be absorbed by demand."
                )

    if chp_warnings:
        sections.append("CHP technologies with forced minimum capacity co-produce "
                       "electricity and heat simultaneously. Forcing large CHP minimums "
                       "can create infeasibility through coupled balance constraints.\n")
        sections.extend(chp_warnings)
    else:
        sections.append("No CHP technologies have forced minimum capacity (f_min > 0).")
    sections.append("")

    # ---- E. Constraint Summary (inherited vs new) ----
    sections.append("## E. Constraint Summary\n")
    sections.append("All FI Technologies.csv overrides (f_min, f_max applied to model):\n")
    sections.append("| Technology | f_min | f_max | Notes |")
    sections.append("|-----------|-------|-------|-------|")
    for t in sorted(tech_df.index):
        fmin, fmax, cp = _tech_bounds(t)
        # Only show techs that have meaningful constraints
        if fmin > 0 or fmax < 1e14:
            fmax_s = f"{fmax:.2f}" if fmax < 1e14 else "∞"
            note = ""
            if fmax <= 0:
                note = "DISABLED"
            elif fmin > 0 and fmax < 1e14:
                note = "forced range"
            elif fmin > 0:
                note = "lower bound"
            elif fmax < 1e14:
                note = "upper bound"
            sections.append(f"| {t} | {fmin:.2f} | {fmax_s} | {note} |")
    sections.append("")

    return "\n".join(sections)

def extract_metrics(outputs_dir: Path) -> dict:
    """Extract model metrics from a run's outputs/ directory."""
    m = {}

    # ---- Resources.csv -> Primary energy ----
    res_path = outputs_dir / "Resources.csv"
    if res_path.exists():
        df = pd.read_csv(res_path)
        lookup = {}
        for _, row in df.iterrows():
            lookup[row["Resources"]] = (
                row.get("R_year_local", 0) + row.get("R_year_exterior", 0)
            )

        m["PE_BIOMASS"] = sum(
            lookup.get(r, 0) for r in
            ["WOOD", "WET_BIOMASS", "BIOWASTE",
             "BIOMASS_RESIDUES", "ENERGY_CROPS_2"]
        ) / 1000
        m["PE_OIL"] = sum(
            lookup.get(r, 0) for r in
            ["GASOLINE", "DIESEL", "LFO", "JET_FUEL"]
        ) / 1000
        m["PE_GAS"]     = lookup.get("GAS", 0) / 1000
        m["PE_COAL"]    = lookup.get("COAL", 0) / 1000
        m["PE_NUCLEAR"] = lookup.get("URANIUM", 0) / 1000
        m["PE_HYDRO"]   = lookup.get("RES_HYDRO", 0) / 1000
        m["PE_WIND"]    = lookup.get("RES_WIND", 0) / 1000

    # ---- Year_balance.csv -> Electricity ----
    yb_path = outputs_dir / "Year_balance.csv"
    if yb_path.exists():
        yb = pd.read_csv(yb_path, index_col="Elements")
        if "ELECTRICITY" in yb.columns:
            def elec(techs):
                return sum(
                    max(0.0, float(yb.loc[t, "ELECTRICITY"]))
                    for t in techs if t in yb.index
                ) / 1000

            m["ELEC_NUCLEAR"]  = elec(["NUCLEAR"])
            m["ELEC_HYDRO"]    = elec(["HYDRO_DAM", "HYDRO_RIVER"])
            m["ELEC_WIND"]     = elec(["WIND_ONSHORE", "WIND_OFFSHORE"])
            m["ELEC_SOLAR"]    = elec(["PV_ROOFTOP", "PV_UTILITY"])

            chp_techs = [
                "DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL",
                "DHN_COGEN_WASTE", "DHN_COGEN_OIL",
                "IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_COAL",
                "IND_COGEN_WASTE",
                "DEC_COGEN_GAS", "DEC_COGEN_OIL",
                "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2",
            ]
            m["ELEC_CHP"] = elec(chp_techs)

            cond_techs = [
                "CCGT", "OCGT", "COAL_US", "COAL_IGCC",
                "CCGT_AMMONIA", "BIOMASS_TO_POWER",
            ]
            m["ELEC_CONDENSATION"] = elec(cond_techs)

    # ---- Gwp_breakdown.csv -> CO2 ----
    gwp_path = outputs_dir / "Gwp_breakdown.csv"
    if gwp_path.exists():
        df = pd.read_csv(gwp_path)
        if "CO2_net" in df.columns:
            m["CO2"] = df["CO2_net"].sum() / 1000
        elif "GWP_op" in df.columns:
            m["CO2"] = df["GWP_op"].sum() / 1000

    return m


def compute_score(metrics: dict):
    """Weighted average percentage error vs. REALITY_TARGETS.

    Returns (score, errors_dict).
    """
    weighted_sum = 0.0
    weight_sum = 0.0
    errors = {}
    for key, (target, weight) in REALITY_TARGETS.items():
        if key in metrics and target > 0:
            pct_err = abs(metrics[key] - target) / target * 100
            errors[key] = {
                "model": metrics[key],
                "target": target,
                "pct_error": pct_err,
            }
            weighted_sum += pct_err * weight
            weight_sum += weight
    score = weighted_sum / weight_sum if weight_sum > 0 else float("inf")
    return score, errors


def print_scorecard(score, errors):
    print(f"\n{'=' * 60}")
    print(f"  SCORE: {score:.1f}% weighted average error")
    print(f"{'=' * 60}")
    print(f"  {'Metric':<20} {'Model':>8} {'Target':>8} {'Error':>8}")
    print(f"  {'-' * 50}")
    for key in sorted(errors):
        info = errors[key]
        print(f"  {key:<20} {info['model']:>8.2f} "
              f"{info['target']:>8.1f} {info['pct_error']:>7.1f}%")


def append_to_rankings(run_dir, score, errors):
    """Append this run to calibration/run_rankings.csv."""
    row = {
        "run_name": run_dir.name,
        "status": "OK",
        "provenance": "manual",
        "score": round(score, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    for key in REALITY_TARGETS:
        if key in errors:
            row[f"{key}_model"] = round(errors[key]["model"], 2)
            row[f"{key}_err%"] = round(errors[key]["pct_error"], 1)

    new_row = pd.DataFrame([row])
    if RANKINGS_CSV.exists():
        df = pd.read_csv(RANKINGS_CSV)
        df = df[df["run_name"] != run_dir.name]
        df = pd.concat([df, new_row], ignore_index=True)
        df = df.sort_values("score", ascending=True)
    else:
        df = new_row
    df.to_csv(RANKINGS_CSV, index=False)
    print(f"  Rankings updated: {RANKINGS_CSV}")


# ===================================================================
# VALIDATION PLOTS  (delegates to validate_run.py)
# ===================================================================

def run_validation_plots(run_dir: Path):
    """Run validate_run.py on this run directory."""
    try:
        scripts_dir = str(REPO_ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from validate_run import load_reality, validate_one
        reality = load_reality()
        validate_one(run_dir, reality)
        print(f"  Validation plots -> {run_dir / 'validation_plots'}")
    except ImportError:
        print("  WARNING: validate_run.py not importable — skipping plots")
    except Exception as e:
        print(f"  WARNING: validation plots failed: {e}")


# ===================================================================
# METADATA
# ===================================================================

def _git_info():
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        ).stdout.strip()
        return {"commit": commit, "branch": branch}
    except Exception:
        return {}


def save_metadata(run_dir, args, patch_logs, score=None, solve_info=None):
    meta = {
        "run_name": args.run_name,
        "description": args.description,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "f_perc": not args.no_fperc,
            "gwp_limit_overall": args.gwp_limit,
            "re_share_primary": args.re_share,
            "nbr_td": args.nbr_td,
            "data_dir": args.data_dir,
            "solver_strategy": args.solver,
        },
        "patches": patch_logs,
        "score": score,
        "solve_info": solve_info,
        "command": " ".join(sys.argv),
        "git": _git_info(),
    }
    path = run_dir / "run_metadata.json"
    with open(path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"  Metadata saved: {path}")


# ===================================================================
# SOLVE STATUS HELPERS
# ===================================================================

def _describe_status(code):
    """Human-readable description for AMPL solve_result_num."""
    if code == 0:
        return "optimal"
    if code == -1:
        return "unknown (barrier interior, crossover may have failed)"
    if 0 < code < 100:
        return "solved (suboptimal)"
    if 100 <= code < 200:
        return "uncertain (optimality not guaranteed)"
    if 200 <= code < 300:
        return "INFEASIBLE"
    if 300 <= code < 400:
        return "UNBOUNDED"
    if 400 <= code < 500:
        return "LIMIT (time/iteration limit reached)"
    return f"FAILURE (code {code})"


# ===================================================================
# SOLVER WITH FALLBACK
# ===================================================================

def _solve_with_fallback(model, args, ampl_path, log_path):
    """Solve with primary strategy, fall back to dual simplex if needed.

    Returns solve_result_num (0 = optimal).
    """
    # --- Primary solve ---
    if args.solver == "simplex":
        print("  Strategy: dual simplex (user-requested)")
        opts = _dual_simplex_opts(log_path)
    else:
        print("  Strategy: barrier + crossover=1")
        opts = _barrier_crossover_opts(log_path)

    model.set_esom(ampl_path=ampl_path, ampl_options=opts)
    model.solve_esom()
    model.esom.get_solve_info()

    code = int(model.esom.t[2])
    if code == 0:
        print(f"  Solve OK (code {code})")
        return code

    # --- Fallback ---
    # Only fall back if primary was barrier and result is ambiguous
    primary_code = code
    if args.solver != "simplex" and (code == -1 or 100 <= code < 200):
        print(f"\n  Primary solve returned code {code} "
              f"— trying dual simplex fallback...")
        fallback_log = log_path.parent / "log_fallback.txt"
        fallback_opts = _dual_simplex_opts(fallback_log)

        # Close and re-create AMPL instance
        try:
            model.esom.ampl.close()
        except Exception:
            pass

        try:
            model.set_esom(ampl_path=ampl_path, ampl_options=fallback_opts)
            model.solve_esom()
            model.esom.get_solve_info()
            code = int(model.esom.t[2])
            print(f"  Fallback result: code {code} "
                  f"({_describe_status(code)})")
        except Exception as e:
            print(f"  Fallback CRASHED: {e}")
            print(f"  Returning primary code {primary_code} for failure handling.")
            code = primary_code

    return code


# ===================================================================
# CUSTOM INIT_REGIONS (for --data-dir override)
# ===================================================================

def _init_regions_custom(model, data_dir: Path):
    """init_regions() but reading from a custom data directory.

    Minimal monkey-patch: overrides the data_dir that Region.__init__
    receives, without modifying any ESMC source code.
    """
    model.ref_region = Region(
        nuts=model.ref_region_name, data_dir=data_dir, ref_region=True,
    )
    for r in model.regions_names:
        if r != model.ref_region_name:
            model.regions[r] = copy.deepcopy(model.ref_region)
            model.regions[r].__init__(
                nuts=r, data_dir=data_dir, ref_region=False,
            )
        else:
            model.regions[r] = model.ref_region

    model.read_data_exch()


# ===================================================================
# RUN NOTES TEMPLATE
# ===================================================================

def _write_run_notes(run_dir, args, score, patch_files):
    """Write a run_notes.md template for the user to annotate."""
    patches_str = "\n".join(f"- {p.name}" for p in patch_files) or "None"
    score_str = f"{score:.1f}%" if score and score != float("inf") else "N/A"
    notes_path = run_dir / "run_notes.md"
    notes_path.write_text(
        f"# Run Notes: {args.run_name}\n\n"
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"**Score:** {score_str}\n"
        f"**f_perc:** {not args.no_fperc}\n"
        f"**Solver:** {args.solver}\n"
        f"**Patches:** {patches_str}\n\n"
        f"## Observations\n\n"
        f"<!-- Write your notes here -->\n\n"
        f"## Next Steps\n\n"
        f"<!-- What to try next -->\n",
        encoding="utf-8",
    )
    print(f"  Run notes template: {notes_path}")


def _write_failure_summary(run_dir, args, code, desc, model=None):
    """Write failure summary with automatic infeasibility diagnostics."""
    summary_path = run_dir / "FAILURE_SUMMARY.md"
    fi_path = REPO_ROOT / "Data" / "2017" / "FI" / "Technologies.csv"
    fi_info = "not found"
    try:
        df = pd.read_csv(fi_path, encoding="utf-8-sig")
        df.columns = [c.strip() for c in df.columns]
        forced = df[df["f_min"] > 0] if "f_min" in df.columns else pd.DataFrame()
        fi_info = f"{len(df)} rows, {len(forced)} with f_min>0"
    except Exception:
        pass

    text = (
        f"# SOLVE FAILURE: {args.run_name}\n\n"
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"**Code:** {code}\n"
        f"**Status:** {desc}\n"
        f"**Solver:** {args.solver}\n"
        f"**f_perc:** {not args.no_fperc}\n"
        f"**FI/Technologies.csv:** {fi_info}\n\n"
        f"## What to do\n\n"
        f"1. Check `log.txt` for CPLEX diagnostics.\n"
        f"2. Check `CONSTRAINT_DIFF.md` to see which constraints changed.\n"
        f"3. Revert FI/Technologies.csv to the frozen baseline:\n"
        f"   ```\n"
        f"   Copy-Item Data/2017/FI/Technologies.csv.frozen_baseline_20260310 "
        f"Data/2017/FI/Technologies.csv -Force\n"
        f"   ```\n"
        f"4. Re-run with fewer constraints.\n"
    )

    # Append automatic infeasibility diagnostics
    if model is not None:
        try:
            diag_text = _build_infeasibility_diagnostics(model)
            text += f"\n---\n\n# Automatic Infeasibility Diagnostics\n\n{diag_text}\n"
        except Exception as e:
            text += f"\n---\n\nDiagnostics generation failed: {e}\n"

    summary_path.write_text(text, encoding="utf-8")
    print(f"  Failure summary with diagnostics: {summary_path}")



# ===================================================================
# MAIN
# ===================================================================

def main():
    args = parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    case_study_name = f"manual_runs/{ts}__{args.run_name}"
    f_perc = not args.no_fperc

    print("=" * 70)
    print(f"  MANUAL CALIBRATION RUN: {args.run_name}")
    print(f"  Output: case_studies/FI/{case_study_name}/")
    print(f"  f_perc={f_perc}  solver={args.solver}  nbr_td={args.nbr_td}")
    if args.data_dir:
        print(f"  data_dir override: {args.data_dir}")
    print("=" * 70)

    # ---- Config ----
    config = {
        "case_study": case_study_name,
        "comment": args.description or f"manual run {args.run_name}",
        "regions_names": ["FI"],
        "gwp_limit_overall": args.gwp_limit,
        "re_share_primary": args.re_share,
        "f_perc": f_perc,
        "year": 2017,
    }

    # ---- [1] Initialize ESMC ----
    print("\n[1/7] Initializing ESMC...")
    ampl_path = Path(args.ampl_path) if args.ampl_path else None
    my_model = Esmc(config, nbr_td=args.nbr_td)
    run_dir = my_model.cs_dir

    # ---- [2] Read data ----
    print("[2/7] Reading data...")
    my_model.read_data_indep()

    if args.data_dir:
        alt_dir = REPO_ROOT / args.data_dir
        if not alt_dir.exists():
            print(f"  ERROR: --data-dir does not exist: {alt_dir}")
            sys.exit(1)
        print(f"  Using data from: {alt_dir}")
        _init_regions_custom(my_model, alt_dir)
    else:
        my_model.init_regions()

    # ---- [3] Apply patches (in-memory) ----
    patch_files = resolve_patch_files(args.patch)
    patch_logs = []
    if patch_files:
        print(f"\n[3/7] Applying {len(patch_files)} patch(es) in-memory...")
        patch_logs = apply_patches(my_model, patch_files, run_dir,
                                   dry_run=args.dry_run)
    else:
        print("\n[3/7] No patches — running with default inputs")

    # ---- [3b] Finland 2017 technology disabling (always applied) ----
    apply_fi2017_disabling(my_model)

    if args.dry_run:
        print("\n[DRY RUN] Stopping here. No .dat files, no solve.")
        save_metadata(run_dir, args, patch_logs)
        return

    # ---- [4] Temporal aggregation ----
    td_algo = "kmedoid" if args.kmedoid else "read"
    print(f"\n[4/7] Temporal aggregation (algo={td_algo}, nbr_td={args.nbr_td})...")
    my_model.init_ta(algo=td_algo, ampl_path=ampl_path)

    # ---- [5] Generate .dat files + snapshot ----
    print("[5/7] Generating .dat files...")
    my_model.print_td_data()
    my_model.print_data(indep=True)
    snapshot_inputs(my_model.cs_dir, run_dir)

    # ---- [5b] Constraint diff vs frozen baseline ----
    try:
        diff_summary = generate_constraint_diff(my_model, run_dir)
        print(f"  Constraint diff: {diff_summary}")
    except Exception as e:
        print(f"  WARNING: constraint diff failed: {e}")

    # ---- [6] Solve ----
    print("\n[6/7] Solving...")
    log_path = run_dir / "log.txt"
    try:
        solve_result_num = _solve_with_fallback(
            my_model, args, ampl_path, log_path,
        )
    except Exception as e:
        print(f"\n  SOLVE EXCEPTION: {e}")
        solve_result_num = -999  # sentinel for unhandled crash

    # ---- Check solve status ----
    desc = _describe_status(solve_result_num)
    if solve_result_num != 0:
        print(f"\n  {'=' * 60}")
        print(f"  SOLVE FAILED — solve_result_num = {solve_result_num}")
        print(f"  Meaning: {desc}")
        print(f"  Outputs from this run are UNRELIABLE.")
        print(f"  Check log.txt for details.")
        print(f"  {'=' * 60}")
        try:
            save_metadata(
                run_dir, args, patch_logs,
                solve_info={
                    "status": "FAILED",
                    "code": solve_result_num,
                    "desc": desc,
                },
            )
        except Exception as meta_err:
            print(f"  WARNING: metadata save failed: {meta_err}")
        # Write failure summary with infeasibility diagnostics
        try:
            _write_failure_summary(run_dir, args, solve_result_num, desc, model=my_model)
        except Exception as fs_err:
            # Last-resort: write a minimal failure summary
            try:
                (run_dir / "FAILURE_SUMMARY.md").write_text(
                    f"# SOLVE FAILURE: {args.run_name}\n\n"
                    f"Code: {solve_result_num}\n"
                    f"Status: {desc}\n"
                    f"Failure summary generation error: {fs_err}\n",
                    encoding="utf-8",
                )
            except Exception:
                pass
            print(f"  WARNING: failure summary generation failed: {fs_err}")
        sys.exit(1)

    # ---- [7] Results + score + plots ----
    print("\n[7/7] Collecting results...")
    my_model.get_year_results()
    my_model.prints_esom(inputs=True, outputs=True, solve_info=True)

    # Close AMPL
    try:
        my_model.esom.ampl.close()
    except Exception:
        pass

    outputs_dir = run_dir / "outputs"

    # Score
    metrics = extract_metrics(outputs_dir)
    score, errors = compute_score(metrics)
    if score != float("inf"):
        print_scorecard(score, errors)
        append_to_rankings(run_dir, score, errors)
    else:
        print("  Could not compute score (missing output files)")

    # Validation plots
    if not args.skip_plots and outputs_dir.exists():
        run_validation_plots(run_dir)

    # Metadata
    save_metadata(
        run_dir, args, patch_logs, score=score,
        solve_info={"status": "OK", "code": 0, "desc": "optimal"},
    )

    # Run notes template
    _write_run_notes(run_dir, args, score, patch_files)

    print(f"\n{'=' * 70}")
    print(f"  RUN COMPLETE: {run_dir.name}")
    if score is not None and score != float("inf"):
        print(f"  Score: {score:.1f}% weighted error")
    print(f"  Outputs: {outputs_dir}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
