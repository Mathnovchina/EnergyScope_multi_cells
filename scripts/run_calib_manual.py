#!/usr/bin/env python3
"""
Manual Calibration Runner for EnergyScope Multi-Cells.

This script provides a structured workflow for manual calibration:
1. Clone baseline configuration
2. Apply user-defined patches (CSV overrides)
3. Run the model
4. Generate validation plots
5. Compare against reality targets
6. Archive run with metadata

Usage:
    python run_calib_manual.py --run-name my_experiment --patch patches/my_patch.csv
    python run_calib_manual.py --run-name test_nuclear_cap --from-baseline calib_2017_finland

Author: EnergyScope Team
Date: 2024
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Repository root
REPO_ROOT = Path(__file__).parent.parent
CASE_STUDIES = REPO_ROOT / "case_studies" / "FI"
DATA_2017 = REPO_ROOT / "Data" / "2017"
CALIBRATION_DIR = REPO_ROOT / "calibration"
REALITY_REF = CALIBRATION_DIR / "reality" / "finland_2017_reference.csv"


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Manual calibration runner for Finland 2017",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run with a patch file
    python run_calib_manual.py --run-name test_biomass --patch patches/increase_biomass.csv
    
    # Clone from existing baseline and run
    python run_calib_manual.py --run-name v12_test --from-baseline calib_2017_finland_v9
    
    # Dry run (prepare but don't execute)
    python run_calib_manual.py --run-name v12_test --dry-run
        """
    )
    
    parser.add_argument(
        "--run-name", "-n",
        required=True,
        help="Name for this calibration run (will be prefixed with calib_2017_finland_)"
    )
    
    parser.add_argument(
        "--from-baseline", "-b",
        default="calib_2017_finland",
        help="Baseline run to clone from (default: calib_2017_finland)"
    )
    
    parser.add_argument(
        "--patch", "-p",
        action="append",
        default=[],
        help="CSV patch file(s) to apply (can specify multiple)"
    )
    
    parser.add_argument(
        "--description", "-d",
        default="",
        help="Description of this calibration run"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare run but don't execute AMPL"
    )
    
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip validation plot generation after run"
    )
    
    parser.add_argument(
        "--solver",
        default="cplex",
        choices=["cplex", "gurobi", "highs"],
        help="Solver to use (default: cplex)"
    )
    
    parser.add_argument(
        "--reuse-dat",
        action="store_true",
        help="Use existing .dat files from baseline without regenerating (ignores patches)"
    )
    
    return parser.parse_args()


def load_reality_targets():
    """Load reality targets from reference CSV."""
    if REALITY_REF.exists():
        return pd.read_csv(REALITY_REF)
    return None


