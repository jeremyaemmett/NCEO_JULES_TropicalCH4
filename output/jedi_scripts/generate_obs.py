import yaml
import subprocess
from datetime import datetime, timedelta
import os

from iso8601 import iso8601
from utc import utc
from singularity_app import singularity_app

def generate_obs(start_time: datetime, end_time: datetime, 
                 first_obs_time: datetime, period: timedelta,
                 truth_initial_time: datetime, nx: int, ny: int,
                 template_yaml: str = "make_obs_3d.yaml",
                 executable: str = "qg_hofx.x",
                 output_file: str = "Data/truth.obs3d.nc") -> None:

    # template_yaml = "make_obs_4d_12h.yaml"
    with open(f"yamls/{template_yaml}", "r") as f:
        config = yaml.safe_load(f)

    config["geometry"]["nx"] = nx
    config["geometry"]["ny"] = ny
    config["initial condition"]["date"] = utc(start_time)
    config["initial condition"]["filename"] = f"Data/truth.fc.{utc(truth_initial_time)}.{iso8601(start_time - truth_initial_time)}.nc"
    config["forecast length"] = iso8601(end_time - start_time)
    config["time window"]["begin"] = utc(start_time)
    config["time window"]["length"] = iso8601(end_time - start_time)

    for observer in config["observations"]["observers"]:
        observer["obs space"]["obsdataout"]["obsfile"] = output_file
        observer["obs space"]["generate"]["begin"] = iso8601(first_obs_time)
        observer["obs space"]["generate"]["obs period"] = iso8601(period)

    # Write modified YAML
    base_name = os.path.splitext(template_yaml)[0]
    modified_yaml = f"{base_name}_new.yaml"
    with open(f"yamls/{modified_yaml}", 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
  
    # Run the YAML file using singularity
    singularity_app(executable, modified_yaml)
    print(f"[Observation Done]: {output_file}")