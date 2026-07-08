#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1
#SBATCH --output=screen_output.txt
#SBATCH --time=12:00:00 
#SBATCH --mem=10G # 10GB

module load anaconda/2023.09-0/met-env

python main.py truth
python main.py initial_background
python main.py obs
python main.py letkf
