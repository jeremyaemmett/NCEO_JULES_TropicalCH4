from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# =====================================================
# SETTINGS
# =====================================================

directory = Path(
    "/Users/jae35/Desktop/JULES_test_data/ID_suites"
)

# True  = read scaled data
# False = read unscaled data
apply_scale_factor = True

scale_folder = (
    "scaled"
    if apply_scale_factor
    else "unscaled"
)


# =====================================================
# ANOVA SETTINGS
# =====================================================

# True:
#   Plot all main effects + all interactions
#
# False:
#   Plot main effects only, with omitted interaction
#   variance shown as "Interactions / unaccounted".

include_interactions = False


print("Using:", scale_folder, "data")

print(
    "Interactions:",
    "ON" if include_interactions else "OFF"
)


# =====================================================
# MONTHS
# =====================================================

months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


# =====================================================
# ORIGINAL ENSEMBLE VISUAL ENCODING
# =====================================================

# -----------------------------------------------------
# Colour = substrate
# -----------------------------------------------------

substrates = [
    "0",
    "1",
    "2"
]

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


# -----------------------------------------------------
# Line style = soil map
# -----------------------------------------------------

soil_styles = {
    "0": "-",
    "1": "--"
}

soil_labels = {
    "0": "Standard",
    "1": "Oxi + Ulti"
}


# -----------------------------------------------------
# Line width = Q10
# -----------------------------------------------------

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


# =====================================================
# FIND ENSEMBLE MEMBERS
# =====================================================

files = []
rows = []


for subdir in sorted(directory.iterdir()):

    if not subdir.is_dir():
        continue

    name = subdir.name

    # -------------------------------------------------
    # Decode ensemble member
    #
    # Example:
    #
    # u-dk105_231
    #
    # 2 = substrate
    # 3 = Q10
    # 1 = soil map
    # -------------------------------------------------

    try:

        code = name.split("_")[1]

        if len(code) < 3:
            continue

        substrate = code[0]
        q10 = code[1]
        soilmap = code[2]

    except IndexError:

        continue


    # -------------------------------------------------
    # Only accept recognised factor codes
    # -------------------------------------------------

    if substrate not in color_map:
        continue

    if q10 not in q10_width:
        continue

    if soilmap not in soil_styles:
        continue


    # -------------------------------------------------
    # File path
    # -------------------------------------------------

    filepath = (
        subdir
        / "plots"
        / "output"
        / scale_folder
        / "fch4_wetl"
        / "_arealmean_tseries.txt"
    )


    if not filepath.exists():
        continue


    # -------------------------------------------------
    # Read monthly data
    # -------------------------------------------------

    y = np.loadtxt(filepath)


    if len(y) != 12:

        print(
            f"Skipping {name}: "
            f"expected 12 months, "
            f"found {len(y)}"
        )

        continue


    # -------------------------------------------------
    # Store plotting information
    # -------------------------------------------------

    files.append(
        (
            name,
            substrate,
            q10,
            soilmap,
            filepath
        )
    )


    # -------------------------------------------------
    # Store data for ANOVA
    # -------------------------------------------------

    row = {

        "suite": name,

        "substrate": int(substrate),

        "q10": int(q10),

        "soilmap": int(soilmap)
    }


    for i, month in enumerate(months):

        row[month] = y[i]


    rows.append(row)


# =====================================================
# DATAFRAME
# =====================================================

df = pd.DataFrame(rows)


if df.empty:

    raise RuntimeError(
        "No valid ensemble members were found."
    )


# =====================================================
# REPORT ENSEMBLE
# =====================================================

print()
print(
    "Suites plotted:",
    len(files)
)

print(
    "Substrate codes found:",
    sorted(
        df["substrate"].unique()
    )
)

print(
    "Q10 codes found:",
    sorted(
        df["q10"].unique()
    )
)

print(
    "Soil map codes found:",
    sorted(
        df["soilmap"].unique()
    )
)


# =====================================================
# CHECK FOR BALANCED FACTORIAL DESIGN
# =====================================================

expected_n = (
    len(df["substrate"].unique())
    *
    len(df["q10"].unique())
    *
    len(df["soilmap"].unique())
)

actual_n = len(df)


print()
print(
    "Expected full factorial:",
    expected_n
)

print(
    "Actual ensemble members:",
    actual_n
)


if actual_n != expected_n:

    print(
        "WARNING: ensemble is not a complete "
        "factorial design."
    )


# =====================================================
# ANOVA DECOMPOSITION
# =====================================================

