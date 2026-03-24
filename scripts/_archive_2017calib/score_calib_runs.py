#!/usr/bin/env python3
"""
Score and rank calibration runs against Finland 2017 reality targets.

Reads outputs from all calib_2017_finland* runs and computes weighted
absolute percentage errors vs. reality targets.
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent

# Reality targets (from calibration/reality/finland_2017_reference.csv)
REALITY_TARGETS = {
    # Primary energy (TWh)
    "PE_BIOMASS": (100.0, 1.5),    # (value, weight)
    "PE_OIL": (82.0, 1.5),
    "PE_GAS": (20.0, 1.0),
    "PE_COAL": (35.0, 1.5),
    "PE_NUCLEAR": (65.0, 1.0),
    "PE_HYDRO": (15.0, 0.8),
    "PE_WIND": (5.0, 0.8),
    # Electricity (TWh)
    "ELEC_NUCLEAR": (21.6, 1.5),
    "ELEC_HYDRO": (14.6, 1.2),
    "ELEC_WIND": (4.8, 1.0),
    # Emissions (MtCO2)
    "CO2": (41.2, 2.0),
}


def extract_metrics_from_run(outputs_dir: Path) -> dict:
    """Extract key metrics from a single run's outputs."""
    metrics = {}
    
    # Check solve status first
    solve_info_path = outputs_dir / "Solve_info.csv"
    if solve_info_path.exists():
        df = pd.read_csv(solve_info_path)
        if "solve_result_num" in df.columns:
            solve_status = df["solve_result_num"].iloc[0]
            if solve_status not in [0, 100]:
                return {"FAILED": True, "solve_status": solve_status}
    
    # Resources.csv for primary energy
    resources_path = outputs_dir / "Resources.csv"
    if resources_path.exists():
        df = pd.read_csv(resources_path)
        # Create lookup dict
        res_lookup = {}
        for _, row in df.iterrows():
            res_name = row["Resources"]
            # Use R_year_local + R_year_exterior for total consumption
            total = row.get("R_year_local", 0) + row.get("R_year_exterior", 0)
            res_lookup[res_name] = total
        
        # Map resources to PE categories (values in GWh, convert to TWh)
        metrics["PE_BIOMASS"] = (res_lookup.get("WOOD", 0) + 
                                  res_lookup.get("WET_BIOMASS", 0) + 
                                  res_lookup.get("BIOWASTE", 0) +
                                  res_lookup.get("BIOMASS_RESIDUES", 0) +
                                  res_lookup.get("ENERGY_CROPS_2", 0)) / 1000
        
        # For PE_OIL, only count fossil oil (not _RE variants which are synthetic)
        metrics["PE_OIL"] = (res_lookup.get("GASOLINE", 0) + 
                             res_lookup.get("DIESEL", 0) + 
                             res_lookup.get("LFO", 0) +
                             res_lookup.get("JET_FUEL", 0)) / 1000
        
        metrics["PE_GAS"] = res_lookup.get("GAS", 0) / 1000
        metrics["PE_COAL"] = res_lookup.get("COAL", 0) / 1000
        metrics["PE_NUCLEAR"] = res_lookup.get("URANIUM", 0) / 1000
        metrics["PE_HYDRO"] = res_lookup.get("RES_HYDRO", 0) / 1000
        metrics["PE_WIND"] = res_lookup.get("RES_WIND", 0) / 1000
    
    # Year_balance.csv for electricity generation
    year_balance_path = outputs_dir / "Year_balance.csv"
    if year_balance_path.exists():
        df = pd.read_csv(year_balance_path)
        df = df.set_index("Elements")
        
        # Nuclear electricity
        if "NUCLEAR" in df.index and "ELECTRICITY" in df.columns:
            metrics["ELEC_NUCLEAR"] = max(0, df.loc["NUCLEAR", "ELECTRICITY"]) / 1000
        
        # Hydro electricity (dam + river)
        hydro_elec = 0
        for tech in ["HYDRO_DAM", "HYDRO_RIVER"]:
            if tech in df.index:
                hydro_elec += max(0, df.loc[tech, "ELECTRICITY"])
        metrics["ELEC_HYDRO"] = hydro_elec / 1000
        
        # Wind electricity (onshore + offshore)
        wind_elec = 0
        for tech in ["WIND_ONSHORE", "WIND_OFFSHORE"]:
            if tech in df.index:
                wind_elec += max(0, df.loc[tech, "ELECTRICITY"])
        metrics["ELEC_WIND"] = wind_elec / 1000
    
    # Gwp_breakdown.csv for CO2 emissions
    gwp_path = outputs_dir / "Gwp_breakdown.csv"
    if gwp_path.exists():
        df = pd.read_csv(gwp_path)
        # CO2_net is in ktCO2, convert to MtCO2
        if "CO2_net" in df.columns:
            metrics["CO2"] = df["CO2_net"].sum() / 1000  # ktCO2 → MtCO2
        elif "GWP_op" in df.columns:
            # Fallback: use operational GWP (also in ktCO2)
            metrics["CO2"] = df["GWP_op"].sum() / 1000
    
    return metrics


