import matplotlib.patheffects as PathEffects
import cartopy.io.shapereader as shpreader
import cartopy.io.img_tiles as cimgt
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import processJULES
import numpy as np
import plotPARAMS
import readJULES
import rasterio
import dataOPS
import sysOPS
import os


def make_maps():

    # Clear all .txt files in the output path
    [os.remove(os.path.join(dp, f)) for dp, dn, fn in os.walk(plotPARAMS.outp_path) for f in fn if f.endswith('.txt')]

    # Full 'time' array
    times, times_unit, times_long_name, times_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, 'time')
    times = dataOPS.ensure_np_datetime(times)
    # Get the time dimension indices that fall within the desired year
    year_indices = np.where((times >= np.datetime64(f'{plotPARAMS.year}-01-01')) & (times < np.datetime64(f'{plotPARAMS.year + 1}-01-01')))[0]

    header = readJULES.read_jules_header(plotPARAMS.data_path + plotPARAMS.file_name)
    dimension_keys, variable_keys = list(header[0]), list(header[1])

    if 'latitude' in variable_keys and 'longitude' in variable_keys: lat_string, lon_string = 'latitude', 'longitude'
    if 'lat' in variable_keys and 'lon' in variable_keys: lat_string, lon_string = 'lat', 'lon'

    if 'lat' in dimension_keys and 'lon' in dimension_keys: lat_key, lon_key = 'lat', 'lon'
    if 'y' in dimension_keys and 'x' in dimension_keys: lat_key, lon_key = 'y', 'x'

    # Latitudes and Longitudes, their full arrays
    lats, lats_units, lats_long_name, lats_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, lat_string)
    lons, lons_units, lons_long_name, lons_dims = readJULES.read_jules_m2(plotPARAMS.data_path + plotPARAMS.file_name, lon_string)
    
    # Flatten 1D arrays and infer grid
    lats_flat = lats.flatten()
    lons_flat = lons.flatten()
    lats_unique = np.sort(np.unique(lats_flat))
    lons_unique = np.sort(np.unique(lons_flat))
    dlat = np.median(np.diff(lats_unique))
    dlon = np.median(np.diff(lons_unique))
    lat_grid = np.arange(lats_unique.min(), lats_unique.max() + dlat/2, dlat)
    lon_grid = np.arange(lons_unique.min(), lons_unique.max() + dlon/2, dlon)
    Ny, Nx = len(lat_grid), len(lon_grid)
    lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)
    lat_idx = ((lats_flat - lat_grid[0]) / dlat).round().astype(int)
    lon_idx = ((lons_flat - lon_grid[0]) / dlon).round().astype(int)
    lat2d, lon2d = np.meshgrid(lat_grid, lon_grid, indexing='ij')

    print('Lats: ', lats)
    print('Lons: ', lons)
    print('Coords are serialized with inferred lat/lon resolution: ', dlat, dlon)

    print(' ')
    # Loop through variables
    for variable_name in plotPARAMS.variable_names:
        print('Processing variable:', variable_name)

        # 1. Read variable
        variable_array, variable_unit, variable_long_name, variable_dims = readJULES.read_jules_m2(
            plotPARAMS.data_path + plotPARAMS.file_name, variable_name
        )

        # 2. Sanitize extreme values
        variable_array = dataOPS.sanitize_extreme_values(variable_array)

        # 3. Map 1D variable to grid
        lat_axis = variable_dims.index(lat_key) if lat_key in variable_dims else None
        lon_axis = variable_dims.index(lon_key) if lon_key in variable_dims else None
        
        extra_axes = [i for i in range(len(variable_dims)) if i not in [lat_axis, lon_axis]]
        extra_shape = [variable_array.shape[i] for i in extra_axes]
        var_grid = np.full(extra_shape + [Ny, Nx], np.nan)
        
        # Loop through extra dimensions e.g. layer, soil type, etc.
        for idx in np.ndindex(*extra_shape):
            orig_idx = list(idx)
            if lat_axis is not None:
                orig_idx.insert(lat_axis if lat_axis < len(orig_idx) else len(orig_idx), slice(None))
            if lon_axis is not None:
                orig_idx.insert(lon_axis if lon_axis < len(orig_idx) else len(orig_idx), slice(None))
            
            flat_values = variable_array[tuple(orig_idx)].flatten()
            if flat_values.size != lat_idx.size:
                raise ValueError(f"Mismatch between flat_values ({flat_values.size}) and lat/lon points ({lat_idx.size})")
            
            var_grid[idx + (lat_idx, lon_idx)] = flat_values

        variable_array = var_grid
        print('Variable gridded shape:', variable_array.shape)

        # 4. Trim time to desired year
        if 'time' in variable_dims and variable_array.shape[0] > 12:
            time_dim_index = np.where(np.array(variable_dims) == 'time')[0][0]
            variable_array = np.take(variable_array, indices=year_indices, axis=time_dim_index)

        # 5. Generate slice indices for additional dimensions
        iterable_dimension_mask = ~np.isin(list(variable_dims), [lon_key, lat_key])
        iterable_dimension_keys = np.array(list(variable_dims))[iterable_dimension_mask]
        iterable_dimension_idxs = np.where(iterable_dimension_mask)[0]
        iterable_dimension_iter = np.array(variable_array.shape)[iterable_dimension_idxs]
        indices = dataOPS.generate_indices(list(iterable_dimension_iter))

        for combo in indices:
            key_labels = [str(plotPARAMS.year)]
            variable_array2 = np.copy(variable_array)
            count = 0
            for var_dim_key, slice_index, slice_val in zip(iterable_dimension_keys, iterable_dimension_idxs, combo):
                variable_array2 = variable_array2.take(slice_val, axis=slice_index - count)
                key_labels.append("("+str(slice_val)+")" + dataOPS.keyval2keylabel(var_dim_key, slice_val))
                count += 1

            sub_folder = key_labels[-1].replace(".", "p").replace(" ", "") if len(key_labels) > 2 else None

            # Make map and save
            # lat2d, lon2d, and variable_array2 have dimensions: [n_lats, n_lons]
            fig, ax = world_map(lat2d, lon2d)
            overplot_variable(ax, lat2d, lon2d, variable_name, variable_long_name,
                              variable_array2, variable_unit, key_labels,
                              'inferno', *dataOPS.globalMinMax(variable_array, variable_unit))
            
            print('test: ', variable_array2.shape)
            print('lats: ', lat2d.shape)
            print('lons: ', lon2d.shape)

            zonal_mean = processJULES.compute_zonal_mean2(variable_array2)
            areal_mean = processJULES.compute_areal_mean2(variable_array2, lat2d, lon2d)
            zonal_intg = processJULES.compute_zonal_intg2(variable_array2, lat2d, lon2d)

            print('zonal_mean: ', zonal_mean)
            #def compute_zonal_mean(variable_array, variable_unit, lat2d, lon2d, lats, lons, lat1, lat2, lon1, lon2): 

            cleaned_text = str(key_labels).translate(str.maketrans({char: "" for char in "[]',"})).replace(" ", "_").replace(".", "p")
            save_dir = os.path.join(plotPARAMS.outp_path, 'output', variable_name)
            if sub_folder:
                save_dir = os.path.join(save_dir, sub_folder)

            os.makedirs(save_dir, exist_ok=True)
            with open(save_dir + '/_zonalmean_tseries.txt', 'a') as file: file.write(' '.join(map(str, zonal_mean)) + '\n')    
            with open(save_dir + '/_arealmean_tseries.txt', 'a') as file: file.write(str(areal_mean) + '\n')  
            with open(save_dir + '/_zonalintg_tseries.txt', 'a') as file: file.write(' '.join(map(str, zonal_intg)) + '\n')
            
            plt.savefig(os.path.join(save_dir, f'{variable_name}_{cleaned_text}_map.png'), dpi=300, bbox_inches='tight')
            plt.close()


