from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.cm as cm

directory = Path("/Users/jae35/Desktop/JULES_test_data/ID_suites")

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

    filepath = subdir / "plots" / "output" / "fch4_wetl" / "_arealmean_tseries.txt"

    if filepath.exists():
        files.append((name, substrate, q10, soilmap, filepath))

print("Suites plotted:", len(files))
print("Substrate codes found:", sorted(set(f[1] for f in files)))
print("Q10 codes found:", sorted(set(f[2] for f in files)))
print("Soil map codes found:", sorted(set(f[3] for f in files)))

# -------------------------------------------------
# Visual encoding
# -------------------------------------------------

# Colours = substrate
substrates = sorted(set(f[1] for f in files))
colors = cm.tab10(np.linspace(0, 1, len(substrates)))
color_map = dict(zip(substrates, colors))

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

# Labels shown in legend
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

# -------------------------------------------------
# Plot
# -------------------------------------------------

plt.figure(figsize=(14, 8))

series_length = None

for name, substrate, q10, soilmap, filepath in files:

    y = np.loadtxt(filepath)
    series_length = len(y)

    plt.plot(
        y,
        color=color_map[substrate],
        linestyle=soil_styles[soilmap],
        linewidth=q10_width[q10],
        alpha=0.85
    )

if series_length == 12:
    plt.xticks(range(12), months)

# -------------------------------------------------
# Legends
# -------------------------------------------------

substrate_handles = [
    Line2D(
        [0], [0],
        color=color_map[s],
        lw=3,
        label=substrate_labels.get(s, f"Substrate {s}")
    )
    for s in substrates
]

soil_handles = [
    Line2D(
        [0], [0],
        color="black",
        lw=2,
        linestyle=soil_styles[s],
        label=soil_labels[s]
    )
    for s in sorted(soil_styles)
]

q10_handles = [
    Line2D(
        [0], [0],
        color="black",
        lw=q10_width[q],
        label=q10_labels[q]
    )
    for q in sorted(q10_width)
]

leg1 = plt.legend(
    handles=substrate_handles,
    title="Substrate",
    loc="upper left"
)
plt.gca().add_artist(leg1)

leg2 = plt.legend(
    handles=soil_handles,
    title="Soil map",
    loc="upper right"
)
plt.gca().add_artist(leg2)

plt.legend(
    handles=q10_handles,
    title="Q10",
    loc="lower right"
)

plt.xlabel("Month")
plt.ylabel("f$_{CH4}$")
plt.title("Global Mean f$_{CH4}$ vs Month")

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()