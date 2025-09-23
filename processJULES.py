import cartopy.crs as ccrs
import numpy as np
import mapJULES

def areal_mean(ax, variable_array, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2): 

    # Filter the latitudes and longitudes that lie within specified ranges
    lat2d, lon2d = (mapJULES.bounded_coords(lat2d, lon2d, lat1, lat2, lon1, lon2))

    # Get the areas of the filtered latitudes and longitudes
    box_areas = mapJULES.latlon2area(lats, lons, lat2d, lon2d)

    # Compute the areal mean of the sliced variable
    valid_mask = ~np.isnan(variable_array)
    weighted_sum = np.nansum(box_areas[valid_mask] * variable_array[valid_mask])
    total_area = np.nansum(box_areas[valid_mask])
    areal_mean = weighted_sum / total_area if total_area > 0 else np.nan

    ax.plot([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1], transform=ccrs.PlateCarree(), color='black', linewidth=3.0)
    ax.plot([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1], transform=ccrs.PlateCarree(), color='limegreen', linewidth=1.5)

    ax.text(lon1+2.5, lat1+2.5, 'mean\n'+str(round(areal_mean, 2)) + ' ' + variable_unit, fontsize=9, color='black', ha='left', va='bottom', bbox=dict(facecolor='limegreen', edgecolor='none', alpha=0.2, boxstyle='round,pad=0.1'))

    return areal_mean