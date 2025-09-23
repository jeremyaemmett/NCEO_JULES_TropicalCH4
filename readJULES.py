from netCDF4 import Dataset
import xarray as xr


def read_jules_m1(file_path, variable):

    # Method 1 to read JULES output (using netCDF4)

    data_dict = {}

    with Dataset(file_path, 'r') as nc_file:
        # print("Variables in the file:")
        for var_name in nc_file.variables:
            # print(var_name)
            var = nc_file.variables[var_name]
            data_dict[var_name] = {'data': var[:], 'attrs': dict(var.__dict__)}

    array = data_dict[variable]['data']
    units = data_dict[variable]['attrs'].get('units', 'unknown')

    return array, units


def read_jules_m2(file_path, variable):

    # Method 2 to read JULES output (using xarray)

    data_dict = {}

    ds = xr.open_dataset(file_path)
    #print(list(ds.variables))
    for var_name in ds.variables:
        var = ds[var_name]
        data_dict[var_name] = {'data': var.values, 'attrs': dict(var.attrs)}

    array = data_dict[variable]['data']
    #print(data_dict[variable]['attrs'])
    long_name = data_dict[variable]['attrs'].get('long_name', 'unknown')
    units = data_dict[variable]['attrs'].get('units', 'unknown')

    return array, units, long_name


def read_jules_header(file_path):

    with Dataset(file_path, 'r') as nc:

        dimensions = nc.dimensions.keys()
        variables = nc.variables.keys()
        global_attributes = nc.ncattrs()

    return(dimensions, variables, global_attributes)
