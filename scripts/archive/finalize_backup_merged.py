import pandas as pd
import os
import shutil
import time

# Define paths
base_dir = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
source_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_V2.xlsx')
dest_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_old_UPDATED.xlsx')

def finalize_backup():
    print(f"Processing {source_file}...")
    
    if not os.path.exists(source_file):
        print(f"Error: Source file {source_file} does not exist.")
        return

    try:
        # Load the excel file to ensure it is valid and read sheets
        print("Reading source file to verify...")
        xls = pd.ExcelFile(source_file)
        sheet_names = xls.sheet_names
        print(f"Found {len(sheet_names)} sheets: {sheet_names}")
        xls.close()
        
        # Create the copy
        print(f"Copying to {dest_file}...")
        shutil.copy2(source_file, dest_file)
        print("Copy successful.")
        
        # Verify the new file
        print("Verifying new file...")
        xls_new = pd.ExcelFile(dest_file)
        new_sheets = xls_new.sheet_names
        xls_new.close()
        print(f"Verification successful. New file has {len(new_sheets)} sheets.")
        
        # Attempt to delete the old file
        print(f"Attempting to delete original file {source_file}...")
        try:
            os.remove(source_file)
            print("Original file deleted successfully.")
        except OSError as e:
            print(f"Warning: Could not delete original file. It might be open in another program. Error: {e}")
            print("You can manually delete it later.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    finalize_backup()
