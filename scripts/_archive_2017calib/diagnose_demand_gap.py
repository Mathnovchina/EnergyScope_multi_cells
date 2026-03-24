"""
Comprehensive demand gap diagnosis for Finland 2017 EnergyScope calibration.

Compares model internal electricity balance with Finnish reality,
identifies the structural sources of the ~14 TWh gap, and proposes fixes.
"""
import pandas as pd

run = 'case_studies/FI/manual_runs/20260317_121151__v26_gas_rebalance'
yb = pd.read_csv(f'{run}/outputs/Year_balance.csv', index_col=0)

print("=" * 70)
print("DIAGNOSIS: Why does the model use 71 TWh electricity vs Finland's ~85 TWh?")
print("=" * 70)

# 1. Model electricity balance
elec_col = yb['ELECTRICITY']
prod = elec_col[elec_col > 0]
cons = elec_col[elec_col < 0]

print("\n--- Model v26 Electricity Balance ---")
print(f"Total production:  {prod.sum()/1000:.2f} TWh")
print(f"Total consumption: {-cons.sum()/1000:.2f} TWh")

print("\nProduction breakdown (TWh):")
for tech, val in prod.sort_values(ascending=False).items():
    if val > 10:
        print(f"  {tech:40s}: {val/1000:8.3f}")

print("\nConsumption breakdown (TWh):")
for tech, val in cons.sort_values().items():
    print(f"  {tech:40s}: {-val/1000:8.3f}")

# 2. Key issue: END_USES includes grid losses
end_uses = -yb.loc['END_USES', 'ELECTRICITY'] / 1000
demands_elec = 43.007  # from Demands.csv total
grid_losses_elec = end_uses - demands_elec
loss_pct = grid_losses_elec / end_uses * 100

print(f"\n--- Grid Loss Analysis ---")
print(f"Demands.csv ELECTRICITY:        {demands_elec:.3f} TWh")
print(f"END_USES in Year_balance:        {end_uses:.3f} TWh")
print(f"Network losses (elec):           {grid_losses_elec:.3f} TWh")
print(f"Loss rate (on production):       {loss_pct:.1f}%")
print(f"Misc_indep.json loss_network:    8.64%")
print(f"Finland real grid loss:           ~3%")
print(f"Excess losses:                   {grid_losses_elec - demands_elec * 0.03 / (1 - 0.03):.2f} TWh")

# 3. DHN heat analysis
print(f"\n--- DHN Heat Issue ---")
heat_sh_total = 85635.5 / 1000  # TWh from Demands.csv
heat_hw_total = 20379.1 / 1000
heat_low_t = heat_sh_total + heat_hw_total
dhn_share = 0.45
dhn_demand = heat_low_t * dhn_share
dec_demand = heat_low_t * (1 - dhn_share)

# Industry contribution to DHN (the problem)
heat_sh_ind = 22111.9 / 1000
heat_hw_ind = 9130.4 / 1000
heat_low_t_ind = heat_sh_ind + heat_hw_ind
dhn_ind_phantom = heat_low_t_ind * dhn_share

print(f"Total HEAT_LOW_T (SH+HW):        {heat_low_t:.1f} TWh")
print(f"  HOUSEHOLDS:                    {(38557 + 6009)/1000:.1f} TWh")
print(f"  SERVICES:                      {(24967 + 5240)/1000:.1f} TWh")
print(f"  INDUSTRY:                      {heat_low_t_ind:.1f} TWh")
print(f"DHN share applied:               {dhn_share:.1%}")
print(f"Total DHN demand:                {dhn_demand:.1f} TWh")
print(f"  of which phantom Industry DHN: {dhn_ind_phantom:.1f} TWh")
print(f"Reality DHN production:          36.5 TWh")
print(f"Model DHN production (v26):      52.7 TWh")
print(f"DHN overshoot:                   {52.7 - 36.5:.1f} TWh (~= phantom industry)")

# 4. How DEC_HP_ELEC gets so large
dec_hp = -yb.loc['DEC_HP_ELEC', 'ELECTRICITY'] / 1000
print(f"\n--- DEC_HP_ELEC Analysis ---")
print(f"DEC_HP_ELEC electricity consumed: {dec_hp:.2f} TWh")
dec_heat_delivered = yb.loc['DEC_HP_ELEC', 'HEAT_LOW_T_DECEN'] / 1000 if 'HEAT_LOW_T_DECEN' in yb.columns else 0
print(f"DEC_HP_ELEC heat delivered:       {dec_heat_delivered:.2f} TWh")
if dec_hp > 0:
    cop_eff = dec_heat_delivered / dec_hp
    print(f"Effective COP:                    {cop_eff:.2f}")
print(f"In Finnish reality: electric heating ~7 TWh total (resistive + HP)")
print(f"Model overestimates by: {dec_hp - 7:.1f} TWh")

