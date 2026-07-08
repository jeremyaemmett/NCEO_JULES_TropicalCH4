import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import sys

def geodesic_circle_clipped(ref_lat, ref_lon, radius_km, lat_bounds, lon_bounds, n_points=180):
    """
    Generate a clipped circle (arc) around (ref_lat, ref_lon) with given radius (in km),
    keeping only points within lat/lon bounds.
    """
    R = 6371.0  # Earth radius in km
    bearings = np.linspace(0, 2 * np.pi, n_points)
    lat_min, lat_max = lat_bounds
    lon_min, lon_max = lon_bounds

    lat1 = np.radians(ref_lat)
    lon1 = np.radians(ref_lon)
    d_by_r = radius_km / R

    arc_lats, arc_lons = [], []
    for theta in bearings:
        lat2 = np.arcsin(np.sin(lat1) * np.cos(d_by_r) +
                         np.cos(lat1) * np.sin(d_by_r) * np.cos(theta))
        lon2 = lon1 + np.arctan2(np.sin(theta) * np.sin(d_by_r) * np.cos(lat1),
                                 np.cos(d_by_r) - np.sin(lat1) * np.sin(lat2))
        lat_deg = np.degrees(lat2)
        lon_deg = np.degrees(lon2)

        if (lat_min <= lat_deg <= lat_max) and (lon_min <= lon_deg <= lon_max):
            arc_lats.append(lat_deg)
            arc_lons.append(lon_deg)

    return arc_lats, arc_lons

# --- Usage: python plot_ensemble_covariance.py variable_name ensemble_size radius_m ---

# Allowed variable names and their labels
variable_labels = {
    "x": "Streamfunction",
    "q": "Potential vorticity",
    "u": "Eastward wind",
    "v": "Northward wind"
}

# Parse command-line arguments
if len(sys.argv) != 4:
    print("Usage: python plot_ensemble_covariance.py <variable_name> <ensemble_size> <radius_m>")
    print("       <variable_name> must be one of:", ", ".join(variable_labels.keys()))
    print("       <ensemble_size> must be from 2 to 100")
    print("       <radius_m> localization radius (try 5e6)")
    sys.exit(1)

variable = sys.argv[1]

if variable not in variable_labels:
    print(f"Error: variable_name '{variable}' is not valid.")
    print(f"       Choose from: {', '.join(variable_labels.keys())}")
    sys.exit(1)

try:
    n_members = int(sys.argv[2])
    if not (2 <= n_members <= 100):
        raise ValueError
except ValueError:
    print("Error: <ensemble_size> must be an integer between 2 and 100.")
    sys.exit(1)

# file_template = "Data/forecast.ens.{}.2009-12-31T00:00:00Z.P1DT12H.nc"
file_template = "Data/forecast.{}.fc.2010-01-01T06:00:00Z.PT12H.nc"

z_coord = Dataset(file_template.format(1)).variables["z"][:]
lon_coord = Dataset(file_template.format(1)).variables["lon"][:]
lat_coord = Dataset(file_template.format(1)).variables["lat"][:]

nlevel = len(z_coord)
nlat = lat_coord.shape[0]
nlon = lon_coord.shape[1]

ensemble_data = []

for i in range(1, n_members + 1):
    file_path = file_template.format(i)
    try:
        with Dataset(file_path, 'r') as nc:
            var_data = nc.variables[variable][:]            
            ensemble_data.append(var_data)
    
    except FileNotFoundError:
        print(f"Warning: File not found - {file_path}")

# Stack into a NumPy array of shape (n_members, level, lat, lon)
ensemble_array = np.stack(ensemble_data)

# print("Ensemble shape:", ensemble_array.shape)
# print("Latitude shape:", lat_coord.shape)
# print("Longitude shape:", lon_coord.shape)

# Select a model grid point (index-based)
ref_ilevel = 0
ref_ilat = 10            
ref_ilon = 20  

# Compute ensemble mean
mean_ensemble = np.mean(ensemble_array, axis=0)  # shape: (nlevel, nlat, nlon)

# Compute ensemble perturbation
X_prime = ensemble_array - mean_ensemble

correlation_fields = np.zeros((nlevel, nlat, nlon))

ref = X_prime[:, ref_ilevel, ref_ilat, ref_ilon]
ref_std = np.std(ref, ddof=1)

for ilevel in range(nlevel):
    for ilat in range(nlat):
        for ilon in range(nlon):
            target = X_prime[:, ilevel, ilat, ilon]
            target_std = np.std(target, ddof=1)
            correlation_fields[ilevel, ilat, ilon] = (
                (ref @ target) / (n_members - 1)
            ) / (ref_std * target_std)
            
# Plotting
plot_width=7 #units in inches
plot_height=3.5 #units in inches

fig, axs = plt.subplots(2, 1, figsize=(plot_width, plot_height), constrained_layout=True)

# Find global min/max for consistent colorbar scaling
vmin = np.min(correlation_fields)
vmax = np.max(correlation_fields)
scope = max([abs(vmin), abs(vmax)])

# Plot level 0
cs = axs[1].contourf(lon_coord, lat_coord, correlation_fields[0, :, :],
                     vmin=-scope, vmax=scope, cmap='coolwarm')
axs[1].plot(lon_coord[ref_ilat, ref_ilon], lat_coord[ref_ilat, ref_ilon], marker='x', color='black', markersize=8)
axs[1].set_ylabel(f'Altitude {int(z_coord[0])}m')

# Plot level 1
axs[0].contourf(lon_coord, lat_coord, correlation_fields[1, :, :],
                vmin=-scope, vmax=scope, cmap='coolwarm')
axs[0].set_ylabel(f'Altitude {int(z_coord[1])}m')

# Visulise domain localization
arc_lats, arc_lons = geodesic_circle_clipped(
    lat_coord[ref_ilat, ref_ilon], 
    lon_coord[ref_ilat, ref_ilon], 
    float(sys.argv[3])/1000,
    lat_bounds=(np.min(lat_coord), np.max(lat_coord)),
    lon_bounds=(np.min(lon_coord), np.max(lon_coord))
)

axs[0].plot(arc_lons, arc_lats, linestyle='--', color='black', linewidth=1)
axs[1].plot(arc_lons, arc_lats, linestyle='--', color='black', linewidth=1)

# Add a single colorbar for all subplots
cbar = fig.colorbar(cs, ax=axs, orientation='vertical', fraction=0.02, pad=0.04)
cbar.set_label("Correlation")

# Add a single title for all subplots
fig.suptitle(f"{variable_labels[variable]} error correlation ($N={n_members}$)", fontsize=14)

# Save to file
plt.savefig("correlation_fields.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved: correlation_fields.png")