def compute_score(metrics: dict) -> tuple:
    """Compute weighted absolute percentage error score."""
    if metrics.get("FAILED"):
        return float("inf"), {}
    
    errors = {}
    weighted_sum = 0
    weight_sum = 0
    
    for key, (target, weight) in REALITY_TARGETS.items():
        if key in metrics and target > 0:
            model_val = metrics[key]
            pct_error = abs(model_val - target) / target * 100
            errors[key] = {
                "model": model_val,
                "target": target,
                "pct_error": pct_error,
                "weight": weight
            }
            weighted_sum += pct_error * weight
            weight_sum += weight
    
    if weight_sum > 0:
        score = weighted_sum / weight_sum
    else:
        score = float("inf")
    
    return score, errors


def find_all_runs(case_studies_dir: Path) -> list:
    """Find all calib_2017_finland* run directories."""
    runs = []
    fi_dir = case_studies_dir / "FI"
    if fi_dir.exists():
        for d in fi_dir.iterdir():
            if d.is_dir() and d.name.startswith("calib_2017_finland"):
                outputs_dir = d / "outputs"
                if outputs_dir.exists():
                    runs.append((d.name, outputs_dir))
    return runs


def main():
    case_studies = REPO_ROOT / "case_studies"
    runs = find_all_runs(case_studies)
    
    if not runs:
        print("No runs found in case_studies/FI/calib_2017_finland*/outputs/")
        sys.exit(1)
    
    print(f"Found {len(runs)} calibration runs\n")
    print("=" * 80)
    
    results = []
    
    for run_name, outputs_dir in sorted(runs):
        metrics = extract_metrics_from_run(outputs_dir)
        score, errors = compute_score(metrics)
        
        results.append({
            "run": run_name,
            "score": score,
            "metrics": metrics,
            "errors": errors
        })
    
    # Sort by score (lower is better)
    results.sort(key=lambda x: x["score"])
    
    # Print rankings
    print(f"{'Rank':<5} {'Run Name':<35} {'Score':>10} {'Status':<15}")
    print("-" * 70)
    
    for i, r in enumerate(results, 1):
        if r["score"] == float("inf"):
            status = "FAILED"
        elif r["score"] < 50:
            status = "GOOD"
        elif r["score"] < 100:
            status = "ACCEPTABLE"
        else:
            status = "POOR"
        
        score_str = f"{r['score']:.1f}" if r["score"] != float("inf") else "N/A"
        print(f"{i:<5} {r['run']:<35} {score_str:>10} {status:<15}")
    
    # Show detailed breakdown for top 3
    print("\n" + "=" * 80)
    print("DETAILED BREAKDOWN (Top 3 runs)")
    print("=" * 80)
    
    for r in results[:3]:
        if r["score"] == float("inf"):
            continue
        
        print(f"\n### {r['run']} (Score: {r['score']:.1f})")
        print(f"{'Metric':<15} {'Model':>12} {'Target':>12} {'Error %':>12} {'Weight':>8}")
        print("-" * 60)
        
        for key, info in sorted(r["errors"].items()):
            print(f"{key:<15} {info['model']:>12.2f} {info['target']:>12.2f} "
                  f"{info['pct_error']:>11.1f}% {info['weight']:>8.1f}")
    
    # Save to CSV
    output_csv = REPO_ROOT / "calibration" / "run_rankings.csv"
    rows = []
    for r in results:
        row = {"run": r["run"], "score": r["score"]}
        for key in REALITY_TARGETS.keys():
            if key in r.get("metrics", {}):
                row[f"{key}_model"] = r["metrics"][key]
            if key in r.get("errors", {}):
                row[f"{key}_error"] = r["errors"][key]["pct_error"]
        rows.append(row)
    
    pd.DataFrame(rows).to_csv(output_csv, index=False)
    print(f"\n\nRankings saved to: {output_csv}")
    
    # Print best run recommendation
    best = results[0]
    if best["score"] != float("inf"):
        print(f"\n{'='*80}")
        print(f"RECOMMENDED BASELINE: {best['run']}")
        print(f"Weighted Average Error: {best['score']:.1f}%")
        print(f"{'='*80}")


if __name__ == "__main__":
    main()
