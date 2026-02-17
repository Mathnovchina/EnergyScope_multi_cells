
import sys
import copy
from pathlib import Path
import pandas as pd
import numpy as np

# Adjust sys.path to be able to import esmc modules
# Assuming script is run from scripts/ directory or root.
# Getting the root directory relative to this script
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from esmc.utils.region import Region

def debug_resources():
    # Configuration
    year = 2017
    region_name = 'FI'
    ref_region_name = '02_REF_REGION'
    
    # Path to Data
    data_dir = project_root / 'Data' / str(year)
    
    print(f"Data Dir: {data_dir}")
    
    # 1. Instantiate Ref Region
    print(f"Instantiating Ref Region: {ref_region_name}")
    ref_region = Region(nuts=ref_region_name, data_dir=data_dir, ref_region=True)
    
    # Check Ref Region Resources for debugging
    if 'Resources' in ref_region.data:
        print(f"Ref Region Resources loaded. Shape: {ref_region.data['Resources'].shape}")
    else:
        print("Ref Region Resources NOT loaded.")
    
    # 2. Instantiate FI Region as ESMC does
    print(f"Instantiating Region: {region_name}")
    region = copy.deepcopy(ref_region)
    # Re-initialize with FI parameters
    region.__init__(nuts=region_name, data_dir=data_dir, ref_region=False)
    
    # 3. Check Resources
    if 'Resources' in region.data:
        resources_df = region.data['Resources']
        print(f"Region {region_name} Resources loaded. Shape: {resources_df.shape}")
        
        # 4. Print specific rows
        target_resources = ['GASOLINE', 'DIESEL', 'COAL']
        print(f"\nChecking specific resources: {target_resources}")
        
        # Check availability
        try:
            # Check if index exists
            present_resources = [r for r in target_resources if r in resources_df.index]
            missing_resources = [r for r in target_resources if r not in resources_df.index]
            
            if missing_resources:
                print(f"WARNING: The following resources are missing from index: {missing_resources}")
            
            if present_resources:
                # Select only the column 'avail_exterior' if it exists, otherwise print whole row
                if 'avail_exterior' in resources_df.columns:
                    print(resources_df.loc[present_resources, ['avail_exterior']])
                else:
                    print(f"Column 'avail_exterior' not found. Columns are: {resources_df.columns}")
                    print(resources_df.loc[present_resources])
        except Exception as e:
            print(f"Error accessing resources: {e}")

        # 5. Print all index names
        print(f"\nAll Resources index names:")
        print(resources_df.index.tolist())
        
    else:
        print(f"Resources not found in region.data for {region_name}")

if __name__ == "__main__":
    debug_resources()
