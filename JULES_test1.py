import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import readJULES
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)


def world_map():

    fig = plt.figure(figsize=(9, 4.5))
    ax = plt.axes(projection=ccrs.Robinson())
    ax.coastlines()
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='white')
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    ax.set_global()

    return fig, ax


def overplot_variable(ax, variable_name, variable_long_name, variable_array, variable_unit, key_labels, cmap):

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


def keyval2keylabel(keyname, keyval):

    if keyname == 'month': labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if keyname == 'pool': labels = ['DPM', 'RPM', 'Micro. Bio', 'Humus']
    if keyname == 'layer': labels = ['0-0.1 m', '0.1-0.35 m', '0.35-1.0 m', '1.0-2.0 m']

    key_label = labels[keyval]

    return key_label


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


# JULES output file path/name
root_path = '/Users/jae35/Desktop/JULES_test_data/'
file_name = 'Jv4.5_WFDEI_nti_TRIFFID_gridded_monthly_ch4.2014.nc'

# Variable(s) to visualize, with their dimension keys and values
variable_names = {'fch4_wetl': {'month':6},
                  'cs':        {'month':6, 'pool':1},
                  't_soil':    {'month':6, 'layer':0}}
cmap = 'inferno'

for variable_name in list(variable_names.keys()):

    # Variable to plot, its full array
    variable_array, variable_unit, variable_long_name = readJULES.read_jules_m2(root_path + file_name, variable_name)

    # Coordinates, their full arrays
    lats, lats_units, lats_long_name = readJULES.read_jules_m2(root_path + file_name, 'latitude')
    lons, lons_units, lons_long_name = readJULES.read_jules_m2(root_path + file_name, 'longitude')
    lon2d, lat2d = np.meshgrid(lons, lats)

    # Get the variable's dimension keys and values, for slicing
    variable_dimension_keys = list(variable_names[variable_name].keys())

    # Slice the variable along desired dimensions, i.e., month 3, layer 1, etc.
    key_labels = []
    for var_dim_key in variable_dimension_keys:
        slice_index = variable_names[variable_name][var_dim_key]
        variable_array = variable_array[slice_index]
        key_labels.append(keyval2keylabel(var_dim_key, slice_index))  # Labels describing the slices, for plotting

    # Make an empty world map
    fig, ax = world_map()

    # Overlay the sliced variable with contours
    overplot_variable(ax, variable_name, variable_long_name, variable_array, variable_unit, key_labels, cmap)

    lat1, lat2, lon1, lon2 = -10, 15, -15, 50

    # Filter the latitudes and longitudes that lie within specified ranges
    lat2d, lon2d = (bounded_coords(lat2d, lon2d, lat1, lat2, lon1, lon2))

    ax.plot([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1], transform=ccrs.PlateCarree(), color='black', linewidth=3.0)
    ax.plot([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1], transform=ccrs.PlateCarree(), color='limegreen', linewidth=1.5)

    # Get the areas of the filtered latitudes and longitudes
    box_areas = latlon2area(lats, lons, lat2d, lon2d)

    # Compute the areal mean of the sliced variable
    valid_mask = ~np.isnan(variable_array)
    weighted_sum = np.nansum(box_areas[valid_mask] * variable_array[valid_mask])
    total_area = np.nansum(box_areas[valid_mask])
    areal_mean = weighted_sum / total_area if total_area > 0 else np.nan

    print('test: ', areal_mean)

plt.show()
