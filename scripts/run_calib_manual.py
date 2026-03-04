#!/usr/bin/env python3
"""
==========================================================================
  Manual Calibration Runner for Finland 2017 — ESMC Framework Edition
==========================================================================

WHAT THIS DOES
--------------
Runs the EnergyScope Multi-Cells model for Finland 2017 with optional
patches applied IN-MEMORY (never modifies Data/ CSV files). Safe to
Ctrl-C at any time.

HOW IT WORKS
------------
1. Creates ESMC model with your run name as case_study
2. Reads Data/2017 files via the standard ESMC pipeline
3. Applies patch CSV(s) to in-memory DataFrames before .dat generation
4. Runs the solver (CPLEX by default)
5. Saves outputs to case_studies/FI/manual_runs/<timestamp>__<name>/outputs/
6. Auto-scores against Finland 2017 reality targets (14 metrics)
7. Generates validation plots (PE, electricity, CO2, CHP breakdown, error chart)
8. Appends score to calibration/run_rankings.csv

USAGE EXAMPLES
--------------
    # Basic run with default config (no patches)
    python run_calib_manual.py -n baseline_check

    # Apply a patch
    python run_calib_manual.py -n test_nuclear --patch calibration/patches/p01_disable_futuretechs.csv

    # Stack multiple patches
    python run_calib_manual.py -n combined --patch patches/p01.csv --patch patches/p02.csv

    # Dry run (shows what patches would do, no model execution)
    python run_calib_manual.py -n test --patch patches/p01.csv --dry-run

    # Use f_perc=False (disables all fmin_perc/fmax_perc constraints)
    python run_calib_manual.py -n nofperc --no-fperc

    # Reuse existing TD data (much faster if 00_td_dat already populated)
    python run_calib_manual.py -n quick --td-algo read

PATCH FORMAT (CSV)
------------------
    file,parameter,technology_or_resource,value
    Technologies.csv,f_max,NUCLEAR,2.8
    Technologies.csv,f_min,NUCLEAR,2.5
    Resources.csv,avail_exterior,COAL,30000

DATA SAFETY
-----------
- Data/2017/ is NEVER modified.  All patches happen in-memory.
- Each run gets a timestamped directory so nothing is overwritten.
- If the solver fails, outputs may be incomplete but nothing is corrupted.
- After running, check calibration/run_rankings.csv for your score.

REALITY TARGETS
---------------
Scoring uses Statistics Finland 2017 official data:
  - Primary energy: biomass 100, oil 82, gas 20, coal+peat 35, nuclear 65,
    hydro 15, wind 5 TWh
  - Electricity (by production mode): nuclear 21.6, hydro 14.6, wind 4.8,
    CHP 20.735, condensation 3.284, solar 0.044 TWh
  - CO2: 41.2 MtCO2
  Source: calibration/reality/finland_2017_reference.csv

The scorer reports a WEIGHTED AVERAGE of absolute percentage errors.
Lower is better;  <15% is a reasonable calibration target.  The validation
plotter (validate_run.py) is automatically called after scoring, generating
PE/electricity/CO2 comparison charts, a CHP+condensation diagnostic, and a
colour-coded error chart under <run_dir>/validation_plots/.

TYPICAL WORKFLOW
----------------
1. Edit/create a patch CSV in calibration/patches/
2. Run:  python run_calib_manual.py -n my_test --patch patches/my.csv
3. Check terminal scorecard  →  quick pass/fail
4. Open validation_plots/error_chart.png  →  per-metric diagnostics
5. If promising, compare to baselines in calibration/run_rankings.csv

==========================================================================
"""

import argparse
import json
import os
import re
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
REALITY_REF = CALIBRATION_DIR / "reality" / "finland_2017_reference.csv"

