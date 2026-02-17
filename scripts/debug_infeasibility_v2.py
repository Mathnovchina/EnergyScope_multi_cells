import pandas as pd
import os

# Paths
CASE_STUDY_PATH = r"case_studies/FI/calib_2017_finland_v9"
LOG_PATH = os.path.join(CASE_STUDY_PATH, "log.txt")
TECHNOLOGIES_PATH = os.path.join(CASE_STUDY_PATH, "reg_technologies.dat")
RESOURCES_PATH = os.path.join(CASE_STUDY_PATH, "reg_resources.dat")
INDEP_PATH = os.path.join(CASE_STUDY_PATH, "indep.dat")

def check_log_constraints():
    print(f"Checking {LOG_PATH}...")
    if not os.path.exists(LOG_PATH):
        print("Log file not found.")
        return

    with open(LOG_PATH, 'r') as f:
        content = f.read()
        
    if "feasible or optimal but numeric issue" in content:
        print("ALERT: Solver reported 'feasible or optimal but numeric issue'.")
    
    if "presolve results" in content:
        print("Presolve results found.")
    
    # Check for specific constraint violations (if printed)
    # Usually AMPL/CPLEX prints violated constraints if any
    
    print("Log check done.")

def check_non_energy_producers():
    print(f"Checking NON_ENERGY producers in {INDEP_PATH}...")
    
    # Read indep.dat to find layers_in_out for HVC producers
    # This is rough parsing
    hvc_producers = ["OIL_TO_HVC", "GAS_TO_HVC", "BIOMASS_TO_HVC", "METHANOL_TO_HVC"]
    
    print("Checking availability of HVC producers:")
    # We need to map inputs. 
    # OIL_TO_HVC uses LFO (-1.818 in layers_in_out)
    # GAS_TO_HVC uses GAS (-2.79 in layers_in_out)
    
    # Check resources availability in reg_resources.dat
    print(f"Checking {RESOURCES_PATH}...")
    with open(RESOURCES_PATH, 'r') as f:
        lines = f.readlines()
    
    resources = {}
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "FI": # Assuming FI region
            res_name = parts[1]
            avail_exterior = parts[3]
            resources[res_name] = avail_exterior
            
    check_res = ["LFO", "GAS", "WOOD", "METHANOL"]
    for r in check_res:
        val = resources.get(r, "Not found")
        print(f"Resource {r} avail_exterior: {val}")

def check_technologies_bounds():
    print(f"Checking {TECHNOLOGIES_PATH}...")
    with open(TECHNOLOGIES_PATH, 'r') as f:
        lines = f.readlines()
        
    techs = ["OIL_TO_HVC", "GAS_TO_HVC", "BIOMASS_TO_HVC", "METHANOL_TO_HVC"]
    
    for line in lines:
        for t in techs:
            if t in line and "FI" in line:
                print(f"Tech {t}: {line.strip()}")

if __name__ == "__main__":
    check_log_constraints()
    check_non_energy_producers()
    check_technologies_bounds()
