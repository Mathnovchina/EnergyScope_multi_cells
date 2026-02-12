
import pandas as pd
from datetime import datetime

file_path = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\exogenous_data\Finland_Calibration_UPDATES.xlsx'

def main():
    print(f"Creating {file_path}")
    today = datetime.now().strftime("%Y-%m-%d")
    
    with pd.ExcelWriter(file_path) as writer:
        # 1. Critical Changes
        changes_data = [
            ['High', 'WIND_ONSHORE 2017', '2035 constraint (f_min > 3GW) infeasible for 2017 (<2GW)', 'Update f_min using 2017 specific data', 'Done', 'Critical - Feasibility'],
            ['High', 'NUCLEAR 2035/2050', 'Forced to 0 GW in default config', 'Updated CSVs with realistic capacity (4.36 GW)', 'Done', 'Critical - Base Load']
        ]
        df_changes = pd.DataFrame(changes_data, columns=['Priority', 'Item', 'Issue', 'Fix', 'Status', 'Impact'])
        df_changes.to_excel(writer, sheet_name='3_Critical_Changes_Log', index=False)

        # 2. Next Steps
        steps_data = [
            ['Calibration', 1, 'Initial 2017 Model Run', 'Ready', '1 day', 'Data structure complete'],
            ['Post-Processing', 2, 'Validate 2017 Output vs Stats', 'Pending', '1 day', 'Check production mix']
        ]
        df_steps = pd.DataFrame(steps_data, columns=['Phase', 'Priority', 'Task', 'Status', 'Expected_Duration', 'Notes'])
        df_steps.to_excel(writer, sheet_name='11_Next_Steps_Log', index=False)

        # 3. Issues Decisions
        issues_data = [
            [today, '2017 demand data source', 'Use Energy in Finland 2022 (via Calibration file)', 'Validated source', 'Closed'],
            [today, 'Cost Learning Curves', 'Use static 2035 costs for now', 'No learning script in repo. Impact considered low for 2017 calib.', 'Open']
        ]
        df_issues = pd.DataFrame(issues_data, columns=['Date', 'Issue', 'Decision', 'Rationale', 'Status'])
        df_issues.to_excel(writer, sheet_name='12_Issues_Decisions_Log', index=False)
        
    print("New log file created.")

if __name__ == "__main__":
    main()