# ---------------------------------------------------------------------------
# Reality targets for scoring (same as score_all_fi_runs.py)
# ---------------------------------------------------------------------------
REALITY_TARGETS = {
    "PE_BIOMASS":    (100.0, 1.5),
    "PE_OIL":        (82.0,  1.5),
    "PE_GAS":        (20.0,  1.0),
    "PE_COAL":       (35.0,  1.5),
    "PE_NUCLEAR":    (65.0,  1.0),
    "PE_HYDRO":      (15.0,  0.8),
    "PE_WIND":       (5.0,   0.8),
    "ELEC_NUCLEAR":      (21.6,   1.5),
    "ELEC_HYDRO":        (14.6,   1.2),
    "ELEC_WIND":         (4.8,    1.0),
    "ELEC_CHP":          (20.735, 1.2),
    "ELEC_CONDENSATION": (3.284,  0.8),
    "ELEC_SOLAR":        (0.044,  0.3),
    "CO2":               (41.2,   2.0),
}


# ===================================================================
# CLI
# ===================================================================

def parse_args():
    p = argparse.ArgumentParser(
        description="Manual calibration runner — Finland 2017",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See script header for detailed usage examples and patch format.",
    )
    p.add_argument("-n", "--run-name", required=True,
                   help="Short name for this run (e.g. test_nuclear)")
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
                   help="Minimum RE share of primary energy (default: None = no constraint)")
    p.add_argument("--nbr-td", type=int, default=12,
                   help="Number of typical days (default: 12)")
    p.add_argument("--td-algo", default="read", choices=["read", "kmedoid"],
                   help="TD algorithm: 'read' (reuse existing) or 'kmedoid' (recompute)")
    p.add_argument("--ampl-path", default=None,
                   help="Path to ampl executable (default: use PATH)")
    p.add_argument("--skip-score", action="store_true",
                   help="Skip auto-scoring after run")
    return p.parse_args()


# ===================================================================
# Patch application (in-memory)
# ===================================================================

def apply_patches_in_memory(model, patch_files, dry_run=False):
    """
    Apply CSV patch files by modifying region.data DataFrames in-memory.
    
    This is safe: Data/2017/ CSV files are NEVER touched.
    
    Returns list of patch logs for metadata.
    """
    patch_logs = []
    
    # After init_regions(), region DataFrames are index-based:
    #   Technologies: index = "Technologies param" (e.g. NUCLEAR, CCGT)
    #   Resources:    index = "parameter name" (e.g. GASOLINE, COAL)
    #   Demands:      index = "parameter name" (e.g. ELECTRICITY)
    #   Misc:         dict-like (keys in index)
    # Map from CSV filename to data_dict_key
    FILE_MAP = {
        "Technologies.csv": "Technologies",
        "Resources.csv":    "Resources",
        "Demands.csv":      "Demands",
        "Misc.csv":         "Misc",
    }
    
    for patch_path in patch_files:
        log = {"file": str(patch_path), "changes": []}
        df = pd.read_csv(patch_path)
        
        print(f"\n  Patch: {patch_path.name} ({len(df)} changes)")
        
        for _, row in df.iterrows():
            target_file = row["file"].strip()
            param = row["parameter"].strip()
            entity = str(row["technology_or_resource"]).strip()
            new_val = row["value"]
            
            if target_file not in FILE_MAP:
                print(f"    SKIP: unknown file {target_file}")
                continue
            
            data_key = FILE_MAP[target_file]
            
            # Apply to each region (for FI single-country, there's just one)
            for r_code, region in model.regions.items():
                if data_key not in region.data or region.data[data_key] is None:
                    print(f"    SKIP: {data_key} not in region {r_code}")
                    continue
                
                rdf = region.data[data_key]
                
                # All region DataFrames are indexed by entity name
                if entity not in rdf.index:
                    print(f"    SKIP: {entity} not found in {r_code}/{data_key}")
                    continue
                
                if param not in rdf.columns:
                    print(f"    SKIP: column {param} not in {r_code}/{data_key}")
                    continue
                
                old_val = rdf.loc[entity, param]
                if not dry_run:
                    rdf.loc[entity, param] = new_val
                
                prefix = "[DRY] " if dry_run else ""
                print(f"    {prefix}{r_code}/{entity}.{param}: {old_val} -> {new_val}")
                
                log["changes"].append({
                    "region": r_code,
                    "data_key": data_key,
                    "entity": entity,
                    "parameter": param,
                    "old_value": str(old_val),
                    "new_value": str(new_val),
                })
        
        patch_logs.append(log)
    
    return patch_logs


