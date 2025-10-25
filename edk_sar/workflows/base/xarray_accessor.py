import os
import logging
import xarray as xr
import rasterio
import numpy as np
import folium
from branca import colormap as cm
import matplotlib.cm as mpl_cm
import matplotlib.colors as mcolors

logger = logging.getLogger(__name__)

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
            geom_root = self._find_data_root()

        # Find lon/lat raster files
        lon_rdr = self._find_geom_file(geom_root, "lon.rdr.vrt")
        lat_rdr = self._find_geom_file(geom_root, "lat.rdr.vrt")

        # Read lon/lat rasters
        with rasterio.open(lon_rdr) as lon_ds:
            lon = lon_ds.read(1)
        with rasterio.open(lat_rdr) as lat_ds:
            lat = lat_ds.read(1)

        # --- Correct 2D geocoding ---
        # Assign full 2D coordinates to the DataArray
        geocoded_da = da.copy()
        geocoded_da = geocoded_da.assign_coords({
            "lon": (("y", "x"), lon),
            "lat": (("y", "x"), lat)
        })

        # Preserve attributes
        geocoded_da.attrs.update(da.attrs)
        geocoded_da.attrs['geocoded'] = True

        logger.info(f"Updated coordinates using:\n  {lon_rdr}\n  {lat_rdr}")
        print(f"[OK] Updated coordinates using:\n  {lon_rdr}\n  {lat_rdr}")
        return geocoded_da


    def _find_data_root(self):
        """
        Search for edk_sar/data directory starting from current directory
        and moving up the directory tree.
        """
        current = os.path.abspath(".")

        # Try up to 5 levels up
        for _ in range(5):
            # Check if edk_sar/data exists here
            candidate = os.path.join(current, "edk_sar", "data")
            if os.path.exists(candidate):
                return candidate

            # Move up one level
            parent = os.path.dirname(current)
            if parent == current:  # reached root
                break
            current = parent

        # Default to current directory if not found
        return os.path.abspath(".")

    def _find_geom_file(self, root_dir, filename):
        for dirpath, _, files in os.walk(root_dir):
            if filename in files:
                return os.path.join(dirpath, filename)
        raise FileNotFoundError(f"{filename} not found under {root_dir}")

    def plot(self, colors="linear", opacity=0.8):

        da = self._obj

        # Extract and preprocess data
        if np.iscomplexobj(da.values):
            data = np.angle(da.values)  # phase for complex data
        else:
            data = da.values

        # If there's a band dimension, take the first band
        if "band" in da.dims:
            data = data[0]

        # Get lon/lat values
        lon = da.lon.values
        lat = da.lat.values
        # Before plotting, check:
        print(f"Data shape: {data.shape}")
        print(f"Data size in MB: {data.nbytes / 1024 / 1024:.2f}")

