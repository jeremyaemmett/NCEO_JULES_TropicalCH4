from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader


# =====================================================
# SETTINGS
# =====================================================

directory = Path(
    "/Users/jae35/Desktop/JULES_test_data/ID_suites"
)

# -----------------------------------------------------
# NetCDF containing the latitude / longitude grid.
#
# CHANGE THIS TO THE ACTUAL NETCDF FILE USED BY JULES.
# -----------------------------------------------------

NETCDF_FILE = Path(
    "/Users/jae35/Desktop/JULES_test_data/ID_suites/u-dk105_0100/CRUJRA2.4_2023_n96_v8.0_S3.ilamb.2015.nc"
)

# -----------------------------------------------------
# The 2D map produced by JULES.
# This is a TEXT file, NOT a PNG.
# -----------------------------------------------------

MAP_FILENAME = "fch4_wetl_2005_(5)Jun_map.txt"


FACTORS = [
    "substrate",
    "q10",
    "soilmap",
    "competition",
]


# =====================================================
# VARIABLE TABLE
# =====================================================

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


expected_combinations = {
    tuple(row[f] for f in FACTORS)
    for _, row in variable_table.iterrows()
}


# =====================================================
# READ LAT/LON FROM NETCDF
# =====================================================

def read_lat_lon_from_netcdf(netcdf_file):
    """
    Read latitude and longitude from the NetCDF.

    Supports:
        latitude / longitude
        lat / lon

    Also supports either 1D or 2D coordinates.
    """

    import xarray as xr

    print("\n==============================================")
    print("READING LATITUDE / LONGITUDE")
    print("==============================================")

    print("NetCDF:", netcdf_file)

    ds = xr.open_dataset(netcdf_file)

    # -------------------------------------------------
    # Find latitude variable
    # -------------------------------------------------

    if "latitude" in ds.variables:
        lat = ds["latitude"].values

    elif "lat" in ds.variables:
        lat = ds["lat"].values

    else:
        raise ValueError(
            "Could not find latitude variable in NetCDF. "
            "Expected 'latitude' or 'lat'."
        )

    # -------------------------------------------------
    # Find longitude variable
    # -------------------------------------------------

    if "longitude" in ds.variables:
        lon = ds["longitude"].values

    elif "lon" in ds.variables:
        lon = ds["lon"].values

    else:
        raise ValueError(
            "Could not find longitude variable in NetCDF. "
            "Expected 'longitude' or 'lon'."
        )

    ds.close()

    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)

    print("Latitude shape:", lat.shape)
    print("Longitude shape:", lon.shape)

    # -------------------------------------------------
    # If coordinates are already 2D, use them directly.
    # -------------------------------------------------

    if lat.ndim == 2 and lon.ndim == 2:

        if lat.shape != lon.shape:
            raise ValueError(
                f"2D latitude shape {lat.shape} does not match "
                f"longitude shape {lon.shape}"
            )

        lat2d = lat
        lon2d = lon

    # -------------------------------------------------
    # If coordinates are 1D, construct mesh.
    # -------------------------------------------------

    elif lat.ndim == 1 and lon.ndim == 1:

        lon2d, lat2d = np.meshgrid(
            lon,
            lat,
        )

    else:

        raise ValueError(
            "Latitude and longitude must both be 1D "
            "or both be 2D."
        )

    print("Map grid shape:", lat2d.shape)

    print(
        f"Latitude range:  "
        f"{np.nanmin(lat2d):.4f} to "
        f"{np.nanmax(lat2d):.4f}"
    )

    print(
        f"Longitude range: "
        f"{np.nanmin(lon2d):.4f} to "
        f"{np.nanmax(lon2d):.4f}"
    )

    return lat2d, lon2d


# =====================================================
# READ ONE 2D MAP
# =====================================================

