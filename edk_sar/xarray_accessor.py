import os
import logging
import xarray as xr
import rasterio
import numpy as np
from edk_sar import edk_datashader
from osgeo import gdal

gdal.UseExceptions()

logger = logging.getLogger(__name__)


def get_gdal_dtype(numpy_dtype):
    # Map numpy data types to GDAL data types
    numpy_to_gdal_dtype = {
        np.uint8: gdal.GDT_Byte,
        np.uint16: gdal.GDT_UInt16,
        np.int16: gdal.GDT_Int16,
        np.uint32: gdal.GDT_UInt32,
        np.int32: gdal.GDT_Int32,
        np.float32: gdal.GDT_Float32,
        np.float64: gdal.GDT_Float64,
        np.complex64: gdal.GDT_CFloat32,
        np.complex128: gdal.GDT_CFloat64,
    }
    # Convert numpy dtype objects to their type
    if hasattr(numpy_dtype, "type"):
        numpy_dtype = numpy_dtype.type

    return numpy_to_gdal_dtype.get(
        numpy_dtype, gdal.GDT_Float32
    )  # Default to Float32 if type not found


@xr.register_dataarray_accessor("edk")
class EDKAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def geocode(self, lon_rdr, lat_rdr):
        da_src = self._obj

        # 1) Create an in-memory GDAL source from the DataArray
        arr = da_src.values
        nb, ny, nx = arr.shape

        mem_tif = "/vsimem/src.tif"
        tif_ds = gdal.GetDriverByName("GTiff").Create(
            mem_tif,
            nx,
            ny,
            nb,
            get_gdal_dtype(arr.dtype),
            options=["TILED=YES", "COMPRESS=DEFLATE"],
        )
        for i in range(nb):
            tif_ds.GetRasterBand(i + 1).WriteArray(arr[i])
        tif_ds.FlushCache()
        tif_ds = None  # close

        # No geotransform/projection on source (curvilinear); we'll supply GEOLOCATION arrays via VRT.

        # 2) Wrap the MEM dataset in a /vsimem/ VRT
        vrt_path = "/vsimem/src.vrt"
        vrt_ds = gdal.Translate(vrt_path, mem_tif, format="VRT")  # no georef required
        if vrt_ds is None:
            raise RuntimeError("Translate to VRT failed")

        # 2) Add GEOLOCATION metadata once (applies to all bands)
        from osgeo import osr

        # Create SRS object
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        wkt_4326 = srs.ExportToWkt()

        # Add GEOLOCATION metadata
        vrt_ds.SetMetadata(
            {
                "X_DATASET": lon_rdr,
                "X_BAND": "1",
                "Y_DATASET": lat_rdr,
                "Y_BAND": "1",
                "PIXEL_OFFSET": "0",
                "LINE_OFFSET": "0",
                "PIXEL_STEP": "1",
                "LINE_STEP": "1",
                "SRS": wkt_4326,  # <-- Full WKT fixes both "missing [" and "unhandled keyword"
            },
            "GEOLOCATION",
        )


        vrt_ds.FlushCache()

        # 4) Warp the VRT entirely in memory
        warped_ds = gdal.Warp(
            "",
            vrt_ds,
            format="MEM",
            dstSRS="EPSG:4326",
            multithread=True,
        )
        vrt_ds = None  # close

        # 6) Read the data and build an xarray.DataArray WITHOUT rasterio
        out_arr = warped_ds.ReadAsArray()
        if nb == 1:
            out_arr = np.array([out_arr])

        gt = warped_ds.GetGeoTransform()  # (x0, dx, rx, y0, ry, dy)
        # Build 1D x/y coords for north-up rasters (rx == ry == 0). Warp above uses north-up.

        x0, dx, rx, y0, ry, dy = gt
        nx_out = warped_ds.RasterXSize
        ny_out = warped_ds.RasterYSize
        # Pixel-center coordinates
        x = x0 + dx * (np.arange(nx_out) + 0.5)
        y = y0 + dy * (np.arange(ny_out) + 0.5)  # dy negative for north-up; that’s fine
        # Create DataArray; name & attrs carried from source if available
        da_warped = xr.DataArray(
            out_arr,
            dims=("band", "lat", "lon"),
            coords={"band": 1 + np.arange(nb), "lat": y, "lon": x},
            name=getattr(da_src, "name", None),
        )

        # Cleanup (you can unlink now if you don’t need bytes again)
        gdal.Unlink(vrt_path)

        # Close datasets
        warped_ds = None
        vrt_ds = None
        tif_ds = None

        return da_warped

    # TODO: Add legend block
    def plot(self, colors="linear", opacity=0.8):
        da = self._obj

        # Extract and preprocess data
        if np.iscomplexobj(da):
            logger.info("Found complex object, will plot phase")
            da = xr.apply_ufunc(np.angle, da)  # phase for complex data

        m = edk_datashader.Datashader(da)
        return m.plot()

    def export(self, output_path: str, compress="LZW"):
        """
        Export the geocoded DataArray to a GeoTIFF (COG recommended).
        """
        da = self._obj
        if not hasattr(da, "lon") or not hasattr(da, "lat"):
            raise ValueError(
                "DataArray must be geocoded (have lon/lat coords) before export."
            )

        # Create parent directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Tell rioxarray which are the spatial dims
        da_to_save = da.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=False)

        # Assign CRS (WGS84)
        da_to_save.rio.write_crs("EPSG:4326", inplace=True)

        # Export as GeoTIFF
        da_to_save.rio.to_raster(output_path, driver="COG", compress=compress)
        print(f"[OK] DataArray exported as COG: {output_path}")
