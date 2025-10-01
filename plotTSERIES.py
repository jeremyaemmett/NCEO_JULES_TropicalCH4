from matplotlib import colormaps
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotPARAMS
import readJULES
import dataOPS
import sysOPS
import os


def tseries_axes(plot_title, y_units, tseries_values, plot_margin, facecolor):

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_title(plot_title, loc='left', fontsize=18)
    ax.set_xticks(range(12))
    ax.set_xlim([0, 11])
    ax.set_ylim([np.min(tseries_values) - plot_margin, np.max(tseries_values) + plot_margin])
    ax.set_xticklabels(['JanFebMarAprMayJunJulAugSepOctNovDec'[j*3:j*3+3] for j in range(12)], fontsize=12)
    ax.set_ylabel(dataOPS.cleanup_exponents(y_units), fontsize=18)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_facecolor(facecolor)
    ax.grid(True)

    return fig, ax


def make_tseries():

    grouped = {}
    grouped_files = {}

    # Make a list of every t-series file across all of the input variables
    files = [os.path.join(r, f) for r, _, fs in os.walk(plotPARAMS.outp_path) for f in fs if f.endswith('.txt')]
    files = dataOPS.filter_strings_by_substrings(files, plotPARAMS.variable_names)

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
        k_array, k_unit, k_long_name, k_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, k)

        # T-series plot prep.
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title(rf"$\mathbf{{{k.replace('_', r'\_')}}}$" + "  (area-weighted mean)", fontsize=8)
        ax.set_xticks(range(12))
        ax.set_xticklabels(['JanFebMarAprMayJunJulAugSepOctNovDec'[i*3:i*3+3] for i in range(12)], fontsize=12)
        ax.set_ylabel(dataOPS.cleanup_exponents(k_unit), fontsize=12)
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

            # Plot the t-series, colored to differentiate it from other t-series belonging to the variable
            label = dataOPS.remove_parenthetical_substrings(os.path.basename(os.path.dirname(fpath))).replace("p",".")
            color = cmap(i / max(len(grouped[k]) - 1, 1))
            c = ax.plot(series, alpha=0.7, label=label, linewidth=3.0, color=color)
        
        # Save the plot in the variable's main directory
        out_dir = plotPARAMS.outp_path + 'output/' + k
        out_path = os.path.join(out_dir, f"tseries_complete_{k}.png")
        plt.savefig(out_path, dpi=300)
        plt.close()
        print('fig saved to: ', out_path)


def make_animated_tseries():

    # Make a list of every t-series file across all of the input variables
    files = sysOPS.discover_files(plotPARAMS.outp_path, 'tseries.txt')

    unique_end_directories = sysOPS.get_unique_end_directories(files)

    cmap = colormaps['magma']

    for unique_end_directory in unique_end_directories:

        tseries_file = sysOPS.discover_files(unique_end_directory, 'tseries.txt')[0]
        tseries_values = pd.read_csv(tseries_file, header=None)[0].tolist()

        # Recover the variable name from the file path
        parts = os.path.normpath(tseries_file).split(os.sep)
        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(tseries_file))
        # Recover variable metadata, particuarly the unit
        k_array, k_unit, k_long_name, k_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, key)

        name1 = dataOPS.remove_parenthetical_substrings(tseries_file.split('/')[-1]).replace("_ ", " ")[0:-12]
        name2 = name1.split(" ")[-1].replace("p", ".") if key != name1 else ""

        for i in range(1, 13):

            # T-series plot prep.
            plot_margin = 0.10 * (np.max(tseries_values) - np.min(tseries_values))
            fig, ax = tseries_axes("Area-weighted mean", k_unit, tseries_values, plot_margin, 'white')
            ax.tick_params(axis='both', labelsize=16)
            fig.tight_layout()
            fig.subplots_adjust(right=0.74)

            # --- Gray full curve with fading alpha ---
            color1 = cmap((tseries_values[i-1] - np.nanmin(k_array)) / (np.nanmax(k_array - np.nanmin(k_array))))

            for j in range(11):

                color2 = cmap((tseries_values[j] - np.nanmin(k_array)) / (np.nanmax(k_array - np.nanmin(k_array))))
                dist = abs((j + 0.5) - (i - 1))  # Distance from segment center to current index
                alpha, width = max(0.1, 1.0 - dist / 2.0), max(0.1, 4.0 - dist / 3.0)
                ax.plot([j, j + 1], [tseries_values[j], tseries_values[j + 1]], color=color2, alpha=alpha, linewidth=width)

            # --- Black 3-point segment centered around i ---
            start, end = max(0, i - 2), min(12, i - 1)
            if end - start > 1:
                
                ax.plot(range(start, end), tseries_values[start:end], color=color1, alpha=0.9, linewidth=4.0)

            #ax.legend(edgecolor='white', facecolor='white', fontsize=10)
            ax.text(0.35, np.min(tseries_values) - 0.5*plot_margin, plotPARAMS.year, fontsize=18, color='black', ha='left', va='bottom', style='italic')

            plt.savefig(unique_end_directory + '/' + str(i) + '_' + 'tseries.png', dpi=300, bbox_inches='tight')
            plt.close()

        sysOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/tseries_animation.gif', duration=150, smooth=True, exclude_substr=['map', 'complete'])

        [os.remove(os.path.join(dp, f)) for dp, dn, fn in os.walk(unique_end_directory) for f in fn if f.endswith('_tseries.png')]