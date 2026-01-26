import pandas as pd

xls = pd.ExcelFile('Data/exogenous_data/Finland_MASTER_Calibration.xlsx')
print('\nFINAL MASTER FILE VERIFICATION')
print('='*80)
print(f'Location: Data/exogenous_data/Finland_MASTER_Calibration.xlsx')
print(f'Total Sheets: {len(xls.sheet_names)}')
print(f'\nSheet Names:')
for i, sheet in enumerate(xls.sheet_names, 1):
    df = pd.read_excel(xls, sheet)
    print(f'  {i}. {sheet}: {df.shape[0]} rows × {df.shape[1]} columns')

print('\n' + '='*80)
print('Data Flow Overview (First 3 stages):')
print('='*80)
df_flow = pd.read_excel(xls, '0_Data_Flow_Overview')
print(df_flow[['Stage', 'Description']].head(3).to_string(index=False))

print('\n' + '='*80)
print('Sample from Data Traceability (First 5 entries):')
print('='*80)
df_trace = pd.read_excel(xls, '1_Data_Traceability')
print(df_trace[['Data_Category', 'Specific_Parameter', 'Year_Applied', 'Model_Location']].head(5).to_string(index=False))
