
import pandas as pd
import numpy as np
import os

# Paths
path_ref = "Data/2017/02_REF_REGION"
path_fi = "Data/2017/FI"

# Load Resources
print("Loading Resources...")
try:
    resources_ref = pd.read_csv(f"{path_ref}/Resources.csv", index_col=2, comment='#')
    # Skip first 2 rows of units/comments if necessary, but pandas might handle it if header is line 0.
    # Actually, lines 0, 1, 2 are header info in some files?
    # Let's re-read line 1-5 to be sure.
    # The file read before showed:
    # ,,,Local availability,Exterior availability...
    # ,,units,[GWh/y],[GWh/y]...
    # Category,Subcategory,parameter name,avail_local,avail_exterior...
    # So header is on line 2 (0-indexed).
    resources_ref = pd.read_csv(f"{path_ref}/Resources.csv", header=2, index_col=2)
except Exception as e:
    print(f"Error loading REF Resources: {e}")
    resources_ref = pd.DataFrame()

try:
    # FI Resources seems to have header on line 0?
    # It started with ,avail_local,c_op_local
    resources_fi = pd.read_csv(f"{path_fi}/Resources.csv", index_col=0)
except Exception as e:
    print(f"Error loading FI Resources: {e}")
    resources_fi = pd.DataFrame()

resources_to_check = ['JET_FUEL', 'LFO', 'URANIUM', 'COAL', 'GAS', 'GASOLINE', 'DIESEL']

print("\n--- Resource Availability ---")
for res in resources_to_check:
    avail_ext = np.nan
    avail_loc = np.nan
    
    # Get from REF
    if res in resources_ref.index:
        try:
            avail_ext = float(resources_ref.loc[res, 'avail_exterior'])
        except:
            pass
        try:
            avail_loc = float(resources_ref.loc[res, 'avail_local'])
        except:
            pass

    # Override with FI
    if res in resources_fi.index:
        if 'avail_local' in resources_fi.columns:
            try:
                avail_loc = float(resources_fi.loc[res, 'avail_local'])
            except:
                pass
        if 'avail_exterior' in resources_fi.columns:
            try:
                avail_ext = float(resources_fi.loc[res, 'avail_exterior'])
            except:
                pass
    
    print(f"{res}: Exterior={avail_ext}, Local={avail_loc}")

# Load Technologies
print("\nLoading Technologies...")
try:
    tech_ref = pd.read_csv(f"{path_ref}/Technologies.csv", header=0, index_col=3, comment='#') # technologies name on col 2, param on 3?
    # Wait, header line 0: Category,Subcategory,Technologies name,Technologies param...
    # technologies param is index.
except Exception as e:
    print(f"Error loading REF Technologies: {e}")
    tech_ref = pd.DataFrame()

try:
    tech_fi = pd.read_csv(f"{path_fi}/Technologies.csv", on_bad_lines='skip') 
    # Attempt to align columns if structure differs, but let's assume standard first?
    # Often FI/Technologies.csv might just be overrides. 
    # Let's check if it exists.
    if os.path.exists(f"{path_fi}/Technologies.csv"):
        tech_fi = pd.read_csv(f"{path_fi}/Technologies.csv", index_col=0)
    else:
        tech_fi = pd.DataFrame()
except Exception as e:
    print(f"Error loading FI Technologies: {e}")
    tech_fi = pd.DataFrame()

print("\n--- Technology Constraints (f_min, fmin_perc) ---")
# technologies patterns to check: PLANE_*, BOILER_LFO_*, NUCLEAR_*
techs_to_check_patterns = ['PLANE', 'BOILER', 'NUCLEAR']

# Get list of all techs
all_techs = set(tech_ref.index)
if not tech_fi.empty:
    all_techs.update(tech_fi.index)

relevant_techs = []
for t in all_techs:
    if not isinstance(t, str): continue
    for pat in techs_to_check_patterns:
        if pat in t:
            relevant_techs.append(t)

for tech in relevant_techs:
    f_min = np.nan
    fmin_perc = np.nan
    
    # REF
    if tech in tech_ref.index:
        try:
            f_min = float(tech_ref.loc[tech, 'f_min'])
        except:
            pass
        try:
            fmin_perc = float(tech_ref.loc[tech, 'fmin_perc'])
        except:
            pass
            
    # FI Override
    if tech in tech_fi.index:
        if 'f_min' in tech_fi.columns:
            try:
                val = float(tech_fi.loc[tech, 'f_min'])
                if not np.isnan(val): f_min = val
            except:
                pass
        if 'fmin_perc' in tech_fi.columns:
            try:
                val = float(tech_fi.loc[tech, 'fmin_perc'])
                if not np.isnan(val): fmin_perc = val
            except:
                pass
    
    if (f_min > 0) or (fmin_perc > 0):
        print(f"{tech}: f_min={f_min}, fmin_perc={fmin_perc}")

print("\n--- All PLANE Technologies ---")
plane_techs = [t for t in all_techs if 'PLANE' in str(t)]
for tech in plane_techs:
    f_min = 0.0
    fmin_perc = 0.0
    # REF
    if tech in tech_ref.index:
        try: f_min = float(tech_ref.loc[tech, 'f_min']) 
        except: pass
        try: fmin_perc = float(tech_ref.loc[tech, 'fmin_perc'])
        except: pass
    # FI Override
    if tech in tech_fi.index:
        if 'f_min' in tech_fi.columns:
            try: val = float(tech_fi.loc[tech, 'f_min']); f_min = val if not np.isnan(val) else f_min
            except: pass
        if 'fmin_perc' in tech_fi.columns:
            try: 
                val = float(tech_fi.loc[tech, 'fmin_perc'])
                fmin_perc = val if not np.isnan(val) else fmin_perc
            except: 
                pass
    print(f"{tech}: f_min={f_min}, fmin_perc={fmin_perc}")


