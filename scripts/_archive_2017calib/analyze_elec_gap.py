"""Analyze electricity demand gap between model and Finnish reality."""
import pandas as pd

run = 'case_studies/FI/manual_runs/20260317_121151__v26_gas_rebalance'
yb = pd.read_csv(f'{run}/outputs/Year_balance.csv', index_col=0)

end_uses_elec = -yb.loc['END_USES','ELECTRICITY'] / 1000
dec_hp = -yb.loc['DEC_HP_ELEC','ELECTRICITY'] / 1000
dhn_hp = -yb.loc['DHN_HP_ELEC','ELECTRICITY'] / 1000
ind_cool = -yb.loc['IND_ELEC_COLD','ELECTRICITY'] / 1000
dec_cool = -yb.loc['DEC_ELEC_COLD','ELECTRICITY'] / 1000
trains = (-yb.loc['TRAIN_FREIGHT','ELECTRICITY'] - yb.loc['TRAIN_PUB','ELECTRICITY'] - yb.loc['TRAMWAY_TROLLEY','ELECTRICITY']) / 1000
cars = (-yb.loc['CAR_BEV','ELECTRICITY'] - yb.loc['CAR_PHEV','ELECTRICITY']) / 1000
other = (-yb.loc['OIL_TO_HVC','ELECTRICITY'] - yb.loc['BEV_BATT','ELECTRICITY'] - yb.loc['DEC_DIRECT_ELEC','ELECTRICITY'] - yb.loc['IND_DIRECT_ELEC','ELECTRICITY'] - yb.loc['HABER_BOSCH','ELECTRICITY'] - yb.loc['CAES','ELECTRICITY']) / 1000

total_cons = end_uses_elec + dec_hp + dhn_hp + ind_cool + dec_cool + trains + cars + other

print("=== v26 Electricity Consumption Breakdown (TWh) ===")
print(f"END_USES (direct demand):    {end_uses_elec:.2f}")
print(f"DEC_HP_ELEC (dec heat pump): {dec_hp:.2f}")
print(f"DHN_HP_ELEC (dhn heat pump): {dhn_hp:.2f}")
print(f"IND_ELEC_COLD:               {ind_cool:.2f}")
print(f"DEC_ELEC_COLD:               {dec_cool:.2f}")
print(f"Trains + trams:              {trains:.2f}")
print(f"BEV + PHEV cars:             {cars:.2f}")
print(f"Other (OIL_TO_HVC, storage): {other:.2f}")
print(f"TOTAL consumption:           {total_cons:.2f}")
print()

# Grid loss analysis
demands_elec = 43.007
print(f"Demands.csv ELECTRICITY input: {demands_elec:.3f} TWh")
print(f"END_USES in Year_balance:      {end_uses_elec:.3f} TWh")
print(f"Ratio (END_USES/input):        {end_uses_elec/demands_elec:.4f}")
print(f"Implied grid loss:             {(end_uses_elec - demands_elec) / end_uses_elec * 100:.1f}%")
print()

# Read reg_misc.dat to check loss factor
import os
misc_path = 'Data/2017/FI/reg_misc.dat'
if os.path.exists(misc_path):
    with open(misc_path) as f:
        for line in f:
            if 'loss' in line.lower() or 'elec' in line.lower():
                print(f"  reg_misc: {line.strip()}")

# Also check INDEP misc
misc_indep = 'Data/2017/INDEP/indep_misc.dat'
if os.path.exists(misc_indep):
    print(f"\n=== INDEP misc (loss-related lines) ===")
    with open(misc_indep) as f:
        for line in f:
            if 'loss' in line.lower() or 'grid' in line.lower():
                print(f"  {line.strip()}")

print()
print("=== Finnish 2017 Reality (Statistics Finland) ===")
print("Total final elec consumption: ~85.5 TWh")
print("  Of which:")
print("    Industry (incl CHP own use & elec motors): ~47-48 TWh")
print("    Services + public:                         ~12 TWh")
print("    Households:                                ~10 TWh")
print("    Transport (trains, trams):                 ~1 TWh")
print("    Losses + grid services:                    ~3 TWh")
print("    Other (construction, agric):               ~2 TWh")
print()
print(f"Model total electricity throughput:  {total_cons:.2f} TWh")
print(f"Finnish reality:                     ~85.5 TWh")
print(f"Gap:                                 ~{85.5 - total_cons:.1f} TWh")
print()
print("=== Key insight: Where is the gap? ===")
print(f"Model IND electricity (from Demands.csv): 23.4 TWh")
print(f"Finland IND elec reality (stat.fi):       ~38-40 TWh")
print(f"  -> IND electricity gap: ~15-17 TWh")
print()
print("The model ELECTRICITY demand counts only 'specific electricity'")
print("(lighting, motors, electronics). In Finland, a large portion of")
print("industrial electricity goes to electric arc furnaces, electrolysis,")
print("and electric process heating that may be counted under HEAT_HIGH_T")
print("or NON_ENERGY in the model, but are real electricity consumption.")
print()
print("Additionally, the model's electric heat pumps consume ~19 TWh of")
print("electricity for heating - but in Finnish reality, electric heating")
print("is ~6-7 TWh (resistive + HP), not 19 TWh. The DHN share constraint")
print("forces DHN_HP_ELEC to consume ~3.7 TWh, and DEC_HP_ELEC consumes")
print("~15.4 TWh - both much higher than Finnish reality.")
