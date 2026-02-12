import pandas as pd
import json
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR_2017 = BASE_DIR / "Data" / "2017"
DATA_DIR_2035 = BASE_DIR / "Data" / "2035"
FI_DIR = DATA_DIR_2017 / "FI"
REF_REGION_DIR = DATA_DIR_2017 / "02_REF_REGION"

def check_input_assumptions():
    """
    Checks if the input assumptions (shares, bounds) for 2017 match the expected calibration values.
    """
    logging.info("--- CHECKING INPUT ASSUMPTIONS (2017) ---")
    
    # Load Misc.json
    misc_path = FI_DIR / "Misc.json"
    if not misc_path.exists():
        logging.error(f"Misc.json not found at {misc_path}")
        return
    
    with open(misc_path, 'r') as f:
        misc = json.load(f)

    # 1. District Heating Share
    dhn_min = misc.get('share_heat_dhn_min', 0)
    dhn_max = misc.get('share_heat_dhn_max', 0)
    expected_dhn = 0.45 
    if abs(dhn_min - expected_dhn) < 0.01 and abs(dhn_max - expected_dhn) < 0.01:
        logging.info(f"OK: DHN Share aligned with target ~{expected_dhn} ({dhn_min}-{dhn_max})")
    else:
        logging.warning(f"CHECK: DHN Share ({dhn_min}-{dhn_max}) differs from target {expected_dhn}")

    # 2. Freight Rail Share
    rail_min = misc.get('share_freight_train_min', 0)
    expected_rail = 0.276
    if abs(rail_min - expected_rail) < 0.01:
        logging.info(f"OK: Freight Rail aligned with target ~{expected_rail} ({rail_min})")
    else:
        logging.warning(f"CHECK: Freight Rail ({rail_min}) differs from target {expected_rail}")
        
    # 3. Public Mobility
    pub_min = misc.get('share_mobility_public_min', 0)
    expected_pub = 0.161
    if abs(pub_min - expected_pub) < 0.01:
         logging.info(f"OK: Public Mobility aligned with target ~{expected_pub} ({pub_min})")
    else:
        logging.warning(f"CHECK: Public Mobility ({pub_min}) differs from target {expected_pub}")

def check_cost_inputs():
    """
    Checks if costs have been updated from 2035 values.
    """
    logging.info("\n--- CHECKING COST ASSUMPTIONS ---")
    
    tech_path_17 = REF_REGION_DIR / "Technologies.csv"
    tech_path_35 = DATA_DIR_2035 / "02_REF_REGION" / "Technologies.csv"
    
    if not tech_path_17.exists() or not tech_path_35.exists():
        logging.error("Technologies.csv missing in 2017 or 2035 folder.")
        return

    try:
        # Load skipping first row (units)
        t17 = pd.read_csv(tech_path_17, header=0, encoding='utf-8')
        # Handle potential BOM or encoding issues if simple read fails, but try simple first.
        # Check if first row is unit
        if "Meuro" in str(t17.iloc[0,4]):
             t17 = t17.iloc[1:]
        t17 = t17.set_index('Technologies param')

        t35 = pd.read_csv(tech_path_35, header=0, encoding='utf-8')
        if "Meuro" in str(t35.iloc[0,4]):
             t35 = t35.iloc[1:]
        t35 = t35.set_index('Technologies param')
        
        cols = ['c_inv', 'c_maint']
        
        # Intersect indices to compare only common techs
        common_techs = t17.index.intersection(t35.index)
        
        identical = 0
        total = len(common_techs)
        
        for tech in common_techs:
            # We must be careful with types. Force numeric.
            c17 = pd.to_numeric(t17.loc[tech, cols], errors='coerce').fillna(0)
            c35 = pd.to_numeric(t35.loc[tech, cols], errors='coerce').fillna(0)
            
            # Simple equality check
            if c17.equals(c35):
                identical += 1
                
        if identical == total:
            logging.error(f"CRITICAL: All {total} technologies have IDENTICAL costs to 2035. Update required using 2017 data (e.g. DEA catalogs).")
        elif identical > total * 0.8:
            logging.warning(f"WARNING: {identical}/{total} technologies have identical costs. Verify if this is intentional.")
        else:
            logging.info("OK: Technology costs show significant differences from 2035.")
            
    except Exception as e:
        logging.error(f"Error checking costs: {e}")

def validate_model_outputs():
    """
    Placeholder: To be filled when model run outputs are available.
    Will compare Main_results with Finland 2017 Statistics.
    """
    logging.info("\n--- VALIDATING MODEL OUTPUTS (Placeholder) ---")
    
    # Check if files exist
    output_dir = BASE_DIR / "case_studies" / "FI" / "output"
    results_file = output_dir / "year_summary.csv" # Hypothetical name
    
    if not results_file.exists():
        logging.info("Model output not found. Please run the model first.")
        return

    logging.info("Comparing model results with validation targets...")
    # Add comparison logic here once we know the output format and target values.

if __name__ == "__main__":
    print(f"Running Validation for Finland 2017 Case")
    check_input_assumptions()
    check_cost_inputs()
    validate_model_outputs()
