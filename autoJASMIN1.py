import xarray as xr
import pandas as pd
import numpy as np
import subprocess
import readJULES
import shlex
import glob
import time
import os

def load_key():

    result = subprocess.run(
        'ssh-add ~/.ssh/id_ecdsa_jasmin --apple-use-keychain && ' \
        'echo "ssh-add --apple-load-keychain" >> ~/.zshrc && ' \
        'ssh-add -l',
        shell=True, capture_output=True, text=True)

    print(result.stdout)
    print(result.stderr)


def ssh_to_jasmin():

    ssh_login_command = "ssh -AX jae35@login-03.jasmin.ac.uk"
    ssh_cylc_command = "ssh cylc2.jasmin.ac.uk"
    ssh_sci_command = "ssh sci-vm-02.jasmin.ac.uk"
    delay_seconds = 5  # adjust based on how long login typically takes

    apple_script = f'''
    tell application "Terminal"
        activate
        do script "{ssh_login_command}"
        delay {delay_seconds}
        do script "{ssh_cylc_command}" in front window
    end tell
    '''

    subprocess.run(["osascript", "-e", apple_script])


def copy_bashrc():

    copy_command = 'cp ~tmarthews/.bashrc ~jae35/.bashrc'
    
    apple_script = f'''
    tell application "Terminal"
        do script "{copy_command}" in front window
    end tell
    '''
    
    result = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    
    print(result.stdout)
    print(result.stderr)


def modify_bashrc_paths():
    edit1 = "sed -i.bak 's/tmarthews/jae35/g' cylc-src/u-dn883/app/jules/rose-app.conf"
    edit2 = "sed -i.bak 's/tmarthews/jae35/g' cylc-src/u-dn883/app/fcm_make/rose-app.conf"
    edit3 = "sed -i.bak 's/tmarthews/jae35/g' ~/.bashrc"
    edit4 = "source ~/.bashrc"
    
    apple_script = f'''
    tell application "Terminal"
        activate
        -- assuming front window is the target
        tell front window
            do script "{edit1}; {edit2}; {edit3}; {edit4}" in selected tab
        end tell
    end tell
    '''

    result = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


def set_environment_variables():
    shell_script = '''
export RSUITE=$HOME/cylc-src/u-dn883; \
tmp1=$(grep -ir "JULES_SOURCE" "$RSUITE/app/fcm_make/rose-app.conf"); \
export JULES_ROOT=${tmp1##*=}; \
unset tmp1; \
tmp1=$(grep -ir "output_dir" "$RSUITE/app/jules/rose-app.conf"); \
export OUTPUT_DIR=$(echo ${tmp1##*=} | sed "s/'//g"); \
unset tmp1; \
tmp1=$(grep -ir "run_id" "$RSUITE/app/jules/rose-app.conf"); \
export RUN_ID=$(echo ${tmp1##*=} | sed "s/'//g"); \
unset tmp1; \
echo "Cylc workflow is: $RSUITE"; \
echo "     which uses this version of JULES: $JULES_ROOT"; \
echo "     and will save output to these files: ls $OUTPUT_DIR/$RUN_ID*";
'''
#suite_name=$(basename "$RSUITE"); \
#export NAMELIST=$HOME/cylc-src/nlists_$suite_name; \
#mkdir -p "$NAMELIST"; \
#cd "$NAMELIST"; \
#rose app-run -i -C "$RSUITE/app/jules"; \
#cd ~
#'''

    # Escape quotes and collapse to single line
    escaped = shell_script.strip().replace('"', '\\"').replace('\n', ' ')

    apple_script = f'''
    tell application "Terminal"
        do script "{escaped}" in front window
    end tell
    '''

    result = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)

    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)


def make_name_lists():
    commands = [
        'source ~/.zshrc || source ~/.bash_profile || source ~/.bashrc',
        'export NAMELIST=$HOME/cylc-src/nlists_${RSUITE##*/}',
        'mkdir -p "$NAMELIST"',
        'cd "$NAMELIST"',
        'rose app-run -i -C "$RSUITE/app/jules"',
        'cd ~'
    ]

    # AppleScript to run each command separately in Terminal, waiting a bit between them
    # so they execute in order in the same Terminal window.
    apple_script_commands = '\n'.join(f'do script "{cmd}" in front window' for cmd in commands)

    # But AppleScript do script opens a new tab/window for each command if used separately,
    # so instead, we send them one by one with short delays in between using Python.
    # So better to open Terminal, then run each command with small pause.

    apple_script = f'''
    tell application "Terminal"
        activate
        if not (exists window 1) then
            do script ""
            delay 1
        end if
    end tell
    '''

    # Run the AppleScript to open Terminal first
    subprocess.run(["osascript", "-e", apple_script])

    # Now send commands one by one with small delay so they run in the same Terminal window
    for cmd in commands:
        as_cmd = f'''
        tell application "Terminal"
            do script "{cmd}" in front window
        end tell
        '''
        subprocess.run(["osascript", "-e", as_cmd])
        time.sleep(1)  # 1 second delay between commands, adjust if needed


def clear_cylc_workflows():
    workflow = "u-dn883/run1"
    stop_and_clean = f"cylc stop --now {workflow}; cylc clean {workflow}"

    apple_script = f'''
    tell application "Terminal"
        activate
        do script "{stop_and_clean}" in front window
    end tell
    '''

    subprocess.run(["osascript", "-e", apple_script])


