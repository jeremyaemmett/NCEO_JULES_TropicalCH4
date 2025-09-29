from matplotlib import colormaps
import matplotlib.pyplot as plt
import pandas as pd
import processJULES
import numpy as np
import plotPARAMS
import readJULES
import mapJULES
import warnings
import miscOPS
import os

# JULES output file path/name
data_path, outp_path, file_name = plotPARAMS.data_path, plotPARAMS.outp_path, plotPARAMS.file_name

# Variable(s) and year to map
variable_names, year = plotPARAMS.variable_names, plotPARAMS.year


def make_maps():

    # Clear all .txt files in the output path
    [os.remove(os.path.join(dp, f)) for dp, dn, fn in os.walk(outp_path) for f in fn if f.endswith('.txt')]

    dimensions, variables, global_attributes = readJULES.read_jules_header(data_path+file_name)
    #readJULES.get_variable_details(variables, data_path, file_name)

    # Full 'time' array
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

        variable_array = miscOPS.sanitize_extreme_values(variable_array)

        #variable_global_min, variable_global_max = np.nanmin(variable_array), np.nanmax(variable_array)
        variable_global_min, variable_global_max = miscOPS.globalMinMax(variable_array, variable_unit)

        print(variable_name, np.shape(variable_array))

        # If the variable has a 'time' axis, trim it along the time axis to the desired year
        if 'time' in variable_dims:
            time_dimension_index = np.where(np.array(variable_dims) == 'time')[0][0]
            variable_array = np.take(variable_array, indices=year_indices, axis=time_dimension_index)

        # Boolean mask to indicate which variable array axes contain non-lat/lon data
        # Example: [True True False False] indicates that axes 0 and 1 contain non-lat/lon data.
        iterable_dimension_mask = ~np.isin(list(variable_dims), ['lon', 'lat'])

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
        indices = miscOPS.generate_indices(list(iterable_dimension_iter))
        
        # Loop through each tuple (slice combo). Each combo makes a unique map.
        for combo in indices:

            key_labels = [str(year)]
            variable_array2 = np.copy(variable_array)
            count = 0

            # Loop through each element of the tuple to perform a slice
            for var_dim_key, slice_index, slice_val in zip(iterable_dimension_keys, iterable_dimension_idxs, combo):

                # Slice the array along its 'slice_index'-count axis and 'slice_val' dimension
                # The '-count' is necessary because the array's dimension shrinks by one dimension with each slice
                variable_array2 = variable_array2.take(slice_val, axis=slice_index-count)

                # Append the label for file-naming purposes
                key_labels.append("("+str(slice_val)+")" + miscOPS.keyval2keylabel(var_dim_key, slice_val))
                count += 1

            sub_folder = key_labels[-1].replace(".", "p").replace(" ", "") if len(key_labels) > 2 else None

            # Transpose to match the lat/lon meshgrid shape
            variable_array2 = np.transpose(variable_array2)

            # Make an empty world map
            fig, ax = mapJULES.world_map(lats, lons)

            # Overlay the sliced variable with contours
            mapJULES.overplot_variable(ax, lats, lons, variable_name, variable_long_name, variable_array2, variable_unit, key_labels, 'inferno', variable_global_min, variable_global_max)

            # Compute an areal mean within a desired min, max-latitude and min, max-longitude range
            areal_mean = processJULES.areal_mean(ax, variable_array2, variable_unit, lat2d, lon2d, lats, lons, -20, 15, -15, 50)

            # Clean up strings
            translation_table = str.maketrans({char: "" for char in "[]',"})
            cleaned_text = str(key_labels).translate(translation_table).replace(" ", "_").replace(".", "p")

            # Make an output folder and a variable folder inside the output folder
            os.makedirs(outp_path + 'output', exist_ok=True)
            os.makedirs(outp_path + 'output/' + variable_name, exist_ok=True)

            # Make a sub-folder within the variable folder, if the variable has another non-lat/lon dimension besides 'time'
            if sub_folder != None: os.makedirs(outp_path + 'output/' + variable_name + '/' + sub_folder, exist_ok=True)

            # Save plots and files in their end-point folder
            if sub_folder != None: 
                with open(outp_path + 'output/' + variable_name + '/' + sub_folder + '/' + variable_name + '_' + sub_folder + '_tseries.txt', 'a') as file: file.write(str(areal_mean) + '\n')
                plt.savefig(outp_path + 'output/' + variable_name + '/' + sub_folder + '/' + variable_name + '_' + cleaned_text + '.png')
            else: 
                with open(outp_path + 'output/' + variable_name + '/' + variable_name + '_tseries.txt', 'a') as file: file.write(str(areal_mean) + '\n')
                plt.savefig(outp_path + 'output/' + variable_name + '/' + variable_name + '_' + cleaned_text + '.png')

            plt.close()

    #plt.show()

