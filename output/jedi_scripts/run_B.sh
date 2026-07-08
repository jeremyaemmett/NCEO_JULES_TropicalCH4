#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1
#SBATCH --output=screen_output.txt
#SBATCH --time=00:05:00   # 5 minutes (hh:mm:ss)
#SBATCH --mem=1G # 1GB

# JEDI code path
BASE_PATH="/storage/research/nceo/DA-training-course"

singularity exec --bind $BASE_PATH \
$BASE_PATH/docs/jedi-gnu-openmpi-dev_latest.sif \
./bin/qg_gen_ens_pert_B.x yamls/gen_ens_pert_B.yaml