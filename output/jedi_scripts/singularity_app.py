def singularity_app(executable, yaml_file):
    import subprocess
    import os
    
    # JEDI code path
    base_path = "/storage/research/nceo/DA-training-course"
    sif_path = os.path.join(base_path, "docs", "jedi-gnu-openmpi-dev_latest.sif")

    log_file = os.path.splitext(yaml_file)[0] + ".txt"
    cmd = [
        "singularity", "exec",
        "--bind", base_path,
        sif_path,
        f"./bin/{executable}",
        f"yamls/{yaml_file}"
    ]

    with open(f"log/{log_file}", "w") as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)