def apply_patch(run_dir: Path, patch_file: Path, dry_run: bool = False) -> dict:
    """
    Apply a CSV patch to the DATA files (at repo root Data/2017/).
    
    Patch format:
        file,parameter,technology_or_resource,value,[old_value]
        
    Example:
        Technologies.csv,f_max,NUCLEAR,2.8
        Resources.csv,avail_exterior,COAL,30000
    
    NOTE: Patches are applied to shared Data/2017/ files.
    Original files are backed up and restored after model run.
    Patched copies are saved in run_dir for audit.
    
    If dry_run=True, only shows what would be changed without modifying files.
    """
    patch_log = {"file": str(patch_file), "changes": [], "backups": []}
    
    df = pd.read_csv(patch_file)
    
    # Group changes by target file for efficiency
    files_to_patch = {}
    
    for _, row in df.iterrows():
        target_file = row["file"]
        param = row["parameter"]
        entity = str(row["technology_or_resource"]).strip()
        new_val = row["value"]
        
        # Look in shared Data folder at repo root (FI overrides first, then REF_REGION)
        target_path = DATA_2017 / "FI" / target_file
        if not target_path.exists():
            target_path = DATA_2017 / "02_REF_REGION" / target_file
        
        if not target_path.exists():
            print(f"  WARNING: {target_file} not found, skipping patch for {entity}")
            continue
        
        if str(target_path) not in files_to_patch:
            files_to_patch[str(target_path)] = {
                "path": target_path,
                "df": pd.read_csv(target_path),
                "changes": []
            }
        
        files_to_patch[str(target_path)]["changes"].append({
            "param": param,
            "entity": entity,
            "new_val": new_val
        })
    
    # Apply changes to each file
    for file_key, file_data in files_to_patch.items():
        target_path = file_data["path"]
        target_df = file_data["df"]
        
        # Create backup directory in run_dir
        backup_dir = run_dir / "data_backup"
        backup_dir.mkdir(exist_ok=True)
        
        # Save original file as backup
        backup_path = backup_dir / f"{target_path.parent.name}_{target_path.name}"
        if not dry_run:
            shutil.copy(target_path, backup_path)
            patch_log["backups"].append({
                "original": str(target_path),
                "backup": str(backup_path)
            })
        
        # Identify entity column
        entity_col = None
        for col in ["Name", "Technologies", "Technologies param", "Resources"]:
            if col in target_df.columns:
                entity_col = col
                break
        
        if not entity_col:
            print(f"  WARNING: Cannot identify entity column in {target_path.name}")
            print(f"  Available columns: {list(target_df.columns)}")
            continue
        
        # Apply each change
        for change in file_data["changes"]:
            param = change["param"]
            entity = change["entity"]
            new_val = change["new_val"]
            
            idx = target_df[target_df[entity_col].astype(str).str.strip() == entity].index
            
            if len(idx) == 0:
                print(f"  WARNING: Entity {entity} not found in {target_path.name}")
                continue
            
            old_val = target_df.loc[idx[0], param]
            
            if not dry_run:
                target_df.loc[idx[0], param] = new_val
            
            change_record = {
                "file": target_path.name,
                "file_path": str(target_path),
                "entity": entity,
                "parameter": param,
                "old_value": old_val,
                "new_value": new_val
            }
            patch_log["changes"].append(change_record)
            
            prefix = "[DRY RUN] " if dry_run else ""
            print(f"  {prefix}{entity}.{param}: {old_val} -> {new_val}")
        
        # Save modified file (only if not dry run)
        if not dry_run:
            target_df.to_csv(target_path, index=False)
            
            # Also save patched copy in run_dir for audit
            patched_dir = run_dir / "data_patched"
            patched_dir.mkdir(exist_ok=True)
            patched_path = patched_dir / f"{target_path.parent.name}_{target_path.name}"
            target_df.to_csv(patched_path, index=False)
    
    return patch_log


def restore_from_backups(run_dir: Path, patch_logs: list):
    """Restore original files from backups after model run."""
    print("\nRestoring baseline files from backups...")
    
    total_restored = 0
    for patch_log in patch_logs:
        backups = patch_log.get("backups", [])
        
        for backup in backups:
            original = Path(backup["original"])
            backup_path = Path(backup["backup"])
            
            if backup_path.exists():
                shutil.copy(backup_path, original)
                print(f"  Restored: {original.name}")
                total_restored += 1
    
    print(f"  Total: Restored {total_restored} files to original state")


def clone_baseline(baseline_name: str, new_run_name: str) -> Path:
    """Clone a baseline run directory."""
    baseline_dir = CASE_STUDIES / baseline_name
    new_dir = CASE_STUDIES / new_run_name
    
    if new_dir.exists():
        print(f"ERROR: Run directory already exists: {new_dir}")
        print("  Use a different --run-name or delete existing directory first")
        sys.exit(1)
    
    if not baseline_dir.exists():
        print(f"ERROR: Baseline not found: {baseline_dir}")
        print(f"  Available baselines:")
        for d in CASE_STUDIES.iterdir():
            if d.is_dir() and d.name.startswith("calib_2017"):
                print(f"    - {d.name}")
        sys.exit(1)
    
    print(f"Cloning {baseline_name} -> {new_run_name}...")
    shutil.copytree(baseline_dir, new_dir)
    
    return new_dir


