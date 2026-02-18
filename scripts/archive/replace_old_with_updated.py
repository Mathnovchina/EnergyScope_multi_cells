import os
import shutil
import time

base_dir = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
old_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_old.xlsx')
updated_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_old_UPDATED.xlsx')

def replace_file():
    print(f"Replacing {old_file} with {updated_file}...")
    
    if not os.path.exists(updated_file):
        print("Updated file not found! Aborting.")
        return

    # Try to remove the old file
    if os.path.exists(old_file):
        try:
            os.remove(old_file)
            print("Old file removed successfully.")
        except OSError as e:
            print(f"Error removing old file: {e}")
            print("It might be open in Excel. Please close it.")
            # If we can't remove it, we can't rename over it easily on Windows if locked.
            # But let's try to rename anyway, sometimes it works if only delete is blocked (unlikely).
            return

    # Rename updated to old
    try:
        os.rename(updated_file, old_file)
        print("Rename successful. Finland_MASTER_Calibration_old.xlsx is now the updated file.")
    except OSError as e:
        print(f"Error renaming file: {e}")
        # Fallback: copy content
        try:
            shutil.copy2(updated_file, old_file)
            print("Copy successful (fallback).")
            # If copy worked, we can delete the updated file
            os.remove(updated_file)
        except Exception as e2:
             print(f"Copy also failed: {e2}")

if __name__ == "__main__":
    replace_file()
