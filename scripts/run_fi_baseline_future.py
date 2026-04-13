#!/usr/bin/env python3
"""
==========================================================================
  Finland Baseline Runner — 2035 / 2050  (ESMC Framework)
==========================================================================

Single-country Finland runner for future-year scenarios.
Derived from run_calib_manual.py but without calibration scoring (no
"reality" reference for future years).

Pipeline:
  1. Initialize ESMC with config (year=2035 or 2050)
  2. Read data from Data/<year>/  (3-tier merge: 00_INDEP → 02_REF_REGION → FI)
  3. Apply patches in-memory (Data/ CSV files are NEVER touched)
  4. Temporal aggregation (kmedoid or read frozen TDs)
  5. Numerics preflight check (flag absurd bounds)
  6. Generate .dat files + snapshot them
  7. Solve (barrier + deterministic fallback to dual simplex)
  8. Extract results, write metadata & README

Usage examples:
  # Dry-run preprocessing only — no solve
  python scripts/run_fi_baseline_future.py --year 2035 --name baseline_2035 --dry-run --kmedoid

  # Full run with kmedoid TD generation
  python scripts/run_fi_baseline_future.py --year 2035 --name baseline_2035 --kmedoid

  # Reuse frozen TDs from a previous kmedoid run
  python scripts/run_fi_baseline_future.py --year 2050 --name baseline_2050 --read-td

  # Finnish national plan baseline — 2035 (progressive, 50% reduction)
  #   gwp_limit = 21000 ktCO2/y  (co2_net-based, ~50% of 2017 level 41200)
  #   DHN share: 0.42–0.50 (Finnish reality ~46%)
  #   Brownfield: f_min for wind/PV/offshore from current installations
  #   Electricity trade: 25 TWh import cap
  python scripts/run_fi_baseline_future.py --year 2035 --name national_plan_2035 \\
      --gwp-limit 21000 --dhn-min 0.42 --dhn-max 0.50 \\
      -p calibration/patches/fi_baseline_2035.csv --kmedoid

  # Finnish national plan baseline — 2050 (near-zero)
  python scripts/run_fi_baseline_future.py --year 2050 --name national_plan_2050 \\
      --gwp-limit 3000 --dhn-min 0.42 --dhn-max 0.50 \\
      -p calibration/patches/fi_baseline_2050.csv --kmedoid

  # With RE share constraint
  python scripts/run_fi_baseline_future.py --year 2050 --name net_zero_2050 \\
      --gwp-limit 0 --re-share 0.8

Patch CSV format (same as calibration runner):
  file,parameter,technology_or_resource,value
  Technologies.csv,f_min,NUCLEAR,4.36
  Resources.csv,avail_exterior,GAS,20000

Output:
  case_studies/FI/manual_runs/<YYYYMMDD_HHMMSS>__<run_name>/
    outputs/           — standard ESMC outputs (Year_balance, etc.)
    input_snapshot/    — frozen copy of every .dat fed to AMPL
    patch_applied/     — copies of patches + diff summary
    run_metadata.json  — full reproducibility record
    run_notes.md       — template for annotations
    log.txt            — AMPL/CPLEX log
    log_fallback.txt   — fallback solver log (if triggered)
    README.md          — auto-generated run description

Data safety:
  Data/<year>/ is NEVER modified.  All patches are applied to in-memory
  DataFrames after init_regions().
"""

import argparse
import copy
import hashlib
import json
import shutil
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

VALID_YEARS = [2035, 2050]

# ---------------------------------------------------------------------------
# Numerics guard thresholds
# ---------------------------------------------------------------------------
FMAX_WARN_THRESHOLD = 1e10   # flag any f_max above this


# ===================================================================
# SOLVER OPTIONS  (single source of truth: esmc/utils/esmc.py CPLEX)
# ===================================================================

