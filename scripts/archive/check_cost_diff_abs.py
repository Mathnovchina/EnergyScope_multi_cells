import pandas as pd
import os
import numpy as np

base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"

try:
    tech_2017_path = os.path.join(base_path, "Data", "2017", "02_REF_REGION", "Technologies.csv")
    tech_2035_path = os.path.join(base_path, "Data", "2035", "02_REF_REGION", "Technologies.csv")
    
    # Read with flexible separator handling
    # index_col=3 is 'Technologies param' which is the unique ID usually (e.g. NUCLEAR, WIND_ONSHORE)
    tech_2017 = pd.read_csv(tech_2017_path, header=0)
    tech_2017 = tech_2017.iloc[1:] # Drop unit row
    tech_2017 = tech_2017.set_index('Technologies param')

    tech_2035 = pd.read_csv(tech_2035_path, header=0)
    tech_2035 = tech_2035.iloc[1:] # Drop unit row
    tech_2035 = tech_2035.set_index('Technologies param')

    cols_to_check = ['c_inv', 'c_maint']
    
    print("\n--- Comparison of Costs (2017 vs 2035) ---")
    diff_count = 0
    same_count = 0
    missing_count = 0
    
    for tech in tech_2017.index:
        if tech in tech_2035.index:
            cost17 = tech_2017.loc[tech, cols_to_check]
            cost35 = tech_2035.loc[tech, cols_to_check]
            
            # Allow for small float differences
            if np.allclose(cost17.values.astype(float), cost35.values.astype(float), rtol=1e-05):
                same_count += 1
                # print(f"SAME {tech}")
            else:
                diff_count += 1
                if diff_count <= 5: # Print first few diffs
                     print(f"DIFF {tech} (Inv/Maint):")
                     print(f"  2017: {cost17.values}")
                     print(f"  2035: {cost35.values}")
        else:
            missing_count += 1

    print(f"\nSummary: {same_count} technologies have IDENTICAL costs.")
    print(f"Summary: {diff_count} technologies have DIFFERENT costs.")
    print(f"Summary: {missing_count} technologies are not in 2035 dataset.")
    
    if same_count > 0 and diff_count == 0:
         print("CONCLUSION: 2017 costs are EXACT COPIES of 2035.")
    elif same_count > diff_count:
         print("CONCLUSION: Most costs are identical. Significant copying suspected.")
    else:
         print("CONCLUSION: Costs seem to be updated for 2017.")

except Exception as e:
    print(f"An error occurred: {e}")
