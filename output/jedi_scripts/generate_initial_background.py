def generate_initial_background(ensemble_size, nx, ny, analysis_time, cycling_interval, truth_initial_time):
    import yaml
    import os
    from datetime import datetime
    from iso8601 import iso8601
    from utc import utc
    from singularity_app import singularity_app

    template_yaml = "gen_ens_pert_B.yaml"
    executable = "qg_gen_ens_pert_B.x"

    leadtime = iso8601(analysis_time - cycling_interval - truth_initial_time)

    with open(f"yamls/{template_yaml}", 'r') as f:
        config = yaml.safe_load(f)

    # Modify the ensemble size
    config['forecast length'] = iso8601(cycling_interval)
    config['initial condition']['date'] = utc(analysis_time - cycling_interval)
    config['initial condition']['filename'] = f"Data/truth.fc.{utc(truth_initial_time)}.{leadtime}.nc"
    config['members'] = ensemble_size
    config['output']['date'] = utc(analysis_time - cycling_interval)
    config['output']['first'] = iso8601(cycling_interval)
    config['output']['frequency'] = iso8601(cycling_interval)
    config["geometry"]["nx"] = nx
    config["geometry"]["ny"] = ny

    # Save the modified YAML
    new_yaml = os.path.splitext(template_yaml)[0] + "_new.yaml"
    with open(f"yamls/{new_yaml}", 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    singularity_app(executable, new_yaml)
    print(f"[Initial background] Generated: Data/forecast.ens.*.nc\n")