from scipy.interpolate import interp1d
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
from matplotlib import colormaps
import matplotlib.pyplot as plt
import processJULES
import pandas as pd
import numpy as np
import plotTSERIES
import plotPARAMS
import plotMAPS_1D
import plotMAPS_1D_2
import plotZONAL_1D
import plotZONAL_1D_2
import plotZONAL
import plotMAPS
import sysOPS

# JULES output file path/name
#data_path, outp_path, file_name = plotPARAMS.data_path, plotPARAMS.outp_path, plotPARAMS.file_name

# Variable(s) and year to map
#variable_names, year = plotPARAMS.variable_names, plotPARAMS.year

def process_workflow(data_path, file_name, year):

    print(' ')
    print(data_path + file_name)

    outp_path = data_path + 'plots/global/'
    print(' ')
    print('     Making scaled maps...')
    plotMAPS_1D_2.make_maps(data_path, outp_path, file_name, year, stack_longitude_panels=True, apply_scale_factor=True, latitude_bounds=None)
    print(' ')
    print('     Making scaled zonal plots...')
    plotZONAL_1D_2.make_zonal(data_path, outp_path, file_name, year, apply_scale_factor=True)

    outp_path = data_path + 'plots/band/'
    print(' ')
    print('     Making scaled maps...')
    #plotMAPS_1D_2.make_maps(data_path, outp_path, file_name, year, stack_longitude_panels=True, apply_scale_factor=True, latitude_bounds=(-36,36))
    print(' ')
    print('     Making scaled zonal plots...')
    #plotZONAL_1D_2.make_zonal(data_path, outp_path, file_name, year, apply_scale_factor=True)

    outp_path = data_path + 'plots/global/'
    print(' ')
    print('     Making unscaled maps...')
    plotMAPS_1D_2.make_maps(data_path, outp_path, file_name, year, stack_longitude_panels=True, apply_scale_factor=False, latitude_bounds=None)
    print(' ')
    print('     Making unscaled zonal plots...')
    plotZONAL_1D_2.make_zonal(data_path, outp_path, file_name, year, apply_scale_factor=False)

    outp_path = data_path + 'plots/band/'
    print(' ')
    print('     Making unscaled maps...')
    #plotMAPS_1D.make_maps(data_path, outp_path, file_name, year, stack_longitude_panels=True, apply_scale_factor=False, latitude_bounds=(-36,36))
    print(' ')
    print('     Making unscaled zonal plots...')
    #plotZONAL_1D.make_zonal(data_path, outp_path, file_name, year, apply_scale_factor=False)

    #print(' ')
    #print('     Making animated map...')
    #print(' ')
    #plotTSERIES.make_tseries()
    ##plotMAPS_1D.make_animated_maps(data_path, outp_path, file_name, year)
    #plotZONAL.make_animated_zonal()
    #plotTSERIES.make_animated_tseries()

    gif_stuff = False
    if gif_stuff: 
        gif1 = '/Users/jae35/Documents/nceo/output/t_soil/(3)1p0-2p0m/map_animation.gif'
        gif2 = '/Users/jae35/Documents/nceo/output/t_soil/(3)1p0-2p0m/arealmean_tseries_animation.gif'
        sysOPS.combine_gifs_on_canvas(gif1, gif2, plotPARAMS.outp_path + '/test.gif', (4000, 3500), (120, 1200), (0, 0))

        gif1 = '/Users/jae35/Documents/nceo/test.gif'
        gif2 = '/Users/jae35/Documents/nceo/output/t_soil/(3)1p0-2p0m/zonal_animation.gif'
        sysOPS.combine_gifs_on_canvas(gif1, gif2, plotPARAMS.outp_path + '/test3.gif', (7000, 3500), (0, 0), (2600, 1110))