def read_map(filepath, expected_shape):
    """
    Read one JULES 2D map text file.

    NaN values are retained as missing spatial cells.
    """

    try:

        data = np.loadtxt(
            filepath,
            dtype=float,
        )

    except Exception as exc:

        raise ValueError(
            f"Could not read map:\n"
            f"{filepath}\n"
            f"Reason: {exc}"
        )

    data = np.asarray(data, dtype=float)

    if data.ndim != 2:

        raise ValueError(
            f"Expected a 2D map in {filepath}, "
            f"but got shape {data.shape}"
        )

    if data.shape != expected_shape:

        raise ValueError(
            f"Map shape mismatch:\n"
            f"  file: {filepath}\n"
            f"  map shape: {data.shape}\n"
            f"  coordinate shape: {expected_shape}"
        )

    return data


# =====================================================
# MAP ALL SUITES
# =====================================================

def load_all_maps():

    suite_directories = sorted(
        p for p in directory.iterdir()
        if p.is_dir()
    )

    print("\n==============================================")
    print("SUITE DIRECTORY CHECK")
    print("==============================================")

    print(
        f"Suite directories found: "
        f"{len(suite_directories)}"
    )

    if len(suite_directories) != 48:

        raise ValueError(
            f"Expected 48 suite directories, "
            f"but found {len(suite_directories)}"
        )

    maps = {}

    suite_names = []

    for subdir in suite_directories:

        name = subdir.name

        # -------------------------------------------------
        # Extract four-digit factorial code.
        # -------------------------------------------------

        code = name.split("_")[-1]

        if len(code) != 4 or not code.isdigit():

            print(
                f"Skipping suite with invalid code: {name}"
            )

            continue

        combination = tuple(
            int(x)
            for x in code
        )

        if combination not in expected_combinations:

            print(
                f"WARNING: unexpected combination "
                f"{combination} in {name}"
            )

            continue

        filepath = subdir / "plots" / "output" / "scaled" / "fch4_wetl" / MAP_FILENAME

        if not filepath.exists():

            raise FileNotFoundError(
                "\nMISSING MAP:\n"
                f"  suite: {name}\n"
                f"  file:  {filepath}"
            )

        suite_names.append(name)

        maps[combination] = filepath

        print(
            f"FOUND: {name:15s} "
            f"S={combination[0]} "
            f"Q={combination[1]} "
            f"M={combination[2]} "
            f"C={combination[3]}"
        )

    if len(maps) != 48:

        raise ValueError(
            f"Expected 48 maps but found {len(maps)}"
        )

    return maps


# =====================================================
# BUILD 4D ARRAY
# =====================================================

def build_data_array(map_files, lat2d, lon2d):

    ny, nx = lat2d.shape

    data = np.full(
        (
            3,      # substrate
            4,      # q10
            2,      # soilmap
            2,      # competition
            ny,
            nx,
        ),
        np.nan,
        dtype=float,
    )

    print("\n==============================================")
    print("READING 2D MAPS")
    print("==============================================")

    for combination, filepath in sorted(
        map_files.items()
    ):

        substrate, q10, soilmap, competition = combination

        print(
            f"Reading "
            f"S={substrate} "
            f"Q={q10} "
            f"M={soilmap} "
            f"C={competition}"
        )

        values = read_map(
            filepath,
            lat2d.shape,
        )

        data[
            substrate,
            q10,
            soilmap,
            competition,
            :, :
        ] = values

    return data


# =====================================================
# FACTORIAL EFFECT CALCULATION
# =====================================================

