from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SETTINGS
# ============================================================

BASE_DIRECTORY = Path(
    "/Users/jae35/Desktop/JULES_test_data/ID_suites"
)

FACTORS = [
    "substrate",
    "q10",
    "soilmap",
    "competition",
]

MAP_RELATIVE_PATH = Path(
    "plots",
    "output",
    "scaled",
    "fch4_wetl",
    "fch4_wetl_2005_(5)Jun_map.txt",
)

OUTPUT_DIRECTORY = Path(
    "anova_output"
)


# ============================================================
# FACTORIAL DESIGN
# ============================================================

variable_table = pd.DataFrame(
    [
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 0, 1, 1],

        [0, 1, 0, 0],
        [0, 1, 0, 1],
        [0, 1, 1, 0],
        [0, 1, 1, 1],

        [0, 2, 0, 0],
        [0, 2, 0, 1],
        [0, 2, 1, 0],
        [0, 2, 1, 1],

        [0, 3, 0, 0],
        [0, 3, 0, 1],
        [0, 3, 1, 0],
        [0, 3, 1, 1],

        [1, 0, 0, 0],
        [1, 0, 0, 1],
        [1, 0, 1, 0],
        [1, 0, 1, 1],

        [1, 1, 0, 0],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
        [1, 1, 1, 1],

        [1, 2, 0, 0],
        [1, 2, 0, 1],
        [1, 2, 1, 0],
        [1, 2, 1, 1],

        [1, 3, 0, 0],
        [1, 3, 0, 1],
        [1, 3, 1, 0],
        [1, 3, 1, 1],

        [2, 0, 0, 0],
        [2, 0, 0, 1],
        [2, 0, 1, 0],
        [2, 0, 1, 1],

        [2, 1, 0, 0],
        [2, 1, 0, 1],
        [2, 1, 1, 0],
        [2, 1, 1, 1],

        [2, 2, 0, 0],
        [2, 2, 0, 1],
        [2, 2, 1, 0],
        [2, 2, 1, 1],

        [2, 3, 0, 0],
        [2, 3, 0, 1],
        [2, 3, 1, 0],
        [2, 3, 1, 1],
    ],
    columns=FACTORS,
)


EXPECTED_COMBINATIONS = {
    tuple(row[factor] for factor in FACTORS)
    for _, row in variable_table.iterrows()
}


# ============================================================
# FIND SUITES
# ============================================================

suite_directories = sorted(
    path
    for path in BASE_DIRECTORY.iterdir()
    if path.is_dir()
)


if len(suite_directories) != 48:

    raise ValueError(
        f"Expected exactly 48 suite directories, "
        f"but found {len(suite_directories)}."
    )


# ============================================================
# READ ALL 48 MAPS
# ============================================================

suite_information = []
maps = []


print()
print("=" * 70)
print("READING JULES MAPS")
print("=" * 70)


for suite_directory in suite_directories:

    suite_name = suite_directory.name

    code = suite_name.split("_")[-1]

    if len(code) != 4 or not code.isdigit():
        continue


    substrate = int(code[0])
    q10 = int(code[1])
    soilmap = int(code[2])
    competition = int(code[3])


    combination = (
        substrate,
        q10,
        soilmap,
        competition,
    )


    if combination not in EXPECTED_COMBINATIONS:

        raise ValueError(
            f"Unexpected factorial combination "
            f"for {suite_name}: {combination}"
        )


    map_file = (
        suite_directory
        / MAP_RELATIVE_PATH
    )


    if not map_file.is_file():

        raise FileNotFoundError(
            "\nMAP FILE NOT FOUND\n"
            f"Suite: {suite_name}\n"
            f"Expected:\n{map_file}\n"
        )


    spatial_map = np.loadtxt(
        map_file,
        dtype=float,
    )


    spatial_map = np.asarray(
        spatial_map,
        dtype=float,
    )


    if spatial_map.ndim != 2:

        raise ValueError(
            f"{suite_name} is not a 2D map. "
            f"Shape = {spatial_map.shape}"
        )


    if maps:

        if spatial_map.shape != maps[0].shape:

            raise ValueError(
                f"Map dimensions do not match.\n"
                f"Suite: {suite_name}\n"
                f"Expected: {maps[0].shape}\n"
                f"Found: {spatial_map.shape}"
            )


    suite_information.append(
        {
            "suite": suite_name,
            "substrate": substrate,
            "q10": q10,
            "soilmap": soilmap,
            "competition": competition,
        }
    )


    maps.append(
        spatial_map
    )


    print(
        f"READ: {suite_name:15s}"
        f" S={substrate}"
        f" Q={q10}"
        f" M={soilmap}"
        f" C={competition}"
        f" shape={spatial_map.shape}"
    )


# ============================================================
# DATAFRAME + ARRAY
# ============================================================

if len(maps) != 48:

    raise ValueError(
        f"Only {len(maps)} maps were read. "
        f"Expected 48."
    )


df = pd.DataFrame(
    suite_information
)


