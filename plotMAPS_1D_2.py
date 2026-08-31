import matplotlib.patheffects as PathEffects
import cartopy.io.shapereader as shpreader
import matplotlib.patches as patches
import cartopy.io.img_tiles as cimgt
import matplotlib.colors as mcolors
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.cm as cm

import processJULES
import numpy as np
import plotPARAMS
import readJULES
import rasterio
import textwrap
import dataOPS
import sysOPS

import os
import re


# =============================================================
# GLOBAL MATPLOTLIB SETTINGS
# =============================================================

plt.rcParams.update({
    'axes.grid': False,
    'xtick.bottom': False,
    'xtick.top': False,
    'xtick.labelbottom': False,
    'xtick.labeltop': False,
    'ytick.left': False,
    'ytick.right': False,
    'ytick.labelleft': False,
    'ytick.labelright': False,
})


# =============================================================
# HELPER: COMPLETELY CLEAN CARTOPY AXIS
# =============================================================

def clean_map_axis(ax):
    """
    Completely remove coordinate/grid decoration from a
    Cartopy GeoAxes.

    This intentionally does NOT create a Cartopy Gridliner.
    """

    # ---------------------------------------------------------
    # Remove GeoAxes frame
    # ---------------------------------------------------------

    try:
        ax.spines['geo'].set_visible(False)
    except Exception:
        pass

    # ---------------------------------------------------------
    # Remove ordinary matplotlib ticks
    # ---------------------------------------------------------

    try:
        ax.set_xticks([])
        ax.set_yticks([])
    except Exception:
        pass

    # ---------------------------------------------------------
    # Disable every tick/label location
    # ---------------------------------------------------------

    ax.tick_params(
        axis='both',
        which='both',
        bottom=False,
        top=False,
        left=False,
        right=False,
        labelbottom=False,
        labeltop=False,
        labelleft=False,
        labelright=False,
        length=0,
        width=0
    )

    # ---------------------------------------------------------
    # Explicitly disable matplotlib grid
    # ---------------------------------------------------------

    try:
        ax.grid(
            False,
            which='both',
            axis='both'
        )
    except Exception:
        pass

    # ---------------------------------------------------------
    # Remove any existing Gridliner objects.
    #
    # This is defensive. The code below never creates one,
    # but this prevents inherited gridliners from surviving.
    # ---------------------------------------------------------

    try:

        children = list(
            ax.get_children()
        )

        for child in children:

            if (
                child.__class__.__name__
                == 'Gridliner'
            ):

                try:
                    child.set_visible(False)
                except Exception:
                    pass

    except Exception:
        pass


# =============================================================
# MAKE MAPS
# =============================================================

