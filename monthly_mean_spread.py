from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# =================================================
# SETTINGS
# =================================================

directory = Path("/Users/jae35/Desktop/JULES_test_data/ID_suites")

# True  = read scaled data and save to ID_suites/scaled/
# False = read unscaled data and save to ID_suites/unscaled/
apply_scale_factor = False

scale_folder = "scaled" if apply_scale_factor else "unscaled"

print("Using:", scale_folder, "data")


# =================================================
# Find files
# =================================================

files = []

for subdir in sorted(directory.iterdir()):

    if not subdir.is_dir():
        continue

    name = subdir.name

    # Example: u-dk105_231
    # First digit  = substrate
    # Second digit = Q10
    # Third digit  = soil map
    try:
        code = name.split("_")[1]
        substrate = code[0]
        q10 = code[1]
        soilmap = code[2]
    except IndexError:
        continue

    # Read from the appropriate scaled/unscaled folder
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
            (name, substrate, q10, soilmap, filepath)
        )

print("Suites plotted:", len(files))
print("Substrate codes found:", sorted(set(f[1] for f in files)))
print("Q10 codes found:", sorted(set(f[2] for f in files)))
print("Soil map codes found:", sorted(set(f[3] for f in files)))


# =================================================
# Visual encoding
# =================================================

# Colours = substrate

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


# Line style = soil map

soil_styles = {
    "0": "-",
    "1": "--"
}

soil_labels = {
    "0": "Standard",
    "1": "Oxi + Ulti"
}


# Line width = Q10

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


months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


# =================================================
# Plot
# =================================================

fig, ax = plt.subplots(figsize=(16, 8))

series_length = None

for name, substrate, q10, soilmap, filepath in files:

    y = np.loadtxt(filepath)
    series_length = len(y)

    ax.plot(
        y,
        color=color_map[substrate],
        linestyle=soil_styles[soilmap],
        linewidth=q10_width[q10],
        alpha=0.85
    )


if series_length == 12:
    ax.set_xticks(range(12))
    ax.set_xticklabels(months)


# =================================================
# Formatting
# =================================================

ax.set_xlabel("Month")
ax.set_ylabel("f$_{CH4}$")

ax.set_title(
    f"Global Mean f$_{{CH4}}$ Ensemble (2005) — "
    f"{scale_folder.capitalize()}"
)

ax.grid(alpha=0.3)


# =================================================
# Legends
# =================================================

# Substrate legend

substrate_handles = [
    Line2D(
        [0], [0],
        color=color_map[s],
        linewidth=3,
        label=substrate_labels[s]
    )
    for s in substrates
]

leg1 = ax.legend(
    handles=substrate_handles,
    title="Substrate",
    loc="upper left",
    bbox_to_anchor=(0.01, 0.99),
    frameon=False
)

ax.add_artist(leg1)


# Soil map legend

soil_handles = [
    Line2D(
        [0], [0],
        color="black",
        linewidth=2,
        linestyle=soil_styles[s],
        label=soil_labels[s]
    )
    for s in ["0", "1"]
]

leg2 = ax.legend(
    handles=soil_handles,
    title="Soil map",
    loc="upper left",
    bbox_to_anchor=(0.10, 0.99),
    frameon=False
)

ax.add_artist(leg2)


# Q10 legend

q10_handles = [
    Line2D(
        [0], [0],
        color="black",
        linewidth=q10_width[q],
        label=q10_labels[q]
    )
    for q in sorted(q10_width)
]

leg3 = ax.legend(
    handles=q10_handles,
    title="Q10",
    loc="upper left",
    bbox_to_anchor=(0.28, 0.99),
    frameon=False
)

ax.add_artist(leg3)


# =================================================
# Save
# =================================================

plt.tight_layout()

# Save directly under ID_suites/scaled or ID_suites/unscaled
output_directory = directory / scale_folder

output_directory.mkdir(parents=True, exist_ok=True)

output_file = (
    output_directory
    / "monthly_mean_spread_tseries.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

print("Saved:", output_file)

# plt.show()