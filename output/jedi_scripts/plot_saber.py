import sys
import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature

# --- Usage: python plot_saber.py yourfile.nc variable_name level ---

# List of allowed variable names
allowed_variables = [
    "eastward_wind",
    "northward_wind",
    "air_potential_temperature",
    "dry_air_density_levels_minus_one",
    "cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water",
    "cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water",
    "dimensionless_exner_function_levels_minus_one",
    "water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water"
]

# Parse command-line arguments
if len(sys.argv) != 4:
    print("Usage: python plot_saber.py <filename.nc> <variable_name> <level>")
    print("       <variable_name> must be one of:")
    for var in allowed_variables:
        print(f"         - {var}")
    print("       <level> must be an integer between 1 and 70 (inclusive).")
    sys.exit(1)

filename = sys.argv[1]
varname = sys.argv[2]

# Check if variable is allowed
if varname not in allowed_variables:
    print(f"Error: '{varname}' is not a valid variable name.")
    print("       Choose from:")
    for var in allowed_variables:
        print(f"         - {var}")
    sys.exit(1)

try:
    level = int(sys.argv[3])
    if not (1 <= level <= 70):
        raise ValueError
except ValueError:
    print("Error: <level> must be an integer between 1 and 70 (inclusive).")
    sys.exit(1)

# Open NetCDF file
ds = nc.Dataset(filename)

# Extract variable
if varname not in ds.variables:
    print(f"Variable '{varname}' not found in {filename}")
    sys.exit(1)

var = ds.variables[varname][:]
var_level = var[level-1, :, :]

# Squeeze singleton dimensions for 2D plotting
data = np.squeeze(var)

# Get coordinates if available
lon = ds.variables['lon'][:]
lat = ds.variables['lat'][:]

# Normalize longitudes to [-180, 180] to prevent discontinuity at 0°
lon_wrapped = np.where(lon > 180, lon - 360, lon)

vmin = np.nanmin(var_level)
vmax = np.nanmax(var_level)
maximum = max(vmin, vmax)

# Create plot
plt.figure(figsize=(7, 3.5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([lon_wrapped.min(), lon_wrapped.max(), lat.min(), lat.max()], crs=ccrs.PlateCarree())
ax.coastlines()

# Use pcolormesh for robust plotting of gridded data
cf = ax.pcolormesh(lon_wrapped, lat, var_level,
    cmap='RdBu_r',
    vmin=-maximum,
    vmax=maximum,
    shading='auto',
    transform=ccrs.PlateCarree()
)

# Add colorbar
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.05, aspect=50, extend='both')
cbar.set_label(varname)

# Add title
plt.title(f'{varname} at vertical level {level}')
plt.tight_layout()
plt.savefig(f'figure_{varname}.png', dpi=150, bbox_inches='tight')