def apply_patch_to_dat(run_dir: Path, patch_file: Path) -> dict:
    """Apply a patch directly to .dat files (for --reuse-dat mode)."""
    patch_log = {"file": str(patch_file), "changes": []}
    
    df = pd.read_csv(patch_file)
    
    # Column mapping for reg_technologies.dat
    # Format: Region Tech c_inv c_maint gwp_constr lifetime c_p fmin_perc fmax_perc f_min f_max
    tech_col_map = {
        'c_inv': 2, 'c_maint': 3, 'gwp_constr': 4, 'lifetime': 5,
        'c_p': 6, 'fmin_perc': 7, 'fmax_perc': 8, 'f_min': 9, 'f_max': 10
    }
    
    # Group patches by target file
    for _, row in df.iterrows():
        target_file = row["file"]
        param = row["parameter"]
        entity = str(row["technology_or_resource"]).strip()
        new_val = row["value"]
        
        if target_file == "Technologies.csv":
            # Map to reg_technologies.dat
            dat_file = run_dir / "reg_technologies.dat"
            if not dat_file.exists():
                print(f"  WARNING: {dat_file.name} not found, skipping")
                continue
            
            if param not in tech_col_map:
                print(f"  WARNING: Unknown parameter {param} for Technologies, skipping")
                continue
            
            col_idx = tech_col_map[param]
            
            # Read and modify dat file
            lines = dat_file.read_text().split('\n')
            modified = False
            
            for i, line in enumerate(lines):
                parts = line.split()
                if len(parts) > col_idx and parts[1] == entity:
                    old_val = parts[col_idx]
                    parts[col_idx] = str(new_val)
                    lines[i] = '\t'.join(parts)
                    modified = True
                    
                    patch_log["changes"].append({
                        "file": dat_file.name,
                        "entity": entity,
                        "parameter": param,
                        "old_value": old_val,
                        "new_value": new_val
                    })
                    print(f"  {entity}.{param}: {old_val} -> {new_val} (in {dat_file.name})")
                    break
            
            if modified:
                dat_file.write_text('\n'.join(lines))
            else:
                print(f"  WARNING: {entity} not found in {dat_file.name}")
        else:
            print(f"  WARNING: Direct .dat patching for {target_file} not implemented")
    
    return patch_log


def run_model_direct(run_dir: Path, solver: str = "cplex") -> int:
    """Run AMPL directly on existing .dat files without regenerating."""
    print("  Running in DIRECT mode (reusing existing .dat files)...")
    
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from esmc.utils.opti_probl import OptiProbl
        
        # Clear old outputs directory to ensure fresh results
        outputs_dir = run_dir / "outputs"
        if outputs_dir.exists():
            print("  Clearing old outputs directory...")
            shutil.rmtree(outputs_dir)
        outputs_dir.mkdir(exist_ok=True)
        
        # Find mod and dat files
        mod_files = list(run_dir.glob("*.mod"))
        dat_files = list(run_dir.glob("*.dat"))
        
        if not mod_files:
            print("  ERROR: No .mod files found in run directory")
            return 1
        if not dat_files:
            print("  ERROR: No .dat files found in run directory")
            return 1
        
        print(f"  Found {len(mod_files)} .mod files, {len(dat_files)} .dat files")
        
        # Default CPLEX options (matching v10)
        cplex_options = ['baropt', 'predual=-1', 'barstart=4', 'comptol=1e-5',
                         'crossover=0', 'timelimit 172800', 'bardisplay=1', 'display=2']
        
        ampl_options = {
            'show_stats': 3,
            'log_file': str(run_dir / 'log.txt'),
            'presolve': 200,
            'times': 1,
            'gentimes': 1,
            'cplex_options': ' '.join(cplex_options)
        }
        
        # Create OptiProbl directly
        print("  Creating optimization problem...")
        esom = OptiProbl(mod_path=mod_files, data_path=dat_files, 
                         options=ampl_options, solver=solver)
        
        # Solve
        print("  Solving...")
        esom.run_ampl()
        
        # Get solve info
        solve_time = esom.ampl.get_value("_solve_elapsed_time")
        solve_result = esom.ampl.get_value("solve_result_num")
        obj_value = esom.ampl.get_value("TotalCost")
        
        # Convert obj_value to float if needed
        try:
            obj_value = float(obj_value)
        except (ValueError, TypeError):
            obj_value = 0.0
        
        print(f"  Solve time: {solve_time:.1f}s")
        print(f"  Solve result: {solve_result}")
        print(f"  TotalCost: {obj_value:,.2f}")
        
        # Save outputs
        outputs_dir = run_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        # Save TotalCost
        pd.DataFrame({'TotalCost': [obj_value]}).to_csv(outputs_dir / 'TotalCost.csv', index=False)
        
        # Save Solve_info
        pd.DataFrame({
            'solve_time': [solve_time],
            'solve_result': [solve_result],
            'TotalCost': [obj_value]
        }).to_csv(outputs_dir / 'Solve_info.csv', index=False)
        
        # Get F variable (installed capacity per technology)
        try:
            F = esom.ampl.get_variable("F")
            if F:
                f_df = F.get_values().to_pandas()
                f_df.to_csv(outputs_dir / "F_capacity.csv")
                print(f"  Saved F_capacity.csv ({len(f_df)} rows)")
                
                # Show key technologies
                print("  Key capacities [GW]:")
                for tech in ['NUCLEAR', 'DEC_ADVCOGEN_GAS', 'IND_COGEN_WOOD', 'DHN_COGEN_WOOD']:
                    try:
                        val = f_df.loc[f_df.index.get_level_values(1) == tech, 'F.val'].sum()
                        print(f"    {tech}: {val:.2f}")
                    except:
                        pass
        except Exception as e:
            print(f"  Warning: Could not extract F: {e}")
        
        # Close AMPL
        esom.ampl.close()
        
        return 0 if solve_result == 0 else 1
        
    except Exception as e:
        import traceback
        print(f"  ERROR: {e}")
        traceback.print_exc()
        return 1


