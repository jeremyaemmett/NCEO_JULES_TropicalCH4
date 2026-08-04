import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import readJULES
import dataOPS
from os import listdir
from os.path import join, isdir

mode = 'ten_year' # single_year

file_path_test = (
    "/Users/jae35/Desktop/alice_output/GSWP3-W5E5_OBSCLIM/"
    "isimip3a_notriffid_gswp3-w5e5_obsclim_historical.gen_mon.1980.nc"
)
#file_directory = '/Users/jae35/Desktop/JULES_test_data/sp1/JASMIN_output_u-dk105_3_sp1'
outer_directory = '/Users/jae35/Desktop/JULES_test_data/sp2/'

def infer_res(coord):
    u = np.unique(np.round(np.asarray(coord).ravel(), 6))
    d = np.diff(np.sort(u))
    return float(np.median(d[d > 1e-6]))


def total_flux(file_path):

    # Constants
    C_TO_CH4 = 16.043 / 12.011
    R_EARTH = 6.371e6

    # Read file
    ds = xr.open_dataset(file_path)

    # Array of month durations from file calendar [sec]
    sec_per_month = (ds["time"].dt.days_in_month.values.astype(float) * 86400.0)

    # Timestamps of monthly means (first day of next calendar month)
    times, _, _, _ = readJULES.read_jules_m2(file_path, "time")
    times = dataOPS.ensure_np_datetime(times)

    header = readJULES.read_jules_header(file_path)
    dimension_keys = list(header[0])
    variable_keys = list(header[1])

    if "latitude" in variable_keys and "longitude" in variable_keys:
        lat_name, lon_name = "latitude", "longitude"
    elif "lat" in variable_keys and "lon" in variable_keys:
        lat_name, lon_name = "lat", "lon"
    else:
        raise ValueError("Could not find latitude/longitude variables")

    # Read `fch4_wetl` (stored in 10⁻⁹ kg m⁻² s⁻¹, a carbon mass flux)
    flux, _, _, _ = readJULES.read_jules_m2(file_path, "fch4_wetl")
    lat, _, _, _ = readJULES.read_jules_m2(file_path, lat_name)
    lon, _, _, _ = readJULES.read_jules_m2(file_path, lon_name)

    # Multiply by `1e-9` to get physical kg C m⁻² s⁻¹.
    flux = np.asarray(flux, dtype=float) * 1e-9
    flux = flux.reshape(flux.shape[0], -1) # time x land

    # Cell area from grid spacing
    lat = np.asarray(lat).ravel()
    lon = np.asarray(lon).ravel()
    dlat = infer_res(lat)
    dlon = infer_res(lon)
    area = ((R_EARTH * np.deg2rad(dlat))*(R_EARTH * np.deg2rad(dlon)* np.cos(np.deg2rad(lat))))

    # kg C m-2 yr-1
    emission = np.nansum(flux * sec_per_month[:, None], axis=0)

    # kg C yr-1
    total_kg_C = np.nansum(emission * area)

    # Tg C yr-1
    total_Tg_C = total_kg_C / 1e9

    # Tg CH4 yr-1
    total_Tg_CH4 = total_Tg_C * C_TO_CH4

    return total_Tg_CH4 

if mode == 'ten_year':

    for subdir in sorted(listdir(outer_directory)):

        file_directory = join(outer_directory, subdir)

        # Skip .DS_Store and any other non-directories
        if not isdir(file_directory):
            continue

        directory_files = sorted(f for f in listdir(file_directory) if f.endswith(".nc"))
        files_2000_2009 = [f"{file_directory}/{f}" for f in directory_files if 2000 <= int(f.split(".")[-2]) <= 2009]

        totals = []
        for file_path in files_2000_2009:
            
            # Calculate total annual fch4_wetl emission [Tg CH4 yr-1]
            total = total_flux(file_path)
            totals.append(total)
            #print(' ')
            #print(file_path)
            #print(f"Global annual total = {total:.2f} Tg CH4 yr-1")

        mean_total = np.mean(totals)
        scale_factor = 180.0 / mean_total

        print(
            f"{file_directory.split('/')[-1]} 2000-2009 Mean: "
            f"{mean_total:.2f}  Scale Factor: {scale_factor:.6f}"
        )

        # Write scale factor to a text file
        output_file = f"{file_directory}/scale_factor.txt"
        with open(output_file, "w") as f:
            f.write(f"{scale_factor}\n")

        print(f"Scale factor written to {output_file}")

if mode == 'test_year':

    # Calculate total annual fch4_wetl emission [Tg CH4 yr-1]
    totals = []
    total = total_flux(file_path_test)
    totals.append(total)
    print(' ')
    print(file_path_test)
    print(f"Global annual total = {total:.2f} Tg CH4 yr-1")

def flux_map(flxs, lats, lons):

    annual_mean = np.nanmean(flxs * 1e-9, axis=0)

    # kg C m-2 s-1 -> mg C m-2 day-1
    mg_day = annual_mean * 1e6 * 86400.0

    lat_plot = np.asarray(lats).ravel()
    lon_plot = np.asarray(lons).ravel()

    plt.figure(figsize=(8, 6))

    sc = plt.scatter(lon_plot, lat_plot, c=mg_day, s=8, marker="s",
        cmap="viridis", vmin=0, vmax=np.nanpercentile(mg_day, 99))

    plt.gca().set_aspect("equal")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.title("JULES wetland CH$_4$ flux\n"
        f"{file_path.split('/')[-1]}\n"
        f"Total = {total:.2f} Tg CH$_4$ yr$^{{-1}}$")

    cb = plt.colorbar(sc)
    cb.set_label("mg C m$^{-2}$ day$^{-1}$")

    plt.tight_layout()
    plt.show()