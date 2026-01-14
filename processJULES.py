import cartopy.crs as ccrs
import numpy as np
import plotPARAMS
import readJULES
import dataOPS
import os


def compute_areal_mean(variable_array, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2): 

    """Compute the area-weighted mean value of a mapped variable within a specified box-shaped region
    Args:
        ax (matplotlib.axes._axes.Axes object): Plot axis
        variable_array (float): Mapped variable array
        variable_unit (string): Physical unit of the mapped variable
        lat2d / lon2d (float): 2D meshgrids of latitude / longitude coordinates
        lats / lons (float): 1D arrays of latitude / longitude coordinates
        lat1 / lat2 (float):  Latitude range minimum / maximum (for averaging)
        lon1 / lon2 (float): Longitude range minimum / maximum (for averaging)
    Returns:
        areal_mean (float): Area-weighted mean
    """

    # Filter the latitudes and longitudes that lie within specified ranges
    lat2d, lon2d = (dataOPS.bounded_coords(lat2d, lon2d, lat1, lat2, lon1, lon2))

    # Get the areas of the filtered latitudes and longitudes
    box_areas = dataOPS.latlon2area(lats, lons, lat2d, lon2d)
    #print(np.array2string(box_areas, threshold=np.inf))

    # Compute the areal mean of the sliced variable
    valid_mask = ~np.isnan(variable_array)
    weighted_sum = np.nansum(box_areas[valid_mask] * variable_array[valid_mask])
    total_area = np.nansum(box_areas[valid_mask])
    areal_mean = weighted_sum / total_area if total_area > 0 else np.nan

    #ax.plot([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1], transform=ccrs.PlateCarree(), color='black', linewidth=3.0)
    #ax.plot([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1], transform=ccrs.PlateCarree(), color='limegreen', linewidth=1.5)

    #ax.text(lon1 + 0.5, lat2 + 0.5, dataOPS.cleanup_exponents(str(round(areal_mean, 3)) + variable_unit), fontsize=16, color='white', ha='left', va='bottom', bbox=dict(facecolor='limegreen', edgecolor='none', alpha=0.7, boxstyle='round,pad=0.2'))

    return areal_mean


def compute_zonal_mean(variable_array, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2): 

    zonal_mean = np.nanmean(variable_array, axis=1)
    
    return zonal_mean


def compute_zonal_intg(variable_array, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2): 

    # Filter the latitudes and longitudes that lie within specified ranges
    lat2d, lon2d = (dataOPS.bounded_coords(lat2d, lon2d, lat1, lat2, lon1, lon2))

    # Get the areas of the filtered latitudes and longitudes (m^2)
    box_areas = dataOPS.latlon2area(lats, lons, lat2d, lon2d)

    latlon_totals = variable_array * box_areas # (kg/m2/s) x (m2) = (kg/s)

    zonal_intg = 2.628e6 * np.nansum(latlon_totals, axis=1) # (s/month) * Σ(kg/s) = Σ(kg/month)

    return zonal_intg


