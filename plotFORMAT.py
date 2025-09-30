import matplotlib.pyplot as plt
import numpy as np
import miscOPS


def tseries_axes(plot_title, y_units, tseries_values, plot_margin):

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_title(plot_title, loc='left')
    ax.set_xticks(range(12))
    ax.set_xlim([0, 11])
    ax.set_ylim([np.min(tseries_values) - plot_margin, np.max(tseries_values) + plot_margin])
    ax.set_xticklabels(['JanFebMarAprMayJunJulAugSepOctNovDec'[j*3:j*3+3] for j in range(12)], fontsize=12)
    ax.set_ylabel(miscOPS.cleanup_exponents(y_units), fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_facecolor('gainsboro')
    ax.grid(True)

    return fig, ax