"""
Build v6 Block 0 Technologies.csv: Degeneracy Fix
===================================================
Adds FI overrides for all 120 technologies that currently have f_max=1e15
in REF_REGION without any FI-specific override.

Also caps some existing FI overrides that have f_max=100000.

Classification: NUMERICAL STABILIZATION (all Block 0 changes)

Author: auto-generated for v6 calibration
Date: 2025-02-28
"""
import pandas as pd
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FI_TECH = ROOT / 'Data' / '2017' / 'FI' / 'Technologies.csv'
FI_RES  = ROOT / 'Data' / '2017' / 'FI' / 'Resources.csv'

# ── Backup current v5_fperc files ──────────────────────────────────
backup_dir = ROOT / 'Data' / '2017' / 'FI' / 'backups_v5_fperc'
backup_dir.mkdir(exist_ok=True)
for f in [FI_TECH, FI_RES]:
    dst = backup_dir / f.name
    if not dst.exists():
        shutil.copy2(f, dst)
        print(f"Backed up {f.name} → backups_v5_fperc/")
    else:
        print(f"Backup already exists: {dst.name}")

# ── Load current FI Technologies ───────────────────────────────────
fi = pd.read_csv(FI_TECH, index_col=0)
print(f"\nCurrent FI Technologies: {len(fi)} rows, "
      f"{fi.notna().any(axis=1).sum()} with data")

# ══════════════════════════════════════════════════════════════════════
# BLOCK 0 OVERRIDES: Technologies NOT in current FI
# Classification: ALL are "numerical stabilization" 
# ══════════════════════════════════════════════════════════════════════

# Category 1: DISABLE (f_max=0) - Future/non-existent in Finland 2017
DISABLE = [
    # Electricity - future
    'CCGT_AMMONIA', 'COAL_IGCC', 'BIOMASS_TO_POWER',
    # Advanced heating
    'DEC_ADVCOGEN_GAS', 'DEC_ADVCOGEN_H2', 'DEC_THHP_GAS',
    # Transport - future fuels
    'BUS_COACH_HYDIESEL', 'BUS_COACH_CNG_STOICH',
    'CAR_NG',
    'BOAT_FREIGHT_NG', 'BOAT_FREIGHT_METHANOL',
    'CARGO_LNG', 'CARGO_METHANOL', 'CARGO_AMMONIA',
    'CARGO_FUELCELL_LH2', 'CARGO_FUELCELL_AMMONIA',
    'CARGO_RETRO_METHANOL', 'CARGO_RETRO_AMMONIA',
    # Hydrogen chain
    'H2_ELECTROLYSIS', 'H2_NG', 'H2_BIOMASS',
    'H2_RETROFITTED', 'H2_NEW', 'H2_SUBSEA_RETRO', 'H2_SUBSEA_NEW',
    # Gas infrastructure (single-region, not needed)
    'GAS_PIPELINE', 'GAS_SUBSEA',
    # Biogas / syngas
    'BIOMASS_TO_METHANE', 'BIOWASTE_TO_METHANE', 'SYN_METHANATION',
    'BIOMETHANATION_WET_BIOMASS', 'BIOMETHANATION_BIOWASTE',
    # Biomass-to-liquids
    'BIOMASS_TO_GASOLINE', 'BIOMASS_TO_DIESEL', 'BIOMASS_TO_JET_FUEL', 'BIOMASS_TO_LFO',
    'BIOWASTE_TO_GASOLINE', 'BIOWASTE_TO_DIESEL', 'BIOWASTE_TO_JET_FUEL', 'BIOWASTE_TO_LFO',
    'DIESEL_TO_JET_FUEL',
    # CCS
    'ATM_CCS', 'INDUSTRY_CCS', 'CO2_STORAGE',
    # Methanol chain
    'SYN_METHANOLATION', 'METHANE_TO_METHANOL', 'BIOMASS_TO_METHANOL', 'BIOWASTE_TO_METHANOL',
    # Ammonia chain
    'HABER_BOSCH', 'AMMONIA_TO_H2',
    # Power-to-X
    'POWER_TO_GASOLINE', 'POWER_TO_DIESEL', 'POWER_TO_JET_FUEL', 'POWER_TO_LFO',
    # H2-to-liquids
    'H2_TO_GASOLINE', 'H2_TO_DIESEL', 'H2_TO_JET_FUEL', 'H2_TO_LFO',
    # HVC alternatives (only OIL_TO_HVC existing)
    'GAS_TO_HVC', 'BIOMASS_TO_HVC', 'METHANOL_TO_HVC',
    # Storage - future
    'H2_STORAGE', 'AMMONIA_STORAGE', 'METHANOL_STORAGE',
    'CAES',
    # Solar thermal storage (parents disabled)
    'PT_STORAGE', 'ST_STORAGE',
    # Thermal storage for disabled parent techs
    'TS_DEC_ADVCOGEN_GAS', 'TS_DEC_ADVCOGEN_H2', 'TS_DEC_THHP_GAS',
    # Plane H2
    'PLANE_H2_SHORT_HAUL',
    # DEC cooling with thhp gas
    'DEC_THHP_GAS_COLD',
]

