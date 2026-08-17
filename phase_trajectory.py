from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


# =================================================
# SETTINGS
# =================================================

directory = Path(
    "/Users/jae35/Desktop/JULES_test_data/ID_suites"
)

# True  = scaled data
# False = unscaled data
apply_scale_factor = True

scale_folder = (
    "scaled" if apply_scale_factor else "unscaled"
)


# =================================================
# Parameter definitions
# =================================================

substrates = ["0", "1", "2"]

substrate_labels = {
    "0": "Carbon",
    "1": "NPP",
    "2": "Resps"
}


q10_codes = ["0", "1", "2", "3"]

q10_labels = {
    "0": "1.0",
    "1": "2.0",
    "2": "3.0",
    "3": "4.0"
}


soil_maps = ["0", "1"]

soil_labels = {
    "0": "Standard",
    "1": "Oxi + Ulti"
}


months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


# =================================================
# Find ensemble members
# =================================================

files = []

for subdir in sorted(directory.iterdir()):

    if not subdir.is_dir():
        continue

    name = subdir.name

    try:
        code = name.split("_")[1]

        substrate = code[0]
        q10 = code[1]
        soilmap = code[2]

    except (IndexError, ValueError):
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

        files.append(
            (
                name,
                substrate,
                q10,
                soilmap,
                filepath
            )
        )


print("Ensemble members found:", len(files))


# =================================================
# Read all ensemble trajectories
# =================================================

ensemble = []

for (
    name,
    substrate,
    q10,
    soilmap,
    filepath
) in files:

    flux = np.loadtxt(filepath)

    if len(flux) != 12:

        print(
            f"Skipping {name}: "
            f"expected 12 months, found {len(flux)}"
        )

        continue

    ensemble.append(
        {
            "name": name,
            "substrate": substrate,
            "q10": q10,
            "soilmap": soilmap,
            "flux": flux
        }
    )


print("Trajectories plotted:", len(ensemble))


# =================================================
# Flux range
# =================================================

all_flux = np.concatenate(
    [
        member["flux"]
        for member in ensemble
    ]
)

flux_min = np.min(all_flux)
flux_max = np.max(all_flux)

print(
    f"Flux range: {flux_min:.4g} to {flux_max:.4g}"
)


# =================================================
# Dot-size scaling
# =================================================

# Make dot area proportional to flux.
#
# If flux can be negative, shift it before scaling.

flux_range = flux_max - flux_min

if flux_range == 0:
    flux_range = 1.0


min_dot_size = 20
max_dot_size = 500


def flux_to_size(value):

    scaled = (
        (value - flux_min)
        / flux_range
    )

    return (
        min_dot_size
        + scaled * (
            max_dot_size
            - min_dot_size
        )
    )


# =================================================
# Month colours
# =================================================

month_colours = plt.cm.turbo(
    np.linspace(0, 1, 12)
)


# =================================================
# Figure
# =================================================

fig = plt.figure(
    figsize=(15, 10)
)

ax = fig.add_subplot(
    111,
    projection="3d"
)


# =================================================
# Plot all ensemble trajectories
# =================================================

for member in ensemble:

    substrate = member["substrate"]
    q10 = member["q10"]
    soilmap = member["soilmap"]

    flux = member["flux"]


    # -------------------------------------------------
    # Parameter-space coordinates
    # -------------------------------------------------

    x = substrates.index(substrate)

    y = q10_codes.index(q10)

    z = soil_maps.index(soilmap)


    # -------------------------------------------------
    # Plot the trajectory
    # -------------------------------------------------
    #
    # The parameter coordinates are fixed for the
    # ensemble member, so the trajectory is represented
    # by changing dot size/colour through the months.
    #

    for month in range(12):

        ax.scatter(
            x,
            y,
            z,

            s=flux_to_size(flux[month]),

            color=month_colours[month],

            edgecolor="black",
            linewidth=0.35,

            alpha=0.55,

            depthshade=False
        )


    # -------------------------------------------------
    # Optional faint line through monthly points
    #
    # Since parameter coordinates do not change,
    # there is no spatial movement between months.
    # -------------------------------------------------

    ax.plot(
        np.full(12, x),
        np.full(12, y),
        np.full(12, z),

        color="black",
        linewidth=0.4,
        alpha=0.15
    )


# =================================================
# X axis: substrate
# =================================================

ax.set_xlabel(
    "Substrate",
    labelpad=12
)

ax.set_xticks(
    range(len(substrates))
)

ax.set_xticklabels(
    [
        substrate_labels[s]
        for s in substrates
    ]
)


# =================================================
# Y axis: Q10
# =================================================

ax.set_ylabel(
    "Q10",
    labelpad=12
)

ax.set_yticks(
    range(len(q10_codes))
)

ax.set_yticklabels(
    [
        q10_labels[q]
        for q in q10_codes
    ]
)


# =================================================
# Z axis: soil map
# =================================================

ax.set_zlabel(
    "Soil map",
    labelpad=12
)

ax.set_zticks(
    range(len(soil_maps))
)

ax.set_zticklabels(
    [
        soil_labels[s]
        for s in soil_maps
    ]
)


# =================================================
# Month colour bar
# =================================================

month_norm = Normalize(
    vmin=0,
    vmax=11
)

month_sm = ScalarMappable(
    norm=month_norm,
    cmap=plt.cm.turbo
)

month_sm.set_array([])

month_cbar = fig.colorbar(
    month_sm,
    ax=ax,
    pad=0.10,
    shrink=0.7
)

month_cbar.set_ticks(
    range(12)
)

month_cbar.set_ticklabels(
    months
)

month_cbar.set_label(
    "Month"
)


# =================================================
# Flux size legend
# =================================================

# Choose representative flux values for the legend

legend_values = np.linspace(
    flux_min,
    flux_max,
    4
)


legend_handles = []

for value in legend_values:

    handle = ax.scatter(
        [],
        [],
        [],
        s=flux_to_size(value),
        color="grey",
        edgecolor="black",
        linewidth=0.6,
        alpha=0.65
    )

    legend_handles.append(handle)


ax.legend(
    legend_handles,
    [
        f"{value:.3g}"
        for value in legend_values
    ],
    title=r"$f_{CH4}$",
    loc="upper left",
    bbox_to_anchor=(1.02, 1.0),
    frameon=False
)


# =================================================
# Title
# =================================================

ax.set_title(
    "Ensemble parameter space — monthly fCH4",
    fontsize=15,
    pad=20
)


# =================================================
# View
# =================================================

ax.view_init(
    elev=25,
    azim=-55
)

ax.grid(
    alpha=0.25
)


# =================================================
# Save
# =================================================

plt.tight_layout()

output_directory = (
    directory / scale_folder
)

output_directory.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    output_directory
    / "ensemble_substrate_q10_soilmap_flux.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

print()
print("Saved:", output_file)

plt.show()