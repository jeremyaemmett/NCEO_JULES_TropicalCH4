# JULES output file path/name
ftype = 4

if ftype == 1:
    data_path = '/Users/jae35/Desktop/JULES_test_data/JULES_wetlands_JE/'
    outp_path = '/Users/jae35/Documents/nceo/'
    file_name = 'u-ck843_preprocessed.nc'
    lat_min, lat_max, lon_min, lon_max = -25.0, 25.0, -20.0, 60.0
    year = 2015
if ftype == 2: 
    data_path = '/Users/jae35/Desktop/JULES_test_data/JASMIN_output/'#
    outp_path = '/Users/jae35/Documents/jasmin/'
    file_name = 'monthly_means_2015.nc'
    lat_min, lat_max, lon_min, lon_max = 3.25, 6.45, 100.0, 103.7
    year = 2015
if ftype == 3:
    data_path = '/Users/jae35/Desktop/JULES_test_data/JASMIN_output_Umzimvubu3/'
    outp_path = data_path + 'plots/'
    #file_name = 'Umzimvubu_RFMh.Monthly.nc'
    file_name = 'umz2010.nc'
    lat_min, lat_max, lon_min, lon_max = -25.0, 25.0, -20.0, 60.0
    year = 2010
#if ftype == 4:
    ##data_path = '/Users/jae35/Desktop/JULES_test_data/sp1/JASMIN_output_u-dk105_1_sp1/'
    #data_path = '/Users/jae35/Desktop/JULES_test_data/JULES_wetlands_JE/'
    #data_path = '/Users/jae35/Desktop/JULES_test_data/JASMIN_output_u-dk105_3_n6/'
    ##outp_path = data_path + 'plots/'
    #file_name = 'Umzimvubu_RFMh.Monthly.nc'
    #file_name = 'CRUJRA2.4_2023_n96_v8.0_S3.ilamb.1701.nc'
    ##file_name = 'CRUJRA2.4_2023_n96_v8.0_S3.ilamb.2022.nc'
    #lat_min, lat_max, lon_min, lon_max = -90.0, 90.0, 0.0, -50.0
    #year = 1701
    #year = 2022

# Variable(s)
variable_names = ['t_soil', 'fch4_wetl', 'tstar_gb', 'frac', 'lai', 'lai_gb', 'lw_net', 'sw_net', 
                  't1p5m_gb', 'q1p5m_gb', 'latent_heat', 'lw_up', 'rad_net', 'albedo_land',
                  'runoff', 'surf_roff', 'rflow', 'fqw', 'fsat', 'fwetl', 'lw_down', 'sw_down',
                  'precip', 'ls_rain', 'pstar', 'qw1', 'tl1', 'u1', 'v1', 'co2_mmr', 'albsoil',
                  'b', 'fexp', 'hcap', 'hcon', 'satcon', 'sathh', 'sm_crit', 'sm_sat', 'sm_wilt',
                  'ti_mean', 'ti_sig']

variable_names = ['fch4_wetl']
#variable_names = ['fch4_wetl', 't_soil', 'npp_gb', 'resp_p_gb']