from matplotlib.patches import Patch
import matplotlib.colors as mcolors
import cartopy.feature as cfeature
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.cm as cm
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
        areal_file = sysOPS.discover_files(unique_end_directory, '_arealmean_tseries.txt')[0]
        integ_file = sysOPS.discover_files(unique_end_directory, '_zonalintg_tseries.txt')[0]

        # Recover the variable name from the file path
        parts = os.path.normpath(zonal_file).split(os.sep)
        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(zonal_file))

        k_array, k_unit, k_long_name, k_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, key)

        zonal_values = np.loadtxt(zonal_file).T  # shape (100, 12)
        zonal_values_trimmed = np.copy(zonal_values)
        #zonal_values_trimmed[zonal_values_trimmed < 0.01] = np.nan

        areal_values = np.loadtxt(areal_file).T

        integ_values = np.loadtxt(integ_file).T
        integ_values_cumsum = np.cumsum(integ_values, axis=1)

        # Assuming lats is your latitude array with length 100
        X, Y = np.meshgrid(np.arange(zonal_values.shape[1]) , lats)  # shape (100, 12)

        fig, axs = plt.subplots(2, 2, figsize=(15, 10), gridspec_kw={'width_ratios': [2, 1]})
        ax1, ax2, ax3, ax4 = axs.ravel()  # Or axs.flatten()

        #c = ax1.contourf(X, Y, zonal_values_trimmed, levels=20, cmap='magma')
        c = ax1.pcolormesh(X, Y, zonal_values_trimmed, cmap='magma', shading='auto', alpha=0.85)

        plot_title = "  Zonal mean"
        ax1.set_title(plot_title, loc='left', fontsize=18, fontstyle='italic')
        ax1.set_ylabel("Latitude", fontsize=18)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax1.set_xticks(np.arange(zonal_values.shape[1]))
        ax1.set_xticklabels(months, fontsize=16)
        ax1.tick_params(axis='both', which='major', labelsize=14)
        #ax1.grid(True)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
        cb.set_label(dataOPS.cleanup_exponents(k_unit), fontsize=18)
        cb.ax.set_title(" ", fontsize=18)  
        cb.ax.tick_params(labelsize=14)
        for i in range(1, zonal_values.shape[1]):
            if (i)%3 == 0:
                ax1.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='black', linewidth=4.0)
                ax1.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='white', linewidth=2.0)

        ax_areal_mean = ax1.twinx()
        ax_areal_mean.plot(areal_values, linewidth=8.0, color='white')
        ax_areal_mean.plot(areal_values, linewidth=4.0, color='black')
        ax_areal_mean.tick_params(direction='in')

        #ax_areal_mean.step(range(len(areal_values)), areal_values, linewidth=4.0, color='white', where='mid')
        #ax_areal_mean.step(range(len(areal_values)), areal_values, linewidth=2.0, color='black', where='mid')

        plot_title = "  Seasonal mean"
        ax2.set_title(plot_title, loc='left', fontsize=18, fontstyle='italic')
        ax2.set_xlabel(dataOPS.cleanup_exponents(k_unit.replace("m-2", "")), fontsize=18)
        ax2.set_ylim([np.nanmin(lats), np.nanmax(lats)])
        ax2.tick_params(axis='both', which='major', labelsize=14)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        # cumulative sum along columns
        cumulative = np.cumsum(zonal_values, axis=1)  # shape: (lat, num_curves)

        # Get colormap
        num_layers = cumulative.shape[1]
        cmap = cm.get_cmap('viridis', num_layers)

        # Fill between subsequent layers
        for i in range(1, num_layers):
            ax2.plot(zonal_values[:, i], lats, color=cmap(i), label=f"Layer {i}")


        c = ax3.pcolormesh(X, Y, integ_values_cumsum, cmap='magma', shading='auto', alpha=0.85)

        plot_title = "  Zonally-integrated"
        ax3.set_title(plot_title, loc='left', fontsize=18, fontstyle='italic')
        ax3.set_ylabel("Latitude", fontsize=18)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax3.set_xticks(np.arange(zonal_values.shape[1]))
        ax3.set_xticklabels(months, fontsize=16)
        ax3.tick_params(axis='both', which='major', labelsize=14)
        #ax1.grid(True)
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
        cb.set_label(dataOPS.cleanup_exponents(k_unit), fontsize=18)
        cb.ax.set_title(" ", fontsize=18)  
        cb.ax.tick_params(labelsize=14)
        for i in range(1, zonal_values.shape[1]):
            if (i)%3 == 0:
                ax3.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='black', linewidth=4.0)
                ax3.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='white', linewidth=2.0)

        ax_zonal_intg = ax3.twinx()
        ax_zonal_intg.plot(np.nansum(integ_values_cumsum, axis=0), linewidth=8.0, color='white')
        ax_zonal_intg.plot(np.nansum(integ_values_cumsum, axis=0), linewidth=4.0, color='black')
        ax_zonal_intg.tick_params(direction='in')

        plot_title = "  Seasonal cumulative"
        ax4.set_title(plot_title, loc='left', fontsize=18, fontstyle='italic')
        ax4.set_xlabel(dataOPS.cleanup_exponents(k_unit.replace("m-2", "")), fontsize=18)
        ax4.set_ylim([np.nanmin(lats), np.nanmax(lats)])
        ax4.tick_params(axis='both', which='major', labelsize=14)
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)

        # cumulative sum along columns
        cumulative = np.cumsum(integ_values, axis=1)  # shape: (lat, num_curves)

        # Get colormap
        num_layers = cumulative.shape[1]
        cmap = cm.get_cmap('viridis', num_layers)

        # First fill: from zero to first layer
        ax4.fill_betweenx(lats, 0, cumulative[:, 0], color=cmap(0), label="Layer 0")

        # Fill between subsequent layers
        for i in range(1, num_layers):
            lower = cumulative[:, i - 1]
            upper = cumulative[:, i]
            ax4.fill_betweenx(lats, lower, upper, color=cmap(i), label=f"Layer {i}")
            if (i+1)%3 == 0 and i != num_layers-1: ax4.plot(upper, lats, color='black', linestyle='-', linewidth = 3.0)
            if (i+1)%3 == 0 and i != num_layers-1: ax4.plot(upper, lats, color='white', linestyle='-', linewidth = 1.0)
            #if i == 5: ax2.plot(upper, lats, color='gray', linestyle='-', linewidth = 2.0)

        legend_handles = [Patch(facecolor=cmap(i), label=months[i]) for i in range(num_layers)]
        ax4.legend(handles=legend_handles, title=" ", loc='upper left', fontsize=14, title_fontsize=16, ncol=1, borderaxespad=0, bbox_to_anchor=(1.05, 1), frameon=False)

        plt.tight_layout()
        #plt.show()

        plt.savefig(unique_end_directory + '/' + 'complete_zonalmeans.png', dpi=300, bbox_inches='tight')
        plt.close()


