#!/usr/bin/env python3
"""
Score ALL Finland 2017 calibration runs against reality targets.

Scans every directory under case_studies/FI/, extracts output metrics,
computes weighted absolute percentage error vs. reality, and writes
a 100%-coverage run_rankings.csv.

Usage:
    python scripts/score_all_fi_runs.py              # score all, write CSV
    python scripts/score_all_fi_runs.py --verbose     # with per-metric breakdowns
    python scripts/score_all_fi_runs.py --top 5       # show top N in detail
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
CASE_STUDIES_FI = REPO_ROOT / "case_studies" / "FI"
REALITY_CSV = REPO_ROOT / "calibration" / "reality" / "finland_2017_reference.csv"
OUTPUT_CSV = REPO_ROOT / "calibration" / "run_rankings.csv"

# ---------------------------------------------------------------------------
# Reality targets: metric_key → (target_value, weight)
#   PE_*   = primary energy in TWh
#   ELEC_* = electricity generation in TWh
#   CO2    = emissions in MtCO2
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

# Provenance categories
PROVENANCE_RULES = [
    # (regex on short name, label)
    (r"^p(\d+)", lambda m: "user-patch" if int(m.group(1)) <= 21 else "copilot-patch"),
    (r"^v\d",     lambda _: "named-version"),
    (r"^ref_",    lambda _: "reference"),
]


def classify_provenance(run_name: str) -> str:
    """Classify a run by provenance based on its name."""
    short = run_name.replace("calib_2017_finland_", "")
    for pattern, labeller in PROVENANCE_RULES:
        m = re.match(pattern, short)
        if m:
            return labeller(m)
    return "other"


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_solve_info(outputs_dir: Path) -> dict:
    """Parse Solve_info.csv (tab-mangled key-value pairs)."""
    si_path = outputs_dir / "Solve_info.csv"
    if not si_path.exists():
        return {}
    info = {}
    with open(si_path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                key = parts[0].strip().replace("\t", "")
                val = parts[1].strip().replace("\t", "")
                try:
                    info[key] = float(val)
                except ValueError:
                    info[key] = val
    return info


# Threshold: objective above this with code=0 signals tolerance violations
# Normal runs have objectives ~40K-60K; anything above 500K is suspicious
INVALID_TOL_THRESHOLD = 500_000


def determine_status(run_dir: Path) -> str:
    """
    Determine solve status:
      EMPTY       – no outputs dir or outputs dir is empty
      NO_SOLVE    – outputs exist but no Solve_info.csv
      FAILED      – solve_result_num not in {0, 100}
      INFEASIBLE  – solve_result_num == 200
      INVALID_TOL – solve_result_num in {0,100} but TotalCost > 1e10
      OK          – solve_result_num in {0, 100} and TotalCost reasonable
      UNKNOWN     – can't determine
    """
    outputs = run_dir / "outputs"
    if not outputs.exists():
        return "EMPTY"
    csv_files = list(outputs.glob("*.csv"))
    if len(csv_files) == 0:
        return "EMPTY"
    
    si = parse_solve_info(outputs)
    if not si:
        return "NO_SOLVE"
    
    srn = si.get("solve_result_num", None)
    if srn is None:
        return "UNKNOWN"
    srn = int(srn)
    if srn in (0, 100):
        # Check Objective.csv for tolerance violations
        obj_path = outputs / "Objective.csv"
        if obj_path.exists():
            try:
                with open(obj_path) as f:
                    lines = f.read().strip().split("\n")
                    obj_val = float(lines[-1].split(",")[-1].strip())
                    if obj_val > INVALID_TOL_THRESHOLD:
                        return "INVALID_TOL"
            except Exception:
                pass
        return "OK"
    if srn == 200:
        return "INFEASIBLE"
    return f"FAILED({srn})"


def extract_metrics(outputs_dir: Path) -> dict:
    """Extract PE, electricity, and CO2 metrics from run outputs."""
    metrics = {}
    
    # ---- Resources.csv → primary energy ----
    res_path = outputs_dir / "Resources.csv"
    if res_path.exists():
        try:
            df = pd.read_csv(res_path)
            lookup = {}
            for _, row in df.iterrows():
                name = row["Resources"]
                total = row.get("R_year_local", 0) + row.get("R_year_exterior", 0)
                lookup[name] = total
            
            metrics["PE_BIOMASS"] = sum(
                lookup.get(r, 0) for r in
                ["WOOD", "WET_BIOMASS", "BIOWASTE", "BIOMASS_RESIDUES", "ENERGY_CROPS_2"]
            ) / 1000  # GWh → TWh
            
            metrics["PE_OIL"] = sum(
                lookup.get(r, 0) for r in
                ["GASOLINE", "DIESEL", "LFO", "JET_FUEL"]
            ) / 1000
            
            metrics["PE_GAS"]     = lookup.get("GAS", 0) / 1000
            metrics["PE_COAL"]    = lookup.get("COAL", 0) / 1000
            metrics["PE_NUCLEAR"] = lookup.get("URANIUM", 0) / 1000
            metrics["PE_HYDRO"]   = lookup.get("RES_HYDRO", 0) / 1000
            metrics["PE_WIND"]    = lookup.get("RES_WIND", 0) / 1000
        except Exception as e:
            metrics["_resources_error"] = str(e)
    
    # ---- Year_balance.csv → electricity generation ----
    yb_path = outputs_dir / "Year_balance.csv"
    if yb_path.exists():
        try:
            df = pd.read_csv(yb_path, index_col="Elements")
            
            if "ELECTRICITY" in df.columns:
                # Nuclear
                if "NUCLEAR" in df.index:
                    metrics["ELEC_NUCLEAR"] = max(0.0, df.loc["NUCLEAR", "ELECTRICITY"]) / 1000
                
                # Hydro (dam + river)
                hydro = 0.0
                for tech in ["HYDRO_DAM", "HYDRO_RIVER"]:
                    if tech in df.index:
                        hydro += max(0.0, float(df.loc[tech, "ELECTRICITY"]))
                metrics["ELEC_HYDRO"] = hydro / 1000
                
                # Wind (onshore + offshore)
                wind = 0.0
                for tech in ["WIND_ONSHORE", "WIND_OFFSHORE"]:
                    if tech in df.index:
                        wind += max(0.0, float(df.loc[tech, "ELECTRICITY"]))
                metrics["ELEC_WIND"] = wind / 1000

                # Solar
                solar = 0.0
                for tech in ["PV_ROOFTOP", "PV_UTILITY"]:
                    if tech in df.index:
                        solar += max(0.0, float(df.loc[tech, "ELECTRICITY"]))
                metrics["ELEC_SOLAR"] = solar / 1000

                # CHP (all cogeneration technologies)
                chp_techs = [
                    "DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_COAL",
                    "DHN_COGEN_WASTE", "DHN_COGEN_OIL",
                    "IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_COAL",
                    "IND_COGEN_WASTE",
                    "DEC_COGEN_GAS", "DEC_COGEN_OIL",
                    "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2",
                ]
                chp = 0.0
                for tech in chp_techs:
                    if tech in df.index:
                        chp += max(0.0, float(df.loc[tech, "ELECTRICITY"]))
                metrics["ELEC_CHP"] = chp / 1000

                # Condensation (electricity-only thermal plants)
                cond_techs = ["CCGT", "OCGT", "COAL_US", "COAL_IGCC",
                              "CCGT_AMMONIA", "BIOMASS_TO_POWER"]
                cond = 0.0
                for tech in cond_techs:
                    if tech in df.index:
                        cond += max(0.0, float(df.loc[tech, "ELECTRICITY"]))
                metrics["ELEC_CONDENSATION"] = cond / 1000
        except Exception as e:
            metrics["_yearbalance_error"] = str(e)
    
    # ---- Gwp_breakdown.csv → CO2 ----
    gwp_path = outputs_dir / "Gwp_breakdown.csv"
    if gwp_path.exists():
        try:
            df = pd.read_csv(gwp_path)
            if "CO2_net" in df.columns:
                metrics["CO2"] = df["CO2_net"].sum() / 1000  # ktCO2 → MtCO2
            elif "GWP_op" in df.columns:
                metrics["CO2"] = df["GWP_op"].sum() / 1000
        except Exception as e:
            metrics["_gwp_error"] = str(e)
    
    # ---- Objective.csv ----
    obj_path = outputs_dir / "Objective.csv"
    if obj_path.exists():
        try:
            with open(obj_path) as f:
                lines = f.read().strip().split("\n")
                if len(lines) >= 2:
                    metrics["_objective"] = float(lines[1].strip())
                elif len(lines) == 1:
                    metrics["_objective"] = float(lines[0].strip())
        except Exception:
            pass
    
    return metrics


def compute_score(metrics: dict) -> tuple[float, dict]:
    """
    Compute weighted average absolute percentage error.
    Returns (score, per_metric_errors).
    Score = inf if no metrics available.
    """
    errors = {}
    weighted_sum = 0.0
    weight_sum = 0.0
    
    for key, (target, weight) in REALITY_TARGETS.items():
        if key in metrics and target > 0:
            model_val = metrics[key]
            pct_error = abs(model_val - target) / target * 100
            errors[key] = {
                "model": model_val,
                "target": target,
                "pct_error": pct_error,
                "weight": weight,
            }
            weighted_sum += pct_error * weight
            weight_sum += weight
    
    score = weighted_sum / weight_sum if weight_sum > 0 else float("inf")
    return score, errors


def get_run_timestamp(run_dir: Path) -> str:
    """Get modification time of the run directory."""
    try:
        t = run_dir.stat().st_mtime
        return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def scan_all_runs(include_archive: bool = False) -> list[dict]:
    """Scan all run directories and produce scored results."""
    results = []
    
    if not CASE_STUDIES_FI.exists():
        print(f"ERROR: {CASE_STUDIES_FI} not found")
        sys.exit(1)
    
    # Collect all run directories to scan
    run_dirs = []
    for d in sorted(CASE_STUDIES_FI.iterdir()):
        if not d.is_dir():
            continue
        if d.name in ("__pycache__", ".ipynb_checkpoints", "00_td_dat"):
            continue
        if d.name.startswith("_archive"):
            if include_archive:
                # Recurse into archive subdirectories
                for sub in sorted(d.iterdir()):
                    if sub.is_dir():
                        run_dirs.append((sub, f"archive/{sub.name}"))
            continue
        if d.name == "manual_runs":
            # Recurse into manual_runs subdirectories
            for sub in sorted(d.iterdir()):
                if sub.is_dir():
                    run_dirs.append((sub, f"manual_runs/{sub.name}"))
            continue
        run_dirs.append((d, d.name))
    
    for d, display_name in run_dirs:
        
        status = determine_status(d)
        provenance = classify_provenance(d.name)
        timestamp = get_run_timestamp(d)
        
        row = {
            "run_name": display_name,
            "status": status,
            "provenance": provenance,
            "timestamp": timestamp,
            "score": float("inf"),
            "notes": "",
        }
        
        # Extract metrics and score for OK and INVALID_TOL runs
        if status in ("OK", "INVALID_TOL"):
            metrics = extract_metrics(d / "outputs")
            score, errors = compute_score(metrics)
            row["score"] = round(score, 2) if score != float("inf") else float("inf")
            
            # Store individual metric values
            for key in REALITY_TARGETS:
                row[f"{key}_model"] = round(metrics.get(key, float("nan")), 2)
                if key in errors:
                    row[f"{key}_err%"] = round(errors[key]["pct_error"], 1)
                else:
                    row[f"{key}_err%"] = float("nan")
            
            # Store objective
            if "_objective" in metrics:
                row["objective"] = metrics["_objective"]
            
            # Flag parse errors
            errs = [v for k, v in metrics.items() if k.startswith("_") and k.endswith("_error")]
            if errs:
                row["notes"] = "; ".join(errs)
        else:
            row["notes"] = status
            for key in REALITY_TARGETS:
                row[f"{key}_model"] = float("nan")
                row[f"{key}_err%"] = float("nan")
        
        results.append(row)
    
    return results


def write_rankings(results: list[dict]):
    """Write run_rankings.csv with all results."""
    # Build ordered columns
    base_cols = ["run_name", "status", "provenance", "score", "timestamp"]
    metric_cols = []
    for key in REALITY_TARGETS:
        metric_cols.extend([f"{key}_model", f"{key}_err%"])
    extra_cols = ["objective", "notes"]
    
    all_cols = base_cols + metric_cols + extra_cols
    
    df = pd.DataFrame(results)
    # Ensure all columns exist
    for c in all_cols:
        if c not in df.columns:
            df[c] = float("nan")
    
    df = df[all_cols]
    df = df.sort_values("score", ascending=True)
    
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    return df


def print_summary(df: pd.DataFrame, top_n: int = 5, verbose: bool = False):
    """Print a human-readable summary."""
    total = len(df)
    ok = len(df[df["status"] == "OK"])
    empty = len(df[df["status"] == "EMPTY"])
    inv_tol = len(df[df["status"] == "INVALID_TOL"])
    failed = len(df[~df["status"].isin(["OK", "EMPTY", "INVALID_TOL"])])
    
    print(f"\n{'=' * 80}")
    print(f"FINLAND 2017 RUN SCORING — {total} runs scanned")
    print(f"  OK: {ok}   INVALID_TOL: {inv_tol}   EMPTY: {empty}   FAILED/OTHER: {failed}")
    print(f"{'=' * 80}\n")
    
    # Rankings table
    print(f"{'Rank':<5} {'Score':>7} {'Status':<10} {'Prov':<15} {'Run Name'}")
    print("-" * 90)
    
    for i, (_, row) in enumerate(df.iterrows(), 1):
        score_str = f"{row['score']:.1f}" if row["score"] != float("inf") else "---"
        print(f"{i:<5} {score_str:>7} {row['status']:<10} {row['provenance']:<15} {row['run_name']}")
    
    # Detailed top N
    if verbose or top_n > 0:
        ok_df = df[df["status"] == "OK"].head(top_n)
        if len(ok_df) > 0:
            print(f"\n{'=' * 80}")
            print(f"DETAILED BREAKDOWN — Top {min(top_n, len(ok_df))} runs")
            print(f"{'=' * 80}")
            
            for _, row in ok_df.iterrows():
                print(f"\n### {row['run_name']}  (Score: {row['score']:.1f}, Prov: {row['provenance']})")
                print(f"  {'Metric':<15} {'Model':>10} {'Target':>10} {'Error%':>10}")
                print(f"  {'-'*50}")
                for key, (target, weight) in REALITY_TARGETS.items():
                    model_col = f"{key}_model"
                    err_col = f"{key}_err%"
                    model_val = row.get(model_col, float("nan"))
                    err_val = row.get(err_col, float("nan"))
                    if pd.notna(model_val):
                        print(f"  {key:<15} {model_val:>10.2f} {target:>10.1f} {err_val:>9.1f}%")
                    else:
                        print(f"  {key:<15} {'N/A':>10} {target:>10.1f} {'N/A':>10}")
    
    print(f"\nRankings saved to: {OUTPUT_CSV}")
    
    # Recommend baseline
    ok_df = df[df["status"] == "OK"]
    if len(ok_df) > 0:
        best = ok_df.iloc[0]
        print(f"\nBEST RUN: {best['run_name']}  (Score: {best['score']:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Score all Finland 2017 calibration runs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-metric breakdowns")
    parser.add_argument("--top", "-t", type=int, default=5, help="Number of top runs to detail (default: 5)")
    parser.add_argument("--include-archive", action="store_true",
                        help="Also scan _archive_*/ directories")
    args = parser.parse_args()
    
    results = scan_all_runs(include_archive=args.include_archive)
    df = write_rankings(results)
    print_summary(df, top_n=args.top, verbose=args.verbose)


if __name__ == "__main__":
    main()
