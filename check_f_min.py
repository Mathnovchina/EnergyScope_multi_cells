import pandas as pd
import numpy as np

file_path = 'case_studies/FI/calib_2017_finland_v11_heat_fix/reg_technologies.dat'

# The file likely has a header line or lines to skip. The data starts after `param : ... :=`
# We'll read it manually to find the data lines.

with open(file_path, 'r') as f:
    lines = f.readlines()

data_lines = []
start_reading = False
for line in lines:
    if ':=' in line:
        start_reading = True
        continue
    if ';' in line:
        break
    if start_reading:
        if line.strip():
            data_lines.append(line.strip().split())

# Columns based on inspection:
# region, tech, c_inv, c_maint, gwp_constr, lifetime, c_p, fmin_perc, fmax_perc, f_min, f_max
# But let's just look at the last few columns.
# f_min seems to be the second to last.
# f_max seems to be the last.

large_f_min = []

for parts in data_lines:
    if len(parts) < 10:
        continue
    
    tech = parts[1]
    # f_min is usually index 8 if 0-indexed and region is included?
    # Let's count from end.
    # f_max is -1
    # f_min is -2
    
    f_min_str = parts[-2]
    f_max_str = parts[-1]

    try:
        f_min_val = float(f_min_str)
        if f_min_val == float('inf') or f_min_val > 1000:
            large_f_min.append((tech, f_min_val))
    except ValueError:
        pass # maybe it's a string or something else

print("Technologies with large f_min (> 1000) or Infinity:")
for tech, val in large_f_min:
    print(f"{tech}: {val}")

if not large_f_min:
    print("No large f_min found.")