def calculate_effect(
    data,
    target_factors,
    factor_axes,
):
    """
    Calculate the pure factorial effect at every
    spatial grid cell.

    Missing values are handled using nanmean.

    target_factors:
        e.g. ("substrate",)

        or ("substrate", "q10")

        or ("substrate", "q10", "soilmap")

        etc.

    Returns:
        effect[lat, lon]
    """

    all_factors = list(FACTORS)

    k = len(target_factors)

    effect = np.zeros(
        data.shape[-2:],
        dtype=float,
    )

    # -------------------------------------------------
    # Inclusion-exclusion over all subsets.
    # -------------------------------------------------

    for subset_size in range(k + 1):

        for subset in combinations(
            target_factors,
            subset_size,
        ):

            # -------------------------------------------------
            # Sign:
            #
            # (-1)^(k - subset_size)
            # -------------------------------------------------

            sign = (
                -1
                if (k - subset_size) % 2
                else 1
            )

            if subset_size == 0:

                # Grand mean over all 48 factorial cells.
                marginal = np.nanmean(
                    data,
                    axis=tuple(
                        factor_axes[f]
                        for f in all_factors
                    ),
                )

            else:

                # -------------------------------------------------
                # Average over factors NOT in subset.
                # -------------------------------------------------

                axes_to_average = [
                    factor_axes[f]
                    for f in all_factors
                    if f not in subset
                ]

                marginal = np.nanmean(
                    data,
                    axis=tuple(
                        axes_to_average
                    ),
                )

                # -------------------------------------------------
                # marginal currently has dimensions:
                #
                # subset-factor dimensions + lat + lon
                #
                # We need to average over the subset levels too
                # only when calculating each combination's effect.
                #
                # For the spatial ANOVA SS we need the effect for
                # each target combination, so this function is
                # instead handled below by summing all combination
                # effects.
                # -------------------------------------------------

            # This branch is not used directly here.
            # The actual spatial SS calculation is below.

    raise RuntimeError(
        "calculate_effect should not be called directly."
    )


# =====================================================
# PURE EFFECTS FOR EVERY FACTOR COMBINATION
# =====================================================

def calculate_spatial_anova(data):

    """
    Calculate spatial sum of squares for all 15
    factorial terms.

    Returns:

        components[name] = 2D SS map

    where each pixel contains the ANOVA SS for that
    factorial term.
    """

    n_factors = len(FACTORS)

    factor_sizes = {
        "substrate": 3,
        "q10": 4,
        "soilmap": 2,
        "competition": 2,
    }

    ny, nx = data.shape[-2:]

    # -------------------------------------------------
    # Grand mean.
    # -------------------------------------------------

    grand_mean = np.nanmean(
        data,
        axis=(0, 1, 2, 3),
    )

    # -------------------------------------------------
    # Valid observation count.
    # -------------------------------------------------

    valid_count = np.sum(
        np.isfinite(data),
        axis=(0, 1, 2, 3),
    )

    components = {}

    effect_order = []

    # -------------------------------------------------
    # Loop through every non-empty factor subset.
    # -------------------------------------------------

    for order in range(
        1,
        n_factors + 1,
    ):

        for target in combinations(
            FACTORS,
            order,
        ):

            name = ":".join(target)

            print(
                f"Calculating {name}"
            )

            # -------------------------------------------------
            # Pure effect for each target-level combination.
            #
            # We store:
            #
            # effect[level combination, lat, lon]
            # -------------------------------------------------

            target_shape = [
                factor_sizes[f]
                for f in target
            ]

            effects = np.zeros(
                target_shape + [ny, nx],
                dtype=float,
            )

            # -------------------------------------------------
            # Iterate over every target combination.
            # -------------------------------------------------

            for target_indices in np.ndindex(
                *target_shape
            ):

                effect = np.zeros(
                    (ny, nx),
                    dtype=float,
                )

                # -------------------------------------------------
                # Inclusion-exclusion.
                # -------------------------------------------------

                for subset_size in range(
                    order + 1
                ):

                    for subset in combinations(
                        target,
                        subset_size,
                    ):

                        sign = (
                            -1
                            if (
                                order - subset_size
                            ) % 2
                            else 1
                        )

                        # -------------------------------------------------
                        # Empty subset = grand mean.
                        # -------------------------------------------------

                        if subset_size == 0:

                            marginal = grand_mean

                        else:

                            # -------------------------------------------------
                            # Determine target indices belonging to subset.
                            # -------------------------------------------------

                            subset_positions = [
                                target.index(f)
                                for f in subset
                            ]

                            subset_indices = tuple(
                                target_indices[p]
                                for p in subset_positions
                            )

                            # -------------------------------------------------
                            # Axes to average over:
                            #
                            # all factorial axes except those in subset.
                            # -------------------------------------------------

                            axes = []

                            for factor in FACTORS:

                                if factor not in subset:

                                    axes.append(
                                        FACTORS.index(
                                            factor
                                        )
                                    )

                            # -------------------------------------------------
                            # np.nanmean over factorial dimensions.
                            # -------------------------------------------------

                            marginal_all = np.nanmean(
                                data,
                                axis=tuple(axes),
                            )

                            # -------------------------------------------------
                            # marginal_all now has dimensions:
                            #
                            # subset dimensions + lat + lon
                            #
                            # Select the desired subset combination.
                            # -------------------------------------------------

                            selector = (
                                subset_indices
                                + (
                                    slice(None),
                                    slice(None),
                                )
                            )

                            marginal = marginal_all[
                                selector
                            ]

                        effect += (
                            sign * marginal
                        )

                effects[
                    target_indices
                ] = effect

            # -------------------------------------------------
            # Sum of squares for this term.
            #
            # With one observation per factorial cell:
            #
            # SS = sum(effect^2)
            #
            # across all levels of the term.
            # -------------------------------------------------

            ss = np.nansum(
                effects ** 2,
                axis=tuple(
                    range(order)
                ),
            )

            # -------------------------------------------------
            # Mask locations where there are no observations.
            # -------------------------------------------------

            ss[
                valid_count == 0
            ] = np.nan

            components[name] = ss

            effect_order.append(name)

    return (
        components,
        grand_mean,
        valid_count,
        effect_order,
    )