data = np.stack(
    maps,
    axis=0,
)


n_suites, nrows, ncols = data.shape


print()
print("=" * 70)
print("INPUT DATA")
print("=" * 70)

print(
    f"Suites: {n_suites}"
)

print(
    f"Map size: {nrows} x {ncols}"
)


# ============================================================
# DESIGN CHECK
# ============================================================

found_combinations = {
    tuple(row[factor] for factor in FACTORS)
    for _, row in df.iterrows()
}


missing = (
    EXPECTED_COMBINATIONS
    - found_combinations
)


extra = (
    found_combinations
    - EXPECTED_COMBINATIONS
)


if missing:

    raise ValueError(
        f"Missing factorial combinations: "
        f"{sorted(missing)}"
    )


if extra:

    raise ValueError(
        f"Unexpected combinations: "
        f"{sorted(extra)}"
    )


if df.duplicated(
    subset=FACTORS
).any():

    raise ValueError(
        "Duplicate factorial combinations found."
    )


# ============================================================
# GRAND MEAN
# ============================================================

grand_mean = np.nanmean(
    data,
    axis=0,
)


# ============================================================
# TOTAL SS
# ============================================================

total_ss = np.nansum(
    (
        data
        - grand_mean[None, :, :]
    ) ** 2,
    axis=0,
)


valid_count = np.sum(
    np.isfinite(data),
    axis=0,
)


total_ss[
    valid_count == 0
] = np.nan


# ============================================================
# MARGINAL MEANS
# ============================================================

def get_marginal_means(
    target_factors,
):

    target_factors = tuple(
        target_factors
    )


    if len(target_factors) == 0:

        return {
            (): grand_mean
        }


    groups = {}


    for index, row in df.iterrows():

        key = tuple(
            row[factor]
            for factor in target_factors
        )

        if key not in groups:

            groups[key] = []

        groups[key].append(
            index
        )


    marginal_means = {}


    for key, indices in groups.items():

        marginal_means[key] = np.nanmean(
            data[indices],
            axis=0,
        )


    return marginal_means


# ============================================================
# PURE EFFECT
# ============================================================

def calculate_effect_ss(
    target_factors,
):

    target_factors = tuple(
        target_factors
    )

    order = len(
        target_factors
    )


    marginal_means = {}


    for subset_size in range(
        order + 1
    ):

        for subset in combinations(
            target_factors,
            subset_size,
        ):

            marginal_means[subset] = (
                get_marginal_means(
                    subset
                )
            )


    ss = np.zeros(
        (nrows, ncols),
        dtype=float,
    )


    for index, row in df.iterrows():

        effect = np.zeros(
            (nrows, ncols),
            dtype=float,
        )


        for subset_size in range(
            order + 1
        ):

            for subset in combinations(
                target_factors,
                subset_size,
            ):

                if (
                    (order - subset_size)
                    % 2
                    == 0
                ):

                    sign = 1.0

                else:

                    sign = -1.0


                if len(subset) == 0:

                    marginal = marginal_means[
                        ()
                    ][
                        ()
                    ]

                else:

                    key = tuple(
                        row[factor]
                        for factor in subset
                    )

                    marginal = marginal_means[
                        subset
                    ][
                        key
                    ]


                effect += (
                    sign
                    * marginal
                )


        ss += np.where(
            np.isfinite(effect),
            effect ** 2,
            0.0,
        )


    return ss


# ============================================================
# CALCULATE ALL 15 TERMS
# ============================================================

components = {}


print()
print("=" * 70)
print("CALCULATING SPATIAL ANOVA")
print("=" * 70)


for order in range(
    1,
    len(FACTORS) + 1,
):

    for subset in combinations(
        FACTORS,
        order,
    ):

        name = ":".join(
            subset
        )


        print(
            f"  {name}"
        )


        ss_map = calculate_effect_ss(
            subset
        )


        percent_map = np.full(
            (nrows, ncols),
            np.nan,
        )


        valid = (
            np.isfinite(total_ss)
            & (total_ss > 0)
        )


        percent_map[valid] = (
            ss_map[valid]
            / total_ss[valid]
            * 100.0
        )


        components[name] = {
            "sum_sq": ss_map,
            "percent": percent_map,
        }


# ============================================================
# SAVE TEXT OUTPUTS
# ============================================================

OUTPUT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


np.savetxt(
    OUTPUT_DIRECTORY / "grand_mean.txt",
    grand_mean,
    fmt="%.12e",
)


np.savetxt(
    OUTPUT_DIRECTORY / "total_ss.txt",
    total_ss,
    fmt="%.12e",
)


for name, result in components.items():

    filename = name.replace(
        ":",
        "_",
    )


    np.savetxt(
        OUTPUT_DIRECTORY
        / f"{filename}_sum_sq.txt",
        result["sum_sq"],
        fmt="%.12e",
    )


    np.savetxt(
        OUTPUT_DIRECTORY
        / f"{filename}_percent.txt",
        result["percent"],
        fmt="%.12e",
    )


