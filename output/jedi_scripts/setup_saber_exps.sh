#!/bin/bash

# JEDI code path
BASE_PATH="/storage/research/nceo/DA-training-course"

# Check if the base path exists
if [ -d "$BASE_PATH" ]; then
  # echo "Base path '$BASE_PATH' exists."

  # SABER experiments
  if [ -d "saber_exps" ]; then
    echo "Folder saber_exps already exists."
  else
    mkdir "saber_exps"
    mkdir "saber_exps/testdata"
    
    # saber_quench_error_covariance_toolbox.x
    LINK_TARGET="$BASE_PATH/build/bin/saber_quench_error_covariance_toolbox.x"
    LINK_NAME="saber_exps/saber_quench_error_covariance_toolbox.x"
    ln -s "$LINK_TARGET" "$LINK_NAME"

    # testdata/
    cp "$BASE_PATH/src/fv3-bundle/saber/test/testdata/gauss_state.nc" saber_exps/testdata/
    cp "$BASE_PATH/src/fv3-bundle/saber/test/testdata/spectralcov.nc" saber_exps/testdata/
    cp "$BASE_PATH/src/fv3-bundle/saber/test/testdata/FPstats.nc" saber_exps/testdata/
    cp "$BASE_PATH/src/fv3-bundle/saber/test/testdata/MUstats.nc" saber_exps/testdata/
    cp "$BASE_PATH/src/fv3-bundle/saber/test/testdata/MIO_coefficients.nc" saber_exps/testdata/

    # run_saber.sh
    SOURCE="$BASE_PATH/docs/run_saber.sh"
    DESTINATION="saber_exps/run_saber.sh"
    cp "$SOURCE" "$DESTINATION"

    # dirac_spectralb_gauss_vader_1.yaml
    SOURCE="$BASE_PATH/docs/yamls/dirac_spectralb_gauss_vader_1.yaml"
    DESTINATION="saber_exps/dirac_spectralb_gauss_vader_1.yaml"
    cp "$SOURCE" "$DESTINATION"

    # plot_saber.py 
    SOURCE="$BASE_PATH/docs/plot_saber.py"
    DESTINATION="saber_exps/plot_saber.py"
    cp "$SOURCE" "$DESTINATION"
    # LINK_TARGET="$BASE_PATH/docs/plot_saber.py"
    # LINK_NAME="saber_exps/plot_saber.py"
    # ln -s "$LINK_TARGET" "$LINK_NAME"

    echo "Folder saber_exps created."
  fi

else
  echo "Base path '$BASE_PATH' does not exist. Cannot proceed."
  exit 1
fi