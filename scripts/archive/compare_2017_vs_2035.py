#!/usr/bin/env python3
"""
Compare Finland 2017 vs 2035 data files.

This script identifies differences between the 2017 calibration data
and the original 2035 projections to help identify potential errors
or intentional modifications.

Usage:
    python compare_2017_vs_2035.py
"""

import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_2017_FI = REPO_ROOT / "Data" / "2017" / "FI"
DATA_2035_FI = REPO_ROOT / "Data" / "2035" / "FI"


def compare_technologies():
    """Compare Technologies.csv between 2017 and 2035."""
    print("=" * 70)
    print("TECHNOLOGIES COMPARISON: 2017 FI vs 2035 FI")
    print("=" * 70)
    
    tech_2017 = pd.read_csv(DATA_2017_FI / "Technologies.csv")
    tech_2035 = pd.read_csv(DATA_2035_FI / "Technologies.csv")
    
    # Column comparison
    cols_2017 = set(tech_2017.columns)
    cols_2035 = set(tech_2035.columns)
    
    print(f"\n2017 columns: {sorted(cols_2017)}")
    print(f"2035 columns: {sorted(cols_2035)}")
    print(f"Extra in 2017: {sorted(cols_2017 - cols_2035)}")
    print(f"Missing in 2017: {sorted(cols_2035 - cols_2017)}")
    
    # Row count
    print(f"\n2017 technologies: {len(tech_2017)}")
    print(f"2035 technologies: {len(tech_2035)}")
    
    # Technology comparison
    techs_2017 = set(tech_2017["Technologies param"].dropna().astype(str))
    techs_2035 = set(tech_2035["Technologies param"].dropna().astype(str))
    
    common = techs_2017 & techs_2035
    only_2017 = techs_2017 - techs_2035
    only_2035 = techs_2035 - techs_2017
    
    print(f"\nCommon technologies: {len(common)}")
    if only_2017:
        print(f"Only in 2017 ({len(only_2017)}): {sorted(only_2017)[:20]}...")
    if only_2035:
        print(f"Only in 2035 ({len(only_2035)}): {sorted(only_2035)}")
    
    # Value differences for common technologies
    print("\n--- Key value differences for common technologies ---")
    for tech in sorted(common):
        row_2017 = tech_2017[tech_2017["Technologies param"] == tech].iloc[0]
        row_2035 = tech_2035[tech_2035["Technologies param"] == tech].iloc[0]
        
        diffs = []
        for col in ["f_min", "f_max"]:
            if col in row_2017.index and col in row_2035.index:
                v17 = row_2017.get(col, 0)
                v35 = row_2035.get(col, 0)
                if v17 != v35 and not (pd.isna(v17) and pd.isna(v35)):
                    diffs.append(f"{col}: {v17} vs {v35}")
        
        if diffs:
            print(f"  {tech}: {', '.join(diffs)}")


def compare_resources():
    """Compare Resources.csv between 2017 and 2035."""
    print("\n" + "=" * 70)
    print("RESOURCES COMPARISON: 2017 FI vs 2035 FI")
    print("=" * 70)
    
    res_2017 = pd.read_csv(DATA_2017_FI / "Resources.csv", index_col=0)
    res_2035 = pd.read_csv(DATA_2035_FI / "Resources.csv", index_col=0)
    
    print(f"\n2017 resources: {len(res_2017)}")
    print(f"2035 resources: {len(res_2035)}")
    
    common = set(res_2017.index) & set(res_2035.index)
    only_2017 = set(res_2017.index) - set(res_2035.index)
    only_2035 = set(res_2035.index) - set(res_2017.index)
    
    print(f"\nCommon resources: {len(common)}")
    if only_2017:
        print(f"Only in 2017 ({len(only_2017)}): {sorted(only_2017)}")
    if only_2035:
        print(f"Only in 2035 ({len(only_2035)}): {sorted(only_2035)}")
    
    # Value differences
    print("\n--- avail_local differences ---")
    for res in sorted(common):
        if "avail_local" in res_2017.columns and "avail_local" in res_2035.columns:
            v17 = res_2017.loc[res, "avail_local"]
            v35 = res_2035.loc[res, "avail_local"]
            if abs(v17 - v35) > 0.01:
                pct = abs(v17 - v35) / max(abs(v17), abs(v35)) * 100 if max(abs(v17), abs(v35)) > 0 else 0
                print(f"  {res}: 2017={v17:.2f}, 2035={v35:.2f} ({pct:.1f}% diff)")


def compare_demands():
    """Compare Demands.csv between 2017 and 2035."""
    print("\n" + "=" * 70)
    print("DEMANDS COMPARISON: 2017 FI vs 2035 FI")
    print("=" * 70)
    
    dem_2017 = pd.read_csv(DATA_2017_FI / "Demands.csv")
    dem_2035 = pd.read_csv(DATA_2035_FI / "Demands.csv")
    
    # Compare key demands
    print("\n--- Demand parameter differences ---")
    for _, row_2017 in dem_2017.iterrows():
        param = row_2017.get("parameter name", "")
        if pd.isna(param):
            continue
        
        row_2035 = dem_2035[dem_2035["parameter name"] == param]
        if len(row_2035) == 0:
            continue
        
        row_2035 = row_2035.iloc[0]
        
        for sector in ["HOUSEHOLDS", "SERVICES", "INDUSTRY", "TRANSPORTATION"]:
            v17 = row_2017.get(sector, 0)
            v35 = row_2035.get(sector, 0)
            
            if pd.notna(v17) and pd.notna(v35) and v17 != v35 and v17 > 0 and v35 > 0:
                pct = (v17 - v35) / v35 * 100
                if abs(pct) > 1:  # Only show >1% differences
                    print(f"  {param}/{sector}: 2017={v17:.1f}, 2035={v35:.1f} ({pct:+.1f}%)")


def check_data_consistency():
    """Check for potential data issues in 2017 files."""
    print("\n" + "=" * 70)
    print("DATA CONSISTENCY CHECKS")
    print("=" * 70)
    
    # Check Technologies.csv
    tech = pd.read_csv(DATA_2017_FI / "Technologies.csv")
    
    issues = []
    
    # Check for f_max < f_min
    for _, row in tech.iterrows():
        tech_name = row.get("Technologies param", "")
        f_min = row.get("f_min", 0)
        f_max = row.get("f_max", 0)
        
        if pd.notna(f_min) and pd.notna(f_max) and f_max < f_min:
            issues.append(f"  {tech_name}: f_max ({f_max}) < f_min ({f_min})")
    
    if issues:
        print("\n⚠️ Technologies with f_max < f_min:")
        for issue in issues:
            print(issue)
    else:
        print("\n✓ No f_max < f_min issues found")
    
    # Check for unreasonably large values
    large_values = []
    for _, row in tech.iterrows():
        tech_name = row.get("Technologies param", "")
        f_max = row.get("f_max", 0)
        
        if pd.notna(f_max) and f_max > 1e10 and f_max < 1e14:  # Between 10B and 100T (suspicious)
            large_values.append(f"  {tech_name}: f_max = {f_max:.2e}")
    
    if large_values:
        print(f"\n⚠️ Technologies with very large f_max (possible errors):")
        for lv in large_values[:10]:
            print(lv)


if __name__ == "__main__":
    compare_technologies()
    compare_resources()
    compare_demands()
    check_data_consistency()
    
    print("\n" + "=" * 70)
    print("Comparison complete. Review above for potential issues.")
    print("=" * 70)
