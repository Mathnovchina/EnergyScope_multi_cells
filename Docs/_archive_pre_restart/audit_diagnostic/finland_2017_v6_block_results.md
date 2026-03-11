# Finland 2017 v6 Calibration — Block-by-Block Results

Generated: 2026-02-26 18:06

## Solver Note

All runs use CPLEX 22.1.2 barrier solver (crossover disabled — consistently
produces 0 simplex iterations regardless of settings). The barrier interior-point
solution does NOT exactly satisfy variable bounds or linear constraints.
Tolerance violations (MaxAbs up to ~10^2 on bounds, ~10^5 on constraints) mean
that f_max caps and resource availability limits are only **approximately** enforced.
solve_result_num = -1 for all runs (feasible with numerical issues).

## Objective Function Progression

![Objective Progression](../plots/v6_blocks/01_objective_progression.png)

| Block | Objective (MEUR) |
|-------|-----------------|
| v5_fperc | 2.32e+16 |
| Block0_degeneracy | 1.94e+07 |
| Block1_oil | 2.47e+07 |
| Block2_biomass | 1.67e+07 |
| Block3_nuclear | 2.57e+07 |
| Block4_solar | 2.63e+07 |
| Block5_coal | 1.62e+07 |
| Block6_elecmix | 2.12e+07 |

## Key Resource Usage (GWh)

Reality targets: WOOD=105K, Total Oil=96K, GAS=25K, COAL+PEAT=50K, NUCLEAR=65K

![Resource Evolution](../plots/v6_blocks/02_resource_evolution.png)

| Resource | v5_fperc | Block0_degeneracy | Block1_oil | Block2_biomass | Block3_nuclear | Block4_solar | Block5_coal | Block6_elecmix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ELECTRICITY | 24998.0 | 24998.0 | 24996.0 | 24996.0 | 24999.0 | 24999.0 | 24995.0 | 24999.0 |
| GASOLINE | 15361.0 | 16042.0 | 15862.0 | 16126.0 | 16132.0 | 15787.0 | 15815.0 | 15808.0 |
| DIESEL | 24890.0 | 24989.0 | 24978.0 | 24980.0 | 24990.0 | 24986.0 | 24879.0 | 24981.0 |
| LFO | 149140.0 | 81808.0 | 78759.0 | 77907.0 | 78742.0 | 79246.0 | 77812.0 | 78806.0 |
| JET_FUEL | 14156.0 | 15087.0 | 5554.0 | 5741.0 | 5736.0 | 5547.0 | 5584.0 | 5577.0 |
| GAS | 27999.0 | 27999.0 | 27999.0 | 22004.0 | 22004.0 | 22002.0 | 22001.0 | 22002.0 |
| WOOD | 3024.0 | 15353.0 | 15092.0 | 51847.0 | 50431.0 | 51577.0 | 50439.0 | 50581.0 |
| ENERGY_CROPS_2 | 1222.0 | 7640.0 | 7713.0 | 7983.0 | 8031.0 | 8675.0 | 8667.0 | 8558.0 |
| BIOWASTE | 408.0 | 537.0 | 549.0 | 692.0 | 635.0 | 622.0 | 792.0 | 690.0 |
| BIOMASS_RESIDUES | 411.0 | 536.0 | 549.0 | 693.0 | 635.0 | 622.0 | 793.0 | 690.0 |
| COAL | 9188.0 | 19347.0 | 18698.0 | 14329.0 | 14368.0 | 13331.0 | 18427.0 | 18370.0 |
| URANIUM | 79959.0 | 120558.0 | 144484.0 | 188311.0 | 192259.0 | 190337.0 | 197462.0 | 195788.0 |
| WASTE | 1021.0 | 8488.0 | 10909.0 | 1924.0 | 1388.0 | 1974.0 | 2488.0 | 2124.0 |
| WET_BIOMASS | 81.0 | 44.0 | 41.0 | 53.0 | 46.0 | 45.0 | 101.0 | 54.0 |
| RES_WIND | 6761.0 | 7348.0 | 7301.0 | 7550.0 | 7564.0 | 7341.0 | 7329.0 | 5925.0 |
| RES_SOLAR | 5505.0 | 7861.0 | 7987.0 | 7379.0 | 7566.0 | 5788.0 | 4898.0 | 5145.0 |
| RES_HYDRO | 15470.0 | 15605.0 | 15522.0 | 15459.0 | 15517.0 | 15410.0 | 15326.0 | 15395.0 |
| RES_GEO | 2346.0 | 2528.0 | 2483.0 | 2558.0 | 2578.0 | 2547.0 | 2561.0 | 2562.0 |
| TOTAL_OIL | 203546.0 | 137926.0 | 125153.0 | 124754.0 | 125601.0 | 125565.0 | 124089.0 | 125172.0 |
| TOTAL_BIOMASS | 5146.0 | 24111.0 | 23944.0 | 61269.0 | 59778.0 | 61541.0 | 60792.0 | 60573.0 |

