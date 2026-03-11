"""Parse c_p_t time series for WIND from the Block 2 TD .dat file."""
import re

content = open('case_studies/FI/manual_runs/20260310_142104__block2_wind_from_block1/reg_12TD.dat').read()
idx = content.find('param  c_p_t:=')
section = content[idx:]

# Find WIND_ONSHORE and WIND_OFFSHORE blocks
for tech in ['WIND_ONSHORE', 'WIND_OFFSHORE']:
    marker = '["' + tech + '","FI"'
    start = section.find(marker)
    if start < 0:
        print(f"=== {tech}: NOT FOUND ===")
        continue
    # Find end (next [ or ;)
    end = section.find('\n[', start + 1)
    if end < 0:
        end = section.find(';', start)
    block = section[start:end]
    
    print(f"=== {tech} ===")
    # Extract all floats (c_p_t values are fractional, skip integer row labels)
    numbers = re.findall(r'[\d]+\.[\d]+(?:e[+-]?\d+)?', block)
    float_vals = [float(v) for v in numbers]
    
    # Also find the integer row labels (hours 1-24)
    lines = block.split('\n')
    for l in lines[:4]:
        print(f"  {l[:120]}")
    
    if float_vals:
        print(f"  Values: {len(float_vals)}")
        print(f"  Mean c_p_t: {sum(float_vals)/len(float_vals):.4f}")
        print(f"  Min:  {min(float_vals):.4f}")
        print(f"  Max:  {max(float_vals):.4f}")
    print()

# Also check: what is the annual c_p used in formulation?
# c_p from .dat is 1.0 for both onshore and offshore
# The actual capacity factor comes from c_p_t time series weighted by typical days
print("=== KEY OBSERVATION ===")
print("c_p in reg_technologies.dat = 1.0 for both WIND_ONSHORE and WIND_OFFSHORE")
print("This means the rated capacity equals the nameplate GW value.")
print("The actual hourly output fraction is determined by c_p_t time series.")
print("The model computes: F_t[tech,h] <= F[tech] * c_p * c_p_t[tech,h]")
print("So with c_p=1.0, the constraint is: F_t[tech,h] <= F[tech] * c_p_t[tech,h]")

# Check typical day weights
content2 = open('case_studies/FI/manual_runs/20260310_142104__block2_wind_from_block1/reg_12TD.dat').read()
td_idx = content2.find('param td_count')
if td_idx >= 0:
    td_section = content2[td_idx:td_idx+500]
    print("\n=== TYPICAL DAY COUNTS ===")
    print(td_section[:400])
