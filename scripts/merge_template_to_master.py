import pandas as pd
import os
from datetime import datetime

def merge_template_into_master():
    """
    Merges content from the template v4 file into the master calibration file.
    """
    
    print("="*80)
    print("MERGING TEMPLATE INTO MASTER CALIBRATION")
    print("="*80)
    
    # Read template
    template_path = 'Data/exogenous_data/EnergyScope_Finland_calibration_template_v4.xlsx'
    master_path = 'Data/exogenous_data/Finland_MASTER_Calibration.xlsx'
    
    print(f"\nReading template: {template_path}")
    xls_template = pd.ExcelFile(template_path)
    
    # Read all template sheets
    df_template_2020 = pd.read_excel(xls_template, 'Finland_inputs_2020')
    df_template_eud = pd.read_excel(xls_template, 'EUD_params_simplified')
    df_template_inputs = pd.read_excel(xls_template, 'Finland_inputs')
    df_template_comparators = pd.read_excel(xls_template, 'Comparators')
    df_template_method = pd.read_excel(xls_template, 'Method_notes')
    
    print(f"  - Finland_inputs_2020: {len(df_template_2020)} rows")
    print(f"  - EUD_params_simplified: {len(df_template_eud)} rows")
    print(f"  - Finland_inputs: {len(df_template_inputs)} rows")
    print(f"  - Comparators: {len(df_template_comparators)} rows")
    print(f"  - Method_notes: {len(df_template_method)} rows")
    
    # Read existing master
    print(f"\nReading master: {master_path}")
    xls_master = pd.ExcelFile(master_path)
    
    df_master_log = pd.read_excel(xls_master, '1_Master_Log')
    df_demands = pd.read_excel(xls_master, '2_Demands')
    df_tech = pd.read_excel(xls_master, '3_Technologies')
    df_res = pd.read_excel(xls_master, '4_Resources')
    df_next_steps = pd.read_excel(xls_master, '5_Next_Steps')
    df_issues = pd.read_excel(xls_master, '6_Issues_Decisions')
    
    print(f"  - Current sheets: {len(xls_master.sheet_names)}")
    
    # Create new comprehensive master
    print("\nCreating comprehensive master with template data...")
    
    output_path = master_path  # Overwrite existing
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Existing sheets (numbered 1-6)
        df_master_log.to_excel(writer, sheet_name='1_Master_Log', index=False)
        df_demands.to_excel(writer, sheet_name='2_Demands', index=False)
        df_tech.to_excel(writer, sheet_name='3_Technologies', index=False)
        df_res.to_excel(writer, sheet_name='4_Resources', index=False)
        df_next_steps.to_excel(writer, sheet_name='5_Next_Steps', index=False)
        df_issues.to_excel(writer, sheet_name='6_Issues_Decisions', index=False)
        
        # Template sheets (numbered 7-11)
        df_template_method.to_excel(writer, sheet_name='7_Method_Notes', index=False)
        df_template_2020.to_excel(writer, sheet_name='8_Finland_Inputs_2020', index=False)
        df_template_eud.to_excel(writer, sheet_name='9_EUD_Parameters', index=False)
        df_template_inputs.to_excel(writer, sheet_name='10_Finland_Inputs', index=False)
        df_template_comparators.to_excel(writer, sheet_name='11_Comparators', index=False)
        
        # Format all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 5, 100)
                worksheet.column_dimensions[column].width = adjusted_width
    
    print("\n" + "="*80)
    print("SUCCESS: Master file updated with template content")
    print("="*80)
    print(f"\nOutput: {output_path}")
    print(f"Total Sheets: 11")
    print(f"\nStructure:")
    print(f"  Sheets 1-6: Current 2017 calibration data & logs")
    print(f"  Sheets 7-11: Reference data from template v4")

if __name__ == "__main__":
    merge_template_into_master()