def make_maps(
        data_path,
        outp_path,
        file_name,
        year,
        stack_longitude_panels=False,
        apply_scale_factor=False,
        latitude_bounds=None):

    scale_factor = 1.0

    # ---------------------------------------------------------
    # Scale factor
    # ---------------------------------------------------------

    if apply_scale_factor:

        scale_file = os.path.join(
            data_path,
            "scale_factor.txt"
        )

        with open(
            scale_file,
            "r"
        ) as f:

            scale_factor = float(
                f.read().strip()
            )

        print(
            "Applying scale factor:",
            scale_factor
        )

    # ---------------------------------------------------------
    # Output directory
    # ---------------------------------------------------------

    output_root = os.path.join(
        outp_path,
        'output',
        'scaled'
        if apply_scale_factor
        else 'unscaled'
    )

    os.makedirs(
        output_root,
        exist_ok=True
    )

    print(
        "Saving outputs to:",
        output_root
    )

    # ---------------------------------------------------------
    # Clear TXT files
    # ---------------------------------------------------------

    for dp, dn, fn in os.walk(
        output_root
    ):

        for f in fn:

            if f.endswith('.txt'):

                os.remove(
                    os.path.join(
                        dp,
                        f
                    )
                )

    # =========================================================
    # TIME
    # =========================================================

    times, times_unit, times_long_name, times_dims = (
        readJULES.read_jules_m2(
            data_path + file_name,
            'time'
        )
    )

    times = dataOPS.ensure_np_datetime(
        times
    )

    year_indices = np.where(
        (times >= np.datetime64(
            f'{year}-01-01'
        ))
        &
        (times < np.datetime64(
            f'{year + 1}-01-01'
        ))
    )[0]

    # =========================================================
    # HEADER
    # =========================================================

    header = readJULES.read_jules_header(
        data_path + file_name
    )

    dimension_keys, variable_keys = (
        list(header[0]),
        list(header[1])
    )

    # =========================================================
    # LAT/LON VARIABLE NAMES
    # =========================================================

    if (
        'latitude' in variable_keys
        and
        'longitude' in variable_keys
    ):

        lat_string = 'latitude'
        lon_string = 'longitude'

    elif (
        'lat' in variable_keys
        and
        'lon' in variable_keys
    ):

        lat_string = 'lat'
        lon_string = 'lon'

    else:

        raise ValueError(
            "Could not identify latitude/longitude variables."
        )

    # =========================================================
    # LAT/LON DIMENSION NAMES
    # =========================================================

    if (
        'lat' in dimension_keys
        and
        'lon' in dimension_keys
    ):

        lat_key = 'lat'
        lon_key = 'lon'

    elif (
        'y' in dimension_keys
        and
        'x' in dimension_keys
    ):

        lat_key = 'y'
        lon_key = 'x'

    else:

        raise ValueError(
            "Could not identify latitude/longitude dimensions."
        )

    # =========================================================
    # READ LAT/LON
    # =========================================================

    lats, lats_units, lats_long_name, lats_dims = (
        readJULES.read_jules_m2(
            data_path + file_name,
            lat_string
        )
    )

    lons, lons_units, lons_long_name, lons_dims = (
        readJULES.read_jules_m2(
            data_path + file_name,
            lon_string
        )
    )

    # =========================================================
    # FLATTEN
    # =========================================================

    lats_flat_full = lats.flatten()
    lons_flat_full = lons.flatten()

    # =========================================================
    # LATITUDE MASK
    # =========================================================

    if latitude_bounds is not None:

        lat_min, lat_max = latitude_bounds

        lat_mask = (
            (lats_flat_full >= lat_min)
            &
            (lats_flat_full <= lat_max)
        )

        if not np.any(lat_mask):

            raise ValueError(
                f"No latitude points found between "
                f"{lat_min} and {lat_max}"
            )

        print(
            f"Restricting latitude range to "
            f"{lat_min} to {lat_max}"
        )

    else:

        lat_mask = np.ones(
            lats_flat_full.shape,
            dtype=bool
        )

    lats_flat = (
        lats_flat_full[
            lat_mask
        ]
    )

    lons_flat = (
        lons_flat_full[
            lat_mask
        ]
    )

    # =========================================================
    # INFER GRID
    # =========================================================

    lats_unique = np.sort(
        np.unique(
            lats_flat
        )
    )

    lons_unique = np.sort(
        np.unique(
            lons_flat
        )
    )

    if len(lats_unique) < 2:

        raise ValueError(
            "Not enough unique latitude points "
            "to construct a grid."
        )

    if len(lons_unique) < 2:

        raise ValueError(
            "Not enough unique longitude points "
            "to construct a grid."
        )

    dlat = np.median(
        np.diff(
            lats_unique
        )
    )

    dlon = np.median(
        np.diff(
            lons_unique
        )
    )

    lat_grid = np.arange(
        lats_unique.min(),
        lats_unique.max() + dlat / 2,
        dlat
    )

    lon_grid = np.arange(
        lons_unique.min(),
        lons_unique.max() + dlon / 2,
        dlon
    )

    Ny = len(
        lat_grid
    )

    Nx = len(
        lon_grid
    )

    lat_idx = (
        (
            lats_flat
            -
            lat_grid[0]
        )
        /
        dlat
    ).round().astype(int)

    lon_idx = (
        (
            lons_flat
            -
            lon_grid[0]
        )
        /
        dlon
    ).round().astype(int)

    # ---------------------------------------------------------
    # Bounds checking
    # ---------------------------------------------------------

    if (
        np.any(lat_idx < 0)
        or
        np.any(lat_idx >= Ny)
    ):

        raise ValueError(
            "Latitude indices fall outside inferred grid."
        )

    if (
        np.any(lon_idx < 0)
        or
        np.any(lon_idx >= Nx)
    ):

        raise ValueError(
            "Longitude indices fall outside inferred grid."
        )

    # =========================================================
    # 2D GRID
    # =========================================================

    lat2d, lon2d = np.meshgrid(
        lat_grid,
        lon_grid,
        indexing='ij'
    )

    # =========================================================
    # LOOP VARIABLES
    # =========================================================

    for variable_name in (
        plotPARAMS.variable_names
    ):

        print(
            'Processing variable:',
            variable_name
        )

        # -----------------------------------------------------
        # Read variable
        # -----------------------------------------------------

        variable_array, variable_unit, variable_long_name, variable_dims = (
            readJULES.read_jules_m2(
                data_path + file_name,
                variable_name
            )
        )

        # -----------------------------------------------------
        # Sanitize
        # -----------------------------------------------------

        variable_array = (
            dataOPS.sanitize_extreme_values(
                variable_array
            )
        )

        # -----------------------------------------------------
        # Scale
        # -----------------------------------------------------

        if (
            apply_scale_factor
            and
            variable_name == "fch4_wetl"
        ):

            variable_array *= (
                scale_factor
            )

        # -----------------------------------------------------
        # kg C -> kg CH4
        # -----------------------------------------------------

        if variable_name == "fch4_wetl":

            variable_array *= (
                16.043 / 12.011
            )

        # =====================================================
        # IDENTIFY AXES
        # =====================================================

        lat_axis = (
            variable_dims.index(
                lat_key
            )
            if lat_key in variable_dims
            else None
        )

        lon_axis = (
            variable_dims.index(
                lon_key
            )
            if lon_key in variable_dims
            else None
        )

        extra_axes = [
            i
            for i in range(
                len(variable_dims)
            )
            if i not in [
                lat_axis,
                lon_axis
            ]
        ]

        extra_shape = [
            variable_array.shape[i]
            for i in extra_axes
        ]

        var_grid = np.full(
            extra_shape + [
                Ny,
                Nx
            ],
            np.nan
        )

        # =====================================================
        # MAP DATA TO GRID
        # =====================================================

        for idx in np.ndindex(
            *extra_shape
        ):

            orig_idx = list(
                idx
            )

            if lat_axis is not None:

                orig_idx.insert(
                    lat_axis,
                    slice(None)
                )

            if lon_axis is not None:

                orig_idx.insert(
                    lon_axis,
                    slice(None)
                )

            flat_values = variable_array[
                tuple(orig_idx)
            ].flatten()

            if (
                flat_values.size
                !=
                lats_flat_full.size
            ):

                raise ValueError(
                    f"Mismatch between flat_values "
                    f"({flat_values.size}) and lat/lon "
                    f"points ({lats_flat_full.size})"
                )

            flat_values = (
                flat_values[
                    lat_mask
                ]
            )

            var_grid[
                idx + (
                    lat_idx,
                    lon_idx
                )
            ] = flat_values

        variable_array = (
            var_grid
        )

        print(
            'Variable gridded shape:',
            variable_array.shape
        )

        # =====================================================
        # TIME
        # =====================================================

        if (
            'time' in variable_dims
            and
            variable_array.shape[0] > 12
        ):

            time_dim_index = np.where(
                np.array(variable_dims)
                == 'time'
            )[0][0]

            variable_array = np.take(
                variable_array,
                indices=year_indices,
                axis=time_dim_index
            )

        # =====================================================
        # EXTRA DIMENSIONS
        # =====================================================

        iterable_dimension_mask = ~np.isin(
            list(variable_dims),
            [
                lon_key,
                lat_key
            ]
        )

        iterable_dimension_keys = (
            np.array(
                list(variable_dims)
            )[
                iterable_dimension_mask
            ]
        )

        iterable_dimension_idxs = (
            np.where(
                iterable_dimension_mask
            )[0]
        )

        iterable_dimension_iter = (
            np.array(
                variable_array.shape
            )[
                iterable_dimension_idxs
            ]
        )

        indices = (
            dataOPS.generate_indices(
                list(
                    iterable_dimension_iter
                )
            )
        )

        # =====================================================
        # DIMENSION COMBINATIONS
        # =====================================================

        for combo in indices:

            key_labels = [
                str(year)
            ]

            variable_array2 = (
                np.copy(
                    variable_array
                )
            )

            count = 0

            for (
                var_dim_key,
                slice_index,
                slice_val
            ) in zip(
                iterable_dimension_keys,
                iterable_dimension_idxs,
                combo
            ):

                variable_array2 = (
                    variable_array2.take(
                        slice_val,
                        axis=slice_index - count
                    )
                )

                key_labels.append(
                    "("
                    +
                    str(slice_val)
                    +
                    ")"
                    +
                    dataOPS.keyval2keylabel(
                        var_dim_key,
                        slice_val
                    )
                )

                count += 1

            # -------------------------------------------------
            # Subfolder
            # -------------------------------------------------

            sub_folder = (
                key_labels[-1]
                .replace(".", "p")
                .replace(" ", "")
                if len(key_labels) > 2
                else None
            )

            # =================================================
            # CREATE MAP
            # =================================================

            fig, ax = world_map(
                lat2d,
                lon2d
            )

            # =================================================
            # DATA
            # =================================================

            overplot_variable(
                ax,
                lat2d,
                lon2d,
                variable_name,
                variable_long_name,
                variable_array2,
                variable_unit,
                key_labels,
                'jet',
                *dataOPS.globalMinMax(
                    variable_array,
                    variable_unit
                ),
                [
                    0.40,
                    0.05,
                    0.20,
                    0.025
                ]
            )

            # -------------------------------------------------
            # Ocean mask
            # -------------------------------------------------

            ax.add_feature(
                cfeature.OCEAN,
                facecolor='white',
                edgecolor='none',
                linewidth=0,
                zorder=5,
                alpha=1.0
            )

            # =================================================
            # DIAGNOSTICS
            # =================================================

            zonal_mean = (
                processJULES.compute_zonal_mean2(
                    variable_array2
                )
            )

            areal_mean = (
                processJULES.compute_areal_mean2(
                    variable_array2,
                    lat2d,
                    lon2d
                )
            )

            zonal_intg = (
                processJULES.compute_zonal_intg2(
                    variable_array2,
                    lat2d,
                    lon2d
                )
            )

            # =================================================
            # OUTPUT DIRECTORY
            # =================================================

            cleaned_text = str(
                key_labels
            ).translate(
                str.maketrans(
                    {
                        char: ""
                        for char in "[]',"
                    }
                )
            ).replace(
                " ",
                "_"
            ).replace(
                ".",
                "p"
            )

            save_dir = os.path.join(
                output_root,
                variable_name
            )

            if sub_folder:

                save_dir = os.path.join(
                    save_dir,
                    sub_folder
                )

            os.makedirs(
                save_dir,
                exist_ok=True
            )

            # =================================================
            # DIAGNOSTIC FILES
            # =================================================

            with open(
                os.path.join(
                    save_dir,
                    '_zonalmean_tseries.txt'
                ),
                'a'
            ) as file:

                file.write(
                    ' '.join(
                        map(
                            str,
                            zonal_mean
                        )
                    )
                    +
                    '\n'
                )

            with open(
                os.path.join(
                    save_dir,
                    '_arealmean_tseries.txt'
                ),
                'a'
            ) as file:

                file.write(
                    str(
                        areal_mean
                    )
                    +
                    '\n'
                )

            with open(
                os.path.join(
                    save_dir,
                    '_zonalintg_tseries.txt'
                ),
                'a'
            ) as file:

                file.write(
                    ' '.join(
                        map(
                            str,
                            zonal_intg
                        )
                    )
                    +
                    '\n'
                )

            # =================================================
            # SAVE MAP DATA
            # =================================================

            map_txt_path = os.path.join(
                save_dir,
                f'{variable_name}_{cleaned_text}_map.txt'
            )

            np.savetxt(
                map_txt_path,
                variable_array2,
                fmt='%.6e'
            )

            # =================================================
            # SAVE PNG
            # =================================================

            map_name = (
                f'{variable_name}_{cleaned_text}_map.png'
            )

            fname = os.path.basename(
                map_name
            )

            try:

                title_text = (
                    fname
                    .split(')')[1]
                    .split('_map')[0]
                )

            except IndexError:

                title_text = (
                    fname.replace(
                        '_map.png',
                        ''
                    )
                )

            ax.set_title(
                title_text,
                fontsize=48,
                fontstyle='italic',
                loc='left',
                y=0.1,
                x=0.02
            )

            # -------------------------------------------------
            # FINAL AXIS CLEAN
            # -------------------------------------------------

            clean_map_axis(
                ax
            )

            # -------------------------------------------------
            # Save
            # -------------------------------------------------

            plt.savefig(
                os.path.join(
                    save_dir,
                    map_name
                ),
                dpi=300,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )

            plt.close(
                fig
            )

        # =====================================================
        # SEASONAL PANEL
        # =====================================================

        make_seasonal_panel_from_txt(
            save_dir,
            lat2d,
            lon2d,
            variable_name,
            variable_long_name,
            variable_unit,
            *dataOPS.globalMinMax(
                variable_array,
                variable_unit
            )
        )


