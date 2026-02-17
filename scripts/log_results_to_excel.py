import pandas as pd
import datetime
import os

# Define the constraints used in the latest run (Methodical Calibration)
res_constraints = {
    'GAS':      {'avail_local': 0.0, 'avail_exterior': 28000.0,  'c_op_local': 0.02},
    'GAS_RE':   {'avail_local': 0.0, 'avail_exterior': 0.0,      'c_op_local': 0.02},
    'OIL':      {'avail_local': 0.0, 'avail_exterior': 120000.0, 'c_op_local': 0.05},
    'GASOLINE':    {'avail_local': 0.0, 'avail_exterior': 15000.0,  'c_op_local': 0.06},
    'GASOLINE_RE': {'avail_local': 0.0, 'avail_exterior': 0.0,      'c_op_local': 0.06},
    'DIESEL':      {'avail_local': 0.0, 'avail_exterior': 25000.0,  'c_op_local': 0.05},
    'DIESEL_RE':   {'avail_local': 0.0, 'avail_exterior': 0.0,      'c_op_local': 0.05},
    'LFO':         {'avail_local': 0.0, 'avail_exterior': 150000.0, 'c_op_local': 0.05},
    'LFO_RE':      {'avail_local': 0.0, 'avail_exterior': 0.0,      'c_op_local': 0.05},
    'JET_FUEL':    {'avail_local': 0.0, 'avail_exterior': 15000.0,  'c_op_local': 0.05},
    'JET_FUEL_RE': {'avail_local': 0.0, 'avail_exterior': 0.0,      'c_op_local': 0.05},
    'COAL':     {'avail_local': 0.0, 'avail_exterior': 50000.0,  'c_op_local': 0.015},
    'URANIUM':  {'avail_local': 0.0, 'avail_exterior': 100000.0, 'c_op_local': 0.005},
    'ELECTRICITY': {'avail_local': 0.0, 'avail_exterior': 25000.0, 'c_op_local': 0.05}
}

tech_constraints = {
    'CAR_BEV': {'f_max': 0.02},
    'CAR_PHEV': {'f_max': 0.02},
    'WIND_ONSHORE': {'f_max': 2.1},  
    'WIND_OFFSHORE': {'f_max': 0.1}, 
    'PV': {'f_max': 0.1},
    'CCGT_AMMONIA': {'f_max': 0},
    'COAL_IGCC': {'f_max': 0},
    'SMR': {'f_max': 0}, 
    'NUCLEAR_SMR': {'f_max': 0},
    'IND_BOILER_WOOD': {'f_max': 500.0}, 
    'DHN_BOILER_WOOD': {'f_max': 500.0},
    'IND_BOILER_GAS': {'f_max': 500.0},
    'DHN_BOILER_GAS': {'f_max': 500.0},
    'IND_BOILER_OIL': {'f_max': 500.0},
    'DHN_BOILER_OIL': {'f_max': 500.0},
    'IND_BOILER_COAL': {'f_max': 500.0},
    'DHN_BOILER_COAL': {'f_max': 500.0},
}

data = []
for res, limits in res_constraints.items():
    row = {'Category': 'Resource', 'Name': res}
    row.update(limits)
    data.append(row)

for tech, limits in tech_constraints.items():
    row = {'Category': 'Technology', 'Name': tech}
    row.update(limits)
    data.append(row)

df_log = pd.DataFrame(data)
df_log['Date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
df_log['Description'] = "Methodical 2017 Calibration Constraints"

file_path = os.path.join('Data', 'exogenous_data', 'Finland_MASTER_Calibration.xlsx')

print(f"Adding log to {file_path}...")

# Append to Excel
try:
    # Use 'a' mode to append to existing workbook
    # if_sheet_exists='replace' will overwrite the specific sheet if it exists
    with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_log.to_excel(writer, sheet_name='Run_Feb14_Methodical', index=False)
    print("Successfully logged parameters to sheet 'Run_Feb14_Methodical'.")
except Exception as e:
    print(f"Error writing to Excel: {e}")
