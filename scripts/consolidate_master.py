import pandas as pd
import os
from datetime import datetime

def consolidate_all_calibrations():
    """
    Consolidates ALL Finland calibration files into one comprehensive master file.
    Reads from:
    - Finland_Calibration_UPDATES.xlsx (log entries)
    - Finland_Calibration_MASTER_2017.xlsx (update log + data)
    - Finland_Calibration_Exhaustive_2017.xlsx (methodology + data)
    - Data/2017/FI/Demands.csv, Technologies.csv, Resources.csv (current state)
    
    Creates:
    - Data/exogenous_data/Finland_MASTER_Calibration.xlsx (single comprehensive file)
    """
    
    print("="*80)
    print("CONSOLIDATING ALL FINLAND CALIBRATION FILES")
    print("="*80)
    
    # ============================================================================
    # 1. Read all existing calibration files
    # ============================================================================
    
    # File 1: UPDATES (log entries)
    updates_path = 'Data/exogenous_data/Finland_Calibration_UPDATES.xlsx'
    df_updates_critical = pd.DataFrame()
    df_updates_next = pd.DataFrame()
    df_updates_issues = pd.DataFrame()
    
    if os.path.exists(updates_path):
        print(f"\nReading: {updates_path}")
        xls_updates = pd.ExcelFile(updates_path)
        if '3_Critical_Changes_Log' in xls_updates.sheet_names:
            df_updates_critical = pd.read_excel(xls_updates, '3_Critical_Changes_Log')
            print(f"  - Critical Changes: {len(df_updates_critical)} entries")
        if '11_Next_Steps_Log' in xls_updates.sheet_names:
            df_updates_next = pd.read_excel(xls_updates, '11_Next_Steps_Log')
            print(f"  - Next Steps: {len(df_updates_next)} entries")
        if '12_Issues_Decisions_Log' in xls_updates.sheet_names:
            df_updates_issues = pd.read_excel(xls_updates, '12_Issues_Decisions_Log')
            print(f"  - Issues/Decisions: {len(df_updates_issues)} entries")
    
    # File 2: MASTER_2017 (has update log)
    master2017_path = 'Finland_Calibration_MASTER_2017.xlsx'
    df_master2017_log = pd.DataFrame()
    
    if os.path.exists(master2017_path):
        print(f"\nReading: {master2017_path}")
        xls_master2017 = pd.ExcelFile(master2017_path)
        if 'Update_Log' in xls_master2017.sheet_names:
            df_master2017_log = pd.read_excel(xls_master2017, 'Update_Log')
            print(f"  - Update Log: {len(df_master2017_log)} entries")
    
    # File 3: EXHAUSTIVE (has methodology)
    exhaustive_path = 'Data/exogenous_data/Finland_Calibration_Exhaustive_2017.xlsx'
    df_methodology = pd.DataFrame()
    
    if os.path.exists(exhaustive_path):
        print(f"\nReading: {exhaustive_path}")
        xls_exhaustive = pd.ExcelFile(exhaustive_path)
        if 'Methodology_and_Sources' in xls_exhaustive.sheet_names:
            df_methodology = pd.read_excel(xls_exhaustive, 'Methodology_and_Sources')
            print(f"  - Methodology: {len(df_methodology)} entries")
    
    # ============================================================================
    # 2. Read current data state (the TRUTH)
    # ============================================================================
    
    print("\n" + "="*80)
    print("Reading CURRENT DATA STATE (source of truth)")
    print("="*80)
    
    csv_demands = os.path.join('Data', '2017', 'FI', 'Demands.csv')
    csv_tech = os.path.join('Data', '2017', 'FI', 'Technologies.csv')
    csv_res = os.path.join('Data', '2017', 'FI', 'Resources.csv')
    
    df_demands = pd.read_csv(csv_demands)
    df_tech = pd.read_csv(csv_tech)
    df_res = pd.read_csv(csv_res)
    
    print(f"  - Demands: {len(df_demands)} rows")
    print(f"  - Technologies: {len(df_tech)} rows")
    print(f"  - Resources: {len(df_res)} rows")
    
    # ============================================================================
    # 3. Create comprehensive master file
    # ============================================================================
    
    print("\n" + "="*80)
    print("CREATING COMPREHENSIVE MASTER FILE")
    print("="*80)
    
    output_path = os.path.join('Data', 'exogenous_data', 'Finland_MASTER_Calibration.xlsx')
    
    # Create comprehensive log by merging all logs
    print("\nConsolidating all logs...")
    
    # Start with methodology as base
    comprehensive_log = []
    
    # Add header
    comprehensive_log.append({
        'Category': 'METADATA',
        'Parameter': 'Document Title',
        'Value': 'Finland 2017 - Master Calibration File',
        'Source/Methodology': 'Consolidated from all previous calibration files',
        'Date': datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    comprehensive_log.append({
        'Category': 'METADATA',
        'Parameter': 'Scope',
        'Value': 'Finland (FI) - Year 2017',
        'Source/Methodology': 'EnergyScope Multi-cells Model',
        'Date': datetime.now().strftime("%Y-%m-%d")
    })
    
    # Add methodology entries
    if not df_methodology.empty:
        for _, row in df_methodology.iterrows():
            comprehensive_log.append({
                'Category': row.get('Category', ''),
                'Parameter': row.get('Item', ''),
                'Value': row.get('Description / Value', ''),
                'Source/Methodology': row.get('Source / Methodology', ''),
                'Date': row.get('Date Updated', '')
            })
    
    # Add entries from master2017 log
    if not df_master2017_log.empty:
        for _, row in df_master2017_log.iterrows():
            comprehensive_log.append({
                'Category': row.get('Category', ''),
                'Parameter': row.get('Parameter', ''),
                'Value': row.get('Value / Note', ''),
                'Source/Methodology': row.get('Source', ''),
                'Date': row.get('Date', '')
            })
    
    # Add critical changes from UPDATES
    if not df_updates_critical.empty:
        for _, row in df_updates_critical.iterrows():
            comprehensive_log.append({
                'Category': 'CRITICAL_CHANGE',
                'Parameter': row.get('Parameter_Changed', ''),
                'Value': str(row.get('New_Value', '')) + ' (was: ' + str(row.get('Previous_Value', '')) + ')',
                'Source/Methodology': row.get('Reason', ''),
                'Date': row.get('Date', '')
            })
    
    # Create DataFrame
    df_comprehensive_log = pd.DataFrame(comprehensive_log)
    
    # Remove duplicates based on Category + Parameter
    df_comprehensive_log = df_comprehensive_log.drop_duplicates(subset=['Category', 'Parameter'], keep='first')
    
    print(f"  - Comprehensive Log: {len(df_comprehensive_log)} unique entries")
    
    # ============================================================================
    # 4. Write to Excel
    # ============================================================================
    
    print(f"\nWriting to: {output_path}")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: Master Log
        df_comprehensive_log.to_excel(writer, sheet_name='1_Master_Log', index=False)
        
        # Sheet 2: Demands (Current State)
        df_demands.to_excel(writer, sheet_name='2_Demands', index=False)
        
        # Sheet 3: Technologies (Current State)
        df_tech.to_excel(writer, sheet_name='3_Technologies', index=False)
        
        # Sheet 4: Resources (Current State)
        df_res.to_excel(writer, sheet_name='4_Resources', index=False)
        
        # Sheet 5: Next Steps (if exists)
        if not df_updates_next.empty:
            df_updates_next.to_excel(writer, sheet_name='5_Next_Steps', index=False)
        
        # Sheet 6: Issues and Decisions (if exists)
        if not df_updates_issues.empty:
            df_updates_issues.to_excel(writer, sheet_name='6_Issues_Decisions', index=False)
        
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
                adjusted_width = min(max_length + 5, 80)
                worksheet.column_dimensions[column].width = adjusted_width
    
    print("\n" + "="*80)
    print("SUCCESS: Master file created")
    print("="*80)
    print(f"\nOutput: {output_path}")
    print(f"Sheets: 6 comprehensive sheets")
    print("\nYou can now delete the following files:")
    print("  - Finland_Calibration_MASTER_2017.xlsx")
    print("  - Data/exogenous_data/Finland_Calibration_UPDATES.xlsx")
    print("  - Data/exogenous_data/Finland_Calibration_Exhaustive_2017.xlsx")
    print("  - Data/exogenous_data/Finland_Calibration_MASTER.xlsx (already corrupted/empty)")

if __name__ == "__main__":
    consolidate_all_calibrations()
