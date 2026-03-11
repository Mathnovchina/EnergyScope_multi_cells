"""Quick diff: v9 frozen .dat vs current Technologies.csv"""
import pandas as pd

# v9 frozen .dat
v9 = {}
for line in open('case_studies/FI/calib_2017_finland_v9/reg_technologies.dat'):
    parts = line.strip().split('\t')
    if len(parts) >= 10 and parts[0] == 'FI':
        tech = parts[1]
        v9[tech] = dict(fmin_perc=parts[6], fmax_perc=parts[7],
                        f_min=parts[8], f_max=parts[9].rstrip(' ;'))

# Current
cur = pd.read_csv('Data/2017/FI/Technologies.csv', index_col='Technologies param')
cur.index = cur.index.str.strip()

def to_f(s):
    s = str(s).strip()
    if s == 'Infinity': return float('inf')
    return float(s)

header = "{:<25s} {:>12s} {:>12s} {:>12s} {:>12s} {:>12s} {:>12s} {:>12s} {:>12s}".format(
    "TECH", "v9_fmin", "NOW_fmin", "v9_fmax", "NOW_fmax",
    "v9_fminp", "NOW_fminp", "v9_fmaxp", "NOW_fmaxp")
print(header)
print("-" * len(header))

diffs = 0
for tech in sorted(v9.keys()):
    if tech not in cur.index:
        continue
    v = v9[tech]
    c = cur.loc[tech]
    changed = False
    for k in ['f_min','f_max','fmin_perc','fmax_perc']:
        vf = to_f(v[k])
        cf = to_f(c[k])
        if abs(vf - cf) > 0.001 and not (vf == float('inf') and cf == float('inf')):
            changed = True
    if changed:
        diffs += 1
        vfmin, vfmax = v['f_min'], v['f_max']
        vfminp, vfmaxp = v['fmin_perc'], v['fmax_perc']
        cfmin = "{:.2f}".format(c['f_min'])
        cfmax = "{:.2f}".format(c['f_max']) if c['f_max'] < 1e10 else "Inf"
        cfminp = "{:.2f}".format(c['fmin_perc'])
        cfmaxp = "{:.2f}".format(c['fmax_perc'])
        print("{:<25s} {:>12s} {:>12s} {:>12s} {:>12s} {:>12s} {:>12s} {:>12s} {:>12s}".format(
            tech, vfmin, cfmin, vfmax, cfmax, vfminp, cfminp, vfmaxp, cfmaxp))

print("\nTotal techs with parameter differences: {}".format(diffs))
