#!/bin/bash
# Description: Plot output of LETKF experiments

# Show arguments of plot.py
# python plot.py qg –h

# Observation file
OBS_FILE="truth.obs4d_12h_global.nc"
# OBS_FILE="truth.obs4d_12h_north.nc"
# OBS_FILE="truth.obs4d_12h_south.nc"

# Truth field 
TRUTH_FILE="Data/truth.fc.2009-12-15T00:00:00Z.P17DT12H.nc" 

# Analysis file
ANALYSIS_FILE="output/letkf.end.000000.an.2010-01-01T12:00:00Z.nc"

# Plot the turth field
python plot.py qg fields --plotwind $TRUTH_FILE

# Plot analysis error and observation locations in spatial space
python plot.py qg fields --output qg_analysis_error \
    $ANALYSIS_FILE \
    $TRUTH_FILE \
    --plotObsLocations Data/$OBS_FILE \
    --title "Analysis error & Obs locations"

# Copy the observation file values from the NetCDF into a text file
python plot.py qg obs --output qg_obs Data/$OBS_FILE

# Plot mean increment and observation locations in spatial space
# python plot.py qg fields --output qg_increment \
#     $ANALYSIS_FILE \
#     output/prior.mean.fc.2010-01-01T12:00:00Z.PT0S.nc \
#     --plotObsLocations Data/$OBS_FILE \
#     --title "Mean increment & Obs locations"