# If > 10MB, the JavaScript embedding might fail

        # For 2D coordinates, we need to handle flipping carefully
        # Folium expects: bounds = [[south, west], [north, east]]
        # Our data: row 0 = north, row -1 = south (normal for images)
        #           col 0 = east, col -1 = west (REVERSED - need to flip horizontally)

        if lon.ndim == 2 and lat.ndim == 2:
            mid_row = lon.shape[0] // 2
            mid_col = lat.shape[1] // 2

            # Check if longitude decreases left-to-right (needs horizontal flip)
            if lon[mid_row, 0] > lon[mid_row, -1]:
                print("[INFO] Flipping data horizontally for correct display")
                data = np.flip(data, axis=-1)  # flip along x-axis (columns)
                lon = np.flip(lon, axis=-1)

            # For latitude: if row 0 has higher lat than row -1, that's CORRECT
            # (row 0 = north/top, row -1 = south/bottom)
            # We do NOT need to flip vertically

        bounds = [[lat.min(), lon.min()], [lat.max(), lon.max()]]

        # Choose color palette
        if isinstance(colors, str):
            if colors.lower() == "cyclic":
                colors = ["blue", "cyan", "green", "yellow", "red", "magenta", "blue"]
            elif colors.lower() == "linear":
                colors = ["blue", "cyan", "green", "yellow", "red"]
            else:
                raise ValueError("Invalid color mode. Use 'linear', 'cyclic', or a custom list.")

        # Create Folium map
        m = folium.Map(
            location=[(lat.min() + lat.max()) / 2, (lon.min() + lon.max()) / 2],
            zoom_start=10,
            tiles="OpenStreetMap"
        )

        # Create colormap for display
        colormap = cm.LinearColormap(colors=colors, vmin=np.nanmin(data), vmax=np.nanmax(data))
        colormap.caption = "Pixel Value"
        colormap.add_to(m)

        # Matplotlib colormap for rendering
        mpl_colormap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", colors)
        norm = mcolors.Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data))
        rgba_data = mpl_colormap(norm(data))
        rgba_data = (rgba_data * 255).astype(np.uint8)

        # Add image overlay
        overlay = folium.raster_layers.ImageOverlay(
            image=rgba_data,
            bounds=bounds,
            opacity=opacity,
            interactive=True,
            cross_origin=False
        )
        overlay.add_to(m)
        folium.LayerControl().add_to(m)

        # Add opacity control
        opacity_slider = f"""
        <div id='opacity-control' style="
            position: fixed;
            bottom: 40px;
            left: 10px;
            z-index: 9999;
            background: white;
            padding: 6px 10px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        ">
            <label for='opacityRange'><b>Opacity</b></label>
            <input type='range' id='opacityRange' min='0' max='1' value='{opacity}' step='0.01' />
        </div>

        <script>
        (function waitForMap() {{
            var map = null;
            for (var k in window) {{
                try {{
                    if (window[k] && window[k] instanceof L.Map) {{
                        map = window[k];
                        break;
                    }}
                }} catch (e) {{}}
            }}

            if (!map) {{
                setTimeout(waitForMap, 200);
                return;
            }}

            var imageOverlay = null;
            map.eachLayer(function(layer) {{
                if (layer instanceof L.ImageOverlay) {{
                    imageOverlay = layer;
                    return;
                }}
            }});

            var slider = document.getElementById('opacityRange');
            if (!slider) return;
            if (imageOverlay && typeof imageOverlay.options.opacity !== 'undefined') {{
                slider.value = imageOverlay.options.opacity;
            }}

            slider.addEventListener('input', function(e) {{
                var val = parseFloat(e.target.value);
                if (imageOverlay && typeof imageOverlay.setOpacity === 'function') {{
                    imageOverlay.setOpacity(val);
                }}
            }});
        }})();
        </script>
        """
        m.get_root().html.add_child(folium.Element(opacity_slider))

        # --- Add pixel hover tooltip ---
        hover_js = f"""
        <style>
        #pixelValueTooltip {{
            position: fixed;
            pointer-events: none;
            background: rgba(0,0,0,0.85);
            color: white;
            padding: 6px 10px;
            border-radius: 5px;
            font-size: 12px;
            font-family: monospace;
            z-index: 10000;
            display: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
            white-space: nowrap;
        }}
        </style>
        <div id="pixelValueTooltip"></div>

        <script>
        (function() {{
            var map = null;
            var imageOverlay = null;

            // Wait for map to be ready
            for (var k in window) {{
                try {{
                    if (window[k] && window[k] instanceof L.Map) {{
                        map = window[k];
                        break;
                    }}
                }} catch (e) {{}}
            }}
            if (!map) {{
                setTimeout(arguments.callee, 200);
                return;
            }}

            // Find the image overlay
            map.eachLayer(function(layer) {{
                if (layer instanceof L.ImageOverlay) {{
                    imageOverlay = layer;
                }}
            }});

            if (!imageOverlay) {{
                console.warn("No ImageOverlay found");
                return;
            }}

            var tooltip = document.getElementById("pixelValueTooltip");
            if (!tooltip) return;

            var data = {np.nan_to_num(data).tolist()};
            var lats = {lat.tolist()};
            var lons = {lon.tolist()};
            var nrows = data.length;
            var ncols = data[0].length;

            var bounds = {bounds};
            var minLat = bounds[0][0];
            var minLon = bounds[0][1];
            var maxLat = bounds[1][0];
            var maxLon = bounds[1][1];

            function isInsideBounds(lat, lon) {{
                return lat >= minLat && lat <= maxLat && lon >= minLon && lon <= maxLon;
            }}

            function getPixelValue(lat, lon) {{
                // Find closest pixel by searching 2D lat/lon arrays
                var minDist = Infinity;
                var bestRow = 0, bestCol = 0;

                for (var i = 0; i < nrows; i++) {{
                    for (var j = 0; j < ncols; j++) {{
                        var pixelLat = lats[i][j];
                        var pixelLon = lons[i][j];
                        var dist = Math.sqrt(Math.pow(pixelLat - lat, 2) + Math.pow(pixelLon - lon, 2));

                        if (dist < minDist) {{
                            minDist = dist;
                            bestRow = i;
                            bestCol = j;
                        }}
                    }}
                }}

                return {{
                    value: data[bestRow][bestCol],
                    nearestLat: lats[bestRow][bestCol],
                    nearestLon: lons[bestRow][bestCol]
                }};
            }}

            var isOverImage = false;

            map.on('mousemove', function(e) {{
                var lat = e.latlng.lat;
                var lon = e.latlng.lng;

                // Check if mouse is within image bounds
                if (isInsideBounds(lat, lon)) {{
                    isOverImage = true;
                    var result = getPixelValue(lat, lon);
                    var val = result.value;

                    if (val !== undefined && !isNaN(val)) {{
                        tooltip.innerHTML =
                            "<b>Pixel Value:</b> " + val.toFixed(4) + "<br>" +
                            "<b>Lat:</b> " + result.nearestLat.toFixed(6) + "<br>" +
                            "<b>Lon:</b> " + result.nearestLon.toFixed(6);
                        tooltip.style.left = (e.originalEvent.clientX + 15) + "px";
                        tooltip.style.top = (e.originalEvent.clientY - 10) + "px";
                        tooltip.style.display = "block";
                    }} else {{
                        tooltip.style.display = "none";
                    }}
                }} else {{
                    // Mouse is outside image bounds
                    if (isOverImage) {{
                        tooltip.style.display = "none";
                        isOverImage = false;
                    }}
                }}
            }});

            map.on('mouseout', function() {{
                tooltip.style.display = "none";
                isOverImage = false;
            }});
        }})();
        </script>
        """
        m.get_root().html.add_child(folium.Element(hover_js))

        return m

    def export(self, output_path: str, dtype=None, compress="LZW"):
        """
        Export the geocoded DataArray to a GeoTIFF (COG recommended).
        """
        da = self._obj
        if not hasattr(da, "lon") or not hasattr(da, "lat"):
            raise ValueError("DataArray must be geocoded (have lon/lat coords) before export.")

        # Create parent directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Set dtype if provided
        if dtype is not None:
            da_to_save = da.astype(dtype)
        else:
            da_to_save = da.copy()

        # For 2D coordinates (non-uniform grids), we need to use 1D coordinates
        # by extracting the center line values to create a proper affine transform
        if da_to_save.lon.ndim == 2 and da_to_save.lat.ndim == 2:
            # Extract 1D coordinate vectors from the 2D arrays
            # Use the middle row for lon and middle column for lat
            mid_row = da_to_save.lon.shape[0] // 2
            mid_col = da_to_save.lon.shape[1] // 2

            lon_1d = da_to_save.lon.values[mid_row, :]
            lat_1d = da_to_save.lat.values[:, mid_col]

            # Ensure coordinates are sorted in ascending order
            if lon_1d[0] > lon_1d[-1]:
                print("[INFO] Flipping longitude coordinates to ascending order")
                da_to_save = da_to_save.isel(x=slice(None, None, -1))
                lon_1d = lon_1d[::-1]

            if lat_1d[0] > lat_1d[-1]:
                print("[INFO] Flipping latitude coordinates to ascending order")
                da_to_save = da_to_save.isel(y=slice(None, None, -1))
                lat_1d = lat_1d[::-1]

            # Recompute after potential flipping
            lon_1d = da_to_save.lon.values[mid_row, :]
            lat_1d = da_to_save.lat.values[:, mid_col]

            # Create new 1D coordinate DataArray
            da_to_save = da_to_save.assign_coords({
                "x": lon_1d,
                "y": lat_1d
            })

            # Remove the 2D lon/lat coordinates
            da_to_save = da_to_save.drop_vars(["lon", "lat"])

        # Tell rioxarray which are the spatial dims
        da_to_save = da_to_save.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=False)

        # Assign CRS (WGS84)
        da_to_save.rio.write_crs("EPSG:4326", inplace=True)

        # Export as GeoTIFF
        da_to_save.rio.to_raster(
            output_path,
            driver="COG",
            compress=compress
        )
        print(f"[OK] DataArray exported as COG: {output_path}")

    





