"""Quick analysis script for comparing block outputs."""
import sys
import pandas as pd

def analyze(block_dir, prev_dir=None):
    out = f'case_studies/FI/{block_dir}/outputs'
    
    # Resources
    r = pd.read_csv(f'{out}/Resources.csv')
    print(f'=== RESOURCES ({block_dir}) ===')
    key_res = ['WOOD','GAS','COAL','URANIUM','LFO','DIESEL','GASOLINE','JET_FUEL',
               'ELECTRICITY','WASTE','ENERGY_CROPS_2','BIOWASTE','BIOMASS_RESIDUES','WET_BIOMASS']
    for _, row in r.iterrows():
        name = row['Resources']
        loc = row['R_year_local']
        ext = row['R_year_exterior']
        total = loc + ext
        if total > 1 and name in key_res:
            print(f"  {name:20s}  local={loc:10.0f}  ext={ext:10.0f}  total={total:10.0f}")
    
    # Objective
    obj = pd.read_csv(f'{out}/Objective.csv')
    print(f"\nObjective: {obj.iloc[0,1]:.2e}")
    
    # Assets violations
    a = pd.read_csv(f'{out}/Assets.csv')
    v = a[a['F'] > a['f_max'] + 0.001].copy()
    v['excess'] = v['F'] - v['f_max']
    v['pct'] = (v['excess'] / v['f_max'] * 100).round(1)
    print(f'\nF>f_max violations ({len(v)}):')
    for _, row in v.iterrows():
        print(f"  {row['Technologies']:25s}  F={row['F']:10.3f}  f_max={row['f_max']:10.3f}  excess={row['excess']:8.3f} ({row['pct']}%)")
    
    # Top 15 deployments
    print('\nTop 15 deployments:')
    for _, row in a.nlargest(15,'F').iterrows():
        print(f"  {row['Technologies']:25s}  F={row['F']:12.1f}  f_max={row['f_max']:12.1f}")
    
    # Compare with previous block
    if prev_dir:
        prev_out = f'case_studies/FI/{prev_dir}/outputs'
        r_prev = pd.read_csv(f'{prev_out}/Resources.csv')
        obj_prev = pd.read_csv(f'{prev_out}/Objective.csv')
        
        m = r_prev[['Resources','R_year_local','R_year_exterior']].merge(
            r[['Resources','R_year_local','R_year_exterior']], on='Resources', suffixes=('_prev','_cur'))
        m['diff_loc'] = m['R_year_local_cur'] - m['R_year_local_prev']
        m['diff_ext'] = m['R_year_exterior_cur'] - m['R_year_exterior_prev']
        sig = m[(m['diff_loc'].abs()>100)|(m['diff_ext'].abs()>100)]
        
        print(f'\n=== SIGNIFICANT RESOURCE CHANGES vs {prev_dir} ===')
        for _, row in sig.iterrows():
            print(f"  {row['Resources']:20s}  local: {row['R_year_local_prev']:10.0f} -> {row['R_year_local_cur']:10.0f} ({row['diff_loc']:+.0f})  ext: {row['R_year_exterior_prev']:10.0f} -> {row['R_year_exterior_cur']:10.0f} ({row['diff_ext']:+.0f})")
        
        print(f"\nObjective change: {obj_prev.iloc[0,1]:.2e} -> {obj.iloc[0,1]:.2e}")


if __name__ == '__main__':
    block_dir = sys.argv[1]
    prev_dir = sys.argv[2] if len(sys.argv) > 2 else None
    analyze(block_dir, prev_dir)
