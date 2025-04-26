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
img_path1 = base_path / "../dataset/images/val/92f118b0-DJI_20250424193049_0053_V.jpeg"
img_path2 = base_path / "DJI_20250424193048_0052_V.jpeg"
img_plane_1 = [(1860, 1984), (1965, 2009), (1959, 2172), (1866, 2143)]
img_plane_2 = [(2031, 1944), (2133, 1967), (2118, 2131), (2025, 2101)]

img_1_metadata = read_metadata(img_path1)
img_2_metadata = read_metadata(img_path2)
print(img_1_metadata.absolute_altitude)
print(img_2_metadata.absolute_altitude)


def ecef_to_lla_pyproj(x, y, z):
    transformer = Transformer.from_crs("epsg:4978", "epsg:4979", always_xy=True)
    lon, lat, alt = transformer.transform(x, y, z)
    return lat, lon, alt

for (pos_1, pos_2) in zip(img_plane_1, img_plane_2):
    result = triangulate(img_1_metadata, img_2_metadata, pos_1, pos_2)
    result = ecef_to_lla_pyproj(result[0], result[1], result[2])
    print(result)

images = [("0053_V", img_1_metadata), ("0052_V", img_2_metadata)]
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
