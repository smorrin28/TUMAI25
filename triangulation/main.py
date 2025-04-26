# from triangulate import triangulate
# from metadata import read_metadata
# from create_kml import create_kml
# from pyproj import Transformer
# from pathlib import Path
# from dataclasses import dataclass, asdict
# import json
#
#
# @dataclass
# class Coordinates:
#     latitude: float
#     longitude: float
#     altitude: float
#     name: str
#
# base_path = Path.cwd()
# img_path1 = base_path / "../dataset/images/val/92f118b0-DJI_20250424193049_0053_V.jpeg"
# img_path2 = base_path / "DJI_20250424193048_0052_V.jpeg"
# img_plane_1 = [(1860, 1984), (1965, 2009), (1959, 2172), (1866, 2143)]
# img_plane_2 = [(2031, 1944), (2133, 1967), (2118, 2131), (2025, 2101)]
#
# img_1_metadata = read_metadata(img_path1)
# img_2_metadata = read_metadata(img_path2)
# print(img_1_metadata.absolute_altitude)
# print(img_2_metadata.absolute_altitude)
#
#
# def ecef_to_lla_pyproj(x, y, z):
#     transformer = Transformer.from_crs("epsg:4978", "epsg:4979", always_xy=True)
#     lon, lat, alt = transformer.transform(x, y, z)
#     return lat, lon, alt
#
# for (pos_1, pos_2) in zip(img_plane_1, img_plane_2):
#     result = triangulate(img_1_metadata, img_2_metadata, pos_1, pos_2)
#     result = ecef_to_lla_pyproj(result[0], result[1], result[2])
#     print(result)
#
# images = [("0053_V", img_1_metadata), ("0052_V", img_2_metadata)]
# output = {
#     "result": asdict(Coordinates(*ecef_to_lla_pyproj(*result), name="result")),
#     "points": [
#         asdict(Coordinates(float(p.latitude), float(p.longitude), p.absolute_altitude, name=n)) for n, p in images
#     ]
# }
#
# lat = output["result"]["latitude"]
# lon = output["result"]["longitude"]
# alt = output["result"]["altitude"]
# name = output["result"]["name"]
#
# create_kml([(lat, lon, alt)])


from bbox import get_bbox_positions, image_bbox
from flight_planning import generate_flight_plan, Position
from metadata import read_metadata
from export import write_file
import numpy as np


def write_flight_plan(image_pairs: list[tuple[image_bbox, image_bbox]], output_file="output.kmz", plane_distance=3.0, descend=1.5):
    """
    Writes a flight plan from the image paris to ``output_file``.
    The drone will pass ``plane_distance``m (default=3) in front of the bbox
    and descend ``descend``m (default=1.5) after each row.
    """
    bbox_positions = get_bbox_positions(image_pairs)
    # required for the flight plan
    metadata = read_metadata(image_pairs[0][0][0])
    drone_position = Position(metadata.latitude, metadata.longitude, metadata.relative_altitude)
    flight_plan = generate_flight_plan(bbox_positions[0], bbox_positions[1], drone_position, PLANE_DISTANCE=plane_distance, DESCEND=descend)
    write_file(flight_plan, output_file)


if __name__ == "__main__":
    images = [(('/Users/smorrin/Downloads/dev_data/DJI_20250424193052_0058_V.jpeg',
                np.array([983.9920, 1805.4355, 1660.2649, 2020.0222])),
               ('/Users/smorrin/Downloads/dev_data/DJI_20250424193049_0053_V.jpeg',
                np.array([1301.3892, 1939.1567, 2263.3398, 2223.6248]))),
              (('/Users/smorrin/Downloads/dev_data/DJI_20250424193039_0039_V.jpeg',
                np.array([2232.0859, 1355.0895, 2859.7336, 1538.9474])),
               ('/Users/smorrin/Downloads/dev_data/DJI_20250424193044_0046_V.jpeg',
                np.array([1697.3778, 1069.0656, 2257.6340, 1263.9067])))]
    write_flight_plan(images)