def _barrier_opts(log_path: Path) -> dict:
    """Primary strategy: CPLEX barrier with crossover=0 (ESMC default)."""
    cplex_options = [
        'baropt',
        'predual=-1',
        'barstart=4',
        'comptol=1e-5',
        'crossover=0',
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
    """Fallback: dual simplex — clear infeasibility certificate."""
    cplex_options = [
        'dual',
        'predual=-1',
        'timelimit 1800',
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
        description="Finland baseline runner — 2035 / 2050",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See script header for detailed usage examples.",
    )
    p.add_argument("--year", type=int, required=True, choices=VALID_YEARS,
                   help="Target year: 2035 or 2050")
    p.add_argument("--name", required=True,
                   help="Short name for this run (e.g. baseline_2035)")
    p.add_argument("--desc", default="",
                   help="Human-readable description of this run")
    p.add_argument("--dry-run", action="store_true",
                   help="Preprocessing + snapshot only — do NOT solve")
    p.add_argument("-p", "--patch", action="append", default=[],
                   help="CSV patch file(s) to apply in-memory (repeatable)")
    # TD mode — mutually exclusive
    td_group = p.add_mutually_exclusive_group(required=True)
    td_group.add_argument("--kmedoid", action="store_true",
                          help="Run k-medoid clustering to generate typical days")
    td_group.add_argument("--read-td", action="store_true",
                          help="Reuse frozen TDs from previous kmedoid run")
    # Constraints
    p.add_argument("--gwp-limit", type=float, default=None,
                   help="GWP limit in ktCO2/y (default: None = constraint dropped)")
    p.add_argument("--re-share", type=float, default=None,
                   help="Minimum RE share of primary energy 0–1 (default: None)")
    p.add_argument("--f-perc", action="store_true", default=False,
                   help="Enable fmin_perc/fmax_perc constraints (default: disabled)")
    p.add_argument("--nbr-td", type=int, default=12,
                   help="Number of typical days (default: 12)")
    p.add_argument("--ampl-path", default=None,
                   help="Path to AMPL executable (default: use PATH)")
    # DHN override (Finland has ~46%% DHN, but REF default is 2-37%%)
    p.add_argument("--dhn-min", type=float, default=None,
                   help="Override share_heat_dhn_min (0-1). Finland reality ~0.46")
    p.add_argument("--dhn-max", type=float, default=None,
                   help="Override share_heat_dhn_max (0-1). Finland reality ~0.46")
    return p.parse_args()


# ===================================================================
# PATCH APPLICATION (same mechanism as run_calib_manual.py)
# ===================================================================

_FILE_MAP = {
    "Technologies.csv": "Technologies",
    "Resources.csv":    "Resources",
    "Demands.csv":      "Demands",
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
            p = REPO_ROOT / "calibration" / "patches" / pf
        if p.exists():
            resolved.append(p)
        else:
            print(f"  ERROR: patch not found: {pf}")
            sys.exit(1)
    return resolved


def apply_patches(model, patch_files, run_dir):
    """Apply CSV patches to region DataFrames in-memory.

    Returns list of dicts documenting each change.
    """
    patch_log = []
    patch_dir = run_dir / "patch_applied"
    patch_dir.mkdir(parents=True, exist_ok=True)

    for pf in patch_files:
        shutil.copy2(pf, patch_dir / pf.name)
        df_patch = pd.read_csv(pf)
        for _, row in df_patch.iterrows():
            csv_file = row["file"]
            param = row["parameter"]
            tech_or_res = row["technology_or_resource"]
            value = row["value"]

            data_key = _FILE_MAP.get(csv_file)
            if data_key is None:
                print(f"  WARNING: unknown file '{csv_file}' in patch {pf.name}, skipping")
                continue

            for rname, region in model.regions.items():
                df = region.data[data_key]
                if tech_or_res in df.index and param in df.columns:
                    old_val = df.loc[tech_or_res, param]
                    try:
                        value_typed = type(old_val)(value)
                    except (ValueError, TypeError):
                        value_typed = float(value)
                    df.loc[tech_or_res, param] = value_typed
                    entry = {
                        "patch_file": pf.name,
                        "region": rname,
                        "data_key": data_key,
                        "index": tech_or_res,
                        "parameter": param,
                        "old_value": old_val,
                        "new_value": value_typed,
                    }
                    patch_log.append(entry)
                    print(f"  PATCH {rname}.{data_key}[{tech_or_res}].{param}: "
                          f"{old_val} -> {value_typed}")
                else:
                    print(f"  SKIP {rname}: {tech_or_res}.{param} not found in {data_key}")

    # Write diff summary
    if patch_log:
        diff_path = patch_dir / "diff_summary.txt"
        with open(diff_path, "w", encoding="utf-8") as f:
            for entry in patch_log:
                f.write(f"{entry['region']}.{entry['data_key']}[{entry['index']}]."
                        f"{entry['parameter']}: {entry['old_value']} -> {entry['new_value']}\n")
    return patch_log


# ===================================================================
# NUMERICS PREFLIGHT CHECK
# ===================================================================

def numerics_preflight(model):
    """Check for absurdly large bounds that could cause numeric issues.

    Returns list of warning strings.
    """
    warnings = []
    for rname, region in model.regions.items():
        tech_df = region.data["Technologies"]
        if "f_max" in tech_df.columns:
            large = tech_df[tech_df["f_max"] > FMAX_WARN_THRESHOLD]
            if len(large) > 0:
                for idx, row in large.iterrows():
                    warnings.append(
                        f"NUMERIC RISK: {rname} tech {idx} has f_max={row['f_max']:.2e}"
                    )
        res_df = region.data["Resources"]
        for col in ["avail_local", "avail_exterior"]:
            if col in res_df.columns:
                large_res = res_df[res_df[col] > FMAX_WARN_THRESHOLD]
                if len(large_res) > 0:
                    for idx, row in large_res.iterrows():
                        warnings.append(
                            f"NUMERIC RISK: {rname} resource {idx} has {col}={row[col]:.2e}"
                        )
    return warnings


# ===================================================================
# FILE HASHING
# ===================================================================

def hash_file(path: Path) -> str:
    """SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def hash_input_files(year: int) -> dict:
    """Hash key input files for provenance."""
    data_dir = REPO_ROOT / "Data" / str(year)
    hashes = {}
    key_files = [
        data_dir / "00_INDEP" / "Layers_in_out.csv",
        data_dir / "00_INDEP" / "Misc_indep.json",
        data_dir / "02_REF_REGION" / "Technologies.csv",
        data_dir / "02_REF_REGION" / "Resources.csv",
        data_dir / "FI" / "Technologies.csv",
        data_dir / "FI" / "Resources.csv",
        data_dir / "FI" / "Demands.csv",
        data_dir / "FI" / "Time_series.csv",
        data_dir / "FI" / "Misc.json",
    ]
    for fp in key_files:
        if fp.exists():
            rel = str(fp.relative_to(REPO_ROOT))
            hashes[rel] = hash_file(fp)
    return hashes


# ===================================================================
# METADATA & README
# ===================================================================

def get_git_info():
    """Get current git commit info."""
    try:
        import git
        repo = git.Repo(REPO_ROOT, search_parent_directories=True)
        return {
            "commit": str(repo.head.commit),
            "branch": str(repo.active_branch),
            "summary": repo.head.commit.summary,
            "dirty": repo.is_dirty(),
        }
    except Exception:
        return {"commit": "unknown", "branch": "unknown", "summary": "unknown", "dirty": None}


def save_metadata(run_dir, args, patch_log, numeric_warnings):
    """Write run_metadata.json with full reproducibility record."""
    meta = {
        "timestamp": datetime.now().isoformat(),
        "year": args.year,
        "run_name": args.name,
        "description": args.desc,
        "dry_run": args.dry_run,
        "td_mode": "kmedoid" if args.kmedoid else "read",
        "nbr_td": args.nbr_td,
        "gwp_limit_overall": args.gwp_limit,
        "re_share_primary": args.re_share,
        "f_perc": args.f_perc,
        "dhn_min": args.dhn_min,
        "dhn_max": args.dhn_max,
        "patches": [str(p) for p in resolve_patch_files(args.patch)] if args.patch else [],
        "patch_log": patch_log,
        "numeric_warnings": numeric_warnings,
        "input_file_hashes": hash_input_files(args.year),
        "git": get_git_info(),
        "solver_strategy": "barrier -> dual_simplex fallback",
        "script": "scripts/run_fi_baseline_future.py",
    }
    meta_path = run_dir / "run_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"  Metadata saved: {meta_path}")
    return meta


def write_run_readme(run_dir, args, numeric_warnings):
    """Write a README.md inside the run folder."""
    readme_path = run_dir / "README.md"
    gwp_str = f"{args.gwp_limit} ktCO2/y" if args.gwp_limit is not None else "None (dropped)"
    re_str = f"{args.re_share}" if args.re_share is not None else "None (dropped)"
    td_str = "kmedoid" if args.kmedoid else "read (frozen)"

    warn_section = ""
    if numeric_warnings:
        warn_section = "\n## Numeric Warnings\n\n"
        for w in numeric_warnings:
            warn_section += f"- {w}\n"

    content = f"""# Run: {args.name}

- **Year**: {args.year}
- **Description**: {args.desc or '(none)'}
- **Dry-run**: {args.dry_run}
- **Typical days**: {args.nbr_td} ({td_str})
- **GWP limit**: {gwp_str}
- **RE share**: {re_str}
- **f_perc**: {args.f_perc}
- **Patches**: {', '.join(args.patch) if args.patch else 'none'}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Data source

- `Data/{args.year}/00_INDEP/` — region-independent parameters
- `Data/{args.year}/02_REF_REGION/` — reference region (base for 167 techs)
- `Data/{args.year}/FI/` — Finland overrides (20 techs, 6 resources, demands, time series)

## Merge order

02_REF_REGION (base) → FI/ overrides via pandas `.update()` → patches in-memory
{warn_section}
## Outputs

After a successful solve, this folder will contain:
- `outputs/` — Year_balance, Gwp_breakdown, Resources, Assets, etc.
- `input_snapshot/` — frozen .dat files fed to AMPL
- `run_metadata.json` — full reproducibility record
- `log.txt` — AMPL/CPLEX solver log

## Plotting hooks (post-solve)

- Energy balance (Sankey / stacked bar)
- Capacity mix (installed GW by technology)
- Primary energy / final energy by sector
- CO2/GWP breakdown by source
- Shadow price of GWP constraint (if enabled)
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)


def write_run_notes(run_dir, args):
    """Write a run_notes.md template for user annotations."""
    notes_path = run_dir / "run_notes.md"
    content = f"""# Run Notes: {args.name} ({args.year})

## Observations


## Issues


## Next steps

"""
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(content)


# ===================================================================
# PLACEHOLDER OUTPUT STUBS (dry-run)
# ===================================================================

def write_placeholder_outputs(run_dir, args):
    """In dry-run mode, create stub files showing what would be produced."""
    outputs_dir = run_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    stub = (f"# PLACEHOLDER — dry-run for {args.name} ({args.year})\n"
            f"# This file would be populated after a real solve.\n")

    expected_files = [
        "Year_balance.csv",
        "Gwp_breakdown.csv",
        "Resources.csv",
        "Assets.csv",
        "Cost_breakdown.csv",
        "Solve_info.csv",
    ]
    for fname in expected_files:
        with open(outputs_dir / fname, "w") as f:
            f.write(stub)

    # Create plotting hooks directory
    plots_dir = run_dir / "validation_plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    plot_stubs = [
        "energy_balance_sankey.md",
        "capacity_mix.md",
        "primary_energy_by_sector.md",
        "co2_gwp_breakdown.md",
        "gwp_shadow_price.md",
    ]
    for fname in plot_stubs:
        with open(plots_dir / fname, "w") as f:
            f.write(f"# {fname.replace('.md','').replace('_',' ').title()}\n\n"
                    f"Placeholder — will be generated after solve.\n"
                    f"Year: {args.year}, Run: {args.name}\n")

    print(f"  Placeholder outputs written to {outputs_dir}")