# =============================================================
# ANIMATED MAPS
# =============================================================

def make_animated_maps(
        data_path,
        outp_path,
        file_name,
        year):

    files = sysOPS.discover_files(
        outp_path,
        '_map.png'
    )

    unique_end_directories = (
        sysOPS.get_unique_end_directories(
            files
        )
    )

    for unique_end_directory in (
        unique_end_directories
    ):

        map_files = sysOPS.discover_files(
            unique_end_directory,
            '_map.png'
        )

        sysOPS.pngs_to_gif(
            unique_end_directory,
            unique_end_directory
            + '/map_animation.gif',
            duration=150,
            smooth=True,
            exclude_substr=[
                'plot_',
                'complete',
                'zonalmeans'
            ]
        )


# =============================================================
# WORLD MAP
# =============================================================

def world_map(
        lats,
        lons,
        dem_path='ETOPO1.tiff',
        country_fontsize=8):

    """
    Create a map with absolutely no coordinate grid,
    coordinate labels, or axis ticks.
    """

    # ---------------------------------------------------------
    # Figure
    # ---------------------------------------------------------

    fig = plt.figure(
        figsize=(40, 10)
    )

    # ---------------------------------------------------------
    # Cartopy axis
    # ---------------------------------------------------------

    ax = plt.axes(
        projection=ccrs.PlateCarree(
            central_longitude=25
        )
    )

    # ---------------------------------------------------------
    # Extent
    # ---------------------------------------------------------

    ax.set_extent(
        [
            -180,
            180,
            -65,
            65
        ],
        crs=ccrs.PlateCarree()
    )

    # ---------------------------------------------------------
    # Clean axis FIRST
    # ---------------------------------------------------------

    clean_map_axis(
        ax
    )

    # =========================================================
    # BASE MAP
    # =========================================================

    ax.add_feature(
        cfeature.LAND,
        facecolor='#f5e6c8',
        edgecolor='none',
        linewidth=0,
        zorder=1
    )

    ax.add_feature(
        cfeature.OCEAN,
        facecolor='white',
        edgecolor='none',
        linewidth=0,
        zorder=1
    )

    ax.add_feature(
        cfeature.LAKES,
        facecolor='#a6cee3',
        edgecolor='none',
        linewidth=0,
        zorder=1
    )

    # =========================================================
    # RIVERS
    # =========================================================

    ax.add_feature(
        cfeature.RIVERS.with_scale('50m'),
        edgecolor='blue',
        linewidth=0.5,
        zorder=2
    )

    # =========================================================
    # BORDERS
    # =========================================================

    ax.add_feature(
        cfeature.BORDERS.with_scale('50m'),
        edgecolor='gray',
        linewidth=1.2,
        zorder=3
    )

    # =========================================================
    # COASTLINES
    # =========================================================

    ax.coastlines(
        resolution='50m',
        linewidth=1.0,
        zorder=4
    )

    # =========================================================
    # CRITICAL:
    #
    # THERE IS NO ax.gridlines() CALL.
    #
    # THERE ARE NO GRIDLINER OBJECTS.
    #
    # THERE ARE NO LON/LAT LABELS.
    # =========================================================

    clean_map_axis(
        ax
    )

    return fig, ax


