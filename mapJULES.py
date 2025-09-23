import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np


def world_map(lats, lons):

    lon_min, lon_max, lat_min, lat_max = np.min(lons)-2.5, np.max(lons)+2.5, np.min(lats)-2.5, np.max(lats)+2.5

    scale = 0.1
    map_width, map_height = lon_max - lon_min, lat_max - lat_min
    fig_width, fig_height = map_width*scale, map_height*scale

    fig = plt.figure(figsize=(fig_width, fig_height))
    #ax = plt.axes(projection=ccrs.Robinson())
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.coastlines()
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='white')
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    #ax.set_global()

    return fig, ax


def overplot_variable(ax, lat2d, lon2d, variable_name, variable_long_name, variable_array, variable_unit, key_labels, cmap):

    c = ax.contourf(lon2d, lat2d, variable_array,
                    levels=20, cmap=cmap, transform=ccrs.PlateCarree())
    cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
    cb.set_label(variable_unit)
    #ax.set_title(variable_name + ': \n' + variable_long_name, fontstyle='italic', fontweight='bold')
    if len(variable_name.split('_')) > 1:
        variable_name_fix = variable_name.split('_')[0] + '\_' + variable_name.split('_')[1]
    else:
        variable_name_fix = variable_name
    subtitle = ''
    for key in key_labels:
        subtitle += key + '  '
    ax.set_title(r"$\bf{" + variable_name_fix + "}$" + '\n' + variable_long_name + '\n' + subtitle)


def latlon2area(lats, lons, latitude, longitude):

    # Determine the spacing of latitude and longitude grid cells (degrees)
    lat_sep, lon_sep = np.diff(lats)[0], np.diff(lons)[0]

    # Compute the bounding latitudes and longitudes of the input coordinate (radians)
    lat1, lat2, lon1, lon2 = latitude - lat_sep, latitude + lat_sep, longitude - lon_sep, longitude + lon_sep
    lat1, lat2, lon1, lon2 = np.deg2rad(lat1), np.deg2rad(lat2), np.deg2rad(lon1), np.deg2rad(lon2)

    # Compute the area of the grid box centered upon the input coordinate (km^2)
    r_earth = 6.378e3  # Radius of Earth (km)
    box_area = (r_earth**2.0) * (np.sin(lat1) - np.sin(lat2)) * (lon1 - lon2)

    return(box_area)


def bounded_coords(lat2d, lon2d, lat1, lat2, lon1, lon2):

    # Ensure correct min/max in case lat1 > lat2 or lon1 > lon2
    lat_min, lat_max = min(lat1, lat2), max(lat1, lat2)
    lon_min, lon_max = min(lon1, lon2), max(lon1, lon2)

    # Build mask for points INSIDE the bounding box
    inside_mask = (
        (lat2d >= lat_min) & (lat2d <= lat_max) &
        (lon2d >= lon_min) & (lon2d <= lon_max)
    )

    # Set values OUTSIDE the bounding box to NaN
    lat2d_masked = np.where(inside_mask, lat2d, np.nan)
    lon2d_masked = np.where(inside_mask, lon2d, np.nan)

    return lat2d_masked, lon2d_masked