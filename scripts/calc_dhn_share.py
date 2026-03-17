"""
Calculate the correct share_heat_dhn to match Finnish reality.

The model applies share_heat_dhn uniformly to ALL sectors' low-T heat.
In Finnish reality, DHN serves mainly HH and SVC, not Industry.
Industry uses on-site boilers and CHP.
"""
import pandas as pd

# Current demands (GWh)
demands = {
    'HEAT_LOW_T_SH': {'HH': 38556.68, 'SVC': 24966.99, 'IND': 22111.86},
    'HEAT_LOW_T_HW': {'HH': 6008.83,  'SVC': 5239.85,  'IND': 9130.41},
}

# Totals
for param in demands:
    demands[param]['TOTAL'] = sum(demands[param].values())

heat_sh = demands['HEAT_LOW_T_SH']
heat_hw = demands['HEAT_LOW_T_HW']

total_low_t = heat_sh['TOTAL'] + heat_hw['TOTAL']
hh_svc_low_t = heat_sh['HH'] + heat_sh['SVC'] + heat_hw['HH'] + heat_hw['SVC']
ind_low_t = heat_sh['IND'] + heat_hw['IND']

print("=== Current Low-T Heat Demands (TWh) ===")
print(f"  HH:        {(heat_sh['HH'] + heat_hw['HH'])/1000:.1f}")
print(f"  SVC:       {(heat_sh['SVC'] + heat_hw['SVC'])/1000:.1f}")
print(f"  IND:       {ind_low_t/1000:.1f}")
print(f"  TOTAL:     {total_low_t/1000:.1f}")
print()

# Finnish DHN reality: 36.5 TWh delivered (before DHN losses)
# DHN loss = 8.5% (from calibration template)
# DHN demand including losses = 36.5 * (1 + 0.085) = ~39.6 TWh?
# Actually: model DHN demand = (HH+SVC+IND) * share_dhn + DHN_losses
# DHN losses are separate in the model via loss_network[HEAT_LOW_T_DHN] = 0.05

dhn_reality_production = 36.5  # TWh, from Finnish Energy
dhn_loss_rate = 0.05  # from Misc_indep.json
# Production = demand + losses... but the model constraint is different
# In the model: End_uses[DHN] = (SH*ts + HW/8760) * share_dhn + Network_losses[DHN]
# And Network_losses[DHN] = sum(production_DHN) * loss_network[DHN]
# So: sum(production_DHN) = End_uses[DHN] where End_uses includes losses

print("=== DHN Share Calculation ===")
print(f"Finnish DHN production (reality): {dhn_reality_production:.1f} TWh")
print(f"DHN loss rate (model):            {dhn_loss_rate:.1%}")
print()

# If DHN share applies to ALL sectors (current):
# DHN demand (before losses) = total_low_t * 0.45 = 106 * 0.45 = 47.7 TWh
# Then losses add another 5% of production on top
# So total DHN supply needed = 47.7 / (1 - 0.05) = 50.2 TWh approx
# We see 52.7 TWh in the model (extra because of temporal mismatch)
current_dhn_demand = total_low_t / 1000 * 0.45
print(f"Current model DHN demand (before losses): {current_dhn_demand:.1f} TWh")
print(f"Current model DHN production (v26):       52.7 TWh")
print()

# OPTION A: Change share_heat_dhn to exclude industry
# If DHN only serves HH+SVC, the effective share on total heat should be:
# 36.5 TWh = correct_share * total_low_t + DHN_losses
# Roughly: correct_share = 36.5 / 106 ≈ 0.344
effective_share_for_hh_svc_only = dhn_reality_production / (total_low_t / 1000)
print(f"OPTION A: Reduce share_heat_dhn")
print(f"  Effective share for 36.5 TWh on {total_low_t/1000:.0f} TWh = {effective_share_for_hh_svc_only:.3f}")
print(f"  But losses inflate this, so accounting for 5% loss:")
# More precisely: total_production = demand * (1 + loss_on_prod)
# The model formula is: losses = production * 0.05
# So production = demand / (1 - 0.05) => demand = production * 0.95
# If target production = 36.5, demand = 36.5 * 0.95 = 34.675
# share = 34.675 / 106 = 0.327
dhn_demand_net = dhn_reality_production * (1 - dhn_loss_rate)
share_option_a = dhn_demand_net / (total_low_t / 1000)
print(f"  Corrected share = {dhn_demand_net:.1f} / {total_low_t/1000:.0f} = {share_option_a:.3f}")
print(f"  Set share_heat_dhn_min/max ≈ 0.327")
print()

# OPTION B: Remove Industry from low-T heat (move to HEAT_HIGH_T)
# Keep share_heat_dhn = 0.45, but zero out HEAT_LOW_T for Industry
# Then: DHN demand = (HH+SVC) * 0.45 = 74.8 * 0.45 = 33.6 TWh
# That's too low compared to 36.5 reality...
hh_svc_only = hh_svc_low_t / 1000
dhn_if_hh_svc = hh_svc_only * 0.45
print(f"OPTION B: Zero out IND HEAT_LOW_T (move to HEAT_HIGH_T)")
print(f"  HH+SVC low-T: {hh_svc_only:.1f} TWh")
print(f"  DHN demand = {hh_svc_only:.1f} * 0.45 = {dhn_if_hh_svc:.1f} TWh")
print(f"  vs reality 36.5 TWh -> {'too low' if dhn_if_hh_svc < 36.5 else 'OK'}")
print()

