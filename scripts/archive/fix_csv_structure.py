import pandas as pd
import os

path = "c:\\Users\\borde\\OneDrive\\Bureau\\model\\EnergyScope_multi_cells\\Data\\2017\\00_INDEP\\Layers_in_out.csv"

# Read as raw test to avoid pandas error
with open(path, 'r') as f:
    lines = f.readlines()

header = lines[0].strip().split(',')
expected_cols = len(header)
print(f"Header has {expected_cols} columns.")

new_lines = []
new_lines.append(lines[0].strip())

for i, line in enumerate(lines[1:]):
    parts = line.strip().split(',')
    if len(parts) > expected_cols:
        print(f"Line {i+2} has {len(parts)} columns. Truncating.")
        parts = parts[:expected_cols]
    elif len(parts) < expected_cols:
        print(f"Line {i+2} has {len(parts)} columns. Padding.")
        parts = parts + ['0'] * (expected_cols - len(parts))
    
    new_lines.append(",".join(parts))

with open(path, 'w', newline='\n') as f:
    f.write("\n".join(new_lines))

print("Fixed CSV.")
