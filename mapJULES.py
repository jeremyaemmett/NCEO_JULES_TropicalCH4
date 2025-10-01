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
    #fig = plt.figure(figsize=(8, 4))
    #fig.tight_layout(pad=0)

    lat_range = lat_max - lat_min
    lon_range = lon_max - lon_min
    aspect_ratio = lat_range / lon_range  # Height / Width

    # Use a fixed width and compute matching height
    fig_width = 10
    fig_height = fig_width * aspect_ratio

    fig = plt.figure(figsize=(fig_width, fig_height))

    fig.set_constrained_layout(True)

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

    vmin, vmax = variable_global_min, variable_global_max
    n_levels = 10

    step_raw = (vmax - vmin) / (n_levels - 1)
    mag = 10 ** np.floor(np.log10(step_raw))
    step = mag * (1 if step_raw/mag <= 1 else 2 if step_raw/mag <= 2 else 5)

    vmin_r = np.floor(vmin / step) * step
    vmax_r = np.ceil(vmax / step) * step

    levels = np.arange(vmin_r, vmax_r + step/2, step)

    c = ax.contourf(lon2d, lat2d, variable_array,
                    levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
    cb.set_label(miscOPS.cleanup_exponents(variable_unit), fontsize=12)
    cb.ax.tick_params(labelsize=12)

    variable_name_fix = variable_name.split('_')[0] + '\_' + variable_name.split('_')[1] if len(variable_name.split('_')) > 1 else variable_name

    subtitle = ''
    for key in key_labels: subtitle += key + '  '
    
    ax.set_title(miscOPS.remove_parenthetical_substrings(r"$\bf{" + variable_name_fix + "}$" + '\n' + variable_long_name), loc='left', fontsize=14)
    ax.text(np.min(lon2d)-1, np.min(lat2d)-1, miscOPS.remove_parenthetical_substrings(subtitle), fontsize=14, color='black', ha='left', va='bottom', style='italic')