def make_tseries():

    grouped = {}
    grouped_files = {}

    # Make a list of every t-series file across all of the input variables
    files = [os.path.join(r, f) for r, _, fs in os.walk(outp_path) for f in fs if f.endswith('.txt')]
    files = miscOPS.filter_strings_by_substrings(files, variable_names)

    # Loop through every t-series file
    for f in files:

        # Recover the variable name from the file path
        parts = os.path.normpath(f).split(os.sep)
        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(f))
        
        # Group the t-series file paths by their variables: Dictionary with {variable1: [t-series list], variable2: [t-series list]}
        grouped.setdefault(key, []).append(pd.read_csv(f, header=None)[0].tolist())
        grouped_files.setdefault(key, []).append(f)

    cmap = colormaps['magma']

    # Loop through each variable in the grouped dictionary
    for k in grouped:

        # Recover variable metadata, particuarly the unit
        k_array, k_unit, k_long_name, k_dims = readJULES.read_jules_m2(data_path + file_name, k)

        # T-series plot prep.
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title(rf"$\mathbf{{{k.replace('_', r'\_')}}}$" + "  (area-weighted mean)")
        ax.set_xticks(range(12))
        ax.set_xticklabels(['JanFebMarAprMayJunJulAugSepOctNovDec'[i*3:i*3+3] for i in range(12)], fontsize=12)
        ax.set_ylabel(k_unit, fontsize=12)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(edgecolor='gainsboro', facecolor='gainsboro', fontsize=10)
        ax.set_facecolor('gainsboro')
        ax.grid(True)

        # For the current variable, loop through all of its t-series arrays (and their file paths)
        for i, (series, fpath) in enumerate(zip(grouped[k], grouped_files[k])):

            # Get the name of the end-directory for the current t-series, so the code remembers where it belongs in the tree
            final_directory_path = '/'.join(fpath.split('/')[0:-1])
            print('save here: ', final_directory_path + '/' + final_directory_path.split('/')[-1] + '.gif')

            # While we know the end-directory, we might as well make an animated gif of the monthly maps, using all the existing png's
            miscOPS.pngs_to_gif(final_directory_path, final_directory_path + '/' + final_directory_path.split('/')[-1] + '.gif', duration=150, smooth=True, exclude_substr='plot_')

            # Plot the t-series, colored to differentiate it from other t-series belonging to the variable
            label = miscOPS.remove_parenthetical_substrings(os.path.basename(os.path.dirname(fpath))).replace("p",".")
            color = cmap(i / max(len(grouped[k]) - 1, 1))
            ax.plot(series, alpha=0.7, label=label, linewidth=3.0, color=color)
        
        # Save the plot in the variable's main directory
        out_dir = outp_path + 'output/' + k
        out_path = os.path.join(out_dir, f"plot_{k}.png")
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
        print('fig saved to: ', out_path)
        

#make_maps()
make_tseries()

test = outp_path + 'output/' + 'fch4_wetl'
test2 = miscOPS.pngs_to_gif(test, 'test.gif', duration=150, smooth=True, exclude_substr='plot_')

