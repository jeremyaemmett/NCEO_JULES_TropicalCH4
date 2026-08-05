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
    # substrate = 2
    # q10       = 3
    # soil map  = 1
    try:
        code = name.split("_")[1]
        substrate = code[0]
        q10 = code[1]
        soilmap = code[2]
    except IndexError:
        continue

    filepath = subdir / "plots" / "output" / "fch4_wetl" / "_arealmean_tseries.txt"

    if filepath.exists():
        files.append(
            (name, substrate, q10, soilmap, filepath)
        )

print("Suites plotted:", len(files))


# -----------------------
# Visual encoding
# -----------------------

# Substrate -> color
substrates = sorted(set(f[1] for f in files))
colors = cm.tab10(np.linspace(0, 1, len(substrates)))
color_map = dict(zip(substrates, colors))

# Soil map -> line style (ONLY 2 maps)
soil_styles = {
    "0": "-",
    "1": "--"
}

# Q10 -> line thickness
q10_width = {
    "0": 1.0,
    "1": 1.7,
    "2": 2.4,
    "3": 3.1
}


# -----------------------
# Plot
# -----------------------

plt.figure(figsize=(14, 8))

for name, substrate, q10, soilmap, filepath in files:

    y = np.loadtxt(filepath)

    plt.plot(
        y,
        color=color_map[substrate],
        linestyle=soil_styles[soilmap],
        linewidth=q10_width[q10],
        alpha=0.85
    )


# -----------------------
# Legends
# -----------------------

substrate_handles = [
    Line2D(
        [0], [0],
        color=color_map[s],
        lw=3,
        label=f"Substrate {s}"
    )
    for s in substrates
]

soil_handles = [
    Line2D(
        [0], [0],
        color="black",
        lw=2,
        linestyle="-",
        label="Soil map 0"
    ),
    Line2D(
        [0], [0],
        color="black",
        lw=2,
        linestyle="--",
        label="Soil map 1"
    )
]

q10_handles = [
    Line2D(
        [0], [0],
        color="black",
        lw=q10_width[q],
        label=f"Q10 choice {q}"
    )
    for q in sorted(q10_width)
]


leg1 = plt.legend(
    handles=substrate_handles,
    title="Substrate type",
    loc="upper left"
)

plt.gca().add_artist(leg1)

leg2 = plt.legend(
    handles=soil_handles,
    title="Soil property map",
    loc="upper right"
)

plt.gca().add_artist(leg2)

plt.legend(
    handles=q10_handles,
    title="Q10 choice",
    loc="lower right"
)


plt.xlabel("Time step")
plt.ylabel("fCH$_4$")
plt.title("Areal Mean fCH4 Time Series")

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()