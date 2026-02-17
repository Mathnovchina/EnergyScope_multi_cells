import pandas as pd
import os
import shutil

# Paths
base_dir = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
source_a_path = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration (1).xlsx')
source_b_path = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_old.xlsx')
merged_path = os.path.join(base_dir, 'Data', 'exogenous_data', 'Finland_MASTER_Calibration_Merged.xlsx')

print(f"Reading Source A: {source_a_path}")
try:
    # Use sheet_name=None to read all sheets into a dict of dataframes
    xls_a = pd.ExcelFile(source_a_path)
    source_a_sheets = {sheet_name: xls_a.parse(sheet_name) for sheet_name in xls_a.sheet_names}
except Exception as e:
    print(f"Error reading Source A: {e}")
    exit(1)

print(f"Reading Source B: {source_b_path}")
try:
    xls_b = pd.ExcelFile(source_b_path)
    source_b_sheets = {sheet_name: xls_b.parse(sheet_name) for sheet_name in xls_b.sheet_names}
except Exception as e:
    print(f"Error reading Source B: {e}")
    exit(1)

print("Merging sheets...")
# Using ExcelWriter to write sheets one by one
# Check if file exists to remove it first, although 'w' mode should handle it,
# but sometimes excel locks files or appends weirdly if not careful.
if os.path.exists(merged_path):
    os.remove(merged_path)

with pd.ExcelWriter(merged_path, engine='openpyxl') as writer:
    existing_sheet_names = set()

    # --- Process Source A (The "Old/Original" content - Priority 1 as per instruction to copy first) ---
    for sheet_name, df in source_a_sheets.items():
        # Clean sheet name logic
        clean_name = sheet_name
        
        # Excel sheet name limit is 31 chars
        if len(clean_name) > 31:
            clean_name = clean_name[:31]
            
        # Ensure Uniqueness within Source A (unlikely to have dups but good practice)
        original_base = clean_name
        counter = 1
        while clean_name.lower() in [s.lower() for s in existing_sheet_names]:
            suffix = f"_{counter}"
            clean_name = f"{original_base[:31-len(suffix)]}{suffix}"
            counter += 1
            
        df.to_excel(writer, sheet_name=clean_name, index=False)
        existing_sheet_names.add(clean_name)
        print(f"  [A] Added: '{clean_name}'")

    # --- Process Source B (The "New/Price Update" content) ---
    for sheet_name, df in source_b_sheets.items():
        # Logic: If exists in A, rename. If new, keep name.
        
        clean_name = sheet_name
        # Check against existing names from A
        # The user says: "If a sheet name exists in both... rename the one from Source B"
        
        # If the exact name exists, or a case-insensitive match exists
        is_duplicate = False
        if clean_name.lower() in [s.lower() for s in existing_sheet_names]:
            is_duplicate = True
            
        if is_duplicate:
            # It exists in A. Rename B's version.
            # User suggestion: "Overview_PriceUpdate"
            # General approach: Append "_Update"
            suffix = "_Update"
            base_len = 31 - len(suffix)
            candidate_name = f"{clean_name[:base_len]}{suffix}"
            
            # Ensure this new candidate name is also valid and unique
            original_candidate = candidate_name
            counter = 1
            while candidate_name.lower() in [s.lower() for s in existing_sheet_names]:
                 suffix_cnt = f"_{counter}"
                 # Recalculate base to fit suffix+counter
                 # e.g. "Overview_Update_1"
                 # We want the "_Update" part to stick if possible, so maybe just append number
                 # Let's just create a unique name based on the original name
                 unique_suffix = f"_Upd{counter}"
                 candidate_name = f"{clean_name[:31-len(unique_suffix)]}{unique_suffix}"
                 counter += 1
            
            clean_name = candidate_name
            print(f"  [B] Renamed duplicate '{sheet_name}' to '{clean_name}'")
        else:
             # It's new in B, keep it (checking length and uniqueness just in case B has internal dups or conflicts with truncated A names)
            if len(clean_name) > 31:
                clean_name = clean_name[:31]
            
            original_base = clean_name
            counter = 1
            while clean_name.lower() in [s.lower() for s in existing_sheet_names]:
                suffix = f"_{counter}"
                clean_name = f"{original_base[:31-len(suffix)]}{suffix}"
                counter += 1
            print(f"  [B] Added new: '{clean_name}'")

        df.to_excel(writer, sheet_name=clean_name, index=False)
        existing_sheet_names.add(clean_name)

print(f"\nMerged file created at: {merged_path}")

# Verify
print("-" * 30)
print("Verifying merged file content:")
try:
    merged_xls = pd.ExcelFile(merged_path)
    print(f"Total sheets: {len(merged_xls.sheet_names)}")
    for sheet in merged_xls.sheet_names:
        print(f" - {sheet}")
except Exception as e:
    print(f"Error verifying merged file: {e}")
    exit(1)

print("\nMerge procedure completed successfully.")
