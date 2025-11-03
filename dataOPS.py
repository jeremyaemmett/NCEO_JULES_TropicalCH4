import numpy as np


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

    """_summary_
    Args:
        lats / lons (float): 1D arrays of latitude / longitude coordinates
        latitude / longitude (float): latitude / longitude where area is desired
    Returns:
        box_area (float): Surface area of the gridbox centered on latitude / longitude
    """

    # Determine the spacing of latitude and longitude grid cells (degrees)
    lat_sep, lon_sep = np.diff(lats)[0], np.diff(lons)[0]

    # Clip to avoid going outside valid lat range
    lat1, lat2 = np.clip([latitude - lat_sep, latitude + lat_sep], -90, 90)
    lon1, lon2 = longitude - lon_sep, longitude + lon_sep

    # Convert to radians
    lat1, lat2 = np.deg2rad(lat1), np.deg2rad(lat2)
    lon1, lon2 = np.deg2rad(lon1), np.deg2rad(lon2)

    # Compute area in km^2
    r_earth = 6.378e6  # km
    box_area = (r_earth**2) * (np.sin(lat2) - np.sin(lat1)) * (lon2 - lon1)

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


