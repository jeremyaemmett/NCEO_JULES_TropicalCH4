from matplotlib.patches import Rectangle
from matplotlib.patches import Patch
from scipy.interpolate import interp1d
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
from matplotlib import colormaps
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.cm as cm
import pandas as pd
import numpy as np

base_path = '/Users/jae35/Desktop/JULES_test_data/JASMIN_output_'
suites = ['u-dk105_8', 'u-dk105_7', 'u-dk105_6', 'u-dk105_5', 'u-dk105_4', 'u-dk105_3', 'u-dk105_2', 'u-dk105_1']
values = [2.7, 2.5, 2.3, 2.1, 2.0, 1.7, 1.5, 1.3]
variable = 'fch4_wetl'

cmap = plt.get_cmap('copper_r')  # choose your colormap

cmap = plt.get_cmap('Grays')  # choose your colormap
colors = cmap(np.linspace(0, 1, len(suites)))

# Create ONE figure with 2 subplots side by side
fig, axes = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [2, 1]} )  # 1 row, 2 columns
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

    ax_left.plot(time, areal_values, label=suite, color=0.7*colors[i], linewidth=3.0)

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

    ax_right.plot(values[i], intgs[i], marker='o', linestyle='', color=0.7*colors[i])

ax_left.set_xlabel(' \nMonth', fontsize=18)
ax_left.set_ylabel("$F_{{CH4}}$", fontsize=18)
#ax_left.set_title('Area-Mean')
ax_left.set_title('   Areal mean', loc='left', fontsize=16, fontstyle='italic')
ax_left.grid(True, color='lightgrey', linewidth=3, alpha=0.2)

months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
# Set ticks first
#ax_left.set_xticks(np.arange(len(months)))
#ax_left.set_xticklabels(months)  # do NOT pass fontsize here
ax_left.set_xticks(np.arange(12))
ax_left.set_xticklabels(months, fontsize=18)

cmap = cm.get_cmap('managua', 12)
# Add month-colored rectangles
for i in range(12):
    rect = Rectangle(
        (i - 0.5, -0.113),  # align with tick
        1.0,               # width = 1 month
        0.09,              # height of strip
        transform=ax_left.get_xaxis_transform(),
        color=cmap(i),
        alpha=0.3,
        clip_on=False,
        zorder=0
    )
    ax_left.add_patch(rect)

# Apply colors
for i, label in enumerate(ax_left.get_xticklabels()):
    label.set_color('black')
    #label.set_fontweight('bold')
    #label.set_path_effects([
    #    pe.Stroke(linewidth=5.0, foreground='white'),
    #    pe.Normal()])
    label.set_rotation(0)
    label.set_ha('center')  # important for clean alignment
    label.set_y(-0.025)  # default ~0, negative moves down
    if label.get_text() == 'J':
        label.set_y(-0.017) 
    label.set_fontname('DejaVu Sans')
    label.set_fontstyle('italic')

# --- RIGHT PLOT (empty for now) ---
ax_right.set_facecolor('white')
#ax_right.set_title('Annual Area-Cumulative')
ax_right.set_title('   Annual areal cummulative', loc='left', fontsize=16, fontstyle='italic')
ax_right.set_xlabel("$q_{{10}}$", fontsize=18)
ax_right.set_ylabel("$F_{{CH4}}$", fontsize=18)
ax_right.grid(True, color='lightgrey', linewidth=3, alpha=0.2)

ax_left.tick_params(axis='x', labelsize=16)  # x-axis tick labels
ax_left.tick_params(axis='y', labelsize=16)  # y-axis tick labels

ax_right.tick_params(axis='x', labelsize=16)  # x-axis tick labels
ax_right.tick_params(axis='y', labelsize=16)  # y-axis tick labels

plt.tight_layout()
plt.savefig('/Users/jae35/Desktop/JULES_test_data/q10_comparisons.png', dpi=300, bbox_inches='tight')
plt.close()
#plt.show()