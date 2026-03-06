#!/usr/bin/env python3
"""Show all technologies with f_min > 0 and their forced minimum output."""
import sys
sys.path.insert(0, '.')
exec(open('scripts/compare_dat_bounds.py').read().split('def main')[0])

current_t = parse_tech_dat('case_studies/FI/manual_runs/20260305_110121__baseline_no_patch/reg_technologies.dat')

print("All technologies with f_min > 0 (current):")
header = f"{'Tech':<30} {'f_min':>8} {'f_max':>8} {'c_p':>8} {'min_TWh':>10} {'max_TWh':>10}"
print(header)
print("-" * 80)
total_min = 0
for tech in sorted(current_t.index):
    fmin = current_t.loc[tech, 'f_min']
    fmax = current_t.loc[tech, 'f_max']
    cp = current_t.loc[tech, 'c_p']
    if fmin > 0:
        min_twh = fmin * cp * 8.76
        max_twh = fmax * cp * 8.76
        total_min += min_twh
        print(f"{tech:<30} {fmin:>8.2f} {fmax:>8.2f} {cp:>8.3f} {min_twh:>10.1f} {max_twh:>10.1f}")

print(f"\nTotal forced minimum output: {total_min:.1f} TWh")
