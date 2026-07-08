#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1
#SBATCH --output=screen_output.txt
#SBATCH --time=00:05:00   # 5 minutes (hh:mm:ss)
#SBATCH --mem=1G          # 1GB

# JEDI code path
BASE_PATH="/storage/research/nceo/DA-training-course"

# Run YAMLs sequentially, suppressing all output except echo
for yaml in yamls/make_obs_4d_12h_*.yaml; do
  # Extract timestamp from YAML filename (e.g., 20100101T00)
  tag=$(basename "$yaml" .yaml | sed 's/make_obs_4d_12h_//')

  echo "Generating observation file: Data/truth.obs4d_12h_${tag}.nc"
  singularity exec --bind "$BASE_PATH \
  "$BASE_PATH/docs/jedi-gnu-openmpi-dev_latest.sif" \
  ./bin/qg_hofx.x "$yaml" > log/make_obs_4d_12h_${tag}.txt 2>&1
done