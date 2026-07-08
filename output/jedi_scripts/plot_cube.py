"""Plotting a cubed sphere using matplotlib and cartopy

This example is based on specific netCDF data from LFric
model that has specific grid ordering.
"""
import itertools
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import cartopy.crs as ccrs # type: ignore
import numpy as np
import netCDF4

def treat_lon(x:list[float]) -> list[float]:
    """
    Treat the periodic longitude

    Parameters
    ----------
    x: list[float]
        longitude of the four corners of a quadrilateral


    Returns
    -------
    x: list[float]
        treated longitude of the four corners of a quadrilateral
    """
    if len(x) != 4:
        return x

    if np.abs(x[2] - x[1]) > 180:
        x[2] += 360
        x[3] += 360
    if np.abs(x[0] - x[1]) > 180:
        x[1] += 360
    if np.abs(x[2] - x[3]) > 180:
        x[2] += 360
    return x


def treat_pole(x:list[float], y:list[float]) -> tuple[list[float], list[float]]:
    """
    Avoid distorted cells near the pole when plotting

    Parameters
    ----------
    x, y: list[float]
        longitude and latitude of the four corners of a quadrilateral

    Returns
    -------
    x0, y0, x1, y1: float
        treated longitude and latitude of the two points
    """
    if len(x) != 4:
        return x, y
    if y[0] == 90: x[0], y[0] = 90, 88
    if y[1] == 90: x[1], y[1] = 90, 88
    if y[2] == 90: x[2], y[2] = 270, 88
    if y[3] == 90: x[3], y[3] = 270, 88

    if y[0] == -90: x[0], y[0] = 180, -88
    if y[1] == -90: x[1], y[1] = 180, -88
    if y[2] == -90: x[2], y[2] = 360, -88
    if y[3] == -90: x[3], y[3] = 0, -88
    return x, y


def generate_cell(x, y, value_array, quads, values):
    x_stacked = np.stack(x, axis=1)
    y_stacked = np.stack(y, axis=1)
    for x, y, val in zip(x_stacked, y_stacked, value_array):
        x = treat_lon(x)
        x, y = treat_pole(x, y)
        quads.append(list(zip(x, y)))
        values.append(val)
    return quads, values

# The following slices are based on hand-crafted indices
# it is not sure if they can be obtained algorithmically.

# array slices for each of the six cubed sphere faces
slices = [
    (slice(None, -1), slice(None, -1)),
    (slice(None, -1), slice(1, None)),
    (slice(1, None), slice(1, None)),
    (slice(1, None), slice(None, -1)),
]

