import os

path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\2017\00_INDEP\Layers_in_out.csv"

row_name = "CO2_EMISSIONS"
# 38 zeros
zeros = ",".join(["0"] * 38)
new_line = f"\n{row_name},{zeros}"

with open(path, 'a') as f:
    f.write(new_line)

print(f"Appended {row_name} row.")
