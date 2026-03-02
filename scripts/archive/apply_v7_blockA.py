"""
Apply v7 Block A: Disable Future Technologies
==============================================
Changes f_max from 100.0 to 0.0 for all technologies that did not exist
in Finland 2017.

This fixes the root cause of the v6 degeneracy issue where technologies
with f_max=100.0 were deploying at ~99 GW.

Author: Copilot v7 calibration
Date: 2026-02-27
"""
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
FI_TECH = ROOT / 'Data' / '2017' / 'FI' / 'Technologies.csv'

# ══════════════════════════════════════════════════════════════════════
# BLOCK A: Technologies to DISABLE (f_max → 0)
# These should NOT exist in Finland 2017
# ══════════════════════════════════════════════════════════════════════

DISABLE = [
    # === Electricity - Future ===
    'CCGT_AMMONIA',       # No ammonia power in 2017
    'COAL_IGCC',          # No IGCC in 2017
    'BIOMASS_TO_POWER',   # Standalone biomass power not counted separately
    
    # === Hydrogen Production ===
    'H2_ELECTROLYSIS',    # Negligible H2 electrolysis in 2017
    'H2_NG',              # No SMR H2 in 2017
    'H2_BIOMASS',         # No biomass gasification H2 in 2017
    
    # === Hydrogen Infrastructure ===
    'H2_RETROFITTED',     # No H2 pipelines in 2017
    'H2_NEW',             # No H2 pipelines in 2017
    'H2_SUBSEA_RETRO',    # No H2 subsea in 2017
    'H2_SUBSEA_NEW',      # No H2 subsea in 2017
    'H2_STORAGE',         # No H2 storage in 2017
    
    # === Syngas / Biogas ===
    'BIOMASS_TO_METHANE',          # Limited biogas in 2017
    'BIOWASTE_TO_METHANE',         # Limited biogas in 2017
    'SYN_METHANATION',             # No PtG in 2017
    'BIOMETHANATION_WET_BIOMASS',  # Very small scale
    'BIOMETHANATION_BIOWASTE',     # Very small scale
    
    # === Biomass-to-Liquids ===
    'BIOMASS_TO_GASOLINE',
    'BIOMASS_TO_DIESEL',
    'BIOMASS_TO_JET_FUEL',
    'BIOMASS_TO_LFO',
    
    # === Biowaste-to-Liquids ===
    'BIOWASTE_TO_GASOLINE',
    'BIOWASTE_TO_DIESEL',
    'BIOWASTE_TO_JET_FUEL',
    'BIOWASTE_TO_LFO',
    
    # === Fuel Conversion ===
    'DIESEL_TO_JET_FUEL',  # No diesel-to-jet in 2017
    
    # === CCS ===
    'ATM_CCS',        # No DAC in 2017
    'INDUSTRY_CCS',   # No industrial CCS in 2017
    'CO2_STORAGE',    # No CO2 storage in 2017
    
    # === Methanol Chain ===
    'SYN_METHANOLATION',     # No synthetic methanol in 2017
    'METHANE_TO_METHANOL',   # No methane-to-methanol in 2017
    'BIOMASS_TO_METHANOL',   # No biomass-to-methanol in 2017
    'BIOWASTE_TO_METHANOL',  # No biowaste-to-methanol in 2017
    'METHANOL_STORAGE',      # No methanol storage at scale
    
    # === Ammonia Chain ===
    'HABER_BOSCH',       # Not for energy in 2017
    'AMMONIA_TO_H2',     # No ammonia cracking in 2017
    'AMMONIA_STORAGE',   # No ammonia storage for energy
    
    # === Power-to-X ===
    'POWER_TO_GASOLINE',
    'POWER_TO_DIESEL',
    'POWER_TO_JET_FUEL',
    'POWER_TO_LFO',
    
    # === H2-to-Liquids ===
    'H2_TO_GASOLINE',
    'H2_TO_DIESEL',
    'H2_TO_JET_FUEL',
    'H2_TO_LFO',
    
    # === Advanced Heating (Future) ===
    'DEC_ADVCOGEN_GAS',   # Advanced cogen not in 2017
    'DEC_ADVCOGEN_H2',    # H2 cogen not in 2017
    'DEC_THHP_GAS',       # Thermally-driven HP not common in 2017
    
    # === HVC Alternatives ===
    # Keep OIL_TO_HVC (exists), disable alternatives
    'GAS_TO_HVC',
    'BIOMASS_TO_HVC',
    'METHANOL_TO_HVC',
    
    # === Future Shipping ===
    'CARGO_LNG',              # Very limited LNG shipping in 2017
    'CARGO_METHANOL',         # No methanol shipping
    'CARGO_AMMONIA',          # No ammonia shipping
    'CARGO_FUELCELL_LH2',     # No H2 fuel cell ships
    'CARGO_FUELCELL_AMMONIA', # No ammonia fuel cell ships
    'CARGO_RETRO_METHANOL',   # No retrofits
    'CARGO_RETRO_AMMONIA',    # No retrofits
    
    # === Future Freight ===
    'BOAT_FREIGHT_NG',        # Very limited
    'BOAT_FREIGHT_METHANOL',  # Non-existent
    
    # === Future Bus/Coach ===
    'BUS_COACH_HYDIESEL',     # Negligible
    'BUS_COACH_CNG_STOICH',   # Negligible
    
    # === Future Cars ===
    'CAR_NG',  # Very limited CNG cars in 2017
    
    # === Future Trucks ===
    'TRUCK_METHANOL',  # No methanol trucks
    'TRUCK_NG',        # Very limited NG trucks
    
    # === Gas Infrastructure (single-region) ===
    'GAS_PIPELINE',  # Not needed for single-region
    'GAS_SUBSEA',    # Not needed for single-region
    
    # === Storage - Future ===
    'CAES',          # No CAES in Finland 2017
    'PT_STORAGE',    # No parabolic trough storage
    'ST_STORAGE',    # No solar tower storage
]

# ══════════════════════════════════════════════════════════════════════

def main():
    # Backup current file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = FI_TECH.parent / f'Technologies_pre_v7_blockA_{timestamp}.csv'
    shutil.copy2(FI_TECH, backup_path)
    print(f"Backed up → {backup_path.name}")
    
    # Read current Technologies.csv
    df = pd.read_csv(FI_TECH)
    print(f"\nOriginal file: {len(df)} rows")
    
    # Count how many will be changed
    changed = 0
    for tech in DISABLE:
        mask = df['Technologies param'] == tech
        if mask.any():
            old_fmax = df.loc[mask, 'f_max'].values[0]
            if old_fmax != 0.0:
                df.loc[mask, 'f_max'] = 0.0
                changed += 1
                print(f"  {tech}: f_max {old_fmax} → 0.0")
        else:
            print(f"  ** {tech} not found in Technologies.csv (may be in REF_REGION only)")
    
    print(f"\nChanged {changed} technologies from f_max>0 to f_max=0.0")
    
    # Save
    df.to_csv(FI_TECH, index=False)
    print(f"Saved → {FI_TECH}")
    
    # Summary
    print("\n" + "="*60)
    print("BLOCK A APPLIED: Future Technologies Disabled")
    print("="*60)
    print(f"Total technologies disabled: {len(DISABLE)}")
    print(f"Technologies found and modified: {changed}")
    print("\nNext steps:")
    print("1. Run model: python scripts/run_calib_case.py --version v7_blockA")
    print("2. Compare outputs with v6_block6")
    print("3. Check that F=0 for all disabled technologies")

if __name__ == '__main__':
    main()
