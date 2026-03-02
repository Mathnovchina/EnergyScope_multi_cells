"""Compare v5_fperc original outputs vs rerun outputs."""
import pandas as pd
import os

base = r'c:\Users\borde\OneDrive\Bureau\model\EnergyScope_multi_cells'
orig = os.path.join(base, 'case_studies', 'FI', 'calib_2017_finland_v5_fperc', 'outputs')
rerun = os.path.join(base, 'case_studies', 'FI', 'calib_2017_finland_v5_fperc_repro', 'outputs')

def load(d, f):
    p = os.path.join(d, f)
    if not os.path.exists(p):
        return pd.DataFrame()
    try:
        return pd.read_csv(p)
    except:
        return pd.read_csv(p, sep=';')

# ── 1. Objective ──
print("=" * 80)
print("1. OBJECTIVE FUNCTION")
print("=" * 80)
obj_o = load(orig, 'Objective.csv')
obj_r = load(rerun, 'Objective.csv')
print("Original:")
print(obj_o.to_string())
print("\nRerun:")
print(obj_r.to_string())

# ── 2. Solve Info ──
print("\n" + "=" * 80)
print("2. SOLVE INFO")
print("=" * 80)
si_o = load(orig, 'Solve_info.csv')
si_r = load(rerun, 'Solve_info.csv')
print("Original:")
print(si_o.to_string())
print("\nRerun:")
print(si_r.to_string())

# ── 3. Resources ──
print("\n" + "=" * 80)
print("3. RESOURCES COMPARISON")
print("=" * 80)
res_o = load(orig, 'Resources.csv')
res_r = load(rerun, 'Resources.csv')

# Standardize column names
res_o.rename(columns={res_o.columns[0]: 'Resource'}, inplace=True)
res_r.rename(columns={res_r.columns[0]: 'Resource'}, inplace=True)

# Merge
merged = res_o.merge(res_r, on='Resource', suffixes=('_orig', '_rerun'), how='outer')

# Focus on main consumption columns
for col_base in ['R_year_local', 'R_year_exterior']:
    c_o = col_base + '_orig'
    c_r = col_base + '_rerun'
    if c_o in merged.columns and c_r in merged.columns:
        merged[col_base + '_diff'] = merged[c_r].fillna(0) - merged[c_o].fillna(0)

# Print key resources
key_res = ['WOOD', 'WET_BIOMASS', 'ENERGY_CROPS_2', 'BIOMASS_RESIDUES', 'BIOWASTE', 'WASTE',
           'GAS', 'COAL', 'URANIUM', 'LFO', 'DIESEL', 'GASOLINE', 'JET_FUEL', 
           'ELECTRICITY', 'RES_HYDRO', 'RES_WIND', 'RES_SOLAR',
           'H2', 'AMMONIA', 'METHANOL', 'CO2_EMISSIONS']

print("{:<24} {:>12} {:>12} {:>12}".format('Resource', 'Original', 'Rerun', 'Diff'))
print("-" * 64)
for res in key_res:
    row_o = res_o[res_o['Resource'] == res]
    row_r = res_r[res_r['Resource'] == res]
    
    # Sum local + exterior for total
    def get_total(row):
        total = 0
        for c in ['R_year_local', 'R_year_exterior', 'R_year_import']:
            if c in row.columns and len(row) > 0:
                v = row[c].values[0]
                if pd.notna(v):
                    total += v
        return total
    
    t_o = get_total(row_o) if len(row_o) > 0 else 0
    t_r = get_total(row_r) if len(row_r) > 0 else 0
    d = t_r - t_o
    
    print("{:<24} {:>12.1f} {:>12.1f} {:>12.1f}".format(res, t_o, t_r, d))

# ── 4. Assets ──
print("\n" + "=" * 80)
print("4. KEY ASSETS (installed capacity GW)")
print("=" * 80)
ass_o = load(orig, 'Assets.csv')
ass_r = load(rerun, 'Assets.csv')
ass_o.rename(columns={ass_o.columns[0]: 'Tech'}, inplace=True)
ass_r.rename(columns={ass_r.columns[0]: 'Tech'}, inplace=True)

key_techs = ['NUCLEAR', 'CCGT', 'CCGT_AMMONIA', 'COAL_US', 'COAL_IGCC',
             'WIND_ONSHORE', 'WIND_OFFSHORE', 'HYDRO_DAM', 'HYDRO_RIVER',
             'PV_ROOFTOP', 'PV_UTILITY', 'GEOTHERMAL',
             'DHN_COGEN_WOOD', 'DHN_COGEN_GAS', 'DHN_COGEN_COAL',
             'IND_BOILER_WOOD', 'IND_BOILER_COAL', 'IND_BOILER_GAS', 'IND_BOILER_OIL',
             'IND_COGEN_WOOD',
             'DEC_DIRECT_ELEC', 'DEC_HP_ELEC', 'DEC_BOILER_GAS', 'DEC_BOILER_OIL',
             'CAR_GASOLINE', 'CAR_DIESEL', 'CAR_BEV', 'CAR_HEV', 'CAR_PHEV',
             'TRUCK_DIESEL',
             'H2_ELECTROLYSIS', 'SMR', 'SYN_METHANOLATION', 'HABER_BOSCH']

