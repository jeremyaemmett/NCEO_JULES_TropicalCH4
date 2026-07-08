#!/usr/bin/env python3

from __future__ import annotations
import subprocess
import sys
from datetime import datetime, timezone
from iso8601 import iso8601

# --- constants (edit as needed) ---------------------------------------------
TIME = sys.argv[1] if len(sys.argv) > 1 else "2010-01-01T06:00:00Z"
START= "2009-12-15T00:00:00Z"

_TIME_FMT = "%Y-%m-%dT%H:%M:%SZ"
def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, _TIME_FMT).replace(tzinfo=timezone.utc)

LEAD = iso8601(_parse(TIME) - _parse(START))

# File templates identical to the Bash version
OBS_FILE = f"truth.obs3d.nc"
TRUTH_FILE = f"Data/truth.fc.{START}.{LEAD}.nc"
ANALYSIS_FILE = f"Data/letkf.bgn.000000.an.{TIME}.nc"

# --- helpers ----------------------------------------------------------------
def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main() -> None:
    # 1) Plot the truth field (with wind)
    run([sys.executable, "plot.py", "qg", "fields", "--plotwind", TRUTH_FILE])

    # 2) Plot analysis error + observation locations
    run([
        sys.executable,
        "plot.py",
        "qg",
        "fields",
        "--output",
        "qg_analysis_error",
        ANALYSIS_FILE,
        TRUTH_FILE,
        "--plotObsLocations",
        f"Data/{OBS_FILE}",
        "--title",
        "Analysis error & Obs locations",
    ])

    # 3) Extract observation file values to text
    run([
        sys.executable,
        "plot.py",
        "qg",
        "obs",
        "--output",
        f"qg_obs_{TIME}",
        f"Data/{OBS_FILE}",
    ])

if __name__ == "__main__":
    main()
