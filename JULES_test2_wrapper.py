from scipy.interpolate import interp1d
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
from matplotlib import colormaps
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import JULES_test2
import re

def natural_key(s):
    return [int(part) if part.isdigit() else part
            for part in re.split(r'(\d+)', s)]

root_path = '/Users/jae35/Desktop/JULES_test_data/'

folder = 'sp1'

folder_path = os.path.join(root_path, folder)

subfolders = [
    os.path.join(folder_path, name + '/')
    for name in os.listdir(folder_path)
    if os.path.isdir(os.path.join(folder_path, name))
]

subfolders = sorted(subfolders, key=natural_key)

file_name = 'CRUJRA2.4_2023_n96_v8.0_S3.ilamb.2022.nc'

year = 2022

for subfolder in subfolders:

    JULES_test2.process_workflow(subfolder, file_name, year)




