import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import processJULES
import numpy as np
import plotPARAMS
import readJULES
import dataOPS
import sysOPS
import os


def make_maps():

    # Full 'time' array
    times, times_unit, times_long_name, times_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, 'time')
    # Get the time dimension indices that fall within the desired year
    year_indices = np.where((times >= np.datetime64(f'{plotPARAMS.year}-01-01')) & (times < np.datetime64(f'{plotPARAMS.year + 1}-01-01')))[0]

    header = readJULES.read_jules_header(plotPARAMS.data_path + plotPARAMS.file_name)
    dimension_keys, variable_keys = list(header[0]), list(header[1])

    if 'latitude' in variable_keys and 'longitude' in variable_keys: lat_string, lon_string = 'latitude', 'longitude'
    if 'lat' in variable_keys and 'lon' in variable_keys: lat_string, lon_string = 'lat', 'lon'

    if 'lat' in dimension_keys and 'lon' in dimension_keys: lat_key, lon_key = 'lat', 'lon'
    if 'y' in dimension_keys and 'x' in dimension_keys: lat_key, lon_key = 'y', 'x'

    # Latitudes and Longitudes, their full arrays, converted to 2D meshgrids
    lats, lats_units, lats_long_name, lats_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, lat_string)
    lons, lons_units, lons_long_name, lons_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, lon_string)
    
    coords_are_2d = len(np.shape(lats)) == 2
    if coords_are_2d: lats, lons = lats[:, 0], lons[0, :]
    
    lon2d, lat2d = np.meshgrid(lons, lats)

    for variable_name in plotPARAMS.variable_names:

        # Variable to plot, its full array
        variable_array, variable_unit, variable_long_name, variable_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, variable_name)

        variable_array = dataOPS.sanitize_extreme_values(variable_array)

        #variable_global_min, variable_global_max = np.nanmin(variable_array), np.nanmax(variable_array)
        variable_global_min, variable_global_max = dataOPS.globalMinMax(variable_array, variable_unit)

        # If the variable has a 'time' axis, trim it along the time axis to the desired year
        if 'time' in variable_dims:
            time_dimension_index = np.where(np.array(variable_dims) == 'time')[0][0]
            variable_array = np.take(variable_array, indices=year_indices, axis=time_dimension_index)

        # Boolean mask to indicate which variable array axes contain non-lat/lon data
        # Example: [True True False False] indicates that axes 0 and 1 contain non-lat/lon data.
        iterable_dimension_mask = ~np.isin(list(variable_dims), [lon_key, lat_key])

        # Array providing the labels (keys) of the non-lat/lon axes
        # Example: ['time' 'soil'] indicates that the array contains 'time' (month) and 'soil' (depth) data
        iterable_dimension_keys = np.array(list(variable_dims))[iterable_dimension_mask]

        # Array providing the indices of the non-lat/lon variable axes
        # Example: [0 1] indicates that 'time' is contained in the 0th index, 'soil' in the 1st
        iterable_dimension_idxs = np.where(iterable_dimension_mask)[0]

        # Array providing the the number of dimensions along each non-lat/lon axis
        # Example: [12 4] indicates that 'time' has 12 values and 'soil' has 4 values
        iterable_dimension_iter = np.array(np.shape(variable_array))[iterable_dimension_idxs]

        # Make a list of tuples given the information above. Each tuple represents a unique slice combo through the non-lat/lon axes of the variable's array.
        # Example: If axis 0 represents month, axis 1 represents depth, '(2, 3)' slices the [month x depth x lat x lon] array at month 2 and depth 3
        indices = dataOPS.generate_indices(list(iterable_dimension_iter))
        
        # Loop through each tuple (slice combo). Each combo makes a unique map.
        for combo in indices:

            key_labels = [str(plotPARAMS.year)]
            variable_array2 = np.copy(variable_array)
            count = 0

            # Loop through each element of the tuple to perform a slice
            for var_dim_key, slice_index, slice_val in zip(iterable_dimension_keys, iterable_dimension_idxs, combo):

                # Slice the array along its 'slice_index'-count axis and 'slice_val' dimension
                # The '-count' is necessary because the array's dimension shrinks by one dimension with each slice
                variable_array2 = variable_array2.take(slice_val, axis=slice_index-count)

                # Append the label for file-naming purposes
                key_labels.append("("+str(slice_val)+")" + dataOPS.keyval2keylabel(var_dim_key, slice_val))
                count += 1

            sub_folder = key_labels[-1].replace(".", "p").replace(" ", "") if len(key_labels) > 2 else None

            # Transpose to match the lat/lon meshgrid shape
            if variable_array2.shape != lon2d.shape: variable_array2 = np.transpose(variable_array2)

            # Make an empty world map
            fig, ax = world_map(lats, lons)

            # Overlay the sliced variable with contours
            overplot_variable(ax, lats, lons, variable_name, variable_long_name, variable_array2, variable_unit, key_labels, 'inferno', variable_global_min, variable_global_max)

            # Clean up strings
            translation_table = str.maketrans({char: "" for char in "[]',"})
            cleaned_text = str(key_labels).translate(translation_table).replace(" ", "_").replace(".", "p")

            # Save plots and files in their end-point folder
            if sub_folder != None: 
                plt.savefig(plotPARAMS.outp_path + 'output/' + variable_name + '/' + sub_folder + '/' + variable_name + '_' + cleaned_text + '_map.png', dpi=300,  bbox_inches='tight')
            else: 
                plt.savefig(plotPARAMS.outp_path + 'output/' + variable_name + '/' + variable_name + '_' + cleaned_text + '_map.png', dpi=300,  bbox_inches='tight')

            plt.close()