## F > f_max Violations (Block 6 final)

![F > f_max Violations](../plots/v6_blocks/04_violations.png)

| Technology | F (GW) | f_max (GW) | Excess | % Over |
|-----------|--------|-----------|--------|--------|
| CARGO_FUELCELL_LH2 | 152.134 | 100.000 | 52.134 | 52.1% |
| CCGT | 1.663 | 1.200 | 0.463 | 38.5% |
| COAL_US | 5.837 | 4.500 | 1.337 | 29.7% |
| HYDRO_DAM | 1.739 | 1.300 | 0.439 | 33.8% |
| HYDRO_RIVER | 2.902 | 2.100 | 0.802 | 38.2% |
| NUCLEAR | 5.928 | 2.800 | 3.128 | 111.7% |
| PV_ROOFTOP | 0.222 | 0.050 | 0.172 | 343.0% |
| PV_UTILITY | 0.056 | 0.020 | 0.036 | 178.2% |
| WIND_OFFSHORE | 0.147 | 0.030 | 0.117 | 388.5% |
| WIND_ONSHORE | 2.181 | 1.700 | 0.481 | 28.3% |

## Block Descriptions

- **Block 0 (Degeneracy)**: Cap 120 previously-unconstrained techs (f_max 1e15 → 5-100K)
- **Block 1 (Oil)**: LFO 150K→80K, JET_FUEL 15K→5K [historical realism]
- **Block 2 (Biomass)**: Wood tech fmin_perc forcing, GAS 28K→22K, COAL 50K→35K [calibration forcing]
- **Block 3 (Nuclear)**: URANIUM 100K→62K, NUCLEAR f_min=2.76 [historical realism]
- **Block 4 (Solar)**: PV_ROOFTOP 2→0.05, PV_UTILITY 1→0.02 [historical realism]
- **Block 5 (Coal)**: IND_BOILER_COAL fmin_perc 0.15, DHN_COGEN_COAL fmin_perc 0.20 [calibration forcing]
- **Block 6 (ElecMix)**: CCGT f_max 1.5→1.2, WIND_ONSHORE f_max 2.1→1.7 / f_min 1.5, WIND_OFFSHORE f_max 0.1→0.03 [mixed]

## Electricity Generation Mix

![Electricity Mix](../plots/v6_blocks/05_electricity_mix.png)

## Heating & Industrial Technologies

![Heating Mix](../plots/v6_blocks/06_heating_mix.png)

## Assessment vs Reality

![Block 6 vs Reality](../plots/v6_blocks/03_vs_reality.png)

![Gap Waterfall](../plots/v6_blocks/07_gap_waterfall.png)

| Metric | Reality (TWh) | v5_fperc | Block 6 | Direction |
|--------|-------------|---------|---------|-----------|
| WOOD | 105K | 3.0K | 50.6K | IMPROVED |
| Total Oil | 96K | 203.5K | 125.2K | IMPROVED |
| GAS | 25K | 28.0K | 22.0K | IMPROVED |
| COAL | 50K | 9.2K | 18.4K | IMPROVED |
| URANIUM | 65K | 80.0K | 195.8K | WORSE |