# =============================================================
# OVERPLOT VARIABLE
# =============================================================

def overplot_variable(
        ax,
        lat2d,
        lon2d,
        variable_name,
        variable_long_name,
        variable_array,
        variable_unit,
        key_labels,
        cmap,
        variable_global_min,
        variable_global_max,
        cbar_pos=None):

    """
    Plot variable data without pcolormesh cell-edge artefacts.
    """

    # =========================================================
    # COLOUR LIMITS
    # =========================================================

    vmin = variable_global_min
    vmax = variable_global_max

    if variable_name == 'fch4_wetl':

        vmin = 0.0
        vmax = 0.25

    # =========================================================
    # NORMALISATION
    # =========================================================

    norm = mcolors.Normalize(
        vmin=vmin,
        vmax=vmax
    )

    rgba_cmap = plt.get_cmap(
        cmap
    )

    # =========================================================
    # RGBA
    # =========================================================

    rgba_colors = rgba_cmap(
        norm(
            variable_array
        )
    )

    alpha = norm(
        variable_array
    )

    alpha = np.clip(
        alpha,
        0,
        1
    )

    alpha = np.nan_to_num(
        alpha,
        nan=0.0,
        posinf=1.0,
        neginf=0.0
    )

    rgba_colors[
        ...,
        -1
    ] = alpha

    # =========================================================
    # DATA MASK
    # =========================================================

    rgba_colors = np.asarray(
        rgba_colors
    )

    # =========================================================
    # PLOT
    #
    # IMPORTANT:
    #
    # antialiased=False
    # edgecolors='none'
    # linewidth=0
    #
    # These prevent the faint rectangular seams which can
    # otherwise appear between pcolormesh cells.
    # =========================================================

    c = ax.pcolormesh(
        lon2d,
        lat2d,
        rgba_colors,
        shading='nearest',
        antialiased=False,
        edgecolors='none',
        linewidth=0,
        rasterized=True,
        transform=ccrs.PlateCarree(),
        zorder=3
    )

    # =========================================================
    # COLOURBAR
    # =========================================================

    if cbar_pos is not None:

        cb_ax = plt.gcf().add_axes(
            cbar_pos
        )

        cb_ax.add_patch(
            plt.Rectangle(
                (0, 0),
                1,
                1,
                transform=cb_ax.transAxes,
                color='#f5e6c8',
                zorder=0,
                alpha=0.5
            )
        )

        N = 256

        colors = rgba_cmap(
            np.linspace(
                0,
                1,
                N
            )
        )

        colors[
            :,
            -1
        ] = np.linspace(
            0,
            1,
            N
        )

        alpha_cmap = (
            mcolors.ListedColormap(
                colors
            )
        )

        sm = cm.ScalarMappable(
            cmap=alpha_cmap,
            norm=norm
        )

        sm.set_array(
            variable_array
        )

        cb = plt.colorbar(
            sm,
            cax=cb_ax,
            orientation='horizontal'
        )

        cb.set_label(
            dataOPS.cleanup_exponents(
                variable_unit
            ),
            fontsize=36
        )

        cb.ax.tick_params(
            labelsize=18
        )

    return c


