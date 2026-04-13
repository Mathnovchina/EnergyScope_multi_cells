#!/usr/bin/env python3
"""
==========================================================================
  run_ghg_sweep_2035.py  —  GHG-savings parametric sweep for Finland 2035
==========================================================================

Runs a series of Finland 2035 scenarios with different GWP limits,
from unconstrained down to 90-95 % reduction vs the 2017 baseline.

Inspired by Colla et al. (2022) — "Optimal Use of Lignocellulosic Biomass
for the Energy Transition", which analyses Belgium 2035 in 10 % GHG steps.

The script:
  1. Loops over a configurable set of GHG-savings fractions
  2. Calls run_fi_baseline_future.py for each case (subprocess)
  3. Logs success / failure per case
  4. Writes a sweep manifest (JSON) for downstream analysis

GHG baseline: Finland 2017 = 41,200 ktCO2/y (co2_net, calibrated).
Formula: gwp_limit = 41200 * (1 - savings_fraction)

Usage:
  # Full sweep (unconstrained + 10 % steps to 90 %)
  python scripts/run_ghg_sweep_2035.py

  # Subset test (unconstrained, 50 %, 90 % only)
  python scripts/run_ghg_sweep_2035.py --cases unconstrained 50 90

  # Dry-run (check commands without solving)
  python scripts/run_ghg_sweep_2035.py --dry-run

  # Custom step size
  python scripts/run_ghg_sweep_2035.py --step 20

  # Include 95 % case
  python scripts/run_ghg_sweep_2035.py --include-95

Prerequisites:
  - Existing kmedoid TDs from a previous run (--read-td will be used)
  - AMPL + CPLEX in PATH
  - calibration/patches/fi_baseline_2035.csv present
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GHG_BASELINE_2017 = 41_200  # ktCO2/y (Finland 2017 calibrated)

DEFAULT_PATCH = "calibration/patches/fi_baseline_2035.csv"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "run_fi_baseline_future.py"


def build_cases(step: int = 10, include_95: bool = False,
                explicit: list = None) -> list:
    """
    Build the list of (label, gwp_limit) tuples.

    Returns list of dict: {label, savings_pct, gwp_limit}
    gwp_limit=None means unconstrained.

    NOTE: The unconstrained 2035 optimum already achieves ~69% CO2_net savings
    (12,960 kt vs 41,200 baseline). Constraints below ~69% are SLACK.
    The interesting range is 70-95%.
    """
    if explicit is not None:
        cases = []
        for c in explicit:
            if c.lower() == "unconstrained":
                cases.append({
                    "label": "unconstrained",
                    "savings_pct": None,
                    "gwp_limit": None,
                })
            else:
                pct = int(c)
                cases.append({
                    "label": f"ghg_{pct}pct",
                    "savings_pct": pct,
                    "gwp_limit": round(GHG_BASELINE_2017 * (1 - pct / 100)),
                })
        return cases

    cases = [{
        "label": "unconstrained",
        "savings_pct": None,
        "gwp_limit": None,
    }]
    for pct in range(step, 91, step):
        cases.append({
            "label": f"ghg_{pct}pct",
            "savings_pct": pct,
            "gwp_limit": round(GHG_BASELINE_2017 * (1 - pct / 100)),
        })
    if include_95:
        cases.append({
            "label": "ghg_95pct",
            "savings_pct": 95,
            "gwp_limit": round(GHG_BASELINE_2017 * 0.05),
        })
    return cases


def run_one_case(case: dict, dry_run: bool = False,
                 extra_args: list = None,
                 patches: list = None, suffix: str = "") -> dict:
    """Run a single GHG case via subprocess.

    Returns dict with case info + result status.
    """
    label = case["label"]
    gwp = case["gwp_limit"]
    run_name = f"sweep_{label}{suffix}"

    cmd = [
        sys.executable,
        str(RUNNER_SCRIPT),
        "--year", "2035",
        "--name", run_name,
        "--desc", f"GHG sweep: {case.get('savings_pct', 'unconstrained')}% savings from 2017 baseline{suffix}",
        "--dhn-min", "0.42",
        "--dhn-max", "0.50",
        "--read-td",
    ]

    for p in (patches or [DEFAULT_PATCH]):
        cmd.extend(["-p", p])

    if gwp is not None:
        cmd.extend(["--gwp-limit", str(gwp)])

    if dry_run:
        cmd.append("--dry-run")

    if extra_args:
        cmd.extend(extra_args)

    print(f"\n{'='*70}")
    print(f"  CASE: {label}")
    print(f"  GWP limit: {gwp if gwp is not None else 'NONE (unconstrained)'} ktCO2/y")
    if case["savings_pct"] is not None:
        print(f"  GHG savings: {case['savings_pct']}% from 2017 ({GHG_BASELINE_2017} kt)")
    print(f"  Command: {' '.join(cmd)}")
    print(f"{'='*70}\n")

    t0 = datetime.now()
    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=False,  # let output flow to console
    )
    elapsed = (datetime.now() - t0).total_seconds()

    return {
        **case,
        "exit_code": result.returncode,
        "elapsed_s": round(elapsed, 1),
        "success": result.returncode == 0,
        "command": " ".join(cmd),
    }


def parse_args():
    p = argparse.ArgumentParser(
        description="GHG-savings sweep for Finland 2035",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--step", type=int, default=10,
                   help="GHG savings step size in %% (default: 10)")
    p.add_argument("--include-95", action="store_true",
                   help="Add a 95%% savings case")
    p.add_argument("--cases", nargs="+", default=None,
                   help="Explicit cases: e.g. 'unconstrained 50 70 90'")
    p.add_argument("--dry-run", action="store_true",
                   help="Dry-run only (preprocessing, no solve)")
    p.add_argument("--patch", "-p", action="append", default=None,
                   help="Patch CSV (repeatable). Default: fi_baseline_2035.csv")
    p.add_argument("--suffix", default="",
                   help="Suffix for run directory names (e.g. '_nuke_phaseout')")
    p.add_argument("--ampl-path", default=None,
                   help="Path to AMPL executable")
    return p.parse_args()


def main():
    args = parse_args()

    cases = build_cases(
        step=args.step,
        include_95=args.include_95,
        explicit=args.cases,
    )

    print("=" * 70)
    print("  Finland 2035 GHG-Savings Sweep")
    print(f"  Baseline: {GHG_BASELINE_2017} ktCO2/y (Finland 2017)")
    print(f"  Cases: {len(cases)}")
    print(f"  Dry-run: {args.dry_run}")
    print("=" * 70)

    for i, c in enumerate(cases):
        gwp_str = f"{c['gwp_limit']:,} kt" if c['gwp_limit'] is not None else "unconstrained"
        print(f"  [{i+1:2d}] {c['label']:20s}  gwp_limit = {gwp_str}")
    print()

    extra = []
    if args.ampl_path:
        extra.extend(["--ampl-path", args.ampl_path])

    patches = args.patch  # None → run_one_case defaults to [DEFAULT_PATCH]

    results = []
    for i, case in enumerate(cases):
        print(f"\n>>> Running case {i+1}/{len(cases)}: {case['label']} <<<\n")
        r = run_one_case(case, dry_run=args.dry_run, extra_args=extra,
                         patches=patches, suffix=args.suffix)
        results.append(r)

        status = "OK" if r["success"] else f"FAILED (exit={r['exit_code']})"
        print(f"\n  Case {case['label']}: {status}  ({r['elapsed_s']:.0f}s)")

    # ---- Summary ----
    print("\n" + "=" * 70)
    print("  SWEEP SUMMARY")
    print("=" * 70)
    ok = sum(1 for r in results if r["success"])
    fail = len(results) - ok
    print(f"  Total: {len(results)}, Success: {ok}, Failed: {fail}\n")
    for r in results:
        gwp_str = f"{r['gwp_limit']:>8,} kt" if r['gwp_limit'] is not None else "     unconstrained"
        status = "OK  " if r["success"] else "FAIL"
        print(f"  [{status}] {r['label']:20s}  gwp={gwp_str}  time={r['elapsed_s']:>6.0f}s")

    # ---- Save manifest ----
    manifest_dir = REPO_ROOT / "case_studies" / "FI" / "manual_runs"
    manifest_path = manifest_dir / "ghg_sweep_2035_manifest.json"
    manifest = {
        "created": datetime.now().isoformat(),
        "ghg_baseline_2017_ktCO2": GHG_BASELINE_2017,
        "year": 2035,
        "dry_run": args.dry_run,
        "cases": results,
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n  Manifest saved: {manifest_path}")
    print("=" * 70)

    # Exit with failure if any case failed
    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
