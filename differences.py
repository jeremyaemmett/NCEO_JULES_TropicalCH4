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

# Grab unit from original JULES file (just once)
_, variable_unit, _, _ = readJULES.read_jules_m2(
    plotPARAMS.data_path + plotPARAMS.file_name,
    variable
)

suites = ['u-dk105_4_n3','u-dk105_3_n3','u-dk105_2_n3']
values = [4.0, 3.0, 2.0]

#suites = ['u-dk105_7_n3','u-dk105_3_n3','u-dk105_11_n3']
#values = ['NPP', 'Carb.', 'Resp.']

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
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
# GRID
# =========================
lat2d, lon2d = get_latlon_grid(plotPARAMS.data_path + plotPARAMS.file_name)


# =========================
# PRELOAD ALL DATA (for consistent scaling)
# =========================
all_data = []

for month in months:

    intgs = []
    for suite in suites:
        path = find_files_with_suffix(
            base_path + suite + '/plots/output/' + variable + '/',
            f'{month}_map.txt'
        )[0]
        print(path)
        intgs.append(np.loadtxt(path))

    intgs = np.stack(intgs)

    if mode == "absolute":
        data = intgs
    else:
        data = intgs[:-1] - intgs[1:]

    all_data.append(data)

all_data = np.concatenate(all_data, axis=0)

vmin = np.nanmin(all_data)
vmax = np.nanmax(all_data)

if mode == "difference":
    if all_pos:
        vmax = np.nanmax(np.abs(all_data))
        vmin = np.nanmin(np.abs(all_data))
    if not all_pos:
        vmax = np.nanmax(np.abs(all_data))
        vmin = -vmax

cmap_name = "inferno" if mode == "absolute" else "Reds"
rgba_cmap = plt.get_cmap(cmap_name)
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)


# =========================
# VIEW: FLAT (GRID)
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
                f"ΔQ10 = {values[i+1]} → {values[i]}"
                for i in range(len(values)-1)
            ]

        for i in range(data.shape[0]):

            ax = axes[i, m]
            setup_map(ax, lat2d, lon2d)

            rgba = rgba_cmap(norm(data[i]))
            rgba[..., -1] = norm(data[i])  # alpha blending

            ax.pcolormesh(
                lon2d, lat2d, rgba,
                shading='auto',
                transform=ccrs.PlateCarree()
            )

            # month titles
            if i == 0:
                ax.set_title(month, fontsize=26, fontstyle='italic')

            # Q10 labels on left
            if m == 0:

                x0 = np.min(lon2d)
                y0 = np.max(lat2d) - 3 + 0.75
                rect_width = 20.0
                rect_height = 2.0

                #rect = plt.matplotlib.patches.FancyBboxPatch(
                #    (x0, y0),
                #    width=rect_width,
                #    height=rect_height,
                #    boxstyle="round,pad=0.6",
                #    facecolor='white',
                #    edgecolor='black',
                #    alpha=0.8,
                #    zorder=20,
                #    linestyle='dashed'
                #)
                #ax.add_patch(rect)

                #ax.text(
                #    x0 + 0.3,
                #    y0 + rect_height / 2,
                #    ha='left',
                #    dataOPS.remove_parenthetical_substrings(titles[i]),
                #    va='center',
                #    fontsize=11,
                #    color='black',
                #    style='italic',
                #    zorder=21
                #)

            # ocean ON TOP
            ax.add_feature(cfeature.OCEAN, facecolor='powderblue', zorder=10, alpha=1.0)

    # ===== COLORBAR (alpha-aware) =====
    cb_ax = fig.add_axes([0.91, 0.2, 0.02, 0.6])

    cb_ax.add_patch(
        plt.Rectangle((0, 0), 1, 1,
                      transform=cb_ax.transAxes,
                      color="#f5e6c8", alpha=1)
    )

    N = 256
    colors = rgba_cmap(np.linspace(0, 1, N))
    colors[:, -1] = np.linspace(0, 1, N)

    alpha_cmap = mcolors.ListedColormap(colors)
    sm = cm.ScalarMappable(cmap=alpha_cmap, norm=norm)
    sm.set_array([])

    cb = plt.colorbar(sm, cax=cb_ax)
    cb.set_label(dataOPS.cleanup_exponents(variable_unit), fontsize=18)
    cb.ax.tick_params(labelsize=16)

    plt.tight_layout(rect=[0, 0, 0.9, 1])
    #plt.show()

    fig.patch.set_alpha(0)  # figure background transparent

    plt.savefig(
        "/Users/jae35/Desktop/JULES_test_data/differences1.png",
        dpi=300,
        transparent=True,
        bbox_inches='tight'
    )


# =========================
# VIEW: 3D STACKED
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

            ax.plot_surface(
                lon2d, lat2d,
                np.full_like(Z, z),
                facecolors=rgba_cmap(norm(Z)),
                shade=False
            )

    ax.view_init(elev=35, azim=-60)

    ax.set_xlabel("Lon")
    ax.set_ylabel("Lat")
    ax.set_zlabel("Month index")

    plt.tight_layout()
    plt.show()


else:
    raise ValueError("view must be 'flat' or '3d'")