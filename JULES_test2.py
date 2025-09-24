import matplotlib.pyplot as plt
import processJULES
import numpy as np
import readJULES
import mapJULES
import warnings
import os


def keyval2keylabel(keyname, keyval):

    if keyname == 'time': labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if keyname == 'pool': labels = ['DPM', 'RPM', 'Micro. Bio', 'Humus']
    if keyname == 'soil': labels = ['0-0.1 m', '0.1-0.35 m', '0.35-1.0 m', '1.0-2.0 m']
    if keyname == 'pft':  labels = ['pft1', 'pft2', 'pft3', 'pft4', 'pft5', 'pft6', 'pft7', 'pft8', 'pft9', 'pft10', 'pft11', 'pft12', 'pft13']

    key_label = labels[keyval]

    return key_label


def generate_indices(shape):

    if not shape:
        return [()]
    
    rest = generate_indices(shape[1:])
    return [(i,) + r for i in range(shape[0]) for r in rest]


# JULES output file path/name
data_path = '/Users/jae35/Desktop/JULES_test_data/JULES_wetlands_JE/'
outp_path = '/Users/jae35/Documents/nceo/'
file_name = 'u-ck843_preprocessed.nc'

dimensions, variables, global_attributes = readJULES.read_jules_header(data_path+file_name)

#readJULES.get_variable_details(variables, data_path, file_name)

# Variable(s) to visualize
variable_names = ['t_soil', 'fch4_wetl', 'tstar_gb']

cmap = 'inferno'
year = 2016

# Time, its full array
times, times_unit, times_long_name, times_dims = readJULES.read_jules_m2(data_path + file_name, 'time')
# Get the time dimension indices that fall within the desired year
year_indices = np.where((times >= np.datetime64(f'{year}-01-01')) & (times < np.datetime64(f'{year + 1}-01-01')))[0]

# Latitudes and Longitudes, their full arrays, converted to 2D meshgrids
lats, lats_units, lats_long_name, lats_dims = readJULES.read_jules_m2(data_path + file_name, 'lat')
lons, lons_units, lons_long_name, lons_dims = readJULES.read_jules_m2(data_path + file_name, 'lon')
lon2d, lat2d = np.meshgrid(lons, lats)

for variable_name in variable_names:

    # Variable to plot, its full array
    variable_array, variable_unit, variable_long_name, variable_dims = readJULES.read_jules_m2(data_path + file_name, variable_name)
    variable_global_min, variable_global_max = np.nanmin(variable_array), np.nanmax(variable_array)

    print(variable_name, np.shape(variable_array))

    # If the variable has a 'time' axis, trim it along the time axis to the desired year
    if 'time' in variable_dims:
        time_dimension_index = np.where(np.array(variable_dims) == 'time')[0][0]
        variable_array = np.take(variable_array, indices=year_indices, axis=time_dimension_index)

    # Get the variable's dimension keys and values, for slicing
    #variable_dimension_keys = list(variable_names[variable_name].keys())

    # Get the variable's iterable dimension keys and their axis lengths (axes other than 'lon' and 'lat')
    iterable_dimension_mask = ~np.isin(list(variable_dims), ['lon', 'lat'])
    iterable_dimension_keys = np.array(list(variable_dims))[iterable_dimension_mask]
    iterable_dimension_idxs = np.where(iterable_dimension_mask)[0]
    iterable_dimension_iter = np.array(np.shape(variable_array))[iterable_dimension_idxs]

    print('its')
    print('keys: ', iterable_dimension_keys)
    print('idxs: ', iterable_dimension_idxs)
    print('iter: ', iterable_dimension_iter)

    indices = generate_indices(list(iterable_dimension_iter))
    for combo in indices:
        #print(combo)
        #print(iterable_dimension_idxs)
        key_labels = []
        variable_array2 = np.copy(variable_array)
        count = 0
        print('init shape: ', np.shape(variable_array2))
        for var_dim_key, slice_index, slice_val in zip(iterable_dimension_keys, iterable_dimension_idxs, combo):
            print(var_dim_key, slice_index, slice_val)
            variable_array2 = variable_array2.take(slice_val, axis=slice_index-count)
            print('reshaped: ', np.shape(variable_array2))
            key_labels.append(keyval2keylabel(var_dim_key, slice_val))
            count += 1
        #stop
        print(key_labels)
        print(' ')
        variable_array2 = np.transpose(variable_array2)

        # Make an empty world map
        fig, ax = mapJULES.world_map(lats, lons)

        lat1, lat2, lon1, lon2 = -10, 15, -15, 50

        print(np.shape(variable_array2))

        # Overlay the sliced variable with contours
        mapJULES.overplot_variable(ax, lats, lons, variable_name, variable_long_name, variable_array2, variable_unit, key_labels, cmap, variable_global_min, variable_global_max)

        areal_mean = processJULES.areal_mean(ax, variable_array2, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2)

        # Save the final map to the workspace directory
        translation_table = str.maketrans({char: "" for char in "[]',."})
        cleaned_text = str(key_labels).translate(translation_table).replace(" ", "_")
        os.makedirs(outp_path + 'output', exist_ok=True)
        os.makedirs(outp_path + 'output/' + variable_name, exist_ok=True)
        print('plot')
        plt.savefig(outp_path + 'output/' + variable_name + '/' + variable_name + '_' + cleaned_text + '_test.png')

#plt.show()