# Category 2: CAP at realistic Finnish levels
CAP = {
    # DHN heating
    'DHN_HP_ELEC':      0.5,    # small heat pump capacity in DHN
    'DHN_BOILER_GAS':   2.0,    # gas boilers in Finnish DHN
    'DHN_BOILER_WOOD':  5.0,    # wood boilers in DHN
    'DHN_COGEN_WASTE':  1.0,    # waste CHP
    # Decentralised heating
    'DEC_HP_ELEC':      5.0,    # heat pumps still limited in 2017
    'DEC_COGEN_GAS':    0.5,    # small CHP
    'DEC_COGEN_OIL':    0.5,    # oil CHP rare
    'DEC_BOILER_GAS':   5.0,    # gas boilers
    'DEC_BOILER_WOOD':  10.0,   # wood stoves common in Finland
    'DEC_BOILER_OIL':   8.0,    # oil heating still common in 2017
    'DEC_ELEC_COLD':    5.0,    # electric cooling
    # Industry
    'IND_COGEN_GAS':    2.0,
    'IND_COGEN_WASTE':  1.0,
    'IND_COGEN_COAL':   2.0,
    'IND_BOILER_BIOWASTE': 1.0,
    'IND_BOILER_WASTE': 1.0,
    'IND_DIRECT_ELEC':  5.0,    # electric arc furnaces etc
    'IND_ELEC_COLD':    5.0,    # industrial cooling
    # Storage
    'BATT_LI':          1.0,    # negligible in 2017
    'GAS_STORAGE':      100.0,
    'DIESEL_STORAGE':   100.0,
    'JET_FUEL_STORAGE': 100.0,
    'GASOLINE_STORAGE': 100.0,
    'LFO_STORAGE':      100.0,
    # Thermal storage (follow parent tech caps)
    'TS_DEC_BOILER_GAS':    5.0,
    'TS_DEC_BOILER_OIL':    8.0,
    'TS_DEC_BOILER_WOOD':   10.0,
    'TS_DEC_COGEN_GAS':     0.5,
    'TS_DEC_COGEN_OIL':     0.5,
    'TS_DEC_DIRECT_ELEC':   5.0,
    'TS_DEC_HP_ELEC':       5.0,
    'TS_COLD':              5.0,
    'TS_HIGH_TEMP':         20.0,  # industrial heat storage
    'TS_DHN_DAILY':         20.0,  # DHN daily storage
    'TS_DHN_SEASONAL':      20.0,  # DHN seasonal (limited in 2017)
}

# Category 3: KEEP at 100000 (demand-driven, bounded by sector constraints)
KEEP_LARGE = {
    'GRID':                 100000,
    'DHN':                  100000,
    'EFFICIENCY':           100000,
    'BUS_COACH_DIESEL':     100000,
    'TRAMWAY_TROLLEY':      100000,
    'TRAIN_PUB':            100000,
    'TRAIN_FREIGHT':        100000,
    'PLANE_SHORT_HAUL':     100000,
    'PLANE_LONG_HAUL':      100000,
    'BOAT_FREIGHT_DIESEL':  100000,
    'CARGO_LFO':            100000,
    'OIL_TO_HVC':           100000,
    'BEV_BATT':             100000,  # follows CAR_BEV
    'PHEV_BATT':            100000,  # follows CAR_PHEV
}

