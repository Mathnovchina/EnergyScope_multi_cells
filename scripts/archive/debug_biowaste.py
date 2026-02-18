
import pandas as pd
import os

def debug_biowaste():
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resources_path = os.path.join(base_dir, 'Data', '2017', 'FI', 'Resources.csv')
    technologies_path = os.path.join(base_dir, 'Data', '2017', 'FI', 'Technologies.csv')
    layers_path = os.path.join(base_dir, 'Data', '2017', '00_INDEP', 'Layers_in_out.csv')
    ref_tech_path = os.path.join(base_dir, 'Data', '2017', '02_REF_REGION', 'Technologies.csv')

    print(f"Reading Resources from {resources_path}")
    resources = pd.read_csv(resources_path, index_col=0)
    
    print(f"Reading Technologies from {technologies_path}")
    technologies = pd.read_csv(technologies_path, index_col=0)
    
    print(f"Reading Layers_in_out from {layers_path}")
    layers = pd.read_csv(layers_path, index_col=0)

    print(f"Reading REF Technologies from {ref_tech_path}")
    try:
        # Assuming column 3 is the ID in REF region file
        # Check first row to see if it has headers
        df_check = pd.read_csv(ref_tech_path, nrows=1, header=None)
        if df_check.iloc[0,0] == 'Category': # Or similar
             ref_technologies = pd.read_csv(ref_tech_path, index_col=3)
        else:
             ref_technologies = pd.read_csv(ref_tech_path, header=None)
             if ref_technologies.shape[1] > 3:
                ref_technologies.set_index(3, inplace=True)
    except Exception as e:
        print(f"Error reading REF Technologies: {e}")
        ref_technologies = pd.DataFrame()

    total_avail = 0
    target_resources = ['BIOWASTE', 'BIOMASS_RESIDUES']
    print("\n--- Resource Availability (FI) ---")
    
    for res in target_resources:
        if res in resources.index:
            avail = resources.loc[res, 'avail_local']
            # formatting
            print(f"{res}: {avail} GWh")
            total_avail += avail
        else:
            print(f"{res}: Not found")
            
    print(f"Total BIOWASTE/RESIDUES Available: {total_avail} GWh (~{total_avail/1000:.2f} TWh)")

    # 2. Check consumers of BIOWASTE layer
    # Note: BIOMASS_RESIDUES feeds BIOWASTE layer.
    biowaste_layer = 'BIOWASTE'
    print(f"\n--- Consumers of {biowaste_layer} layer ---")
    
    potential_consumers = []
    if biowaste_layer in layers.columns:
        # Techs with negative value in BIOWASTE column
        consumers = layers[layers[biowaste_layer] < -1e-6].index.tolist()
        potential_consumers = consumers
        print(f"Defined in Layers_in_out.csv: {consumers}")
    else:
        print(f"Layer {biowaste_layer} not found in Layers_in_out.csv")

    # 3. Check presence in FI Technologies
    print("\n--- Checking Consumers in FI Technologies ---")
    present_consumers = []
    missing_consumers = []
    
    for tech in potential_consumers:
        if tech in technologies.index:
            present_consumers.append(tech)
            f_min = technologies.loc[tech, 'f_min']
            print(f"[FOUND] {tech} (f_min={f_min})")
            
            if f_min > 0:
                print(f"    WARNING: {tech} has f_min > 0")
        else:
            missing_consumers.append(tech)

    if not present_consumers:
        print("CRITICAL: No technology in current FI/Technologies.csv consumes BIOWASTE.")
    else:
        print(f"Found {len(present_consumers)} active consumers.")

    # 4. Check REF Region
    print("\n--- Checking Missing Consumers in REF Region ---")
    for tech in missing_consumers:
        if tech in ref_technologies.index:
             print(f"[AVAILABLE in REF] {tech}")
        else:
             print(f"[MISSING in REF] {tech}")

    print("\nPotential Conflict Analysis:")
    if total_avail > 0 and not present_consumers:
        print(f"  - {total_avail/1000:.2f} TWh BIOWASTE available but no technology to use it!")
        print("  - Did you forget to import BIOWASTE technologies for FI?")

if __name__ == "__main__":
    debug_biowaste()