def run_model(run_dir: Path, solver: str = "cplex", reuse_dat: bool = False) -> int:
    """Run the EnergyScope AMPL model using the Esmc framework."""
    print(f"\nRunning model with {solver}...")
    
    if reuse_dat:
        return run_model_direct(run_dir, solver)
    
    try:
        # Import the Esmc framework
        sys.path.insert(0, str(REPO_ROOT))
        from esmc import Esmc
        from esmc.common import CSV_SEPARATOR
        
        # Read config from the case study if exists, or use defaults
        config_file = run_dir / "config.yaml"
        if config_file.exists():
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)
        else:
            # Default configuration for Finland 2017 calibration
            config = {
                'case_study': str(run_dir.name),
                'comment': 'calibration run',
                'regions_names': ['FI'],
                'gwp_limit_overall': None,  # No GWP limit for calibration
                're_share_primary': None,
                'f_perc': False,  # Disable fmin_perc/fmax_perc for stability
                'year': 2017
            }
        
        # Override case_study to use our run directory
        config['case_study'] = str(run_dir.name)
        
        # Determine number of typical days
        nbr_td = 12  # Default for Finland
        
        print(f"  Initializing Esmc model for {config['case_study']}...")
        my_model = Esmc(config, nbr_td=nbr_td)
        
        # Read independent data
        print("  Reading independent data...")
        my_model.read_data_indep()
        
        # Initialize regions
        print("  Initializing regions...")
        my_model.init_regions()
        
        # Initialize temporal aggregation (use 'read' if already computed, else 'kmedoid')
        print("  Initializing temporal aggregation...")
        td_data_dir = my_model.cs_dir / 'td_data'
        if td_data_dir.exists() and any(td_data_dir.iterdir()):
            my_model.init_ta(algo='read')
        else:
            my_model.init_ta(algo='kmedoid')
        
        # Print time-related data
        print("  Printing TD data...")
        my_model.print_td_data()
        
        # Print all data (generates .dat files from CSVs)
        print("  Printing data (CSV -> DAT)...")
        my_model.print_data(indep=True)
        
        # Set up ESOM with DEFAULT CPLEX options (matching original v10)
        print("  Setting up ESOM...")
        
        # Use framework defaults (crossover=0) which v10 used successfully
        my_model.set_esom()
        
        # Solve
        print("  Solving ESOM...")
        my_model.solve_esom()
        
        # Get results
        print("  Getting year results...")
        my_model.get_year_results()
        
        # Print outputs
        print("  Printing outputs...")
        my_model.prints_esom(inputs=True, outputs=True, solve_info=True)
        
        # Close AMPL
        if hasattr(my_model, 'esom') and hasattr(my_model.esom, 'ampl'):
            my_model.esom.ampl.close()
        
        print("  Model run complete!")
        return 0
        
    except Exception as e:
        import traceback
        print(f"ERROR: Model run failed: {e}")
        traceback.print_exc()
        
        # Save error to log
        log_dir = run_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        with open(log_dir / "error.log", "w") as f:
            f.write(f"Error: {e}\n")
            traceback.print_exc(file=f)
        
        return 1


