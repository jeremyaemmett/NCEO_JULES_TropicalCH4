import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.ticker as mticker

TICK_SIZE = 9

fig = plt.figure(figsize=(16, 9.5), constrained_layout=True)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()

fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# ----------------------------
# MAP FEATURES (UNCHANGED)
# ----------------------------
ax.add_feature(cfeature.OCEAN, facecolor='black')
ax.add_feature(cfeature.LAND, facecolor='dimgray')
ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='lightsteelblue')
ax.add_feature(cfeature.BORDERS, linewidth=0.8, edgecolor='beige', alpha=1.0)
ax.add_feature(cfeature.RIVERS, edgecolor='blue', linewidth=0.4)
ax.add_feature(cfeature.LAKES, facecolor='powderblue', linewidth=0.5)

# Equator + Prime Meridian
ax.plot([-180, 180], [0, 0],
        transform=ccrs.PlateCarree(),
        color='orange', linewidth=0.5, alpha=0.8)

ax.plot([0, 0], [-90, 90],
        transform=ccrs.PlateCarree(),
        color='orange', linewidth=0.5, alpha=0.8)

import cartopy.feature as cfeature

admin1 = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none'
)
ax.add_feature(admin1, edgecolor='darkgray', linewidth=0.4, alpha=0.7)
import cartopy.feature as cfeature

admin1 = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none'
)
ax.add_feature(admin1, edgecolor='darkgray', linewidth=0.4, alpha=0.7)

import cartopy.crs as ccrs

# Tropics band (23.4365°N/S approx)
ax.fill_between(
    x=np.linspace(-180, 180, 1000),
    y1=23.4365,
    y2=-23.4365,
    transform=ccrs.PlateCarree(),
    color='dimgray',
    alpha=0.3,
    zorder=0
)

# ----------------------------
# GRIDLINES (FIXED: EXACT 10°)
# ----------------------------
gl = ax.gridlines(
    draw_labels=False,
    linewidth=0.6,
    color='violet',
    linestyle='--',
    alpha=0.7
)

gl.xlocator = mticker.FixedLocator(np.arange(-180, 181, 10))
gl.ylocator = mticker.FixedLocator(np.arange(-90, 91, 10))

# ----------------------------
# BOTTOM AXES (CLEAN 10° + °)
# ----------------------------
xticks = np.arange(-180, 181, 10)
yticks = np.arange(-90, 91, 10)

ax.set_xticks(xticks, crs=ccrs.PlateCarree())
ax.set_yticks(yticks, crs=ccrs.PlateCarree())

ax.set_xticklabels([f"{x}°" for x in xticks],
                   color='lightsteelblue',
                   fontsize=TICK_SIZE)

ax.set_yticklabels([f"{y}°" for y in yticks],
                   color='lightsteelblue',
                   fontsize=TICK_SIZE)

# ----------------------------
# TOP AXIS (0–360°, 10° MATCHED)
# ----------------------------
top = ax.secondary_xaxis('top', functions=(lambda x: x, lambda x: x))

ticks = np.arange(-180, 181, 10)
labels = (ticks + 360) % 360

top.set_xticks(ticks)
top.set_xticklabels([f"{v}°" for v in labels])

top.tick_params(axis='x', colors='lightsteelblue', labelsize=TICK_SIZE)
top.set_xlabel("")

for s in ['bottom', 'left', 'right']:
    top.spines[s].set_visible(False)
top.spines['top'].set_color('white')

import cartopy.io.shapereader as shpreader

shp = shpreader.natural_earth(
    resolution='50m',
    category='cultural',
    name='admin_0_countries'
)

reader = shpreader.Reader(shp)

def rough_area(geom):
    minx, miny, maxx, maxy = geom.bounds
    return (maxx - minx) * (maxy - miny)

AREA_THRESHOLD = 20  # increase to remove more small countries

for rec in reader.records():
    label = rec.attributes.get('ISO_A3', rec.attributes['NAME_LONG'])
    geom = rec.geometry

    #if name == "Antarctica":
    #    continue

    area = rough_area(geom)

    # skip small countries
    if area < AREA_THRESHOLD:
        continue

    point = geom.representative_point()

    ax.text(
        point.x,
        point.y,
        label,
        transform=ccrs.PlateCarree(),
        fontsize=7,
        color='lavender',
        ha='center',
        va='center',
        fontstyle='italic',
        alpha = 0.5
    )

plt.savefig(
    "/Users/jae35/Desktop/world_map.png",
    dpi=300,
    facecolor=fig.get_facecolor(),
    bbox_inches='tight'
)

#plt.show()