#!/bin/bash
set -e

# Default values
POLARIZATION="vv"
SWATH_NUM="1 2 3"
SLC_PATH="/workspace/data/slcs"

# Help
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: $0 [-p polarization] [-n swath_num] [-s slc_path]"
  exit 0
fi

# Parse args
while getopts "p:n:s:" opt; do
  case $opt in
    p) POLARIZATION="$OPTARG" ;;
    n) SWATH_NUM="$OPTARG" ;;
    s) SLC_PATH="$OPTARG" ;;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
  esac
done

# Env setup
export ISCE_STACK=/tmp/repos/isce2/contrib/stack
export PYTHONPATH=${PYTHONPATH}:${ISCE_STACK}
export PATH=${PATH}:${ISCE_STACK}/topsStack

cd /data/stack

# Build command safely
CMD=(
  "$ISCE_STACK/topsStack/stackSentinel.py"
  -s "$SLC_PATH"
  -d /data/dem/dem.wgs84
  -a /data/aux_cal
  -o /data/orbits
  -c all
  -W interferogram
  -n "$SWATH_NUM"
  -p "$POLARIZATION"
)

"${CMD[@]}"
