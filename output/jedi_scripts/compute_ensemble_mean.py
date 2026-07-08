#!/usr/bin/env python3
import numpy as np
import netCDF4

def _stack_members(filepaths, variable):
   data = []
   for fp in filepaths:
      with netCDF4.Dataset(fp) as ds:
         data.append(ds.variables[variable][:])
   return np.stack(data, axis=0)

def compute_ensemble_mean(filepaths, variable):
   data = _stack_members(filepaths, variable)
   return data.mean(axis=0)

# import numpy as np
# import netCDF4

# def compute_ensemble_mean(filepaths, variable):
#     x = []
#     for filepath in filepaths:
#        x.append(netCDF4.Dataset(filepath).variables[variable][:])
#     return(np.mean(x, axis=0))