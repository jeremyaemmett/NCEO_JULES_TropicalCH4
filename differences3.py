from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import dataOPS
import plotPARAMS
import readJULES


# =========================
# CONFIG
# =========================
mode = "difference"
base_path = "/Users/jae35/Desktop/JULES_test_data/JASMIN_output_"
variable = "fch4_wetl"

suites = ["u-dk105_3_n6", "u-dk105_2_n6"]
months = ["Mar", "Jun", "Sep", "Dec"]


# =========================
# UNIT
# =========================
_, variable_unit, _, _ = readJULES.read_jules_m2(
    plotPARAMS.data_path + plotPARAMS.file_name,
    variable
)


# =========================
# HELPERS
# =========================
def find_file(base, suffix):
    return [str(p) for p in Path(base).rglob(f"*{suffix}")][0]


def get_latlon(file_path):
    header = readJULES.read_jules_header(file_path)
    keys = list(header[1])

    lat_k = "latitude" if "latitude" in keys else "lat"
    lon_k = "longitude" if "longitude" in keys else "lon"

    lats, _, _, _ = readJULES.read_jules_m2(file_path, lat_k)
    lons, _, _, _ = readJULES.read_jules_m2(file_path, lon_k)

    lats = lats.flatten()
    lons = lons.flatten()

    lat_u = np.sort(np.unique(lats))
    lon_u = np.sort(np.unique(lons))

    dlat = np.median(np.diff(lat_u))
    dlon = np.median(np.diff(lon_u))

    lat_grid = np.arange(lat_u.min(), lat_u.max() + dlat/2, dlat)
    lon_grid = np.arange(lon_u.min(), lon_u.max() + dlon/2, dlon)

    return np.meshgrid(lat_grid, lon_grid, indexing="ij")


# =========================
# GRID
# =========================
lat2d, lon2d = get_latlon(
    plotPARAMS.data_path + plotPARAMS.file_name
)


# =========================
# COLOR SCALE
# =========================
all_data = []

for month in months:
    stack = []
    for suite in suites:
        path = find_file(
            base_path + suite + "/plots/output/" + variable + "/",
            f"{month}_map.txt"
        )
        stack.append(np.loadtxt(path))

    stack = np.stack(stack)
    data = stack if mode == "absolute" else stack[:-1] - stack[1:]
    all_data.append(data)

all_data = np.concatenate(all_data, axis=0)

abs_max = np.nanmax(np.abs(all_data))
norm = mcolors.Normalize(-abs_max, abs_max)
cmap = plt.get_cmap("seismic")


# =========================
# PLOT (CORRECT CARTOPY LAYER ORDER)
# =========================
fig, axes = plt.subplots(
    2, 2,
    figsize=(8, 3),
    subplot_kw={"projection": ccrs.Mollweide(central_longitude=25)},
    squeeze=False
)

for m, month in enumerate(months):

    stack = []
    for suite in suites:
        path = find_file(
            base_path + suite + "/plots/output/" + variable + "/",
            f"{month}_map.txt"
        )
        stack.append(np.loadtxt(path))

    stack = np.stack(stack)
    data = stack if mode == "absolute" else stack[:-1] - stack[1:]
    field = data.mean(axis=0)

    ax = axes[m // 2, m % 2]
    ax.set_title(month)

    # =========================================================
    # CRITICAL FIX: BACKGROUND MODEL (NO CARTOPY OCEAN FEATURE)
    # =========================================================
    ax.set_facecolor("#a6cbe3")  # ocean base (clean, no artifacts)

    ax.add_feature(
        cfeature.LAND,
        facecolor="#f5e6c8",
        edgecolor="none",
        zorder=1
    )

    # coastlines ONLY as outline (prevents halo interaction)
    ax.coastlines(
        linewidth=0.6,
        zorder=3
    )

    # =========================================================
    # DATA (SINGLE PASS, NO ALPHA, NO STACKING ARTIFACTS)
    # =========================================================
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

    ax.add_feature(
        cfeature.OCEAN,
        facecolor="#a6cbe3",
        edgecolor="none",
        zorder=4
    )


# =========================
# COLORBAR (BEIGE UI STYLE RESTORED)
# =========================
cb_ax = fig.add_axes([0.92, 0.2, 0.02, 0.6])
cb_ax.set_facecolor("#f5e6c8")

sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

cb = plt.colorbar(sm, cax=cb_ax)
cb.set_label(dataOPS.cleanup_exponents(variable_unit))

plt.tight_layout(rect=[0, 0, 0.9, 1])

#fig.patch.set_alpha(0)
fig.patch.set_facecolor("white")

plt.savefig(
    "/Users/jae35/Desktop/JULES_test_data/differences3.png",
    dpi=300,
    bbox_inches="tight"
)