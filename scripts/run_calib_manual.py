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
# SCORING (lightweight, same logic as score_all_fi_runs.py)
# ===================================================================

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

        model.set_esom(ampl_path=ampl_path, ampl_options=fallback_opts)
        model.solve_esom()
        model.esom.get_solve_info()
        code = int(model.esom.t[2])
        print(f"  Fallback result: code {code} "
              f"({_describe_status(code)})")

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

    # ---- [6] Solve ----
    print("\n[6/7] Solving...")
    log_path = run_dir / "log.txt"
    solve_result_num = _solve_with_fallback(
        my_model, args, ampl_path, log_path,
    )

    # ---- Check solve status ----
    desc = _describe_status(solve_result_num)
    if solve_result_num != 0:
        print(f"\n  {'=' * 60}")
        print(f"  SOLVE FAILED — solve_result_num = {solve_result_num}")
        print(f"  Meaning: {desc}")
        print(f"  Outputs from this run are UNRELIABLE.")
        print(f"  Check log.txt for details.")
        print(f"  {'=' * 60}")
        save_metadata(
            run_dir, args, patch_logs,
            solve_info={
                "status": "FAILED",
                "code": solve_result_num,
                "desc": desc,
            },
        )
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
