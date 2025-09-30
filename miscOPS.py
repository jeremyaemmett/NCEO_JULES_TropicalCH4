from PIL import Image
import pandas as pd
import numpy as np
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

def pngs_to_gif(folder, out='out.gif', duration=600, smooth=False, exclude_substr=None):

    def get_sorted_pngs(folder, exclude_substr):
        def sort_key(name):
            num = ''
            for c in name:
                if c.isdigit():
                    num += c
            return int(num) if num else -1  # sort purely by number

        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith('.png') and (
                exclude_substr is None or 
                not any(sub in f for sub in exclude_substr)
            )
        ]
        return sorted(files, key=sort_key)

    files = get_sorted_pngs(folder, exclude_substr)
    print('sorted files: ', files)
    
    if not files:
        raise ValueError("No PNG files found in folder.")

    # Load and resize images
    base_img = Image.open(os.path.join(folder, files[0])).convert('RGB')
    base_size = base_img.size
    images = [base_img]

    for f in files[1:]:
        img = Image.open(os.path.join(folder, f)).convert('RGB').resize(base_size)
        images.append(img)

    # Prepare full list of frames (including blended if smooth=True)
    full_frames = []
    for i, img in enumerate(images):
        full_frames.append(img)
        if smooth:
            # Blend to next frame if not the last
            if i < len(images) - 1:
                next_img = images[i + 1]
                for alpha in (0.33, 0.66):
                    blended = Image.blend(img, next_img, alpha)
                    full_frames.append(blended)
            # ALSO, if this is the last image (December), blend back to first (January)
            elif i == len(images) - 1:
                first_img = images[0]
                for alpha in (0.33, 0.66):
                    blended = Image.blend(img, first_img, alpha)
                    full_frames.append(blended)

    # Create a global palette by merging all RGB frames into one long image
    palette_base = Image.new('RGB', (base_size[0], base_size[1] * len(full_frames)))
    for i, frame in enumerate(full_frames):
        palette_base.paste(frame, (0, i * base_size[1]))

    # Use this image to generate a global palette
    palette_image = palette_base.quantize(colors=256, method=Image.MEDIANCUT)

    # Apply global palette to all frames
    paletted_frames = [frame.quantize(palette=palette_image) for frame in full_frames]

    # Save to GIF
    print('saving to: ', out)
    paletted_frames[0].save(out, save_all=True, append_images=paletted_frames[1:], duration=duration, loop=0)


def discover_files(root_path, end_string):

    # Make a list of every t-series file across all of the input variables
    files = [os.path.join(r, f) for r, _, fs in os.walk(root_path) for f in fs if f.endswith(end_string)]

    return files
    
    
def group_file_names_by_end_directory(file_names):

    # Loop through every t-series file
    grouped_files = {}
    for f in file_names:

        # Recover the variable name from the file path
        parts = os.path.normpath(f).split(os.sep)
 
        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(f))
            
        # Group the t-series file paths by their variables: Dictionary with {variable1: [t-series list], variable2: [t-series list]}
        grouped_files.setdefault(key, []).append(f)

    return grouped_files
        

def group_file_contents_by_end_directory(file_names):

    # Loop through every t-series file
    grouped = {}
    for f in file_names:

        # Recover the variable name from the file path
        parts = os.path.normpath(f).split(os.sep)

        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(f))
            
        # Group the t-series file paths by their variables: Dictionary with {variable1: [t-series list], variable2: [t-series list]}
        grouped.setdefault(key, []).append(pd.read_csv(f, header=None)[0].tolist())

    return grouped


def get_unique_end_directories(file_paths):
    end_dirs = set()
    for path in file_paths:
        dir_path = os.path.dirname(os.path.abspath(path))  # Get full absolute dir path
        end_dirs.add(dir_path)
    return sorted(end_dirs)  # Optional: sorted for consistent order