def make_animated_zonal():

    files = sysOPS.discover_files(plotPARAMS.outp_path, '_zonalmean_tseries.txt')
    
    unique_end_directories = sysOPS.get_unique_end_directories(files)

    # Latitudes and Longitudes, their full arrays, converted to 2D meshgrids
    lats, lats_units, lats_long_name, lats_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, 'lat')
    lons, lons_units, lons_long_name, lons_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, 'lon')

    for unique_end_directory in unique_end_directories:

        zonal_file = sysOPS.discover_files(unique_end_directory, '_zonalmean_tseries.txt')[0]

        # Recover the variable name from the file path
        parts = os.path.normpath(zonal_file).split(os.sep)
        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(zonal_file))

        k_array, k_unit, k_long_name, k_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, key)

        zonal_values = np.loadtxt(zonal_file).T  # shape (100, 12)
        zonal_values_trimmed = np.copy(zonal_values)
        zonal_values_trimmed[zonal_values_trimmed < 0.01] = np.nan

        cumulative = np.cumsum(zonal_values, axis=1)  # shape: (lat, num_curves)

        # Assuming lats is your latitude array with length 100
        X, Y = np.meshgrid(np.arange(zonal_values.shape[1]) , lats)  # shape (100, 12)

        for m in range(0, 12):

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={'width_ratios': [2, 1]})

            ax2.fill_betweenx(lats, 0, cumulative[:, -1], color='gainsboro')

            #c = ax1.contourf(X, Y, zonal_values_trimmed, levels=20, cmap='magma')
            c = ax1.pcolormesh(X, Y, zonal_values_trimmed, cmap='magma', shading='auto')

            plot_title = "  Zonal mean"
            ax1.set_title(plot_title, loc='left', fontsize=18, fontstyle='italic')
            #ax1.set_ylabel("Latitude", fontsize=18)
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            ax1.set_xticks(np.arange(zonal_values.shape[1]))
            ax1.set_xticklabels(months, fontsize=16)
            ax1.tick_params(axis='both', which='major', labelsize=14)
            #ax1.grid(True)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
            cb.set_label(dataOPS.cleanup_exponents(k_unit), fontsize=18)
            cb.ax.set_title(" ", fontsize=18)  
            cb.ax.tick_params(labelsize=14)
            ax1.plot([m-0.5, m+0.5, m+0.5, m-0.5, m-0.5], [np.nanmin(lats), np.nanmin(lats), np.nanmax(lats), np.nanmax(lats), np.nanmin(lats)], linestyle='-', color='red', linewidth=6.0)
            for i in range(1, zonal_values.shape[1]):
                if (i)%3 == 0:
                    ax1.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='black', linewidth=4.0)
                    ax1.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='white', linewidth=2.0)

            plot_title = "  Seasonal cummulative / 5°Lat."
            ax2.set_title(plot_title, loc='left', fontsize=18, fontstyle='italic')
            ax2.set_xlabel(dataOPS.cleanup_exponents(k_unit.replace("m-2", "")), fontsize=18)
            ax2.set_ylim([np.nanmin(lats), np.nanmax(lats)])
            ax2.tick_params(axis='both', which='major', labelsize=14)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)

            # cumulative sum along columns
            ax2.set_xlim([0.0, np.nanmax(cumulative[:,-1])])

            # Get colormap
            num_layers = cumulative.shape[1]
            cmap = cm.get_cmap('viridis', num_layers)

            # First fill: from zero to first layer
            ax2.fill_betweenx(lats, 0, cumulative[:, 0], color=cmap(0), label="Layer 0")

            # Fill between subsequent layers
            for i in range(1, m):
                lower = cumulative[:, i - 1]
                upper = cumulative[:, i]
                ax2.fill_betweenx(lats, lower, upper, color=cmap(i), label=f"Layer {i}")
                if (i+1)%3 == 0 and i != num_layers-1: ax2.plot(upper, lats, color='black', linestyle='-', linewidth = 3.0)
                if (i+1)%3 == 0 and i != num_layers-1: ax2.plot(upper, lats, color='white', linestyle='-', linewidth = 1.0)
                #if i == 5: ax2.plot(upper, lats, color='gray', linestyle='-', linewidth = 2.0)

            legend_handles = [Patch(facecolor=cmap(i), label=months[i]) for i in range(num_layers)]
            ax2.legend(handles=legend_handles, title=" ", loc='upper left', fontsize=14, title_fontsize=16, ncol=1, borderaxespad=0, bbox_to_anchor=(1.05, 1), frameon=False)

            plt.tight_layout()
            #plt.show()

            plt.savefig(unique_end_directory + '/' + str(m) + '_' + '_zonalmeans.png', dpi=300, bbox_inches='tight')
            print('saved to: ', unique_end_directory + '/' + str(m) + '_' + '_zonalmeans.png')
            plt.close()

    #miscOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/' + unique_end_directory.split('/')[-1] + '_animation.gif', duration=150, smooth=True, exclude_substr='plot_')
    sysOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/zonal_animation.gif', duration=150, smooth=True, exclude_substr=['plot_', 'complete', 'map', 'tseries'])

    [os.remove(os.path.join(dp, f)) for dp, dn, fn in os.walk(unique_end_directory) for f in fn if f.endswith('__zonalmeans.png')]