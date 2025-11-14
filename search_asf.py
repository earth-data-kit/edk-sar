import os
from pathlib import Path

try:
    import asf_search as asf
except ImportError:
    raise ImportError("Install with: pip install asf_search")

def download_sar_data(
    lon,
    lat,
    start_date,
    end_date,
    platform=None,
    output_dir="./data/new_slc",
    processing_level=None,
    max_results=50
):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    username = os.environ.get('USGS_USERNAME')
    password = os.environ.get('USGS_PASSWORD')
    
    if not username or not password:
        raise ValueError(
            "Set credentials:\n"
            "  export USGS_USERNAME='your_username'\n"
            "  export USGS_PASSWORD='your_password'\n"
            "Register at: https://urs.earthdata.nasa.gov/"
        )
    
    print(f"Searching ASF for SAR data...")
    print(f"  Location: {lon}, {lat}")
    print(f"  Dates: {start_date} to {end_date}")
    if platform:
        print(f"  Platform: {platform}")
    else:
        print(f"  Platform: ALL (Sentinel-1, ALOS, RADARSAT, etc.)")
    if processing_level:
        print(f"  Processing level: {processing_level}")
    
    opts = {
        'intersectsWith': f"POINT({lon} {lat})",
        'start': start_date,
        'end': end_date,
        'maxResults': max_results
    }
    
    # Add platform filter if specified
    if platform:
        platform_map = {
            'SENTINEL1': asf.PLATFORM.SENTINEL1,
            'ALOS': asf.PLATFORM.ALOS,
            'RADARSAT': asf.PLATFORM.RADARSAT,
            'ERS': asf.PLATFORM.ERS,
            'ERS1': asf.PLATFORM.ERS1,
            'ERS2': asf.PLATFORM.ERS2,
            'JERS': asf.PLATFORM.JERS,
            'SMAP': asf.PLATFORM.SMAP,
            'SEASAT': asf.PLATFORM.SEASAT,
            'UAVSAR': asf.PLATFORM.UAVSAR,
            'AIRSAR': asf.PLATFORM.AIRSAR,
            'SIRC': asf.PLATFORM.SIRC,
            'NISAR': asf.PLATFORM.NISAR
        }
        if platform.upper() in platform_map:
            opts['platform'] = platform_map[platform.upper()]
        else:
            print(f"[WARNING] Unknown platform '{platform}', searching all platforms")
            print(f"Available: {', '.join(platform_map.keys())}")
    
    if processing_level:
        opts['processingLevel'] = processing_level
    
    results = asf.search(**opts)
    print(f"Found {len(results)} scenes")
    
    if not results:
        print("No scenes found")
        return []
    
    # Show what was found
    total_gb = sum(r.properties.get('bytes', 0) for r in results) / 1e9
    platforms = set(r.properties.get('platform', 'N/A') for r in results)
    
    print(f"  Platforms: {', '.join(sorted(platforms))}")
    print(f"  Total size: {total_gb:.1f} GB")
    
    print(f"\nDownloading to {output_dir}...")
    session = asf.ASFSession().auth_with_creds(username, password)
    
    downloaded = []
    for i, result in enumerate(results, 1):
        scene_name = result.properties['sceneName']
        output_file = Path(output_dir) / f"{scene_name}.zip"
        
        if output_file.exists():
            print(f"[{i}/{len(results)}] Skipping {scene_name} (exists)")
            downloaded.append(str(output_file))
            continue
        
        size_gb = result.properties.get('bytes', 0) / 1e9
        print(f"[{i}/{len(results)}] {scene_name} ({size_gb:.1f} GB)")
        result.download(path=output_dir, session=session)
        downloaded.append(str(output_file))
    
    print(f"Downloaded {len(downloaded)} scenes to {output_dir}")
    return downloaded

if __name__ == "__main__":
    # Example 1: Download Sentinel-1 data
    #files = download_sar_data(
    #    lon=130.6,
    #    lat=33.3,
    #    start_date="2016-03-01",
    #    end_date="2016-05-31",
    #    platform="SENTINEL1",
    #    processing_level="SLC",
    #    max_results=10
    #)
    
    # Example 2: Download ALOS data
     files = download_sar_data(
         lon=130.6,
         lat=33.3,
         start_date="2006-01-01",
         end_date="2011-12-31",
         platform="ALOS",
         max_results=10
     )
    
    # Example 3: Download ALL available SAR data (no platform specified)
    # files = download_sar_data(
    #     lon=130.6,
    #     lat=33.3,
    #     start_date="2016-03-01",
    #     end_date="2016-05-31",
    #     max_results=50
    # )
    
     print(f"\nFiles:")
     for f in files:
        print(f"  {Path(f).name}")
