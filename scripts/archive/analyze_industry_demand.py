import pandas as pd
import os

def analyze_industry_demand():
    # Path to the data file
    file_path = os.path.join(os.path.dirname(__file__), '..', 'Data', '2017', 'FI', 'Demands.csv')
    
    print(f"Reading file: {os.path.abspath(file_path)}")
    
    try:
        df = pd.read_csv(file_path, comment='#')
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Filter for relevant rows based on 'parameter name'
    # The relevant parameters are usually in the 3rd column, which seems to be unnamed in the provided snippet but header suggests 'parameter name'?
    # Actually, looking at the read_file output: Category,Subcategory,parameter name,HOUSEHOLDS...
    
    # Let's clean column names just in case
    df.columns = [c.strip() for c in df.columns]
    
    # We obey the user request:
    # HEAT_HIGH_T
    # HEAT_LOW_T_DECEN (if any). The file shows HEAT_LOW_T_SH and HEAT_LOW_T_HW. I will sum them as Low T heat.
    # ELECTRICITY
    # NON_ENERGY
    
    industry_col = 'INDUSTRY'
    
    if industry_col not in df.columns:
        print(f"Column '{industry_col}' not found in CSV.")
        print("Columns found:", df.columns)
        return

    # Helper to get value
    def get_val(param_name):
        row = df[df['parameter name'] == param_name]
        if not row.empty:
            return row[industry_col].values[0]
        return 0.0

    elec = get_val('ELECTRICITY')
    heat_high = get_val('HEAT_HIGH_T')
    
    # Summing Low T components
    heat_low_sh = get_val('HEAT_LOW_T_SH')
    heat_low_hw = get_val('HEAT_LOW_T_HW')
    heat_low = heat_low_sh + heat_low_hw
    
    non_energy = get_val('NON_ENERGY')
    
    # Process Cooling if interested (User didn't explicitly ask but good for context)
    process_cooling = get_val('PROCESS_COOLING')

    print("-" * 30)
    print("INDUSTRY DEMAND ANALYSIS (2017 Model Data)")
    print("-" * 30)
    
    # Convert GWh to TWh
    def gwh_to_twh(gwh):
        return gwh / 1000.0

    print(f"{'Category':<20} | {'GWh':>15} | {'TWh':>15}")
    print("-" * 56)
    print(f"{'ELECTRICITY':<20} | {elec:>15.2f} | {gwh_to_twh(elec):>15.2f}")
    print(f"{'HEAT_HIGH_T':<20} | {heat_high:>15.2f} | {gwh_to_twh(heat_high):>15.2f}")
    print(f"{'HEAT_LOW_T (SH+HW)':<20} | {heat_low:>15.2f} | {gwh_to_twh(heat_low):>15.2f}")
    print(f"{'  - SH':<20} | {heat_low_sh:>15.2f} | {gwh_to_twh(heat_low_sh):>15.2f}")
    print(f"{'  - HW':<20} | {heat_low_hw:>15.2f} | {gwh_to_twh(heat_low_hw):>15.2f}")
    print(f"{'NON_ENERGY':<20} | {non_energy:>15.2f} | {gwh_to_twh(non_energy):>15.2f}")
    print(f"{'PROCESS_COOLING':<20} | {process_cooling:>15.2f} | {gwh_to_twh(process_cooling):>15.2f}")
    print("-" * 56)
    
    total_heat = heat_high + heat_low
    print(f"{'TOTAL HEAT':<20} | {total_heat:>15.2f} | {gwh_to_twh(total_heat):>15.2f}")
    
    total_energy_incl_feedstock = elec + total_heat + non_energy + process_cooling
    print(f"{'TOTAL (Sum)':<20} | {total_energy_incl_feedstock:>15.2f} | {gwh_to_twh(total_energy_incl_feedstock):>15.2f}")

if __name__ == "__main__":
    analyze_industry_demand()
