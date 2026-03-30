import xarray as xr
import numpy as np
import plotPARAMS
import readJULES
import os


def generate_indices(shape):

    """Given an array shape, generate a list of tuples representing all possible
       combinations of slices through the array.
    Args:
        shape (_type_): Array shape, as a list e.g. [np.int64(12), np.int64(4)]
    Returns:
        list: List of tuples representing slice combinations e.g. [(0, 0), (0, 1), (0, 2), (0, 3), ... (11, 3)]
    """

    if not shape:
        return [()]
    
    rest = generate_indices(shape[1:])

    return [(i,) + r for i in range(shape[0]) for r in rest]


def keyval2keylabel(keyname, keyval):

    """Given a variable key, convert a dimension on the axis to a descriptive string.
    Args:
        keyname (string): Variable key e.g. 'time'
        keyval (integer): Dimension along the key axis e.g. 2
    Returns:
        key_label (string): A readable/plot-able string e.g. 'Mar'
    """

    if keyname == 'time': labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if keyname == 'pool': labels = ['DPM', 'RPM', 'Micro. Bio', 'Humus']
    if keyname == 'soil': labels = ['0-0.1 m', '0.1-0.35 m', '0.35-1.0 m', '1.0-2.0 m']
    if keyname == 'pft':  labels = ['BET-Tr', 'BET-Te', 'BDT', 'NET', 'NDT', 'C3G', 'C4G', 'ESh', 'DSh', 'C3Cr', 'C4Cr', 'C3Pa', 'C4Pa']

    #print('key stuff: ', keyval, keyname)
    key_label = labels[keyval]

    return key_label


def globalMinMax(variable_array, variable_unit):

    """_summary_
    Args:
        variable_array (_type_): _description_
        variable_unit (_type_): _description_
    Returns:
        _type_: _description_
    """

    variable_global_min = np.nanmin(variable_array) if variable_unit != '1' else 0.0
    variable_global_max = np.nanmax(variable_array) if variable_unit != '1' else 5.0

    variable_global_min, variable_global_max = np.nanmin(variable_array), np.nanmax(variable_array)

    if variable_global_min == 0.0 and variable_global_max == 0.0:
        variable_global_min, variable_global_max = 0.0, 1.0

    if variable_global_min == 1.0 and variable_global_max == 1.0:
        variable_global_min, variable_global_max = 0.0, 1.0

    return variable_global_min, variable_global_max


def sanitize_extreme_values(arr, min_valid=-1e10, max_valid=1e10):
    """
    Replaces extreme values in any N-dimensional NumPy array with NaN,
    while preserving the original shape.

    NaNs already in the array are untouched.
    """
    # Create a copy to avoid modifying original array
    arr_clean = np.array(arr, dtype='float64')  # force float to support NaNs

    mask = (arr_clean < min_valid) | (arr_clean > max_valid)
    arr_clean[mask] = np.nan

    return arr_clean


def filter_strings_by_substrings(input_list, substring_list):
        
        return [
        string for string in input_list
        if any(sub in string for sub in substring_list)]


def get_month_index(filename):
    month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    for month in month_map:
        if month in filename:
            return month_map[month]
    return 0  # Unknown months go first


def cleanup_exponents(text):

    superscript_map = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '-': '⁻', '+': '⁺'
    }

    def replace_exp(match):
        base, exp = match.group(1), match.group(2)
        # Convert each character in exp to superscript if possible
        sup_exp = ''.join(superscript_map.get(ch, ch) for ch in exp)
        return base + sup_exp

    import re
    # Replace 10^number pattern
    text = re.sub(r'(10)\^([-\d]+)', replace_exp, text)
    # Replace letter-number negative powers like m-2, s-3 etc.
    text = re.sub(r'([a-zA-Z])([-\d]+)', replace_exp, text)

    return text


