import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

import readJULES
import dataOPS


# ======================================================================
# USER INPUT
# ======================================================================

file_path = (
    "/Users/jae35/Desktop/alice_output/GSWP3-W5E5_OBSCLIM/"
    "isimip3a_notriffid_gswp3-w5e5_obsclim_historical.gen_mon.1980.nc"
)

C_TO_CH4 = 16.043 / 12.011


# ======================================================================
# CONSTANTS
# ======================================================================

R_EARTH = 6.371e6


# ======================================================================
# FUNCTIONS
# ======================================================================

def infer_res(coord):
    u = np.unique(np.round(np.asarray(coord).ravel(), 6))
    d = np.diff(np.sort(u))
    return float(np.median(d[d > 1e-6]))



def total_flux(flux, sec_per_month, lat, lon):
    """
    Total annual fch4_wetl emission.

    Input:
        flux:
            JULES fch4_wetl
            units: 1e-9 kg C m-2 s-1

    Output:
        Tg CH4 yr-1
    """

    # convert storage units
    # (1b) Multiply by `1e-9` to get physical kg C m⁻² s⁻¹.
    flux = np.asarray(flux, dtype=float) * 1e-9

    # time x land
    flux = flux.reshape(flux.shape[0], -1)

    lat = np.asarray(lat).ravel()
    lon = np.asarray(lon).ravel()


    # cell dimensions
    dlat = infer_res(lat)
    dlon = infer_res(lon)


    # cell area
    area = (
        (R_EARTH * np.deg2rad(dlat))
        *
        (R_EARTH * np.deg2rad(dlon)
         * np.cos(np.deg2rad(lat)))
    )


    # kg C m-2 yr-1
    emission = np.nansum(
        flux * sec_per_month[:, None],
        axis=0
    )


    # kg C yr-1
    total_kg_C = np.nansum(
        emission * area
    )


    # Tg C yr-1
    total_Tg_C = total_kg_C / 1e9


    # Tg CH4 yr-1
    return total_Tg_C * C_TO_CH4



# ======================================================================
# READ FILE
# ======================================================================

print("Reading:")
print(file_path)


ds = xr.open_dataset(file_path)


# month duration from file calendar
sec_per_month = (
    ds["time"].dt.days_in_month.values.astype(float)
    * 86400.0
)



times, _, _, _ = readJULES.read_jules_m2(
    file_path,
    "time"
)

times = dataOPS.ensure_np_datetime(times)



header = readJULES.read_jules_header(file_path)

dimension_keys = list(header[0])
variable_keys = list(header[1])


if "latitude" in variable_keys and "longitude" in variable_keys:
    lat_name = "latitude"
    lon_name = "longitude"

elif "lat" in variable_keys and "lon" in variable_keys:
    lat_name = "lat"
    lon_name = "lon"

else:
    raise ValueError(
        "Could not find latitude/longitude variables"
    )



# read fields

# (1a) **Read** `fch4_wetl` (stored in 10⁻⁹ kg m⁻² s⁻¹, a **carbon**-mass flux)
flxs, _, _, _ = readJULES.read_jules_m2(
    file_path,
    "fch4_wetl"
)

lats, _, _, _ = readJULES.read_jules_m2(
    file_path,
    lat_name
)

lons, _, _, _ = readJULES.read_jules_m2(
    file_path,
    lon_name
)



# ======================================================================
# CALCULATE TOTAL
# ======================================================================

total = total_flux(
    flxs,
    sec_per_month,
    lats,
    lons
)


print()
print(
    f"Global annual total = {total:.2f} Tg CH4 yr-1"
)



# ======================================================================
# AFRICA FLUX MAP
# ======================================================================

annual_mean = np.nanmean(
    flxs * 1e-9,
    axis=0
)


# kg C m-2 s-1 -> mg C m-2 day-1
mg_day = annual_mean * 1e6 * 86400.0


lat_plot = np.asarray(lats).ravel()
lon_plot = np.asarray(lons).ravel()


plt.figure(figsize=(8, 6))

sc = plt.scatter(
    lon_plot,
    lat_plot,
    c=mg_day,
    s=8,
    marker="s",
    cmap="viridis",
    vmin=0,
    vmax=np.nanpercentile(mg_day, 99)
)

plt.gca().set_aspect("equal")

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.title(
    "JULES wetland CH$_4$ flux\n"
    f"{file_path.split('/')[-1]}\n"
    f"Total = {total:.2f} Tg CH$_4$ yr$^{{-1}}$"
)


cb = plt.colorbar(sc)
cb.set_label(
    "mg C m$^{-2}$ day$^{-1}$"
)

plt.tight_layout()
plt.show()