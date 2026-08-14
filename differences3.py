from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import dataOPS
import readJULES


# =========================================================
# CONFIG
# =========================================================

mode = "difference"

base_path = Path(
    "/Users/jae35/Desktop/JULES_test_data/ID_suites"
)

variable = "fch4_wetl"

suites = [
    "u-dk105_000",
    "u-dk105_010",
]

months = [
    "Mar",
    "Jun",
    "Sep",
    "Dec",
]


# =========================================================
# HELPERS
# =========================================================

def find_file(base, suffix):
    """
    Find the first file below 'base' ending with 'suffix'.
    """
    base = Path(base)

    matches = list(base.rglob(f"*{suffix}"))

    if not matches:
        raise FileNotFoundError(
            f"\nNo file matching '*{suffix}' found under:\n{base}\n"
        )

    return matches[0]


def find_netcdf(base):
    """
    Find a NetCDF file below 'base'.

    This is used for reading the variable units and
    latitude/longitude with readJULES/xarray.
    """
    base = Path(base)

    extensions = [
        "*.nc",
        "*.nc4",
        "*.netcdf",
    ]

    matches = []

    for pattern in extensions:
        matches.extend(base.rglob(pattern))

    if not matches:
        raise FileNotFoundError(
            "\nNo NetCDF file was found under:\n"
            f"{base}\n\n"
            "A NetCDF/JULES file is needed for reading the "
            "variable unit and latitude/longitude."
        )

    # Remove duplicates and sort for reproducibility
    matches = sorted(set(matches))

    print("\nNetCDF files found:")

    for f in matches:
        print(f"  {f}")

    print(f"\nUsing NetCDF reference file:\n  {matches[0]}\n")

    return matches[0]


def get_latlon(file_path):
    """
    Read latitude and longitude from a JULES NetCDF file
    and construct regular 2D latitude/longitude grids.
    """

    file_path = str(file_path)

    header = readJULES.read_jules_header(file_path)
    keys = list(header[1])

    lat_k = "latitude" if "latitude" in keys else "lat"
    lon_k = "longitude" if "longitude" in keys else "lon"

    lats, _, _, _ = readJULES.read_jules_m2(
        file_path,
        lat_k
    )

    lons, _, _, _ = readJULES.read_jules_m2(
        file_path,
        lon_k
    )

    lats = lats.flatten()
    lons = lons.flatten()

    lat_u = np.sort(np.unique(lats))
    lon_u = np.sort(np.unique(lons))

    dlat = np.median(np.diff(lat_u))
    dlon = np.median(np.diff(lon_u))

    lat_grid = np.arange(
        lat_u.min(),
        lat_u.max() + dlat / 2,
        dlat
    )

    lon_grid = np.arange(
        lon_u.min(),
        lon_u.max() + dlon / 2,
        dlon
    )

    return np.meshgrid(
        lat_grid,
        lon_grid,
        indexing="ij"
    )


def get_map_file(suite, month):
    """
    Return the *_map.txt file for a given suite and month.
    """

    directory = (
        base_path
        / suite
        / "plots"
        / "output"
        / variable
    )

    return find_file(
        directory,
        f"{month}_map.txt"
    )


# =========================================================
# REFERENCE NETCDF FILE
# =========================================================
#
# IMPORTANT:
# The *_map.txt files contain the plotted data.
#
# readJULES.read_jules_m2() expects a NetCDF/JULES file,
# so we use a separate .nc file for:
#
#   1. variable unit
#   2. latitude
#   3. longitude
#
# =========================================================

reference_directory = (
    base_path / suites[0]
)

reference_file = find_netcdf(
    reference_directory
)


# =========================================================
# UNIT
# =========================================================

_, variable_unit, _, _ = readJULES.read_jules_m2(
    str(reference_file),
    variable
)

print(f"Variable : {variable}")
print(f"Unit     : {variable_unit}")


# =========================================================
# GRID
# =========================================================

