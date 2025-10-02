import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import processJULES
import pandas as pd
import numpy as np
import plotPARAMS
import readJULES
import plotMAPS
import dataOPS
import sysOPS
import os


def make_zonal():

    files = sysOPS.discover_files(plotPARAMS.outp_path, '_zonalmean_tseries.txt')
    
    unique_end_directories = sysOPS.get_unique_end_directories(files)

    # Latitudes and Longitudes, their full arrays, converted to 2D meshgrids
    lats, lats_units, lats_long_name, lats_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, 'lat')
    lons, lons_units, lons_long_name, lons_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, 'lon')

    for unique_end_directory in unique_end_directories:

        zonal_file = sysOPS.discover_files(unique_end_directory, '_zonalmean_tseries.txt')[0]

        zonal_values = np.loadtxt(zonal_file).T  # shape (100, 12)
        zonal_values[zonal_values < 0.01] = np.nan

        # Assuming lats is your latitude array with length 100
        X, Y = np.meshgrid(np.arange(zonal_values.shape[1]) , lats)  # shape (100, 12)

        fig, ax = plt.subplots(figsize=(10, 5))  # Create figure and axis

        c = ax.contourf(X, Y, zonal_values, levels=20, cmap='magma')

        plot_title = "Zonal mean"
        ax.set_title(plot_title, loc='left', fontsize=18)
        ax.set_ylabel("Latitude", fontsize=18)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax.set_xticks(np.arange(zonal_values.shape[1]))
        ax.set_xticklabels(months, fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.grid(True)
        cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
        cb.set_label(dataOPS.cleanup_exponents('test'), fontsize=18)
        cb.ax.tick_params(labelsize=14)

        plt.tight_layout()
        plt.show()

        stop

        #print(zonal_file)
        #print(zonal_values)
        #print(np.shape(zonal_values))