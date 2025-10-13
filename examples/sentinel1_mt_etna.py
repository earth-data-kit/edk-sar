"""
Example: Mount Etna Sentinel-1 Displacement Mapping with EDK-SAR
================================================================

This example demonstrates how to use **EDK-SAR** to generate a line-of-sight
(LOS) displacement map and coherence map from Sentinel-1 SLC data over Mount Etna.

The workflow includes:
1. Initializing the EDK-SAR environment.
2. Co-registering Sentinel-1 SLCs.
3. Generating interferograms.
4. Loading and geocoding interferogram and coherence files.
5. Computing phase and LOS displacement.
6. Exporting results as GeoTIFFs.
7. Visualizing the outputs on an interactive folium map.

This example showcases how to perform an end-to-end InSAR analysis with minimal code.
"""

import edk_sar as es
import xarray as xr
import numpy as np
import webbrowser
from edk_sar.workflows.base import xarray_accessor  # noqa: F401  (register accessor)
from edk_sar.workflows.base.constants import SENTINEL_WAVELENGTH as WAVELENGTH


def run_mount_etna_workflow():
    """Main function to process Sentinel-1 data over Mount Etna and generate LOS displacement."""
    
    #  Initialize environment
    env_path = ".env"
    es.init(env_path)
    print("[OK] Environment initialized")

    # Define path to Mount Etna Sentinel-1 SLCs
    slc_path = "edk_sar/data/slc"

    # Run preprocessing workflows
    es.workflows.coregister.run(slc_path)
    es.workflows.interferograms.run(slc_path)
    print("[OK] Coregistration and interferogram generation complete")

    # Load interferogram and coherence (update dates based on your dataset)
    intf_path = "path to filt_fine.int.vrt"
    coh_path = "path to filt_fine.cor.vrt"

    interferogram = xr.open_dataarray(intf_path, engine="rasterio")
    coherence = xr.open_dataarray(coh_path, engine="rasterio")

    # Geocode interferogram and coherence
    geocoded_interferogram = interferogram.edk.geocode()
    geocoded_coherence = coherence.edk.geocode()
    print("[OK] Geocoding complete")

    # Compute phase from complex interferogram
    phase = xr.apply_ufunc(np.angle, geocoded_interferogram)
    geocoded_phase = phase.edk.geocode()
    print(f"Phase range: {geocoded_phase.min().values:.3f} to {geocoded_phase.max().values:.3f}")

    # Compute LOS displacement
    displacement = (geocoded_phase * WAVELENGTH) / (4 * np.pi)
    displacement.attrs.update({
        "units": "meters",
        "description": "Line-of-sight displacement over Mount Etna"
    })
    print("[OK] LOS displacement computed")

    # Export all outputs as GeoTIFFs
    geocoded_phase.edk.export("examples/mount_etna_phase.tif")
    geocoded_coherence.edk.export("examples/mount_etna_coherence.tif")
    displacement.edk.export("examples/mount_etna_displacement.tif")
    print("[OK] Exported GeoTIFFs to examples/")

    # Visualization using folium
    m_disp = displacement.edk.plot(colors=['blue', 'cyan', 'green'], opacity=0.7)
    m_disp.save("examples/mount_etna_displacement_map.html")
    webbrowser.open("file://examples/mount_etna_displacement_map.html")
    print("[OK] Displacement map opened in browser")

    m_phase = geocoded_phase.edk.plot(colors=['purple','yellow','red'], opacity=0.7)
    m_phase.save("examples/mount_etna_phase_map.html")
    webbrowser.open("file://examples/mount_etna_phase_map.html")
    

    m_coh = geocoded_coherence.edk.plot(colors=['blue','cyan','green'], opacity=0.7)
    m_coh.save("examples/mount_etna_coherence_map.html")
    webbrowser.open("file://examples/mount_etna_coherence_map.html")


if __name__ == "__main__":
    run_mount_etna_workflow()
