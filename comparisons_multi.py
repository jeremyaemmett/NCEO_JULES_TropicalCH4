from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import numpy as np

# -------------------------
# CONFIG
# -------------------------
base_path = '/Users/jae35/Desktop/JULES_test_data/JASMIN_output_'
variable = 'fch4_wetl'

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

# -------------------------
# PREP
# -------------------------
all_suites = []
suite_to_group = {}

for g, slist in suite_groups.items():
    for s in slist:
        all_suites.append(s)
        suite_to_group[s] = g

unique_q10 = sorted(set(q10_map.values()), reverse=True)

cmap = cm.get_cmap('copper_r', len(unique_q10))
q10_to_color = {}

for i, q in enumerate(unique_q10):
    rgba = np.array(cmap(i))
    rgba[:3] *= 0.7
    q10_to_color[q] = rgba

# -------------------------
# LOAD DATA
# -------------------------
data_store = []
q10_series = {q: [] for q in unique_q10}
group_points = {g: [] for g in suite_groups}

for suite in all_suites:

    group = suite_to_group[suite]
    q10 = q10_map[suite]

    path = f"{base_path}{suite}/plots/output/{variable}/_arealmean_tseries.txt"
    integ_file = f"{base_path}{suite}/plots/output/{variable}/_zonalintg_tseries.txt"

    areal = np.loadtxt(path).T
    integ = np.loadtxt(integ_file).T

    integ_cumsum = np.cumsum(integ, axis=1)
    final_val = np.nansum(integ_cumsum, axis=0)[-1]

    data_store.append({
        "suite": suite,
        "group": group,
        "q10": q10,
        "areal": areal,
        "final": final_val
    })

    q10_series[q10].append(areal)
    group_points[group].append((q10, final_val))

time = np.arange(len(data_store[0]["areal"]))

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
# Q10 BANDS + LABELS
# -------------------------
for q10, series_list in q10_series.items():

    data = np.vstack(series_list)
    ymin = np.nanmin(data, axis=0)
    ymax = np.nanmax(data, axis=0)

    ax_left.fill_between(
        time,
        ymin,
        ymax,
        color=q10_to_color[q10],
        alpha=0.15,
        zorder=1
    )

    mid = len(time) // 2
    y_mid = (ymin[mid] + ymax[mid]) / 2

    ax_left.text(
        time[mid],
        y_mid,
        f"$q_{{10}} = {q10}$",
        color=q10_to_color[q10],
        fontsize=14,
        ha='center',
        va='center',
        fontstyle='italic',
        zorder=3,
        path_effects=[pe.withStroke(linewidth=3, foreground='white')]
    )

# -------------------------
# LEFT: LINES
# -------------------------
for d in data_store:
    ax_left.plot(
        time,
        d["areal"],
        color=q10_to_color[d["q10"]],
        linestyle=linestyles[d["group"]],
        linewidth=3,
        zorder=2
    )

# -------------------------
# RIGHT: LINES + COLOURED MARKERS
# -------------------------
for group, pts in group_points.items():

    pts_sorted = sorted(pts, key=lambda x: x[0])
    q_vals = [p[0] for p in pts_sorted]
    y_vals = [p[1] for p in pts_sorted]

    # connecting line (substrate)
    ax_right.plot(
        q_vals,
        y_vals,
        linestyle=linestyles[group],
        color='black',
        linewidth=2,
        zorder=1
    )

    # coloured markers (q10)
    for q, y in pts_sorted:
        ax_right.plot(
            q,
            y,
            marker=markers[group],
            linestyle='',
            color=q10_to_color[q],
            markersize=8,
            markeredgecolor='black',
            markeredgewidth=0.5,
            zorder=2
        )

# -------------------------
# FORMATTING
# -------------------------
ax_left.set_title(
    r"$\mathbf{Monthly\ mean\ } \mathbf{F}_{\mathbf{CH_4}}$" + "\n" + "full-region",
    loc='left',
    fontsize=14
)
ax_left.set_xlabel('\nMonth', fontsize=16)
ax_left.set_ylabel(r"$10^{-9}\,\mathrm{kg\,m^{-2}\,s^{-1}}$", fontsize=18)
ax_left.grid(True, color='lightgrey', linewidth=3, alpha=0.2)

months = ['J','F','M','A','M','J','J','A','S','O','N','D']
ax_left.set_xticks(np.arange(12))
ax_left.set_xticklabels(months, fontsize=18)

cmap_month = cm.get_cmap('rainbow', 12)
# Add month-colored rectangles
for i in range(12):
    rect = Rectangle(
        (i - 0.5, -0.113),  # align with tick
        1.0,               # width = 1 month
        0.09,              # height of strip
        transform=ax_left.get_xaxis_transform(),
        color=cmap_month(i),
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

ax_right.set_title(
    r"$\mathbf{Annual\ cumulative\ } \mathbf{F}_{\mathbf{CH_4}}$" + "\n" + "full-region",
    loc='left',
    fontsize=14
)
ax_right.set_xlabel("$q_{10}$", fontsize=18)
ax_right.set_ylabel(r"$\mathrm{kg\,yr^{-1}}$", fontsize=18)
ax_right.grid(True, color='lightgrey', linewidth=3, alpha=0.2)

# -------------------------
# LEGEND
# -------------------------
group_handles = [
    Line2D([0], [0], color='black',
           linestyle=linestyles[g],
           marker=markers[g],
           label=g)
    for g in suite_groups
]

ax_left.legend(handles=group_handles, title="Substrate", loc='upper center')

# -------------------------
# FINAL
# -------------------------
for ax in [ax_left, ax_right]:
    ax.tick_params(axis='both', labelsize=16)

plt.tight_layout()
plt.savefig('/Users/jae35/Desktop/JULES_test_data/q10_comparisons.png',
            dpi=300, bbox_inches='tight')
plt.close()