# ============================================================
# CHECK SUM OF SS
# ============================================================

component_ss = np.zeros(
    (nrows, ncols),
)


for result in components.values():

    component_ss += (
        result["sum_sq"]
    )


component_ss[
    valid_count == 0
] = np.nan


difference = (
    total_ss
    - component_ss
)


valid_check = (
    np.isfinite(total_ss)
    & (total_ss > 0)
)


if np.any(valid_check):

    max_error = np.max(
        np.abs(
            difference[valid_check]
        )
    )

else:

    max_error = np.nan


print()
print("=" * 70)
print("ANOVA CHECK")
print("=" * 70)

print(
    f"Maximum SS error: "
    f"{max_error:.12e}"
)


if np.any(valid_check):

    if not np.allclose(
        component_ss[valid_check],
        total_ss[valid_check],
        rtol=1e-10,
        atol=1e-20,
    ):

        raise ValueError(
            "ANOVA components do not sum to total SS."
        )


# ============================================================
# PLOT ALL 15 ANOVA TERMS
# ============================================================
#
# 15 terms:
#
#   4 main effects
#   6 two-way interactions
#   4 three-way interactions
#   1 four-way interaction
#
# They are displayed in a 3 x 5 grid.
#
# Each map shows:
#
#   percentage of local total variance
#
# ============================================================

print()
print("=" * 70)
print("CREATING ANOVA MAP GRID")
print("=" * 70)


terms = list(
    components.keys()
)


fig, axes = plt.subplots(
    3,
    5,
    figsize=(20, 11),
    constrained_layout=True,
)


axes = axes.ravel()


# ------------------------------------------------------------
# Use one common colour scale for all 15 maps.
#
# This makes the colours directly comparable.
# ------------------------------------------------------------

all_percent_values = np.concatenate(
    [
        result["percent"][
            np.isfinite(
                result["percent"]
            )
        ]
        for result in components.values()
    ]
)


if all_percent_values.size > 0:

    vmax = np.nanpercentile(
        all_percent_values,
        99,
    )

    vmax = max(
        vmax,
        1.0,
    )

else:

    vmax = 100.0


vmin = 0.0


# ------------------------------------------------------------
# Plot each ANOVA term.
# ------------------------------------------------------------

image = None


for ax, name in zip(
    axes,
    terms,
):

    percent_map = (
        components[name]["percent"]
    )


    image = ax.imshow(
        percent_map,
        origin="upper",
        cmap="viridis",
        vmin=vmin,
        vmax=vmax,
        interpolation="nearest",
    )


    ax.set_title(
        name,
        fontsize=11,
        fontweight="bold",
    )


    ax.set_xticks([])
    ax.set_yticks([])


# ------------------------------------------------------------
# Shared colourbar.
# ------------------------------------------------------------

cbar = fig.colorbar(
    image,
    ax=axes.tolist(),
    shrink=0.85,
    pad=0.02,
)


cbar.set_label(
    "Contribution to local total SS (%)",
    fontsize=12,
)


fig.suptitle(
    "Spatial 4-Factor ANOVA — fCH4",
    fontsize=18,
    fontweight="bold",
)


# ------------------------------------------------------------
# Save a copy.
# ------------------------------------------------------------

figure_file = (
    OUTPUT_DIRECTORY
    / "ANOVA_spatial_grid.png"
)


fig.savefig(
    figure_file,
    dpi=200,
    bbox_inches="tight",
)


print()
print(
    f"Saved figure to:\n"
    f"  {figure_file.resolve()}"
)


# ------------------------------------------------------------
# POP THE FIGURE UP.
# ------------------------------------------------------------

plt.show()


# ============================================================
# OPTIONAL SECOND FIGURE:
# TOTAL SS
# ============================================================

fig2, ax2 = plt.subplots(
    figsize=(9, 6)
)


total_image = ax2.imshow(
    total_ss,
    origin="upper",
    cmap="magma",
    interpolation="nearest",
)


ax2.set_title(
    "Total Spatial Sum of Squares",
    fontsize=15,
    fontweight="bold",
)


ax2.set_xticks([])
ax2.set_yticks([])


cbar2 = fig2.colorbar(
    total_image,
    ax=ax2,
)


cbar2.set_label(
    "Total SS",
)


fig2.tight_layout()


total_figure_file = (
    OUTPUT_DIRECTORY
    / "total_SS_map.png"
)


fig2.savefig(
    total_figure_file,
    dpi=200,
    bbox_inches="tight",
)


print(
    f"Saved total SS map to:\n"
    f"  {total_figure_file.resolve()}"
)


plt.show()


# ============================================================
# FINISHED
# ============================================================

print()
print("=" * 70)
print("SUCCESS")
print("=" * 70)

print(
    "Spatial ANOVA completed for all 48 factorial suites."
)

print(
    f"ANOVA grid: {figure_file.resolve()}"
)

print(
    f"Total SS map: {total_figure_file.resolve()}"
)
