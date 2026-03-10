"""Layer dependency analysis for Finland 2017 technology disabling.
For each layer, identify which technologies produce (output > 0) or consume it.
Flag technologies that are sole/rare producers of important layers."""
import pandas as pd
import numpy as np

lio = pd.read_csv('Data/2017/00_INDEP/Layers_in_out.csv', index_col=0)

# Strip whitespace from column names and index
lio.columns = lio.columns.str.strip()
lio.index = lio.index.str.strip()

# Separate resource rows (first ~34) from technology rows
# Resources are rows that match layer names or have _RE suffix
resource_names = set(lio.columns)
# Add known resource variants
for c in list(resource_names):
    resource_names.add(c + '_RE')
resource_names.update(['ENERGY_CROPS_2', 'BIOMASS_RESIDUES', 'CO2_ATM', 'CO2_INDUSTRY', 'CO2_CAPTURED', 'PT_HEAT', 'ST_HEAT'])

tech_rows = [r for r in lio.index if r not in resource_names]

# Also read Technologies.csv for f_min/f_max context
tech_csv = pd.read_csv('Data/2017/02_REF_REGION/Technologies.csv', skiprows=[1])
tech_csv.columns = tech_csv.columns.str.strip()
tech_csv = tech_csv.set_index('Technologies param')

fi_csv = pd.read_csv('Data/2017/FI/Technologies.csv', skiprows=[1])
fi_csv.columns = fi_csv.columns.str.strip()
fi_csv = fi_csv.set_index('Technologies param')

# For each important layer, list producers
important_layers = ['H2', 'AMMONIA', 'METHANOL', 'HVC', 'HEAT_HIGH_T', 
                    'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN', 'ELECTRICITY',
                    'MOB_PUBLIC', 'MOB_PRIVATE', 'AVIATION_SHORT_HAUL', 
                    'AVIATION_LONG_HAUL', 'MOB_FREIGHT_RAIL', 'MOB_FREIGHT_ROAD',
                    'MOB_FREIGHT_BOAT', 'SHIPPING', 'GASOLINE', 'DIESEL',
                    'LFO', 'JET_FUEL', 'GAS', 'SPACE_COOLING', 'PROCESS_COOLING']

print("=" * 90)
print("LAYER DEPENDENCY ANALYSIS — producers (positive output) among technologies")
print("=" * 90)

for layer in important_layers:
    if layer not in lio.columns:
        continue
    col = lio[layer]
    producers = []
    for t in tech_rows:
        val = col.get(t, 0)
        if isinstance(val, (int, float)) and val > 0:
            producers.append((t, val))
    
    if producers:
        print(f"\n--- {layer} ({len(producers)} producers) ---")
        for t, v in sorted(producers, key=lambda x: -x[1]):
            # Check if already banned (f_max=0 in FI)
            fi_fmax = ""
            if t in fi_csv.index and 'f_max' in fi_csv.columns:
                fm = fi_csv.loc[t, 'f_max']
                if pd.notna(fm) and float(fm) == 0:
                    fi_fmax = " [FI:f_max=0]"
            print(f"  {t:40s} output={v:>8.4f}{fi_fmax}")

# Now list candidate disable technologies and check their layer connections
print("\n" + "=" * 90)
print("CANDIDATE TECHNOLOGIES FOR DISABLING — layer check")
print("=" * 90)

candidates = [
    'NUCLEAR_SMR', 'TIDAL_STREAM', 'TIDAL_RANGE', 'WAVE', 'GEOTHERMAL',
    'PT_POWER_BLOCK', 'ST_POWER_BLOCK', 'PT_COLLECTOR', 'ST_COLLECTOR',
    'DHN_DEEP_GEO',
    'PLANE_H2_SHORT_HAUL',
    'BUS_COACH_FC_HYBRIDH2', 'CAR_FUEL_CELL', 'CAR_METHANOL',
    'TRUCK_FUEL_CELL', 'TRUCK_METHANOL',
    'CARGO_FUELCELL_LH2', 'CARGO_FUELCELL_AMMONIA',
    'CARGO_RETRO_METHANOL', 'CARGO_RETRO_AMMONIA',
    'CARGO_METHANOL', 'CARGO_AMMONIA', 'CARGO_LNG',
    'BOAT_FREIGHT_METHANOL', 'BOAT_FREIGHT_NG',
    'H2_TO_GASOLINE', 'H2_TO_DIESEL', 'H2_TO_JET_FUEL', 'H2_TO_LFO',
    'POWER_TO_GASOLINE', 'POWER_TO_DIESEL', 'POWER_TO_JET_FUEL', 'POWER_TO_LFO',
    'BIOMASS_TO_GASOLINE', 'BIOMASS_TO_DIESEL', 'BIOMASS_TO_JET_FUEL', 'BIOMASS_TO_LFO',
    'BIOWASTE_TO_GASOLINE', 'BIOWASTE_TO_DIESEL', 'BIOWASTE_TO_JET_FUEL', 'BIOWASTE_TO_LFO',
    'CCGT_AMMONIA', 'COAL_IGCC',
    'DEC_ADVCOGEN_H2', 'DEC_ADVCOGEN_GAS',
    'SYN_METHANATION', 'SYN_METHANOLATION',
    'HABER_BOSCH', 'AMMONIA_TO_H2',
    'H2_ELECTROLYSIS', 'H2_NG', 'H2_BIOMASS',
    'METHANOL_TO_HVC', 'OIL_TO_HVC', 'GAS_TO_HVC', 'BIOMASS_TO_HVC',
    'METHANE_TO_METHANOL', 'BIOMASS_TO_METHANOL', 'BIOWASTE_TO_METHANOL',
    'BIOMASS_TO_METHANE', 'BIOWASTE_TO_METHANE',
    'BIOMETHANATION_WET_BIOMASS', 'BIOMETHANATION_BIOWASTE',
    'ATM_CCS', 'INDUSTRY_CCS',
    'DIESEL_TO_JET_FUEL',
    'BUS_COACH_HYDIESEL',
    'HVAC_LINE', 'HVDC_SUBSEA', 'GAS_SUBSEA', 'H2_RETROFITTED', 'H2_NEW',
    'H2_SUBSEA_RETRO', 'H2_SUBSEA_NEW',
]

for t in candidates:
    if t not in lio.index:
        print(f"  {t:40s} NOT IN Layers_in_out")
        continue
    row = lio.loc[t]
    consumes = [(c, v) for c, v in row.items() if isinstance(v, (int, float)) and v < 0]
    produces = [(c, v) for c, v in row.items() if isinstance(v, (int, float)) and v > 0]
    
    cons_str = ", ".join(f"{c}({v:.3f})" for c, v in consumes) if consumes else "none"
    prod_str = ", ".join(f"{c}({v:.3f})" for c, v in produces) if produces else "none"
    
    # Check if this tech is sole producer of any layer
    sole_producer_of = []
    for c, v in produces:
        if c in lio.columns:
            other_producers = [r for r in tech_rows if r != t and 
                             isinstance(lio.loc[r, c], (int, float)) and lio.loc[r, c] > 0]
            if len(other_producers) == 0:
                sole_producer_of.append(c)
    
    sole_str = f" *** SOLE PRODUCER OF: {sole_producer_of}" if sole_producer_of else ""
    print(f"  {t:40s} consumes=[{cons_str}] produces=[{prod_str}]{sole_str}")