def anova_decomposition(
    data,
    response
):

    """
    Full factorial sum-of-squares decomposition.

    Returns:

        substrate
        q10
        soilmap

    and, if requested:

        substrate:q10
        substrate:soilmap
        q10:soilmap
        substrate:q10:soilmap

    The percentages are always relative to TOTAL
    ensemble variance. They are NOT renormalised.
    """


    # =================================================
    # GRAND MEAN
    # =================================================

    grand_mean = (
        data[response].mean()
    )


    # =================================================
    # TOTAL SUM OF SQUARES
    # =================================================

    total_ss = np.sum(
        (
            data[response]
            - grand_mean
        ) ** 2
    )


    components = {}


    # =================================================
    # MAIN EFFECTS
    # =================================================

    for factor in [
        "substrate",
        "q10",
        "soilmap"
    ]:

        means = (
            data
            .groupby(factor)[response]
            .mean()
        )


        ss = 0.0


        for level, mean in means.items():

            n = np.sum(
                data[factor] == level
            )


            ss += (
                n
                *
                (
                    mean
                    - grand_mean
                ) ** 2
            )


        components[
            factor
        ] = ss


    # =================================================
    # TWO-WAY INTERACTIONS
    # =================================================

    if include_interactions:

        pairs = [

            (
                "substrate",
                "q10"
            ),

            (
                "substrate",
                "soilmap"
            ),

            (
                "q10",
                "soilmap"
            )
        ]


        for a, b in pairs:

            cell_means = (
                data
                .groupby(
                    [a, b]
                )[response]
                .mean()
            )


            mean_a = (
                data
                .groupby(a)[response]
                .mean()
            )


            mean_b = (
                data
                .groupby(b)[response]
                .mean()
            )


            ss = 0.0


            for (
                ia,
                ib
            ), cell_mean in cell_means.items():

                interaction = (

                    cell_mean

                    - mean_a.loc[ia]

                    - mean_b.loc[ib]

                    + grand_mean
                )


                n = np.sum(
                    (
                        data[a] == ia
                    )
                    &
                    (
                        data[b] == ib
                    )
                )


                ss += (
                    n
                    *
                    interaction ** 2
                )


            components[
                f"{a}:{b}"
            ] = ss


        # =================================================
        # THREE-WAY INTERACTION
        # =================================================

        cell_means = (
            data
            .groupby(
                [
                    "substrate",
                    "q10",
                    "soilmap"
                ]
            )[response]
            .mean()
        )


        mean_s = (
            data
            .groupby(
                "substrate"
            )[response]
            .mean()
        )


        mean_q = (
            data
            .groupby(
                "q10"
            )[response]
            .mean()
        )


        mean_m = (
            data
            .groupby(
                "soilmap"
            )[response]
            .mean()
        )


        mean_sq = (
            data
            .groupby(
                [
                    "substrate",
                    "q10"
                ]
            )[response]
            .mean()
        )


        mean_sm = (
            data
            .groupby(
                [
                    "substrate",
                    "soilmap"
                ]
            )[response]
            .mean()
        )


        mean_qm = (
            data
            .groupby(
                [
                    "q10",
                    "soilmap"
                ]
            )[response]
            .mean()
        )


        ss = 0.0


        for (
            s,
            q,
            m
        ), cell_mean in cell_means.items():

            interaction = (

                cell_mean

                - mean_sq.loc[
                    (s, q)
                ]

                - mean_sm.loc[
                    (s, m)
                ]

                - mean_qm.loc[
                    (q, m)
                ]

                + mean_s.loc[s]

                + mean_q.loc[q]

                + mean_m.loc[m]

                - grand_mean
            )


            ss += (
                interaction ** 2
            )


        components[
            "substrate:q10:soilmap"
        ] = ss


    # =================================================
    # RESULTS
    # =================================================

    result = pd.DataFrame(
        {
            "sum_sq": components
        }
    )


    if total_ss > 0:

        result["percent"] = (
            result["sum_sq"]
            / total_ss
            * 100
        )

    else:

        result["percent"] = 0.0


    return (
        result,
        total_ss
    )


# =====================================================
# COMPONENTS
# =====================================================

all_components = [

    "substrate",

    "q10",

    "soilmap",

    "substrate:q10",

    "substrate:soilmap",

    "q10:soilmap",

    "substrate:q10:soilmap"
]


main_components = [

    "substrate",

    "q10",

    "soilmap"
]


# =====================================================
# RUN MONTHLY ANOVA
# =====================================================

all_results = []


for month in months:

    result, total_ss = (
        anova_decomposition(
            df,
            month
        )
    )


    for component, row in result.iterrows():

        all_results.append(
            {

                "month": month,

                "component": component,

                "sum_sq": row["sum_sq"],

                "percent": row["percent"],

                "total_ss": total_ss
            }
        )


