from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.lines import Line2D
import numpy as np

# -------------------------
# CONFIG
# -------------------------
base_path = '/Users/jae35/Desktop/JULES_test_data/JASMIN_output_'
variable = 'fch4_wetl'

suite_groups = {
    "Soil Carbon": ['u-dk105_10_n2', 'u-dk105_7_n2', 'u-dk105_4_n2', 'u-dk105_1_n2'],
    "NPP": ['u-dk105_11_n2', 'u-dk105_8_n2', 'u-dk105_5_n2', 'u-dk105_2_n2'],
    "Soil Resp.": ['u-dk105_12_n2', 'u-dk105_9_n2', 'u-dk105_6_n2', 'u-dk105_3_n2'],
}

suite_groups = {
    "Soil Carbon": ['u-dk105_4_n3', 'u-dk105_3_n3', 'u-dk105_2_n3', 'u-dk105_1_n3'],
    "NPP": ['u-dk105_8_n3', 'u-dk105_7_n3', 'u-dk105_6_n3', 'u-dk105_5_n3'],
    "Soil Resp.": ['u-dk105_12_n3', 'u-dk105_11_n3', 'u-dk105_10_n3', 'u-dk105_9_n3'],
}

q10_map = {
    'u-dk105_4_n3': 4.0, 'u-dk105_3_n3': 3.0, 'u-dk105_2_n3': 2.0, 'u-dk105_1_n3': 1.0,
    'u-dk105_8_n3': 4.0, 'u-dk105_7_n3': 3.0, 'u-dk105_6_n3': 2.0, 'u-dk105_5_n3': 1.0,
    'u-dk105_12_n3': 4.0, 'u-dk105_11_n3': 3.0, 'u-dk105_10_n3': 2.0, 'u-dk105_9_n3': 1.0,
}

linestyles = {"Soil Carbon": "-", "NPP": "--", "Soil Resp.": ":"}
markers = {"Soil Carbon": "o", "NPP": "s", "Soil Resp.": "^"}

# Flatten
all_suites = []
suite_to_group = {}
for g, slist in suite_groups.items():
    for s in slist:
        all_suites.append(s)
        suite_to_group[s] = g

# -------------------------
# COLOR SETUP (FIXED)
# -------------------------
unique_q10 = sorted(set(q10_map.values()), reverse=True)
cmap = cm.get_cmap('copper_r', len(unique_q10))

q10_to_color = {}
for i, q in enumerate(unique_q10):
    rgba = np.array(cmap(i))        # <-- FIX: convert to array
    rgba[:3] *= 0.7                # darken RGB only
    q10_to_color[q] = rgba

# -------------------------
# FIGURE
# -------------------------
fig, (ax_left, ax_right) = plt.subplots(
    1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [2, 1]}
)

for ax in [ax_left, ax_right]:
    ax.set_facecolor('white')
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")

# -------------------------
# LOOP
# -------------------------
for suite in all_suites:

    group = suite_to_group[suite]
    q10 = q10_map[suite]
    color = q10_to_color[q10]

    path = f"{base_path}{suite}/plots/output/{variable}/_arealmean_tseries.txt"
    integ_file = f"{base_path}{suite}/plots/output/{variable}/_zonalintg_tseries.txt"

    areal = np.loadtxt(path).T
    integ = np.loadtxt(integ_file).T

    integ_cumsum = np.cumsum(integ, axis=1)
    final_val = np.nansum(integ_cumsum, axis=0)[-1]

    time = np.arange(len(areal))

    # LEFT
    ax_left.plot(
        time,
        areal,
        color=color,
        linewidth=3,
        linestyle=linestyles[group]
    )

    mid = len(time) // 2
    ax_left.text(
        time[mid],
        areal[mid] + 0.0015,
        f"$q_{{10}}$ = {q10}",
        color=color,
        fontsize=14,
        ha='center',
        fontstyle='italic',
        path_effects=[pe.withStroke(linewidth=3, foreground='white')]
    )

    # RIGHT
    ax_right.plot(
        q10,
        final_val,
        marker=markers[group],
        linestyle='',
        color=color
    )

# -------------------------
# LEFT FORMAT
# -------------------------
ax_left.set_title('   Areal mean', loc='left', fontsize=16, fontstyle='italic')
ax_left.set_xlabel('\nMonth', fontsize=18)
ax_left.set_ylabel(r"$10^{-9}\,\mathrm{kg\,m^{-2}\,s^{-1}}$")
ax_left.grid(True, color='lightgrey', linewidth=3, alpha=0.2)

months = ['J','F','M','A','M','J','J','A','S','O','N','D']
ax_left.set_xticks(np.arange(12))
ax_left.set_xticklabels(months, fontsize=18)

cmap_month = cm.get_cmap('rainbow', 12)
for i in range(12):
    ax_left.add_patch(Rectangle(
        (i - 0.5, -0.113),
        1.0,
        0.09,
        transform=ax_left.get_xaxis_transform(),
        color=cmap_month(i),
        alpha=0.3,
        clip_on=False
    ))

# -------------------------
# RIGHT FORMAT
# -------------------------
ax_right.set_title('   Annual areal cumulative', loc='left', fontsize=16, fontstyle='italic')
ax_right.set_xlabel("$q_{10}$", fontsize=18)
ax_right.set_ylabel(r"$\mathrm{kg\,yr^{-1}}$")
ax_right.grid(True, color='lightgrey', linewidth=3, alpha=0.2)

# -------------------------
# LEGENDS
# -------------------------
group_handles = [
    Line2D([0], [0], color='black',
           linestyle=linestyles[g],
           marker=markers[g],
           label=f"{g}")
    for g in suite_groups
]
ax_left.legend(handles=group_handles, title="Substrate", loc='upper left')

# -------------------------
# FINAL
# -------------------------
for ax in [ax_left, ax_right]:
    ax.tick_params(axis='both', labelsize=16)

plt.tight_layout()
plt.savefig('/Users/jae35/Desktop/JULES_test_data/q10_comparisons.png',
            dpi=300, bbox_inches='tight')
plt.close()