from scipy.interpolate import interp1d
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
from matplotlib import colormaps
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

base_path = '/Users/jae35/Desktop/JULES_test_data/JASMIN_output_'
suites = ['u-dk105_8', 'u-dk105_7', 'u-dk105_6', 'u-dk105_5', 'u-dk105_4', 'u-dk105_3', 'u-dk105_2', 'u-dk105_1']
values = [2.7, 2.5, 2.3, 2.1, 2.0, 1.7, 1.5, 1.3]
variable = 'fch4_wetl'

cmap = plt.get_cmap('copper_r')  # choose your colormap
colors = cmap(np.linspace(0, 1, len(suites)))

# Create ONE figure with 2 subplots side by side
fig, axes = plt.subplots(1, 2, figsize=(16, 6))  # 1 row, 2 columns
ax_left, ax_right = axes

# --- LEFT PLOT ---
ax_left.yaxis.tick_right()
ax_left.yaxis.set_label_position("right")
ax_left.set_facecolor('white')

ax_right.yaxis.tick_right()
ax_right.yaxis.set_label_position("right")
ax_right.set_facecolor('white')

intgs = []
for i, suite in enumerate(suites):

    path = base_path + suite + '/plots/output/' + variable + '/' + '_arealmean_tseries.txt'
    integ_file = base_path + suite + '/plots/output/' + variable + '/' + '_zonalintg_tseries.txt'
    areal_values = np.loadtxt(path).T
    integ_values = np.loadtxt(integ_file).T
    integ_values_cumsum = np.cumsum(integ_values, axis=1)
    integ_values_cumsum_final = np.nansum(integ_values_cumsum, axis=0)[-1]
    intgs.append(integ_values_cumsum_final)

    time = np.arange(len(areal_values))

    ax_left.plot(time, areal_values, label=suite, color=0.8*colors[i], linewidth=3.0)

    mid_idx = len(time) // 2
    ax_left.text(
        time[mid_idx],                 # x position
        areal_values[mid_idx] + 0.0015,  # y position
        f"$q_{{10}}$ = {values[i]}",      # label text
        color=0.8*colors[i],
        fontsize=14,
        va='bottom',
        ha='center',
        fontweight='bold',
        fontstyle='italic',
        fontfamily='sans-serif',
        path_effects=[pe.withStroke(linewidth=3, foreground='white')]
    )

    ax_right.plot(values[i], intgs[i], marker='o', linestyle='', color=0.8*colors[i])

ax_left.set_xlabel('Month', fontsize=18)
ax_left.set_ylabel("$F_{{CH4}}$", fontsize=18)
ax_left.set_title('Area-Mean')
ax_left.grid(True, color='lightgrey', linewidth=3, alpha=0.2)

# --- RIGHT PLOT (empty for now) ---
ax_right.set_facecolor('white')
ax_right.set_title('Annual Area-Cumulative')
ax_right.set_xlabel("$q_{{10}}$", fontsize=18)
ax_right.set_ylabel("$F_{{CH4}}$", fontsize=18)
ax_right.grid(True, color='lightgrey', linewidth=3, alpha=0.2)

plt.tight_layout()
plt.show()