anova_df = pd.DataFrame(
    all_results
)


# =====================================================
# CALCULATE UNACCOUNTED VARIANCE
# =====================================================
#
# This is the key part.
#
# When interactions are OFF:
#
#   unaccounted =
#       100%
#       - substrate
#       - q10
#       - soilmap
#
# This is NOT unexplained numerical error.
# It represents the variance attributable to the
# interaction terms that were deliberately omitted.
#
# When interactions are ON, all interaction terms are
# explicitly plotted, so no unaccounted category is
# required.
# =====================================================

if not include_interactions:

    unaccounted_rows = []


    for month in months:

        subset = anova_df[
            anova_df["month"] == month
        ]


        main_percent = (
            subset[
                subset["component"].isin(
                    main_components
                )
            ]["percent"]
            .sum()
        )


        unaccounted = (
            100.0
            - main_percent
        )


        # Small numerical rounding errors can produce
        # values such as -1e-14.

        if abs(unaccounted) < 1e-10:

            unaccounted = 0.0


        unaccounted_rows.append(
            {
                "month": month,

                "component":
                    "interactions_unaccounted",

                "sum_sq":
                    np.nan,

                "percent":
                    unaccounted,

                "total_ss":
                    subset["total_ss"].iloc[0]
            }
        )


    anova_df = pd.concat(
        [
            anova_df,
            pd.DataFrame(
                unaccounted_rows
            )
        ],
        ignore_index=True
    )


# =====================================================
# PRINT ANOVA RESULTS
# =====================================================

print()
print("=" * 75)
print("MONTHLY VARIANCE DECOMPOSITION")
print("=" * 75)


for month in months:

    print()
    print(month)
    print("-" * 55)


    subset = anova_df[
        anova_df["month"] == month
    ]


    if include_interactions:

        display_components = all_components

    else:

        display_components = (
            main_components
            + [
                "interactions_unaccounted"
            ]
        )


    for component in display_components:

        row = subset[
            subset["component"] == component
        ]


        if len(row) == 0:
            continue


        value = row[
            "percent"
        ].iloc[0]


        print(
            f"{component:32s}"
            f"{value:8.3f}%"
        )


# =====================================================
# COMPONENTS FOR PLOT
# =====================================================

if include_interactions:

    plot_components = all_components

else:

    plot_components = [

        "substrate",

        "q10",

        "soilmap",

        "interactions_unaccounted"
    ]


# =====================================================
# PIVOT FOR PLOT
# =====================================================

plot_df = (
    anova_df
    .pivot(
        index="month",
        columns="component",
        values="percent"
    )
    .reindex(months)
)


plot_df = plot_df[
    plot_components
]


# =====================================================
# VERIFY THAT PLOT SUMS TO 100%
# =====================================================

plot_totals = (
    plot_df.sum(
        axis=1
    )
)


print()
print("=" * 75)
print("CHECK: PLOTTED VARIANCE")
print("=" * 75)


for month, total in plot_totals.items():

    print(
        f"{month:5s}"
        f"{total:12.6f}%"
    )


if not np.allclose(
    plot_totals.values,
    100.0,
    atol=1e-8
):

    raise RuntimeError(
        "Variance decomposition does not sum "
        "to 100%. Check the ANOVA calculation."
    )


# =====================================================
# ANOVA COLOURS
# =====================================================

component_colours = {

    "substrate":
        "#8c510a",

    "q10":
        "#01665e",

    "soilmap":
        "#5ab4ac",

    "substrate:q10":
        "#d8b365",

    "substrate:soilmap":
        "#dfc27d",

    "q10:soilmap":
        "#80cdc1",

    "substrate:q10:soilmap":
        "#c7eae5",

    "interactions_unaccounted":
        "#bdbdbd"
}


component_labels = {

    "substrate":
        "Substrate",

    "q10":
        "Q10",

    "soilmap":
        "Soil map",

    "substrate:q10":
        "Substrate × Q10",

    "substrate:soilmap":
        "Substrate × soil map",

    "q10:soilmap":
        "Q10 × soil map",

    "substrate:q10:soilmap":
        "Substrate × Q10 × soil map",

    "interactions_unaccounted":
        "Interactions / unaccounted"
}


# =====================================================
# FIGURE
# =====================================================

fig, ax = plt.subplots(
    figsize=(16, 8)
)


# =====================================================
# ANOVA SECONDARY AXIS
# =====================================================

ax_anova = ax.twinx()


