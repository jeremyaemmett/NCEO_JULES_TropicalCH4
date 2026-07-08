import numpy as np
import netCDF4 as nc
from iso8601 import iso8601
from utc import utc
from compute_ensemble_mean import compute_ensemble_mean
from compute_ensemble_spread import compute_ensemble_spread

def compute_analysis_error(truth_initial_time, analysis_time, cycling_interval, ensemble_size, initial):
    
    variable = 'x'
    tag1 = utc(truth_initial_time)
    tag2 = utc(analysis_time)     
    tag3 = utc(analysis_time - cycling_interval)

    leadtime_truth = iso8601(analysis_time - truth_initial_time)
    leadtime_fcst = iso8601(cycling_interval)

    xt = nc.Dataset(f'Data/truth.fc.{tag1}.{leadtime_truth}.nc')[variable][:]
    xa_files = [f"Data/letkf.bgn.{str(i).zfill(6)}.an.{tag2}.nc" for i in range(1,ensemble_size+1)]
    xa_mean = nc.Dataset(f'Data/letkf.bgn.000000.an.{tag2}.nc')[variable][:]

    if initial:
        xb_files = [f"Data/forecast.ens.{i}.{tag3}.{leadtime_fcst}.nc" for i in range(1,ensemble_size+1)]
    else:
        xb_files = [f"Data/forecast.{i}.fc.{tag3}.{leadtime_fcst}.nc" for i in range(1,ensemble_size+1)]

    xb_mean = compute_ensemble_mean(xb_files, variable)

    erra = np.sqrt(np.mean((xa_mean - xt) ** 2))
    errb = np.sqrt(np.mean((xb_mean - xt) ** 2))  
    print(f"{'RMSE (background/analysis)':32}: {errb:.2f}/{erra:.2f} ({(erra - errb) / errb * 100:.2f}%)")

    xa_spread = np.mean(compute_ensemble_spread(xa_files, variable))
    xb_spread = np.mean(compute_ensemble_spread(xb_files, variable))
    print(f"{'Ensemble spread (background/analysis)':32}: {xb_spread:.2f}/{xa_spread:.2f} ({(xa_spread - xb_spread) / xb_spread * 100:.2f}%)")
    
    # stdb = np.std(xb_mean - xt)
    # stda = np.std(xa_mean - xt)
    # print(f"{'Error std (background/analysis)':32}: {stdb:.2f}/{stda:.2f} ({(stda - stdb) / stdb * 100:.2f}%)")
