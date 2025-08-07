COPERNICUS_DATASPACE_USERNAME="${COPERNICUS_DATASPACE_USERNAME}"
COPERNICUS_DATASPACE_PASSWORD="${COPERNICUS_DATASPACE_PASSWORD}"

if [[ -n "$COPERNICUS_DATASPACE_USERNAME" && -n "$COPERNICUS_DATASPACE_PASSWORD" ]]; then
    echo "machine dataspace.copernicus.eu login $COPERNICUS_DATASPACE_USERNAME password $COPERNICUS_DATASPACE_PASSWORD" >> ~/.netrc
    chmod 600 ~/.netrc
fi

if [[ -n "$USGS_USERNAME" && -n "$USGS_PASSWORD" ]]; then
    echo "machine urs.earthdata.nasa.gov login $USGS_USERNAME password $USGS_PASSWORD" >> ~/.netrc
    chmod 600 ~/.netrc
fi