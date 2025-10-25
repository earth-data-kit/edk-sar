# edk-sar

A powerful Python wrapper around the ISCE2 (InSAR Scientific Computing Environment) framework that simplifies Interferometric Synthetic Aperture Radar (InSAR) analysis.

**edk-sar** provides an end-to-end workflow for processing SAR data, generating interferograms, and analyzing ground deformation with minimal setup. It abstracts the complexity of ISCE2 while adding modern data science tools like xarray for interactive analysis and visualization.

## Key Features

- **Automated InSAR Workflows**: Coregistration, interferogram generation, and displacement computation
- **xarray Integration**: Custom `.edk` accessor for seamless geocoding, plotting, and exporting
- **Interactive Visualization**: Built-in Folium maps with opacity controls and pixel value tooltips
- **GeoTIFF Export**: Cloud-Optimized GeoTIFF (COG) output with LZW compression
- **Docker-Based**: Consistent environment with ISCE2 and dependencies pre-configured

If you're looking to leverage the power of ISCE2 for InSAR analysis without dealing with its complexity directly, edk-sar is designed for you.

## Prerequisites

- **Docker**: Make sure you have [Docker](https://docs.docker.com/get-docker/) installed on your system. edk-sar uses Docker to provide a consistent environment and to run ISCE2 and related tools.
- **Python 3**: You should have Python 3 installed.
- **pip**: Ensure you have `pip3` installed for managing Python packages.

> **Note:** Some processes, such as phase unwrapping, require higher amounts of RAM. If your process is abruptly killed, try increasing the available RAM for your Docker container or system.


## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/earth-data-kit/edk-sar.git
   cd edk-sar
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

**Required dependencies:**
- `docker` - Docker SDK for Python
- `xarray` - Multi-dimensional array manipulation
- `rasterio` - Geospatial raster I/O
- `shapely` - Geometric operations
- `lxml` - XML processing
- `folium` - Interactive map visualization
- `branca` - Colormap support
- `matplotlib` - Plotting utilities
- `numpy` - Numerical operations

> **Note:** You will also need to have **GDAL** and its Python bindings installed on your system.
> - On Ubuntu:
>   ```bash
>   sudo apt-get install gdal-bin python3-gdal
>   ```
> - On macOS (with Homebrew):
>   ```bash
>   brew install gdal
>   pip3 install GDAL
>   ```
> - Or via pip (if you already have GDAL installed):
>   ```bash
>   pip3 install GDAL
>   ```
> Make sure the GDAL version matches your Python version.

## Quick Start

### 1. Setup Environment

Create required directories:
```bash
mkdir data tmp
```

Create a `.env` file with your credentials:
```bash
USGS_USERNAME=your_usgs_username
USGS_PASSWORD=your_usgs_password
COPERNICUS_DATASPACE_USERNAME=your_copernicus_dataspace_username
COPERNICUS_DATASPACE_PASSWORD=your_copernicus_dataspace_password
```

### 2. Run InSAR Processing

```python
import edk_sar as es

# Initialize environment
es.init(".env")

# Define path to your Sentinel-1 SLCs
slc_path = "/path/to/your_slc_folder"

# Run preprocessing workflows
es.workflows.coregister.run(slc_path)
es.workflows.interferograms.run(slc_path)
```

### 3. Load and Analyze Results

```python
import xarray as xr

# Load interferogram data
interferogram = xr.open_dataarray("path/to/interferogram.int")

# Compute phase, displacement, and coherence
phase = interferogram.edk.compute_phase()
displacement = interferogram.edk.compute_displacement()

# Geocode the data
phase_geocoded = phase.edk.geocode()
displacement_geocoded = displacement.edk.geocode()
```

### 4. Visualize and Export

```python
phase_map = phase_geocoded.edk.plot(colors="cyclic", opacity=0.8)
displacement_map = displacement_geocoded.edk.plot(colors="linear", opacity=0.8)

# Save individual maps
phase_map.save("phase_map.html")
displacement_map.save("displacement_map.html")

# Export to GeoTIFF (Cloud-Optimized GeoTIFF with LZW compression)
phase_geocoded.edk.export("phase.tif", dtype="float32", compress="LZW")
displacement_geocoded.edk.export("displacement.tif", dtype="float32", compress="LZW")
coherence_geocoded.edk.export("coherence.tif", dtype="float32", compress="LZW")
```

**Multi-layer Map Features:**
- 🗺️ Toggle layers on/off using the layer control panel
- 🎨 Individual colormaps for each layer (cyclic for phase, linear for displacement/coherence)
- 🔍 Opacity slider to adjust transparency of all layers
- 📍 Interactive pixel value tooltips on hover
- 💾 Export to HTML for easy sharing

## Project Structure

```
edk-sar/
├── edk_sar/
│   ├── workflows/
│   │   ├── base/
│   │   │   ├── xarray_accessor.py  # Custom .edk accessor
│   │   │   ├── constants.py        # Physical constants
│   │   │   └── helpers.py          # Utility functions
│   │   ├── coregister/             # SLC coregistration
│   │   └── interferograms/         # Interferogram generation
│   └── frameworks/                 # ISCE2 integration
├── examples/
│   └── sentinel1_mt_etna.ipynb     # Complete workflow example
└── requirements.txt
```

## Troubleshooting

**Out of Memory Errors:** Phase unwrapping requires significant RAM. Increase Docker memory allocation:
- Docker Desktop: Settings → Resources → Memory → Set to 8GB+

**Geocoding Fails:** Ensure geometry files exist in `edk_sar/data/stack/merged/geom_reference/`:
- `lon.rdr.vrt`
- `lat.rdr.vrt`

**Import Errors:** Verify all dependencies are installed, especially GDAL:
```bash
python3 -c "from osgeo import gdal; print(gdal.__version__)"
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

See [LICENSE](LICENSE) for details.
