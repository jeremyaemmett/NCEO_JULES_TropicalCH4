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

scale_folder = "scaled" if apply_scale_factor else "unscaled"

print("Using:", scale_folder, "data")
print("Looking in:", directory)
print()


# ============================================================
# FIND INPUT FILES
# ============================================================

files = []

for subdir in sorted(directory.iterdir()):

    if not subdir.is_dir():
        continue

    name = subdir.name

    if not name.startswith("u-dk105_"):
        continue

    try:
        code = name.split("_")[1]

        if len(code) != 4:
            print(
                "WARNING:",
                name,
                "does not contain 4 digits"
            )
            continue

        substrate = code[0]
        q10 = code[1]
        soilmap = code[2]
        dynamics = code[3]

    except IndexError:
        continue

    filepath = (
        subdir
        / "plots"
        / "output"
        / scale_folder
        / "fch4_wetl"
        / "_arealmean_tseries.txt"
    )

    if filepath.exists():

        print(
            f"Found {name}: "
            f"substrate={substrate}, "
            f"Q10={q10}, "
            f"soilmap={soilmap}, "
            f"plants={dynamics}"
        )

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

    else:

        print(
            "NOT FOUND:",
            filepath
        )


# ============================================================
# DIAGNOSTICS
# ============================================================

print()
print("===============================================")
print("Suites plotted:", len(files))

print(
    "Substrate codes found:",
    sorted(set(f[1] for f in files))
)

print(
    "Q10 codes found:",
    sorted(set(f[2] for f in files))
)

print(
    "Soil map codes found:",
    sorted(set(f[3] for f in files))
)

print(
    "Plant modes found:",
    sorted(set(f[4] for f in files))
)

print("===============================================")


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


# ------------------------------------------------------------
# Soil map labels
# ------------------------------------------------------------

soil_labels = {
    "0": "Standard",
    "1": "Oxi + Ulti"
}


# ------------------------------------------------------------
# Plant dynamics
#
# 0 = Competitive
# 1 = Non-competitive
# ------------------------------------------------------------

dynamics_alpha = {
    "0": 0.60,
    "1": 0.60
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
# LOAD ALL DATA
# ============================================================

loaded_data = []

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

    loaded_data.append(
        (
            name,
            substrate,
            q10,
            soilmap,
            dynamics,
            filepath,
            y
        )
    )


# ============================================================
# CHECK DATA
# ============================================================

if len(loaded_data) == 0:

    raise RuntimeError(
        f"No input files found in "
        f"'{scale_folder}' folders."
    )


# ============================================================
# MASTER ENSEMBLE FULL SPREAD
#
# ALL simulations from ALL suites.
#
# For each month:
#
#   Box       = 25th to 75th percentile
#   Median    = median
#   Whiskers  = minimum to maximum
#
# This distribution is shown as the large background
# box-and-whisker in every panel.
# ============================================================

all_data = np.vstack(
    [
        item[6]
        for item in loaded_data
    ]
)

series_length = all_data.shape[1]

if series_length != 12:

    raise ValueError(
        "Expected 12 monthly values."
    )


x = np.arange(series_length)


# One distribution for each month across ALL simulations
ensemble_monthly_data = [
    all_data[:, month]
    for month in range(12)
]


print()
print("===============================================")
print("MASTER ENSEMBLE")
print("Members:", len(loaded_data))
print("Length:", series_length)
print("Calculated across ALL suites")
print("Each monthly box contains ALL simulations")
print("Box: 25th–75th percentile")
print("Centre line: median")
print("Whiskers: minimum–maximum")
print("===============================================")


# ============================================================
# CREATE 2 × 2 PANEL
# ============================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 9),
    sharex=True,
    sharey=True
)


soilmaps = ["0", "1"]
dynamics_modes = ["0", "1"]


# ============================================================
# PLOT EACH PANEL
# ============================================================