def write_processed_files():

    # Clear all .txt files in the output path
    [os.remove(os.path.join(dp, f)) for dp, dn, fn in os.walk(plotPARAMS.outp_path) for f in fn if f.endswith('.txt')]

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

    #print('mesh shape: ', np.shape(lon2d))

    for variable_name in plotPARAMS.variable_names:
        #print('var name: ', variable_name)
        # Variable to plot, its full array
        variable_array, variable_unit, variable_long_name, variable_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, variable_name)

        variable_array = dataOPS.sanitize_extreme_values(variable_array)

        print('var shape: ', np.shape(variable_array))
        print('variable name: ', variable_name)
        print(np.nanmax(variable_array))

        # If the variable has a 'time' axis, trim it along the time axis to the desired year
        if 'time' in variable_dims:
            time_dimension_index = np.where(np.array(variable_dims) == 'time')[0][0]
            variable_array = np.take(variable_array, indices=year_indices, axis=time_dimension_index)

        print('var shape2: ', np.shape(variable_array))

        # Boolean mask to indicate which variable array axes contain non-lat/lon data
        # Example: [True True False False] indicates that axes 0 and 1 contain non-lat/lon data.
        iterable_dimension_mask = ~np.isin(list(variable_dims), [lon_key, lat_key])
        #print('mask:', iterable_dimension_mask)

        # Array providing the labels (keys) of the non-lat/lon axes
        # Example: ['time' 'soil'] indicates that the array contains 'time' (month) and 'soil' (depth) data
        iterable_dimension_keys = np.array(list(variable_dims))[iterable_dimension_mask]

        # Array providing the indices of the non-lat/lon variable axes
        # Example: [0 1] indicates that 'time' is contained in the 0th index, 'soil' in the 1st
        iterable_dimension_idxs = np.where(iterable_dimension_mask)[0]
        print('idxs: ', iterable_dimension_idxs)
        # Array providing the the number of dimensions along each non-lat/lon axis
        # Example: [12 4] indicates that 'time' has 12 values and 'soil' has 4 values
        iterable_dimension_iter = np.array(np.shape(variable_array))[iterable_dimension_idxs]
        print('iterable dim iter: ', iterable_dimension_iter)
        # Make a list of tuples given the information above. Each tuple represents a unique slice combo through the non-lat/lon axes of the variable's array.
        # Example: If axis 0 represents month, axis 1 represents depth, '(2, 3)' slices the [month x depth x lat x lon] array at month 2 and depth 3
        indices = dataOPS.generate_indices(list(iterable_dimension_iter))
        
        # Loop through each tuple (slice combo). Each combo makes a unique map.
        print('indices: ', indices)
        for combo in indices:

            print(variable_name, combo)

            key_labels = [str(plotPARAMS.year)]
            variable_array2 = np.copy(variable_array)
            count = 0

            # Loop through each element of the tuple to perform a slice
            for var_dim_key, slice_index, slice_val in zip(iterable_dimension_keys, iterable_dimension_idxs, combo):

                # Slice the array along its 'slice_index'-count axis and 'slice_val' dimension
                # The '-count' is necessary because the array's dimension shrinks by one dimension with each slice
                variable_array2 = variable_array2.take(slice_val, axis=slice_index-count)
                #print('variable name: ', variable_name)
                # Append the label for file-naming purposes
                key_labels.append("("+str(slice_val)+")" + dataOPS.keyval2keylabel(var_dim_key, slice_val))
                count += 1

            sub_folder = key_labels[-1].replace(".", "p").replace(" ", "") if len(key_labels) > 2 else None
            
            # Transpose to match the lat/lon meshgrid shape
            if variable_array2.shape != lon2d.shape: variable_array2 = np.transpose(variable_array2)

            #print('dimensions: ', np.shape(lat2d))
            #stop

            lat_min, lat_max, lon_min, lon_max = np.nanmin(lats), np.nanmax(lats), np.nanmin(lons), np.nanmax(lons)
            #lat_min, lat_max, lon_min, lon_max = -20, 15, -15, 50
            #lat_min, lat_max, lon_min, lon_max = 3.0, 7.0, 99.0, 105.0
            
            # Compute an areal mean within a desired min, max-latitude and min, max-longitude range
            areal_mean = compute_areal_mean(variable_array2, variable_unit, lat2d, lon2d, lats, lons, lat_min, lat_max, lon_min, lon_max)
            zonal_mean = compute_zonal_mean(variable_array2, variable_unit, lat2d, lon2d, lats, lons, lat_min, lat_max, lon_min, lon_max)
            zonal_intg = compute_zonal_intg(variable_array2, variable_unit, lat2d, lon2d, lats, lons, lat_min, lat_max, lon_min, lon_max)
            
            # Clean up strings
            translation_table = str.maketrans({char: "" for char in "[]',"})
            cleaned_text = str(key_labels).translate(translation_table).replace(" ", "_").replace(".", "p")

            # Make an output folder and a variable folder inside the output folder
            os.makedirs(plotPARAMS.outp_path + 'output', exist_ok=True)
            os.makedirs(plotPARAMS.outp_path + 'output/' + variable_name, exist_ok=True)

            # Make a sub-folder within the variable folder, if the variable has another non-lat/lon dimension besides 'time'
            if sub_folder != None: os.makedirs(plotPARAMS.outp_path + 'output/' + variable_name + '/' + sub_folder, exist_ok=True)
            
            # Save plots and files in their end-point folder
            if sub_folder != None: 
                with open(plotPARAMS.outp_path + 'output/' + variable_name + '/' + sub_folder + '/' + variable_name + '_' + sub_folder + '_arealmean_tseries.txt', 'a') as file: file.write(str(areal_mean) + '\n')
                with open(plotPARAMS.outp_path + 'output/' + variable_name + '/' + sub_folder + '/' + variable_name + '_' + sub_folder + '_zonalmean_tseries.txt', 'a') as file: file.write(' '.join(map(str, zonal_mean)) + '\n')
                with open(plotPARAMS.outp_path + 'output/' + variable_name + '/' + sub_folder + '/' + variable_name + '_' + sub_folder + '_zonalintg_tseries.txt', 'a') as file: file.write(' '.join(map(str, zonal_intg)) + '\n')
            else: 
                with open(plotPARAMS.outp_path + 'output/' + variable_name + '/' + variable_name + '_arealmean_tseries.txt', 'a') as file: file.write(str(areal_mean) + '\n')
                with open(plotPARAMS.outp_path + 'output/' + variable_name + '/' + variable_name + '_zonalmean_tseries.txt', 'a') as file: file.write(' '.join(map(str, zonal_mean)) + '\n')
                with open(plotPARAMS.outp_path + 'output/' + variable_name + '/' + variable_name + '_zonalintg_tseries.txt', 'a') as file: file.write(' '.join(map(str, zonal_intg)) + '\n')