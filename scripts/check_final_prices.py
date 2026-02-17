import pandas as pd
import os

# Define file path
file_path = os.path.join('Data', '2017', 'FI', 'Resources.csv')

# Check if file exists
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    # Read the CSV file
    df = pd.read_csv(file_path, index_col=0)

    # List of resources to check
    resources_to_check = ['COAL', 'GAS', 'LFO', 'DIESEL', 'GASOLINE', 'JET_FUEL']
    
    # Filter for these resources if they exist
    existing_resources = [res for res in resources_to_check if res in df.index]
    
    # Print the table with specific columns
    print(f"{'Resource':<15} {'c_op_local':<15} {'avail_exterior':<20}")
    print("-" * 50)
    
    for res in existing_resources:
        c_op = df.loc[res, 'c_op_local']
        avail = df.loc[res, 'avail_exterior']
        print(f"{res:<15} {c_op:<15.4f} {avail:<20.1f}")

    # Verify expected values
    expected_values = {
        'COAL': 0.0103,
        'GAS': 0.0195,
        'LFO': 0.0521,
        'DIESEL': 0.0543,
        'GASOLINE': 0.0588,
        'JET_FUEL': 0.0359
    }

    print("\nVerification:")
    all_match = True
    for res, expected in expected_values.items():
        if res in df.index:
            actual = df.loc[res, 'c_op_local']
            # Check with a small tolerance
            if abs(actual - expected) < 1e-6:
                print(f"[OK] {res}: {actual}")
            else:
                print(f"[FAIL] {res}: Expected {expected}, got {actual}")
                all_match = False
        else:
            print(f"[MISSING] {res} not found in file")
            all_match = False
            
    if all_match:
        print("\nAll checks passed successfully.")
    else:
        print("\nSome checks failed.")
