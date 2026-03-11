#!/usr/bin/env python3
"""
==========================================================================
  Manual Calibration Runner — Finland 2017  (FI-only, single-country)
==========================================================================

Tutorial
--------
1) Baseline run (no patches):

     python scripts/run_calib_manual_fi.py --run-name baseline_ok

   Creates:  case_studies/FI/<run-name>/
   Contents: outputs/, input_snapshot/, validation_plots/,
             run_metadata.json, log.txt

2) Run with a patch CSV:

     python scripts/run_calib_manual_fi.py --run-name test_nuclear \
         --patch calibration/patches/nuclear_cap.csv

3) Dry-run (show patch diffs, no solve):

     python scripts/run_calib_manual_fi.py --run-name preview \
         --patch calibration/patches/nuclear_cap.csv --dry-run

4) Where results are stored:

     case_studies/FI/<run-name>/
       outputs/                  ESMC results CSVs
       outputs/regional_results/ per-region CSVs
       input_snapshot/           frozen .dat files
       validation_plots/         pe/elec/co2/error charts + report
       run_metadata.json         full config, score, solve info
       log.txt                   AMPL/CPLEX log

5) How scoring is updated:

     Each successful solve appends a row to calibration/run_rankings.csv
     sorted by ascending weighted-% error.

6) Compare two runs quickly:

     python scripts/validate_run.py --runs <name_A> <name_B>
     # or inspect calibration/run_rankings.csv

Patch CSV format (one change per row):
  file,parameter,technology_or_resource,value
  Technologies.csv,f_max,NUCLEAR,8000
  Resources.csv,avail_local,COAL,50000

Data safety:
  Data/2017/ is NEVER modified.  All patches are applied to in-memory
  DataFrames after init_regions().  The script snapshots .dat files so
  the exact numerical input is preserved per run.

Solver strategy:
  Uses the SAME default CPLEX options defined in esmc/utils/esmc.py
  (barrier + crossover=0).  If the primary solve returns an ambiguous
  status (code -1 or 100-199), ONE deterministic fallback re-solve with
  dual simplex is attempted.  Both logs are saved in the run folder.
"""

import argparse
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

CALIBRATION_DIR = REPO_ROOT / "calibration"
RANKINGS_CSV = CALIBRATION_DIR / "run_rankings.csv"
REALITY_CSV = CALIBRATION_DIR / "reality" / "finland_2017_reference.csv"

# ---------------------------------------------------------------------------
# Reality targets (from finland_2017_reference.csv — kept in sync)
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
# CLI
# ===================================================================

def parse_args():
    p = argparse.ArgumentParser(
        description="Manual calibration runner — Finland 2017 (FI-only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See script header for detailed usage examples.",
    )
    p.add_argument("--run-name", "-n", required=True,
                   help="Short name for this run (becomes the output folder)")
    p.add_argument("--patch", "-p", action="append", default=[],
                   help="CSV patch file(s) to apply in-memory (repeatable)")
    p.add_argument("--description", "-d", default="",
                   help="Human-readable description stored in metadata")
    p.add_argument("--dry-run", action="store_true",
                   help="Show patch effects without solving")
    p.add_argument("--no-fperc", action="store_true",
                   help="Disable fmin_perc/fmax_perc constraints")
    p.add_argument("--gwp-limit", type=float, default=None,
                   help="GWP limit in ktCO2/y (default: no limit)")
    p.add_argument("--re-share", type=float, default=None,
                   help="Minimum RE share of primary energy (default: None)")
    p.add_argument("--nbr-td", type=int, default=12,
                   help="Number of typical days (default: 12)")
    p.add_argument("--skip-plots", action="store_true",
                   help="Skip validation plots")
    p.add_argument("--simplex", action="store_true",
                   help="Use dual simplex instead of barrier (avoids barrier OOM)")
    p.add_argument("--crossover", action="store_true",
                   help="Enable crossover after barrier to get clean BFS (fixes tolerance noise)")
    return p.parse_args()


# ===================================================================
# PATCH WORKFLOW
# ===================================================================

_FILE_MAP = {
    "Technologies.csv": "Technologies",
    "Resources.csv":    "Resources",
    "Demands.csv":      "Demands",
    "Misc.csv":         "Misc",
}


def resolve_patch_files(raw_paths: list) -> list:
    """Resolve patch paths: absolute, repo-relative, or in calibration/patches/."""
    resolved = []
    for pf in raw_paths:
        p = Path(pf)
        if not p.is_absolute():
            p = REPO_ROOT / pf
        if not p.exists():
            p = CALIBRATION_DIR / "patches" / Path(pf).name
        if p.exists():
            resolved.append(p)
        else:
            print(f"  ERROR: patch not found: {pf}")
            sys.exit(1)
    return resolved


