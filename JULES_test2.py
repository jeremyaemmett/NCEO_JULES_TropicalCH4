from scipy.interpolate import interp1d
from matplotlib import colormaps
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotTSERIES
import plotPARAMS
import plotZONAL
import plotMAPS
import sysOPS

# JULES output file path/name
data_path, outp_path, file_name = plotPARAMS.data_path, plotPARAMS.outp_path, plotPARAMS.file_name

# Variable(s) and year to map
variable_names, year = plotPARAMS.variable_names, plotPARAMS.year

plotZONAL.make_zonal()

stop

plotMAPS.make_maps()
plotTSERIES.make_tseries()
plotMAPS.make_animated_maps()
plotTSERIES.make_animated_tseries()

gif1 = '/Users/jae35/Documents/nceo/output/fch4_wetl/map_animation.gif'
gif2 = '/Users/jae35/Documents/nceo/output/fch4_wetl/tseries_animation.gif'
sysOPS.combine_gifs_on_canvas(gif1, gif2, plotPARAMS.outp_path + '/test.gif', (4000, 3500), (120, 1200), (0, 0))

