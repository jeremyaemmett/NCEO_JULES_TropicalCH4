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
mode = "difference"   # "absolute" or "difference"
view = "flat"         # "flat" or "3d"

all_pos = True

base_path = '/Users/jae35/Desktop/JULES_test_data/JASMIN_output_'
variable = 'fch4_wetl'

_, variable_unit, _, _ = readJULES.read_jules_m2(
    plotPARAMS.data_path + plotPARAMS.file_name,
    variable
)

suites = ['u-dk105_11_n3','u-dk105_3_n3','u-dk105_7_n3']
values = ['Resp.', 'Carb.', 'NPP']

months = ['Mar','Jun','Sep','Dec']


# =========================
# HELPERS
# =========================
def find_files_with_suffix(base_path, suffix):
    return [str(p) for p in Path(base_path).rglob(f"*{suffix}")]


def get_latlon_grid(file_path):
    import readJULES

    header = readJULES.read_jules_header(file_path)
    variable_keys = list(header[1])

    if 'latitude' in variable_keys:
        lat_string, lon_string = 'latitude', 'longitude'
    else:
        lat_string, lon_string = 'lat', 'lon'

    lats, _, _, _ = readJULES.read_jules_m2(file_path, lat_string)
    lons, _, _, _ = readJULES.read_jules_m2(file_path, lon_string)

    lats = lats.flatten()
    lons = lons.flatten()

    lat_u = np.sort(np.unique(lats))
    lon_u = np.sort(np.unique(lons))

    dlat = np.median(np.diff(lat_u))
    dlon = np.median(np.diff(lon_u))

    lat_grid = np.arange(lat_u.min(), lat_u.max() + dlat/2, dlat)
    lon_grid = np.arange(lon_u.min(), lon_u.max() + dlon/2, dlon)

    return np.meshgrid(lat_grid, lon_grid, indexing='ij')


def setup_map(ax, lats, lons):
    lon_min, lon_max = np.min(lons)-1.5, np.max(lons)+1.5
    lat_min, lat_max = np.min(lats)-1.5, np.max(lats)+1.5

    ax.set_extent([lon_min, lon_max, lat_min, lat_max], ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, facecolor="#f5e6c8", alpha=1)
    ax.add_feature(cfeature.BORDERS, linewidth=0.6)
    ax.coastlines()


# =========================
# ALPHA FUNCTION (KEY FIX)
# =========================
def alpha_from_norm(t):
    # t in [0,1]
    return 2.0 * np.abs(t - 0.5)


# =========================
# GRID
# =========================
lat2d, lon2d = get_latlon_grid(plotPARAMS.data_path + plotPARAMS.file_name)


# =========================
# PRELOAD DATA
# =========================
all_data = []

for month in months:

    intgs = []
    for suite in suites:
        path = find_files_with_suffix(
            base_path + suite + '/plots/output/' + variable + '/',
            f'{month}_map.txt'
        )[0]
        intgs.append(np.loadtxt(path))

    intgs = np.stack(intgs)

    if mode == "absolute":
        data = intgs
    else:
        data = intgs[:-1] - intgs[1:]

    all_data.append(data)

all_data = np.concatenate(all_data, axis=0)

abs_max = np.nanmax(np.abs(all_data))
vmin = -abs_max
vmax = abs_max

cmap_name = "seismic"
rgba_cmap = plt.get_cmap(cmap_name)
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)