# OPTION B+: Recalculate the DHN share for HH+SVC only
share_for_hh_svc = dhn_demand_net / hh_svc_only
print(f"OPTION B+: Keep IND low-T heat, adjust share for HH+SVC only")
print(f"  Required share (HH+SVC only): {dhn_demand_net:.1f} / {hh_svc_only:.1f} = {share_for_hh_svc:.3f}")
print(f"  But the model has NO per-sector DHN share! share_heat_dhn is global.")
print()

# OPTION C: Reduce Industry HEAT_LOW_T_SH and HEAT_LOW_T_HW
# Move some industry low-T to HEAT_HIGH_T
# Target: reduce total low-T so that 45% of remaining = 36.5 TWh
# target_total_low_t * 0.45 = 36.5 / 0.95 = 38.4 (accounting for net)
# Wait, the relationship is more complex. Let me think about this differently.
#
# Actually the simplest fix: reduce share_heat_dhn from 0.45 to ~0.33
# This gives: 106 * 0.33 = 35.0 TWh DHN demand (close to 36.5 after losses)
print(f"=== RECOMMENDED FIX ===")
print()

# Method: set share_heat_dhn_min/max to deliver the correct DHN demand
# Target: model DHN production = 36.5 TWh
# The actual relationship includes temporal effects, but approximately:
# share_dhn * total_low_t_demand ≈ DHN_demand
# DHN_production ≈ DHN_demand / (1 - 0.05) ? No, model formula is different
# Network_losses = sum(production) * loss_rate
# End_uses = demand + losses
# So: production = demand + losses = demand + production * 0.05
# => production = demand / 0.95
# => demand = production * 0.95 = 36.5 * 0.95 = 34.675 TWh
# => share = 34.675 / 106 = 0.327

target_share = dhn_demand_net / (total_low_t / 1000)
print(f"OPTION 1 (SIMPLEST): Change share_heat_dhn in reg_misc.dat")
print(f"  Old:  share_heat_dhn_min = 0.449, share_heat_dhn_max = 0.451")
print(f"  New:  share_heat_dhn_min = {target_share - 0.001:.3f}, share_heat_dhn_max = {target_share + 0.001:.3f}")
print(f"  This reduces DHN demand from ~48 to ~35 TWh")
print(f"  DHN production after 5% losses: ~{target_share * total_low_t / 1000 / 0.95:.1f} TWh (target: 36.5)")
print()

# But wait - this changes the HH/SVC heating mix too!
# Currently HH+SVC get 45% DHN, 55% decentralized
# If we reduce to 33%, they get 33% DHN, 67% decentralized
# Finnish reality: 45% of HH+SVC heating from DHN is correct!
# The issue is only that IND shouldn't use DHN.

print(f"PROBLEM with Option 1: it also reduces DHN share for HH+SVC")
print(f"  from 45% to {target_share:.0%}, but HH+SVC really do get ~45% DHN!")
print()

print(f"OPTION 2 (BETTER): Move Industry HEAT_LOW_T to HEAT_HIGH_T in Demands.csv")
print(f"  Rationale: In Finland, industry 'low-temperature' heat (process heat")
print(f"  <100°C) is mostly provided by on-site boilers/CHP, not DHN.")
print(f"  By reclassifying IND low-T as high-T, the DHN share only applies")
print(f"  to HH+SVC, where 45% is correct.")
print()
print(f"  Change in Demands.csv:")
print(f"    HEAT_LOW_T_SH[IND]: {heat_sh['IND']:.2f} -> 0 GWh")
print(f"    HEAT_LOW_T_HW[IND]: {heat_hw['IND']:.2f} -> 0 GWh")
print(f"    HEAT_HIGH_T[IND]:   59820.73 -> {59820.73 + heat_sh['IND'] + heat_hw['IND']:.2f} GWh")
print()
new_total_low_t = hh_svc_low_t / 1000
new_dhn = new_total_low_t * 0.45
print(f"  Result: Total low-T = {new_total_low_t:.1f} TWh (HH+SVC only)")
print(f"  DHN demand = {new_total_low_t:.1f} * 0.45 = {new_dhn:.1f} TWh")
print(f"  DHN production = {new_dhn / 0.95:.1f} TWh (target: 36.5)")

# This gives 33.7 / 0.95 = 35.4 TWh - still slightly below 36.5
# Let's check: maybe we need share_heat_dhn = 0.46-0.47 for HH+SVC?
needed_share_hh_svc = dhn_demand_net / new_total_low_t
print()
print(f"  Fine-tune: for exactly 36.5 TWh DHN production:")
print(f"  share_heat_dhn = {needed_share_hh_svc:.3f} (very close to current 0.45)")
print(f"  With share={needed_share_hh_svc:.3f}: DHN demand = {needed_share_hh_svc * new_total_low_t:.1f} TWh")
print(f"  DHN production = {needed_share_hh_svc * new_total_low_t / 0.95:.1f} TWh")
print()
print(f"OPTION 2 VERDICT: Move IND low-T to high-T, keep share_heat_dhn ~ 0.463")
print(f"  This correctly represents Finnish reality where:")
print(f"  - HH/SVC get ~46% of heating from DHN (Finnish Energy data)")
print(f"  - Industry uses on-site boilers for low-T heat, not DHN")