def generate_validation_plots(run_dir: Path):
    """Generate validation plots for the run."""
    print("\nGenerating validation plots...")
    
    plot_script = REPO_ROOT / "scripts" / "plot_validate_2017.py"
    
    if plot_script.exists():
        subprocess.run([
            sys.executable, str(plot_script),
            "--run-dir", str(run_dir)
        ], cwd=str(REPO_ROOT))
    else:
        print("  plot_validate_2017.py not found, skipping plots")


def save_metadata(run_dir: Path, args, patch_logs: list, return_code: int):
    """Save run metadata for reproducibility."""
    metadata = {
        "run_name": args.run_name,
        "baseline": args.from_baseline,
        "description": args.description,
        "timestamp": datetime.now().isoformat(),
        "solver": args.solver,
        "return_code": return_code,
        "patches_applied": patch_logs,
        "command": " ".join(sys.argv),
        "git_info": get_git_info()
    }
    
    metadata_path = run_dir / "calibration_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nMetadata saved to: {metadata_path}")


def get_git_info() -> dict:
    """Get current git commit info."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        ).stdout.strip()
        
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        ).stdout.strip()
        
        return {"commit": commit, "branch": branch}
    except:
        return {"error": "Could not get git info"}


def score_run(run_dir: Path) -> dict:
    """Quick score of run against reality targets."""
    from score_calib_runs import extract_metrics_from_run, compute_score
    
    outputs_dir = run_dir / "outputs"
    if outputs_dir.exists():
        metrics = extract_metrics_from_run(outputs_dir)
        score, errors = compute_score(metrics)
        return {"score": score, "errors": errors}
    return None


def main():
    args = parse_args()
    
    # Normalize run name
    run_name = args.run_name
    if not run_name.startswith("calib_2017_finland_"):
        run_name = f"calib_2017_finland_{run_name}"
    
    print("=" * 70)
    print(f"MANUAL CALIBRATION RUN: {run_name}")
    print("=" * 70)
    
    if args.dry_run:
        print("[DRY RUN MODE - No files will be modified]")
    
    # 1. Clone baseline (creates run directory structure)
    run_dir = clone_baseline(args.from_baseline, run_name)
    
    # 2. Apply patches
    patch_logs = []
    for patch_file in args.patch:
        patch_path = Path(patch_file)
        if not patch_path.exists():
            patch_path = REPO_ROOT / patch_file
        
        if patch_path.exists():
            print(f"\nApplying patch: {patch_path.name}")
            if args.reuse_dat:
                # Directly edit .dat files when using --reuse-dat
                log = apply_patch_to_dat(run_dir, patch_path)
            else:
                # Standard CSV patch with backup/restore
                log = apply_patch(run_dir, patch_path, dry_run=args.dry_run)
            patch_logs.append(log)
        else:
            print(f"WARNING: Patch file not found: {patch_file}")
    
    # For dry-run, stop here (no model execution, no restore needed since nothing changed)
    if args.dry_run:
        print("\n[DRY RUN] Skipping model execution")
        print("\n" + "=" * 70)
        print(f"Dry run complete. Run directory prepared: {run_dir}")
        print("=" * 70)
        return
    
    # 3. Run model with try/finally to ensure restore happens
    return_code = -1
    try:
        return_code = run_model(run_dir, args.solver, reuse_dat=args.reuse_dat)
        
        if return_code != 0:
            print(f"\nWARNING: Model returned non-zero exit code: {return_code}")
    finally:
        # Restore baseline files after model run (only if not using --reuse-dat)
        if not args.reuse_dat:
            restore_from_backups(run_dir, patch_logs)
    
    # 4. Generate plots
    if not args.skip_plots:
        generate_validation_plots(run_dir)
    
    # 5. Save metadata
    save_metadata(run_dir, args, patch_logs, return_code)
    
    # 6. Quick score
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        result = score_run(run_dir)
        if result:
            print(f"\nWeighted Error Score: {result['score']:.1f}%")
    except Exception as e:
        print(f"\nCould not compute score: {e}")
    
    print("\n" + "=" * 70)
    print(f"Run complete: {run_dir}")
    print("Patched versions saved in: {run_dir}/data_patched/")
    print("=" * 70)


if __name__ == "__main__":
    main()
