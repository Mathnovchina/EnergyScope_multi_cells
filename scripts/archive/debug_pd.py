import os

base_dir = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
paths = {
    "v10": os.path.join(base_dir, "case_studies", "FI", "calib_2017_finland_v10_oil_constr"),
    "v11": os.path.join(base_dir, "case_studies", "FI", "calib_2017_finland_v11_heat_fix")
}

print(f"{'Ver':<5} | {'f_max':<10} | {'Diesel':<10} | {'Gasoline':<10} | {'Liq Total':<10}")
print("-" * 65)

import csv

for label, p in paths.items():
    f_max_val = "N/A"
    tech_file = os.path.join(p, "reg_technologies.dat")
    if os.path.exists(tech_file):
        with open(tech_file, 'r') as f:
            for line in f:
                if line.startswith("FI") and "POWER_TO_DIESEL" in line:
                    parts = line.strip().split()
                    f_max_val = parts[-1]
                    break
    
    diesel = 0.0
    gasoline = 0.0
    yb = os.path.join(p, "outputs", "Year_balance.csv")
    if os.path.exists(yb):
        with open(yb, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            try:
                id = header.index("DIESEL")
                ig = header.index("GASOLINE")
                for row in reader:
                     if row[0] == "POWER_TO_DIESEL":
                        diesel = float(row[id])
                        gasoline = float(row[ig])
            except ValueError: pass
            
    print(f"{label:<5} | {f_max_val:<10} | {diesel:<10.1f} | {gasoline:<10.1f} | {diesel+gasoline:<10.1f}")
    
    assets = os.path.join(p, "outputs", "Assets.csv")
    if os.path.exists(assets):
        with open(assets, 'r') as f:
             for line in f:
                 if line.startswith("POWER_TO_DIESEL"):
                     print(f"  Assets ({label}): {line.strip()}")