def make_animated_maps():

    # Make a list of every t-series file across all of the input variables
    files = sysOPS.discover_files(plotPARAMS.outp_path, '_map.png')

    unique_end_directories = sysOPS.get_unique_end_directories(files)

    for unique_end_directory in unique_end_directories:

        map_files = sysOPS.discover_files(unique_end_directory, '_map.png')
        
        #miscOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/' + unique_end_directory.split('/')[-1] + '_animation.gif', duration=150, smooth=True, exclude_substr='plot_')
        sysOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/map_animation.gif', duration=150, smooth=True, exclude_substr=['plot_', 'complete', 'zonalmeans'])


def world_map(lats, lons):

    """Create a world map, given latitude and longitude coordinates
    Args:
        lats (float): 1D array of latitude coordinates
        lons (float): 1D array of longitude coordinates
    Returns:
        fig (matplotlib.figure.Figure object): A matplotlib figure
        ax (matplotlib.axes._axes.Axes object): A matplotlib axis
    """

    # Add some extra space to the map edges
    lon_min, lon_max, lat_min, lat_max = np.min(lons)-2.5, np.max(lons)+2.5, np.min(lats)-2.5, np.max(lats)+2.5
    #lon_min, lon_max, lat_min, lat_max = plotPARAMS.lon_min, plotPARAMS.lon_max, plotPARAMS.lat_min, plotPARAMS.lat_max

    # Figure size
    #scale = 0.1
    #map_width, map_height = lon_max - lon_min, lat_max - lat_min
    #fig_width, fig_height = map_width*scale, map_height*scale
    #fig = plt.figure(figsize=(fig_width, fig_height))
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

    # Topography, details
    ax.coastlines()
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='white')
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'fontsize': 16}  # Longitude labels
    gl.ylabel_style = {'fontsize': 16}  # Latitude labels

    return fig, ax


def overplot_variable(ax, lat2d, lon2d, variable_name, variable_long_name, variable_array, variable_unit, key_labels, cmap, variable_global_min, variable_global_max):

    """Overplot, onto an empty map, filled contours and a colorbar to display a mapped variable
    Args:
        ax (matplotlib.axes._axes.Axes object): Plot axis
        lat2d / lon2d (float): 2D meshgrids of latitude / longitude coordinates
        variable_name / variable_long_name (string): Short name / Long name of the mapped variable
        variable_array (float): Mapped variable array
        variable_unit (string): Physical unit of the mapped variable
        key_labels (_type_): Descriptive labels for the mapped variable's dimensions
        cmap (matplotlib.colors.Colormap object): Colormap name
        variable_global_min / variable_global_max (float): Fixed minimum / maximum contour levels for the mapped variable
    """

    vmin, vmax = variable_global_min, variable_global_max
    n_levels = 10

    step_raw = (vmax - vmin) / (n_levels - 1)
    mag = 10 ** np.floor(np.log10(step_raw))
    step = mag * (1 if step_raw/mag <= 1 else 2 if step_raw/mag <= 2 else 5)

    vmin_r = np.floor(vmin / step) * step
    vmax_r = np.ceil(vmax / step) * step

    levels = np.arange(vmin_r, vmax_r + step/2, step)

    c = ax.contourf(lon2d, lat2d, variable_array,
                    levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
    cb.set_label(dataOPS.cleanup_exponents(variable_unit), fontsize=18)
    cb.ax.tick_params(labelsize=14)

    variable_name_fix = variable_name.split('_')[0] + '\_' + variable_name.split('_')[1] if len(variable_name.split('_')) > 1 else variable_name

    subtitle = ''
    for key in key_labels: subtitle += key + '  '
    
    ax.set_title(dataOPS.remove_parenthetical_substrings(r"$\bf{" + variable_name_fix + "}$" + '\n' + variable_long_name), loc='left', fontsize=18)
    ax.text(np.min(lon2d)-1, np.min(lat2d)-1, dataOPS.remove_parenthetical_substrings(subtitle), fontsize=18, color='black', ha='left', va='bottom', style='italic')