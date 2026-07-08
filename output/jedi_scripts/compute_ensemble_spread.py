#!/usr/bin/env python3
import numpy as np
import netCDF4

def _stack_members(filepaths, variable):
   data = []
   for fp in filepaths:
      with netCDF4.Dataset(fp) as ds:
         data.append(ds.variables[variable][:])
   return np.stack(data, axis=0)

def compute_ensemble_spread(filepaths, variable, ddof=1):
   data = _stack_members(filepaths, variable)
   return data.std(axis=0, ddof=ddof)

