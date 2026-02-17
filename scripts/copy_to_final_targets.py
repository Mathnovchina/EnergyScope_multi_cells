import shutil
import os

base_dir = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
updated_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_old_UPDATED.xlsx')
target_file = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration.xlsx')
target_file_new = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_NEW.xlsx')

def copy_to_target():
    print(f"Copying {updated_file} to {target_file}...")
    try:
        shutil.copy2(updated_file, target_file)
        print("Copy to Finland_MASTER_Calibration.xlsx successful.")
    except Exception as e:
        print(f"Failed to copy to Finland_MASTER_Calibration.xlsx: {e}")

    print(f"Copying {updated_file} to {target_file_new}...")
    try:
        shutil.copy2(updated_file, target_file_new)
        print("Copy to Finland_MASTER_Calibration_NEW.xlsx successful.")
    except Exception as e:
        print(f"Failed to copy to Finland_MASTER_Calibration_NEW.xlsx: {e}")

if __name__ == "__main__":
    copy_to_target()
