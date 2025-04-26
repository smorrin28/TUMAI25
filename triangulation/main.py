from triangulate import triangulate
from metadata import read_metadata
from create_kml import create_kml
from pyproj import Transformer
from pathlib import Path
from dataclasses import dataclass, asdict
import json

@dataclass
class Coordinates:
    latitude: float
    longitude: float
    altitude: float
    name: str

base_path = Path.cwd()
img_path1 = base_path / "DJI_20250424192954_0007_V.jpeg"
img_path2 = base_path / "DJI_20250424193048_0052_V.jpeg"
img_pos1 = (1248, 458)
img_pos2 = (2132, 1961)

img_1_metadata = read_metadata(img_path1)
img_2_metadata = read_metadata(img_path2)

result = triangulate(img_1_metadata, img_2_metadata, img_pos1, img_pos2)

transformer = Transformer.from_crs("epsg:4978", "epsg:4979", always_xy=True)

def ecef_to_lla_pyproj(x, y, z):
    lon, lat, alt = transformer.transform(x, y, z)
    return lat, lon, alt

images = [("0007_V", img_1_metadata), ("0052_V", img_2_metadata)]
output = {
    "result": asdict(Coordinates(*ecef_to_lla_pyproj(*result), name="result")),
    "points": [
        asdict(Coordinates(float(p.latitude), float(p.longitude), p.absolute_altitude, name=n)) for n, p in images
    ]
}

lat = output["result"]["latitude"]
lon = output["result"]["longitude"]
alt = output["result"]["altitude"]
name = output["result"]["name"]


create_kml([(lat, lon, alt)])


with open("result.json", "w") as f:
    json.dump(output, f)