def make_animated_maps():

    # Make a list of every t-series file across all of the input variables
    files = sysOPS.discover_files(plotPARAMS.outp_path, '_map.png')

    unique_end_directories = sysOPS.get_unique_end_directories(files)

    for unique_end_directory in unique_end_directories:

        map_files = sysOPS.discover_files(unique_end_directory, '_map.png')
        
        #miscOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/' + unique_end_directory.split('/')[-1] + '_animation.gif', duration=150, smooth=True, exclude_substr='plot_')
        sysOPS.pngs_to_gif(unique_end_directory, unique_end_directory + '/map_animation.gif', duration=150, smooth=True, exclude_substr=['plot_', 'complete', 'zonalmeans'])


def world_map(lats, lons, dem_path='ETOPO1.tiff', country_fontsize=8):
    """
    Create a world map with shaded topography, rivers, borders, and country labels.
    """
    # Map extents
    lon_min, lon_max = np.min(lons)-1.5, np.max(lons)+1.5
    lat_min, lat_max = np.min(lats)-1.5, np.max(lats)+1.5

    # Figure and axis
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])

    # --- Overlay topographic shading from DEM ---
    #try:
    #    with rasterio.open(dem_path) as src:
    #        topo = src.read(1)
    #        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
    #        ax.imshow(topo, extent=extent, transform=ccrs.PlateCarree(),
    #                  cmap='gist_earth', alpha=0.5, zorder=0)
    #except Exception as e:
    #    print(f"Warning: Could not load DEM for shading: {e}")

    # --- Base layers ---
    ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=1)
    ax.add_feature(cfeature.OCEAN, facecolor='white', zorder=1)
    ax.add_feature(cfeature.RIVERS.with_scale('50m'), edgecolor='blue', linewidth=0.5, zorder=2)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=1.2, zorder=3, edgecolor='gray')
    ax.coastlines(resolution='50m', zorder=4)

    # --- Gridlines ---
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'fontsize': 16}
    gl.ylabel_style = {'fontsize': 16}

    # --- Country labels ---
    shpfilename = shpreader.natural_earth(
        resolution='110m', category='cultural', name='admin_0_countries'
    )
    reader = shpreader.Reader(shpfilename)

    for record in reader.records():
        geom = record.geometry
        centroid = geom.centroid
        if (lon_min <= centroid.x <= lon_max and lat_min <= centroid.y <= lat_max):
            txt = ax.text(
                centroid.x, centroid.y, record.attributes['NAME'],
                fontsize=country_fontsize, fontweight='bold',
                fontstyle='italic',      # keep italic if desired
                fontfamily='sans-serif', # keep family if needed
                transform=ccrs.PlateCarree(),
                ha='center', va='center', color='black'
            )
            # Add white outline around text
            txt.set_path_effects([
                PathEffects.withStroke(linewidth=2, foreground='lightgray')
            ])

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

    #print('vmin, vmax: ', vmin, vmax)

    n_levels = 10

    step_raw = (vmax - vmin) / (n_levels - 1)
    mag = 10 ** np.floor(np.log10(step_raw))
    step = mag * (1 if step_raw/mag <= 1 else 2 if step_raw/mag <= 2 else 5)

    vmin_r = np.floor(vmin / step) * step
    vmax_r = np.ceil(vmax / step) * step

    #print('var: ', variable_name)
    levels = np.arange(vmin_r, vmax_r + step/2, step)

    print(lat2d.shape)
    c = ax.contourf(lon2d, lat2d, variable_array,
                    levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    cb = plt.colorbar(c, orientation='vertical', pad=0.05, shrink=0.8)
    cb.set_label(dataOPS.cleanup_exponents(variable_unit), fontsize=18)
    cb.ax.tick_params(labelsize=14)

    variable_name_fix = variable_name.split('_')[0] + '\_' + variable_name.split('_')[1] if len(variable_name.split('_')) > 1 else variable_name

    subtitle = ''
    for key in key_labels: subtitle += key + '  '
    
    ax.set_title(dataOPS.remove_parenthetical_substrings(r"$\bf{" + variable_name_fix + "}$" + '\n' + variable_long_name), loc='left', fontsize=18)
    ax.text(np.min(lon2d)-1, np.min(lat2d)-1, dataOPS.remove_parenthetical_substrings(subtitle), fontsize=18, color='black', ha='left', va='bottom', style='italic')


def add_hillshade(ax):
    tiler = cimgt.Stamen('terrain-background')  # or 'terrain'
    ax.add_image(tiler, 6, zorder=0)  # 6 is zoom level, adjust for resolution