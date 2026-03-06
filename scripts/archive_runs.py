#!/usr/bin/env python3
"""
Archive broken/empty/unwanted calibration runs.

Moves selected run directories from case_studies/FI/ into
case_studies/FI/_archive_YYYYMMDD/ with a generated README.md
listing what was archived and why.

Usage:
  # Archive specific runs
  python scripts/archive_runs.py p26 p27 p28_clean_baseline p30_quick

  # Archive all runs without outputs/
  python scripts/archive_runs.py --empty

  # Archive all runs whose solve_result_num != 0
  python scripts/archive_runs.py --failed

  # Dry-run — show what would be moved
  python scripts/archive_runs.py --empty --dry-run
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CASE_STUDIES = REPO_ROOT / "case_studies" / "FI"


def parse_args():
    p = argparse.ArgumentParser(
        description="Archive calibration runs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("runs", nargs="*",
                   help="Run names or prefixes to archive")
    p.add_argument("--empty", action="store_true",
                   help="Archive all runs that have no outputs/ directory")
    p.add_argument("--failed", action="store_true",
                   help="Archive all runs whose Solve_info.csv shows failure")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would be moved without moving")
    return p.parse_args()


def find_run_dir(name: str) -> Path:
    """Find a run directory by name or calib_2017_finland_ prefix."""
    d = CASE_STUDIES / name
    if d.is_dir():
        return d
    d = CASE_STUDIES / f"calib_2017_finland_{name}"
    if d.is_dir():
        return d
    return None


def is_empty_run(d: Path) -> bool:
    """True if the run has no outputs/ directory or it's empty."""
    outputs = d / "outputs"
    if not outputs.exists():
        return True
    return len(list(outputs.iterdir())) == 0


def is_failed_run(d: Path) -> bool:
    """True if Solve_info.csv shows solve_result_num != 0."""
    si = d / "outputs" / "Solve_info.csv"
    if not si.exists():
        return True  # no solve info = likely failed
    try:
        with open(si) as f:
            for line in f:
                if "solve_result_num" in line:
                    val = line.strip().split(",")[-1].strip()
                    return float(val) != 0
    except Exception:
        return True
    return False


def main():
    args = parse_args()

    # Collect directories to archive
    to_archive = []

    # Manual list
    for name in args.runs:
        d = find_run_dir(name)
        if d is None:
            print(f"  NOT FOUND: {name}")
            continue
        to_archive.append(d)

    # --empty
    if args.empty:
        for d in sorted(CASE_STUDIES.iterdir()):
            if not d.is_dir():
                continue
            if d.name.startswith("_archive") or d.name.startswith("00_"):
                continue
            if d.name == "manual_runs":
                # Scan inside manual_runs/
                for sub in sorted(d.iterdir()):
                    if sub.is_dir() and is_empty_run(sub):
                        to_archive.append(sub)
                continue
            if is_empty_run(d):
                to_archive.append(d)

    # --failed
    if args.failed:
        for d in sorted(CASE_STUDIES.iterdir()):
            if not d.is_dir():
                continue
            if d.name.startswith("_archive") or d.name.startswith("00_"):
                continue
            if d.name == "manual_runs":
                for sub in sorted(d.iterdir()):
                    if sub.is_dir() and is_failed_run(sub):
                        to_archive.append(sub)
                continue
            if is_failed_run(d):
                to_archive.append(d)

    # Deduplicate
    seen = set()
    unique = []
    for d in to_archive:
        if str(d) not in seen:
            seen.add(str(d))
            unique.append(d)
    to_archive = unique

    if not to_archive:
        print("Nothing to archive.")
        return

    # Archive destination
    stamp = datetime.now().strftime("%Y%m%d")
    archive_dir = CASE_STUDIES / f"_archive_{stamp}"

    print(f"\nArchiving {len(to_archive)} run(s) to {archive_dir.name}/")
    for d in to_archive:
        reason = []
        if is_empty_run(d):
            reason.append("empty")
        if is_failed_run(d):
            reason.append("failed")
        print(f"  {d.name}  ({', '.join(reason) or 'user-selected'})")

    if args.dry_run:
        print("\n[DRY RUN] No files moved.")
        return

    archive_dir.mkdir(exist_ok=True)

    # Move
    moved = []
    for d in to_archive:
        dest = archive_dir / d.name
        try:
            d.rename(dest)
            moved.append(d.name)
            print(f"  MOVED: {d.name}")
        except Exception as e:
            print(f"  ERROR moving {d.name}: {e}")

    # Write README
    readme = archive_dir / "README.md"
    lines = [
        f"# Archive {stamp}",
        f"\nArchived {len(moved)} run(s) on "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}.",
        "",
        "| Run | Reason |",
        "|-----|--------|",
    ]
    for name in moved:
        lines.append(f"| {name} | archived by archive_runs.py |")
    readme.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  README: {readme}")
    print(f"  Done: {len(moved)}/{len(to_archive)} runs archived.")


if __name__ == "__main__":
    main()