# 5. The full picture
print(f"\n{'=' * 70}")
print(f"FULL ACCOUNTING: Model vs Finnish Reality 2017")
print(f"{'=' * 70}")
print(f"                              Model    Reality    Gap")
print(f"End-use ELECTRICITY:          {demands_elec:6.1f}      43.0*    0   (JRC-IDEES)")
print(f"Grid losses (on ELEC):         {grid_losses_elec:6.1f}       1.3    +{grid_losses_elec-1.3:.1f} (8.64% vs 3%)")
print(f"DEC_HP_ELEC:                   {dec_hp:5.1f}       7.0   +{dec_hp-7:.1f} (model over-invests)")
dhn_hp = -yb.loc['DHN_HP_ELEC','ELECTRICITY']/1000
print(f"DHN_HP_ELEC:                    {dhn_hp:5.1f}       0.5   +{dhn_hp-0.5:.1f} (phantom IND DHN)")
ind_cool = -yb.loc['IND_ELEC_COLD','ELECTRICITY']/1000
dec_cool = -yb.loc['DEC_ELEC_COLD','ELECTRICITY']/1000
print(f"Cooling (IND+DEC):              {ind_cool+dec_cool:5.1f}       2.2   +{ind_cool+dec_cool-2.2:.1f}")
trains = (-yb.loc['TRAIN_FREIGHT','ELECTRICITY']-yb.loc['TRAIN_PUB','ELECTRICITY']-yb.loc['TRAMWAY_TROLLEY','ELECTRICITY'])/1000
print(f"Trains + trams:                 {trains:5.1f}       0.7    0    (close)")
cars = (-yb.loc['CAR_BEV','ELECTRICITY']-yb.loc['CAR_PHEV','ELECTRICITY'])/1000
print(f"BEV/PHEV:                       {cars:5.1f}       0.1    0    (close)")
other = (-yb.loc['OIL_TO_HVC','ELECTRICITY']-yb.loc['BEV_BATT','ELECTRICITY']-yb.loc['DEC_DIRECT_ELEC','ELECTRICITY']-yb.loc['IND_DIRECT_ELEC','ELECTRICITY']-yb.loc['HABER_BOSCH','ELECTRICITY']-yb.loc['CAES','ELECTRICITY'])/1000
print(f"Other (HVC, storage):           {other:5.1f}       0.2    0")
total_model = end_uses + dec_hp + dhn_hp + ind_cool + dec_cool + trains + cars + other
total_reality = 85.5
print(f"-----------------------------------------------")
print(f"TOTAL:                         {total_model:5.1f}      {total_reality:.1f}  -{total_reality-total_model:.1f}")

print(f"\n* JRC-IDEES 'specific electricity' = lighting+motors+electronics")
print(f"  Does NOT include electricity for heating (HP, resistive) or cooling")
print(f"  The model adds HP/cooling elec ON TOP of this demand")

print(f"\n{'=' * 70}")
print(f"ROOT CAUSES OF THE ~14 TWh GAP")
print(f"{'=' * 70}")
print(f"1. Grid losses too high:      +{grid_losses_elec-1.3:.1f} TWh (8.64% global vs 3% Finland)")
print(f"   -> Cannot fix per-country (INDEP parameter)")
print(f"   -> But Demands.csv could PRE-COMPENSATE by reducing input by ~{grid_losses_elec-1.3:.0f} TWh")
print(f"   -> Or better: just accept it as structural limitation")
print(f"")
print(f"2. DEC_HP_ELEC too large:     +{dec_hp-7:.1f} TWh")
print(f"   -> Model optimally deploys HP for 55% of low-T heat (decen share)")
print(f"   -> Finnish reality: biomass boilers, oil boilers, direct electric")
print(f"   -> Fix: constrain DEC_HP_ELEC f_max or increase DEC_BOILER costs")
print(f"   -> This is a TECHNOLOGY constraint, not a demand issue")
print(f"")
print(f"3. DHN_HP_ELEC phantom demand: +{dhn_hp-0.5:.1f} TWh")
print(f"   -> 45% DHN share applies to Industry low-T heat ({heat_low_t_ind:.1f} TWh)")
print(f"   -> Creates {dhn_ind_phantom:.1f} TWh phantom industrial DHN demand")
print(f"   -> Fix: reduce Industry HEAT_LOW_T in Demands.csv,")
print(f"     OR reduce share_heat_dhn to ~0.34 (45% of HH+SVC only)")
print(f"")
print(f"IMPORTANT: The 43 TWh ELECTRICITY demand is ~correct for JRC-IDEES")
print(f"'specific electricity'. The gap is NOT in the ELECTRICITY row itself.")
print(f"The gap comes from how the model converts heat demand to electricity")
print(f"(via HP) and from the inflated grid losses.")