# Find capacity column
cap_col_o = 'F' if 'F' in ass_o.columns else ass_o.columns[1]
cap_col_r = 'F' if 'F' in ass_r.columns else ass_r.columns[1]

print("{:<30} {:>12} {:>12} {:>10}".format('Technology', 'Orig (GW)', 'Rerun (GW)', 'Ratio'))
print("-" * 68)
for tech in key_techs:
    v_o = ass_o.loc[ass_o['Tech'] == tech, cap_col_o].values
    v_r = ass_r.loc[ass_r['Tech'] == tech, cap_col_r].values
    fo = v_o[0] if len(v_o) > 0 else 0
    fr = v_r[0] if len(v_r) > 0 else 0
    ratio = fr / fo if fo > 1e-6 else ('inf' if fr > 1e-6 else '-')
    if isinstance(ratio, float):
        print("{:<30} {:>12.4f} {:>12.4f} {:>10.3f}".format(tech, fo, fr, ratio))
    else:
        print("{:<30} {:>12.4f} {:>12.4f} {:>10}".format(tech, fo, fr, ratio))

# ── 5. Year Balance (Electricity) ──
print("\n" + "=" * 80)
print("5. ELECTRICITY GENERATION (TWh)")
print("=" * 80)
yb_o = load(orig, 'Year_balance.csv')
yb_r = load(rerun, 'Year_balance.csv')
yb_o.rename(columns={yb_o.columns[0]: 'Tech'}, inplace=True)
yb_r.rename(columns={yb_r.columns[0]: 'Tech'}, inplace=True)

elec_techs = ['NUCLEAR', 'CCGT', 'CCGT_AMMONIA', 'COAL_US', 'COAL_IGCC',
              'WIND_ONSHORE', 'WIND_OFFSHORE', 'HYDRO_DAM', 'HYDRO_RIVER',
              'PV_ROOFTOP', 'PV_UTILITY',
              'IND_COGEN_WOOD', 'DHN_COGEN_WOOD', 'DHN_COGEN_GAS', 'DHN_COGEN_COAL',
              'IND_COGEN_GAS']

elec_col = 'ELECTRICITY'
if elec_col in yb_o.columns:
    print("{:<30} {:>15} {:>15} {:>12}".format('Tech', 'Orig (GWh)', 'Rerun (GWh)', 'Diff'))
    print("-" * 75)
    total_o = 0
    total_r = 0
    for tech in elec_techs:
        v_o = yb_o.loc[yb_o['Tech'] == tech, elec_col].values
        v_r = yb_r.loc[yb_r['Tech'] == tech, elec_col].values
        eo = v_o[0] if len(v_o) > 0 and pd.notna(v_o[0]) and v_o[0] > 0 else 0
        er = v_r[0] if len(v_r) > 0 and pd.notna(v_r[0]) and v_r[0] > 0 else 0
        if eo > 0 or er > 0:
            print("{:<30} {:>15.1f} {:>15.1f} {:>12.1f}".format(tech, eo, er, er - eo))
            total_o += eo
            total_r += er
    print("-" * 75)
    print("{:<30} {:>15.1f} {:>15.1f} {:>12.1f}".format('TOTAL', total_o, total_r, total_r - total_o))

# ── 6. CO2 ──
print("\n" + "=" * 80)
print("6. CO2 EMISSIONS")
print("=" * 80)
gwp_o = load(orig, 'Gwp_breakdown.csv')
gwp_r = load(rerun, 'Gwp_breakdown.csv')
print("Original GWP breakdown:")
print(gwp_o.to_string() if not gwp_o.empty else "Not available")
print("\nRerun GWP breakdown:")
print(gwp_r.to_string() if not gwp_r.empty else "Not available")

# ── 7. Total Cost ──
print("\n" + "=" * 80)
print("7. TOTAL COST")
print("=" * 80)
tc_o = load(orig, 'TotalCost.csv')
tc_r = load(rerun, 'TotalCost.csv')
print("Original:")
print(tc_o.to_string() if not tc_o.empty else "Not available")
print("\nRerun:")
print(tc_r.to_string() if not tc_r.empty else "Not available")

print("\n" + "=" * 80)
print("COMPARISON COMPLETE")
print("=" * 80)
