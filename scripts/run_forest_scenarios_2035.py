#!/usr/bin/env python3
"""
==========================================================================
  run_forest_scenarios_2035.py  —  Forest biomass scenario sweep, FI 2035
==========================================================================

Runs a 3×3 matrix: 3 forest scenarios × 3 GHG targets.

Forest scenarios
  S2-NFS  (Neutral Forest Scenario)  — default Resources.csv, no extra patch
  S1-BES  (Biodiversity Enhancement) — calibration/patches/fi_forest_S1_BES.csv
  S3-BDS  (Biodiversity Default)     — calibration/patches/fi_forest_S3_BDS.csv

GHG targets (vs Finland 2017 baseline = 41,200 ktCO2/y)
  unconstrained          — no gwp_limit
  80%  reduction         — gwp_limit = 8,240 ktCO2/y
  95%  reduction         — gwp_limit = 2,060 ktCO2/y

All outputs go to:  case_studies/FI/forest_scenarios_2035/<timestamp>__<name>/

Usage:
  # Full 3×3 matrix
  python scripts/run_forest_scenarios_2035.py

  # Dry-run (preprocessing only, no solve)
  python scripts/run_forest_scenarios_2035.py --dry-run

  # Single scenario × single GHG target
  python scripts/run_forest_scenarios_2035.py --scenarios S2_NFS --ghg unconstrained

  # Run specific scenarios and GHG levels
  python scripts/run_forest_scenarios_2035.py --scenarios S2_NFS S3_BDS --ghg unconstrained 80

  # First run must compute TDs (--kmedoid); subsequent may reuse (--read-td)
  python scripts/run_forest_scenarios_2035.py --kmedoid

Prerequisites:
  - AMPL + CPLEX in PATH
  - calibration/patches/fi_baseline_2035.csv present
  - calibration/patches/fi_forest_S1_BES.csv present
  - calibration/patches/fi_forest_S3_BDS.csv present
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GHG_BASELINE_2017 = 41_200  # ktCO2/y (Finland 2017 calibrated)
STUDY_GROUP = "forest_scenarios_2035"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "run_fi_baseline_future.py"

BASE_PATCH = "calibration/patches/fi_baseline_2035.csv"

FOREST_SCENARIOS = {
    "S2_NFS": {
        "label": "S2_NFS",
        "desc": "Neutral Forest Scenario (ENS_Med 2035, default availability)",
        "patch": None,  # no extra patch; default Resources.csv is already S2-NFS
    },
    "S1_BES": {
        "label": "S1_BES",
        "desc": "Biodiversity Enhancement Scenario (ENS_Med×1.2, +20% biomass)",
        "patch": "calibration/patches/fi_forest_S1_BES.csv",
    },
    "S3_BDS": {
        "label": "S3_BDS",
        "desc": "Biodiversity Default Scenario (ENS_Low 2030, strict constraints)",
        "patch": "calibration/patches/fi_forest_S3_BDS.csv",
    },
}

GHG_TARGETS = {
    "unconstrained": {
        "label": "unconstrained",
        "gwp_limit": None,
        "savings_pct": None,
        "extra_patches": [],
    },
    "80": {
        "label": "ghg_80pct",
        "gwp_limit": round(GHG_BASELINE_2017 * 0.20),  # 8,240 ktCO2/y
        "savings_pct": 80,
        "extra_patches": [],
    },
    "95": {
        "label": "ghg_95pct",
        "gwp_limit": round(GHG_BASELINE_2017 * 0.05),  # 2,060 ktCO2/y
        "savings_pct": 95,
        "extra_patches": [],
    },
    "95nuke": {
        "label": "ghg_95pct_nonuke",
        "gwp_limit": round(GHG_BASELINE_2017 * 0.05),  # 2,060 ktCO2/y (same as 95%)
        "savings_pct": 95,
        "extra_patches": ["calibration/patches/fi_nuclear_phaseout_strong_2035.csv"],
    },
}


def run_one_case(
    scenario: dict,
    ghg: dict,
    dry_run: bool = False,
    use_kmedoid: bool = False,
    dhn_min: float = 0.42,
    dhn_max: float = 0.50,
) -> dict:
    """Run one (forest_scenario × GHG_target) combination."""
    scen_label = scenario["label"]
    ghg_label = ghg["label"]
    run_name = f"{scen_label}__{ghg_label}"

    # Build patch list: always base patch, then forest-specific patch, then GHG-specific patches
    patches = [BASE_PATCH]
    if scenario["patch"]:
        patches.append(scenario["patch"])
    patches.extend(ghg.get("extra_patches", []))

    desc = f"{scenario['desc']} | GHG: {ghg_label}"

    cmd = [
        sys.executable,
        str(RUNNER_SCRIPT),
        "--year", "2035",
        "--name", run_name,
        "--study-group", STUDY_GROUP,
        "--desc", desc,
        "--dhn-min", str(dhn_min),
        "--dhn-max", str(dhn_max),
    ]

    for p in patches:
        cmd.extend(["-p", p])

    if ghg["gwp_limit"] is not None:
        cmd.extend(["--gwp-limit", str(ghg["gwp_limit"])])

    if use_kmedoid:
        cmd.append("--kmedoid")
    else:
        cmd.append("--read-td")

    if dry_run:
        cmd.append("--dry-run")

    gwp_str = (f"{ghg['gwp_limit']:,} ktCO2/y"
               if ghg["gwp_limit"] is not None else "unconstrained")

    print(f"\n{'='*70}")
    print(f"  CASE: {scen_label} × {ghg_label}")
    print(f"  GWP limit: {gwp_str}")
    if ghg["savings_pct"] is not None:
        print(f"  GHG savings: {ghg['savings_pct']}% from 2017 ({GHG_BASELINE_2017} kt)")
    print(f"  Patches: {patches}")
    print(f"  Command: {' '.join(cmd)}")
    print(f"{'='*70}\n")

    t0 = datetime.now()
    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=False,
    )
    elapsed = (datetime.now() - t0).total_seconds()

    return {
        "scenario": scen_label,
        "ghg_label": ghg_label,
        "gwp_limit": ghg["gwp_limit"],
        "savings_pct": ghg["savings_pct"],
        "patches": patches,
        "exit_code": result.returncode,
        "elapsed_s": round(elapsed, 1),
        "success": result.returncode == 0,
        "command": " ".join(cmd),
    }


def parse_args():
    p = argparse.ArgumentParser(
        description="Forest biomass scenario sweep for Finland 2035 (3×3 matrix)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--scenarios", nargs="+",
        choices=list(FOREST_SCENARIOS.keys()),
        default=list(FOREST_SCENARIOS.keys()),
        help="Forest scenarios to run (default: all three)",
    )
    p.add_argument(
        "--ghg", nargs="+",
        choices=list(GHG_TARGETS.keys()),
        default=list(GHG_TARGETS.keys()),
        help="GHG targets to run: unconstrained 80 95 (default: all three)",
    )
    p.add_argument("--dry-run", action="store_true",
                   help="Preprocessing only, no solve")
    p.add_argument("--kmedoid", action="store_true",
                   help="Re-cluster temporal days (use for first run). "
                        "Default is --read-td (reuse existing TDs).")
    p.add_argument("--dhn-min", type=float, default=0.42,
                   help="Override share_heat_dhn_min (default: 0.42)")
    p.add_argument("--dhn-max", type=float, default=0.50,
                   help="Override share_heat_dhn_max (default: 0.50)")
    return p.parse_args()


def main():
    args = parse_args()

    selected_scenarios = [FOREST_SCENARIOS[s] for s in args.scenarios]
    selected_ghg = [GHG_TARGETS[g] for g in args.ghg]

    n_total = len(selected_scenarios) * len(selected_ghg)

    print("=" * 70)
    print("  Finland 2035 — Forest Biomass Scenario Sweep")
    print(f"  Study group:  {STUDY_GROUP}")
    print(f"  GHG baseline: {GHG_BASELINE_2017:,} ktCO2/y (Finland 2017)")
    print(f"  Scenarios:    {[s['label'] for s in selected_scenarios]}")
    print(f"  GHG targets:  {[g['label'] for g in selected_ghg]}")
    print(f"  Total cases:  {n_total}")
    print(f"  Dry-run:      {args.dry_run}")
    print(f"  Use kmedoid:  {args.kmedoid}")
    print("=" * 70)
    print()

    results = []
    case_num = 0
    for scen in selected_scenarios:
        for ghg in selected_ghg:
            case_num += 1
            print(f"\n>>> Running case {case_num}/{n_total}: "
                  f"{scen['label']} × {ghg['label']} <<<\n")
            r = run_one_case(
                scen, ghg,
                dry_run=args.dry_run,
                use_kmedoid=args.kmedoid,
                dhn_min=args.dhn_min,
                dhn_max=args.dhn_max,
            )
            results.append(r)

            if not r["success"] and not args.dry_run:
                print(f"\n  [WARN] Case {scen['label']} × {ghg['label']} "
                      f"FAILED (exit {r['exit_code']}). Continuing...\n")

    # ---- Summary ----
    print("\n" + "=" * 70)
    print("  SWEEP SUMMARY")
    print("=" * 70)
    ok = sum(1 for r in results if r["success"])
    fail = n_total - ok
    print(f"  Completed: {ok}/{n_total}  |  Failed: {fail}")
    print()
    for r in results:
        status = "OK " if r["success"] else "FAIL"
        gwp_str = (f"{r['gwp_limit']:>8,} kt" if r["gwp_limit"] is not None
                   else " unconstrained")
        print(f"  [{status}] {r['scenario']:8s} × {r['ghg_label']:16s} "
              f"gwp={gwp_str}  t={r['elapsed_s']:.0f}s")

    # ---- Write manifest ----
    manifest_path = (REPO_ROOT / "case_studies" / "FI" / STUDY_GROUP
                     / f"sweep_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump({
            "study_group": STUDY_GROUP,
            "ghg_baseline_2017": GHG_BASELINE_2017,
            "run_at": datetime.now().isoformat(),
            "results": results,
        }, f, indent=2)
    print(f"\n  Manifest saved: {manifest_path.relative_to(REPO_ROOT)}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
