import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.colors import TwoSlopeNorm

# ============================================================
# FILES
# ============================================================

ncfile1 = "/Users/jae35/Desktop/qrparm.soil_n96.nc"
ncfile2 = "/Users/jae35/Desktop/qrparm.soil.dust.merge-plus-soil_kaolinitic_oxisols_ultisols_dominant_vn2.nc"

vars1 = [
    "field329","field330","field332","field1381",
    "field336","field333","field335","field342",
    "field1395","field1397","field2011","field1630"
]

vars2 = [
    "sm_wilt","sm_crit","sm_sat","b",
    "hcon","satcon","hcap","sathh",
    "albsoil","soilcarb","soildens","clayfrac"
]

# ============================================================
# OPEN DATASETS
# ============================================================

ds1 = xr.open_dataset(ncfile1, decode_times=False, mask_and_scale=True)
ds2 = xr.open_dataset(ncfile2, decode_times=False, mask_and_scale=True)

# ============================================================
# HELPERS
# ============================================================

def to_2d(da):
    for d in list(da.dims):
        if d.lower() in ["time","t","lev","level","z","height"]:
            da = da.isel({d: 0})
    while da.ndim > 2:
        da = da.isel({da.dims[0]: 0})
    return da


def latlon(da):
    lat = next(d for d in da.dims if "lat" in d.lower())
    lon = next(d for d in da.dims if "lon" in d.lower())
    return lat, lon

# ============================================================
# LAYOUT
# ============================================================

pairs_per_row = 2
ncols = 8
nrows = int(np.ceil(len(vars1) / pairs_per_row))

fig, axes = plt.subplots(
    nrows,
    ncols,
    figsize=(14, 1.6 * nrows),
    subplot_kw={"projection": ccrs.Robinson()},
)

axes = np.atleast_2d(axes)

fig.subplots_adjust(
    left=0.02, right=0.98,
    bottom=0.02, top=0.98,
    wspace=0.01, hspace=0.01
)

# ============================================================
# LOOP
# ============================================================

for i, (v1, v2) in enumerate(zip(vars1, vars2)):

    row = i // pairs_per_row
    base = (i % pairs_per_row) * 4

    da1 = to_2d(ds1[v1])
    da2 = to_2d(ds2[v2])

    lat1, lon1 = latlon(da1)
    lat2, lon2 = latlon(da2)

    lats1 = da1[lat1].values
    lons1 = da1[lon1].values
    lats2 = da2[lat2].values
    lons2 = da2[lon2].values

    # ========================================================
    # TRUE GRID MATCH TEST (THIS IS WHAT YOU ASKED FOR)
    # ========================================================

    lat_match = np.array_equal(lats1, lats2)
    lon_match = np.array_equal(lons1, lons2)
    grid_match = lat_match and lon_match

    # ========================================================
    # OPTIONAL: interpolate only if grids differ
    # ========================================================

    if grid_match:
        da2r = da2
    else:
        da2r = da2.interp({lat2: lats1, lon2: lons1})

    diff = da2r - da1

    # ========================================================
    # STATS
    # ========================================================

    dvals = diff.values[np.isfinite(diff.values)]
    dmax = np.max(np.abs(dvals)) if dvals.size else 1
    if dmax == 0:
        dmax = 1e-12

    norm = TwoSlopeNorm(vmin=-dmax, vcenter=0, vmax=dmax)

    # ========================================================
    # COORDS FOR PLOTTING (ONLY USED FOR MAPS)
    # ========================================================

    Lon, Lat = np.meshgrid(lons1, lats1)

    # ========================================================
    # GRID PANEL (SIMPLE, HONEST)
    # ========================================================

    axg = axes[row, base + 3]
    axg.set_global()
    axg.coastlines(linewidth=0.4)

    if grid_match:
        axg.text(
            0.5, 0.5,
            "GRID MATCH",
            transform=axg.transAxes,
            ha="center", va="center",
            fontsize=10,
            color="green"
        )
    else:
        axg.text(
            0.5, 0.5,
            "GRID MISMATCH",
            transform=axg.transAxes,
            ha="center", va="center",
            fontsize=10,
            color="red"
        )

    axg.set_title("grid comparison", fontsize=8)

    # ========================================================
    # FILE 1
    # ========================================================

    ax1 = axes[row, base]

    m1 = ax1.pcolormesh(
        da1[lon1], da1[lat1], da1.values,
        transform=ccrs.PlateCarree(),
        shading="auto",
        cmap="managua_r"
    )

    ax1.coastlines(linewidth=0.4)
    ax1.set_global()
    ax1.set_title(v1, fontsize=8)
    plt.colorbar(m1, ax=ax1, orientation="horizontal", pad=0.02, shrink=0.8)

    # ========================================================
    # FILE 2
    # ========================================================

    ax2 = axes[row, base + 1]

    m2 = ax2.pcolormesh(
        da1[lon1], da1[lat1], da2r.values,
        transform=ccrs.PlateCarree(),
        shading="auto",
        cmap="managua_r"
    )

    ax2.coastlines(linewidth=0.4)
    ax2.set_global()
    ax2.set_title(v2, fontsize=8)
    plt.colorbar(m2, ax=ax2, orientation="horizontal", pad=0.02, shrink=0.8)

    # ========================================================
    # DIFF
    # ========================================================

    ax3 = axes[row, base + 2]

    m3 = ax3.pcolormesh(
        da1[lon1], da1[lat1], diff.values,
        transform=ccrs.PlateCarree(),
        shading="auto",
        cmap="RdBu_r",
        norm=norm
    )

    ax3.coastlines(linewidth=0.4)
    ax3.set_global()
    ax3.set_title(f"{v2}-{v1}", fontsize=8)
    plt.colorbar(m3, ax=ax3, orientation="horizontal", pad=0.02, shrink=0.8)

# ============================================================
# CLEAN UNUSED AXES
# ============================================================

used = len(vars1) * 4
total = nrows * ncols

for j in range(used, total):
    r = j // ncols
    c = j % ncols
    fig.delaxes(axes[r, c])

ds1.close()
ds2.close()

output_path = "/Users/jae35/Desktop/ancil_comparisons.png"

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)