def latlon2area(lats, lons, latitude, longitude):
    """
    Compute the surface area of a gridbox centered on a given latitude/longitude.

    Args:
        lats / lons (1D or 2D arrays): latitude and longitude arrays
        latitude / longitude (float or 2D array): location(s) where area is desired

    Returns:
        box_area (float or array): Surface area of the gridbox (same shape as latitude/longitude)
    """
    import numpy as np

    # Ensure lats/lons spacing is scalar
    #if np.ndim(lats) > 1:
    #    lat_sep = np.mean(np.diff(lats, axis=0))
    #else:
    #    lat_sep = np.diff(lats)[0]

    #if np.ndim(lons) > 1:
    #    lon_sep = np.mean(np.diff(lons, axis=1))
    #else:
    #    lon_sep = np.diff(lons)[0]

    lat_sep = get_spacing(lats, 0.25)
    lon_sep = get_spacing(lons, 0.25)

    # Compute grid edges
    lat1 = np.clip(latitude - lat_sep / 2, -90, 90)
    lat2 = np.clip(latitude + lat_sep / 2, -90, 90)
    lon1 = longitude - lon_sep / 2
    lon2 = longitude + lon_sep / 2

    # Convert to radians
    lat1 = np.deg2rad(lat1)
    lat2 = np.deg2rad(lat2)
    lon1 = np.deg2rad(lon1)
    lon2 = np.deg2rad(lon2)

    # Earth radius in meters
    r_earth = 6.378e6

    # Area formula
    box_area = (r_earth ** 2) * (np.sin(lat2) - np.sin(lat1)) * (lon2 - lon1)

    return box_area


def latlon2area2(latitude, longitude):
    """
    Compute the surface area of a gridbox centered on a given latitude/longitude.

    Args:
        lats / lons (1D or 2D arrays): latitude and longitude arrays
        latitude / longitude (float or 2D array): location(s) where area is desired

    Returns:
        box_area (float or array): Surface area of the gridbox (same shape as latitude/longitude)
    """
    import numpy as np

    # Ensure lats/lons spacing is scalar
    #if np.ndim(lats) > 1:
    #    lat_sep = np.mean(np.diff(lats, axis=0))
    #else:
    #    lat_sep = np.diff(lats)[0]

    #if np.ndim(lons) > 1:
    #    lon_sep = np.mean(np.diff(lons, axis=1))
    #else:
    #    lon_sep = np.diff(lons)[0]

    lat_sep = get_spacing(latitude[:, 0], 0.25)
    lon_sep = get_spacing(longitude[0, :], 0.25)

    # Compute grid edges
    lat1 = np.clip(latitude - lat_sep / 2, -90, 90)
    lat2 = np.clip(latitude + lat_sep / 2, -90, 90)
    lon1 = longitude - lon_sep / 2
    lon2 = longitude + lon_sep / 2

    # Convert to radians
    lat1 = np.deg2rad(lat1)
    lat2 = np.deg2rad(lat2)
    lon1 = np.deg2rad(lon1)
    lon2 = np.deg2rad(lon2)

    # Earth radius in meters
    r_earth = 6.378e6

    # Area formula
    box_area = (r_earth ** 2) * (np.sin(lat2) - np.sin(lat1)) * (lon2 - lon1)

    return box_area


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


def remove_parenthetical_substrings(string_with_parentheses):

    """Remove all closed parentheses, and anything enclosed by them, from a string.
    Args:
        string_with_parentheses (_type_): A string containing closed parentheses e.g. '(1)one(2)two'
    Returns:
        string: The same string with parentheses and enclosed substrings removed e.g. 'onetwo'
    """
    
    r, skip = [], 0
    for c in string_with_parentheses:
        if c=='(': skip+=1; r.append(' ') if skip==1 else None
        elif c==')' and skip>0: skip-=1
        elif skip==0: r.append(c)

    return ''.join(r)


def check_if_rate(unit_string):

    substrings = ['s-1', 'm-1', 'y-1']

    is_a_rate = any(sub in unit_string for sub in substrings)

    return(is_a_rate)


import numpy as np
import cftime

def ensure_np_datetime(times):
    """
    Convert a list/array of cftime objects to np.datetime64 only if needed.
    If times are already datetime64 or datetime objects, return unchanged.
    """
    # Check the first element to detect cftime type
    if len(times) == 0:
        return np.array(times)  # empty array, nothing to do

    first_elem = times[0]

    if isinstance(first_elem, (cftime.DatetimeNoLeap,
                               cftime.DatetimeGregorian,
                               cftime.Datetime360Day,
                               cftime.DatetimeProlepticGregorian)):
        # Convert all cftime objects to np.datetime64
        return np.array([np.datetime64(f"{t.year}-{t.month:02d}-{t.day:02d}") for t in times])
    else:
        # Already a datetime-like array
        return np.array(times)
    

