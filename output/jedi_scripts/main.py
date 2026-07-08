
from datetime import datetime, timedelta
import sys

from generate_truth import generate_truth
from generate_initial_background import generate_initial_background
from generate_obs import generate_obs
from generate_forecasts import generate_forecasts
from generate_Ya import generate_Ya

from iso8601 import iso8601
from utc import utc
from letkf import letkf
from compute_analysis_error import compute_analysis_error

# --- Usage: python main.py <options> ---

ensemble_size = 10

truth_initial_time    = datetime(2009, 12, 15, 0)
truth_forecast_length = timedelta(days=210)

cycling_start_time    = datetime(2010, 1, 1, 0)
cycling_interval      = timedelta(hours=12)
cycling_end_time      = datetime(2010, 1, 2, 0)

nx = 40
ny = 20

# Allowed arguments
options = {
    "truth",
    "initial_background",
    "obs",
    "letkf",
}

# Parse command-line arguments
if len(sys.argv) != 2:
    print("Usage: python main.py <options>")
    print("       <options> must be one of:", ", ".join(options))
    sys.exit(1)

option = sys.argv[1]

if option not in options:
    print(f"Error: option '{option}' is not valid.")
    print(f"       Choose from: {', '.join(options)}")
    sys.exit(1)

# Time check
if cycling_end_time > truth_initial_time + truth_forecast_length:
    raise ValueError(
        f"cycling_end_time ({cycling_end_time}) exceeds forecast range "
        f"({truth_initial_time + truth_forecast_length}) from truth_initial_time + truth_forecast_length.\n"
        "You will run out of truth data. Please shorten cycling_end_time or extend forecast length."
    )

match option:
    # Generate truth   
    case "truth":
        generate_truth(
            forecast_length = iso8601(truth_forecast_length), 
            frequency       = iso8601(cycling_interval / 2),
            nx              = nx, 
            ny              = ny, 
            date            = utc(truth_initial_time)
        )

    # Generate initial background
    case "initial_background":
        generate_initial_background(
            ensemble_size      = ensemble_size,
            nx                 = nx,
            ny                 = ny,
            analysis_time      = cycling_start_time + cycling_interval / 2,
            cycling_interval   = cycling_interval,
            truth_initial_time = truth_initial_time
        )

    # Generate observations
    case "obs":
        generate_obs(
            start_time         = cycling_start_time,
            end_time           = cycling_end_time,
            first_obs_time     = cycling_interval / 2,
            period             = cycling_interval,
            truth_initial_time = truth_initial_time,
            nx                 = nx,
            ny                 = ny
        ) 

    # Run LETKF
    case "letkf":   
        window_start_time = cycling_start_time
        cycle_index = 1 
        while window_start_time < cycling_end_time:
            analysis_time = window_start_time + cycling_interval / 2
            print(f"=== {cycle_index}. Analysis time: {analysis_time} ===")
            letkf(
                window_start_time = window_start_time,
                analysis_time     = analysis_time,
                cycling_interval  = cycling_interval,
                ensemble_size     = ensemble_size,
                nx                = nx,
                ny                = ny,
                rtpp              = 0.5,
                mult              = 1.1,
                initial           = window_start_time == cycling_start_time
            )
            compute_analysis_error(
                truth_initial_time = truth_initial_time, 
                analysis_time      = analysis_time, 
                cycling_interval   = cycling_interval, 
                ensemble_size      = ensemble_size,
                initial            = window_start_time == cycling_start_time
            )
            generate_forecasts(
                analysis_time    = analysis_time,
                cycling_interval = cycling_interval,
                ensemble_size    = ensemble_size,
                nx               = nx,
                ny               = ny,
            )
            # generate_Ya(
            #     analysis_time    = analysis_time,
            #     cycling_interval = cycling_interval,
            #     ensemble_size    = ensemble_size,
            #     nx               = nx,
            #     ny               = ny,
            # )
            window_start_time += cycling_interval
            cycle_index += 1