# =====================================================
# CHECK TOTAL SUM OF SQUARES
# =====================================================

def calculate_total_ss(data):

    grand_mean = np.nanmean(
        data,
        axis=(0, 1, 2, 3),
    )

    total_ss = np.nansum(
        (
            data
            - grand_mean[None, None, None, None, :, :]
        ) ** 2,
        axis=(0, 1, 2, 3),
    )

    valid_count = np.sum(
        np.isfinite(data),
        axis=(0, 1, 2, 3),
    )

    total_ss[
        valid_count == 0
    ] = np.nan

    return total_ss


# =====================================================
# MAP STYLE
# =====================================================

def create_map(
    lat2d,
    lon2d,
    title,
):

    fig = plt.figure(
        figsize=(16, 9)
    )

    ax = plt.axes(
        projection=ccrs.Robinson()
    )

    ax.set_global()

    # -------------------------------------------------
    # Land
    # -------------------------------------------------

    ax.add_feature(
        cfeature.LAND,
        facecolor="#f5e6c8",
        zorder=1,
    )

    # -------------------------------------------------
    # Ocean
    # -------------------------------------------------

    ax.add_feature(
        cfeature.OCEAN,
        facecolor="#a6cee3",
        zorder=1,
        alpha=0.5,
    )

    # -------------------------------------------------
    # Lakes
    # -------------------------------------------------

    ax.add_feature(
        cfeature.LAKES,
        facecolor="#a6cee3",
        zorder=1,
        alpha=0.5,
    )

    # -------------------------------------------------
    # Rivers
    # -------------------------------------------------

    ax.add_feature(
        cfeature.RIVERS.with_scale("50m"),
        edgecolor="blue",
        linewidth=0.5,
        zorder=2,
    )

    # -------------------------------------------------
    # Borders
    # -------------------------------------------------

    ax.add_feature(
        cfeature.BORDERS.with_scale("50m"),
        linewidth=1.0,
        edgecolor="gray",
        zorder=3,
    )

    ax.coastlines(
        resolution="50m",
        zorder=4,
    )

    # -------------------------------------------------
    # Gridlines
    # -------------------------------------------------

    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.5,
        color="gray",
        alpha=0.7,
        linestyle="--",
    )

    gl.top_labels = False
    gl.right_labels = False

    gl.xlabel_style = {
        "fontsize": 12
    }

    gl.ylabel_style = {
        "fontsize": 12
    }

    ax.set_title(
        title,
        fontsize=18,
        fontweight="bold",
        loc="left",
    )

    return fig, ax


# =====================================================
# PLOT ONE ANOVA MAP
# =====================================================

def plot_anova_map(
    lat2d,
    lon2d,
    values,
    title,
    output_file,
    vmax=100,
):

    fig, ax = create_map(
        lat2d,
        lon2d,
        title,
    )

    masked = np.ma.masked_invalid(
        values
    )

    mesh = ax.pcolormesh(
        lon2d,
        lat2d,
        masked,
        transform=ccrs.PlateCarree(),
        shading="auto",
        cmap="viridis",
        vmin=0,
        vmax=vmax,
        zorder=5,
    )

    cbar = plt.colorbar(
        mesh,
        ax=ax,
        orientation="horizontal",
        pad=0.05,
        shrink=0.7,
    )

    cbar.set_label(
        "Contribution to variance (%)",
        fontsize=12,
    )

    cbar.ax.tick_params(
        labelsize=10
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        "Saved:",
        output_file,
    )