def run_jules():
    commands = [
        'cd ~',
        'cylc validate $RSUITE',
        'cylc vip $RSUITE',
    ]
    # Join with newline characters
    full_command = '\n'.join(commands)

    # Escape quotes properly for AppleScript
    full_command_escaped = full_command.replace('"', '\\"')

    apple_script = f'''
    tell application "Terminal"
        activate
        if not (exists window 1) then
            do script "{full_command_escaped}"
        else
            do script "{full_command_escaped}" in front window
        end if
    end tell
    '''

    subprocess.run(["osascript", "-e", apple_script])


def check_error_file():

    workflow = "u-dn883/run1"
    check_error = "cat cylc-run/u-dn883/run1/log/job/1/fcm_make/NN/job.err"

    apple_script = f'''
    tell application "Terminal"
        activate
        do script "{check_error}" in front window
    end tell
    '''

    subprocess.run(["osascript", "-e", apple_script])


def scp_from_jasmin(local_directory, remote_directory_and_files):
    # Build the scp command (exactly the one you want)
    cmd = (
        "scp -v -o ProxyJump=jae35@login-03.jasmin.ac.uk "
        f"jae35@cylc2.jasmin.ac.uk:'{remote_directory_and_files}' "
        f"{shlex.quote(local_directory)}"
    )

    print(f"\n🔧 Running command:\n{cmd}\n")

    # Run the command with live output (no capture)
    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print("\nFiles copied successfully!\n")
    else:
        print(f"\nscp failed with exit code {result.returncode}\n")


import xarray as xr
import os
import glob

def daily_to_monthly(input_folder, output_file, file_pattern="*.nc"):
    """
    Convert daily NetCDF files in a folder to a single NetCDF of monthly averages.
    Works without Dask by manually concatenating files.

    Parameters:
    -----------
    input_folder : str
        Path to the folder containing daily NetCDF files.
    output_file : str
        Path to the output NetCDF file for monthly averages.
    file_pattern : str, optional
        Pattern to match files in the folder (default is '*.nc').

    Returns:
    --------
    None
    """
    # Find all files matching the pattern
    files = sorted(glob.glob(os.path.join(input_folder, file_pattern)))
    if not files:
        raise FileNotFoundError(f"No files found matching {file_pattern} in {input_folder}")

    # Open all files into a list of datasets
    datasets = [xr.open_dataset(f) for f in files]

    # Concatenate along the time dimension
    ds = xr.concat(datasets, dim="time")

    # Ensure time coordinate is datetime
    if not xr.core.common.is_np_datetime_like(ds.time):
        ds["time"] = xr.decode_cf(ds).time

    # Compute monthly averages
    monthly_ds = ds.resample(time="1M").mean()

    # Save to NetCDF
    monthly_ds.to_netcdf(output_file)
    print(f"Monthly averages saved to: {output_file}")


def daily_to_monthly2(input_file, output_file):

    # Input and output files
    input_file = "/Users/jae35/Desktop/JULES_test_data/JASMIN_output_Umzimvubu/Umzimvubu_RFMh.Daily.nc"
    output_file = "/Users/jae35/Desktop/JULES_test_data/JASMIN_output_Umzimvubu/Umzimvubu_RFMh.Monthly.nc"

    # Open dataset
    ds = xr.open_dataset(input_file)

    # Ensure 'time' is in datetime format (assuming 'time' is days since a reference date)
    # If 'time' is already a datetime64, this will do nothing
    if not np.issubdtype(ds['time'].dtype, np.datetime64):
        # Replace 'YYYY-01-01' with your reference date if needed
        ds['time'] = pd.to_datetime(ds['time'].values, origin='YYYY-01-01', unit='D')

    # Compute monthly means
    ds_monthly = ds.resample(time='1M').mean(dim='time')

    # Save to new NetCDF
    ds_monthly.to_netcdf(output_file)

    print(f"Monthly averages saved to {output_file}")

task = 'ssh'

if task == 'ssh':

    load_key()
    time.sleep(5)
    ssh_to_jasmin()

if task == 'scp':

    scp_from_jasmin('/Users/jae35/Desktop/JULES_test_data/JASMIN_output', '/work/scratch-pw4/jae35/Umzim*.nc')

if task == 'process':

    daily_to_monthly('/Users/jae35/Desktop/JULES_test_data/JASMIN_output','/Users/jae35/Desktop/JULES_test_data/JASMIN_output/monthly_means_2015.nc','*Daily.2015*.nc')

if task == 'examine':

    readJULES.examine_nc_file('/Users/jae35/Desktop/JULES_test_data/JASMIN_output_Umzimvubu/Umzimvubu_RFMh.Monthly.nc')
    #daily_to_monthly2('/Users/jae35/Desktop/JULES_test_data/JASMIN_output_Umzimvubu/Umzimvubu_RFMh.Daily.nc', 'Umzimvubu_RFMh.Monthly.nc')
    #readJULES.examine_nc_file('/Users/jae35/Desktop/JULES_test_data/JASMIN_output_Umzimvubu/Umzimvubu_RFMh.Monthly.nc')

#copy_bashrc()
#time.sleep(5)

#modify_bashrc_paths()
#time.sleep(5)

#set_environment_variables()
#time.sleep(5)

#make_name_lists()
#time.sleep(5)

#run_jules()

#check_error_file()

#clear_cylc_workflows()

# cat cylc-run/u-dn883/run1/log/job/1/fcm_make/NN/job.err