def get_spacing(arr, default_spacing):
    arr = np.asarray(arr)
    
    if arr.ndim == 1:
        # 1D array → take diff along the only axis if possible
        if arr.size > 1:
            return np.mean(np.diff(arr))
        else:
            return default_spacing
    
    elif arr.ndim == 2:
        # 2D array → take diff along the non-singleton axis
        if arr.shape[0] > 1:
            return np.mean(np.diff(arr, axis=0))
        elif arr.shape[1] > 1:
            return np.mean(np.diff(arr, axis=1))
        else:
            return default_spacing
    
    else:
        # Higher dims? just fallback to default
        return default_spacing
    

def serial2rect():
    # Read time
    times, times_unit, times_long_name, times_dims = readJULES.read_jules_m2(
        plotPARAMS.data_path + plotPARAMS.file_name, 'time')

    # Convert to comparable values (assume times are datetime64-like or comparable)
    year_indices = [i for i, t in enumerate(times)
                    if f"{plotPARAMS.year}-01-01" <= str(t) < f"{plotPARAMS.year + 1}-01-01"]

    # Read header
    header = readJULES.read_jules_header(plotPARAMS.data_path + plotPARAMS.file_name)
    dimension_keys, variable_keys = list(header[0]), list(header[1])

    # Determine lat/lon variable names
    if 'latitude' in variable_keys and 'longitude' in variable_keys:
        lat_string, lon_string = 'latitude', 'longitude'
    elif 'lat' in variable_keys and 'lon' in variable_keys:
        lat_string, lon_string = 'lat', 'lon'
    else:
        raise ValueError("Cannot find latitude and longitude variables.")

    # Determine lat/lon dimension keys
    if 'lat' in dimension_keys and 'lon' in dimension_keys:
        lat_key, lon_key = 'lat', 'lon'
    elif 'y' in dimension_keys and 'x' in dimension_keys:
        lat_key, lon_key = 'y', 'x'
    else:
        raise ValueError("Cannot find latitude and longitude dimensions.")

    # Read lat/lon arrays
    lats, lats_units, lats_long_name, lats_dims = readJULES.read_jules_m2(
        plotPARAMS.data_path + plotPARAMS.file_name, lat_string)
    lons, lons_units, lons_long_name, lons_dims = readJULES.read_jules_m2(
        plotPARAMS.data_path + plotPARAMS.file_name, lon_string)

    # Check if serialized
    serialized = len(lats) != 0 and (len(lats_dims) == 1 or 1 in [len(lats) if hasattr(lats, '__len__') else 0])

    if not serialized:
        print("Data already on a grid")
        return

    # Determine unique lat/lon values
    lat_unique = sorted(list(set([float(x) for x in lats])))
    lon_unique = sorted(list(set([float(x) for x in lons])))

    ny, nx = len(lat_unique), len(lon_unique)

    # Prepare grid dictionary
    rect_data = {}

    for var in variable_keys:
        data, units, long_name, dims = readJULES.read_jules_m2(
            plotPARAMS.data_path + plotPARAMS.file_name, var)

        # Subset time if exists
        if 'time' in dims:
            time_idx = dims.index('time')
            data = [[row[i] for i in year_indices] if isinstance(row[0], list) else [row[i] for i in year_indices] for row in data]

        # Initialize grid with NaNs
        grid_shape = (len(year_indices), ny, nx) if 'time' in dims else (ny, nx)
        grid = [[[float('nan')]*nx for _ in range(ny)] for _ in range(len(year_indices))] if 'time' in dims else [[float('nan')]*nx for _ in range(ny)]

        # Map serialized points to grid
        lat_inds = [lat_unique.index(float(lat)) for lat in lats]
        lon_inds = [lon_unique.index(float(lon)) for lon in lons]

        if 'time' in dims:
            for t_idx, t in enumerate(year_indices):
                for p_idx, (i, j) in enumerate(zip(lat_inds, lon_inds)):
                    try:
                        grid[t_idx][i][j] = data[t_idx][p_idx]
                    except IndexError:
                        pass
        else:
            for p_idx, (i, j) in enumerate(zip(lat_inds, lon_inds)):
                try:
                    grid[i][j] = data[p_idx]
                except IndexError:
                    pass

        rect_data[var] = grid

    rect_data['latitude'] = lat_unique
    rect_data['longitude'] = lon_unique
    rect_data['time'] = [times[i] for i in year_indices]

    return rect_data