# ===================================================================
# Scoring (lightweight, reuses same logic as score_all_fi_runs.py)
# ===================================================================

def extract_and_score(outputs_dir):
    """Quick extraction + scoring from a single run's outputs."""
    metrics = {}
    
    # Resources
    res_path = outputs_dir / "Resources.csv"
    if res_path.exists():
        df = pd.read_csv(res_path)
        lookup = {}
        for _, row in df.iterrows():
            lookup[row["Resources"]] = row.get("R_year_local", 0) + row.get("R_year_exterior", 0)
        
        metrics["PE_BIOMASS"] = sum(lookup.get(r, 0) for r in
            ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"]) / 1000
        metrics["PE_OIL"] = sum(lookup.get(r, 0) for r in
            ["GASOLINE", "DIESEL", "LFO", "JET_FUEL"]) / 1000
        metrics["PE_GAS"]     = lookup.get("GAS", 0) / 1000
        metrics["PE_COAL"]    = lookup.get("COAL", 0) / 1000
        metrics["PE_NUCLEAR"] = lookup.get("URANIUM", 0) / 1000
        metrics["PE_HYDRO"]   = lookup.get("RES_HYDRO", 0) / 1000
        metrics["PE_WIND"]    = lookup.get("RES_WIND", 0) / 1000
    
    # Year_balance
    yb_path = outputs_dir / "Year_balance.csv"
    if yb_path.exists():
        df = pd.read_csv(yb_path, index_col="Elements")
        if "ELECTRICITY" in df.columns:
            if "NUCLEAR" in df.index:
                metrics["ELEC_NUCLEAR"] = max(0.0, float(df.loc["NUCLEAR", "ELECTRICITY"])) / 1000
            hydro = sum(max(0.0, float(df.loc[t, "ELECTRICITY"])) for t in ["HYDRO_DAM", "HYDRO_RIVER"] if t in df.index)
            metrics["ELEC_HYDRO"] = hydro / 1000
            wind = sum(max(0.0, float(df.loc[t, "ELECTRICITY"])) for t in ["WIND_ONSHORE", "WIND_OFFSHORE"] if t in df.index)
            metrics["ELEC_WIND"] = wind / 1000

            # Solar
            solar = sum(max(0.0, float(df.loc[t, "ELECTRICITY"])) for t in ["PV_ROOFTOP", "PV_UTILITY"] if t in df.index)
            metrics["ELEC_SOLAR"] = solar / 1000

            # CHP (all cogeneration)
            chp_techs = [
                "DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL",
                "DHN_COGEN_WASTE", "DHN_COGEN_OIL",
                "IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_COAL",
                "IND_COGEN_WASTE",
                "DEC_COGEN_GAS", "DEC_COGEN_OIL",
                "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2",
            ]
            chp = sum(max(0.0, float(df.loc[t, "ELECTRICITY"])) for t in chp_techs if t in df.index)
            metrics["ELEC_CHP"] = chp / 1000

            # Condensation (electricity-only thermal)
            cond_techs = ["CCGT", "OCGT", "COAL_US", "COAL_IGCC",
                          "CCGT_AMMONIA", "BIOMASS_TO_POWER"]
            cond = sum(max(0.0, float(df.loc[t, "ELECTRICITY"])) for t in cond_techs if t in df.index)
            metrics["ELEC_CONDENSATION"] = cond / 1000
    
    # GWP
    gwp_path = outputs_dir / "Gwp_breakdown.csv"
    if gwp_path.exists():
        df = pd.read_csv(gwp_path)
        if "CO2_net" in df.columns:
            metrics["CO2"] = df["CO2_net"].sum() / 1000
        elif "GWP_op" in df.columns:
            metrics["CO2"] = df["GWP_op"].sum() / 1000
    
    # Score
    weighted_sum = 0.0
    weight_sum = 0.0
    errors = {}
    for key, (target, weight) in REALITY_TARGETS.items():
        if key in metrics and target > 0:
            pct_err = abs(metrics[key] - target) / target * 100
            errors[key] = {"model": metrics[key], "target": target, "pct_error": pct_err}
            weighted_sum += pct_err * weight
            weight_sum += weight
    
    score = weighted_sum / weight_sum if weight_sum > 0 else float("inf")
    return score, errors


def print_scorecard(score, errors):
    """Print a readable scorecard."""
    print(f"\n{'=' * 60}")
    print(f"  SCORE: {score:.1f}% weighted average error")
    print(f"{'=' * 60}")
    print(f"  {'Metric':<15} {'Model':>10} {'Target':>10} {'Error':>10}")
    print(f"  {'-' * 50}")
    for key, info in sorted(errors.items()):
        print(f"  {key:<15} {info['model']:>10.2f} {info['target']:>10.1f} {info['pct_error']:>9.1f}%")


def append_to_rankings(run_name, run_dir, score, errors):
    """Append this run's score to calibration/run_rankings.csv."""
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
        # Remove old entry with same name if exists
        df = df[df["run_name"] != run_dir.name]
        df = pd.concat([df, new_row], ignore_index=True)
        df = df.sort_values("score", ascending=True)
    else:
        df = new_row
    
    df.to_csv(RANKINGS_CSV, index=False)
    print(f"  Rankings updated: {RANKINGS_CSV}")


# ===================================================================
# Metadata
# ===================================================================

def save_metadata(run_dir, args, patch_logs, score=None, solve_status=None):
    """Save a JSON metadata file for reproducibility."""
    meta = {
        "run_name": args.run_name,
        "description": args.description,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "f_perc": not args.no_fperc,
            "gwp_limit_overall": args.gwp_limit,
            "re_share_primary": args.re_share,
            "nbr_td": args.nbr_td,
            "td_algo": args.td_algo,
        },
        "patches": patch_logs,
        "score": score,
        "solve_status": solve_status or "OK",
        "command": " ".join(sys.argv),
        "git": get_git_info(),
    }
    path = run_dir / "run_metadata.json"
    with open(path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"  Metadata: {path}")


