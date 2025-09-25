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

    ax.text(lon1+2.5, lat1+2.5, str(round(areal_mean, 3)) + '\n' + variable_unit, fontsize=11, color='black', ha='left', va='bottom', bbox=dict(facecolor='limegreen', edgecolor='none', alpha=0.3, boxstyle='round,pad=0.2'))

    return areal_mean


def keyval2keylabel(keyname, keyval):

    if keyname == 'time': labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if keyname == 'pool': labels = ['DPM', 'RPM', 'Micro. Bio', 'Humus']
    if keyname == 'soil': labels = ['0-0.1 m', '0.1-0.35 m', '0.35-1.0 m', '1.0-2.0 m']
    if keyname == 'pft':  labels = ['pft1', 'pft2', 'pft3', 'pft4', 'pft5', 'pft6', 'pft7', 'pft8', 'pft9', 'pft10', 'pft11', 'pft12', 'pft13']

    key_label = labels[keyval]

    return key_label