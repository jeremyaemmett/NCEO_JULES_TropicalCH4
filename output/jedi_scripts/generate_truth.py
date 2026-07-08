def generate_truth(forecast_length, frequency, nx, ny, date):
    import yaml
    import os
    from singularity_app import singularity_app

    template_yaml="truth.yaml"
    executable="qg_forecast.x"

    # Open template yaml
    with open(f"yamls/{template_yaml}", "r") as f:
        config = yaml.safe_load(f)

    # Modify template yaml
    config["forecast length"] = forecast_length
    config["geometry"]["nx"] = nx
    config["geometry"]["ny"] = ny
    config["initial condition"]["date"] = date
    config["output"]["date"] = date
    config["output"]["frequency"] = frequency

    # Save modified yaml file
    new_yaml = os.path.splitext(template_yaml)[0] + "_new.yaml"
    with open(f"yamls/{new_yaml}", 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    singularity_app(executable, new_yaml)
    print(f"[Truth] Generated: Data/truth.fc.*.nc\n")