def get_git_info():
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"],
                                capture_output=True, text=True, cwd=str(REPO_ROOT)).stdout.strip()
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True, cwd=str(REPO_ROOT)).stdout.strip()
        return {"commit": commit, "branch": branch}
    except Exception:
        return {}


# ===================================================================
# Main
# ===================================================================

def main():
    args = parse_args()
    
    # Build timestamped run directory name
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use manual_runs/ subdirectory for clean separation
    case_study_name = f"manual_runs/{ts}__{args.run_name}"
    
    print("=" * 70)
    print(f"  MANUAL CALIBRATION RUN: {args.run_name}")
    print(f"  Output: case_studies/FI/{case_study_name}/")
    print("=" * 70)
    
    # ---- Config ----
    f_perc = not args.no_fperc
    config = {
        "case_study": case_study_name,
        "comment": args.description or f"manual run {args.run_name}",
        "regions_names": ["FI"],
        "gwp_limit_overall": args.gwp_limit,
        "re_share_primary": args.re_share,
        "f_perc": f_perc,
        "year": 2017,
    }
    
    print(f"\n  Config: f_perc={f_perc}, gwp_limit={args.gwp_limit}, "
          f"re_share={args.re_share}, nbr_td={args.nbr_td}")
    
    # ---- Initialize ESMC ----
    print("\n[1/7] Initializing ESMC model...")
    ampl_path_arg = Path(args.ampl_path) if args.ampl_path else None
    my_model = Esmc(config, nbr_td=args.nbr_td)
    run_dir = my_model.cs_dir  # case_studies/FI/manual_runs/<ts>__<name>
    
    print(f"  Run directory: {run_dir}")
    
    # ---- Read data ----
    print("\n[2/7] Reading data...")
    my_model.read_data_indep()
    my_model.init_regions()
    
    # ---- Apply patches (in-memory, safe) ----
    patch_files = []
    for pf in args.patch:
        p = Path(pf)
        if not p.is_absolute():
            p = REPO_ROOT / pf
        if not p.exists():
            p = CALIBRATION_DIR / "patches" / pf
        if p.exists():
            patch_files.append(p)
        else:
            print(f"  ERROR: patch not found: {pf}")
            print(f"         Tried: {REPO_ROOT / pf}")
            print(f"         Tried: {CALIBRATION_DIR / 'patches' / pf}")
            sys.exit(1)
    
    patch_logs = []
    if patch_files:
        print(f"\n[3/7] Applying {len(patch_files)} patch(es) in-memory...")
        patch_logs = apply_patches_in_memory(my_model, patch_files, dry_run=args.dry_run)
    else:
        print("\n[3/7] No patches — running with default Data/2017 inputs")
    
    if args.dry_run:
        print("\n[DRY RUN] Stopping here. No model execution, no files modified.")
        save_metadata(run_dir, args, patch_logs)
        return
    
    # ---- Temporal aggregation ----
    print(f"\n[4/7] Temporal aggregation (algo={args.td_algo})...")
    my_model.init_ta(algo=args.td_algo, ampl_path=ampl_path_arg)
    
    # ---- Print data (.dat generation from in-memory DataFrames) ----
    print("\n[5/7] Generating .dat files...")
    my_model.print_td_data()
    my_model.print_data(indep=True)
    
    # ---- Solve ----
    print("\n[6/7] Setting up and solving ESOM...")
    my_model.set_esom(ampl_path=ampl_path_arg)
    my_model.solve_esom()

    # ---- Check solve status ----
    my_model.esom.get_solve_info()
    solve_result_num = my_model.esom.t[2]
    if solve_result_num != 0:
        status_map = {
            -1: "unknown (barrier failed, likely infeasible)",
        }
        if 0 < solve_result_num < 100:
            desc = "solved (non-zero sub-status)"
        elif 100 <= solve_result_num < 200:
            desc = "uncertain (solved but optimality not guaranteed)"
        elif 200 <= solve_result_num < 300:
            desc = "INFEASIBLE (constraints are contradictory)"
        elif 300 <= solve_result_num < 400:
            desc = "UNBOUNDED"
        elif 400 <= solve_result_num < 500:
            desc = "LIMIT (time/iteration limit reached)"
        else:
            desc = status_map.get(solve_result_num, f"FAILURE (code {solve_result_num})")
        print(f"\n  {'=' * 60}")
        print(f"  SOLVE FAILED — solve_result_num = {solve_result_num}")
        print(f"  Meaning: {desc}")
        print(f"  The outputs from this run are UNRELIABLE.")
        print(f"  Check {run_dir.name}/log.txt for details.")
        print(f"  {'=' * 60}")
        # Still save metadata so user can see what was attempted
        save_metadata(run_dir, args, patch_logs, score=None,
                      solve_status=f"FAILED ({solve_result_num}: {desc})")
        sys.exit(1)
    
    # ---- Results ----
    print("\n[7/7] Collecting results...")
    my_model.get_year_results()
    my_model.prints_esom(inputs=True, outputs=True, solve_info=True)
    
    # Close AMPL
    try:
        my_model.esom.ampl.close()
    except Exception:
        pass
    
    # ---- Auto-score ----
    outputs_dir = run_dir / "outputs"
    score = None
    if not args.skip_score and outputs_dir.exists():
        score, errors = extract_and_score(outputs_dir)
        if score != float("inf"):
            print_scorecard(score, errors)
            append_to_rankings(args.run_name, run_dir, score, errors)
        else:
            print("\n  Could not compute score (missing output files)")
    
    # ---- Validation plots (via validate_run.py logic) ----
    if not args.skip_score and outputs_dir.exists():
        try:
            from validate_run import load_reality, validate_one as _validate_one
            reality = load_reality()
            _validate_one(run_dir, reality)
            print(f"  Validation plots: {run_dir / 'validation_plots'}")
        except ImportError:
            print("  WARNING: validate_run.py not importable — skipping plots")
        except Exception as e:
            print(f"  WARNING: validation plots failed: {e}")

    # ---- Metadata ----
    save_metadata(run_dir, args, patch_logs, score=score)
    
    print(f"\n{'=' * 70}")
    print(f"  RUN COMPLETE: {run_dir.name}")
    if score is not None and score != float("inf"):
        print(f"  Score: {score:.1f}% weighted error")
    print(f"  Outputs: {outputs_dir}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
