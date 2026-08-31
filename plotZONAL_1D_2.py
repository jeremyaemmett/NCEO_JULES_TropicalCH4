from matplotlib.patches import Rectangle
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
import matplotlib.colors as mcolors
import matplotlib.colors as mcolor
import cartopy.feature as cfeature
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib import colors
import cartopy.crs as ccrs
import matplotlib.cm as cm
import processJULES
import pandas as pd
import numpy as np
import plotPARAMS
import readJULES
import plotMAPS
import dataOPS
import sysOPS
import os

from matplotlib.ticker import FuncFormatter


def make_zonal(
    data_path,
    outp_path,
    file_name,
    year,
    apply_scale_factor=False
):

    scale_folder = (
        'scaled'
        if apply_scale_factor
        else 'unscaled'
    )

    zonal_search_path = os.path.join(
        outp_path,
        'output',
        scale_folder
    )

    print(
        'Looking for zonal files in:',
        zonal_search_path
    )

    files = sysOPS.discover_files(
        zonal_search_path,
        '_zonalmean_tseries.txt'
    )

    unique_end_directories = (
        sysOPS.get_unique_end_directories(files)
    )

    header = readJULES.read_jules_header(
        data_path + file_name
    )

    dimension_keys, variable_keys = (
        list(header[0]),
        list(header[1])
    )

    # ============================================================
    # COORDINATE NAMES
    # ============================================================

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
            'Could not identify latitude/longitude variables.'
        )

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
            'Could not identify latitude/longitude dimensions.'
        )

    # ============================================================
    # LATITUDES AND LONGITUDES
    # ============================================================

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

    lats_unique_full = np.sort(
        np.unique(
            lats.flatten()
        )
    )

    lats_unique_restricted = (
        lats_unique_full[
            (lats_unique_full >= -36.0)
            &
            (lats_unique_full <= 36.0)
        ]
    )

    # ============================================================
    # MONTH LABELS
    # ============================================================

    months = [
        'J', 'F', 'M', 'A', 'M', 'J',
        'J', 'A', 'S', 'O', 'N', 'D'
    ]

    month_positions = np.arange(
        len(months)
    )

    # ============================================================
    # REGIONAL COLOURS
    # ============================================================

    region_colors = {
        'Global': 'black',
        'Tropical': 'red',
        'Extratropical': 'blue'
    }

    # ============================================================
    # LOOP OVER OUTPUT DIRECTORIES
    # ============================================================

    for unique_end_directory in unique_end_directories:

        zonal_file = sysOPS.discover_files(
            unique_end_directory,
            '_zonalmean_tseries.txt'
        )[0]

        areal_file = sysOPS.discover_files(
            unique_end_directory,
            '_arealmean_tseries.txt'
        )[0]

        integ_file = sysOPS.discover_files(
            unique_end_directory,
            '_zonalintg_tseries.txt'
        )[0]

        # ========================================================
        # RECOVER VARIABLE NAME
        # ========================================================

        parts = os.path.normpath(
            zonal_file
        ).split(os.sep)

        try:

            i = parts.index(
                'output'
            )

            after = parts[
                i + 1:-1
            ]

            key = next(
                part
                for part in after
                if part in plotPARAMS.variable_names
            )

        except (
            ValueError,
            StopIteration
        ):

            key = os.path.basename(
                os.path.dirname(
                    zonal_file
                )
            )

        print(
            'Zonal file:',
            zonal_file
        )

        print(
            'Recovered variable:',
            key
        )

        # ========================================================
        # VARIABLE METADATA
        # ========================================================

        k_array, k_unit, k_long_name, k_dims = (
            readJULES.read_jules_m2(
                data_path + file_name,
                key
            )
        )

        is_rate = dataOPS.check_if_rate(
            k_unit
        )

        # ========================================================
        # READ DATA
        # ========================================================

        zonal_values = np.loadtxt(
            zonal_file
        ).T

        zonal_values_trimmed = np.copy(
            zonal_values
        )

        areal_values = np.loadtxt(
            areal_file
        ).T

        integ_values = np.loadtxt(
            integ_file
        ).T

        # ========================================================
        # CUMULATIVE VALUES
        # ========================================================

        if integ_values.ndim == 1:

            integ_values_cumsum = (
                integ_values
            )

        elif integ_values.ndim == 2:

            integ_values_cumsum = np.cumsum(
                integ_values,
                axis=1
            )

        else:

            raise ValueError(
                f'Unexpected shape: '
                f'{integ_values.shape}'
            )

        # ========================================================
        # LATITUDE ARRAY
        # ========================================================

        num_zonal_lats = (
            zonal_values.shape[0]
        )

        if num_zonal_lats == len(
            lats_unique_full
        ):

            lats_plot = (
                lats_unique_full
            )

        elif num_zonal_lats == len(
            lats_unique_restricted
        ):

            lats_plot = (
                lats_unique_restricted
            )

        else:

            raise ValueError(
                f'Latitude mismatch: '
                f'zonal_values has '
                f'{num_zonal_lats} latitude points, '
                f'full array has '
                f'{len(lats_unique_full)}, '
                f'restricted array has '
                f'{len(lats_unique_restricted)}.'
            )

        print(
            'Using latitude array:',
            lats_plot
        )

        print(
            'Number of latitude bands:',
            len(lats_plot)
        )

        print(
            'zonal_values shape:',
            zonal_values.shape
        )

        print(
            'integ_values shape:',
            integ_values.shape
        )

        # ========================================================
        # X / Y COORDINATES
        # ========================================================

        X, Y = np.meshgrid(
            np.arange(
                zonal_values_trimmed.shape[1]
            ),
            lats_plot
        )

        num_layers = (
            zonal_values.shape[1]
        )

        # ========================================================
        # FIGURE LAYOUT
        # ========================================================

        if is_rate:

            fig = plt.figure(
                figsize=(30.0, 8.5)
            )

            gs = fig.add_gridspec(
                nrows=1,
                ncols=9,
                width_ratios=[
                    0.14,
                    1.00,
                    0.16,
                    0.055,
                    0.30,
                    1.00,
                    0.16,
                    0.055,
                    0.14
                ],
                left=0.035,
                right=0.98,
                bottom=0.16,
                top=0.84,
                wspace=0.0,
                hspace=0.0
            )

            ax1 = fig.add_subplot(
                gs[0, 1]
            )

            cb_ax1 = fig.add_subplot(
                gs[0, 3]
            )

            ax3 = fig.add_subplot(
                gs[0, 5]
            )

            cb_ax3 = fig.add_subplot(
                gs[0, 7]
            )

        else:

            fig = plt.figure(
                figsize=(26.0, 11.0)
            )

            gs = fig.add_gridspec(
                nrows=1,
                ncols=3,
                width_ratios=[
                    1.00,
                    0.055,
                    0.20
                ],
                left=0.10,
                right=0.93,
                bottom=0.16,
                top=0.84,
                wspace=0.0
            )

            ax1 = fig.add_subplot(
                gs[0, 0]
            )

            cb_ax1 = fig.add_subplot(
                gs[0, 1]
            )

        # ========================================================
        # COMMON LATITUDE SETTINGS
        # ========================================================

        ymin = (
            5 * (
                lats_plot.min() // 5
            )
        )

        ymax = (
            5 * (
                (lats_plot.max() + 4) // 5
            )
        )

        first_tick = (
            np.ceil(
                ymin / 30.0
            )
            * 30.0
        )

        last_tick = (
            np.floor(
                ymax / 30.0
            )
            * 30.0
        )

        yticks = np.arange(
            first_tick,
            last_tick + 30,
            30
        )

        latitude_formatter = (
            FuncFormatter(
                lambda y, pos:
                f'{y:.0f}°'
            )
        )

        # ========================================================
        # LEFT PANEL
        # ========================================================

        left_colorbar_min = 0.0
        left_colorbar_max = 0.185

        norm = mcolors.Normalize(
            vmin=left_colorbar_min,
            vmax=left_colorbar_max
        )

        rgba_cmap = plt.get_cmap(
            'jet'
        )

        rgba_colors = rgba_cmap(
            norm(
                zonal_values_trimmed
            )
        )

        rgba_colors[..., -1] = np.clip(
            norm(
                zonal_values_trimmed
            ),
            0.0,
            1.0
        )

        ax1.pcolormesh(
            X,
            Y,
            rgba_colors,
            shading='auto'
        )

        land_color = '#f5e6c8'

        ax1.set_facecolor(
            land_color
        )

        # --------------------------------------------------------
        # TITLE
        # --------------------------------------------------------

        ax1.set_title(
            r'$\mathbf{Monthly\ means}$'
            + '\n'
            + 'zonal (fill) and regional means (lines)',
            loc='left',
            fontsize=26,
            pad=14
        )

        ax1.set_ylabel(
            'Latitude',
            fontsize=26
        )

        ax1.set_xlabel(
            'Month',
            fontsize=26,
            labelpad=20
        )

        # --------------------------------------------------------
        # LEFT X AXIS
        # --------------------------------------------------------

        ax1.set_xlim(
            -0.5,
            len(months) - 0.5
        )

        ax1.set_xticks(
            month_positions
        )

        ax1.set_xticklabels(
            months
        )

        ax1.tick_params(
            axis='x',
            which='major',
            bottom=True,
            top=False,
            labelbottom=True,
            labeltop=False,
            pad=8,
            length=14,
            labelsize=20
        )

        # --------------------------------------------------------
        # LEFT Y AXIS
        # --------------------------------------------------------

        ax1.set_ylim(
            ymin,
            ymax
        )

        ax1.set_yticks(
            yticks
        )

        ax1.yaxis.set_major_formatter(
            latitude_formatter
        )

        ax1.tick_params(
            axis='y',
            which='major',
            left=True,
            labelleft=True,
            right=False,
            labelright=False,
            labelsize=24,
            direction='out',
            length=10,
            width=1.5
        )

        ax1.spines[
            'top'
        ].set_visible(
            False
        )

        ax1.spines[
            'right'
        ].set_visible(
            False
        )

        # ========================================================
        # LEFT COLOURBAR
        # ========================================================

        cb_ax1.set_facecolor(
            land_color
        )

        cb_ax1.add_patch(
            Rectangle(
                (0, 0),
                1,
                1,
                transform=cb_ax1.transAxes,
                color=land_color,
                zorder=0,
                alpha=1
            )
        )

        N = 256

        colors2 = rgba_cmap(
            np.linspace(
                0,
                1,
                N
            )
        )

        colors2[:, -1] = np.linspace(
            0,
            1,
            N
        )

        alpha_cmap = (
            mcolors.ListedColormap(
                colors2
            )
        )

        sm = cm.ScalarMappable(
            cmap=alpha_cmap,
            norm=norm
        )

        sm.set_array(
            rgba_colors
        )

        cb1 = plt.colorbar(
            sm,
            cax=cb_ax1
        )

        cb1.ax.tick_params(
            labelsize=22
        )

        cb1.set_label(
            ' \n'
            + dataOPS.cleanup_exponents(
                k_unit
            )
            + '\n',
            fontsize=22
        )

        # ========================================================
        # REGIONAL MONTHLY MEANS
        # ========================================================

        regional_masks = {

            'Global': np.ones(
                len(lats_plot),
                dtype=bool
            ),

            'Tropical': (
                (lats_plot >= -36)
                &
                (lats_plot <= 36)
            ),

            'Extratropical': (
                (lats_plot < -36)
                |
                (lats_plot > 36)
            )
        }

        latitude_weights = np.cos(
            np.deg2rad(
                lats_plot
            )
        )

        ax_regional = ax1.twinx()

        ax_regional.xaxis.set_visible(
            False
        )

        ax_regional.tick_params(
            axis='x',
            bottom=False,
            top=False,
            labelbottom=False,
            labeltop=False
        )

        ax_regional.tick_params(
            axis='y',
            left=False,
            labelleft=False,
            right=True,
            labelright=True
        )

        # --------------------------------------------------------
        # REGIONAL CALCULATIONS
        # --------------------------------------------------------

        for region_name, mask in (
            regional_masks.items()
        ):

            if not np.any(mask):

                print(
                    f'No latitude points available '
                    f'for {region_name} mean.'
                )

                continue

            region_values = (
                zonal_values[mask, :]
            )

            region_weights = (
                latitude_weights[mask]
            )

            valid = np.isfinite(
                region_values
            )

            weighted_values = np.where(
                valid,
                region_values
                * region_weights[:, None],
                0.0
            )

            weight_matrix = np.where(
                valid,
                region_weights[:, None],
                0.0
            )

            regional_mean = (
                np.sum(
                    weighted_values,
                    axis=0
                )
                /
                np.sum(
                    weight_matrix,
                    axis=0
                )
            )

            ax_regional.plot(
                np.arange(
                    len(regional_mean)
                ),
                regional_mean,
                linewidth=7,
                color='white',
                zorder=20
            )

            ax_regional.plot(
                np.arange(
                    len(regional_mean)
                ),
                regional_mean,
                linewidth=4,
                color=region_colors[
                    region_name
                ],
                label=region_name,
                zorder=21
            )

            print(
                f'{region_name} monthly mean:'
            )

            print(
                np.array2string(
                    regional_mean,
                    precision=6
                )
            )

        # --------------------------------------------------------
        # REGIONAL AXIS
        # --------------------------------------------------------

        ax_regional.set_xlim(
            -0.5,
            num_layers - 0.5
        )

        ax_regional.set_ylim(
            0.0,
            0.1
        )

        ax_regional.tick_params(
            axis='y',
            direction='in',
            labelsize=22
        )

        ax_regional.set_ylabel(
            dataOPS.cleanup_exponents(
                k_unit
            ),
            fontsize=22
        )

        ax_regional.spines[
            'top'
        ].set_visible(
            False
        )

        # ========================================================
        # RIGHT PANEL
        # ========================================================

        if is_rate:

            integ_values_cumsum = (
                1e-9
                *
                integ_values_cumsum
            )

            right_colorbar_min = 0.0
            right_colorbar_max = 9e9

            norm = mcolors.Normalize(
                vmin=right_colorbar_min,
                vmax=right_colorbar_max
            )

            rgba_cmap = plt.get_cmap(
                'jet'
            )

            rgba_colors = rgba_cmap(
                norm(
                    integ_values_cumsum
                )
            )

            rgba_colors[..., -1] = np.clip(
                norm(
                    integ_values_cumsum
                ),
                0.0,
                1.0
            )

            X, Y = np.meshgrid(
                np.arange(
                    integ_values_cumsum.shape[1]
                ),
                lats_plot
            )

            ax3.pcolormesh(
                X,
                Y,
                rgba_colors,
                shading='auto'
            )

            ax3.set_facecolor(
                land_color
            )

            # ----------------------------------------------------
            # TITLE
            # ----------------------------------------------------

            ax3.set_title(
                r'$\mathbf{Monthly\ cumulative}$'
                + '\n'
                + 'zonal (fill) and regional cumulative means (lines)',
                loc='left',
                fontsize=26,
                pad=14
            )

            ax3.set_ylabel(
                ' ',
                fontsize=26
            )

            ax3.set_xlabel(
                'Month',
                fontsize=26,
                labelpad=20
            )

            # ----------------------------------------------------
            # RIGHT X AXIS
            # ----------------------------------------------------

            ax3.set_xlim(
                -0.5,
                len(months) - 0.5
            )

            ax3.set_xticks(
                month_positions
            )

            ax3.set_xticklabels(
                months
            )

            ax3.tick_params(
                axis='x',
                which='major',
                bottom=True,
                top=False,
                labelbottom=True,
                labeltop=False,
                pad=8,
                length=14,
                labelsize=20
            )

            # ----------------------------------------------------
            # RIGHT Y AXIS
            # ----------------------------------------------------

            ax3.set_ylim(
                ymin,
                ymax
            )

            ax3.set_yticks(
                yticks
            )

            ax3.yaxis.set_major_formatter(
                latitude_formatter
            )

            ax3.tick_params(
                axis='y',
                which='major',
                left=True,
                labelleft=True,
                right=False,
                labelright=False,
                labelsize=24,
                direction='out',
                length=10,
                width=1.5
            )

            ax3.spines[
                'top'
            ].set_visible(
                False
            )

            ax3.spines[
                'right'
            ].set_visible(
                False
            )

            # ====================================================
            # RIGHT COLOURBAR
            # ====================================================

            cb_ax3.set_facecolor(
                land_color
            )

            cb_ax3.add_patch(
                Rectangle(
                    (0, 0),
                    1,
                    1,
                    transform=cb_ax3.transAxes,
                    color=land_color,
                    zorder=0,
                    alpha=1
                )
            )

            N = 256

            colors2 = rgba_cmap(
                np.linspace(
                    0,
                    1,
                    N
                )
            )

            colors2[:, -1] = np.linspace(
                0,
                1,
                N
            )

            alpha_cmap = (
                mcolors.ListedColormap(
                    colors2
                )
            )

            sm = cm.ScalarMappable(
                cmap=alpha_cmap,
                norm=norm
            )

            sm.set_array(
                rgba_colors
            )

            cb3 = plt.colorbar(
                sm,
                cax=cb_ax3
            )

            cb3.ax.tick_params(
                labelsize=22
            )

            cb3.set_label(
                'Tg / lat bin',
                fontsize=22
            )

            cb3.ax.yaxis.get_offset_text().set_fontsize(
                14
            )

            # ====================================================
            # REGIONAL CUMULATIVE CURVES
            # ====================================================

            ax_zonal_intg = ax3.twinx()

            ax_zonal_intg.xaxis.set_visible(
                False
            )

            ax_zonal_intg.tick_params(
                axis='x',
                bottom=False,
                top=False,
                labelbottom=False,
                labeltop=False
            )

            ax_zonal_intg.tick_params(
                axis='y',
                left=False,
                labelleft=False,
                right=True,
                labelright=True
            )

            regions = {

                'Global': np.ones(
                    len(lats_plot),
                    dtype=bool
                ),

                'Tropical': (
                    (lats_plot >= -36)
                    &
                    (lats_plot <= 36)
                ),

                'Extratropical': (
                    (lats_plot < -36)
                    |
                    (lats_plot > 36)
                )
            }

            region_colors = {

                'Global': 'black',
                'Tropical': 'red',
                'Extratropical': 'blue'
            }

            for name, mask in regions.items():

                if not np.any(mask):
                    continue

                curve = (
                    1e-9
                    *
                    np.nansum(
                        integ_values_cumsum[
                            mask,
                            :
                        ],
                        axis=0
                    )
                )

                ax_zonal_intg.plot(
                    curve,
                    linewidth=6,
                    color='white',
                    zorder=20
                )

                ax_zonal_intg.plot(
                    curve,
                    linewidth=4,
                    color=region_colors[name],
                    label=name,
                    zorder=21
                )

                print(
                    f'{name} year-end cumulative '
                    f'(Tg): {curve[-1]:.6g}'
                )

            # ----------------------------------------------------
            # CUMULATIVE REGIONAL AXIS
            # ----------------------------------------------------

            ax_zonal_intg.set_ylim(
                0.0,
                300.0
            )

            ax_zonal_intg.tick_params(
                axis='y',
                left=False,
                labelleft=False,
                right=True,
                labelright=True,
                direction='in',
                labelsize=24
            )

            ax_zonal_intg.yaxis.get_offset_text().set_fontsize(
                24
            )

            ax_zonal_intg.set_ylabel(
                dataOPS.cleanup_exponents(
                    'Tg'
                ),
                fontsize=22
            )

            ax_zonal_intg.spines[
                'top'
            ].set_visible(
                False
            )

            # ----------------------------------------------------
            # LEGEND
            # ----------------------------------------------------

            ax_zonal_intg.legend(
                fontsize=18,
                frameon=False,
                loc='upper left'
            )

            # ====================================================
            # FINAL RIGHT PANEL AXIS RESTORATION
            # ====================================================

            ax3.xaxis.set_visible(
                True
            )

            ax3.set_xlim(
                -0.5,
                len(months) - 0.5
            )

            ax3.set_xticks(
                month_positions
            )

            ax3.set_xticklabels(
                months
            )

            ax3.tick_params(
                axis='x',
                which='major',
                bottom=True,
                top=False,
                labelbottom=True,
                labeltop=False,
                length=14,
                width=1.5,
                pad=8,
                labelsize=20
            )

            # ====================================================
            # FORCE RIGHT MONTH LABEL FONT
            # ====================================================

            for tick in ax3.xaxis.get_major_ticks():

                tick.label1.set_visible(
                    True
                )

                tick.label1.set_fontfamily(
                    'DejaVu Sans'
                )

                tick.label1.set_fontstyle(
                    'italic'
                )

                tick.label1.set_fontweight(
                    'normal'
                )

                tick.label1.set_fontsize(
                    20
                )

                tick.label1.set_color(
                    'black'
                )

                tick.label1.set_rotation(
                    0
                )

                tick.label1.set_horizontalalignment(
                    'center'
                )

                tick.label1.set_verticalalignment(
                    'top'
                )

            # ====================================================
            # FINAL RIGHT Y AXIS RESTORATION
            # ====================================================

            ax3.tick_params(
                axis='y',
                which='major',
                left=True,
                labelleft=True,
                right=False,
                labelright=False,
                labelsize=24
            )

            ax3.set_yticks(
                yticks
            )

            ax3.yaxis.set_major_formatter(
                latitude_formatter
            )

        # ========================================================
        # FINAL LEFT MONTH LABEL FONT
        #
        # This is deliberately done at the END too, so both
        # panels are guaranteed to have identical formatting.
        # ========================================================

        ax1.xaxis.set_visible(
            True
        )

        ax1.set_xlim(
            -0.5,
            len(months) - 0.5
        )

        ax1.set_xticks(
            month_positions
        )

        ax1.set_xticklabels(
            months
        )

        ax1.tick_params(
            axis='x',
            which='major',
            bottom=True,
            top=False,
            labelbottom=True,
            labeltop=False,
            length=14,
            width=1.5,
            pad=8,
            labelsize=20
        )

        for tick in ax1.xaxis.get_major_ticks():

            tick.label1.set_visible(
                True
            )

            tick.label1.set_fontfamily(
                'DejaVu Sans'
            )

            tick.label1.set_fontstyle(
                'italic'
            )

            tick.label1.set_fontweight(
                'normal'
            )

            tick.label1.set_fontsize(
                20
            )

            tick.label1.set_color(
                'black'
            )

            tick.label1.set_rotation(
                0
            )

            tick.label1.set_horizontalalignment(
                'center'
            )

            tick.label1.set_verticalalignment(
                'top'
            )

        # ========================================================
        # FINAL LAYOUT
        # ========================================================

        if is_rate:

            fig.subplots_adjust(
                left=0.035,
                right=0.98,
                bottom=0.16,
                top=0.84
            )

        else:

            fig.subplots_adjust(
                left=0.10,
                right=0.93,
                bottom=0.16,
                top=0.84
            )

        # ========================================================
        # SAVE
        # ========================================================

        output_file = os.path.join(
            unique_end_directory,
            'complete_zonalmeans.png'
        )

        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.15
        )

        print(
            'Saved to:',
            output_file
        )

        plt.close()