def apply_patches(model, patch_files, run_dir, dry_run=False):
    """Apply CSV patches in-memory and write a patch_applied.md log.

    Returns list of patch-log dicts for metadata.
    """
    all_logs = []
    md_lines = ["# Patches Applied\n"]

    for patch_path in patch_files:
        log = {"file": str(patch_path), "changes": []}
        df = pd.read_csv(patch_path)
        print(f"\n  Patch: {patch_path.name} ({len(df)} changes)")
        md_lines.append(f"\n## {patch_path.name}\n")
        md_lines.append("| Region | Entity | Parameter | Old | New |")
        md_lines.append("|--------|--------|-----------|-----|-----|")

        for _, row in df.iterrows():
            target_file = str(row["file"]).strip()
            param = str(row["parameter"]).strip()
            entity = str(row["technology_or_resource"]).strip()
            new_val = row["value"]

            if target_file not in _FILE_MAP:
                print(f"    SKIP: unknown file {target_file}")
                continue
            data_key = _FILE_MAP[target_file]

            for r_code, region in model.regions.items():
                if region is None or data_key not in region.data:
                    continue
                rdf = region.data[data_key]
                if rdf is None or entity not in rdf.index or param not in rdf.columns:
                    continue

                old_val = rdf.loc[entity, param]
                if not dry_run:
                    rdf.loc[entity, param] = new_val

                tag = "[DRY] " if dry_run else ""
                print(f"    {tag}{r_code}/{entity}.{param}: {old_val} -> {new_val}")
                md_lines.append(f"| {r_code} | {entity} | {param} | {old_val} | {new_val} |")
                log["changes"].append({
                    "region": r_code, "data_key": data_key,
                    "entity": entity, "parameter": param,
                    "old_value": str(old_val), "new_value": str(new_val),
                })
        all_logs.append(log)

    if any(l["changes"] for l in all_logs):
        (run_dir / "patch_applied.md").write_text("\n".join(md_lines), encoding="utf-8")

    return all_logs


# ===================================================================
# INPUT SNAPSHOT
# ===================================================================

def snapshot_inputs(cs_dir: Path, run_dir: Path):
    """Copy all .dat files from cs_dir into run_dir/input_snapshot/."""
    snap_dir = run_dir / "input_snapshot"
    snap_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for dat in cs_dir.glob("*.dat"):
        shutil.copy2(dat, snap_dir / dat.name)
        count += 1
    print(f"  Input snapshot: {count} .dat files -> {snap_dir}")
    return snap_dir


# ===================================================================
# SOLVER HELPERS
# ===================================================================

def _describe_status(code):
    """Human-readable AMPL solve_result_num."""
    if code == 0:
        return "optimal"
    if code == -1:
        return "unknown (barrier interior / crossover issue)"
    if 0 < code < 100:
        return "solved (suboptimal)"
    if 100 <= code < 200:
        return "uncertain"
    if 200 <= code < 300:
        return "INFEASIBLE"
    if 300 <= code < 400:
        return "UNBOUNDED"
    if 400 <= code < 500:
        return "LIMIT (time/iteration)"
    return f"FAILURE (code {code})"


