import os
import requests

class Sentinel1SLC:
    def __init__(self, bbox, start_date, end_date):
        """
        Args:
            bbox: (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date in 'YYYY-MM-DD' format.
            end_date: End date in 'YYYY-MM-DD' format.
            download_dir: Directory to save downloaded files.
            username: ASF Vertex username (Earthdata Login).
            password: ASF Vertex password (Earthdata Login).
        """
        self.bbox = bbox
        self.start_date = start_date
        self.end_date = end_date

    def _build_search_url(self):
        # ASF Search API: https://api.daac.asf.alaska.edu/services/search/param
        base_url = "https://api.daac.asf.alaska.edu/services/search/param"
        min_lon, min_lat, max_lon, max_lat = self.bbox
        params = {
            "platform": "SENTINEL-1",
            "processingLevel": "SLC",
            "intersectsWith": f"{min_lon},{min_lat},{max_lon},{max_lat}",
            "start": self.start_date,
            "end": self.end_date,
            "output": "json"
        }
        return base_url, params

    def download(self):
        """
        Download Sentinel-1 SLC data for the given bounding box and time period using ASF Data Search.
        Returns:
            List of file paths to downloaded products.
        """
        base_url, params = self._build_search_url()
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json()

        features = results.get("features", [])
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        downloaded_files = []
        for feature in features:
            props = feature.get("properties", {})
            file_name = props.get("fileID", props.get("sceneName", "unknown")) + ".zip"
            download_url = props.get("url")
            if not download_url:
                continue

            out_path = os.path.join(self.download_dir, file_name)
            if os.path.exists(out_path):
                downloaded_files.append(out_path)
                continue

            print(f"Downloading {file_name} ...")
            with requests.get(download_url, auth=(self.username, self.password), stream=True) as r:
                r.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            downloaded_files.append(out_path)
            print(f"Downloaded to {out_path}")

        return downloaded_files

# Example usage:
# bbox = (min_lon, min_lat, max_lon, max_lat)
# s1 = Sentinel1SLC(
#     bbox=(-123.5, 37.0, -122.0, 38.0),
#     start_date="2022-01-01",
#     end_date="2022-01-31",
#     download_dir="./sentinel1_data",
#     username="your_earthdata_username",
#     password="your_earthdata_password"
# )
# s1.download()


