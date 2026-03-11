"""Quick comparison of REF_REGION Technologies between 2017 and 2035."""
import csv

def load(p):
    with open(p) as f:
        r = csv.DictReader(f)
        return {row['Technologies param']: row for row in r}

t17 = load('Data/2017/02_REF_REGION/Technologies.csv')
t35 = load('Data/2035/02_REF_REGION/Technologies.csv')
cols = ['c_inv', 'c_maint', 'gwp_constr', 'lifetime', 'c_p']
diffs = []
for name in sorted(t17):
    if name in t35:
        changed = []
        for c in cols:
            v17, v35 = t17[name].get(c, ''), t35[name].get(c, '')
            if v17 != v35:
                changed.append(f'{c}:{v17}->{v35}')
        if changed:
            diffs.append(f'{name}: {" | ".join(changed)}')

print(f'Techs with different params: {len(diffs)}')
for d in diffs:
    print(d)

only17 = set(t17) - set(t35)
only35 = set(t35) - set(t17)
if only17:
    print(f'\nOnly in 2017: {", ".join(sorted(only17))}')
if only35:
    print(f'\nOnly in 2035: {", ".join(sorted(only35))}')