def _dual_simplex_opts(log_path: Path) -> dict:
    """Deterministic fallback: dual simplex for a clear infeasibility certificate."""
    cplex_options = [
        'dual',
        'predual=-1',
        'timelimit 172800',
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


def _barrier_crossover_opts(log_path: Path) -> dict:
    """Barrier with crossover enabled to produce a clean basic feasible solution."""
    cplex_options = [
        'baropt',
        'predual=-1',
        'barstart=4',
        'comptol=1e-8',
        'crossover=1',
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


def solve_with_fallback(model, run_dir, ampl_path=None, use_simplex=False, use_crossover=False):
    """Solve using ESMC defaults, fall back to dual simplex if ambiguous.

    Uses the exact same CPLEX options that esmc.py defines (barrier + crossover=0).
    If that returns code -1, 100-199, or >=500, retries ONCE with dual simplex.
    If use_simplex=True, skips barrier entirely and uses dual simplex.

    Returns solve_result_num (0 = optimal).
    """
    log_primary = run_dir / "log.txt"

    if use_simplex:
        print("  Strategy: dual simplex (--simplex flag)")
        simplex_opts = _dual_simplex_opts(log_primary)
        model.set_esom(ampl_path=ampl_path, ampl_options=simplex_opts)
        model.solve_esom()
        if model.esom.t is None:
            model.esom.get_solve_info()
        code = int(model.esom.t[2])
        print(f"  Result: code {code} ({_describe_status(code)})")
        return code

    if use_crossover:
        print("  Strategy: barrier + crossover=2 (--crossover flag)")
        xover_opts = _barrier_crossover_opts(log_primary)
        model.set_esom(ampl_path=ampl_path, ampl_options=xover_opts)
        model.solve_esom()
        if model.esom.t is None:
            model.esom.get_solve_info()
        code = int(model.esom.t[2])
        print(f"  Result: code {code} ({_describe_status(code)})")
        return code

    # --- Primary solve (ESMC defaults — ampl_options=None) ---
    default_opts = None  # let set_esom use its built-in defaults
    print("  Strategy: ESMC defaults (barrier + crossover=0)")
    model.set_esom(ampl_path=ampl_path, ampl_options=default_opts)

    # Override log path to land in our run dir
    model.esom.options['log_file'] = str(log_primary)

    model.solve_esom()
    if model.esom.t is None:
        model.esom.get_solve_info()

    code = int(model.esom.t[2])
    print(f"  Primary result: code {code} ({_describe_status(code)})")

    if code == 0:
        return code

    # --- Fallback: dual simplex (one attempt) ---
    # Trigger on: -1 (barrier interior), 100-199 (uncertain), >=500 (failure/crash)
    if code == -1 or (100 <= code < 200) or code >= 500:
        print(f"\n  Ambiguous status ({code}) — retrying with dual simplex...")
        fallback_log = run_dir / "log_fallback.txt"
        fallback_opts = _dual_simplex_opts(fallback_log)

        try:
            model.esom.ampl.close()
        except Exception:
            pass

        model.set_esom(ampl_path=ampl_path, ampl_options=fallback_opts)
        model.solve_esom()
        if model.esom.t is None:
            model.esom.get_solve_info()

        code = int(model.esom.t[2])
        print(f"  Fallback result: code {code} ({_describe_status(code)})")

    return code


# ===================================================================
# METRIC EXTRACTION
# ===================================================================

def extract_metrics(outputs_dir: Path) -> dict:
    """Extract model metrics from outputs/ CSVs."""
    m = {}

    # --- Resources.csv → Primary energy ---
    res_path = outputs_dir / "Resources.csv"
    if res_path.exists():
        df = pd.read_csv(res_path)
        lookup = {}
        for _, row in df.iterrows():
            total = float(row.get("R_year_local", 0)) + float(row.get("R_year_exterior", 0))
            lookup[row.iloc[0]] = total

        m["PE_BIOMASS"] = sum(
            lookup.get(r, 0) for r in
            ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"]
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

    # --- Year_balance.csv → Electricity ---
    yb_path = outputs_dir / "Year_balance.csv"
    if yb_path.exists():
        yb = pd.read_csv(yb_path, index_col=0)
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

    # --- Gwp_breakdown.csv → CO2 ---
    gwp_path = outputs_dir / "Gwp_breakdown.csv"
    if gwp_path.exists():
        df = pd.read_csv(gwp_path)
        if "CO2_net" in df.columns:
            m["CO2"] = df["CO2_net"].sum() / 1000
        elif "GWP_op" in df.columns:
            m["CO2"] = df["GWP_op"].sum() / 1000

    return m


# ===================================================================
# SCORING
# ===================================================================

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
                "model": round(metrics[key], 3),
                "target": target,
                "pct_error": round(pct_err, 2),
            }
            weighted_sum += pct_err * weight
            weight_sum += weight
    score = weighted_sum / weight_sum if weight_sum > 0 else float("inf")
    return round(score, 2), errors


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


def append_to_rankings(run_name, score, errors):
    """Append/update this run in calibration/run_rankings.csv."""
    row = {
        "run_name": run_name,
        "status": "OK",
        "provenance": "manual",
        "score": score,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    for key in REALITY_TARGETS:
        if key in errors:
            row[f"{key}_model"] = errors[key]["model"]
            row[f"{key}_err%"] = errors[key]["pct_error"]

    new_row = pd.DataFrame([row])
    if RANKINGS_CSV.exists():
        df = pd.read_csv(RANKINGS_CSV)
        df = df[df["run_name"] != run_name]
        df = pd.concat([df, new_row], ignore_index=True)
        df = df.sort_values("score", ascending=True)
    else:
        RANKINGS_CSV.parent.mkdir(parents=True, exist_ok=True)
        df = new_row
    df.to_csv(RANKINGS_CSV, index=False)
    print(f"  Rankings updated: {RANKINGS_CSV}")


# ===================================================================
# VALIDATION PLOTS (delegates to validate_run.py)
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


def save_metadata(run_dir, args, patch_logs, score=None, errors=None,
                  solve_info=None):
    meta = {
        "run_name": args.run_name,
        "description": args.description,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "f_perc": not args.no_fperc,
            "gwp_limit_overall": args.gwp_limit,
            "re_share_primary": args.re_share,
            "nbr_td": args.nbr_td,
        },
        "patches": patch_logs,
        "score": score,
        "errors": errors,
        "solve_info": solve_info,
        "command": " ".join(sys.argv),
        "git": _git_info(),
    }
    path = run_dir / "run_metadata.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"  Metadata saved: {path}")


# ===================================================================
# MAIN
# ===================================================================

def main():
    args = parse_args()
    run_name = args.run_name
    f_perc = not args.no_fperc

    print("=" * 70)
    print(f"  MANUAL CALIBRATION — Finland 2017 (FI-only)")
    print(f"  Run name : {run_name}")
    print(f"  f_perc   : {f_perc}")
    print(f"  nbr_td   : {args.nbr_td}")
    print("=" * 70)

    # ---- ESMC Config (single-country, same as run_calib_case.py) ----
    config = {
        "case_study": run_name,
        "comment": args.description or f"manual run {run_name}",
        "regions_names": ["FI"],
        "gwp_limit_overall": args.gwp_limit,
        "re_share_primary": args.re_share,
        "f_perc": f_perc,
        "year": 2017,
    }

    # ---- [1] Initialize ESMC ----
    print("\n[1/7] Initializing ESMC...")
    my_model = Esmc(config, nbr_td=args.nbr_td)
    run_dir = my_model.cs_dir  # case_studies/FI/<run_name>/

    # ---- [2] Read data ----
    print("[2/7] Reading data...")
    my_model.read_data_indep()
    my_model.init_regions()

    # ---- [3] Apply patches (in-memory) ----
    patch_files = resolve_patch_files(args.patch)
    patch_logs = []
    if patch_files:
        print(f"\n[3/7] Applying {len(patch_files)} patch(es) in-memory...")
        patch_logs = apply_patches(my_model, patch_files, run_dir,
                                   dry_run=args.dry_run)
    else:
        print("\n[3/7] No patches — default parameters")

    if args.dry_run:
        print("\n[DRY RUN] Stopping here.")
        save_metadata(run_dir, args, patch_logs)
        return

    # ---- [4] Temporal aggregation ----
    print(f"\n[4/7] Temporal aggregation (read, {args.nbr_td} TDs)...")
    my_model.init_ta(algo="read")

    # ---- [5] Generate .dat files + snapshot ----
    print("[5/7] Generating .dat files...")
    my_model.print_td_data()
    my_model.print_data(indep=True)
    snapshot_inputs(my_model.cs_dir, run_dir)

    # ---- [6] Solve ----
    print("\n[6/7] Solving...")
    solve_result_num = solve_with_fallback(my_model, run_dir,
                                           use_simplex=args.simplex,
                                           use_crossover=args.crossover)

    desc = _describe_status(solve_result_num)
    if solve_result_num != 0:
        print(f"\n  {'=' * 60}")
        print(f"  SOLVE FAILED — code {solve_result_num}: {desc}")
        print(f"  Check {run_dir / 'log.txt'} for details.")
        print(f"  {'=' * 60}")
        save_metadata(run_dir, args, patch_logs,
                      solve_info={"status": "FAILED", "code": solve_result_num,
                                  "desc": desc})
        sys.exit(1)

    # ---- [7] Results + score + plots ----
    print("\n[7/7] Collecting results...")
    my_model.get_year_results()
    my_model.prints_esom(inputs=True, outputs=True, solve_info=True)

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
        append_to_rankings(run_name, score, errors)
    else:
        print("  Could not compute score (missing output files)")

    # Validation plots
    if not args.skip_plots and outputs_dir.exists():
        run_validation_plots(run_dir)

    # Metadata
    save_metadata(run_dir, args, patch_logs, score=score, errors=errors,
                  solve_info={"status": "OK", "code": 0, "desc": "optimal"})

    print(f"\n{'=' * 70}")
    print(f"  RUN COMPLETE: {run_name}")
    if score is not None and score != float("inf"):
        print(f"  Score: {score:.1f}% weighted error")
    print(f"  Outputs: {outputs_dir}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
