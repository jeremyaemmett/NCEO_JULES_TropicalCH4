import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import miscOPS


def world_map(lats, lons):

    """Create a world map, given latitude and longitude coordinates
    Args:
        lats (float): 1D array of latitude coordinates
        lons (float): 1D array of longitude coordinates
    Returns:
        fig (matplotlib.figure.Figure object): A matplotlib figure
        ax (matplotlib.axes._axes.Axes object): A matplotlib axis
    """

    # Add some extra space to the map edges
    lon_min, lon_max, lat_min, lat_max = np.min(lons)-2.5, np.max(lons)+2.5, np.min(lats)-2.5, np.max(lats)+2.5

    # Figure size
    scale = 0.1
    map_width, map_height = lon_max - lon_min, lat_max - lat_min
    fig_width, fig_height = map_width*scale, map_height*scale
    fig = plt.figure(figsize=(fig_width, fig_height))

    # Projection
    ax = plt.axes(projection=ccrs.PlateCarree())  # Use Robinson() for full-globe
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

    # Topography, details
    ax.coastlines()
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='white')
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False

    return fig, ax


def overplot_variable(ax, lat2d, lon2d, variable_name, variable_long_name, variable_array, variable_unit, key_labels, cmap, variable_global_min, variable_global_max):

    """Overplot, onto an empty map, filled contours and a colorbar to display a mapped variable
    Args:
        ax (matplotlib.axes._axes.Axes object): Plot axis
        lat2d / lon2d (float): 2D meshgrids of latitude / longitude coordinates
        variable_name / variable_long_name (string): Short name / Long name of the mapped variable
        variable_array (float): Mapped variable array
        variable_unit (string): Physical unit of the mapped variable
        key_labels (_type_): Descriptive labels for the mapped variable's dimensions
        cmap (matplotlib.colors.Colormap object): Colormap name
        variable_global_min / variable_global_max (float): Fixed minimum / maximum contour levels for the mapped variable
    """

    c = ax.contourf(lon2d, lat2d, variable_array,
                    levels=np.linspace(variable_global_min, variable_global_max, 20), cmap=cmap, transform=ccrs.PlateCarree())
    cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
    cb.set_label(variable_unit, fontsize=12)
    cb.ax.tick_params(labelsize=12)

    variable_name_fix = variable_name.split('_')[0] + '\_' + variable_name.split('_')[1] if len(variable_name.split('_')) > 1 else variable_name

    subtitle = ''
    for key in key_labels: subtitle += key + '  '
    
    ax.set_title(miscOPS.remove_parenthetical_substrings(r"$\bf{" + variable_name_fix + "}$" + '\n' + variable_long_name), loc='left', fontsize=14)
    ax.text(np.min(lon2d)-1, np.min(lat2d)-1, miscOPS.remove_parenthetical_substrings(subtitle), fontsize=14, color='black', ha='left', va='bottom', style='italic')


def latlon2area(lats, lons, latitude, longitude):

    """_summary_
    Args:
        lats / lons (float): 1D arrays of latitude / longitude coordinates
        latitude / longitude (float): latitude / longitude where area is desired
    Returns:
        box_area (float): Surface area of the gridbox centered on latitude / longitude
    """

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

    """Mask mesh-gridded latitudes and longitudes to flag those lying within a specified box-shaped region
    Args:
        lat2d / lon2d (float): 2D meshgrids of latitude / longitude coordinates
        lat1 / lat2 (float):  Latitude range minimum / maximum (for averaging)
        lon1 / lon2 (float): Longitude range minimum / maximum (for averaging)
    Returns:
        lat2d_masked / lon2d_masked (boolean): Arrays flagging which meshgridded latitudes,
            and which meshgridded longitudes, lie within a specified box-shaped region
    """

    # Ensure correct min/max in case lat1 > lat2 or lon1 > lon2
    lat_min, lat_max = min(lat1, lat2), max(lat1, lat2)
    lon_min, lon_max = min(lon1, lon2), max(lon1, lon2)

    # Build mask for points inside the bounding box
    inside_mask = ((lat2d >= lat_min) & (lat2d <= lat_max) &
                   (lon2d >= lon_min) & (lon2d <= lon_max))

    # Set values OUTSIDE the bounding box to NaN
    lat2d_masked = np.where(inside_mask, lat2d, np.nan)
    lon2d_masked = np.where(inside_mask, lon2d, np.nan)

    return lat2d_masked, lon2d_masked