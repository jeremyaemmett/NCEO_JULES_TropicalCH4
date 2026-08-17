from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


# ============================================================
# SETTINGS
# ============================================================

directory = Path("/Users/jae35/Desktop/JULES_test_data/ID_suites")

# True  = use scaled data
# False = use unscaled data
apply_scale_factor = True

# Automatically select the correct folder
scale_folder = "scaled" if apply_scale_factor else "unscaled"


# ============================================================
# FIND INPUT FILES
# ============================================================

files = []

for subdir in sorted(directory.iterdir()):

    if not subdir.is_dir():
        continue

    name = subdir.name

    # Only consider suite directories
    # e.g. u-dk105_0110
    if not name.startswith("u-dk105_"):
        continue

    try:
        code = name.split("_")[1]

        if len(code) != 4:
            continue

        substrate = code[0]
        q10 = code[1]
        soilmap = code[2]
        dynamics = code[3]

    except IndexError:
        continue

    # Read from either:
    #
    # plots/output/scaled/fch4_wetl/
    #
    # or:
    #
    # plots/output/unscaled/fch4_wetl/

    filepath = (
        subdir
        / "plots"
        / "output"
        / scale_folder
        / "fch4_wetl"
        / "_arealmean_tseries.txt"
    )

    if filepath.exists():

        files.append(
            (
                name,
                substrate,
                q10,
                soilmap,
                dynamics,
                filepath
            )
        )


print("========================================")
print("Scale mode:", scale_folder)
print("Suites plotted:", len(files))
print("========================================")


# ============================================================
# VISUAL ENCODING
# ============================================================

substrates = ["0", "1", "2"]

color_map = {
    "0": "saddlebrown",
    "1": "forestgreen",
    "2": "royalblue"
}

substrate_labels = {
    "0": "Carbon",
    "1": "NPP",
    "2": "Resps"
}


soil_labels = {
    "0": "Standard",
    "1": "Oxi + Ulti"
}


# Plant dynamics
#
# 0 = non-dynamic
# 1 = dynamic
#
# Dynamic boxes and whiskers are made more transparent.

dynamics_alpha = {
    "0": 0.65,
    "1": 0.30
}

dynamics_labels = {
    "0": "Competitive",
    "1": "Non-competitive"
}


months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


# ============================================================
# READ DATA
# ============================================================

all_data = []
metadata = []

for (
    name,
    substrate,
    q10,
    soilmap,
    dynamics,
    filepath
) in files:

    y = np.loadtxt(filepath)

    if len(y) != 12:
        raise ValueError(
            f"{filepath} does not contain 12 months"
        )

    all_data.append(y)

    metadata.append(
        (
            substrate,
            soilmap,
            q10,
            dynamics
        )
    )


if len(all_data) == 0:
    raise RuntimeError(
        f"No input files found in '{scale_folder}' folders."
    )


all_data = np.array(all_data)
metadata = np.array(metadata)

x = np.arange(12)


# ============================================================
# ENSEMBLE MEAN ±1 SD
# ============================================================

ensemble_mean = np.mean(
    all_data,
    axis=0
)

ensemble_std = np.std(
    all_data,
    axis=0
)

ensemble_lower = (
    ensemble_mean - ensemble_std
)

ensemble_upper = (
    ensemble_mean + ensemble_std
)


# ============================================================
# SIX SUBSTRATE × SOIL COMBINATIONS
# ============================================================

combo_order = [
    ("0", "0"),
    ("1", "0"),
    ("2", "0"),
    ("0", "1"),
    ("1", "1"),
    ("2", "1")
]

combo_data = {}

for combo in combo_order:

    substrate, soil = combo

    combo_data[combo] = {}

    for dynamics in ["0", "1"]:

        mask = (
            (metadata[:, 0] == substrate) &
            (metadata[:, 1] == soil) &
            (metadata[:, 3] == dynamics)
        )

        combo_data[combo][dynamics] = all_data[mask]


# ============================================================
# PLOT
# ============================================================

fig, ax = plt.subplots(
    figsize=(16, 8)
)


# ============================================================
# POSITIONING
# ============================================================
#
# Overall structure:
#
#          Standard soil             Oxi + Ulti
#
#       C       N       R         C       N       R
#      ND D    ND D    ND D      ND D    ND D    ND D
#
# Each dynamic/non-dynamic pair sits immediately beside
# the corresponding box.
#


# Position of the three substrates within each soil group

substrate_offsets = {
    "0": -0.12,
    "1":  0.00,
    "2":  0.12
}


# Position of the two soil-map groups

soil_centers = {
    "0": -0.24,
    "1":  0.24
}


# Small offset separating non-dynamic and dynamic boxes

dynamics_offsets = {
    "0": -0.030,   # non-dynamic
    "1":  0.030    # dynamic
}


# Width of each individual box

box_width = 0.055


# ============================================================
# BOXPLOTS
# ============================================================

