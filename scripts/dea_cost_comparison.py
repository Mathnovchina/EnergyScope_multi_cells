"""Compare DEA 2015/2020 costs with EnergyScope REF_REGION costs."""
import pandas as pd
import numpy as np

dea = pd.read_excel('Data/exogenous_data/DEA_Elec_Heat.xlsx', sheet_name='alldata_flat')

# Read current REF (2035-based) and original 2017 backup
ref_current = pd.read_csv('Data/2017/02_REF_REGION/Technologies.csv').set_index('Technologies param')
ref_orig = pd.read_csv('Data/2017/02_REF_REGION/Technologies.csv.bak_20260308_pre2035').set_index('Technologies param')

# DEA -> EnergyScope mapping
mapping = {
    'NUCLEAR': {
        'dea_name': None,  # Nuclear not in DEA Elec&Heat catalogue
        'note': 'Nuclear not in DEA catalogue - use IEA/WNA estimates',
    },
    'WIND_ONSHORE': {
        'dea_name': 'Onshore wind turbine, utility - renewable power - wind - large',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
    'WIND_OFFSHORE': {
        'dea_name': 'Offshore Wind - AC connected - Fixed bottom',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
    'PV_ROOFTOP': {
        'dea_name': 'PV - renewable power - solar - residential rooftop',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
    'PV_UTILITY': {
        'dea_name': 'PV - renewable power - solar - utility-scale, ground mounted',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
    'COAL_US': {
        'dea_name': 'Coal power plant, supercritical - extraction - coal - medium',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
    'CCGT': {
        'dea_name': 'Gas turbine, combined cycle - extraction - natural gas - large',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
    'DHN_COGEN_GAS': {
        'dea_name': 'Gas turbine, combined cycle - back pressure - natural gas - medium',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
    'DHN_COGEN_WOOD': {
        'dea_name': 'Biomass CHP - extraction - wood chips - large',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
    'DHN_BOILER_GAS': {
        'dea_name': 'Gas boiler - boiler - natural gas - medium',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_h]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_h/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_h',
    },
    'DHN_BOILER_WOOD': {
        'dea_name': 'Biomass boiler - boiler - wood chips - large',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_h]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_h/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_h',
    },
    'DHN_HP_ELEC': {
        'dea_name': 'Heat pump, air source - heat pump - electricity - large',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_h]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_h/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_h',
    },
    'BIOMASS_TO_POWER': {
        'dea_name': 'Biomass CHP - back pressure - wood chips - medium',
        'inv_par': 'Nominal investment (*total) [MEUR/MW_e]',
        'om_par': 'Fixed O&M (*total) [EUR/MW_e/y]',
        'lt_par': 'Technical lifetime [years]',
        'cap_unit': 'MW_e',
    },
}

print("=" * 130)
print(f"{'ESMC Tech':<22} {'DEA 2015 c_inv':>15} {'DEA 2020 c_inv':>15} {'Interp 2017':>12} {'Orig 2017 REF':>14} {'Curr 2035 REF':>14} {'Orig vs DEA17':>14} {'Need fix?':>10}")
print(f"{'':22} {'(MEUR/MW)':>15} {'(MEUR/MW)':>15} {'(MEUR/MW)':>12} {'(MEUR/MW)':>14} {'(MEUR/MW)':>14} {'(%)':>14} {'':>10}")
print("=" * 130)

for esmc_name, m in mapping.items():
    if m.get('dea_name') is None:
        # Get REF values
        c_inv_orig = float(ref_orig.loc[esmc_name, 'c_inv']) if esmc_name in ref_orig.index else None
        c_inv_curr = float(ref_current.loc[esmc_name, 'c_inv']) if esmc_name in ref_current.index else None
        note = m.get('note', '')
        print(f"{esmc_name:<22} {'N/A':>15} {'N/A':>15} {'N/A':>12} {c_inv_orig:>14.1f} {c_inv_curr:>14.1f} {'N/A':>14} {'--':>10}  ({note})")
        continue

    tech_data = dea[dea['Technology'] == m['dea_name']]
    if len(tech_data) == 0:
        print(f"{esmc_name:<22} NO DEA DATA for: {m['dea_name']}")
        continue

    inv = tech_data[tech_data['par'] == m['inv_par']]
    om = tech_data[tech_data['par'] == m['om_par']]
    lt = tech_data[tech_data['par'] == m['lt_par']]

    # Get DEA 2015 and 2020 values
    inv_2015 = inv[inv['year'] == 2015]['val'].values
    inv_2020 = inv[inv['year'] == 2020]['val'].values
    om_2015 = om[om['year'] == 2015]['val'].values
    om_2020 = om[om['year'] == 2020]['val'].values
    lt_2015 = lt[lt['year'] == 2015]['val'].values
    lt_2020 = lt[lt['year'] == 2020]['val'].values

    # Interpolate to 2017 (linear between 2015 and 2020)
    def interp_2017(v2015, v2020):
        if len(v2015) > 0 and len(v2020) > 0:
            return v2015[0] + (v2020[0] - v2015[0]) * (2017 - 2015) / (2020 - 2015)
        elif len(v2015) > 0:
            return v2015[0]
        elif len(v2020) > 0:
            return v2020[0]
        return None

    inv_17 = interp_2017(inv_2015, inv_2020)
    # MEUR/MW = kEUR/GW (same unit as EnergyScope)
    # DEA gives MEUR/MW, EnergyScope uses MEUR/GW = kEUR/MW... 
    # Actually need to check: EnergyScope c_inv unit
    # In ESMC, c_inv is in MEUR/GW (=kEUR/MW). DEA gives MEUR/MW.
    # So DEA MEUR/MW * 1000 = MEUR/GW (ESMC unit)?  No.
    # Let me check: 1 MEUR/MW = 1000 MEUR/GW? No, 1 MEUR/MW = 1000 MEUR/GW is wrong.
    # 1 MEUR / 1 MW × 1000 MW/GW = 1000 MEUR/GW
    # So DEA 1.095 MEUR/MW_e = 1095 MEUR/GW_e
    # And ESMC shows WIND_ONSHORE c_inv = 1095.36
    # So ESMC c_inv is in MEUR/GW (which equals kEUR/kW)

    # Get original 2017 and current 2035 REF values
    c_inv_orig = float(ref_orig.loc[esmc_name, 'c_inv']) if esmc_name in ref_orig.index else None
    c_inv_curr = float(ref_current.loc[esmc_name, 'c_inv']) if esmc_name in ref_current.index else None

    # Convert DEA to ESMC units: MEUR/MW -> MEUR/GW (multiply by 1000)
    inv_15_esmc = inv_2015[0] * 1000 if len(inv_2015) > 0 else None
    inv_20_esmc = inv_2020[0] * 1000 if len(inv_2020) > 0 else None
    inv_17_esmc = inv_17 * 1000 if inv_17 is not None else None

    # Compare original 2017 REF vs DEA 2017 interpolated
    if c_inv_orig is not None and inv_17_esmc is not None:
        diff_pct = (c_inv_orig - inv_17_esmc) / inv_17_esmc * 100
        need_fix = "YES" if abs(diff_pct) > 15 else ("maybe" if abs(diff_pct) > 5 else "no")
    else:
        diff_pct = None
        need_fix = "??"

    inv15_str = f"{inv_15_esmc:.1f}" if inv_15_esmc else "N/A"
    inv20_str = f"{inv_20_esmc:.1f}" if inv_20_esmc else "N/A"
    inv17_str = f"{inv_17_esmc:.1f}" if inv_17_esmc else "N/A"
    orig_str = f"{c_inv_orig:.1f}" if c_inv_orig else "N/A"
    curr_str = f"{c_inv_curr:.1f}" if c_inv_curr else "N/A"
    diff_str = f"{diff_pct:+.1f}%" if diff_pct is not None else "N/A"

    print(f"{esmc_name:<22} {inv15_str:>15} {inv20_str:>15} {inv17_str:>12} {orig_str:>14} {curr_str:>14} {diff_str:>14} {need_fix:>10}")

print()
print("Units: MEUR/GW (= kEUR/MW). DEA prices in 2020 EUR.")
print("'Orig 2017 REF' = backup from before 2035 overwrite.")
print("'Curr 2035 REF' = currently installed (from 2035 modeller data).")
print("'Interp 2017' = linear interpolation between DEA 2015 and DEA 2020.")
print("'Orig vs DEA17' = how far original 2017 REF was from DEA 2017 interpolated.")
