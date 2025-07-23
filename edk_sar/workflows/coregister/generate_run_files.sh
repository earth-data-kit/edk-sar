export ISCE_STACK=/tmp/repos/isce2/contrib/stack
export PYTHONPATH=${PYTHONPATH}:${ISCE_STACK}


# For TOPS
export PATH=${PATH}:${ISCE_STACK}/topsStack

cd /data/stack
/tmp/repos/isce2/contrib/stack/topsStack/stackSentinel.py -s /data/slcs -d /data/dem/dem.wgs84 -a /data/aux_cal -o /data/orbits -W slc -n '1 2 3'