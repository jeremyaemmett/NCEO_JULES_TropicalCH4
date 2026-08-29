from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.colors import (
    to_rgba,
    LinearSegmentedColormap,
    Normalize
)
from matplotlib.cm import ScalarMappable


# =================================================
# SETTINGS
# =================================================

directory = Path("/Users/jae35/Desktop/JULES_test_data/test")

apply_scale_factor = True
mode_folder = "band"

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

    filepath = (
        subdir
        / "plots"
        / mode_folder
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


# =================================================
# DIAGNOSTICS
# =================================================

print()
print("===============================================")
print(
    "Suites plotted:",
    len(files)
)

print(
    "Substrate codes found:",
    sorted(
        set(
            f[1]
            for f in files
        )
    )
)

print(
    "Q10 codes found:",
    sorted(
        set(
            f[2]
            for f in files
        )
    )
)

print(
    "Soil map codes found:",
    sorted(
        set(
            f[3]
            for f in files
        )
    )
)

print(
    "Plant modes found:",
    sorted(
        set(
            f[4]
            for f in files
        )
    )
)

print(
    "==============================================="
)


# =================================================
# VISUAL ENCODING
# =================================================

substrates = [
    "0",
    "1",
    "2"
]


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
# Q10 = CONTINUOUS OPACITY
# -------------------------------------------------

# Q10 codes:
#
# 0 -> 1.0
# 1 -> 2.0
# 2 -> 3.0
# 3 -> 4.0
#
# Opacity changes continuously between these values.

q10_alpha = {
    "0": 0.20,
    "1": 0.35,
    "2": 0.60,
    "3": 0.90
}


q10_labels = {
    "0": "1.0",
    "1": "2.0",
    "2": "3.0",
    "3": "4.0"
}


# -------------------------------------------------
# Plot background
# -------------------------------------------------

panel_background = "gainsboro"


# -------------------------------------------------
# Full ensemble
# -------------------------------------------------

ensemble_fill_color = "white"


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
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
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

    y = np.asarray(
        np.loadtxt(filepath),
        dtype=float
    )

    if y.ndim != 1:
        y = y.squeeze()

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

    raise RuntimeError(
        "No data files were found."
    )


# =================================================
# CHECK SERIES LENGTH
# =================================================

series_lengths = {
    len(item[6])
    for item in loaded_data
}


if len(series_lengths) != 1:

    raise RuntimeError(
        "Not all time series have the same length: "
        + str(
            sorted(series_lengths)
        )
    )


series_length = next(
    iter(series_lengths)
)


# =================================================
# MASTER ENSEMBLE ENVELOPE
# =================================================

all_series = np.vstack(
    [
        item[6]
        for item in loaded_data
    ]
)


master_x = np.arange(
    series_length
)


master_lower = np.min(
    all_series,
    axis=0
)


master_upper = np.max(
    all_series,
    axis=0
)


# =================================================
# GLOBAL Y LIMITS
#
# IMPORTANT:
#
# The full ensemble envelope determines the bottom
# and top of every panel.
#
# This prevents the lower structure of a substrate
# band from being visually clipped by the image.
# =================================================

global_y_min = np.min(
    master_lower
) - 0.005


global_y_max = np.max(
    master_upper
) + 0.005


# Small numerical padding only.
# This does NOT alter the ensemble boundary.
y_padding = (
    global_y_max
    - global_y_min
) * 0.01


plot_y_min = global_y_min - y_padding
plot_y_max = global_y_max + y_padding


print()
print("===============================================")
print("MASTER ENSEMBLE")
print(
    "Members:",
    len(loaded_data)
)
print(
    "Length:",
    series_length
)
print(
    "Global minimum:",
    global_y_min
)
print(
    "Global maximum:",
    global_y_max
)
print(
    "===============================================")


# =================================================
# FUNCTION:
# CONTINUOUS Q10 OPACITY BAND
# =================================================

def plot_smooth_q10_band(
    ax,
    x,
    q10_data,
    color,
    alpha_map,
    y_axis_min,
    y_axis_max,
    zorder=1
):
    """
    Draw a continuous Q10 opacity field.

    The Q10 trajectories form the actual boundaries
    of the substrate band.

    Opacity is continuously interpolated between
    the Q10 trajectories.

    No individual Q10 lines are drawn.
    No polygon edges are drawn.
    No pcolormesh is used.
    """

    # =================================================
    # SORT Q10 CODES NUMERICALLY
    # =================================================

    q10_codes = sorted(
        q10_data.keys(),
        key=lambda q: int(q)
    )


    if len(q10_codes) < 2:
        return


    # =================================================
    # NUMERICAL Q10 VALUES
    # =================================================

    q10_values = np.array(
        [
            int(q)
            for q in q10_codes
        ],
        dtype=float
    )


    # =================================================
    # TRAJECTORIES
    # =================================================

    y_values = np.array(
        [
            q10_data[q]
            for q in q10_codes
        ],
        dtype=float
    )


    # =================================================
    # OPACITY VALUES
    # =================================================

    alpha_values = np.array(
        [
            alpha_map[q]
            for q in q10_codes
        ],
        dtype=float
    )


    # =================================================
    # HIGH-RESOLUTION X GRID
    # =================================================

    n_x = max(
        2400,
        series_length * 250
    )


    x_fine = np.linspace(
        x[0],
        x[-1],
        n_x
    )


    # =================================================
    # INTERPOLATE EACH Q10 TRAJECTORY
    # =================================================

    y_fine = np.empty(
        (
            len(q10_codes),
            n_x
        ),
        dtype=float
    )


    for i in range(
        len(q10_codes)
    ):

        y_fine[i] = np.interp(
            x_fine,
            x,
            y_values[i]
        )


    # =================================================
    # HIGH-RESOLUTION Y GRID
    # =================================================

    n_y = 1800


    y_grid = np.linspace(
        y_axis_min,
        y_axis_max,
        n_y
    )


    # =================================================
    # ALPHA FIELD
    # =================================================

    alpha_field = np.zeros(
        (
            n_y,
            n_x
        ),
        dtype=np.float32
    )


    # =================================================
    # BUILD CONTINUOUS OPACITY FIELD
    # =================================================

    for j in range(n_x):

        column_y = y_fine[
            :,
            j
        ]


        # -------------------------------------------------
        # Sort Q10 trajectories vertically.
        #
        # This is important because trajectories can
        # cross. We want the opacity field to occupy
        # the actual vertical envelope rather than
        # assuming Q10 always increases monotonically
        # in y.
        # -------------------------------------------------

        order = np.argsort(
            column_y
        )


        y_sorted = column_y[
            order
        ]


        alpha_sorted = alpha_values[
            order
        ]


        # -------------------------------------------------
        # Remove duplicate y positions.
        # -------------------------------------------------

        y_unique, unique_indices = np.unique(
            y_sorted,
            return_index=True
        )


        alpha_unique = alpha_sorted[
            unique_indices
        ]


        if len(y_unique) < 2:
            continue


        # -------------------------------------------------
        # Pixels inside the Q10 envelope.
        # -------------------------------------------------

        inside = (
            (y_grid >= y_unique[0])
            &
            (y_grid <= y_unique[-1])
        )


        if not np.any(inside):
            continue


        # -------------------------------------------------
        # Continuous opacity interpolation.
        # -------------------------------------------------

        alpha_field[
            inside,
            j
        ] = np.interp(
            y_grid[inside],
            y_unique,
            alpha_unique
        )


    # =================================================
    # CREATE RGBA IMAGE
    # =================================================

    rgba = np.array(
        to_rgba(color)
    )


    image = np.empty(
        (
            n_y,
            n_x,
            4
        ),
        dtype=np.float32
    )


    image[:, :, 0] = rgba[0]
    image[:, :, 1] = rgba[1]
    image[:, :, 2] = rgba[2]

    image[:, :, 3] = alpha_field


    # =================================================
    # DRAW IMAGE
    # =================================================

    ax.imshow(
        image,
        origin="lower",
        aspect="auto",
        interpolation="bilinear",
        extent=[
            x_fine[0],
            x_fine[-1],
            y_axis_min,
            y_axis_max
        ],
        zorder=zorder
    )


# =================================================
# CREATE 2 × 2 PANEL
# =================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(11, 6.5),
    sharex=True,
    sharey=True
)