# =========================
# VIEW: FLAT
# =========================
if view == "flat":

    nrows = len(values) if mode == "absolute" else len(values) - 1
    ncols = len(months)

    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(3.2*ncols, 3*nrows),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )

    axes = np.array(axes)

    for m, month in enumerate(months):

        intgs = []
        for suite in suites:
            path = find_files_with_suffix(
                base_path + suite + '/plots/output/' + variable + '/',
                f'{month}_map.txt'
            )[0]
            intgs.append(np.loadtxt(path))

        intgs = np.stack(intgs)

        if mode == "absolute":
            data = intgs
            titles = [f"Q10 = {v:.1f}" for v in values]
        else:
            data = intgs[:-1] - intgs[1:]
            titles = [
                f"Δ Substrate = {values[i+1]} → {values[i]}"
                for i in range(len(values)-1)
            ]

        for i in range(data.shape[0]):

            ax = axes[i, m]
            ax.set_facecolor("yellow")
            setup_map(ax, lat2d, lon2d)

            t = norm(data[i])

            rgba = rgba_cmap(t)
            rgba[..., -1] = alpha_from_norm(t)

            ax.pcolormesh(
                lon2d, lat2d, rgba,
                shading='auto',
                transform=ccrs.PlateCarree()
            )

            if i == 0:
                ax.set_title(month, fontsize=26, fontstyle='italic')

            # Q10 labels on left
            if m == 0:

                x0 = np.min(lon2d)
                y0 = np.max(lat2d) - 3 + 0.75
                rect_width = 33.0
                rect_height = 2.0

                #rect = plt.matplotlib.patches.FancyBboxPatch(
                #    (x0, y0),
                #    width=rect_width,
                #    height=rect_height,
                #    boxstyle="round,pad=0.6",
                #    alpha=0.8,
                #    facecolor='white',
                #    edgecolor='black',
                #    zorder=20,
                #    linestyle='dashed'
                #)
                #ax.add_patch(rect)

                ##    x0 + 0.3,
                #x.text(
                #    y0 + rect_height / 2,
                #    dataOPS.remove_parenthetical_substrings(titles[i]),
                #    ha='left',
                #    va='center',
                #    fontsize=11,
                #    color='black',
                #    style='italic',
                #    zorder=21
                #)

            ax.add_feature(cfeature.OCEAN, facecolor='powderblue', zorder=10)


    # =========================
    # COLORBAR (FIXED ALPHA)
    # =========================
    cb_ax = fig.add_axes([0.91, 0.2, 0.02, 0.6])

    cb_ax.add_patch(
        plt.Rectangle((0, 0), 1, 1,
                      transform=cb_ax.transAxes,
                      color="#f5e6c8", alpha=1)
    )

    #old = "#f5e6c8"

    N = 256
    t = np.linspace(0, 1, N)

    colors = rgba_cmap(t)
    colors[:, -1] = alpha_from_norm(t)

    alpha_cmap = mcolors.ListedColormap(colors)

    sm = cm.ScalarMappable(cmap=alpha_cmap, norm=norm)
    sm.set_array([])

    cb = plt.colorbar(sm, cax=cb_ax)
    cb.set_label(dataOPS.cleanup_exponents(variable_unit), fontsize=18)
    cb.ax.tick_params(labelsize=16)

    plt.tight_layout(rect=[0, 0, 0.9, 1])
    #plt.show()

    #for ax in fig.axes:
    #    ax.patch.set_alpha(0)  # axes background transparent

    fig.patch.set_alpha(0)  # figure background transparent

    plt.savefig(
        "/Users/jae35/Desktop/JULES_test_data/differences2.png",
        dpi=300,
        transparent=True,
        bbox_inches='tight'
    )


# =========================
# VIEW: 3D
# =========================
elif view == "3d":

    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')

    z_spacing = 1.5

    for m, month in enumerate(months):

        intgs = []
        for suite in suites:
            path = find_files_with_suffix(
                base_path + suite + '/plots/output/' + variable + '/',
                f'{month}_map.txt'
            )[0]
            intgs.append(np.loadtxt(path))

        intgs = np.stack(intgs)

        data = intgs if mode == "absolute" else intgs[:-1] - intgs[1:]

        for i in range(data.shape[0]):

            Z = data[i]
            z = m * z_spacing

            t = norm(Z)

            ax.plot_surface(
                lon2d, lat2d,
                np.full_like(Z, z),
                facecolors=rgba_cmap(t),
                shade=False
            )

    ax.view_init(elev=35, azim=-60)

    ax.set_xlabel("Lon")
    ax.set_ylabel("Lat")
    ax.set_zlabel("Month index")

    plt.tight_layout()
    #plt.show()

    fig.patch.set_alpha(0)  # figure background transparent

    for ax in fig.axes:
        ax.patch.set_alpha(0)  # axes background transparent

    plt.savefig(
        "/Users/jae35/Desktop/JULES_test_data/differences2.png",
        dpi=300,
        transparent=True,
        bbox_inches='tight'
    )

else:
    raise ValueError("view must be 'flat' or '3d'")