for row, soilmap in enumerate(soilmaps):

    for col, dynamics in enumerate(dynamics_modes):

        ax = axes[row, col]


        # ----------------------------------------------------
        # Remove panel borders
        # ----------------------------------------------------

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)


        # ----------------------------------------------------
        # Grey panel background
        # ----------------------------------------------------

        ax.set_facecolor("gainsboro")
        ax.patch.set_alpha(0.75)


        # ----------------------------------------------------
        # Select panel data
        # ----------------------------------------------------

        panel_data = [
            item
            for item in loaded_data
            if item[3] == soilmap
            and item[4] == dynamics
        ]


        print(
            f"\nPanel: "
            f"Soil map={soil_labels[soilmap]}, "
            f"Plants={dynamics_labels[dynamics]}"
        )

        print(
            "  Number of series:",
            len(panel_data)
        )


        # ====================================================
        # MASTER ENSEMBLE FULL-SPREAD BOX WHISKERS
        # ====================================================
        #
        # One large background box per month.
        #
        # ALL simulations are included:
        #
        #   - all substrates
        #   - all Q10 values
        #   - all soil maps
        #   - all plant dynamics
        #
        # Box:
        #   25th -> 75th percentile
        #
        # Median:
        #   median of all simulations
        #
        # Whiskers:
        #   minimum -> maximum
        #
        # These boxes are deliberately large and sit
        # behind the coloured substrate boxes.
        # ====================================================

        ax.boxplot(
            ensemble_monthly_data,

            positions=x,

            widths=0.85,

            # Full spread:
            # minimum to maximum
            whis=(0, 100),

            patch_artist=True,

            boxprops=dict(
                facecolor="white",
                edgecolor="gray",
                alpha=0.85,
                linewidth=1.3
            ),

            medianprops=dict(
                color="gray",
                linewidth=2.0
            ),

            whiskerprops=dict(
                color="gray",
                linewidth=1.2,
                alpha=0.9
            ),

            capprops=dict(
                color="gray",
                linewidth=1.2,
                alpha=0.9
            ),

            showfliers=False,

            # Behind substrate boxes
            zorder=1
        )


        # ====================================================
        # BUILD SUBSTRATE-SPECIFIC DATA
        # ====================================================

        data = {}

        for (
            name,
            substrate,
            q10,
            soilmap_code,
            dynamics_code,
            filepath,
            y
        ) in panel_data:

            if substrate not in data:

                data[substrate] = []

            data[substrate].append(y)


        # ====================================================
        # BOXPLOT POSITIONING
        # ====================================================

        substrate_offsets = {
            "0": -0.25,
            "1":  0.00,
            "2":  0.25
        }

        box_width = 0.25


        # ====================================================
        # SUBSTRATE BOXPLOTS
        # ====================================================

        for substrate in substrates:

            if substrate not in data:
                continue

            series = data[substrate]

            if len(series) == 0:
                continue

            series_array = np.vstack(series)

            positions = (
                x
                + substrate_offsets[substrate]
            )


            ax.boxplot(
                series_array,

                positions=positions,

                widths=box_width,

                # Full spread for each substrate
                whis=(0, 100),

                patch_artist=True,

                boxprops=dict(
                    facecolor=color_map[substrate],
                    edgecolor="black",
                    alpha=dynamics_alpha[dynamics],
                    linewidth=1.2
                ),

                medianprops=dict(
                    color="black",
                    linewidth=1.3
                ),

                whiskerprops=dict(
                    color="black",
                    linewidth=1,
                    alpha=dynamics_alpha[dynamics]
                ),

                capprops=dict(
                    color="black",
                    linewidth=1,
                    alpha=dynamics_alpha[dynamics]
                ),

                showfliers=False,

                # Above ensemble background
                zorder=4
            )


        # ====================================================
        # GRID
        # ====================================================

        ax.grid(
            alpha=0.35,
            linewidth=0.8,
            color="gray",
            zorder=2
        )


# ============================================================
# COLUMN HEADERS
# ============================================================

for col, dynamics in enumerate(dynamics_modes):

    axes[0, col].set_title(
        dynamics_labels[dynamics],
        pad=24,
        fontsize=14,
        fontweight="normal",
        fontstyle="italic"
    )


# ============================================================
# MASTER PLANT SCHEME LABEL
# ============================================================

fig.text(
    0.60,
    0.888,
    "Plant Dynamics",
    ha="center",
    va="center",
    fontsize=16,
    fontstyle="italic"
)


# ============================================================
# ROW LABELS
# ============================================================

