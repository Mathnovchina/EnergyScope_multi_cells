import pandas as pd
import os
from datetime import datetime

def rebuild_master_calibration():
    # File Paths
    base_dir = os.path.join('Data', '2017', 'FI')
    output_file = 'Finland_Calibration_MASTER_2017.xlsx'
    
    csv_demands = os.path.join(base_dir, 'Demands.csv')
    csv_technologies = os.path.join(base_dir, 'Technologies.csv')
    csv_resources = os.path.join(base_dir, 'Resources.csv')

    # Read the data we currently have in CSVs
    print("Reading current CSV inputs...")
    df_demands = pd.read_csv(csv_demands)
    df_tech = pd.read_csv(csv_technologies)
    df_res = pd.read_csv(csv_resources)

    # Create the Log DataFrame
    print("Creating Change Log...")
    log_data = [
        ["Category", "Parameter", "Action", "Value / Note", "Source", "Date"],
        ["General", "Year", "Set to 2017", "2017", "User Request", datetime.now().strftime("%Y-%m-%d")],
        ["Demands", "ALL", "Updated values", "Used 2015 data for 2017 proxy", "Data/exogenous_data/regions/Demands.csv (JRC-IDEES/Eurostat)", datetime.now().strftime("%Y-%m-%d")],
        ["Technologies", "NUCLEAR", "Fixed Capacity", "2.76 GW", "Statistics Finland / Energy Authority", datetime.now().strftime("%Y-%m-%d")],
        ["Technologies", "WIND_ONSHORE", "Fixed Capacity", "Min: 1.5 GW, Max: 5.0 GW", "Statistics Finland (~2GW installed in 2017)", datetime.now().strftime("%Y-%m-%d")],
        ["Technologies", "PV_ROOFTOP", "Check Capacity", "Max 2.0 GW", "Estimation", datetime.now().strftime("%Y-%m-%d")],
        ["Resources", "Biomass/Waste", "Availability", "Imported from local estimates", "Finland_Calibration_MASTER (Pre-corruption)", datetime.now().strftime("%Y-%m-%d")]
    ]
    df_log = pd.DataFrame(log_data[1:], columns=log_data[0])

    # Write to Excel
    print(f"Writing to {output_file}...")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_log.to_excel(writer, sheet_name='Update_Log', index=False)
        df_demands.to_excel(writer, sheet_name='Demands', index=False)
        df_tech.to_excel(writer, sheet_name='Technologies', index=False)
        df_res.to_excel(writer, sheet_name='Resources', index=False)
        
        # Adjust column widths for readability (optional/effort)
        for sheet in writer.sheets:
            worksheet = writer.sheets[sheet]
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter # Get the column name
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width

    print(f"Successfully created {output_file} with proper logs and current data.")

if __name__ == "__main__":
    rebuild_master_calibration()
