"""
Apply v6 calibration blocks progressively to FI data files.

Usage:
  python scripts/apply_v6_blocks.py --through 1   (apply blocks 0+1)
  python scripts/apply_v6_blocks.py --through 2   (apply blocks 0+1+2)
  ...etc

This script ALWAYS starts from the v5_fperc backup and applies blocks
cumulatively. This ensures reproducibility -- running --through 3
applies Block 0, then 1, then 2, then 3 on top.

After running this, execute:
  python scripts/run_v6_block.py --block N
where N is the highest block applied.
"""
import sys
import shutil
import pandas as pd
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parent.parent
FI_TECH = ROOT / 'Data' / '2017' / 'FI' / 'Technologies.csv'
FI_RES = ROOT / 'Data' / '2017' / 'FI' / 'Resources.csv'
BACKUP_DIR = ROOT / 'Data' / '2017' / 'FI' / 'backups_v5_fperc'


def restore_from_backup():
    """Restore FI files from v5_fperc backup."""
    for fname in ['Technologies.csv', 'Resources.csv']:
        src = BACKUP_DIR / fname
        dst = ROOT / 'Data' / '2017' / 'FI' / fname
        shutil.copy2(src, dst)
    print("Restored from v5_fperc backup")


def apply_block0(fi_tech, fi_res):
    """Block 0: Degeneracy fix -- numerical stabilization.
    
    Approach: Cap all previously-unconstrained technologies (f_max=1e15 in REF)
    at physically reasonable Finnish levels. Use f_max=100 for intermediate
    chain technologies to preserve layer balance feasibility.
    Do NOT set f_max=0 (causes structural infeasibility from layer balances).
    """
    import pandas as pd
    
    # Load REF to find unconstrained techs
    ref = pd.read_csv(ROOT / 'Data' / '2017' / '02_REF_REGION' / 'Technologies.csv', header=0)
    ref = ref.iloc[1:]
    ref['f_max_num'] = pd.to_numeric(ref['f_max'], errors='coerce')
    ref_idx = ref.set_index('Technologies param')
    big_ref = ref_idx[ref_idx['f_max_num'] >= 1e14]
    fi_has_override = fi_tech[fi_tech.notna().any(axis=1)]
    missing = big_ref.index.difference(fi_has_override.index)
    
    SPECIFIC_CAPS = {
        'GRID': 50000, 'DHN': 50000, 'EFFICIENCY': 50000,
        'BEV_BATT': 50000, 'PHEV_BATT': 50000,
        'BUS_COACH_DIESEL': 50000, 'TRAMWAY_TROLLEY': 50000,
        'TRAIN_PUB': 50000, 'TRAIN_FREIGHT': 50000,
        'PLANE_SHORT_HAUL': 50000, 'PLANE_LONG_HAUL': 50000,
        'BOAT_FREIGHT_DIESEL': 50000, 'CARGO_LFO': 100000,
        'OIL_TO_HVC': 50000,
        'GAS_STORAGE': 100, 'DIESEL_STORAGE': 100, 'JET_FUEL_STORAGE': 100,
        'GASOLINE_STORAGE': 100, 'LFO_STORAGE': 100,
        'DHN_HP_ELEC': 5, 'DHN_BOILER_GAS': 5, 'DHN_BOILER_WOOD': 10,
        'DHN_COGEN_WASTE': 5,
        'DEC_HP_ELEC': 10, 'DEC_COGEN_GAS': 5, 'DEC_COGEN_OIL': 5,
        'DEC_BOILER_GAS': 10, 'DEC_BOILER_WOOD': 15, 'DEC_BOILER_OIL': 15,
        'DEC_ELEC_COLD': 10,
        'IND_COGEN_GAS': 5, 'IND_COGEN_WASTE': 5, 'IND_COGEN_COAL': 5,
        'IND_BOILER_BIOWASTE': 5, 'IND_BOILER_WASTE': 5,
        'IND_DIRECT_ELEC': 10, 'IND_ELEC_COLD': 10,
        'BATT_LI': 5,
        'TS_DEC_BOILER_GAS': 10, 'TS_DEC_BOILER_OIL': 15,
        'TS_DEC_BOILER_WOOD': 15, 'TS_DEC_COGEN_GAS': 5, 'TS_DEC_COGEN_OIL': 5,
        'TS_DEC_DIRECT_ELEC': 10, 'TS_DEC_HP_ELEC': 10,
        'TS_DEC_ADVCOGEN_GAS': 10, 'TS_DEC_ADVCOGEN_H2': 10, 'TS_DEC_THHP_GAS': 10,
        'TS_COLD': 10, 'TS_HIGH_TEMP': 20, 'TS_DHN_DAILY': 20, 'TS_DHN_SEASONAL': 20,
    }
    
    for tech_raw in missing:
        tech = tech_raw.strip()
        fmax = SPECIFIC_CAPS.get(tech, 100)  # Default 100 GW for all others
        fi_tech.loc[tech] = [0.0, fmax, 0.0, 1.0]
    
    # Modify existing with oversized caps
    MODIFY = {
        'DEC_DIRECT_ELEC': 10, 'DHN_COGEN_COAL': 10, 'DHN_COGEN_WOOD': 15,
        'IND_BOILER_COAL': 10, 'IND_BOILER_GAS': 10, 'IND_BOILER_WOOD': 20,
        'IND_COGEN_WOOD': 10,
        'CAR_BEV': 50000, 'CAR_DIESEL': 50000, 'CAR_GASOLINE': 50000,
        'CAR_HEV': 50000, 'CAR_PHEV': 50000,
        'TRUCK_DIESEL': 50000, 'TRUCK_METHANOL': 50000, 'TRUCK_NG': 50000,
    }
    for tech, new_fmax in MODIFY.items():
        if tech in fi_tech.index:
            fi_tech.loc[tech, 'f_max'] = new_fmax
    
    return fi_tech, fi_res


