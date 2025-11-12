import os
from pathlib import Path

try:
    import asf_search as asf
except ImportError:
    raise ImportError("Install with: pip install asf_search")

def download_sentinel1(
    lon,
    lat,
    start_date,
    end_date,
    output_dir="./data/new_slc",
    flight_direction=None,
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
    
    print(f"Searching ASF for Sentinel-1 data...")
    print(f"  Location: {lon}, {lat}")
    print(f"  Dates: {start_date} to {end_date}")
    
    opts = {
        'platform': asf.PLATFORM.SENTINEL1,
        'processingLevel': 'SLC',
        'beamMode': 'IW',
        'intersectsWith': f"POINT({lon} {lat})",
        'start': start_date,
        'end': end_date,
        'maxResults': max_results
    }
    
    if flight_direction:
        opts['flightDirection'] = flight_direction
    
    results = asf.search(**opts)
    print(f"Found {len(results)} scenes")
    
    if not results:
        print("No scenes found")
        return []
    
    total_gb = sum(r.properties.get('bytes', 0) for r in results) / 1e9
    print(f"  Total size: {total_gb:.1f} GB")
    
    print(f"Downloading to {output_dir}...")
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
    files = download_sentinel1(
        lon=130.6,
        lat=33.3,
        start_date="2016-03-01",
        end_date="2016-05-31",
        max_results=50
    )
    print(f"\nFiles:")
    for f in files:
        print(f"  {Path(f).name}")