for combo in combo_order:

    substrate, soil = combo

    for dynamics in ["0", "1"]:

        data = combo_data[combo][dynamics]

        # Skip combinations for which there are no suites

        if data.shape[0] == 0:
            continue

        base_offset = (
            soil_centers[soil]
            + substrate_offsets[substrate]
        )

        offset = (
            base_offset
            + dynamics_offsets[dynamics]
        )

        positions = x + offset

        alpha = dynamics_alpha[dynamics]

        ax.boxplot(

            data,

            positions=positions,

            widths=box_width,

            # Whiskers extend to extreme values

            whis=(0, 100),

            patch_artist=True,

            boxprops=dict(
                facecolor=color_map[substrate],
                edgecolor="black",
                hatch="///" if soil == "1" else "",
                alpha=alpha,
                linewidth=1.2
            ),

            medianprops=dict(
                color="black",
                linewidth=1.3
            ),

            whiskerprops=dict(
                color="black",
                linewidth=1,
                alpha=alpha
            ),

            capprops=dict(
                color="black",
                linewidth=1,
                alpha=alpha
            ),

            showfliers=False,

            zorder=4
        )


# ============================================================
# ENSEMBLE MEAN ±1 SD
# ============================================================

ax.fill_between(

    x,

    ensemble_lower,

    ensemble_upper,

    color="grey",

    alpha=0.30,

    zorder=2
)


ax.plot(

    x,

    ensemble_mean,

    color="black",

    linewidth=3,

    zorder=5
)


# ============================================================
# FORMATTING
# ============================================================

ax.set_xticks(x)

ax.set_xticklabels(months)

ax.set_xlabel("Month")

ax.set_ylabel("f$_{CH4}$")

ax.set_title(
    f"Global Mean f$_{{CH4}}$ Ensemble (2005) — "
    f"{scale_folder.capitalize()}"
)

ax.grid(
    alpha=0.3
)


# ============================================================
# LEGENDS
# ============================================================


# ------------------------------------------------------------
# Substrate legend
# ------------------------------------------------------------

substrate_handles = [

    Patch(
        facecolor=color_map[s],
        edgecolor="black",
        alpha=dynamics_alpha["0"],
        label=substrate_labels[s]
    )

    for s in substrates

]


# ------------------------------------------------------------
# Soil map legend
# ------------------------------------------------------------

soil_handles = [

    Patch(
        facecolor="white",
        edgecolor="black",
        hatch="///" if soil == "1" else "",
        label=soil_labels[soil]
    )

    for soil in ["0", "1"]

]


# ------------------------------------------------------------
# Plant dynamics legend
# ------------------------------------------------------------

dynamics_handles = [

    Patch(
        facecolor="grey",
        edgecolor="black",
        alpha=dynamics_alpha[d],
        label=dynamics_labels[d]
    )

    for d in ["0", "1"]

]


# ------------------------------------------------------------
# Ensemble legend
# ------------------------------------------------------------

summary_handles = [

    Line2D(
        [0],
        [0],
        color="black",
        linewidth=3,
        label="mean"
    ),

    Patch(
        facecolor="grey",
        alpha=0.30,
        label="±1 SD"
    )

]


# ============================================================
# SUBSTRATE LEGEND
# ============================================================

leg1 = ax.legend(

    handles=substrate_handles,

    title="Substrate",

    loc="upper left",

    bbox_to_anchor=(0.01, 0.99),

    frameon=False

)

ax.add_artist(leg1)


# ============================================================
# SOIL MAP LEGEND
# ============================================================

leg2 = ax.legend(

    handles=soil_handles,

    title="Soil map",

    loc="upper left",

    bbox_to_anchor=(0.10, 0.99),

    frameon=False

)

ax.add_artist(leg2)


# ============================================================
# PLANT DYNAMICS LEGEND
# ============================================================

leg3 = ax.legend(

    handles=dynamics_handles,

    title="Plants",

    loc="upper left",

    bbox_to_anchor=(0.19, 0.99),

    frameon=False

)

ax.add_artist(leg3)


# ============================================================
# ENSEMBLE LEGEND
# ============================================================

leg4 = ax.legend(

    handles=summary_handles,

    title="Ensemble",

    loc="upper left",

    bbox_to_anchor=(0.35, 0.99),

    frameon=False

)

ax.add_artist(leg4)


# ============================================================
# SAVE
# ============================================================

plt.tight_layout()


# Output goes directly into:
#
# ID_suites/scaled/
#
# or:
#
# ID_suites/unscaled/

output_dir = directory / scale_folder

output_dir.mkdir(
    parents=True,
    exist_ok=True
)


output_file = (
    output_dir
    / "monthly_mean_spread_boxwhisker_dynamics.png"
)


plt.savefig(

    output_file,

    dpi=300,

    bbox_inches="tight"

)


plt.close()


print("Saved:", output_file)
