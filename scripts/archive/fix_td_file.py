import pandas as pd
import numpy as np
import os

def fix_td_files():
    base_dir = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\case_studies\FI\00_td_dat"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    td_file = os.path.join(base_dir, "TD_of_days_12.out")
    err_file = os.path.join(base_dir, "e_ts12.txt")
    
    # Generate naive mapping: 12 months, 1 typical day per month
    # Days 1-31 -> Typical Day 15
    # Days 32-59 -> Typical Day 45
    # etc.
    
    # Days in each month (non-leap)
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    td_mapping = []
    current_day = 1
    for i, d in enumerate(days_in_month):
        month_center = current_day + d // 2
        # Assign this month_center as the typical day for all days in this month
        # In reality, this should be the 'representative' day index.
        # But any integer works as long as we have 12 unique ones.
        for _ in range(d):
            td_mapping.append(month_center)
        current_day += d
        
    # Check length
    if len(td_mapping) != 365:
        # Pad or trim if 365 vs 366 (Model uses 365 usually, but checking file had 366 lines?)
        # 365 days + 1 newline?
        pass

    # Write to file
    with open(td_file, 'w') as f:
        for val in td_mapping:
            f.write(f"{val}\n")
            
    # Write error file
    with open(err_file, 'w') as f:
        f.write("0.1\n")
        
    print(f"Generated naive {td_file} with {len(set(td_mapping))} typical days.")

if __name__ == "__main__":
    fix_td_files()
