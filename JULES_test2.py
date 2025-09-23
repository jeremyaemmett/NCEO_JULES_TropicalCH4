import matplotlib.pyplot as plt
import processJULES
import numpy as np
import readJULES
import mapJULES
import warnings


def keyval2keylabel(keyname, keyval):

    if keyname == 'month': labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if keyname == 'pool': labels = ['DPM', 'RPM', 'Micro. Bio', 'Humus']
    if keyname == 'layer': labels = ['0-0.1 m', '0.1-0.35 m', '0.35-1.0 m', '1.0-2.0 m']

    key_label = labels[keyval]

    return key_label


# JULES output file path/name
data_path = '/Users/jae35/Desktop/JULES_test_data/JULES_wetlands_JE/'
outp_path = '/Users/jae35/Documents/nceo/'
file_name = 'u-ck843_preprocessed.nc'

dimensions, variables, global_attributes = readJULES.read_jules_header(data_path+file_name)

print('vars: ', variables)

# Variable(s) to visualize, with their dimension keys and values
variable_names = {'fch4_wetl': {'month':6},
                  't_soil':    {'month':6, 'layer':0}}
cmap = 'inferno'

for variable_name in list(variable_names.keys()):

    # Variable to plot, its full array
    variable_array, variable_unit, variable_long_name = readJULES.read_jules_m2(data_path + file_name, variable_name)

    # Coordinates, their full arrays
    lats, lats_units, lats_long_name = readJULES.read_jules_m2(data_path + file_name, 'lat')
    lons, lons_units, lons_long_name = readJULES.read_jules_m2(data_path + file_name, 'lon')
    lon2d, lat2d = np.meshgrid(lons, lats)

    # Get the variable's dimension keys and values, for slicing
    variable_dimension_keys = list(variable_names[variable_name].keys())

    # Slice the variable along desired dimensions, i.e., month 3, layer 1, etc.
    key_labels = []
    for var_dim_key in variable_dimension_keys:
        slice_index = variable_names[variable_name][var_dim_key]
        variable_array = variable_array[slice_index]
        key_labels.append(keyval2keylabel(var_dim_key, slice_index))  # Labels describing the slices, for plotting
    variable_array = np.transpose(variable_array)

    # Make an empty world map
    fig, ax = mapJULES.world_map(lats, lons)

    lat1, lat2, lon1, lon2 = -10, 15, -15, 50

    # Overlay the sliced variable with contours
    mapJULES.overplot_variable(ax, lats, lons, variable_name, variable_long_name, variable_array, variable_unit, key_labels, cmap)

    areal_mean = processJULES.areal_mean(ax, variable_array, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2)

    # Save the final map to the workspace directory
    translation_table = str.maketrans({char: "" for char in "[]',."})
    cleaned_text = str(key_labels).translate(translation_table).replace(" ", "_")
    plt.savefig(outp_path + variable_name + '_' + cleaned_text + '.png')

#plt.show()