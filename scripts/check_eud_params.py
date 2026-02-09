import pandas as pd
from pathlib import Path

# Config
BASE_DIR = Path(r"c:/Users/borde/OneDrive/Bureau/model/EnergyScope_multi_cells")
EXCEL_TEMPLATE_PATH = BASE_DIR / "Data/exogenous_data/EnergyScope_Finland_calibration_template_v4.xlsx"
DEMANDS_CSV_PATH = BASE_DIR / "Data/2017/FI/Demands.csv"

def check_eud_params():
    print(f"--- Checking EUD_params_simplified in {EXCEL_TEMPLATE_PATH.name} ---")
    
    if not EXCEL_TEMPLATE_PATH.exists():
        print(f"File not found: {EXCEL_TEMPLATE_PATH}")
        return

    try:
        # Read Excel
        # Depending on structure, headers might be on different rows
        df_xl = pd.read_excel(EXCEL_TEMPLATE_PATH, sheet_name="EUD_params_simplified")
        print("Excel Columns:", df_xl.columns.tolist())
        print("Excel Head:")
        print(df_xl.head(10))
        
        # Compare with Misc.json instead
        # Read the Excel sheet and extract key values
        # Column names: Parameter, Symbol, Value
        # Map Symbol to Misc.json keys
        
        # Example Mapping based on Misc.json keys I saw
        # share_heat_dhn_min/max  <- District heating share?
        # share_mobility_public_min/max
        # share_freight_train_min/max
        # share_freight_boat_min/max
        
        # Clean Excel - drop rows with NaN in Value or Symbol
        df_xl = df_xl.dropna(subset=['Value', 'Symbol'])
        
        import json
        
        MISC_JSON_PATH = BASE_DIR / "Data/2017/FI/Misc.json"
        
        print(f"\n--- Reading {MISC_JSON_PATH.name} ---")
        with open(MISC_JSON_PATH, 'r') as f:
            misc_data = json.load(f)
            
        print("Comparison:")
        for _, row in df_xl.iterrows():
            symbol = str(row['Symbol']).strip()
            val_excel = row['Value']
            
            # The symbols in Excel might not match JSON keys exactly, let's try direct matches or partials
            # Or manually check specific Known Ones
            
            # Only compare if we find a key in JSON that looks like it
            # JSON keys: share_heat_dhn_min, share_heat_dhn_max ...
            # Excel might just say "share_heat_dhn"
            
            # Manual Mapping logic for verification
            # %Dhn -> share_heat_dhn
            # %Public -> share_mobility_public
            # %Rail -> share_freight_train
            
            target_keys = []
            if symbol == "%Dhn":
                target_keys = ["share_heat_dhn_min", "share_heat_dhn_max"]
            elif symbol == "%Public":
                target_keys = ["share_mobility_public_min", "share_mobility_public_max"]
            elif symbol == "%Rail":
                target_keys = ["share_freight_train_min", "share_freight_train_max"]
                
            if target_keys:
                print(f"\nComparing Excel '{symbol}' ({val_excel}) with JSON:")
                for tk in target_keys:
                    if tk in misc_data:
                        json_val = misc_data[tk]
                        print(f"  - {tk}: {json_val}")
                        if abs(float(val_excel) - float(json_val)) > 0.05:
                            print("    -> MISMATCH (> 5%)")
                        else:
                            print("    -> MATCHES")
            else:
                 print(f"Unknown mapping for Excel symbol: {symbol} (Val: {val_excel})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_eud_params()
