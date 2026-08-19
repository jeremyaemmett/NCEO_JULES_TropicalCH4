from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


# =================================================
# SETTINGS
# =================================================

directory = Path("/Users/jae35/Desktop/JULES_test_data/ID_suites")

apply_scale_factor = True

scale_folder = "scaled" if apply_scale_factor else "unscaled"

print("Using:", scale_folder, "data")
print("Looking in:", directory)
print()


# =================================================
# FIND FILES
# =================================================

files = []

for subdir in sorted(directory.iterdir()):

    if not subdir.is_dir():
        continue

    name = subdir.name

    if not name.startswith("u-dk105_"):
        continue

    code = name.split("_")[1]

    if len(code) != 4:
        print("WARNING:", name, "does not contain 4 digits")
        continue

    substrate = code[0]
    q10 = code[1]
    soilmap = code[2]
    dynamics = code[3]

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
        print("NOT FOUND:", filepath)


# =================================================
# DIAGNOSTICS
# =================================================

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


# =================================================
# VISUAL ENCODING
# =================================================

substrates = ["0", "1", "2"]


# -------------------------------------------------
# Substrate = colour
# -------------------------------------------------

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


# -------------------------------------------------
# Q10 = line width
# -------------------------------------------------

q10_width = {
    "0": 1.0,
    "1": 1.7,
    "2": 2.4,
    "3": 3.1
}

q10_labels = {
    "0": "1.0",
    "1": "2.0",
    "2": "3.0",
    "3": "4.0"
}


# -------------------------------------------------
# Q10 = transparency
# -------------------------------------------------

q10_alpha = {
    "0": 0.35,
    "1": 0.55,
    "2": 0.75,
    "3": 0.95
}


# -------------------------------------------------
# Plot background
# -------------------------------------------------

panel_background="gainsboro"


# -------------------------------------------------
# Master ensemble strip
# -------------------------------------------------

ensemble_fill_color = "white"


# -------------------------------------------------
# Substrate fill transparency
# -------------------------------------------------

substrate_fill_alpha = 0.15


# -------------------------------------------------
# Row / column labels
# -------------------------------------------------

soil_labels = {
    "0": "Standard",
    "1": "Oxi + Ulti"
}

dynamics_labels = {
    "0": "Competitive",
    "1": "Non-competitive"
}


months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


# =================================================
# LOAD ALL DATA
# =================================================

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


# =================================================
# CHECK DATA
# =================================================

if len(loaded_data) == 0:
    raise RuntimeError("No data files were found.")


# =================================================
# MASTER ENSEMBLE ENVELOPE
# =================================================

all_series = np.vstack(
    [
        item[6]
        for item in loaded_data
    ]
)

series_length = all_series.shape[1]

master_lower = np.min(
    all_series,
    axis=0
)

master_upper = np.max(
    all_series,
    axis=0
)

master_x = np.arange(series_length)


print()
print("===============================================")
print("MASTER ENSEMBLE")
print("Members:", len(loaded_data))
print("Length:", series_length)
print("Calculated across ALL panels")
print("===============================================")


# =================================================
# CREATE 2 × 2 PANEL
# =================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 9),
    sharex=True,
    sharey=True
)


soilmaps = ["0", "1"]
dynamics_modes = ["0", "1"]


# =================================================
# PLOT EACH PANEL
# =================================================

for row, soilmap in enumerate(soilmaps):

    for col, dynamics in enumerate(dynamics_modes):

        ax = axes[row, col]

        # Remove upper and right panel borders
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        # -------------------------------------------------
        # Grey panel background
        # -------------------------------------------------

        ax.set_facecolor(panel_background)
        ax.patch.set_alpha(0.75)


        # -------------------------------------------------
        # Select panel data
        # -------------------------------------------------

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


        # =================================================
        # MASTER ENSEMBLE STRIP
        # =================================================

        ax.fill_between(
            master_x,
            master_lower,
            master_upper,
            color=ensemble_fill_color,
            alpha=1.0,
            linewidth=0,
            zorder=0
        )


        # =================================================
        # BUILD SUBSTRATE-SPECIFIC DATA
        # =================================================

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
                data[substrate] = {}

            data[substrate][q10] = y


        # =================================================
        # SUBSTRATE COLOUR STRIPS
        # =================================================

        x = np.arange(series_length)

        for substrate in substrates:

            if substrate not in data:
                continue

            series = list(
                data[substrate].values()
            )

            if len(series) == 0:
                continue

            series_array = np.vstack(series)

            lower = np.min(
                series_array,
                axis=0
            )

            upper = np.max(
                series_array,
                axis=0
            )

            ax.fill_between(
                x,
                lower,
                upper,
                color=color_map[substrate],
                alpha=substrate_fill_alpha,
                linewidth=0,
                zorder=1
            )


        # =================================================
        # INDIVIDUAL MEMBER LINES
        # =================================================

        for (
            name,
            substrate,
            q10,
            soilmap_code,
            dynamics_code,
            filepath,
            y
        ) in panel_data:

            ax.plot(
                x,
                y,
                color=color_map[substrate],
                linewidth=q10_width[q10],
                alpha=q10_alpha[q10],
                zorder=3
            )


        # =================================================
        # GRID
        # =================================================

        ax.grid(
            alpha=0.35,
            linewidth=0.8,
            color="gray",
            zorder=2
        )


