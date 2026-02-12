import pandas as pd
import os
from datetime import datetime

def create_exhaustive_calibration():
    # Paths
    # Input paths (Current state of the model)
    path_2017 = os.path.join('Data', '2017', 'FI')
    csv_demands = os.path.join(path_2017, 'Demands.csv')
    csv_tech = os.path.join(path_2017, 'Technologies.csv')
    csv_res = os.path.join(path_2017, 'Resources.csv')
    
    # Output path
    output_dir = os.path.join('Data', 'exogenous_data')
    output_file = os.path.join(output_dir, 'Finland_Calibration_Exhaustive_2017.xlsx')

    print(f"Reading data from {path_2017}...")
    
    # Read Data
    df_demands = pd.read_csv(csv_demands)
    df_tech = pd.read_csv(csv_tech)
    df_res = pd.read_csv(csv_res)

    # Create Methodology & Sources DataFrame
    meta_data = [
        ["Category", "Item", "Description / Value", "Source / Methodology", "Date Updated"],
        ["General", "Scope", "Finland (FI) - Year 2017", "EnergyScope Multi-cells Calibration", datetime.now().strftime("%Y-%m-%d")],
        ["Demands", "Electricity & Heat", "2015 Statistical Data", "JRC-IDEES/Eurostat (via regions/Demands.csv). Used as 2017 proxy due to data availability and stability.", datetime.now().strftime("%Y-%m-%d")],
        ["Demands", "Mobility", "2015 Statistical Data", "JRC-IDEES/Eurostat (via regions/Demands.csv).", datetime.now().strftime("%Y-%m-%d")],
        ["Technologies", "NUCLEAR", "2.76 GW (Fixed)", "Statistics Finland. Reflects Loviisa 1&2 + Olkiluoto 1&2. No OL3 in 2017.", datetime.now().strftime("%Y-%m-%d")],
        ["Technologies", "WIND_ONSHORE", "Min: 1.5 GW, Max: 5.0 GW", "Statistics Finland (~2GW installed in 2017). Lower bound ensures model respects existing infra.", datetime.now().strftime("%Y-%m-%d")],
        ["Technologies", "PV_ROOFTOP", "Max: 2.0 GW", "Estimated potential for rooftop installations.", datetime.now().strftime("%Y-%m-%d")],
        ["Resources", "Biomass (Wood, Crops, Waste)", "Aggregated Potentials", "Derived from local expert estimates/original calibration inputs.", datetime.now().strftime("%Y-%m-%d")],
        ["Constraints", "Wind Cap", "Fixed infeasibility", "Resolved conflict where default model required 3GW+ wind. Lowered min to 1.5GW.", datetime.now().strftime("%Y-%m-%d")]
    ]
    df_meta = pd.DataFrame(meta_data[1:], columns=meta_data[0])

    print(f"Writing comprehensive file to {output_file}...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Methodology
        df_meta.to_excel(writer, sheet_name='Methodology_and_Sources', index=False)
        
        # Sheet 2: Demands
        df_demands.to_excel(writer, sheet_name='Demands_2017', index=False)
        
        # Sheet 3: Technologies
        df_tech.to_excel(writer, sheet_name='Technologies_2017', index=False)
        
        # Sheet 4: Resources
        df_res.to_excel(writer, sheet_name='Resources_2017', index=False)

        # Formatting
        for sheet in writer.sheets:
            worksheet = writer.sheets[sheet]
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 5)
                worksheet.column_dimensions[column].width = adjusted_width

    print("Success. File created.")

if __name__ == "__main__":
    create_exhaustive_calibration()