for row, soilmap in enumerate(soilmaps):

    axes[row, 0].annotate(
        soil_labels[soilmap],
        xy=(-0.25, 0.5),
        xycoords="axes fraction",
        rotation=0,
        ha="right",
        va="center",
        fontsize=14,
        fontweight="normal",
        fontstyle="italic"
    )


# ============================================================
# MASTER SOIL MAP LABEL
# ============================================================

fig.text(
    0.089,
    0.48,
    "Soil Map",
    ha="center",
    va="center",
    rotation=0,
    fontsize=16,
    fontstyle="italic"
)


# ============================================================
# X AXIS
# ============================================================

for ax in axes.flat:

    ax.set_xticks(range(12))
    ax.set_xticklabels(months)


axes[1, 0].set_xlabel(
    "Month",
    fontsize=15
)

axes[1, 1].set_xlabel(
    "Month",
    fontsize=15
)

axes[1, 0].xaxis.labelpad = 12
axes[1, 1].xaxis.labelpad = 12


# ============================================================
# Y AXIS
# ============================================================

axes[0, 0].set_ylabel(
    "f$_{CH4}$",
    fontsize=16
)

axes[1, 0].set_ylabel(
    "f$_{CH4}$",
    fontsize=16
)

axes[0, 0].yaxis.labelpad = 12
axes[1, 0].yaxis.labelpad = 12


# ============================================================
# OVERALL TITLE
# ============================================================

fig.text(
    0.055,
    0.965,
    f"Global Mean f$_{{CH4}}$ - "
    f"{scale_folder.capitalize()}",
    ha="left",
    va="center",
    fontsize=16,
    fontweight="bold"
)


# ============================================================
# LEGEND HANDLES
# ============================================================

# ------------------------------------------------------------
# Substrate legend
# ------------------------------------------------------------

substrate_handles = [

    Line2D(
        [0],
        [0],
        color=color_map[s],
        linewidth=4,
        alpha=0.85,
        label=substrate_labels[s]
    )

    for s in substrates

]


# ------------------------------------------------------------
# Ensemble legend
#
# No separate min-max legend entry because the whiskers
# are already self-explanatory as part of the boxplot.
# ------------------------------------------------------------

ensemble_box_handle = Patch(
    facecolor="white",
    edgecolor="gray",
    alpha=0.85,
    label="Full ensemble: 25–75%"
)


ensemble_median_handle = Line2D(
    [0],
    [0],
    color="gray",
    linewidth=2,
    label="Ensemble median"
)


# ============================================================
# FLOATING LEGENDS IN FIRST PANEL
# ============================================================

# ------------------------------------------------------------
# Full ensemble legend
# ------------------------------------------------------------

ensemble_legend = axes[0, 0].legend(
    handles=[
        ensemble_box_handle,
        ensemble_median_handle
    ],
    loc="upper left",
    bbox_to_anchor=(0.02, 0.98),
    frameon=False,
    fontsize=11,
    borderpad=0.0,
    handlelength=1.8,
    handleheight=0.8,
    handletextpad=0.6,
    labelspacing=0.4
)

axes[0, 0].add_artist(
    ensemble_legend
)


# ------------------------------------------------------------
# Substrate legend
# ------------------------------------------------------------

axes[0, 0].legend(
    handles=substrate_handles,
    title="Substrate",
    loc="upper left",
    bbox_to_anchor=(0.02, 0.76),
    frameon=False,
    fontsize=11,
    title_fontsize=11,
    borderpad=0.0,
    handlelength=1.0,
    handletextpad=0.6,
    labelspacing=0.4
)


# ============================================================
# LAYOUT
# ============================================================

plt.tight_layout(
    rect=[0.055, 0.045, 0.99, 0.91],
    pad=0.8,
    w_pad=1.0,
    h_pad=1.2
)


# ============================================================
# SAVE
# ============================================================

output_directory = directory / scale_folder

output_directory.mkdir(
    parents=True,
    exist_ok=True
)


output_file = (
    output_directory
    / "monthly_full_spread_boxwhisker_dynamics_2x2.png"
)


plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight",
    pad_inches=0.04
)


print()
print("Saved:", output_file)


plt.show()