lat2d, lon2d = get_latlon(
    reference_file
)


# =========================================================
# READ ALL DATA
# =========================================================

all_data = []

for month in months:

    stack = []

    for suite in suites:

        path = get_map_file(
            suite,
            month
        )

        print(
            f"Reading {month} / {suite}: {path}"
        )

        stack.append(
            np.loadtxt(path)
        )

    stack = np.stack(stack)

    if mode == "absolute":

        data = stack

    elif mode == "difference":

        # Suite 1 minus Suite 2
        data = stack[0] - stack[1]

    else:

        raise ValueError(
            f"Unknown mode: {mode!r}. "
            "Use 'absolute' or 'difference'."
        )

    all_data.append(data)


# =========================================================
# COLOR SCALE
# =========================================================

all_data = np.concatenate(
    [
        np.atleast_3d(data)
        for data in all_data
    ],
    axis=0
)

abs_max = np.nanmax(
    np.abs(all_data)
)

norm = mcolors.Normalize(
    vmin=-abs_max,
    vmax=abs_max
)

cmap = plt.get_cmap(
    "seismic"
)


# =========================================================
# PLOT
# =========================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(8, 3),
    subplot_kw={
        "projection": ccrs.Mollweide(
            central_longitude=25
        )
    },
    squeeze=False
)


for m, month in enumerate(months):

    # -----------------------------------------------------
    # Read the two suite files
    # -----------------------------------------------------

    stack = []

    for suite in suites:

        path = get_map_file(
            suite,
            month
        )

        stack.append(
            np.loadtxt(path)
        )

    stack = np.stack(stack)

    # -----------------------------------------------------
    # Calculate field
    # -----------------------------------------------------

    if mode == "absolute":

        field = stack.mean(axis=0)

    elif mode == "difference":

        # Suite 1 - Suite 2
        field = stack[0] - stack[1]

    # -----------------------------------------------------
    # Select subplot
    # -----------------------------------------------------

    ax = axes[
        m // 2,
        m % 2
    ]

    ax.set_title(
        month
    )

    # =====================================================
    # BACKGROUND
    # =====================================================

    # Ocean base
    ax.set_facecolor(
        "#a6cbe3"
    )

    # Land
    ax.add_feature(
        cfeature.LAND,
        facecolor="#f5e6c8",
        edgecolor="none",
        zorder=1
    )

    # Coastline outline
    ax.coastlines(
        linewidth=0.6,
        zorder=3
    )

    # =====================================================
    # DATA
    # =====================================================

    ax.pcolormesh(
        lon2d,
        lat2d,
        field,
        cmap=cmap,
        norm=norm,
        shading="auto",
        transform=ccrs.PlateCarree(),
        linewidth=0,
        edgecolors="none",
        antialiased=False,
        zorder=2
    )

    # =====================================================
    # OCEAN
    # =====================================================

    ax.add_feature(
        cfeature.OCEAN,
        facecolor="#a6cbe3",
        edgecolor="none",
        zorder=4
    )


# =========================================================
# COLORBAR
# =========================================================

cb_ax = fig.add_axes(
    [
        0.92,
        0.2,
        0.02,
        0.6
    ]
)

cb_ax.set_facecolor(
    "#f5e6c8"
)

sm = cm.ScalarMappable(
    cmap=cmap,
    norm=norm
)

sm.set_array([])

cb = plt.colorbar(
    sm,
    cax=cb_ax
)

cb.set_label(
    dataOPS.cleanup_exponents(
        variable_unit
    )
)


# =========================================================
# LAYOUT
# =========================================================

plt.tight_layout(
    rect=[
        0,
        0,
        0.9,
        1
    ]
)

fig.patch.set_facecolor(
    "white"
)


# =========================================================
# SAVE
# =========================================================

output_file = (
    Path(
        "/Users/jae35/Desktop/JULES_test_data"
    )
    / "differences3_new.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

print(
    f"\nSaved figure to:\n{output_file}\n"
)

plt.show()

