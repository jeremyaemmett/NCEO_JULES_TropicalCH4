from scipy.interpolate import interp1d
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
from matplotlib import colormaps
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import JULES_test2

root_path = '/Users/jae35/Desktop/JULES_test_data/'

folder = 'sp2'

folder_path = os.path.join(root_path, folder)

subfolders = [
    os.path.join(folder_path, name + '/')
    for name in os.listdir(folder_path)
    if os.path.isdir(os.path.join(folder_path, name))
]

for subfolder in subfolders:

    JULES_test2.process_workflow(subfolder)