ax_anova.set_ylim(
    0,
    100
)


ax_anova.set_ylabel(
    "Variance contribution (%)",
    color="0.35"
)


ax_anova.tick_params(
    axis="y",
    colors="0.35"
)


ax_anova.spines[
    "right"
].set_color(
    "0.7"
)


# =====================================================
# ANOVA STACKED BACKGROUND
# =====================================================

x = np.arange(
    12
)


ax_anova.stackplot(
    x,

    *[
        plot_df[c].values
        for c in plot_components
    ],

    colors=[
        component_colours[c]
        for c in plot_components
    ],

    alpha=0.28,

    zorder=1
)


# =====================================================
# ORIGINAL ENSEMBLE CURVES
# =====================================================

for (
    name,
    substrate,
    q10,
    soilmap,
    filepath
) in files:

    y = np.loadtxt(
        filepath
    )


    ax.plot(
        y,

        color=color_map[
            substrate
        ],

        linestyle=soil_styles[
            soilmap
        ],

        linewidth=q10_width[
            q10
        ],

        alpha=0.85,

        zorder=10
    )


# =====================================================
# ORIGINAL AXIS FORMATTING
# =====================================================

ax.set_xticks(
    range(12)
)

ax.set_xticklabels(
    months
)


ax.set_xlabel(
    "Month"
)


ax.set_ylabel(
    "f$_{CH4}$"
)


ax.set_title(
    f"Global Mean f$_{{CH4}}$ Ensemble (2005) — "
    f"{scale_folder.capitalize()}"
)


ax.grid(
    alpha=0.3
)


# Keep ANOVA background transparent

ax_anova.patch.set_alpha(
    0
)


# =====================================================
# ANOVA LEGEND
# =====================================================

anova_handles = [
    Line2D(
        [0],
        [0],

        color=component_colours[c],

        linewidth=7,

        alpha=0.55,

        label=component_labels[c]
    )

    for c in plot_components
]


anova_legend = ax.legend(
    handles=anova_handles,

    title="ANOVA variance contribution",

    loc="upper left",

    bbox_to_anchor=(
        0.01,
        0.73
    ),

    frameon=False,

    fontsize=8
)


ax.add_artist(
    anova_legend
)


# =====================================================
# ORIGINAL SUBSTRATE LEGEND
# =====================================================

substrate_handles = [
    Line2D(
        [0],
        [0],

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

    bbox_to_anchor=(
        0.01,
        0.99
    ),

    frameon=False
)


ax.add_artist(
    leg1
)


# =====================================================
# ORIGINAL SOIL MAP LEGEND
# =====================================================

soil_handles = [
    Line2D(
        [0],
        [0],

        color="black",

        linewidth=2,

        linestyle=soil_styles[s],

        label=soil_labels[s]
    )

    for s in [
        "0",
        "1"
    ]
]


leg2 = ax.legend(
    handles=soil_handles,

    title="Soil map",

    loc="upper left",

    bbox_to_anchor=(
        0.10,
        0.99
    ),

    frameon=False
)


ax.add_artist(
    leg2
)


# =====================================================
# ORIGINAL Q10 LEGEND
# =====================================================

q10_handles = [
    Line2D(
        [0],
        [0],

        color="black",

        linewidth=q10_width[q],

        label=q10_labels[q]
    )

    for q in sorted(
        q10_width
    )
]


leg3 = ax.legend(
    handles=q10_handles,

    title="Q10",

    loc="upper left",

    bbox_to_anchor=(
        0.28,
        0.99
    ),

    frameon=False
)


ax.add_artist(
    leg3
)


# =====================================================
# SAVE
# =====================================================

plt.tight_layout()


output_directory = (
    directory
    / scale_folder
)


output_directory.mkdir(
    parents=True,
    exist_ok=True
)


interaction_suffix = (
    "with_interactions"
    if include_interactions
    else "main_effects_plus_unaccounted"
)


# =====================================================
# SAVE ANOVA TABLE
# =====================================================

csv_file = (
    output_directory
    / (
        "monthly_anova_"
        f"{interaction_suffix}.csv"
    )
)


anova_df.to_csv(
    csv_file,
    index=False
)


# =====================================================
# SAVE FIGURE
# =====================================================

output_file = (
    output_directory
    / (
        "monthly_anova_"
        f"{interaction_suffix}_ensemble.png"
    )
)


plt.savefig(
    output_file,

    dpi=300,

    bbox_inches="tight"
)


print()
print(
    "Saved ANOVA table:",
    csv_file
)

print(
    "Saved figure:",
    output_file
)


plt.show()