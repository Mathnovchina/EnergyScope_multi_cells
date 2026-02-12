import pandas as pd
import os

base_path = r"c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells\Data\2017"
res_path = os.path.join(base_path, "02_REF_REGION", "Resources.csv")
net_path = os.path.join(base_path, "01_EXCH", "Network_exchanges.csv")

def update_data():
    # 1. Update Resources Costs (2017 estimates)
    # Note: Resources.csv header is row 3 (index 2).
    # We read carefully to preserve structure.
    
    with open(res_path, 'r') as f:
        lines = f.readlines()
        
    # Find indices
    header_found = False
    idx_price = -1
    idx_param = -1
    
    for i, line in enumerate(lines):
        if "Category,Subcategory,parameter name" in line:
            parts = line.strip().split(',')
            try:
                idx_param = parts.index('parameter name')
                idx_price = parts.index('c_op_local')
                header_found = True
                print(f"Header found at line {i}")
            except ValueError:
                pass
            break
            
    if header_found:
        updates = {
            'ELECTRICITY': 0.0332, # ~33.2 EUR/MWh (Nord Pool 2017 sys)
            'GAS': 0.020,          # ~20 EUR/MWh (TTF/Import proxy 2017)
            'COAL': 0.010,         # ~10 EUR/MWh
            'DIESEL': 0.057,       # ~0.57 EUR/l -> ~57 EUR/MWh
            'GASOLINE': 0.060,     # ~0.60 EUR/l pre-tax wholesale
            'LFO': 0.055,
            'WOOD': 0.018          # ~18 EUR/MWh (Forest chips 2017)
        }
        
        count = 0
        for i in range(len(lines)):
            parts = lines[i].strip().split(',')
            if len(parts) > idx_param:
                res = parts[idx_param]
                if res in updates:
                    parts[idx_price] = str(updates[res])
                    lines[i] = ",".join(parts) + "\n"
                    print(f"Updated price for {res} to {updates[res]}")
                    count += 1
        
        if count > 0:
            with open(res_path, 'w') as f:
                f.writelines(lines)
            print("Resources.csv updated.")
            
    # 2. Update Network Exchanges (Gas FI-EE)
    print("\nUpdating Network Exchanges...")
    df_net = pd.read_csv(net_path)
    
    # Condition: From FI to EE or EE to FI, for GAS, set tc_min to 0
    # Actually Balticconnector didn't exist, so capacity is 0. 
    # But usually tc_min is existing. Set tc_min=0. tc_max=20 (future potential is fine).
    
    mask_gas_fi_ee = (
        ((df_net['From'] == 'FI') & (df_net['To'] == 'EE') & (df_net['Resources'] == 'GAS')) |
        ((df_net['From'] == 'EE') & (df_net['To'] == 'FI') & (df_net['Resources'] == 'GAS'))
    )
    
    if mask_gas_fi_ee.any():
        print("Found FI-EE Gas connection. Setting tc_min to 0 (Balticconnector opened 2020).")
        df_net.loc[mask_gas_fi_ee, 'tc_min'] = 0
        
        # Save keeping format
        df_net.to_csv(net_path, index=False)
        print("Network_exchanges.csv updated.")
    else:
        print("No FI-EE Gas connection found.")

if __name__ == "__main__":
    update_data()
