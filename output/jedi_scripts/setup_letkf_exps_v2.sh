#!/bin/bash

# JEDI code path
BASE_PATH="/storage/research/nceo/DA-training-course"

# Check if the base path exists
if [ -d "$BASE_PATH" ]; then
  # echo "Base path '$BASE_PATH' exists."

  # LETKF experiments 
  if [ -d "letkf_exps" ]; then
    echo "Folder letkf_exps already exists."
  else
    mkdir "letkf_exps"
    mkdir "letkf_exps/Data"
    mkdir "letkf_exps/bin"
    mkdir "letkf_exps/log"
    
    # Copy of yaml folder
    cp -r "$BASE_PATH/docs/yamls" "letkf_exps/yamls"

    # Symbolic links to excutable files (.x)
    ln -s "$BASE_PATH/build/bin/qg_letkf.x" "letkf_exps/bin/qg_letkf.x"
    ln -s "$BASE_PATH/build/bin/qg_forecast.x" "letkf_exps/bin/qg_forecast.x"
    ln -s "$BASE_PATH/build/bin/qg_gen_ens_pert_B.x" "letkf_exps/bin/qg_gen_ens_pert_B.x"
    ln -s "$BASE_PATH/build/bin/qg_hofx.x" "letkf_exps/bin/qg_hofx.x"

    # Cycling LETKF experiments
    cp "$BASE_PATH/docs/run_main.sh" "letkf_exps/run_main.sh"
    cp "$BASE_PATH/docs/main.py" "letkf_exps/main.py"
    cp "$BASE_PATH/docs/generate_initial_background.py" "letkf_exps/generate_initial_background.py"
    cp "$BASE_PATH/docs/generate_truth.py" "letkf_exps/generate_truth.py"
    cp "$BASE_PATH/docs/generate_obs.py" "letkf_exps/generate_obs.py"
    cp "$BASE_PATH/docs/generate_forecasts.py" "letkf_exps/generate_forecasts.py"
    cp "$BASE_PATH/docs/generate_Ya.py" "letkf_exps/generate_Ya.py"
    cp "$BASE_PATH/docs/compute_analysis_error.py" "letkf_exps/compute_analysis_error.py"
    cp "$BASE_PATH/docs/compute_ensemble_mean.py" "letkf_exps/compute_ensemble_mean.py"
    cp "$BASE_PATH/docs/compute_ensemble_spread.py" "letkf_exps/compute_ensemble_spread.py"
    cp "$BASE_PATH/docs/letkf.py" "letkf_exps/letkf.py"
    cp "$BASE_PATH/docs/singularity_app.py" "letkf_exps/singularity_app.py"
    cp "$BASE_PATH/docs/iso8601.py" "letkf_exps/iso8601.py"
    cp "$BASE_PATH/docs/utc.py" "letkf_exps/utc.py"

    # Plot
    cp "$BASE_PATH/docs/draw_letkf_v2.py" "letkf_exps/draw_letkf_v2.py"
    cp "$BASE_PATH/docs/plot.py" "letkf_exps/plot.py"
    cp -r "$BASE_PATH/docs/plot" "letkf_exps/plot"
    cp "$BASE_PATH/docs/plot_ensemble_covariance.py" "letkf_exps/plot_ensemble_covariance.py"

    # Symbolic link to Data folder
    # ln -s "$BASE_PATH/build/oops/qg/test/Data" "letkf_exps/Data"

    # Copies of batch scripts (.sh)
    # cp "$BASE_PATH/docs/run_letkf.sh" "letkf_exps/run_letkf.sh"
    # cp "$BASE_PATH/docs/run_truth.sh" "letkf_exps/run_truth.sh"
    # cp "$BASE_PATH/docs/run_B.sh" "letkf_exps/run_B.sh"
    # cp "$BASE_PATH/docs/run_obs.sh" "letkf_exps/run_obs.sh"

    echo "Folder letkf_exps created."
  fi

else
  echo "Base path '$BASE_PATH' does not exist. Cannot proceed."
  exit 1
fi