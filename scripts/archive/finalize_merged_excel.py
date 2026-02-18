import pandas as pd
import os
import shutil
import time
import gc

# Define paths
base_dir = r"Data/exogenous_data"
path_v2 = os.path.join(base_dir, "Finland_MASTER_Calibration_V2.xlsx")
path_old = os.path.join(base_dir, "Finland_MASTER_Calibration_old.xlsx")
path_backup = os.path.join(base_dir, "Finland_MASTER_Calibration_old_NEW_CONTENT.xlsx")


def get_sheets(path, name):
    if not os.path.exists(path):
        print(f"File {name} does not exist at {path}")
        return []
    try:
        # Use context manager to ensure closure
        with pd.ExcelFile(path) as xl:
            print(f"Sheets in {name}: {xl.sheet_names}")
            return xl.sheet_names
    except Exception as e:
        print(f"Error reading {name}: {e}")
        return []

print("--- Initial State ---")
sheets_v2 = get_sheets(path_v2, "V2")
sheets_old = get_sheets(path_old, "OLD")


if not sheets_v2:
    print("V2 file is empty or unreadable. Aborting.")
    exit(1)

# Force garbage collection just in case
gc.collect()

print("\n--- Renaming ---")
# Retry logic for renaming 'old' to 'backup'
max_retries = 3
rename_success = False

# Remove backup if it exists and we're about to overwrite it
if os.path.exists(path_backup):
    try:
        os.remove(path_backup)
        print("Removed existing backup file.")
    except PermissionError:
        print("Could not remove existing backup file.")

if os.path.exists(path_old):
    print(f"Attempting to rename {path_old} to {path_backup}")
    for i in range(max_retries):
        try:
            os.rename(path_old, path_backup)
            print("Rename successful.")
            rename_success = True
            break
        except PermissionError:
            print(f"File is locked. Waiting 2 seconds... (Attempt {i+1}/{max_retries})")
            time.sleep(2)
    
    if not rename_success:
        print("Could not rename file. Please close Excel if open.")
        exit(1)
else:
    print(f"{path_old} not found, skipping rename to backup.")

# Now rename V2 to old
print(f"Renaming {path_v2} to {path_old}")
try:
    if os.path.exists(path_old):
        # This shouldn't happen if rename succeeded, but just in case
        os.remove(path_old) 
    os.rename(path_v2, path_old)
except PermissionError:
     print(f"Could not rename V2 to old. Please check if {path_old} is open.")
     exit(1)

print("\n--- Final Verification ---")
sheets_final = get_sheets(path_old, "FINAL (was V2)")

sheet_diff = set(sheets_v2) - set(sheets_final)
if not sheet_diff:
    print("SUCCESS: Final file has expected sheets.")
else:
    print(f"WARNING: Final file sheets differ from V2. Missing: {sheet_diff}")
