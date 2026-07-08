from datetime import datetime, timedelta
import yaml
import os

from utc import utc
from iso8601 import iso8601
from singularity_app import singularity_app

def generate_forecasts(analysis_time: datetime, cycling_interval: timedelta,
                       ensemble_size: int, nx: int, ny: int) -> None:

    template_yaml = "forecast.yaml"
    executable = "qg_forecast.x"
    
    for member in range(1, ensemble_size+1):
        member_str = f"{member:06d}" 

        with open(f"yamls/{template_yaml}", 'r') as f:
            config = yaml.safe_load(f)

        config['initial condition']['date'] = utc(analysis_time)
        config['initial condition']['filename'] = f"Data/letkf.bgn.{member_str}.an.{utc(analysis_time)}.nc"
        config['output']['exp'] = f"forecast.{member}"
        config['output']['date'] = utc(analysis_time)

        config['forecast length'] = iso8601(cycling_interval * 2)
        config['output']['first'] = 'PT0S'
        config['output']['frequency'] = iso8601(cycling_interval)
    
        config["geometry"]["nx"] = nx
        config["geometry"]["ny"] = ny

        base_name = os.path.splitext(template_yaml)[0]
        modified_yaml = f"{base_name}_new.yaml"
        with open(f"yamls/{modified_yaml}", 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        singularity_app(executable, modified_yaml)
    
    print("[Forecast Done]")
    print(f"forecast.*.fc.{utc(analysis_time)}.{iso8601(cycling_interval)}.nc")
    print(f"forecast.*.fc.{utc(analysis_time)}.{iso8601(cycling_interval * 2)}.nc")