soilmaps = [
    "0",
    "1"
]


dynamics_modes = [
    "0",
    "1"
]


# =================================================
# PLOT EACH PANEL
# =================================================

for row, soilmap in enumerate(
    soilmaps
):

    for col, dynamics in enumerate(
        dynamics_modes
    ):

        ax = axes[
            row,
            col
        ]


        # =================================================
        # PANEL BORDERS
        # =================================================

        ax.spines[
            "top"
        ].set_visible(False)

        ax.spines[
            "right"
        ].set_visible(False)

        ax.spines[
            "bottom"
        ].set_visible(False)

        ax.spines[
            "left"
        ].set_visible(False)


        # =================================================
        # PANEL BACKGROUND
        # =================================================

        ax.set_facecolor(
            panel_background
        )

        ax.patch.set_alpha(
            0.75
        )


        # =================================================
        # GLOBAL Y RANGE
        # =================================================

        ax.set_ylim(
            plot_y_min,
            plot_y_max
        )


        # =================================================
        # SELECT PANEL DATA
        # =================================================

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
        # FULL ENSEMBLE ENVELOPE
        # =================================================

        ax.fill_between(
            master_x,
            master_lower,
            master_upper,
            color=ensemble_fill_color,
            alpha=1.0,
            linewidth=0,
            edgecolor="none",
            zorder=0
        )


        # =================================================
        # BUILD SUBSTRATE / Q10 DATA
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

            substrate = str(substrate)
            q10 = str(q10)


            if substrate not in data:

                data[
                    substrate
                ] = {}


            data[
                substrate
            ][q10] = y


        # =================================================
        # SMOOTH SUBSTRATE/Q10 BANDS
        # =================================================

        x = np.arange(
            series_length
        )


        for substrate in substrates:

            if substrate not in data:
                continue


            q10_data = data[
                substrate
            ]


            available_q10 = sorted(
                q10_data.keys(),
                key=lambda q: int(q)
            )


            if len(available_q10) < 2:
                continue


            missing_alpha = [
                q
                for q in available_q10
                if q not in q10_alpha
            ]


            if missing_alpha:

                raise RuntimeError(
                    f"Missing Q10 alpha values "
                    f"for substrate {substrate}: "
                    f"{missing_alpha}"
                )


            plot_smooth_q10_band(
                ax=ax,
                x=x,
                q10_data=q10_data,
                color=color_map[
                    substrate
                ],
                alpha_map=q10_alpha,
                y_axis_min=plot_y_min,
                y_axis_max=plot_y_max,
                zorder=1
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

for col, dynamics in enumerate(
    dynamics_modes
):

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

for row, soilmap in enumerate(
    soilmaps
):

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

        ax.set_xticks(
            range(12)
        )

        ax.set_xticklabels(
            months
        )


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


# =================================================
# Y AXIS
# =================================================

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


# =================================================
# OVERALL TITLE
# =================================================

fig.text(
    0.055,
    0.965,
    mode_folder.capitalize()
    + r" Mean f$_{CH4}$ - "
    + scale_folder.capitalize(),
    ha="left",
    va="center",
    fontsize=16,
    fontweight="bold"
)


# =================================================
# FULL ENSEMBLE LEGEND
# =================================================

ensemble_patch = Patch(
    facecolor="white",
    edgecolor="none",
    label="Full ensemble spread"
)


ensemble_legend = axes[0, 0].legend(
    handles=[
        ensemble_patch
    ],
    loc="upper left",
    bbox_to_anchor=(
        0.02,
        0.98
    ),
    frameon=False,
    fontsize=11,
    borderpad=0.0,
    handlelength=1.8,
    handleheight=0.8,
    handletextpad=0.6
)


axes[0, 0].add_artist(
    ensemble_legend
)


# =================================================
# THREE SUBSTRATE Q10 COLOURBARS
# =================================================

#
# Each substrate receives its own continuous
# colourbar.
#
# The colour is the substrate colour.
# The opacity is Q10.
#
# Therefore:
#
# Carbon : brown opacity gradient
# NPP    : green opacity gradient
# Resps  : blue opacity gradient
#
# Each bar has exact Q10 tick positions:
#
#       1.0   2.0   3.0   4.0
#
# =================================================


# -------------------------------------------------
# Helper function
# -------------------------------------------------

# =================================================
# THREE SUBSTRATE Q10 COLOURBARS
# =================================================

def create_substrate_q10_colorbar(
    fig,
    substrate,
    left,
    bottom,
    width,
    height,
    show_q10_labels=False
):
    """
    Create one vertical substrate-specific Q10 colourbar.

    RGB = substrate
    Opacity = Q10

    Only the right-most colourbar shows Q10 labels.
    """

    base_rgb = np.array(
        to_rgba(
            color_map[substrate]
        )[:3]
    )

    # -------------------------------------------------
    # Continuous Q10 colourmap
    # -------------------------------------------------

    q10_positions = np.array(
        [
            1.0,
            2.0,
            3.0,
            4.0
        ]
    )

    q10_alpha_values = np.array(
        [
            q10_alpha["0"],
            q10_alpha["1"],
            q10_alpha["2"],
            q10_alpha["3"]
        ]
    )

    n = 256

    q10_dense = np.linspace(
        1.0,
        4.0,
        n
    )

    alpha_dense = np.interp(
        q10_dense,
        q10_positions,
        q10_alpha_values
    )

    rgba_table = np.zeros(
        (
            n,
            4
        )
    )

    rgba_table[:, 0] = base_rgb[0]
    rgba_table[:, 1] = base_rgb[1]
    rgba_table[:, 2] = base_rgb[2]
    rgba_table[:, 3] = alpha_dense

    cmap = LinearSegmentedColormap.from_list(
        f"q10_{substrate}",
        rgba_table
    )

    # -------------------------------------------------
    # Normalisation
    # -------------------------------------------------

    norm = Normalize(
        vmin=1.0,
        vmax=4.0
    )

    # -------------------------------------------------
    # Scalar mappable
    # -------------------------------------------------

    mappable = ScalarMappable(
        norm=norm,
        cmap=cmap
    )

    mappable.set_array(
        np.array(
            [
                1.0,
                4.0
            ]
        )
    )

    # -------------------------------------------------
    # Colourbar axes
    # -------------------------------------------------

    cax = fig.add_axes(
        [
            left,
            bottom,
            width,
            height
        ]
    )

    cbar = fig.colorbar(
        mappable,
        cax=cax,
        orientation="vertical"
    )

    # -------------------------------------------------
    # Q10 ticks
    #
    # Only the right-most colourbar gets labels.
    # -------------------------------------------------

    cbar.set_ticks(
        [
            1.0,
            2.0,
            3.0,
            4.0
        ]
    )

    if show_q10_labels:

        cbar.set_ticklabels(
            [
                "1.0",
                "2.0",
                "3.0",
                "4.0"
            ]
        )

        cbar.ax.tick_params(
            axis="y",
            which="both",
            length=3,
            width=0.7,
            labelsize=8,
            pad=2
        )

    else:

        # Keep the ticks but hide their labels.
        cbar.ax.set_yticklabels([])

        cbar.ax.tick_params(
            axis="y",
            which="both",
            length=0
        )

    # -------------------------------------------------
    # Colourbar outline
    # -------------------------------------------------

    cbar.outline.set_linewidth(
        0.5
    )

    # -------------------------------------------------
    # Substrate label
    # -------------------------------------------------

    cbar.ax.set_title(
        substrate_labels[substrate],
        fontsize=10,
        pad=3
    )

    return cbar


# =================================================
# POSITION THE THREE COLOURBARS
# =================================================

#
# Three vertical bars.
#
# They are immediately adjacent:
#
#     Carbon | NPP | Resps | Q10 labels
#
# No horizontal gap between them.
#


colorbar_bottom = 0.615
colorbar_height = 0.115

colorbar_width = 0.012


create_substrate_q10_colorbar(
    fig=fig,
    substrate="0",
    left=0.215,
    bottom=colorbar_bottom,
    width=colorbar_width,
    height=colorbar_height,
    show_q10_labels=False
)


create_substrate_q10_colorbar(
    fig=fig,
    substrate="1",
    left=0.215 + colorbar_width,
    bottom=colorbar_bottom,
    width=colorbar_width,
    height=colorbar_height,
    show_q10_labels=False
)


create_substrate_q10_colorbar(
    fig=fig,
    substrate="2",
    left=0.215 + 2 * colorbar_width,
    bottom=colorbar_bottom,
    width=colorbar_width,
    height=colorbar_height,
    show_q10_labels=True
)



# =================================================
# POSITION THE THREE COLOURBARS
# =================================================

#
# All three are in the first panel.
#
# They are deliberately stacked vertically so that
# each substrate has a clear identity.
#

# =================================================
# LAYOUT
# =================================================

plt.tight_layout(
    rect=[
        0.055,
        0.045,
        0.99,
        0.91
    ],
    pad=0.8,
    w_pad=1.0,
    h_pad=1.2
)


# =================================================
# SAVE
# =================================================

output_directory = (
    directory
    / scale_folder
)


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
print(
    "Saved:",
    output_file
)


# =================================================
# SHOW
# =================================================

plt.show()
