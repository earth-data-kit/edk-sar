export ISCE_STACK=/tmp/repos/isce2/contrib/stack
export PYTHONPATH=${PYTHONPATH}:${ISCE_STACK}


# For TOPS
export PATH=${PATH}:${ISCE_STACK}/topsStack

COPERNICUS_DATASPACE_USERNAME=$1
COPERNICUS_DATASPACE_PASSWORD=$2

if [[ -n "$COPERNICUS_DATASPACE_USERNAME" && -n "$COPERNICUS_DATASPACE_PASSWORD" ]]; then
    echo "machine dataspace.copernicus.eu login $COPERNICUS_DATASPACE_USERNAME password $COPERNICUS_DATASPACE_PASSWORD" >> ~/.netrc
    chmod 600 ~/.netrc
fi

cd /data/stack
/tmp/repos/isce2/contrib/stack/topsStack/stackSentinel.py -s /data/slcs -d /data/dem/dem.wgs84 -a /data/aux_cal -o /data/orbits -W slc -n '1 2 3'