# cells that connect the faces of the cubed sphere
def get_face_slices(n: int) -> list[list[tuple[int,  tuple[int | slice, int | slice]]]]:
    return [
    # faces at the boundaries between k0 and k1
    [
        (0, (n - 1, slice(0, -1))),
        (0, (n - 1, slice(1, None))),
        (1, (0, slice(1, None))),
        (1, (0, slice(0, -1))),
    ],
    # faces at the boundaries between k1 and k2
    [
        (1, (n - 1, slice(1, None))),
        (1, (n - 1, slice(0, -1))),
        (2, (slice(0, -1), n - 1)),
        (2, (slice(1 , None), n - 1)),
        ],
    # faces at the boundaries between k2 and k3
    [
        (2, (slice(0, -1), 0)),
        (2, (slice(1, None), 0)),
        (3, (slice(1 , None), n - 1)),
        (3, (slice(0, -1), n - 1)),
        ],
    # faces at the boundaries between k3 and k0
    [
        (3, (slice(0, -1), 0)),
        (3, (slice(1, None), 0)),
        (0, (0, slice(1 , None))),
        (0, (0, slice(0, -1))),
        ],
    # faces at the boundaries between k1 and k4
    [
        (1, (slice(0, -1), n - 1)),
        (4, (n - 1, slice(0, -1))),
        (4, (n - 1, slice(1 , None))),
        (1, (slice(1, None), n - 1)),
        ],
    # faces at the boundaries between k3 and k4
    [
        (3, (n - 1, slice(0, -1))),
        (4, (0, slice(0, -1))),
        (4, (0, slice(1 , None))),
        (3, (n - 1, slice(1, None))),
        ],
    # faces at the boundaries between k2 and k4
    [
        (2, (n - 1, slice(0, -1))),
        (4, (slice(0, -1), n - 1)),
        (4, (slice(1, None), n - 1)),
        (2, (n - 1, slice(1 , None))),
        ],
    # faces at the boundaries between k0 and k4
    [
        (0, (slice(0, -1), n - 1)),
        (4, (slice(0, -1), 0)),
        (4, (slice(1, None), 0)),
        (0, (slice(1, None), n - 1)),
        ],
    # fill the gap between k0, k1, and k4
    [
        (0, (n - 1, n - 1)),
        (4, (n - 1, 0)),
        (1, (0, n - 1)),
        ],
    # fill the gap between k1, k2, and k4
    [
        (1, (n - 1, n - 1)),
        (4, (n - 1, n - 1)),
        (2, (n - 1, n - 1)),
        ],
    # fill the gap between k2, k3, and k4
    [
        (2, (n - 1, 0)),
        (4, (0, n - 1)),
        (3, (n - 1, n - 1)),
        ],
    # fill the gap between k3, k0, and k4
    [
        (3, (n - 1, 0)),
        (4, (0, 0)),
        (0, (0, n - 1)),
    ],
    # faces at the boundaries between k0 and k5
    [
        (0, (slice(0, -1), 0)),
        (5, (0, slice(0, -1))),
        (5, (0, slice(1, None))),
        (0, (slice(1, None), 0)),
        ],
    # faces at the boundaries between k2 and k5
    [
        (2, (0, slice(0, -1))),
        (5, (n - 1, slice(0, -1))),
        (5, (n - 1, slice(1, None))),
        (2, (0, slice(1, None))),
        ],
    # faces at the boundaries between k1 and k5
    [
        (1, (slice(0, -1), 0)),
        (5, (slice(0, -1), n - 1)),
        (5, (slice(1, None), n - 1)),
        (1, (slice(1, None), 0)),
        ],
    # faces at the boundaries between k3 and k5
    [
        (3, (0, slice(0, -1))),
        (5, (slice(0, -1), 0)),
        (5, (slice(1, None), 0)),
        (3, (0, slice(1, None))),
        ],
    # fill the gap between k0, k1, and k5
    [
        (0, (n - 1, 0)),
        (5, (0, n - 1)),
        (1, (0, 0)),
        ],
    # fill the gap between k1, k2, and k5
    [
        (1, (n - 1, 0)),
        (5, (n - 1, n - 1)),
        (2, (0, n - 1)),
        ],
    # fill the gap between k2, k3, and k5
    [
        (2, (0, 0)),
        (5, (n - 1, 0)),
        (3, (0, n - 1)),
        ],
    # fill the gap between k3, k0, and k5
    [
        (3, (0, 0)),
        (5, (0, 0)),
        (0, (0, 0)),
        ],
]


if __name__ == "__main__":
    # read lat, lon and data
    with netCDF4.Dataset('dirac_spectralb_from_CS.nc', 'r') as f:
        lat = f['lat'][:]
        lon = f['lon'][:]
        data = f['eastward_wind'][:, 1] # 1st level
    # the cubed sphere is divided into 6 faces
    n = int(np.sqrt(len(lat)//6))

    face_slices = get_face_slices(n)

    lats_batch = list(itertools.batched(lat, len(lat)//6))
    lons_batch = list(itertools.batched(lon, len(lon)//6))
    data_batch = list(itertools.batched(data, len(data)//6))
    # Reshape to 2D arrays (assuming column-major order!)
    lats = [np.array(lat).reshape((n, n)).T for lat in lats_batch]
    lons = [np.array(lon).reshape((n, n)).T for lon in lons_batch]
    data_list = [np.array(data).reshape((n, n)).T for data in data_batch]
    # get quadrilateral cells at each faces
    quads = []
    values = []
    for k, (lon, lat, data) in enumerate(zip(lons, lats, data_list)):
        # Build quadrilateral faces
        x = [lon[s].ravel() for s in slices]
        y = [lat[s].ravel() for s in slices]
        value_array = 0.25 * np.sum([data[s].ravel() for s in slices], axis=0)
        quads, values = generate_cell(x, y, value_array, quads, values)

    # build quadrilateral faces at the boundaries between faces
    # and fill the gaps between faces
    for face_slice in face_slices:
        x = [lons[f][i, j].ravel() for f, (i, j) in face_slice]
        y = [lats[f][i, j].ravel() for f, (i, j) in face_slice]
        value_array = np.sum([data_list[f][i, j].ravel()
                            for f, (i, j) in face_slice], axis=0)
        value_array = 1./len(face_slice)*value_array
        quads, values = generate_cell(x, y, value_array, quads, values)

    # plot the data
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.coastlines()
    coll = PolyCollection(quads, array=values, cmap='Blues',
                        edgecolor='k',
                        transform=ccrs.PlateCarree())
    ax.add_collection(coll)
    # ax.set_extent([-180, -90, 180, -30], ccrs.PlateCarree())
    ax.set_global()
    plt.show()