# =====================================================
# PLOT ALL 15 MAPS IN ONE GRID
# =====================================================

def plot_anova_grid(
    lat2d,
    lon2d,
    components,
    total_ss,
    effect_order,
    output_file,
):

    print("\n==============================================")
    print("CREATING ANOVA GRID")
    print("==============================================")

    n_maps = len(effect_order)

    ncols = 3
    nrows = int(
        np.ceil(
            n_maps / ncols
        )
    )

    fig = plt.figure(
        figsize=(
            18,
            5.5 * nrows,
        )
    )

    for i, name in enumerate(
        effect_order
    ):

        print(
            f"Plotting {name}"
        )

        ax = fig.add_subplot(
            nrows,
            ncols,
            i + 1,
            projection=ccrs.Robinson(),
        )

        ax.set_global()

        # -------------------------------------------------
        # Background.
        # -------------------------------------------------

        ax.add_feature(
            cfeature.LAND,
            facecolor="#f5e6c8",
            zorder=1,
        )

        ax.add_feature(
            cfeature.OCEAN,
            facecolor="#a6cee3",
            alpha=0.5,
            zorder=1,
        )

        ax.add_feature(
            cfeature.LAKES,
            facecolor="#a6cee3",
            alpha=0.5,
            zorder=1,
        )

        ax.add_feature(
            cfeature.BORDERS.with_scale("50m"),
            linewidth=0.5,
            edgecolor="gray",
            zorder=3,
        )

        ax.coastlines(
            resolution="50m",
            zorder=4,
        )

        # -------------------------------------------------
        # Percentage contribution.
        # -------------------------------------------------

        percentage = (
            components[name]
            / total_ss
            * 100.0
        )

        percentage[
            ~np.isfinite(total_ss)
            | (total_ss == 0)
        ] = np.nan

        percentage = np.clip(
            percentage,
            0,
            100,
        )

        masked = np.ma.masked_invalid(
            percentage
        )

        mesh = ax.pcolormesh(
            lon2d,
            lat2d,
            masked,
            transform=ccrs.PlateCarree(),
            shading="auto",
            cmap="viridis",
            vmin=0,
            vmax=100,
            zorder=5,
        )

        # -------------------------------------------------
        # Title.
        # -------------------------------------------------

        ax.set_title(
            name,
            fontsize=16,
            fontweight="bold",
        )

        # -------------------------------------------------
        # Gridlines.
        # -------------------------------------------------

        gl = ax.gridlines(
            draw_labels=True,
            linewidth=0.4,
            color="gray",
            alpha=0.6,
            linestyle="--",
        )

        gl.top_labels = False
        gl.right_labels = False

        gl.xlabel_style = {
            "fontsize": 9
        }

        gl.ylabel_style = {
            "fontsize": 9
        }

        # -------------------------------------------------
        # Individual colorbar.
        # -------------------------------------------------

        cbar = plt.colorbar(
            mesh,
            ax=ax,
            orientation="horizontal",
            pad=0.035,
            shrink=0.8,
        )

        cbar.set_label(
            "%",
            fontsize=10,
        )

        cbar.ax.tick_params(
            labelsize=8
        )

    # -----------------------------------------------------
    # Overall title.
    # -----------------------------------------------------

    fig.suptitle(
        "Spatial 4-Factor ANOVA — fCH₄ wetland\n"
        "2005 June",
        fontsize=24,
        fontweight="bold",
        y=0.995,
    )

    plt.tight_layout(
        rect=[
            0,
            0,
            1,
            0.98,
        ]
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    # -------------------------------------------------
    # SHOW MAP WINDOW
    # -------------------------------------------------

    plt.show()

    plt.close()

    print(
        "\nSaved ANOVA grid:",
        output_file,
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print("\n")
    print("==============================================")
    print("SPATIAL FACTORIAL ANOVA")
    print("==============================================")
    print(
        "Map:",
        MAP_FILENAME,
    )

    # -------------------------------------------------
    # 1. Read coordinates from NetCDF.
    # -------------------------------------------------

    lat2d, lon2d = (
        read_lat_lon_from_netcdf(
            NETCDF_FILE
        )
    )

    # -------------------------------------------------
    # 2. Find all 48 map files.
    # -------------------------------------------------

    map_files = load_all_maps()

    # -------------------------------------------------
    # 3. Read all 48 2D maps.
    # -------------------------------------------------

    data = build_data_array(
        map_files,
        lat2d,
        lon2d,
    )

    print("\n==============================================")
    print("DATA ARRAY")
    print("==============================================")

    print(
        "Shape:",
        data.shape,
    )

    print(
        "Expected:",
        "(3, 4, 2, 2, n_lat, n_lon)"
    )

    # -------------------------------------------------
    # 4. Calculate total spatial SS.
    # -------------------------------------------------

    print("\n==============================================")
    print("TOTAL SUM OF SQUARES")
    print("==============================================")

    total_ss = calculate_total_ss(
        data
    )

    # -------------------------------------------------
    # 5. Calculate all 15 ANOVA components.
    # -------------------------------------------------

    (
        components,
        grand_mean,
        valid_count,
        effect_order,
    ) = calculate_spatial_anova(
        data
    )

    # -------------------------------------------------
    # 6. Check decomposition.
    # -------------------------------------------------

    component_ss = np.zeros_like(
        total_ss
    )

    for name in effect_order:

        component_ss += components[
            name
        ]

    valid = (
        np.isfinite(total_ss)
        & (total_ss > 0)
    )

    difference = (
        total_ss
        - component_ss
    )

    max_absolute_error = np.nanmax(
        np.abs(
            difference[valid]
        )
    )

    max_relative_error = np.nanmax(
        np.abs(
            difference[valid]
            / total_ss[valid]
        )
    )

    print("\n==============================================")
    print("SPATIAL SUM OF SQUARES CHECK")
    print("==============================================")

    print(
        "Maximum absolute error:",
        f"{max_absolute_error:.6e}"
    )

    print(
        "Maximum relative error:",
        f"{max_relative_error:.6e}"
    )

    # -------------------------------------------------
    # 7. Percentage contribution maps.
    # -------------------------------------------------

    print("\n==============================================")
    print("ANOVA PERCENTAGES")
    print("==============================================")

    for name in effect_order:

        percentage = (
            components[name]
            / total_ss
            * 100.0
        )

        percentage[
            ~valid
        ] = np.nan

        print(
            f"{name:30s} "
            f"mean={np.nanmean(percentage):8.3f}% "
            f"max={np.nanmax(percentage):8.3f}%"
        )

    # -------------------------------------------------
    # 8. Output directory.
    # -------------------------------------------------

    output_dir = (
        directory
        / "spatial_anova"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -------------------------------------------------
    # 9. Save individual maps.
    # -------------------------------------------------

    for name in effect_order:

        percentage = (
            components[name]
            / total_ss
            * 100.0
        )

        percentage[
            ~valid
        ] = np.nan

        safe_name = (
            name
            .replace(":", "_")
        )

        output_file = (
            output_dir
            / f"anova_{safe_name}_percent.png"
        )

        plot_anova_map(
            lat2d,
            lon2d,
            percentage,
            f"ANOVA contribution: {name}",
            output_file,
            vmax=100,
        )

    # -------------------------------------------------
    # 10. Create the 15-panel grid.
    # -------------------------------------------------

    grid_file = (
        output_dir
        / "fch4_wetl_2005_Jun_ANOVA_grid.png"
    )

    plot_anova_grid(
        lat2d,
        lon2d,
        components,
        total_ss,
        effect_order,
        grid_file,
    )

    print("\n==============================================")
    print("SUCCESS")
    print("==============================================")

    print(
        "Spatial ANOVA complete."
    )

    print(
        "Output directory:",
        output_dir,
    )

    print(
        "Grid:",
        grid_file,
    )
