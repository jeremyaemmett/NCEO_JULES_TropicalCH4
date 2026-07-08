# JEDI experiment scripts

This directory contains the scripts and configuration templates used in the
experiments described in `JEDI_LETKF_exps_v2.pdf`, `JEDI_LETKF_exps.pdf`, and
`JEDI_SABER_exps.pdf`. The examples run JEDI quasi-geostrophic (QG) LETKF
cycling experiments and SABER covariance tests, then inspect or plot their
outputs.

Most scripts assume they are copied
into an experiment directory and run from there, alongside `bin/`, `Data/`,
`log/`, and `yamls/`.

## Important portability warning

These scripts were written for the University of Reading RACC system. Paths
such as

```text
/storage/research/nceo/DA-training-course
```

and the location of `jedi-gnu-openmpi-dev_latest.sif`, a JEDI Singularity
container image, are hardcoded in several setup, run, and Python scripts.
Module names, Slurm options, Singularity bind mounts, executable locations,
and input-data paths are also RACC-specific.

Use the scripts with caution on other systems. Review and update all paths,
software/module commands, scheduler directives, container settings, and file
names before running them. In particular, inspect `BASE_PATH` in the shell
scripts and `base_path` in `singularity_app.py`.

## General workflow

### Cycling LETKF workflow (v2)

1. Run `setup_letkf_exps_v2.sh` from the directory in which the experiment
   should be created. It creates `letkf_exps/`, links the required JEDI
   compiled executables (`.x` files), and copies the Python scripts and YAML
   templates.
2. Edit the experiment settings near the top of `main.py`, including the
   ensemble size, truth and cycling dates, cycling interval, and grid size.
3. Run `run_main.sh` with Slurm, or invoke the four `main.py` stages in order:
   `truth`, `initial_background`, `obs`, and `letkf`.
4. During each LETKF cycle, `main.py` creates a cycle-specific YAML file,
   runs LETKF, reports background/analysis error and spread, and advances each
   analysis member to provide the next cycle's background.
5. Use `draw_letkf_v2.py`, `plot.py`, or
   `plot_ensemble_covariance.py` to inspect the results.

The scripts modify copies of the templates in `yamls/`; the original templates
define the JEDI applications, geometry, observations, covariance settings, and
output conventions.

### single LETKF workflow

`setup_letkf_exps.sh` creates a smaller `letkf_exps/` directory for the
workflow described in the original LETKF notes. The individual Slurm wrappers
run truth generation, ensemble perturbation generation, observation
generation, and LETKF. `draw_letkf.sh` and the plotting utilities then examine
the truth, analysis error, observations, and ensemble covariance.

### SABER workflow

1. Run `setup_saber_exps.sh` to create `saber_exps/`, link the SABER covariance
   toolbox compiled executable (`.x`), and copy its test data, YAML
   configuration, run script, and plotter.
2. Submit `run_saber.sh` to execute the SABER Dirac/covariance test inside the
   `jedi-gnu-openmpi-dev_latest.sif` JEDI Singularity image.
3. Run `plot_saber.py` on an output NetCDF file to visualise a selected
   variable and model level.

## Script reference

### Setup and batch scripts

- `setup_letkf_exps_v2.sh`: builds the complete Python-driven cycling LETKF
  experiment directory and links all required QG executables.
- `setup_letkf_exps.sh`: builds the single-run LETKF
  experiment directory.
- `setup_saber_exps.sh`: builds a SABER test directory with the executable,
  test data, configuration, and plotting script.
- `run_main.sh`: Slurm job that runs the four v2 preparation and cycling stages
  through `main.py`.
- `run_truth.sh`: Slurm wrapper for a QG truth forecast.
- `run_B.sh`: Slurm wrapper that generates an initial perturbed ensemble using
  the configured background-error covariance.
- `run_obs.sh`: Slurm wrapper that runs a series of observation-generation
  YAML files with `qg_hofx.x`.
- `run_letkf.sh`: Slurm wrapper for one `qg_letkf.x` application run.
- `run_saber.sh`: Slurm wrapper for the SABER covariance toolbox.
- `draw_letkf.sh`: runs the legacy LETKF plotting and observation-dump commands
  for hardcoded example output times.

### LETKF cycling scripts

- `main.py`: top-level experiment driver. It defines the experiment settings,
  dispatches the preparation stages, and controls the LETKF cycling loop.
- `generate_truth.py`: adapts `truth.yaml` and runs a long QG forecast used as
  the synthetic truth.
- `generate_initial_background.py`: adapts `gen_ens_pert_B.yaml` to create the
  first forecast ensemble from the truth and a covariance model.
- `generate_obs.py`: adapts an observation YAML and runs `qg_hofx.x` to create
  synthetic observations over the cycling period.
- `letkf.py`: prepares the YAML for one LETKF analysis, selecting the correct
  initial or cycled background files and applying the configured inflation.
- `generate_forecasts.py`: forecasts every analysis ensemble member to supply
  backgrounds for subsequent cycles.
- `generate_Ya.py`: optional helper that applies the observation operator to
  each analysis member and writes member-wise analysis-space output. Its call
  is disabled by default in `main.py`.
- `compute_analysis_error.py`: compares truth, background, and analysis fields,
  and prints RMSE and ensemble-spread diagnostics.
- `compute_ensemble_mean.py`: reads member NetCDF files and returns their mean.
- `compute_ensemble_spread.py`: reads member NetCDF files and returns their
  sample standard deviation.
- `singularity_app.py`: common launcher for a JEDI executable in the
  Singularity image, with output redirected to `log/`.
- `iso8601.py`: converts Python `timedelta` values to the ISO-8601 durations
  required by JEDI YAML files.
- `utc.py`: formats Python datetimes as JEDI UTC timestamps.

### Plotting and diagnostics

- `draw_letkf_v2.py`: plots truth, analysis-minus-truth error with observation
  locations, and a text dump of observations for a selected analysis time.
- `plot.py`: command-line dispatcher for the L95 and QG plotting modules under
  `plot/`.
- `plot/qg_fields.py`: plots QG fields or differences, optionally including
  winds, observation locations, or an animated sequence.
- `plot/qg_obs.py`: writes QG observation locations, values, and model
  equivalents (`H(x)`) from a NetCDF observation file to text.
- `plot/qg_cost.py`: connects QG cost plotting to the generic cost-log parser.
- `plot/l95_fields.py`: plots Lorenz-95 analysis, background, truth, and
  observations.
- `plot/l95_cost.py`: connects Lorenz-95 cost plotting to the generic
  cost-log parser.
- `plot/cost.py`: extracts nonlinear and quadratic cost values from a JEDI log
  and plots their iteration history.
- `plot_ensemble_covariance.py`: computes ensemble correlations from QG
  forecast members and shows the chosen localization radius.
- `plot_saber.py`: plots an allowed SABER output variable at a requested
  vertical level.
- `plot_cube.py`: standalone example for plotting LFric cubed-sphere NetCDF
  data, including treatment of face boundaries and longitude wrapping.

## Requirements

The workflows require a built JEDI environment and the relevant compiled QG or
SABER executables, identified by their `.x` file extension. JEDI applications
are run inside `jedi-gnu-openmpi-dev_latest.sif`, which is a JEDI Singularity
container image. The Python utilities additionally use packages including
`PyYAML`, `numpy`, `netCDF4`, `matplotlib`, and, for map plots, `cartopy`.
Slurm, Singularity, and optionally ImageMagick are expected by some scripts.
