import pandas as pd
import os

# Define paths
CASE_STUDY = "calib_2017_finland_v9"
BASE_PATH = os.path.join("case_studies", "FI", CASE_STUDY, "outputs")
YEAR_BALANCE_PATH = os.path.join(BASE_PATH, "Year_balance.csv")
ASSETS_PATH = os.path.join(BASE_PATH, "Assets.csv")
RESOURCES_PATH = os.path.join(BASE_PATH, "Resources.csv")

def main():
    print(f"--- Diagnosing Transport for {CASE_STUDY} ---")
    
    if not os.path.exists(YEAR_BALANCE_PATH):
        print(f"Error: {YEAR_BALANCE_PATH} not found.")
        return

    # Load data
    yb = pd.read_csv(YEAR_BALANCE_PATH, index_col=0)
    assets = pd.read_csv(ASSETS_PATH, index_col=0)
    res = pd.read_csv(RESOURCES_PATH, index_col=0)
    
    # 0. Check Input Demand
    demands_path = os.path.join("Data", "2017", "FI", "Demands.csv")
    if os.path.exists(demands_path):
        # Read without index first to handle structure properly
        demands_df = pd.read_csv(demands_path)
        # Clean column names if necessary (strip whitespace)
        demands_df.columns = [c.strip() for c in demands_df.columns]
        
        print("\n[0] Input Demands (from Data/2017/FI/Demands.csv):")
        
        # Check for parameter name column
        param_col = 'parameter name'
        if param_col not in demands_df.columns:
            # try to guess if casing is different
            for c in demands_df.columns:
                if 'parameter' in c.lower():
                    param_col = c
                    break
        
        target_demands = ['MOBILITY_PASSENGER', 'MOBILITY_FREIGHT']
        sectors = ['HOUSEHOLDS', 'SERVICES', 'INDUSTRY', 'TRANSPORTATION'] # potential demand columns
        
        for facial_dem in target_demands:
            row = demands_df[demands_df[param_col] == facial_dem]
            if not row.empty:
                # Sum the numeric columns that exist
                total_dem = 0
                for sec in sectors:
                    if sec in row.columns:
                         val = pd.to_numeric(row[sec].values[0], errors='coerce')
                         if not pd.isna(val):
                             total_dem += val
                print(f"  {facial_dem}: {total_dem:.2f}")
            else:
                print(f"  {facial_dem}: Not found in {param_col} column")

    else:
        print(f"Warning: {demands_path} not found.")

    # 1. Check Mobility Demand
    mob_cols = ['MOB_PRIVATE', 'MOB_PUBLIC', 'MOB_FREIGHT_ROAD', 'MOB_FREIGHT_RAIL']
    print("\n[1] Mobility Demand (End Uses):")
    for col in mob_cols:
        if col in yb.columns:
            # Check for END_USES_DEMAND row which usually holds the negative demand or check sum
            # Techs produce positive, Demand is negative or handled separately.
            # In YB, usually technologies produce (+) and Demand is consumed (-). 
            # Or "END_USES_DEMAND" row? Not standard.
            # Let's check the sum of all positive values in the column.
            production = yb[col][yb[col] > 0].sum()
            print(f"  {col}: {production:.2f} units (e.g. Mpkm/Mtkm)")
        else:
            print(f"  {col}: Not in Year_balance columns")

    # 2. Check CAR_GASOLINE / CAR_DIESEL
    cars = ['CAR_GASOLINE', 'CAR_DIESEL', 'CAR_HEV', 'CAR_PHEV', 'CAR_BEV', 'CAR_NG']
    print("\n[2] Passenger Cars (Capacity & Output):")
    for car in cars:
        cap = 0
        prod = 0
        fuel = 0
        
        if car in assets.index:
            cap = assets.loc[car, 'F'] # Installed capacity (GW or equiv)
        
        if car in yb.index:
            if 'MOB_PRIVATE' in yb.columns:
                prod = yb.loc[car, 'MOB_PRIVATE']
            
            # Find fuel consumption
            for fuel_col in ['GASOLINE', 'DIESEL', 'ELECTRICITY', 'GAS']:
                if fuel_col in yb.columns:
                    val = yb.loc[car, fuel_col]
                    if val < -0.01:
                        fuel_name = fuel_col
                        fuel = val
        
        print(f"  {car:15s} | Cap: {cap:10.2f} GW | Prod: {prod:10.2f} Mpkm | Fuel: {fuel:10.2f} ({fuel_name if fuel < 0 else ''})")

    # 3. Check Trucks/Freight
    trucks = ['TRUCK_DIESEL', 'TRUCK_ELEC', 'TRUCK_NG', 'TRUCK_FC', 'TRUCK_METHANOL']
    print("\n[3] Freight Road (Capacity & Output):")
    for truck in trucks:
        cap = 0
        prod = 0
        fuel = 0
        
        if truck in assets.index:
            cap = assets.loc[truck, 'F']
            
        if truck in yb.index:
            if 'MOB_FREIGHT_ROAD' in yb.columns:
                prod = yb.loc[truck, 'MOB_FREIGHT_ROAD']
             # Find fuel consumption
            for fuel_col in ['DIESEL', 'ELECTRICITY', 'GAS', 'METHANOL', 'H2']:
                if fuel_col in yb.columns:
                    val = yb.loc[truck, fuel_col]
                    if val < -0.01:
                        fuel_name = fuel_col
                        fuel = val
        
        print(f"  {truck:15s} | Cap: {cap:10.2f} GW | Prod: {prod:10.2f} Mtkm | Fuel: {fuel:10.2f} ({fuel_name if fuel < 0 else ''})")

    # 4. Check Resources (Imports)
    print("\n[4] Resources Imports (Balance):")
    fuels = ['GASOLINE', 'DIESEL', 'LFO', 'BIOETHANOL', 'BIODIESEL', 'WOOD']
    for f in fuels:
        if f in res.index:
            used = 0
            if 'R_year_exterior' in res.columns:
                used += res.loc[f, 'R_year_exterior']
            if 'R_year_local' in res.columns:
                used += res.loc[f, 'R_year_local']
            # Also check R_year_import if relevant
            imp = 0
            if 'R_year_import' in res.columns:
                imp = res.loc[f, 'R_year_import']
            print(f"  {f}: Used={used:.2f} (Import={imp:.2f})")
        elif f in yb.columns: 
             # Check total consumption in YB
            cons = yb[f].sum()
            print(f"  {f} (YB sum): {cons:.2f}")

    print("\n[5] Who produces GASOLINE and DIESEL?")
    for fuel in ['GASOLINE', 'DIESEL']:
        if fuel in yb.columns:
            # Sort by production (descending)
            producers = yb[fuel][yb[fuel] > 0.1].sort_values(ascending=False)
            print(f"  Producers of {fuel}:")
            for tech, val in producers.items():
                print(f"    {tech}: {val:.2f}")

if __name__ == "__main__":
    main()
