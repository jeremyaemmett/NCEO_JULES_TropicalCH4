from os import listdir
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import plotPARAMS
import readJULES
import dataOPS

import numpy as np

def landpoints_to_grid(times, lats, lons, flxs):

    lats = np.asarray(lats)
    lons = np.asarray(lons)
    flxs = np.asarray(flxs)

    # define true grid axes from data (no assumptions)
    lat_vals = np.sort(np.unique(lats))
    lon_vals = np.sort(np.unique(lons))

    nlat = len(lat_vals)
    nlon = len(lon_vals)
    T, N = flxs.shape

    # map coordinate -> index
    lat_idx = {v: i for i, v in enumerate(lat_vals)}
    lon_idx = {v: j for j, v in enumerate(lon_vals)}

    # output grid
    grid = np.full((T, nlat, nlon), np.nan)

    # fill grid
    for n in range(N):
        i = lat_idx[lats[n]]
        j = lon_idx[lons[n]]
        grid[:, i, j] = flxs[:, n]

    return grid, lat_vals, lon_vals


def annual_total_flux(flux_grid, times, lat_grid, lon_grid):

    flux = np.squeeze(flux_grid) * 1e-9  # kg m-2 s-1

    lat_rad = np.deg2rad(lat_grid)

    year = int(str(times[0])[:4])

    start = np.datetime64(f"{year}-01-01")
    end = np.datetime64(f"{year+1}-01-01")

    months = np.arange(start, end, dtype="datetime64[M]")
    bounds = np.append(months, end)

    dt = np.diff(bounds).astype("timedelta64[s]").astype(float)

    R = 6371000.0

    # derive grid spacing from coordinates
    dlat = np.gradient(lat_rad)                      # (lat,)
    dlon = np.deg2rad(np.gradient(lon_grid))         # (lon,)

    #print('dlat, dlon: ', np.rad2deg(dlat), np.rad2deg(dlon))

    # cell area (lat x lon)
    area_lat = R**2 * np.abs(
        np.sin(lat_rad + dlat/2) - np.sin(lat_rad - dlat/2)
    )

    area = area_lat[:, None] * dlon[None, :]

    # integrate
    annual_kg = np.nansum(
        flux * dt[:, None, None] * area[None, :, :],
        axis=0
    )

    annual_Tg = annual_kg / 1e12

    return annual_Tg, np.nansum(annual_Tg)

print(sorted(f for f in listdir(plotPARAMS.data_path)
                        if f.endswith(".nc")))

for file_name in sorted(f for f in listdir(plotPARAMS.data_path)
                        if f.endswith(".nc")):

    file_path = plotPARAMS.data_path + file_name

    try:
        test = xr.open_dataset(file_path)
    except Exception as e:
        print("FAILED:", file_name)
        print(e)
        continue

    times, _, _, _ = readJULES.read_jules_m2(file_path, 'time')
    times = dataOPS.ensure_np_datetime(times)

    header = readJULES.read_jules_header(file_path)
    dimension_keys, variable_keys = list(header[0]), list(header[1])

    #print(test['fch4_wetl'].dims)

    if 'latitude' in variable_keys and 'longitude' in variable_keys:
        lat_string, lon_string = 'latitude', 'longitude'
    elif 'lat' in variable_keys and 'lon' in variable_keys:
        lat_string, lon_string = 'lat', 'lon'

    #print('Initial shapes:')
    #print(' Lat: ', test[lat_string].shape)
    #print(' Lon: ', test[lon_string].shape)
    #print(' Flx:' , test['fch4_wetl'].shape)

    flxs, _, _, _ = readJULES.read_jules_m2(file_path, 'fch4_wetl_npp')
    lats, _, _, _ = readJULES.read_jules_m2(file_path, lat_string)
    lons, _, _, _ = readJULES.read_jules_m2(file_path, lon_string)

    #print(flxs.shape)
    #print(lats.shape)
    #print(lons.shape)
    #print(' ')

    type = 'new'

    if flxs.shape[0] > 12:
        type = 'old'
        annual_totals = []
        for year in range(2000, 2009 + 1):

            mask = np.array([
                t.astype('datetime64[Y]').astype(int) + 1970 == year
                for t in times
            ])

            flxs_year = flxs[mask]
            times_year = times[mask]

            # old files are stored as time, lon, lat
            flxs_year = np.transpose(flxs_year, (0, 2, 1))

            #print(year, flxs_year.shape)

            #print('Corrected shapes:')
            #print(' Lat: ', lats.shape)
            #print(' Lon: ', lons.shape)
            #print(' Flx: ', flxs_year.shape)

            annual_Tg, global_total = annual_total_flux(
                flxs_year,
                times_year,
                lats,
                lons
            )

            annual_totals.append(global_total)

            #print(file_name, year, global_total)

        mean_total = np.mean(annual_totals)

        print('File: ', file_name, '    Mean annual total: ', mean_total)

        # skip the rest of the loop for old files
        continue

    if flxs.shape[1] == 1: flxs = np.squeeze(flxs)
    if lats.shape[0] == 1: lats = np.squeeze(lats)
    if lons.shape[0] == 1: lons = np.squeeze(lons)

    if len(flxs.shape) == 2: 
        flxs, lats, lons = landpoints_to_grid(times, lats, lons, flxs)

    #print('Corrected shapes:')
    #print(' Lat: ', lats.shape)
    #print(' Lon: ', lons.shape)
    #print(' Flx: ', flxs.shape)

    annual_Tg, global_total = annual_total_flux(
        flxs,
        times,
        lats,
        lons
    )

    Lon, Lat = np.meshgrid(lons, lats)

    plt.close()

    plt.figure(figsize=(12, 5))
    plt.pcolormesh(
        Lon,
        Lat,
        annual_Tg,
        shading="auto",
        cmap="viridis"
    )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Grid cell area")
    plt.colorbar(label="m²")
    #plt.show()

    print(file_name, global_total)