def apply_block1(fi_tech, fi_res):
    """Block 1: Oil overconsumption fix — historical realism."""
    fi_res.loc['LFO', 'avail_exterior'] = 80000
    fi_res.loc['JET_FUEL', 'avail_exterior'] = 5000
    return fi_tech, fi_res


def apply_block2(fi_tech, fi_res):
    """Block 2: Biomass forcing — calibration forcing."""
    fi_tech.loc['IND_BOILER_WOOD', 'fmin_perc'] = 0.30
    fi_tech.loc['IND_COGEN_WOOD', 'fmin_perc'] = 0.15
    fi_tech.loc['DHN_COGEN_WOOD', 'fmin_perc'] = 0.30
    
    # Add DEC_BOILER_WOOD fmin_perc if present
    if 'DEC_BOILER_WOOD' in fi_tech.index:
        fi_tech.loc['DEC_BOILER_WOOD', 'fmin_perc'] = 0.15
    
    # Tighten fossil resource caps
    fi_res.loc['GAS', 'avail_exterior'] = 22000
    fi_res.loc['COAL', 'avail_exterior'] = 35000
    return fi_tech, fi_res


def apply_block3(fi_tech, fi_res):
    """Block 3: Nuclear tightening — historical realism."""
    fi_tech.loc['NUCLEAR', 'f_min'] = 2.76
    fi_res.loc['URANIUM', 'avail_exterior'] = 62000
    return fi_tech, fi_res


def apply_block4(fi_tech, fi_res):
    """Block 4: Solar cap — historical realism."""
    fi_tech.loc['PV_ROOFTOP', 'f_max'] = 0.05
    fi_tech.loc['PV_UTILITY', 'f_max'] = 0.02
    return fi_tech, fi_res


def apply_block5(fi_tech, fi_res):
    """Block 5: Coal/peat rebalancing — calibration forcing."""
    fi_tech.loc['IND_BOILER_COAL', 'fmin_perc'] = 0.15
    fi_tech.loc['DHN_COGEN_COAL', 'fmin_perc'] = 0.20
    return fi_tech, fi_res


def apply_block6(fi_tech, fi_res):
    """Block 6: Electricity mix fine-tuning — calibration forcing."""
    fi_tech.loc['CCGT', 'f_max'] = 1.2
    fi_tech.loc['WIND_ONSHORE', 'f_min'] = 1.5
    fi_tech.loc['WIND_ONSHORE', 'f_max'] = 1.7
    fi_tech.loc['WIND_OFFSHORE', 'f_max'] = 0.03
    return fi_tech, fi_res


BLOCK_FUNCS = {
    0: apply_block0,
    1: apply_block1,
    2: apply_block2,
    3: apply_block3,
    4: apply_block4,
    5: apply_block5,
    6: apply_block6,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--through', type=int, required=True,
                        choices=list(range(7)),
                        help='Apply blocks 0 through N')
    args = parser.parse_args()

    # Always start fresh from backup
    restore_from_backup()

    fi_tech = pd.read_csv(FI_TECH, index_col=0)
    fi_res = pd.read_csv(FI_RES, index_col=0)

    for block_num in range(args.through + 1):
        print(f"\nApplying Block {block_num}...")
        fi_tech, fi_res = BLOCK_FUNCS[block_num](fi_tech, fi_res)

    # Sort and save
    fi_tech = fi_tech.sort_index()
    fi_tech.to_csv(FI_TECH)
    fi_res.to_csv(FI_RES)

    print(f"\nApplied blocks 0 through {args.through}")
    print(f"Technologies.csv: {len(fi_tech)} rows")
    print(f"Resources.csv: {len(fi_res)} rows")
    print(f"\nNow run: python scripts/run_v6_block.py --block {args.through}")


if __name__ == '__main__':
    main()
