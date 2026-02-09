import pandas as pd
import os

path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\2017\00_INDEP\Layers_in_out.csv"

# Rows to remove
remove_list = [
    "HVC"
]

with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    parts = line.strip().split(',')
    if parts[0] in remove_list:
        print(f"Removing row: {parts[0]}")
        continue
    new_lines.append(line)

with open(path, 'w', newline='') as f:
    f.writelines(new_lines)

print("Cleaned Layers_in_out.csv")
