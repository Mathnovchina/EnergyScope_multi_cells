import pandas as pd
import os
import sys

workspace_root = r"c:/Users/borde/OneDrive/Bureau/model/EnergyScope_multi_cells"
case_study = "calib_2017_finland"
output_dir = os.path.join(workspace_root, "case_studies/FI", case_study, "outputs")

def load_data():
    if not os.path.exists(output_dir):
        print(f"Output directory not found: {output_dir}")
        return None, None, None

    yb_path = os.path.join(output_dir, "Year_balance.csv")
    assets_path = os.path.join(output_dir, "Assets.csv")
    res_path = os.path.join(output_dir, "Resources.csv")

    yb = pd.read_csv(yb_path, index_col=0) if os.path.exists(yb_path) else None
    assets = pd.read_csv(assets_path, index_col=0) if os.path.exists(assets_path) else None
    res = pd.read_csv(res_path, index_col=0) if os.path.exists(res_path) else None
    
    return yb, assets, res

def print_mix(yb, assets, res):
    GWh_to_TWh = 1/1000.0
    
    # 1. Electricity Mix
    print("\n=== Electricity Generation (TWh) ===")
    if yb is not None and 'ELECTRICITY' in yb.columns:
        elec = yb['ELECTRICITY'] * GWh_to_TWh
        # Group by type
        groups = {
            'Nuclear': ['NUCLEAR', 'NUCLEAR_SMR'],
            'Wind': ['WIND_ONSHORE', 'WIND_OFFSHORE'],
            'Hydro': ['HYDRO_DAM', 'HYDRO_RIVER'],
            'Solar': ['PV_ROOFTOP', 'PV_UTILITY'],
            'Gas': ['CCGT', 'IND_COGEN_GAS', 'DHN_COGEN_GAS', 'DEC_ADVCOGEN_GAS', 'DEC_COGEN_GAS'],
            'Coal': ['COAL_US', 'COAL_IGCC', 'DHN_COGEN_COAL', 'IND_BOILER_COAL'], # Check names
            'Biomass': ['IND_COGEN_WOOD', 'DHN_COGEN_WOOD', 'BIOMASS_TO_POWER', 'DEC_COGEN_WOOD'],
            'Waste': ['IND_COGEN_WASTE', 'DHN_COGEN_WASTE', 'WT_TO_POWER'],
            'Import': ['Import'] # Not in Year_balance usually directly?
        }
        
        total_gen = 0
        for g, techs in groups.items():
            val = sum([elec.get(t, 0) for t in techs])
            if val > 0.01:
                print(f"{g:<10}: {val:.2f}")
                total_gen += val
        print(f"{'Total':<10}: {total_gen:.2f}")

    # 2. Heat Generation
    print("\n=== Heat Generation (TWh) ===")
    heat_cols = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']
    if yb is not None:
        for dh in heat_cols:
            if dh in yb.columns:
                print(f"\n--- {dh} ---")
                col = yb[dh] * GWh_to_TWh
                sorted_gen = col[col > 0.1].sort_values(ascending=False)
                for t, v in sorted_gen.items():
                   print(f"{t:<25}: {v:.2f}")

    # 3. Resources
    print("\n=== Resource Consumption (TWh) ===")
    if res is not None:
        # Calculate consumption: local + import + exterior - export
        # Or just look at what entered the system.
        # R_year_local + R_year_import + R_year_exterior
        cons = (res['R_year_local'] + res['R_year_import'] + res['R_year_exterior']) * GWh_to_TWh
        sorted_res = cons[cons > 0.1].sort_values(ascending=False)
        for r, v in sorted_res.items():
            print(f"{r:<20}: {v:.2f}")

    # 4. Capacities
    print("\n=== Key Installed Capacities (GW) ===")
    if assets is not None and 'f' in assets.columns:
        # Filter for interesting ones
        interesting = [
            'NUCLEAR', 'WIND_ONSHORE', 'HYDRO_RIVER', 'CCGT', 
            'IND_BOILER_WOOD', 'DHN_COGEN_WOOD', 'DEC_BOILER_WOOD',
            'IND_COGEN_GAS', 'DEC_ADVCOGEN_GAS', 'DEC_THHP_GAS',
            'DHN_HP_ELEC', 'DEC_HP_ELEC'
        ]
        for t in interesting:
            val = assets.loc[t, 'f'] if t in assets.index else 0
            if val > 0.001:
                 print(f"{t:<20}: {val:.3f}")
            else:
                 print(f"{t:<20}: 0.000 (or minimal)")

if __name__ == "__main__":
    yb, assets, res = load_data()
    if yb is not None:
        print_mix(yb, assets, res)
