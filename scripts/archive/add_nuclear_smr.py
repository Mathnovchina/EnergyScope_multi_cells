import pandas as pd
import os

path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\2017\00_INDEP\Layers_in_out.csv"

with open(path, 'r') as f:
    lines = f.readlines()

nuclear_line = None
for line in lines:
    if line.startswith("NUCLEAR,"):
        nuclear_line = line
        break

if nuclear_line:
    print("Found NUCLEAR line, duplicating for NUCLEAR_SMR")
    smr_line = nuclear_line.replace("NUCLEAR,", "NUCLEAR_SMR,")
    with open(path, 'a') as f:
        f.write(smr_line)
    print("Appended NUCLEAR_SMR row.")
else:
    print("NUCLEAR line not found! Cannot duplicate.")
