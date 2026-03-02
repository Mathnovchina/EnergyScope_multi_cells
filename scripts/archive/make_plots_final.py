
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os
import sys
import numpy as np

# Configuration
CASE_PATH = "case_studies/FI/calib_2017_finland"
OUTPUT_DIR = os.path.join(CASE_PATH, "outputs")
PLOT_DIR = "plots"
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

YEAR_BALANCE_FILE = os.path.join(OUTPUT_DIR, "Year_balance.csv")

def get_color(name):
    name = name.upper()
    if "WOOD" in name or "BIO" in name: return "#2ca02c" # Green
    if "COAL" in name: return "#000000" # Black
    if "GAS" in name and "GASOLINE" not in name: return "#7f7f7f" # Grey
    if "OIL" in name or "DIESEL" in name or "GASOLINE" in name or "LFO" in name: return "#8c564b" # Brown
    if "ELEC" in name: return "#ff7f0e" # Orange
    if "HEAT" in name: return "#d62728" # Red
    if "WIND" in name: return "#1f77b4" # Blue
    if "SOLAR" in name: return "#e377c2" # Pink
    if "HYDRO" in name: return "#9467bd" # Purple
    if "URANIUM" in name or "NUCLEAR" in name: return "#bcbd22" # Olive
    return "#c7c7c7" # Default Grey

def plot_energy_mix(df):
    """
    Generate bar chart for Primary Energy Mix
    """
    print("Generating Energy Mix Plot...")
    
    # Define Primary Resources
    # Map model columns to Display Labels
    # We want to group Coal and Peat if Peat exists (or just rename Coal)
    
    resource_map = {
        "COAL": "Coal & Peat",
        "GAS": "Natural Gas",
        "URANIUM": "Nuclear",
        "WOOD": "Wood & Biomass",
        "WET_BIOMASS": "Wood & Biomass",
        "BIOWASTE": "Wood & Biomass",
        "BIOMASS_RESIDUES": "Wood & Biomass",
        "ENERGY_CROPS_2": "Wood & Biomass",
        "WASTE": "Waste",
        "GASOLINE": "Oil Products",
        "DIESEL": "Oil Products",
        "LFO": "Oil Products",
        "JET_FUEL": "Oil Products",
        "RES_WIND": "Wind",
        "RES_SOLAR": "Solar",
        "RES_HYDRO": "Hydro",
        "RES_GEO": "Geothermal"
    }
    
    # Calculate Consumption
    # Logic: For each resource column, sum the POSITIVE flows (Production) from Resource Supply rows?
    # Or sum Inputs (Negative) to consumer techs?
    # In Year_balance, Resource Supply rows (e.g. "GAS") have Positive in GAS column.
    
    consumption = {}
    
    for col in df.columns:
        if col in resource_map:
            label = resource_map[col]
            # Identify "Supply" rows. Usually the row name is the same as the resource name
            # e.g. Row "GAS" has value in Col "GAS".
            # Or Import rows.
            # A safer way to get "Primary Consumption" is to sum the 'Production' of the resource carrier 
            # by the "Resource" technology (which is usually named same as dataset).
            
            # Use positive values in the column, strictly from Resource-like rows
            # But simpler: Sum of all POSITIVE values in that column that come from "Supply" rows.
            # Which rows are supply? "GAS", "COAL", "WOOD", imports.
            
            # Heuristic: Sum of Positive Values in the column.
            # This works because:
            # - Techs CONSUME (Negative).
            # - Supply PROVIDES (Positive).
            # - END_USE is usually Consumption.
            # Be careful of Intermediate productions (e.g. Synfuel). 
            # We want PRIMARY.
            
            # For Primary Resources, usually no tech produces them except the "Import/Extraction" tech.
            # So Sum(Positive) shoud be correct.
            # Exception: Synfuels (e.g. BIOMASS_TO_GASOLINE). 
            # GASOLINE is not strictly Primary. 
            # But the user wants "Energy Mix" -> usually Primary Energy Consumption (PEC).
            # For Oil Products: This is tricky. 30 TWh Diesel imported (Primary) v.s. refined?
            # In ESMC, imported fuels are Primary if they enter the system boundaries.
            
            total_supply = df[col][df[col] > 0].sum()
            
            # If it's a secondary carrier (like Hydrogen or Electricity), we shouldn't sum it here?
            # The list in `resource_map` are Primary Candidates.
            # "GASOLINE" can be secondary. 
            # But if we import it, it counts as PEC. If we make it from Biomass, we count Biomass (Primary) not Gasoline.
            # How to distinguish Import vs Production from other stuff?
            # We check the ROW.
            # Import rows usually match the Resource Name or are special import techs.
            
            # Let's filter by Row Names that look like Resources or "Import".
            # Or simpler: The "Resource" rows in Year_balance are typically named exactly as the column.
            # e.g. Row `GAS` -> Col `GAS`.
            # Row `GAS_RE` -> Col `GAS_RE`. (Renewable Gas import?)
            # Let's try iterating rows.
            
            if col in df.index:
                val = df.loc[col, col]
                if val > 0:
                    consumption[label] = consumption.get(label, 0) + val
            
            # Also catch specific inputs if they are primary but not named same as col?
            # E.g. `GASOLINE` row? 
            # Let's just stick to Sum(Positive) logic BUT exclude techs that convert X to Y.
            # Techs usually produce Y > 0.
            # e.g. `BIOMASS_TO_GASOLINE`: `GASOLINE` > 0.
            # If we count this, we double count (Biomass + Gasoline).
            # So checks strictly for "Source" rows.
            # In ESMC, Source rows are the ones named in Resources.csv.
            # They appear as rows in Year_balance.
            
            if col in df.index:
                 pass # handled above
            elif col == "GASOLINE": 
                 # Check for GASOLINE row ? 
                 if "GASOLINE" in df.index:
                     consumption[label] = consumption.get(label, 0) + df.loc["GASOLINE", "GASOLINE"]
            
    # Iterate all rows, if row_name == col_name or row_name in known_imports, add to sum
    # This is safer.
    
    # Refined Logic:
    # 1. Reset consumption dict
    consumption = {}
    
    # 2. Key Primary imports/sources
    # We use the list of resources from resource_map.
    for r in resource_map.keys():
        if r not in df.columns:
            continue
        label = resource_map[r]
        if r in df.index:
             val = df.loc[r, r]
             if val > 0:
                 consumption[label] = consumption.get(label, 0) + val
                 
    # 3. Add Import techs if any?
    # In ESMC, "GASOLINE" row is the import/avail node.
    
    # 4. Handle specific case: URANIUM
    # Uranium is consumed by NUCLEAR row. In Year_balance, URANIUM col is negative in NUCLEAR row.
    # Supply is in URANIUM row?
    if "URANIUM" in df.index:
        val = df.loc["URANIUM", "URANIUM"]
        # If 0, check consumption
        if val == 0:
             # Look for negative consumption in NUCLEAR
             if "NUCLEAR" in df.index:
                 # It consumes negative
                 consumption["Nuclear"] = abs(df.loc["NUCLEAR", "URANIUM"])

    # Convert to TWh (divide by 1000)
    for k in consumption:
        consumption[k] /= 1000.0

    # Create Series
    s = pd.Series(consumption).sort_values(ascending=False)
    
    # Plot
    plt.figure(figsize=(12, 8))
    colors = [get_color(k) for k in s.index]
    bars = s.plot(kind='bar', color=colors, edgecolor='black')
    
    plt.title("Primary Energy Consumption (TWh) - Finland 2017 Calibration", fontsize=16)
    plt.ylabel("TWh", fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on top
    for i, v in enumerate(s):
        plt.text(i, v + 2, f"{v:.1f}", ha='center', fontsize=11)
        
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "Primary_Energy_Mix.png"))
    plt.close()
    print("Energy Mix Plot Saved.")