# =============================================================
# HILLSHADE
# =============================================================

def add_hillshade(
        ax):

    tiler = cimgt.Stamen(
        'terrain-background'
    )

    ax.add_image(
        tiler,
        6,
        zorder=0
    )


# =============================================================
# MONTH EXTRACTION
# =============================================================

def get_full_month_name(
        text):

    if text is None:

        return None

    text = str(
        text
    )

    month_lookup = {

        'jan': 'January',
        'january': 'January',

        'feb': 'February',
        'february': 'February',

        'mar': 'March',
        'march': 'March',

        'apr': 'April',
        'april': 'April',

        'may': 'May',

        'jun': 'June',
        'june': 'June',

        'jul': 'July',
        'july': 'July',

        'aug': 'August',
        'august': 'August',

        'sep': 'September',
        'sept': 'September',
        'september': 'September',

        'oct': 'October',
        'october': 'October',

        'nov': 'November',
        'november': 'November',

        'dec': 'December',
        'december': 'December'
    }

    ordered_months = sorted(
        month_lookup.keys(),
        key=len,
        reverse=True
    )

    text_lower = text.lower()

    for month_key in ordered_months:

        if re.search(
            r'(?<![A-Za-z])'
            +
            re.escape(
                month_key
            )
            +
            r'(?![A-Za-z])',
            text_lower
        ):

            return month_lookup[
                month_key
            ]

    month_number_lookup = {

        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }

    numbers_in_parentheses = re.findall(
        r'\((\d+)\)',
        text
    )

    for number_string in (
        numbers_in_parentheses
    ):

        number = int(
            number_string
        )

        if number in month_number_lookup:

            return month_number_lookup[
                number
            ]

        if (
            number + 1
            in
            month_number_lookup
        ):

            return month_number_lookup[
                number + 1
            ]

    return None


