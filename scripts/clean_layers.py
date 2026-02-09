import pandas as pd
import os

path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\2017\00_INDEP\Layers_in_out.csv"

# Rows to remove
remove_list = [
    "HEAT_HIGH_T",
    "HEAT_LOW_T_DHN",
    "HEAT_LOW_T_DECEN",
    "SPACE_COOLING",
    "PROCESS_COOLING",
    "MOB_PUBLIC",
    "MOB_PRIVATE",
    "AVIATION_SHORT_HAUL",
    "AVIATION_LONG_HAUL",
    "MOB_FREIGHT_RAIL",
    "MOB_FREIGHT_ROAD",
    "MOB_FREIGHT_BOAT",
    "SHIPPING"
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
