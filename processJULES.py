import cartopy.crs as ccrs
import numpy as np
import dataOPS


def areal_mean(ax, variable_array, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2): 

    """Compute the area-weighted mean value of a mapped variable within a specified box-shaped region
    Args:
        ax (matplotlib.axes._axes.Axes object): Plot axis
        variable_array (float): Mapped variable array
        variable_unit (string): Physical unit of the mapped variable
        lat2d / lon2d (float): 2D meshgrids of latitude / longitude coordinates
        lats / lons (float): 1D arrays of latitude / longitude coordinates
        lat1 / lat2 (float):  Latitude range minimum / maximum (for averaging)
        lon1 / lon2 (float): Longitude range minimum / maximum (for averaging)
    Returns:
        areal_mean (float): Area-weighted mean
    """

    # Filter the latitudes and longitudes that lie within specified ranges
    lat2d, lon2d = (dataOPS.bounded_coords(lat2d, lon2d, lat1, lat2, lon1, lon2))

    # Get the areas of the filtered latitudes and longitudes
    box_areas = dataOPS.latlon2area(lats, lons, lat2d, lon2d)

    # Compute the areal mean of the sliced variable
    valid_mask = ~np.isnan(variable_array)
    weighted_sum = np.nansum(box_areas[valid_mask] * variable_array[valid_mask])
    total_area = np.nansum(box_areas[valid_mask])
    areal_mean = weighted_sum / total_area if total_area > 0 else np.nan

    ax.plot([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1], transform=ccrs.PlateCarree(), color='black', linewidth=3.0)
    ax.plot([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1], transform=ccrs.PlateCarree(), color='limegreen', linewidth=1.5)

    ax.text(lon1 + 0.5, lat2 + 0.5, dataOPS.cleanup_exponents(str(round(areal_mean, 3)) + variable_unit), fontsize=16, color='white', ha='left', va='bottom', bbox=dict(facecolor='limegreen', edgecolor='none', alpha=0.7, boxstyle='round,pad=0.2'))

    return areal_mean


def zonal_mean(ax, variable_array, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2): 

    zonal_mean = np.nanmean(variable_array, axis=1)
    
    return zonal_mean