# =============================================================
# SEASONAL 2x2 PANEL
# =============================================================

def make_seasonal_panel_from_txt(
        save_dir,
        lat2d,
        lon2d,
        variable_name,
        variable_long_name,
        variable_unit,
        variable_global_min,
        variable_global_max):

    """
    Create:

        March       June

        September   December

    with NO longitude/latitude labels and NO gridlines.
    """

    # =========================================================
    # EXTENT
    # =========================================================

    lon_min = -180
    lon_max = 180

    lat_min = -60
    lat_max = 77

    # =========================================================
    # MONTHS
    # =========================================================

    months = [
        'March',
        'June',
        'September',
        'December'
    ]

    # =========================================================
    # FIND FILES
    # =========================================================

    files = {}

    print(
        '\nSearching for seasonal files in:',
        save_dir
    )

    if not os.path.isdir(
        save_dir
    ):

        print(
            'Seasonal directory does not exist:',
            save_dir
        )

        return

    for fname in os.listdir(
        save_dir
    ):

        if not fname.endswith(
            '_map.txt'
        ):

            continue

        full_path = os.path.join(
            save_dir,
            fname
        )

        detected_month = (
            get_full_month_name(
                fname
            )
        )

        if detected_month in months:

            files[
                detected_month
            ] = full_path

            print(
                f'  {detected_month}: {fname}'
            )

    # =========================================================
    # CHECK FILES
    # =========================================================

    missing = [
        month
        for month in months
        if month not in files
    ]

    if missing:

        print(
            f"Skipping {save_dir}, "
            f"missing {missing}"
        )

        return

    # =========================================================
    # FIGURE
    # =========================================================

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(26, 11),
        subplot_kw={
            'projection': ccrs.PlateCarree(
                central_longitude=25
            )
        }
    )

    axes = axes.flatten()

    positions = {

        'March': 0,
        'June': 1,
        'September': 2,
        'December': 3
    }

    # =========================================================
    # PLOT EACH MONTH
    # =========================================================

    for month in months:

        ax = axes[
            positions[month]
        ]

        # -----------------------------------------------------
        # Extent
        # -----------------------------------------------------

        ax.set_extent(
            [
                lon_min,
                lon_max,
                lat_min,
                lat_max
            ],
            crs=ccrs.PlateCarree()
        )

        # -----------------------------------------------------
        # Clean axis
        # -----------------------------------------------------

        clean_map_axis(
            ax
        )

        # =====================================================
        # BASE MAP
        # =====================================================

        ax.add_feature(
            cfeature.LAND,
            facecolor='#f5e6c8',
            edgecolor='none',
            linewidth=0,
            zorder=1
        )

        ax.add_feature(
            cfeature.OCEAN,
            facecolor='white',
            edgecolor='none',
            linewidth=0,
            zorder=1
        )

        ax.add_feature(
            cfeature.LAKES,
            facecolor='#a6cee3',
            edgecolor='none',
            linewidth=0,
            zorder=1
        )

        # =====================================================
        # RIVERS
        # =====================================================

        ax.add_feature(
            cfeature.RIVERS.with_scale('50m'),
            edgecolor='blue',
            linewidth=0.5,
            zorder=2
        )

        # =====================================================
        # BORDERS
        # =====================================================

        ax.add_feature(
            cfeature.BORDERS.with_scale('50m'),
            edgecolor='gray',
            linewidth=1.2,
            alpha=0.3,
            zorder=3
        )

        # =====================================================
        # COASTLINES
        # =====================================================

        ax.coastlines(
            resolution='50m',
            linewidth=1.0,
            zorder=4
        )

        # =====================================================
        # NO GRIDLINES
        #
        # DO NOT ADD ax.gridlines()
        # =====================================================

        # =====================================================
        # NO TICKS
        # =====================================================

        clean_map_axis(
            ax
        )

        # =====================================================
        # READ DATA
        # =====================================================

        data = np.loadtxt(
            files[month]
        )

        # =====================================================
        # PLOT DATA
        # =====================================================

        overplot_variable(
            ax,
            lat2d,
            lon2d,
            variable_name,
            variable_long_name,
            data,
            variable_unit,
            [month],
            'jet',
            variable_global_min,
            variable_global_max,
            None
        )

        # =====================================================
        # OCEAN MASK
        # =====================================================

        ax.add_feature(
            cfeature.OCEAN,
            facecolor='white',
            edgecolor='none',
            linewidth=0,
            zorder=5,
            alpha=1.0
        )

        # =====================================================
        # TITLE
        # =====================================================

        ax.set_title(
            month,
            fontsize=28,
            fontstyle='italic',
            loc='center',
            pad=20
        )

        # =====================================================
        # FINAL CLEAN
        # =====================================================

        clean_map_axis(
            ax
        )

    # =========================================================
    # COLOURBAR
    # =========================================================

    vmin = variable_global_min
    vmax = variable_global_max

    if variable_name == 'fch4_wetl':

        vmin = 0.0
        vmax = 0.25

    norm = mcolors.Normalize(
        vmin=vmin,
        vmax=vmax
    )

    rgba_cmap = plt.get_cmap(
        'jet'
    )

    N = 256

    colors = rgba_cmap(
        np.linspace(
            0,
            1,
            N
        )
    )

    colors[
        :,
        -1
    ] = np.linspace(
        0,
        1,
        N
    )

    alpha_cmap = (
        mcolors.ListedColormap(
            colors
        )
    )

    sm = cm.ScalarMappable(
        cmap=alpha_cmap,
        norm=norm
    )

    sm.set_array([])

    # =========================================================
    # COLOURBAR AXIS
    # =========================================================

    cbar_ax = fig.add_axes(
        [
            0.955,
            0.33,
            0.015,
            0.33
        ]
    )

    cbar_ax.add_patch(
        plt.Rectangle(
            (0, 0),
            1,
            1,
            transform=cbar_ax.transAxes,
            color='#f5e6c8',
            zorder=0,
            alpha=0.5
        )
    )

    cb = fig.colorbar(
        sm,
        cax=cbar_ax,
        orientation='vertical'
    )

    cb.set_label(
        dataOPS.cleanup_exponents(
            variable_unit
        ),
        fontsize=28,
        labelpad=20
    )

    cb.ax.tick_params(
        labelsize=24
    )

    # =========================================================
    # LAYOUT
    # =========================================================

    plt.subplots_adjust(
        left=0.04,
        right=0.93,
        top=0.96,
        bottom=0.06,
        wspace=0.05,
        hspace=0.12
    )

    # =========================================================
    # FINAL AXIS CLEAN
    # =========================================================

    for ax in axes:

        clean_map_axis(
            ax
        )

    # =========================================================
    # SAVE
    # =========================================================

    outfile = os.path.join(
        save_dir,
        f'{variable_name}_seasonal_panel.png'
    )

    plt.savefig(
        outfile,
        dpi=300,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none'
    )

    plt.close(
        fig
    )

    print(
        'Saved:',
        outfile
    )
