"""Check f_min/f_max values in .dat file for key technologies."""
import sys

dat = "case_studies/FI/manual_runs/20260310_095416__stageA_verify/input_snapshot/reg_technologies.dat"
techs = ["NUCLEAR","WIND_ONSHORE","HYDRO_DAM","HYDRO_RIVER","COAL_US","CCGT","DHN_COGEN_GAS",
         "NUCLEAR_SMR","H2_TO_GASOLINE","CCGT_AMMONIA","COAL_IGCC"]

with open(dat) as f:
    lines = f.readlines()

# Header
cols = lines[0].split()
print(f"Columns: {cols}")
print()

# col indices: region=0, tech=1, c_inv=2, c_maint=3, gwp=4, lifetime=5, c_p=6, fmin_perc=7, fmax_perc=8, f_min=9, f_max=10
for tech in techs:
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 11 and parts[0] == "FI" and parts[1] == tech:
            print(f"  {tech:25s}  f_min={parts[9]:>10s}  f_max={parts[10]:>10s}  fmin_perc={parts[7]:>5s}  fmax_perc={parts[8]:>5s}")
            break
    else:
        print(f"  {tech:25s}  NOT IN DAT")
