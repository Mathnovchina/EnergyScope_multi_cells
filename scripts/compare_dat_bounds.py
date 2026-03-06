#!/usr/bin/env python3
"""Compare technology and resource bounds between frozen baseline and current .dat files."""

import pandas as pd
import sys

def parse_tech_dat(path):
    """Parse reg_technologies.dat into a DataFrame."""
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('param') or line.startswith(';') or line.startswith(':'):
                continue
            parts = line.split()
            if len(parts) >= 11:
                rows.append(parts[:11])
    cols = ['region', 'tech', 'c_inv', 'c_maint', 'gwp_constr',
            'lifetime', 'c_p', 'fmin_perc', 'fmax_perc', 'f_min', 'f_max']
    df = pd.DataFrame(rows, columns=cols)
    for c in cols[2:]:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.set_index('tech')
    return df


def parse_resources_dat(path):
    """Parse reg_resources.dat into a DataFrame."""
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('param') or line.startswith(';') or line.startswith(':'):
                continue
            parts = line.split()
            if len(parts) >= 7:
                rows.append(parts[:7])
    cols = ['region', 'resource', 'avail_local', 'avail_exterior',
            'c_op_local', 'c_op_exterior', 'gwp_op']
    df = pd.DataFrame(rows, columns=cols)
    for c in cols[2:]:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.set_index('resource')
    return df


def main():
    frozen_dir = "case_studies/FI/calib_2017_finland"
    current_dir = "case_studies/FI/manual_runs/20260305_110121__baseline_no_patch"

    # ---- Technologies ----
    print("=" * 80)
    print("TECHNOLOGY BOUND COMPARISON (frozen calib vs current)")
    print("=" * 80)
    frozen_t = parse_tech_dat(f"{frozen_dir}/reg_technologies.dat")
    current_t = parse_tech_dat(f"{current_dir}/reg_technologies.dat")

    compare_cols = ['f_min', 'f_max', 'fmin_perc', 'fmax_perc', 'c_p']
    common = frozen_t.index.intersection(current_t.index)
    diffs = []
    for tech in common:
        for col in compare_cols:
            v1 = frozen_t.loc[tech, col]
            v2 = current_t.loc[tech, col]
            if abs(v1 - v2) > 0.001:
                diffs.append((tech, col, v1, v2))

    print(f"\n{len(diffs)} parameter differences across {len(set(d[0] for d in diffs))} technologies:\n")
    print(f"{'Tech':<30} {'Param':<12} {'Frozen':>12} {'Current':>12} {'Change':>12}")
    print("-" * 80)
    for tech, col, v1, v2 in sorted(diffs):
        change = "TIGHTER" if (col == 'f_max' and v2 < v1) or (col == 'fmax_perc' and v2 < v1) else ""
        if (col == 'f_min' and v2 > v1) or (col == 'fmin_perc' and v2 > v1):
            change = "TIGHTER"
        print(f"{tech:<30} {col:<12} {v1:>12.4f} {v2:>12.4f} {change:>12}")

    # Highlight dangerous: f_min > 0 AND f_max reduced
    print("\n\nPOTENTIAL INFEASIBILITY (f_min > 0 AND f_max tightened from frozen):")
    print("-" * 80)
    for tech in common:
        fmin_cur = current_t.loc[tech, 'f_min']
        fmax_cur = current_t.loc[tech, 'f_max']
        fmax_fro = frozen_t.loc[tech, 'f_max']
        fminp_cur = current_t.loc[tech, 'fmin_perc']
        fmaxp_cur = current_t.loc[tech, 'fmax_perc']
        cp_cur = current_t.loc[tech, 'c_p']
        if fmin_cur > 0 and fmax_cur < fmax_fro:
            min_output = fmin_cur * cp_cur * 8.76  # TWh/y
            max_output = fmax_cur * cp_cur * 8.76
            print(f"  {tech:<28} f_min={fmin_cur:.2f} f_max={fmax_cur:.2f} (was {fmax_fro:.2f})  "
                  f"output_range=[{min_output:.1f}, {max_output:.1f}] TWh")

    # Check fmin_perc + fmax_perc conflicts
    print("\n\nf_min_perc + fmax_perc CHECK (current only):")
    print("-" * 80)
    for tech in current_t.index:
        fminp = current_t.loc[tech, 'fmin_perc']
        fmaxp = current_t.loc[tech, 'fmax_perc']
        if fminp > fmaxp and fmaxp > 0:
            print(f"  CONFLICT: {tech:<28} fmin_perc={fminp:.4f} > fmax_perc={fmaxp:.4f}")
        if fminp > 0 and fmaxp > 0 and fmaxp < 1.0:
            print(f"  BOUNDED:  {tech:<28} fmin_perc={fminp:.4f}  fmax_perc={fmaxp:.4f}")

    # ---- Resources ----
    print("\n\n" + "=" * 80)
    print("RESOURCE AVAILABILITY COMPARISON (frozen calib vs current)")
    print("=" * 80)
    frozen_r = parse_resources_dat(f"{frozen_dir}/reg_resources.dat")
    current_r = parse_resources_dat(f"{current_dir}/reg_resources.dat")

    common_r = frozen_r.index.intersection(current_r.index)
    print(f"\n{'Resource':<25} {'avail_local_F':>14} {'avail_local_C':>14} "
          f"{'avail_ext_F':>14} {'avail_ext_C':>14}")
    print("-" * 85)
    for res in common_r:
        al_f = frozen_r.loc[res, 'avail_local']
        al_c = current_r.loc[res, 'avail_local']
        ae_f = frozen_r.loc[res, 'avail_exterior']
        ae_c = current_r.loc[res, 'avail_exterior']
        if abs(al_f - al_c) > 0.01 or abs(ae_f - ae_c) > 0.01:
            flag = " << REDUCED" if (al_c < al_f or ae_c < ae_f) else ""
            print(f"{res:<25} {al_f:>14.1f} {al_c:>14.1f} "
                  f"{ae_f:>14.1f} {ae_c:>14.1f}{flag}")


if __name__ == "__main__":
    main()
