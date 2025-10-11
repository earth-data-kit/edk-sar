import os
import xarray as xr
import rasterio
import numpy as np
import folium
import branca.colormap as cm


@xr.register_dataarray_accessor("edk")
class EDKAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def geocode(self, geom_root=None):
        da = self._obj

        # If already geocoded, return itself
        if "lon" in da.coords and "lat" in da.coords:
            return da

        # Determine geom_reference folder
        if geom_root is None:
            geom_root = os.path.abspath(".")
        lon_rdr, lat_rdr = self._find_geom_file(geom_root, "lon.rdr.vrt"), self._find_geom_file(geom_root, "lat.rdr.vrt")

        # Read lon/lat rasters
        with rasterio.open(lon_rdr) as lon_ds:
            lon = lon_ds.read(1)
        with rasterio.open(lat_rdr) as lat_ds:
            lat = lat_ds.read(1)

        lon_vec = lon[0, :]      
        lat_vec = lat[:, 0]      

        geocoded_da = da.copy()
        geocoded_da = geocoded_da.assign_coords({
            "x": ("x", lon_vec),
            "y": ("y", lat_vec)
        })

        # Rename dimensions
        geocoded_da = geocoded_da.rename({"x": "lon", "y": "lat"})

        # Preserve attributes
        geocoded_da.attrs.update(da.attrs)
        geocoded_da.attrs['geocoded'] = True

        print(f"[OK] Updated coordinates using:\n  {lon_rdr}\n  {lat_rdr}")
        return geocoded_da

    def _find_geom_file(self, root_dir, filename):
        for dirpath, _, files in os.walk(root_dir):
            if filename in files:
                return os.path.join(dirpath, filename)
        raise FileNotFoundError(f"{filename} not found under {root_dir}")
    
    def plot(self, colors=None, opacity=0.8):

        da = self._obj

        # If there is a band dimension, take the first one
        if "band" in da.dims:
            data = np.real(da.isel(band=0).values)  # first band, real part if complex
        else:
            data = np.real(da.values)

        # Use lon/lat coordinates
        lon = da.lon.values
        lat = da.lat.values

        # Map bounds
        bounds = [[lat.min(), lon.min()], [lat.max(), lon.max()]]

        # Create folium map centered
        m = folium.Map(
            location=[(lat.min() + lat.max()) / 2, (lon.min() + lon.max()) / 2],
            zoom_start=12,
        )

        # Colormap: use cyclic for phase if not provided
        if colors is None:
            colormap = cm.LinearColormap(
                colors=["blue", "cyan", "green", "yellow", "red", "magenta", "blue"],
                vmin=-np.pi,
                vmax=np.pi
            )
        else:
            colormap = cm.LinearColormap(colors, vmin=np.nanmin(data), vmax=np.nanmax(data))

        # Convert data to RGBA using colormap
        rgba_data = np.empty(data.shape + (4,), dtype=np.float32)
        for i in range(data.shape[0] if data.ndim == 2 else 1):
            rgba_data[i] = np.array([colormap.rgba_floats_tuple(val) if not np.isnan(val) else (0,0,0,0) for val in data[i]])

        # Apply ImageOverlay
        overlay = folium.raster_layers.ImageOverlay(
            image=rgba_data.squeeze(),  # remove extra dim if present
            bounds=bounds,
            opacity=opacity,
            interactive=True,
        )
        overlay.add_to(m)
        folium.LayerControl().add_to(m)
        return m
    
    def export(self, output_path: str, dtype=None, compress="LZW"):
        """
        Export the geocoded DataArray to a GeoTIFF (COG recommended).
        """
        da = self._obj
        if not hasattr(da, "lon") or not hasattr(da, "lat"):
            raise ValueError("DataArray must be geocoded (have lon/lat coords) before export.")

        # Set dtype if provided
        if dtype is not None:
            da_to_save = da.astype(dtype)
        else:
            da_to_save = da

        # Tell rioxarray which are the spatial dims
        da_to_save = da_to_save.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=False)

        # Assign CRS (WGS84)
        da_to_save.rio.write_crs("EPSG:4326", inplace=True)

        # Export as GeoTIFF
        da_to_save.rio.to_raster(
            output_path,
            driver="COG",
            compress=compress
        )
        print(f"[OK] DataArray exported as COG: {output_path}")