# =================================================
# COLUMN HEADERS
# =================================================

for col, dynamics in enumerate(dynamics_modes):

    axes[0, col].set_title(
        dynamics_labels[dynamics],
        pad=24,
        fontsize=14,
        fontweight="normal",
        fontstyle="italic"
    )


# =================================================
# MASTER PLANT SCHEME LABEL
# =================================================

fig.text(
    0.60,
    0.888,
    "Plant Dynamics",
    ha="center",
    va="center",
    fontsize=16,
    fontstyle="italic"
)

# =================================================
# ROW LABELS
# =================================================

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


# =================================================
# MASTER SOIL MAP LABEL
# =================================================

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


# =================================================
# X AXIS
# =================================================

if series_length == 12:

    for ax in axes.flat:

        ax.set_xticks(range(12))
        ax.set_xticklabels(months)


axes[1, 0].set_xlabel("Month", fontsize=15)
axes[1, 1].set_xlabel("Month", fontsize=15)
axes[1, 0].xaxis.labelpad = 12
axes[1, 1].xaxis.labelpad = 12


# =================================================
# Y AXIS
# =================================================

axes[0, 0].set_ylabel("f$_{CH4}$", fontsize=16)
axes[1, 0].set_ylabel("f$_{CH4}$", fontsize=16)
axes[0, 0].yaxis.labelpad = 12
axes[1, 0].yaxis.labelpad = 12


# =================================================
# OVERALL TITLE
# =================================================

fig.text(
    0.055,
    0.965,
    f"Global Mean f$_{{CH4}}$ - {scale_folder.capitalize()}",
    ha="left",
    va="center",
    fontsize=16,
    fontweight="bold"
)


# =================================================
# LEGEND HANDLES
# =================================================

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


q10_handles = [
    Line2D(
        [0],
        [0],
        color="black",
        linewidth=q10_width[q],
        alpha=q10_alpha[q],
        label=q10_labels[q]
    )
    for q in sorted(q10_width)
]


# =================================================
# FLOATING LEGENDS IN FIRST PANEL
# =================================================

ensemble_patch = Patch(
    facecolor="white",
    edgecolor="none",
    label="Full ensemble spread",
)


# -------------------------------------------------
# Full ensemble legend
# -------------------------------------------------

ensemble_legend = axes[0, 0].legend(
    handles=[ensemble_patch],
    loc="upper left",
    bbox_to_anchor=(0.02, 0.98),
    frameon=False,
    fontsize=11,
    borderpad=0.0,
    handlelength=1.8,
    handleheight=0.8,
    handletextpad=0.6
)

axes[0, 0].add_artist(ensemble_legend)


# -------------------------------------------------
# Substrate legend
# -------------------------------------------------

substrate_legend = axes[0, 0].legend(
    handles=substrate_handles,
    title="Substrate",
    loc="upper left",
    bbox_to_anchor=(0.02, 0.84),
    frameon=False,
    fontsize=11,
    title_fontsize=11,
    borderpad=0.0,
    handlelength=1.0,
    handletextpad=0.6,
    labelspacing=0.4
)

axes[0, 0].add_artist(substrate_legend)


# -------------------------------------------------
# Q10 legend
# -------------------------------------------------

axes[0, 0].legend(
    handles=q10_handles,
    title="Q10",
    loc="upper left",
    bbox_to_anchor=(0.21, 0.86),
    frameon=False,
    fontsize=11,
    title_fontsize=11,
    borderpad=0.0,
    handlelength=1.0,
    handletextpad=0.6,
    labelspacing=0.4
)


# =================================================
# LAYOUT
# =================================================

# Important:
# Keep the left margin small. The previous value of
# rect=[0.12, ...] was creating a large blank region.

plt.tight_layout(
    rect=[0.055, 0.045, 0.99, 0.91],
    pad=0.8,
    w_pad=1.0,
    h_pad=1.2
)


# =================================================
# SAVE
# =================================================

output_directory = directory / scale_folder

output_directory.mkdir(
    parents=True,
    exist_ok=True
)


output_file = (
    output_directory
    / "monthly_mean_soilmap_plantmode_2x2_substrate_ensemble_filled.png"
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