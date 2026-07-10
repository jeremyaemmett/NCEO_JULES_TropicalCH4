from matplotlib.patches import Rectangle
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
import matplotlib.colors as mcolors
import matplotlib.colors as mcolor
import cartopy.feature as cfeature
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib import colors
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


def make_zonal(data_path, outp_path, file_name, year):

    files = sysOPS.discover_files(outp_path, '_zonalmean_tseries.txt')
    
    unique_end_directories = sysOPS.get_unique_end_directories(files)

    header = readJULES.read_jules_header(data_path + file_name)
    dimension_keys, variable_keys = list(header[0]), list(header[1])

    if 'latitude' in variable_keys and 'longitude' in variable_keys: lat_string, lon_string = 'latitude', 'longitude'
    if 'lat' in variable_keys and 'lon' in variable_keys: lat_string, lon_string = 'lat', 'lon'

    if 'lat' in dimension_keys and 'lon' in dimension_keys: lat_key, lon_key = 'lat', 'lon'
    if 'y' in dimension_keys and 'x' in dimension_keys: lat_key, lon_key = 'y', 'x'

    # Latitudes and Longitudes, their full arrays, converted to 2D meshgrids
    lats, lats_units, lats_long_name, lats_dims = readJULES.read_jules_m2(data_path + file_name, lat_string)
    lons, lons_units, lons_long_name, lons_dims = readJULES.read_jules_m2(data_path + file_name, lon_string)

    #coords_are_2d = len(np.shape(lats)) == 2
    #if coords_are_2d: lats, lons = lats[:, 0], lons[0, :]

    lat_spacing = np.diff(np.unique(lats))[0]

    for unique_end_directory in unique_end_directories:
        #print(unique_end_directory)
        zonal_file = sysOPS.discover_files(unique_end_directory, '_zonalmean_tseries.txt')[0]
        areal_file = sysOPS.discover_files(unique_end_directory, '_arealmean_tseries.txt')[0]
        integ_file = sysOPS.discover_files(unique_end_directory, '_zonalintg_tseries.txt')[0]
        #print(integ_file)

        # Recover the variable name from the file path
        parts = os.path.normpath(zonal_file).split(os.sep)
        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(zonal_file))

        k_array, k_unit, k_long_name, k_dims = readJULES.read_jules_m2(data_path + file_name, key)

        #print('k_unit: ', k_unit, ' ', dataOPS.check_if_rate(k_unit))

        is_rate = dataOPS.check_if_rate(k_unit)

        zonal_values = np.loadtxt(zonal_file).T  # shape (100, 12)
        zonal_values_trimmed = np.copy(zonal_values)
        #zonal_values_trimmed[zonal_values_trimmed < 0.01] = np.nan

        areal_values = np.loadtxt(areal_file).T

        integ_values = np.loadtxt(integ_file).T

        integ_values_cumsum = np.cumsum(integ_values, axis=1)

        if integ_values.ndim == 1:
            integ_values_cumsum = integ_values  # 1D, just return as-is
        elif integ_values.ndim == 2:
            integ_values_cumsum = np.cumsum(integ_values, axis=1)  # sum along time, sometimes need axis=0
        else:
            raise ValueError(f"Unexpected shape: {integ_values.shape}")

        # Assuming lats is your latitude array with length 100
        #print(lats)
        #print(np.unique(lats))
        X, Y = np.meshgrid(np.arange(12), np.unique(lats))  # shape (100, 12)
        #print(X)
        #print(Y)

        if is_rate:
            fig, axs = plt.subplots(2, 2, figsize=(17.50, 9.00), gridspec_kw={'width_ratios': [2, 1]})
            ax1, ax2, ax3, ax4 = axs.ravel()  # Or axs.flatten()
        else:
            fig, axs = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={'width_ratios': [2, 1]})
            ax1, ax2 = axs.ravel()  # Or axs.flatten()

        #c = ax1.contourf(X, Y, zonal_values_trimmed, levels=20, cmap='magma')
        #c = ax1.pcolormesh(X, Y, zonal_values_trimmed, cmap='magma', shading='auto', alpha=0.85)

        norm = mcolors.Normalize(vmin=np.nanmin(zonal_values_trimmed),
                                    vmax=np.nanmax(zonal_values_trimmed))
        rgba_cmap = plt.get_cmap('magma')

        rgba_colors = rgba_cmap(norm(zonal_values_trimmed))
        rgba_colors[..., -1] = norm(zonal_values_trimmed)  # alpha proportional to value

        #X, Y = np.meshgrid(np.arange(zonal_values_trimmed.shape[1]),
        #                np.unique(lats))

        c = ax1.pcolormesh(X, Y, rgba_colors, shading='auto')
        land_color = "#f5e6c8"  # your land color
        alpha = 1
        land_rgba = mcolors.to_rgba(land_color, alpha=alpha)
        ax1.set_facecolor(land_rgba)

        # Get colormap
        num_layers = zonal_values.shape[1]
        cmap = cm.get_cmap('managua', num_layers)
        cmap = cm.get_cmap('rainbow', num_layers)
        #ax.set_title(dataOPS.remove_parenthetical_substrings(r"$\bf{" + variable_name_fix + "}$" + '\n' + variable_long_name), loc='left', fontsize=12)
        plot_title = " \n  Zonal (fill) and full-region (line)\n  means"
        ax1.set_title(r"$\mathbf{Monthly\ means}$" + "\n" + "zonal (fill) and full-region (line)", loc='left', fontsize=30)
        #ax1.set_title(plot_title, loc='left', fontsize=16, fontstyle='italic')
        ax1.set_ylabel("Latitude", fontsize=26)
        months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
        #print('shape: ', zonal_values.shape)
        ax1.set_xticks(np.arange(zonal_values.shape[1]))
        ax1.set_xticklabels(months, fontsize=20)

        ymin = 5 * (lats.min() // 5)
        ymax = 5 * ((lats.max() + 4) // 5)  # ensures ceiling to next multiple of 5
        yticks = range(int(ymin), int(ymax)+1, 10)
        ax1.set_ylim(ymin, ymax)
        ax1.set_yticks(yticks)
        ax1.set_yticklabels([f"{y}°" for y in yticks], fontsize=24)

        cb_ax = ax1.inset_axes([1.15, 0.0, 0.04, 1.0])  # left, bottom, width, height
        # Draw a rectangle with land color in the full colorbar area
        cb_ax.add_patch(
            plt.Rectangle(
                (0, 0), 1, 1,                 # fill full axes
                transform=cb_ax.transAxes,     # axes coords
                color="#f5e6c8",               # land color
                zorder=0, alpha = 1
            )
        )

        # Now create the ScalarMappable with your alpha-aware colormap
        N = 256
        colors2 = rgba_cmap(np.linspace(0, 1, N))
        colors2[:, -1] = np.linspace(0, 1, N)  # alpha ramp
        alpha_cmap = mcolors.ListedColormap(colors2)
        sm = cm.ScalarMappable(cmap=alpha_cmap, norm=norm)
        sm.set_array(rgba_colors)

        # Overlay the actual colorbar on top of the land rectangle
        cb = plt.colorbar(sm, cax=cb_ax)
        cb.ax.tick_params(labelsize=16)

        ###


        for i in range(num_layers):
            rect = Rectangle(
                (i - 0.5, -0.18),   # start at left edge of each month bin
                1.0,                # width = one month
                0.155,               # height of strip
                transform=ax1.get_xaxis_transform(),  # x=data, y=axes
                color=cmap(i),
                alpha=0.45,
                clip_on=False,
                zorder=0
            )
            ax1.add_patch(rect)

        # Apply colors
        for i, label in enumerate(ax1.get_xticklabels()):
            label.set_color('black')
            #label.set_fontweight('bold')
            #label.set_path_effects([
            #    pe.Stroke(linewidth=5.0, foreground='white'),
            #    pe.Normal()])
            label.set_rotation(0)
            label.set_ha('center')  # important for clean alignment
            label.set_y(-0.015)  # default ~0, negative moves down
            if label.get_text() == 'J':
                label.set_y(-0.004) 
            label.set_fontname('DejaVu Sans')
            label.set_fontstyle('italic')

        ax1.tick_params(axis='both', which='major', labelsize=20)
        #ax1.grid(True)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        #cb = plt.colorbar(c, orientation='vertical', pad=0.1, shrink=0.8, fraction=0.05)
        cb.set_label(' \n' + dataOPS.cleanup_exponents(k_unit) + '\n', fontsize=26)
        cb.ax.set_title(" ", fontsize=22)  
        cb.ax.tick_params(labelsize=22)
        #for i in range(1, zonal_values.shape[1]):
        #    if (i)%3 == 0:
        #        ax1.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='black', linewidth=4.0)
        #        ax1.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='white', linewidth=2.0)

        ax_areal_mean = ax1.twinx()
        ax_areal_mean.plot(areal_values, linewidth=6.0, color='white')
        ax_areal_mean.plot(areal_values, linewidth=4.0, color='black')
        ax_areal_mean.tick_params(direction='in', labelsize=24)

        #ax_areal_mean.step(range(len(areal_values)), areal_values, linewidth=4.0, color='white', where='mid')
        #ax_areal_mean.step(range(len(areal_values)), areal_values, linewidth=2.0, color='black', where='mid')

        plot_title = "Sliced means"
        #ax2.set_title(plot_title, loc='left', fontsize=16, fontstyle='italic')
        ax2.set_title(r"$\mathbf{Sliced\ means}$" + "\n" + "by month (color)", loc='left', fontsize=30)
        ax2.set_xlabel(dataOPS.cleanup_exponents(k_unit), fontsize=20)
        ax2.set_ylim([np.nanmin(lats), np.nanmax(lats)])
        ax2.tick_params(axis='both', which='major', labelsize=20)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.set_facecolor('none')
        ax2.patch.set_alpha(0)
        ax2.set_yticks(yticks)
        ax2.set_yticklabels([f"{y}°" for y in yticks])

        # cumulative sum along columns
        cumulative = np.cumsum(zonal_values, axis=1)  # shape: (lat, num_curves)

        # Fill between subsequent layers
        for i in range(0, num_layers):
            ax2.plot(zonal_values[:, i], np.unique(lats), color=cmap(i), label=f"Layer {i}", linewidth=4.0, alpha=0.45)


        if is_rate:

            integ_values_cumsum = 1e-9 * integ_values_cumsum

            norm = mcolors.Normalize(vmin=np.nanmin(integ_values_cumsum),
                                    vmax=np.nanmax(integ_values_cumsum))
            rgba_cmap = plt.get_cmap('magma')

            rgba_colors = rgba_cmap(norm(integ_values_cumsum))
            rgba_colors[..., -1] = norm(integ_values_cumsum)  # alpha proportional to value

            X, Y = np.meshgrid(np.arange(integ_values_cumsum.shape[1]),
                            np.unique(lats))

            c = ax3.pcolormesh(X, Y, rgba_colors, shading='auto')

            land_color = "#f5e6c8"  # your land color
            alpha = 1
            land_rgba = mcolors.to_rgba(land_color, alpha=alpha)
            ax3.set_facecolor(land_rgba)

            plot_title = " \n  Zonal (fill) and full-region (line)\n  cumulative"
            #ax3.set_title(plot_title, loc='left', fontsize=16, fontstyle='italic')
            ax3.set_title(r"$\mathbf{Monthly\ cumulative}$" + "\n" + "zonal (fill) and full-region (line)", loc='left', fontsize=30)
            ax3.set_ylabel("Latitude", fontsize=26)
            months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
            # Set ticks first
            ax3.set_xticks(np.arange(len(months)))
            ax3.set_xticklabels(months, fontsize=20)  # do NOT pass fontsize here

            # Add month-colored rectangles
            for i in range(num_layers):
                rect = Rectangle(
                    (i - 0.5, -0.18),  # align with tick
                    1.0,               # width = 1 month
                    0.155,              # height of strip
                    transform=ax3.get_xaxis_transform(),
                    color=cmap(i),
                    alpha=0.45,
                    clip_on=False,
                    zorder=0
                )
                ax3.add_patch(rect)

            # Now customize tick labels
            for i, label in enumerate(ax3.get_xticklabels()):
                label.set_color('black')
                #label.set_fontweight('bold')
                #label.set_path_effects([
                #    pe.Stroke(linewidth=5.0, foreground='white'),
                #    pe.Normal()])
                label.set_rotation(0)
                label.set_ha('center')  # important for clean alignment
                label.set_y(-0.015)  # default ~0, negative moves down
                if label.get_text() == 'J':
                    label.set_y(-0.004) 
                label.set_fontname('DejaVu Sans')
                label.set_fontstyle('italic')

            ax3.tick_params(axis='both', which='major', labelsize=20)
            #ax1.grid(True)
            ax3.spines['top'].set_visible(False)
            ax3.spines['right'].set_visible(False)

            ymin = 5 * (lats.min() // 5)
            ymax = 5 * ((lats.max() + 4) // 5)  # ensures ceiling to next multiple of 5
            yticks = range(int(ymin), int(ymax)+1, 10)
            ax3.set_ylim(ymin, ymax)
            ax3.set_yticks(yticks)
            ax3.set_yticklabels([f"{y}°" for y in yticks])

            cb_ax = ax3.inset_axes([1.15, 0.0, 0.04, 1.0])   # left, bottom, width, height
            # Draw a rectangle with land color in the full colorbar area
            cb_ax.add_patch(
                plt.Rectangle(
                    (0, 0), 1, 1,                 # fill full axes
                    transform=cb_ax.transAxes,     # axes coords
                    color="#f5e6c8",               # land color
                    zorder=0, alpha = 1
                )
            )

            # Now create the ScalarMappable with your alpha-aware colormap
            N = 256
            colors2 = rgba_cmap(np.linspace(0, 1, N))
            colors2[:, -1] = np.linspace(0, 1, N)  # alpha ramp
            alpha_cmap = mcolors.ListedColormap(colors2)
            sm = cm.ScalarMappable(cmap=alpha_cmap, norm=norm)
            sm.set_array(rgba_colors)

            # Overlay the actual colorbar on top of the land rectangle
            cb = plt.colorbar(sm, cax=cb_ax)
            cb.ax.tick_params(labelsize=22)

            ###

            #cb = plt.colorbar(c, orientation='vertical', pad=0.1, shrink=0.8, fraction=0.05)
            #cb.set_label(dataOPS.cleanup_exponents(k_unit), fontsize=18)
            cb.set_label(dataOPS.cleanup_exponents("\n kg") + ' / ' + str(lat_spacing) + '\u00B0' + ' lat', fontsize=26)
            cb.ax.set_title(" ", fontsize=22)  
            cb.ax.tick_params(labelsize=22)
            cb.ax.yaxis.get_offset_text().set_fontsize(14)
            #for i in range(1, zonal_values.shape[1]):
            #    if (i)%3 == 0:
            #        ax3.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='black', linewidth=4.0)
            #        ax3.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='white', linewidth=2.0)

            ax_zonal_intg = ax3.twinx()
            ax_zonal_intg.plot(np.nansum(integ_values_cumsum, axis=0), linewidth=6.0, color='white')
            ax_zonal_intg.plot(np.nansum(integ_values_cumsum, axis=0), linewidth=4.0, color='black')
            ax_zonal_intg.tick_params(direction='in', labelsize=24)
            ax_zonal_intg.yaxis.get_offset_text().set_fontsize(24)

            plot_title = "Collapsed cumulative"
            #ax4.set_title(plot_title, loc='left', fontsize=16, fontstyle='italic')
            ax4.set_title(r"$\mathbf{Stacked\ cumulative}$" + "\n" + "by month (color)", loc='left', fontsize=30)
            #ax4.set_xlabel(dataOPS.cleanup_exponents(k_unit.replace("m-2", "")), fontsize=18)
            ax4.set_xlabel(dataOPS.cleanup_exponents("kg"), fontsize=18)
            ax4.set_ylim([np.nanmin(lats), np.nanmax(lats)])
            ax4.tick_params(axis='both', which='major', labelsize=20)
            ax4.spines['top'].set_visible(False)
            ax4.spines['right'].set_visible(False)
            ax4.set_facecolor('none')
            ax4.patch.set_alpha(0)

            # cumulative sum along columns
            cumulative = 1e-9 * np.cumsum(integ_values, axis=1)  # shape: (lat, num_curves)

            # Get colormap
            num_layers = cumulative.shape[1]
            cmap = cm.get_cmap('managua', num_layers)
            cmap = cm.get_cmap('rainbow', num_layers)

            # First fill: from zero to first layer
            ax4.fill_betweenx(np.unique(lats), 0, cumulative[:, 0], color=cmap(0), label="Layer 0", alpha=0.45)

            # Fill between subsequent layers
            for i in range(1, num_layers):
                lower = cumulative[:, i - 1]
                upper = cumulative[:, i]
                ax4.fill_betweenx(np.unique(lats), lower, upper, color=cmap(i), label=f"Layer {i}", alpha=0.45)
                #if (i+1)%3 == 0 and i != num_layers-1: ax4.plot(upper, lats, color='black', linestyle='-', linewidth = 3.0)
                #if (i+1)%3 == 0 and i != num_layers-1: ax4.plot(upper, lats, color='white', linestyle='-', linewidth = 1.0)
                #if i == 5: ax2.plot(upper, lats, color='gray', linestyle='-', linewidth = 2.0)

        #legend_handles = [Patch(facecolor=cmap(i), label=months[i]) for i in range(num_layers)]
        #ax2.legend(handles=legend_handles, title=" ", loc='upper left', fontsize=14, title_fontsize=16, ncol=1, borderaxespad=0, bbox_to_anchor=(1.05, 1), frameon=False)

        ax2.set_ylim([np.nanmin(lats), np.nanmax(lats)])
        ax2.tick_params(axis='both', which='major', labelsize=20)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.set_facecolor(colors.to_rgba('gainsboro', alpha=0.5))

        # <-- remove y-ticks and labels here
        #ax2.set_yticks([])

        # ... same for ax4
        ax4.set_ylim([np.nanmin(lats), np.nanmax(lats)])
        ax4.tick_params(axis='both', which='major', labelsize=20)
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.set_facecolor(colors.to_rgba('gainsboro', alpha=0.5))
        ax4.set_yticks(yticks)
        ax4.set_yticklabels([f"{y}°" for y in yticks])
        #ax4.set_ylabel(' \n \n \n')

        plt.tight_layout()
        #plt.show()

        fig.patch.set_alpha(0)  # figure background transparent

        plt.savefig(unique_end_directory + '/' + 'complete_zonalmeans.png', dpi=300, bbox_inches='tight')
        plt.close()


def make_animated_zonal():

    files = sysOPS.discover_files(outp_path, '_zonalmean_tseries.txt')
    
    unique_end_directories = sysOPS.get_unique_end_directories(files)

    # Latitudes and Longitudes, their full arrays, converted to 2D meshgrids
    lats, lats_units, lats_long_name, lats_dims = readJULES.read_jules_m2(data_path + file_name, 'lat')
    lons, lons_units, lons_long_name, lons_dims = readJULES.read_jules_m2(data_path + file_name, 'lon')

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

        k_array, k_unit, k_long_name, k_dims = readJULES.read_jules_m2(data_path + file_name, key)

        zonal_values = np.loadtxt(zonal_file).T  # shape (100, 12)
        zonal_values_trimmed = np.copy(zonal_values)
        zonal_values_trimmed[zonal_values_trimmed < 0.01] = np.nan

        cumulative = np.cumsum(zonal_values, axis=1)  # shape: (lat, num_curves)

        # Assuming lats is your latitude array with length 100
        X, Y = np.meshgrid(np.arange(zonal_values.shape[1]) , lats)  # shape (100, 12)

        for m in range(0, 12):

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 5.0), gridspec_kw={'width_ratios': [3, 2]})

            ax2.fill_betweenx(lats, 0, cumulative[:, -1], color='gainsboro')

            norm = mcolors.Normalize(vmin=np.nanmin(zonal_values_trimmed),
                                    vmax=np.nanmax(zonal_values_trimmed))
            rgba_cmap = plt.get_cmap('magma')

            rgba_colors = rgba_cmap(norm(zonal_values_trimmed))
            rgba_colors[..., -1] = norm(zonal_values_trimmed)  # alpha proportional to value

            #X, Y = np.meshgrid(np.arange(zonal_values_trimmed.shape[1]),
            #                np.unique(lats))

            c = ax1.pcolormesh(X, Y, rgba_colors, shading='auto')

            #c = ax1.contourf(X, Y, zonal_values_trimmed, levels=20, cmap='magma')
            #c = ax1.pcolormesh(X, Y, zonal_values_trimmed, cmap='magma', shading='auto')

            plot_title = "  Zonal means"
            ax1.set_title(plot_title, loc='left', fontsize=18, fontstyle='italic')
            #ax1.set_ylabel("Latitude", fontsize=18)
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            ax1.set_xticks(np.arange(zonal_values.shape[1]))
            ax1.set_xticklabels(months, fontsize=20)
            ax1.tick_params(axis='both', which='major', labelsize=14)
            #ax1.grid(True)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)

            cb_ax = ax1.inset_axes([1.15, 0.1, 0.04, 0.8])  # left, bottom, width, height
            # Draw a rectangle with land color in the full colorbar area
            cb_ax.add_patch(
                plt.Rectangle(
                    (0, 0), 1, 1,                 # fill full axes
                    transform=cb_ax.transAxes,     # axes coords
                    color="#f5e6c8",               # land color
                    zorder=0, alpha = 0.5
                )
            )

            # Now create the ScalarMappable with your alpha-aware colormap
            N = 256
            colors2 = rgba_cmap(np.linspace(0, 1, N))
            colors2[:, -1] = np.linspace(0, 1, N)  # alpha ramp
            alpha_cmap = mcolors.ListedColormap(colors2)
            sm = cm.ScalarMappable(cmap=alpha_cmap, norm=norm)
            sm.set_array(rgba_colors)

            # Overlay the actual colorbar on top of the land rectangle
            cb = plt.colorbar(sm, cax=cb_ax)
            cb.ax.tick_params(labelsize=16)

            ###

            ax1.plot([m-0.5, m+0.5, m+0.5, m-0.5, m-0.5], [np.nanmin(lats), np.nanmin(lats), np.nanmax(lats), np.nanmax(lats), np.nanmin(lats)], linestyle='-', color='red', linewidth=6.0)
            for i in range(1, zonal_values.shape[1]):
                if (i)%3 == 0:
                    ax1.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='black', linewidth=4.0)
                    ax1.plot([i-0.5, i-0.5], [np.nanmin(lats), np.nanmax(lats)], linestyle='-', color='white', linewidth=2.0)

            plot_title = "  Seasonal cumulative / 5°Lat."
            ax2.set_title(plot_title, loc='left', fontsize=20, fontstyle='italic')
            ax2.set_xlabel(dataOPS.cleanup_exponents(k_unit.replace("m-2", "")), fontsize=20)
            ax2.set_ylim([np.nanmin(lats), np.nanmax(lats)])
            ax2.tick_params(axis='both', which='major', labelsize=20)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)

            # cumulative sum along columns
            ax2.set_xlim([0.0, np.nanmax(cumulative[:,-1])])

            # Get colormap
            num_layers = cumulative.shape[1]
            cmap = cm.get_cmap('managua', num_layers)

            # First fill: from zero to first layer
            ax2.fill_betweenx(lats, 0, cumulative[:, 0], color=cmap(0), label="Layer 0")

            # Fill between subsequent layers
            for i in range(1, m):
                lower = cumulative[:, i - 1]
                upper = cumulative[:, i]
                ax2.fill_betweenx(lats, lower, upper, color=cmap(i), label=f"Layer {i}")
                #if (i+1)%3 == 0 and i != num_layers-1: ax2.plot(upper, lats, color='black', linestyle='-', linewidth = 3.0)
                #if (i+1)%3 == 0 and i != num_layers-1: ax2.plot(upper, lats, color='white', linestyle='-', linewidth = 1.0)
                #if i == 5: ax2.plot(upper, lats, color='gray', linestyle='-', linewidth = 2.0)

            legend_handles = [Patch(facecolor=cmap(i), label=months[i]) for i in range(num_layers)]
            ax2.legend(handles=legend_handles, title=" ", loc='upper left', fontsize=14, title_fontsize=16, ncol=1, borderaxespad=0, bbox_to_anchor=(1.05, 1), frameon=False, columnspacing=2.0)

            plt.tight_layout()
            #plt.show()

            plt.savefig(unique_end_directory + '/' + str(m) + '_' + '_zonalmeans.png', dpi=300, bbox_inches='tight')
            print('saved to: ', unique_end_directory + '/' + str(m) + '_' + '_zonalmeans.png')
            plt.close()

    #miscOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/' + unique_end_directory.split('/')[-1] + '_animation.gif', duration=150, smooth=True, exclude_substr='plot_')
    sysOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/zonal_animation.gif', duration=150, smooth=True, exclude_substr=['plot_', 'complete', 'map', 'tseries'])

    [os.remove(os.path.join(dp, f)) for dp, dn, fn in os.walk(unique_end_directory) for f in fn if f.endswith('__zonalmeans.png')]