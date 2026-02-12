import pandas as pd
import os
from pathlib import Path

# Paths
workspace_root = Path(r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells")
master_calib_file = workspace_root / "Data/exogenous_data/Finland_MASTER_Calibration.xlsx"

def update_validation_sheet():
    # Data to log (Structured List of Dictionaries)
    validation_data = [
        # --- RESOURCES ---
        {
            "Category": "Resources",
            "Sub-Category": "Import Constraints (Legacy)",
            "Parameter / Tech": "Natural Gas (High Cost)",
            "Model Value": "15 TWh (Max)",
            "Real Value (2017)": "~25 TWh",
            "Delta/Gap": "Intentionally Constrained",
            "Hypothesis": "Gas usage in 2017 driven by legacy contracts/infra not economic in optimal model. Forced constraint allows focusing on Coal/Wood. High cost (0.20 eu/kWh) applied.",
            "Action Taken": "avail_exterior=15000, c_op=0.20"
        },
        {
            "Category": "Resources",
            "Sub-Category": "Import Constraints (Legacy)",
            "Parameter / Tech": "Light Fuel Oil (LFO)",
            "Model Value": "40 TWh (Max)",
            "Real Value (2017)": "~10-15 TWh (Heating)",
            "Delta/Gap": "Relaxed Ceiling",
            "Hypothesis": "Previous runs leaked massive LFO (100 TWh) when Gas was constrained. 40 TWh is a safety ceiling to prevent leakage while allowing feasibility.",
            "Action Taken": "avail_exterior=40000"
        },
        {
            "Category": "Resources",
            "Sub-Category": "Import Constraints (Legacy)",
            "Parameter / Tech": "Oil (Crude/Heavy)",
            "Model Value": "50 TWh (Max)",
            "Real Value (2017)": "Domestic Refinery Input",
            "Delta/Gap": "Proxy for Industry Use",
            "Hypothesis": "Heavy oil likely used in Industry. Constrained to prevent model form using it everywhere.",
            "Action Taken": "avail_exterior=50000"
        },
         {
            "Category": "Resources",
            "Sub-Category": "Import Constraints (Legacy)",
            "Parameter / Tech": "Transport Fuels (Gasoline/Diesel)",
            "Model Value": "~60 TWh (Combined)",
            "Real Value (2017)": "~50-60 TWh",
            "Delta/Gap": "Aligned",
            "Hypothesis": "Constrained to approximate transport demand to prevent cross-sector 'leakage'.",
            "Action Taken": "Gasoline=25000, Diesel=35000"
        },

        # --- EFFICIENCIES ---
        {
            "Category": "Efficiencies",
            "Sub-Category": "Degradation (Legacy Fleet)",
            "Parameter / Tech": "Wood Boilers & CHP",
            "Model Value": "Degraded 15-20%",
            "Real Value (2017)": "Lower than 2035 BAT",
            "Delta/Gap": "Adjustment for Reality",
            "Hypothesis": "2017 fleet is older/less efficient than 2035 Best Available Tech. Degrading efficiency forces higher fuel consumption to match primary energy statistics.",
            "Action Taken": "Layers_in_out: IND_BOILER/COGEN_WOOD degraded 15-20%."
        },
        {
            "Category": "Efficiencies",
            "Sub-Category": "Degradation (Legacy Fleet)",
            "Parameter / Tech": "Coal Boilers",
            "Model Value": "Degraded 15-20%",
            "Real Value (2017)": "Lower than 2035 BAT",
            "Delta/Gap": "Adjustment for Reality",
            "Hypothesis": "Coal plants are old. Inputs increased by 15-20% to represent lower thermal efficiency.",
            "Action Taken": "Layers_in_out: IND/DHN_COAL degraded 15-20%."
        },

        # --- TECHNOLOGY CONSTRAINTS ---
        {
            "Category": "Tech Constraints",
            "Sub-Category": "Must-Run (Sunk Costs)",
            "Parameter / Tech": "Coal/Peat Usage",
            "Model Value": "Forced Min Utilization",
            "Real Value (2017)": "High Usage",
            "Delta/Gap": "Economic Disadvantage in Model",
            "Hypothesis": "Coal is expensive in model but 'sunk cost' in 2017. Forced min market share (fmin_perc) required.",
            "Action Taken": "fmin_perc: IND_BOILER_COAL (30%), DHN_COGEN_COAL (20%)."
        },
        {
            "Category": "Tech Constraints",
            "Sub-Category": "Biomass",
            "Parameter / Tech": "Wood Usage",
            "Model Value": "Forced Min Utilization",
            "Real Value (2017)": "High Usage",
            "Delta/Gap": "-",
            "Hypothesis": "Finland has strong biomass mandate/industry. Forced share ensures it appears.",
            "Action Taken": "fmin_perc: IND_BOILER_WOOD (40%), DHN_COGEN_WOOD (40%)."
        },
        {
            "Category": "Tech Constraints",
            "Sub-Category": "Capacity limits",
            "Parameter / Tech": "Nuclear & Wind",
            "Model Value": "Fixed to 2017 stats",
            "Real Value (2017)": "2.7 GW / 2.0 GW",
            "Delta/Gap": "Match",
            "Hypothesis": "Capacity fixed to historical data.",
            "Action Taken": "Fixed f_min = f_max."
        }
    ]

    df_val = pd.DataFrame(validation_data)

    # Write to Excel
    try:
        if not os.path.exists(master_calib_file):
            print(f"Creating new Master Calibration file at {master_calib_file}")
            # Use 'openpyxl' engine which supports .xlsx
            df_val.to_excel(master_calib_file, sheet_name='2017 Validation', index=False)
        else:
            print(f"Updating existing Master Calibration file at {master_calib_file}")
            with pd.ExcelWriter(master_calib_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_val.to_excel(writer, sheet_name='2017 Validation', index=False)
        print("Calibration Log updated successfully.")
        
    except Exception as e:
        print(f"Could not write to file: {e}")
        backup_file = str(master_calib_file).replace(".xlsx", "_v2.xlsx")
        print(f"Trying backup: {backup_file}")
        df_val.to_excel(backup_file, sheet_name='2017 Validation', index=False)

if __name__ == "__main__":
    update_validation_sheet()
