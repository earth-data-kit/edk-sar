# edk-sar

This repository provides a convenient wrapper around the ISCE2 (InSAR Scientific Computing Environment) framework, making it easy for users to perform InSAR (Interferometric Synthetic Aperture Radar) analysis. 

With edk-sar, you get a collection of tools and utilities that simplify the process of running InSAR workflows. By abstracting and automating many of the steps required by ISCE2, this repo enables researchers, engineers, and enthusiasts to efficiently process SAR data, generate interferograms, and analyze ground deformation with minimal setup.

If you're looking to leverage the power of ISCE2 for InSAR analysis without dealing with its complexity directly, edk-sar is designed for you.

## Prerequisites

- **Docker**: Make sure you have [Docker](https://docs.docker.com/get-docker/) installed on your system. edk-sar uses Docker to provide a consistent environment and to run ISCE2 and related tools.
- **Python 3**: You should have Python 3 installed.
- **pip**: Ensure you have `pip3` installed for managing Python packages.

> **Note:** Some processes, such as phase unwrapping, require higher amounts of RAM. If your process is abruptly killed, try increasing the available RAM for your Docker container or system.


## Installation

1. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
> **Note:** You will also need to have **GDAL** and its Python bindings installed on your system.  
> - On Ubuntu, you can install them with:  
>   ```bash
>   sudo apt-get install gdal-bin python3-gdal
>   ```
> - On Mac (with Homebrew):  
>   ```bash
>   brew install gdal
>   pip3 install GDAL
>   ```
> - Or via pip (if you already have GDAL installed):  
>   ```bash
>   pip3 install GDAL
>   ```
> Make sure the GDAL version matches your Python version.

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/earth-data-kit/edk-sar.git
   cd edk-sar
   ```

2. **Create required directories:**
   ```bash
   mkdir data tmp
   ```

3. **Create a `.env` file**  
   Add your credentials for USGS Earth Data and Copernicus Dataspace Ecosystem.  
   Example `.env`:
   ```
   USGS_USERNAME=your_usgs_username
   USGS_PASSWORD=your_usgs_password
   COPERNICUS_USERNAME=your_copernicus_username
   COPERNICUS_PASSWORD=your_copernicus_password
   ```

4. **Initialize the environment in Python:**
   ```python
   import edk_sar as es

   env_path = ".env"  # Path to your .env file
   es.init(env_path)
   ```

5. **Run the coregistration workflow:**
   ```python
   slc_path = "/path/to/your_slc_folder"  # Path to your downloaded SLCs
   es.workflows.coregister.run(slc_path) # To run coregistration workflow
   es.workflows.interferograms.run(slc_path) # To run interferograms workflow
   ```

Replace the example paths and credentials with your actual information.