def write_unserialized_netcdf():

    input_file = plotPARAMS.data_path + plotPARAMS.file_name
    output_file = plotPARAMS.data_path + plotPARAMS.file_name + "_filled.nc"

    # --- Header ---
    header = readJULES.read_jules_header(input_file)
    dimension_keys, variable_keys = list(header[0]), list(header[1])

    # --- Detect coordinate names ---
    if 'latitude' in variable_keys and 'longitude' in variable_keys:
        lat_string, lon_string = 'latitude', 'longitude'
    elif 'lat' in variable_keys and 'lon' in variable_keys:
        lat_string, lon_string = 'lat', 'lon'

    if 'lat' in dimension_keys and 'lon' in dimension_keys:
        lat_key, lon_key = 'lat', 'lon'
    elif 'y' in dimension_keys and 'x' in dimension_keys:
        lat_key, lon_key = 'y', 'x'

    # --- Read coordinates ---
    lats, _, _, _ = readJULES.read_jules_m2(input_file, lat_string)
    lons, _, _, _ = readJULES.read_jules_m2(input_file, lon_string)

    # --- Fill gaps in latitude and longitude ---
    def fill_gaps(arr):
        arr_filled = arr.copy()
        # Row-wise
        for i in range(arr_filled.shape[0]):
            row = arr_filled[i, :]
            nans = np.isnan(row)
            if np.any(nans):
                valid = np.where(~nans)[0]
                if valid.size > 0:
                    row[nans] = np.interp(np.flatnonzero(nans), valid, row[valid])
                arr_filled[i, :] = row
        # Column-wise
        for j in range(arr_filled.shape[1]):
            col = arr_filled[:, j]
            nans = np.isnan(col)
            if np.any(nans):
                valid = np.where(~nans)[0]
                if valid.size > 0:
                    col[nans] = np.interp(np.flatnonzero(nans), valid, col[valid])
                arr_filled[:, j] = col
        return arr_filled

    lats_filled = fill_gaps(lats)
    lons_filled = fill_gaps(lons)

    # --- Create dataset ---
    ds_out = xr.Dataset()
    ds_out[lat_key] = (('y', 'x'), lats_filled)
    ds_out[lon_key] = (('y', 'x'), lons_filled)
    ds_out[lat_key].attrs['units'] = 'degrees_north'
    ds_out[lon_key].attrs['units'] = 'degrees_east'

    # --- Process variables ---
    for var_name in variable_keys:
        print("Processing:", var_name)
        var, unit, long_name, dims = readJULES.read_jules_m2(input_file, var_name)

        if 'bounds' in var_name.lower():
            ds_out[var_name] = (dims, var)
            continue

        # Sanitize numeric arrays
        try:
            if np.issubdtype(np.asarray(var).dtype, np.number):
                var = sanitize_extreme_values(var)
        except:
            pass

        # Identify spatial axes
        lat_axis = dims.index(lat_key) if lat_key in dims else None
        lon_axis = dims.index(lon_key) if lon_key in dims else None

        if lat_axis is None or lon_axis is None:
            ds_out[var_name] = (dims, var)
            continue

        # Extra axes
        extra_axes = [i for i in range(len(dims)) if i not in [lat_axis, lon_axis]]
        extra_shape = [var.shape[i] for i in extra_axes]

        # Initialize output array
        Ny, Nx = lats_filled.shape
        var_grid = np.full(extra_shape + [Ny, Nx], np.nan)

        # Map serialized variable to grid if same size as flattened coords
        flat_vals = var.flatten()
        if flat_vals.size == lats.size:
            for i in range(flat_vals.size):
                yi, xi = np.unravel_index(i, lats.shape)
                var_grid[(slice(None),)*len(extra_shape) + (yi, xi)] = flat_vals[i]

        new_dims = [dims[i] for i in extra_axes] + [lat_key, lon_key]
        ds_out[var_name] = (new_dims, var_grid)
        try:
            ds_out[var_name].attrs['units'] = unit
            ds_out[var_name].attrs['long_name'] = long_name
        except:
            pass

    # --- Save ---
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    ds_out.to_netcdf(output_file)
    print("Written:", output_file)