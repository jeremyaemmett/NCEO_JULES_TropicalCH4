from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle


# ============================================================
# SETTINGS
# ============================================================

directory = Path("/Users/jae35/Desktop/JULES_test_data/ID_suites")

# True  = use scaled data
# False = use unscaled data
apply_scale_factor = False

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

    try:
        code = name.split("_")[1]
        substrate = code[0]
        q10 = code[1]
        soilmap = code[2]
    except IndexError:
        continue

    # Read from either:
    #
    # plots/output/scaled/fch4_wetl/
    #
    # or:
    #
    # plots/output/unscaled/fch4_wetl/
    #
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

months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


# ============================================================
# READ DATA
# ============================================================

all_data = []
metadata = []

for name, substrate, q10, soilmap, filepath in files:

    y = np.loadtxt(filepath)

    if len(y) != 12:
        raise ValueError(
            f"{filepath} does not contain 12 months"
        )

    all_data.append(y)

    metadata.append(
        (substrate, soilmap, q10)
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

ensemble_mean = np.mean(all_data, axis=0)

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

    mask = (
        (metadata[:, 0] == substrate) &
        (metadata[:, 1] == soil)
    )

    combo_data[combo] = all_data[mask]


# ============================================================
# PLOT
# ============================================================

fig, ax = plt.subplots(
    figsize=(16, 8)
)


# ============================================================
# TOUCHING BOXPLOTS
# ============================================================

substrate_offsets = {
    "0": -0.12,
    "1":  0.00,
    "2":  0.12
}

soil_centers = {
    "0": -0.24,
    "1":  0.24
}


for combo in combo_order:

    substrate, soil = combo

    # Skip combinations for which there are no suites
    if combo_data[combo].shape[0] == 0:
        continue

    offset = (
        soil_centers[soil]
        + substrate_offsets[substrate]
    )

    positions = x + offset

    ax.boxplot(

        combo_data[combo],

        positions=positions,

        widths=0.12,

        # Whiskers extend to extreme values
        whis=(0, 100),

        patch_artist=True,

        boxprops=dict(
            facecolor=color_map[substrate],
            hatch="///" if soil == "1" else "",
            alpha=0.65,
            linewidth=1.2
        ),

        medianprops=dict(
            color="black",
            linewidth=1.3
        ),

        whiskerprops=dict(
            linewidth=1
        ),

        capprops=dict(
            linewidth=1
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
    "Global Mean f$_{CH4}$ Ensemble (2005)"
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
        alpha=0.65,
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
        alpha=0.65,
        label=soil_labels[soil]
    )

    for soil in ["0", "1"]

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


# ------------------------------------------------------------
# Substrate legend
# ------------------------------------------------------------

leg1 = ax.legend(

    handles=substrate_handles,

    title="Substrate",

    loc="upper left",

    bbox_to_anchor=(0.01, 0.99),

    frameon=False
)

ax.add_artist(leg1)


# ------------------------------------------------------------
# Soil legend
# ------------------------------------------------------------

leg2 = ax.legend(

    handles=soil_handles,

    title="Soil map",

    loc="upper left",

    bbox_to_anchor=(0.10, 0.99),

    frameon=False
)

ax.add_artist(leg2)


# ------------------------------------------------------------
# Ensemble legend
# ------------------------------------------------------------

leg3 = ax.legend(

    handles=summary_handles,

    title="Ensemble",

    loc="upper left",

    bbox_to_anchor=(0.28, 0.99),

    frameon=False
)

ax.add_artist(leg3)


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
    / "monthly_mean_spread_boxwhisker.png"
)


plt.savefig(

    output_file,

    dpi=300,

    bbox_inches="tight"
)


plt.close()


print("Saved:", output_file)