# ===================================================================
# MAIN
# ===================================================================

def main():
    args = parse_args()

    print("=" * 70)
    print(f"  Finland Baseline Runner — {args.year}")
    print(f"  Run: {args.name}")
    print(f"  Dry-run: {args.dry_run}")
    print("=" * 70)

    # ---- Run directory ----
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{timestamp}__{args.name}"
    run_dir = REPO_ROOT / "case_studies" / "FI" / "manual_runs" / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n  Run directory: {run_dir}")

    # ---- Config ----
    config = {
        "case_study": f"manual_runs/{run_name}",
        "comment": args.desc or f"FI baseline {args.year} — {args.name}",
        "regions_names": ["FI"],
        "gwp_limit_overall": args.gwp_limit,
        "re_share_primary": {"FI": args.re_share} if args.re_share is not None else None,
        "f_perc": args.f_perc,
        "year": args.year,
    }

    # ---- Initialize ESMC ----
    print("\n[1/7] Initializing ESMC ...")
    model = Esmc(config, nbr_td=args.nbr_td)

    # ---- Read data ----
    print("[2/7] Reading data ...")
    model.read_data_indep()
    model.init_regions()

    # ---- Apply patches (if any) ----
    patch_log = []
    if args.patch:
        print("[3/7] Applying patches ...")
        patch_files = resolve_patch_files(args.patch)
        patch_log = apply_patches(model, patch_files, run_dir)
    else:
        print("[3/7] No patches to apply.")

    # ---- DHN share override ----
    if args.dhn_min is not None or args.dhn_max is not None:
        for rname, region in model.regions.items():
            if args.dhn_min is not None:
                old = region.data['Misc'].get('share_heat_dhn_min', 'N/A')
                region.data['Misc']['share_heat_dhn_min'] = args.dhn_min
                print(f"  DHN override: {rname} share_heat_dhn_min: {old} -> {args.dhn_min}")
            if args.dhn_max is not None:
                old = region.data['Misc'].get('share_heat_dhn_max', 'N/A')
                region.data['Misc']['share_heat_dhn_max'] = args.dhn_max
                print(f"  DHN override: {rname} share_heat_dhn_max: {old} -> {args.dhn_max}")

    # ---- Numerics preflight ----
    print("[4/7] Numerics preflight check ...")
    numeric_warnings = numerics_preflight(model)
    if numeric_warnings:
        print(f"  Found {len(numeric_warnings)} numeric warnings:")
        for w in numeric_warnings[:20]:
            print(f"    {w}")
        if len(numeric_warnings) > 20:
            print(f"    ... and {len(numeric_warnings) - 20} more")
    else:
        print("  No numeric warnings.")

    # ---- Write metadata, README, notes ----
    save_metadata(run_dir, args, patch_log, numeric_warnings)
    write_run_readme(run_dir, args, numeric_warnings)
    write_run_notes(run_dir, args)

    # ---- Dry-run exit point ----
    if args.dry_run:
        write_placeholder_outputs(run_dir, args)
        print("\n" + "=" * 70)
        print("  [DRY RUN] Stopping here. No .dat files generated, no solve.")
        print(f"  Run directory: {run_dir}")
        print("=" * 70)
        return

    # ---- Temporal aggregation ----
    td_algo = "kmedoid" if args.kmedoid else "read"
    print(f"[5/7] Temporal aggregation (algo={td_algo}, nbr_td={args.nbr_td}) ...")
    model.init_ta(algo=td_algo, ampl_path=args.ampl_path)

    # Check TD quality
    if hasattr(model.ta, 'tse') and model.ta.tse is not None:
        print(f"  Time series error: {model.ta.tse:.4f}")

    # ---- Override gwp_limit_overall in data (before .dat generation) ----
    if args.gwp_limit is not None:
        model.data_indep['Misc_indep']['gwp_limit_overall'] = args.gwp_limit
        print(f"  GWP limit override: gwp_limit_overall = {args.gwp_limit} ktCO2/y")

    # ---- Generate .dat files ----
    print("[6/7] Generating .dat files ...")
    model.print_td_data()
    model.print_data(indep=True)

    # Snapshot .dat files
    snapshot_dir = run_dir / "input_snapshot"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    dat_source = model.cs_dir
    for dat_file in dat_source.glob("*.dat"):
        shutil.copy2(dat_file, snapshot_dir / dat_file.name)
    # Also copy TD data
    for dat_file in model.dat_dir.glob("*.dat"):
        shutil.copy2(dat_file, snapshot_dir / dat_file.name)
    print(f"  Input snapshot saved: {snapshot_dir}")

    # ---- Solve ----
    print("[7/7] Solving ...")
    log_path = run_dir / "log.txt"

    # Primary: barrier
    model.set_esom(ampl_path=args.ampl_path, ampl_options=_barrier_opts(log_path))
    model.solve_esom()

    # Check solve status
    try:
        code = int(model.esom.t[2])
    except Exception:
        code = -999

    print(f"  Solve result code: {code}")

    # Fallback if needed
    if code != 0 and (code == -1 or 100 <= code < 200):
        print("  Primary solver failed — falling back to dual simplex ...")
        fallback_log = run_dir / "log_fallback.txt"
        model.set_esom(ampl_path=args.ampl_path,
                       ampl_options=_dual_simplex_opts(fallback_log))
        model.solve_esom()
        try:
            code = int(model.esom.t[2])
        except Exception:
            code = -999
        print(f"  Fallback solve result code: {code}")

    # ---- Extract results ----
    save_hourly = ['Resources', 'Exchanges', 'Assets', 'Storage', 'Curt']
    if code == 0:
        print("\n  Solve successful — extracting results ...")
        model.get_year_results(save_hourly=save_hourly)
        model.prints_esom(inputs=True, outputs=True, solve_info=True, save_hourly=save_hourly)
    else:
        print(f"\n  WARNING: Solve ended with code={code}. Results may be incomplete.")
        try:
            model.get_year_results(save_hourly=save_hourly)
            model.prints_esom(inputs=True, outputs=True, solve_info=True, save_hourly=save_hourly)
        except Exception as e:
            print(f"  Could not extract results: {e}")

    # ---- Update metadata with solve info ----
    meta_path = run_dir / "run_metadata.json"
    with open(meta_path) as f:
        meta = json.load(f)
    meta["solve_result_code"] = code
    meta["solve_completed"] = datetime.now().isoformat()
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print(f"  Run complete: {run_dir}")
    print(f"  Solve code: {code}")
    print("=" * 70)

    # Free AMPL resources
    try:
        model.esom.ampl.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()