# ── Existing FI overrides to MODIFY (f_max=100000 → capped) ────────
# These already exist in FI but have f_max=100000 (too high for solver)
MODIFY_EXISTING = {
    'DEC_DIRECT_ELEC':  5.0,    # currently 100000
    'DHN_COGEN_COAL':   5.0,    # currently 100000
    'DHN_COGEN_WOOD':   10.0,   # currently 100000
    'IND_BOILER_COAL':  5.0,    # currently 100000
    'IND_BOILER_GAS':   5.0,    # currently 100000
    'IND_BOILER_WOOD':  15.0,   # currently 100000
    'IND_COGEN_WOOD':   8.0,    # currently 100000
    'TRUCK_METHANOL':   0.0,    # currently 100000 → disable
    'TRUCK_NG':         0.0,    # currently 100000 → disable
}

# ══════════════════════════════════════════════════════════════════════
# BUILD THE NEW TECHNOLOGIES.CSV
# ══════════════════════════════════════════════════════════════════════

new_rows = []

# Add DISABLE techs
for tech in DISABLE:
    new_rows.append({
        'Technologies param': tech,
        'f_min': 0.0,
        'f_max': 0.0,
        'fmin_perc': 0.0,
        'fmax_perc': 1.0,
    })

# Add CAP techs
for tech, fmax in CAP.items():
    new_rows.append({
        'Technologies param': tech,
        'f_min': 0.0,
        'f_max': fmax,
        'fmin_perc': 0.0,
        'fmax_perc': 1.0,
    })

# Add KEEP_LARGE techs
for tech, fmax in KEEP_LARGE.items():
    new_rows.append({
        'Technologies param': tech,
        'f_min': 0.0,
        'f_max': fmax,
        'fmin_perc': 0.0,
        'fmax_perc': 1.0,
    })

new_df = pd.DataFrame(new_rows)
new_df = new_df.set_index('Technologies param')
print(f"\nNew rows to add: {len(new_df)}")
print(f"  Disabled: {len(DISABLE)}")
print(f"  Capped: {len(CAP)}")
print(f"  Keep large: {len(KEEP_LARGE)}")
print(f"  Total: {len(DISABLE) + len(CAP) + len(KEEP_LARGE)}")

# Modify existing FI overrides
modified_count = 0
for tech, new_fmax in MODIFY_EXISTING.items():
    if tech in fi.index:
        old_fmax = fi.loc[tech, 'f_max']
        fi.loc[tech, 'f_max'] = new_fmax
        if new_fmax == 0.0:
            fi.loc[tech, 'f_min'] = 0.0
            fi.loc[tech, 'fmin_perc'] = 0.0
            fi.loc[tech, 'fmax_perc'] = 1.0
        print(f"  Modified {tech}: f_max {old_fmax} → {new_fmax}")
        modified_count += 1
    else:
        print(f"  WARNING: {tech} not in FI overrides, adding as new")
        new_df.loc[tech] = [0.0, new_fmax, 0.0, 1.0]

# Merge: existing FI + new rows (existing takes precedence except modifications)
# Check for conflicts
conflicts = new_df.index.intersection(fi.index)
if len(conflicts) > 0:
    print(f"\nWARNING: {len(conflicts)} techs in both new and existing FI:")
    for c in conflicts:
        print(f"  {c}: FI f_max={fi.loc[c, 'f_max']}, new f_max={new_df.loc[c, 'f_max']}")
    # Keep FI values for existing entries
    new_df = new_df.drop(conflicts)

# Combine
result = pd.concat([fi, new_df])
# Sort alphabetically
result = result.sort_index()

print(f"\nFinal Technologies.csv: {len(result)} rows")
print(f"  With data: {result.notna().any(axis=1).sum()}")

# Save
result.to_csv(FI_TECH)
print(f"\nSaved to {FI_TECH}")

# ── Summary for changelog ─────────────────────────────────────────
print("\n" + "=" * 60)
print("BLOCK 0 CHANGELOG SUMMARY")
print("=" * 60)
print(f"Classification: NUMERICAL STABILIZATION")
print(f"Total changes: {len(DISABLE) + len(CAP) + len(KEEP_LARGE) + modified_count}")
print(f"  New rows: {len(new_df) + len(conflicts)}")
print(f"    - Disabled (f_max=0): {len(DISABLE)}")
print(f"    - Capped (realistic): {len(CAP)}")
print(f"    - Keep large (100000): {len(KEEP_LARGE)}")
print(f"  Modified existing: {modified_count}")
for tech, new_fmax in MODIFY_EXISTING.items():
    print(f"    - {tech}: → f_max={new_fmax}")
