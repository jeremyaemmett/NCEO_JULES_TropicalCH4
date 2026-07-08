import os
import yaml

from utc import utc
from iso8601 import iso8601
from singularity_app import singularity_app

def generate_Ya(analysis_time, cycling_interval, ensemble_size, nx, ny):

    template_yaml = "ens_hofx_1.yaml"
    executable = "qg_hofx.x"
    
    for member in range(1, ensemble_size+1):
        member_str = f"{member:06d}" 

        with open(f"yamls/{template_yaml}", 'r') as f:
            config = yaml.safe_load(f)

        config['geometry']['nx'] = nx
        config['geometry']['ny'] = ny
        config['initial condition']['date'] = utc(analysis_time)
        config['initial condition']['filename'] = f"Data/letkf.bgn.{member_str}.an.{utc(analysis_time)}.nc"
        config['forecast length'] = iso8601(cycling_interval * 2)
        config['time window']['begin'] = utc(analysis_time)
        config['time window']['length'] = iso8601(cycling_interval * 2)

        for observer in config.get('observations', {}).get('observers', []):
            obs_space = observer.get('obs space', {})
            if 'obsdatain' in obs_space and 'obsfile' in obs_space['obsdatain']:
                obs_space['obsdatain']['obsfile'] = f"Data/truth.obs3d.nc"
            if 'obsdataout' in obs_space and 'obsfile' in obs_space['obsdataout']:
                obs_space['obsdataout']['obsfile'] = f"Data/mem{str(member).zfill(3)}.ana_ens_hofx_{utc(analysis_time)}.nc"

        base_name = os.path.splitext(template_yaml)[0]
        modified_yaml = f"{base_name}_new.yaml"
        with open(f"yamls/{modified_yaml}", 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        singularity_app(executable, modified_yaml)
    
    print("[Ya Done]")
    print(f"Data/mem***.ana_ens_hofx_{utc(analysis_time)}.nc")