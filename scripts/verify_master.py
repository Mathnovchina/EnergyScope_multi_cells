import pandas as pd

xls = pd.ExcelFile('Data/exogenous_data/Finland_MASTER_Calibration.xlsx')
print('\nMASTER FILE VERIFICATION')
print('='*80)
print(f'Location: Data/exogenous_data/Finland_MASTER_Calibration.xlsx')
print(f'Total Sheets: {len(xls.sheet_names)}')
print(f'\nSheet Names:')
for i, sheet in enumerate(xls.sheet_names, 1):
    df = pd.read_excel(xls, sheet)
    print(f'  {i}. {sheet}: {df.shape[0]} rows × {df.shape[1]} columns')

print('\n' + '='*80)
print('Sample from Master Log:')
print('='*80)
df_log = pd.read_excel(xls, '1_Master_Log')
print(df_log[['Category', 'Parameter', 'Source/Methodology']].head(10).to_string(index=False))