def generate_sankey(df):
    """
    Generate Sankey Diagram HTML using Plotly
    """
    print("Generating Sankey Diagram...")
    
    # Filter columns to interesting ones
    # Exclude CO2, Cost(?), etc.
    cols = [c for c in df.columns if "CO2" not in c and "COST" not in c]
    
    # Nodes: Columns (Carriers) + Rows (Techs)
    # To reduce size, we can aggregate Technologies into Categories
    # e.g. "CCGT", "CCGT_AMMONIA" -> "Thermal Plants"
    # But let's verify size first.
    
    # Create Node List
    # Use index for lookup
    
    nodes = []
    node_indices = {}
    
    def get_node_id(name):
        if name not in node_indices:
            node_indices[name] = len(nodes)
            nodes.append(name)
        return node_indices[name]

    sources = []
    targets = []
    values = []
    link_colors = []
    
    # Threshold for displaying flow (TWh/y) -> GWh in table
    THRESHOLD = 500 # 0.5 TWh
    
    # Iterate Rows (Techs)
    for tech_name, row in df.iterrows():
        # Treat End Use differently?
        # NO, END_USES is just a sink tech.
        
        # Link Logic:
        # Carrier (Col) -> Tech (Row) if Val < 0
        # Tech (Row) -> Carrier (Col) if Val > 0
        
        # Determine Tech Category for Color/Grouping
        # Maybe clean name?
        tech_label = tech_name
        
        # Add links
        for col in cols:
            val = row[col]
            if abs(val) < THRESHOLD: continue
            
            carrier_label = col
            
            # Color logic
            color = get_color(col)
            
            if val < 0:
                # Input: Carrier -> Tech
                # Use opacity for links
                lnk_color = color.replace(")", ", 0.4)").replace("rgb", "rgba")
                if "#" in color: lnk_color = color # hex handling todo
                
                sources.append(get_node_id(carrier_label))
                targets.append(get_node_id(tech_label))
                values.append(abs(val)/1000.0) # TWh
                # link_colors.append(lnk_color)
                
            elif val > 0:
                # Output: Tech -> Carrier
                sources.append(get_node_id(tech_label))
                targets.append(get_node_id(carrier_label))
                values.append(val/1000.0) # TWh
                
    # Create Plotly Sankey
    # Node Colors
    node_colors = [get_color(n) for n in nodes]
    
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = nodes,
          color = node_colors
        ),
        link = dict(
          source = sources,
          target = targets,
          value = values,
          # color = link_colors
      ))])

    fig.update_layout(title_text="Energy Flows (2017) - TWh", font_size=12, height=1200)
    
    out_file = os.path.join(PLOT_DIR, "Sankey_Diagram.html")
    fig.write_html(out_file)
    print(f"Sankey saved to {out_file}")

# Main Execution
if __name__ == "__main__":
    if not os.path.exists(YEAR_BALANCE_FILE):
        print(f"Error: {YEAR_BALANCE_FILE} not found.")
        sys.exit(1)
        
    # Read Data
    # Try different separators
    try:
        df = pd.read_csv(YEAR_BALANCE_FILE, index_col=0, sep=",")
    except:
        df = pd.read_csv(YEAR_BALANCE_FILE, index_col=0, sep=";")
        
    plot_energy_mix(df)
    generate_sankey(df)
