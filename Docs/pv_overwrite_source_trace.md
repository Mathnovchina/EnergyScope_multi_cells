# PV_UTILITY and PV_ROOFTOP f_max Overwrite Source Trace

## Function Call Path

1. **main()** ([scripts/run_calib_manual.py](scripts/run_calib_manual.py))
   - Initializes model, reads data.
2. **my_model.init_regions()**
   - Calls **Region.read_tech()** ([esmc/utils/region.py](esmc/utils/region.py)), loading Technologies.csv into memory.
3. **apply_patches()** (if specified)
   - Updates in-memory DataFrames.
4. **apply_fi2017_disabling()**
   - Sets f_max=0 for a list of technologies (not PV).
5. **Temporal aggregation and .dat file generation**
   - **my_model.print_data()** calls [esmc/preprocessing/dat_print.py](esmc/preprocessing/dat_print.py) functions to write .dat files.
6. **Overwrite occurs in compute_cell_w()** ([esmc/utils/region.py](esmc/utils/region.py#L228-L231)):
   - `tot_ts[prod_simple] = tot_ts[prod_simple] * self.data['Technologies'].loc[prod_simple,'f_max']`
   - `for t,l in res_mult_params.items(): tot_ts[t] = tot_ts[t] * self.data['Technologies'].loc[l,'f_max'].sum()`
   - This multiplies time series by the in-memory f_max values, which are set from Technologies.csv or patches.

## Evidence Table

| Stage                | Source File/Function                | Value for PV_UTILITY | Value for PV_ROOFTOP | Notes                          |
|----------------------|-------------------------------------|----------------------|----------------------|---------------------------------|
| Disk                 | Data/2017/FI/Technologies.csv       | 5.0                  | 2.0                  | Direct edit, correct values     |
| In-memory (post-init)| Region.read_tech()                  | 5.0                  | 2.0                  | Loaded from disk                |
| In-memory (pre-dat)  | apply_patches()/apply_fi2017_disabling | 5.0                  | 2.0                  | No patch, disabling not applied |
| .dat generation      | compute_cell_w()/print_data()        | 0.1                  | 0.3                  | Overwritten by later code       |

## Classification

- The overwrite is classified as **C: later overwrite in pipeline (after FI merge, before .dat generation)**.
- The exact overwrite occurs in `compute_cell_w()` ([esmc/utils/region.py](esmc/utils/region.py#L228-L231)), where the f_max values used are those currently in memory, which may have been modified by earlier steps or patch files.

## Summary

- The root cause is a later overwrite in the pipeline, not a disk or patch error.
- The function call path and evidence table above provide strict traceability.
