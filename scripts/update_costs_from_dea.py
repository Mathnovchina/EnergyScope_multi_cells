import pandas as pd
import numpy as np
import os

# Paths
base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells"
dea_path = os.path.join(base_path, "Data", "exogenous_data", "DEA_Elec_Heat.xlsx")
tech_csv_path = os.path.join(base_path, "Data", "2017", "02_REF_REGION", "Technologies.csv")

# Mapping: EnergyScope -> DEA Technology Name
# Note: Use substrings to match if exact names are tricky, but exact is better if confirmed.
mapping = {
    'WIND_ONSHORE': 'Onshore wind turbine, utility - renewable power - wind - large',
    'WIND_OFFSHORE': 'Offshore Wind - AC connected - Fixed bottom',
    'PV_ROOFTOP': 'PV - renewable power - solar - residential rooftop',
    'PV_UTILITY': 'PV - renewable power - solar - utility-scale, ground mounted',
    'CCGT': 'Gas turbine, combined cycle - extraction - natural gas - large',
    # DHN Technologies
    'DHN_HP_ELEC': 'Heat pump, sea water - heat pump - electricity - medium', 
    'DHN_BOILER_GAS': 'Gas boiler - boiler - natural gas - medium',
    'DHN_COGEN_GAS': 'Gas turbine, combined cycle - back pressure - natural gas - medium',
    'DHN_SOLAR': 'Solar DH - renewable heat - solar - medium',
    # Coal - proxy
    'COAL_US': 'Coal power plant, supercritical - extraction - coal - medium',
    # Industrial/Decentralized
    'IND_BOILER_GAS': 'Gas boiler - boiler - natural gas - medium',
    'IND_BOILER_WOOD': 'Biomass boiler - boiler - wood chips - medium',
    'DHN_BOILER_WOOD': 'Biomass boiler - boiler - wood chips - large',
}


def get_interpolated_value(df, tech_name, par_name, year_target=2017):
    # Filter by technology and parameter
    rows = df[
        (df['Technology'] == tech_name) & 
        (df['par'].str.contains(par_name, case=False, regex=False))
    ]
    
    if rows.empty:
        return None
    
    # Extract years
    rows = rows.sort_values('year')
    available_years = rows['year'].unique()
    
    # Logic: try to bracket 2017
    y_before = [y for y in available_years if y <= year_target]
    y_after = [y for y in available_years if y > year_target]
    
    val_target = None
    
    if y_before and y_after:
        y1 = y_before[-1] # Closest before (e.g. 2015)
        y2 = y_after[0]   # Closest after (e.g. 2020)
        v1 = float(rows[rows['year'] == y1]['val'].mean()) # Use mean if multiple entries
        v2 = float(rows[rows['year'] == y2]['val'].mean())
        val_target = v1 + (v2 - v1) * (year_target - y1) / (y2 - y1)
        
    elif y_before:
        # Only years before (e.g. data ends 2015), use last available
        y1 = y_before[-1]
        val_target = float(rows[rows['year'] == y1]['val'].mean())
        
    elif y_after:
        # Only years after (e.g. starts 2025), use first available (proxy)
        y2 = y_after[0]
        val_target = float(rows[rows['year'] == y2]['val'].mean())
        # For cost, if tech is maturing (Wind/PV), older values were likely higher.
        # But without data, using 2025 is safer than 0.
        # Optional: Add simple inflation factor? No, stick to data.
        
    return val_target

def update_costs():
    print("Loading DEA Excel...")
    dea_df = pd.read_excel(dea_path, sheet_name="alldata_flat")
    
    print("Loading Technologies.csv...")
    
    with open(tech_csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    header_idx = None
    for i, line in enumerate(lines):
        if 'Technologies param' in line:
            header_idx = i
            break
            
    if header_idx is None:
        print("Error: Could not find header")
        return

    columns = lines[header_idx].strip().split(',')
    try:
        idx_param = columns.index('Technologies param')
        idx_inv = columns.index('c_inv')
        idx_maint = columns.index('c_maint')
        idx_cp = columns.index('c_p')
    except ValueError as e:
        print(f"Error finding columns: {e}")
        return

    print("Updating lines...")
    new_lines = lines[:]
    updates_made = 0
    
    # 1. Update from DEA
    for es_tech, dea_tech in mapping.items():
        inv = get_interpolated_value(dea_df, dea_tech, "Nominal investment (*total)")
        fix_om = get_interpolated_value(dea_df, dea_tech, "Fixed O&M (*total)")
        var_om = get_interpolated_value(dea_df, dea_tech, "Variable O&M (*total)")
        
        if inv is None:
            print(f"Warning: No DEA investment data for {dea_tech}")
            continue

        val_inv = inv * 1000
        val_maint = fix_om / 1000 if fix_om is not None else 0
        val_cp = var_om if var_om is not None else 0
        
        found = False
        for i in range(len(new_lines)):
            parts = new_lines[i].strip().split(',')
            if len(parts) > idx_param and parts[idx_param] == es_tech:
                parts[idx_inv] = f"{val_inv:.2f}"
                parts[idx_maint] = f"{val_maint:.2f}"
                parts[idx_cp] = f"{val_cp:.2f}"
                new_lines[i] = ",".join(parts) + "\n"
                print(f"Updated {es_tech}: Inv={val_inv:.0f}, Maint={val_maint:.1f}, Cp={val_cp:.1f}")
                found = True
                updates_made += 1
                break
        
        if not found:
            print(f"Warning: Tech {es_tech} not found in Technologies.csv")
            
    # 2. Manual Updates (Nuclear, etc.)
    manual_updates = {
        'NUCLEAR': {'inv': 6000, 'maint': 120, 'cp': 0.0}, # OL3-like costs for validation
    }
    
    for es_tech, vals in manual_updates.items():
        found = False
        for i in range(len(new_lines)):
            parts = new_lines[i].strip().split(',')
            if len(parts) > idx_param and parts[idx_param] == es_tech:
                parts[idx_inv] = f"{vals['inv']:.2f}"
                parts[idx_maint] = f"{vals['maint']:.2f}"
                parts[idx_cp] = f"{vals['cp']:.2f}"
                new_lines[i] = ",".join(parts) + "\n"
                print(f"Updated {es_tech} (Manual): Inv={vals['inv']}, Maint={vals['maint']}, Cp={vals['cp']}")
                found = True
                updates_made += 1
                break

    if updates_made > 0:
        with open(tech_csv_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"\nSuccessfully updated {updates_made} technologies in {tech_csv_path}")


if __name__ == "__main__":
    update_costs()
