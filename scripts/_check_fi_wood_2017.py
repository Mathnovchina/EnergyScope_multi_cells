import pandas as pd

# 2017 wood resources
r17 = pd.read_csv('Data/2017/02_REF_REGION/Resources.csv', index_col=0)
rows = [idx for idx in r17.index if any(x in str(idx) for x in ['WOOD','BIOMASS','BIOWASTE','WASTE'])]
print('2017 FI wood/biomass avail_local (GWh):')
total_wood = 0.0
for r in rows:
    v = float(r17.loc[r, 'avail_local'])
    print(f'  {r:<30s} {v:>10.1f}')
    if 'WOOD' in r or 'BIOMASS' in r or 'BIOWASTE' in r:
        total_wood += v
print(f'  {"WOOD+BIOMASS+BIOWASTE total":<30s} {total_wood:>10.1f} GWh = {total_wood/1000:.1f} TWh')

print()
# Check calibration reality for any bioenergy/wood entries
ref = pd.read_csv('calibration/reality/finland_2017_reference.csv')
print('Columns:', ref.columns.tolist())
print()
# Print all rows where the first few columns mention wood/biomass
for i, row in ref.iterrows():
    s = ' '.join(str(v) for v in row.values).lower()
    if any(x in s for x in ['wood','biomass','bioenergy','biofuel','forest']):
        print(row.to_dict())
