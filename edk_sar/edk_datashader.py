import numpy as np
import xarray as xr
import rioxarray
import holoviews as hv
import geoviews as gv
import panel as pn
import datashader as ds
import cartopy.crs as ccrs
import colorcet as cc
from holoviews.streams import Tap
from holoviews import opts
from holoviews.operation.datashader import rasterize, shade
import datashader.transfer_functions as tf
from holoviews.operation import decimate
from osgeo import osr
from pyproj import Transformer

hv.extension("bokeh")
gv.extension("bokeh")
pn.extension()


class Datashader:
    def __init__(self, da):
        if da.ndim == 2 and "lon" in da.coords and "lat" in da.coords:
            self.da = da
        else:
            raise ValueError(
                "DataArray must have lon and lat coordinates and should have only two dimensions"
            )

    def rasterize(self):
        lon = self.da["lon"].values  # 1D
        lat = self.da["lat"].values  # 1D

        vals = self.da.values
        x_merc, y_merc = ds.utils.lnglat_to_meters(lon, lat)

        quad = hv.QuadMesh((x_merc, y_merc, vals), kdims=["lon", "lat"])

        dyn = rasterize(quad)

        # dyn = rasterize(img)  # this creates a dynamic, server-side aggregation
        shaded = shade(dyn, cmap=cc.fire).opts(
            width=600, height=600, tools=["tap"], active_tools=["tap"]
        )
        return shaded

    def opacity(self, shaded):
        alpha_slider = pn.widgets.FloatSlider(
            name="Opacity", start=0.0, end=1.0, step=0.01, value=0.8
        )

        # ---- 4. Tie the slider's value to the plot's 'alpha' option
        # apply.opts will "replay" opts reactively when the parameter changes
        shaded_with_alpha = shaded.apply.opts(alpha=alpha_slider.param.value)
        return shaded_with_alpha, alpha_slider

    def basemap(self):
        tiles = gv.tile_sources.OSM()
        return tiles

    def plot(self):
        shaded = self.rasterize()
        shaded_with_alpha, alpha_slider = self.opacity(shaded)

        # Interactivity
        #
        # 4. Tap stream: listens for clicks on the plot
        #
        tap_stream = hv.streams.Tap(source=shaded_with_alpha, x=None, y=None)

        #
        # 5. Popup panel, initially empty
        #
        popup_card = pn.Card(
            pn.pane.Markdown("Click on the plot 👆"),
            title="Details",
            collapsible=False,
            width=300,
        )

        def _on_tap(x, y, **kwargs):
            """
            x, y are in data coordinates where the user clicked.
            We'll do 3 things:
            - find nearest point in the original dataframe
            - update popup text
            - (optional) you could trigger more UI here: table, image, etc.
            """
            if x is None or y is None:
                return
            try:
                # Convert lon, lat from EPSG:3857 to EPSG:4326
                srs_3857 = osr.SpatialReference()
                srs_3857.ImportFromEPSG(3857)
                srs_4326 = osr.SpatialReference()
                srs_4326.ImportFromEPSG(4326)
                trans = osr.CoordinateTransformation(srs_3857, srs_4326)
                lat, lon, _ = trans.TransformPoint(x, y)

                val = self.da.sel(lon=lon, lat=lat, method="nearest").values

                popup_md = f"""
                    ### lon: {lon}
                    ### lat: {lat}
                    ### val: {val}
                """
                popup_card.objects = [pn.pane.Markdown(popup_md)]
            except Exception as e:
                popup_md = f"""
                    ### Error: {e.__str__()}
                """
                popup_card.objects = [pn.pane.Markdown(popup_md)]

        # connect the callback to the stream
        tap_stream.add_subscriber(_on_tap)

        tiles = self.basemap()

        proj = ccrs.GOOGLE_MERCATOR  # Web Mercator in meters
        map_view = (tiles * shaded_with_alpha).opts(
            hv.opts.Overlay(projection=proj, frame_width=600)
        )

        m = pn.Row(pn.Column(alpha_slider, map_view), popup_card).servable()
        return m
