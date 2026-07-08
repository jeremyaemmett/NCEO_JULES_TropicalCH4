from datetime import datetime, timedelta
import yaml
import os

from utc import utc
from iso8601 import iso8601
from singularity_app import singularity_app

def letkf(window_start_time: datetime, analysis_time: datetime, cycling_interval: timedelta, ensemble_size: int,
          nx: int, ny: int, rtpp: float, mult: float, initial: bool) -> None:

    template_yaml = "letkf.yaml"
    executable = "qg_letkf.x"

    forecast_start_time = analysis_time - cycling_interval

    # Load and modify YAML
    with open(f"yamls/{template_yaml}", 'r') as f:
        config = yaml.safe_load(f)

    config["time window"]["begin"] = utc(window_start_time)
    config["time window"]["length"] = iso8601(cycling_interval)
    config['members'] = ensemble_size

    config["geometry"]["nx"] = nx
    config["geometry"]["ny"] = ny

    bg_state = config["background"]["members from template"]["template"]["states"][0]
    bg_state["date"] = utc(analysis_time)
    bg_state["filename"] = (
        f"Data/forecast.ens.%mem%.{utc(forecast_start_time)}.{iso8601(cycling_interval)}.nc"
        if initial else
        f"Data/forecast.%mem%.fc.{utc(forecast_start_time)}.{iso8601(cycling_interval)}.nc"
    )

    config["background"]["members from template"]["nmembers"] = ensemble_size

    config['local ensemble DA']['inflation']['rtpp'] = rtpp
    config['local ensemble DA']['inflation']['mult'] = mult

    # Update observation filenames
    for obs in config["observations"]["observers"]:
        obs_space = obs.get("obs space", {})
        if "obsdatain" in obs_space and "obsfile" in obs_space["obsdatain"]:
            obs_space["obsdatain"]["obsfile"] = f"Data/truth.obs3d.nc"
        if "obsdataout" in obs_space and "obsfile" in obs_space["obsdataout"]:
            obs_space["obsdataout"]["obsfile"] = f"Data/letkf.obs3d.{utc(analysis_time)}.nc"

    # Update output date and exp
    config["output"]["states"][0]["date"] = utc(analysis_time)

    # Write YAML file
    base_name = os.path.splitext(template_yaml)[0]
    modified_yaml = f"{base_name}_new.yaml"
    with open(f"yamls/{modified_yaml}", "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    # Run LETKF via Singularity
    singularity_app(executable, modified_yaml)
    print("[LETKF Done]")
    print(f"Data/letkf.bgn.*.an.{utc(analysis_time)}.nc")
    print(f"Data/letkf.obs3d.{utc(analysis_time)}.nc")