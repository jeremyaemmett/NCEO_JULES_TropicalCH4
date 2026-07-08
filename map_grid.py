import xarray as xr
import pandas as pd
import numpy as np
import subprocess
#import readJULES
import shlex
import glob
import time
import os
from netCDF4 import Dataset
import matplotlib.pyplot as plt

def get_grid_info(nc_file):
    ds = xr.open_dataset(nc_file)

    lat = ds["latitude"].values
    lon = ds["longitude"].values

    dlat = float(abs(lat[1] - lat[0]))
    dlon = float(abs(lon[1] - lon[0]))

    return ds, lat, lon, dlat, dlon

def subset_land_points(ds, lat, lon, lat_bounds, lon_bounds, land_threshold=0.0):
    lat_min, lat_max = lat_bounds
    lon_min, lon_max = lon_bounds

    # --- longitude mask (handle wraparound) ---
    if lon_max < lon_min:
        lon_mask = (lon >= lon_min) | (lon <= lon_max)
    else:
        lon_mask = (lon >= lon_min) & (lon <= lon_max)

    # --- latitude mask ---
    lat_mask = (lat >= lat_min) & (lat <= lat_max)

    lat_idx = np.where(lat_mask)[0]
    lon_idx = np.where(lon_mask)[0]

    # --- extract land fraction ---
    land_frac = ds["land_sea_mask"].values

    # subset region
    sub_land = land_frac[np.ix_(lat_idx, lon_idx)]

    # --- apply land mask (THIS is the key bit) ---
    land_bool = sub_land > land_threshold

    # --- get coordinates of land points only ---
    sub_lat = lat[lat_idx]
    sub_lon = lon[lon_idx]

    lon2d, lat2d = np.meshgrid(sub_lon, sub_lat)

    land_lats = lat2d[land_bool]
    land_lons = lon2d[land_bool]

    return {
        "lat_all": sub_lat,
        "lon_all": sub_lon,
        "land_lats": land_lats,
        "land_lons": land_lons,
        "n_total": lat2d.size,
        "n_land": land_lats.size
    }

def scp_from_jasmin(local_directory, remote_directory_and_files):

    cmd = (
        "scp -r -v -o ProxyJump=jae35@login.jasmin.ac.uk "
        f"jae35@cylc2.jasmin.ac.uk:'{remote_directory_and_files}' "
        f"{shlex.quote(local_directory)}"
    )

    print(f"\n🔧 Running command:\n{cmd}\n")

    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print("\nFiles copied successfully\n")
    else:
        print(f"\nscp failed with exit code {result.returncode}\n")

task = 'map'

if task == 'scp':

    scp_from_jasmin('/Users/jae35/Desktop/JULES_test_data/assorted_files', 
                    '/gws/ssde/j25a/jules/eleanorburke/TRENDY/jules_ancils/landfrac_latlon2d_n96.nc')

    scp_from_jasmin('/Users/jae35/Desktop/JULES_test_data/assorted_files', 
                    '/home/users/jae35/ensemble/u-dk105_1_n4/app/jules/opt/rose-app-selpts.conf')

    scp_from_jasmin('/Users/jae35/Desktop/JULES_test_data/assorted_files', 
                    '/gws/ssde/j25a/jules/jae35/TRENDY/init_conds/example_init.selpts.nc')
    
    scp_from_jasmin('/Users/jae35/Desktop/JULES_test_data/assorted_files', 
                    '/gws/ssde/j25a/jules/jae35/TRENDY/init_conds/JULES-ES.vn7.6_CRUJRA2.4.spinup_01_P00.dump.17000101.0.nc.selpts.nc')
    
if task == 'map':

    file_path_0 = '/Users/jae35/Desktop/JULES_test_data/assorted_files/landfrac_latlon2d_n96.nc'
    file_path_1 = '/Users/jae35/Desktop/JULES_test_data/assorted_files/example_init.selpts.nc'
    file_path_2 = '/Users/jae35/Desktop/JULES_test_data/assorted_files/JULES-ES.vn7.6_CRUJRA2.4.spinup_01_P00.dump.17000101.0.nc.selpts.nc'

    #file_path_1 = '/Users/jae35/Desktop/qrparm.soil_n96.nc'
    #file_path_2 = '/Users/jae35/Desktop/qrparm.soil.dust.merge-plus-soil_kaolinitic_oxisols_ultisols_dominant_vn2.nc'

    nc0 = Dataset(file_path_0)
    latitude_0 = nc0.variables["latitude"][:]
    longitude_0 = nc0.variables["longitude"][:]

    ds, lat, lon, dlat, dlon = get_grid_info(file_path_0)
    land_frac = ds["land_sea_mask"].values
    result = subset_land_points(ds, lat, lon, (-24, 24), (0, 360), land_threshold=0.0)   # matches JULES default behaviour                    
    land_lats, land_lons = result['land_lats'], result['land_lons']
    
    lon2d, lat2d = np.meshgrid(longitude_0, latitude_0)

    nc1 = Dataset(file_path_1)
    latitude_1 = nc1.variables["latitude"][:]
    longitude_1 = nc1.variables["longitude"][:]

    nc2 = Dataset(file_path_2)
    latitude_2 = nc2.variables["latitude"][:]
    longitude_2 = nc2.variables["longitude"][:]

    n0 = lat2d.size
    n1 = len(latitude_1)
    n2 = len(latitude_2)

    fig, ax = plt.subplots(figsize=(15, 10))

    ax.scatter(longitude_1, latitude_1, s=6,
               label=f"{file_path_1} ({n1} points)")

    ax.scatter(longitude_2, latitude_2, s=3,
               label=f"{file_path_2} ({n2} points)")
    
    #ax.scatter(lon2d, lat2d, s=1,
    #           label=f"{file_path_0} ({n0} points)", marker = '.')
    
    #ax.scatter(land_lons, land_lats, s=1,
    #           label=f"{file_path_0} ({n0} points)", marker = 'x')

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_aspect("equal")

    # Legend ABOVE plot
    ax.legend(
        title="File source",
        loc="lower center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=1,
        frameon=False
    )

    # Make space for legend
    plt.subplots_adjust(top=0.85)

    plt.show()

    nc1.close()
    nc2.close()