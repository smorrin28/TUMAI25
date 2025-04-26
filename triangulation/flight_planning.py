import numpy as np

from dataclasses import dataclass
from pyproj import Transformer
from pprint import pprint

@dataclass
class Point:
    latitude: float
    longitude: float
    altitude: float


def generate_flight_plan(
    top_left: Point,
    top_right: Point,
    bottom_left: Point,
    bottom_right: Point,
    drone_position: Point,
    PLANE_DISTANCE=3.0,
    DESCEND=1.5,
):
    """
    Generates a flight plan given the coordinates of the plane.
    The route will follow an S shape, starting in the top left corner 
    and ending in the bottom right corner (or bottom left if applicable).
    `drone_position` may be any point in front of the objects of interest.
    The distance from the plane will be `PLANE_DISTANCE` (default: 3) meters and
    the drone will descend `DESCEND` (default: 1.5) meters after each row. 
    """
    points = np.array([
        [top_left.latitude, top_left.longitude, top_left.altitude],
        [top_right.latitude, top_right.longitude, top_right.altitude],
        [bottom_left.latitude, bottom_left.longitude, bottom_left.altitude],
        [bottom_right.latitude, bottom_right.longitude, bottom_right.altitude],
    ])

    wgs84_to_ecef = Transformer.from_crs("EPSG:4326", "EPSG:4978", always_xy=True)
    ecef_to_wgs84 = Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)

    ecef_points = []
    for lat, long, alt in points:
        x, y, z = wgs84_to_ecef.transform(long, lat, alt)
        ecef_points.append([x, y, z])
    ecef_points = np.array(ecef_points)

    drone_ecef = np.array(wgs84_to_ecef.transform(drone_position.longitude, drone_position.latitude, drone_position.altitude))


    # Compute two vectors lying on the plane
    v1 = ecef_points[1] - ecef_points[0]
    v2 = ecef_points[2] - ecef_points[0]

    # Compute the normal vector (cross product) and normalize it
    normal = np.cross(v1, v2)
    normal /= np.linalg.norm(normal)

    inverted_normal = -normal
    # check which direction the normal vector should face
    if np.linalg.norm(inverted_normal - drone_ecef) < np.linalg.norm(normal - drone_ecef):
        normal = inverted_normal

    # Displacement amount
    d = PLANE_DISTANCE

    # Displace points
    displaced_ecef_points = ecef_points + d * normal

    # Convert displaced points back to lat/lon/alt
    displaced_points = []
    for x, y, z in displaced_ecef_points:
        lon, lat, alt = ecef_to_wgs84.transform(x, y, z)
        displaced_points.append([lat, lon, alt])

    displaced_points = np.array(displaced_points)
    current_altitude = displaced_points[0][-1].item() # top left altitude
    min_altitude = displaced_points[-1][-1].item() # bottom right altitude
    start_lat, start_long = [float(x) for x in displaced_points[0][:2]]
    end_lat, end_long = [float(x) for x in displaced_points[-1][:2]]

    flight_path = []
    while current_altitude > min_altitude:
        # fly from left to right, then
        first_point = [start_lat, start_long, current_altitude]
        second_point = [end_lat, end_long, current_altitude]
        flight_path.append(first_point)
        flight_path.append(second_point)
        current_altitude -= DESCEND
        # switch the latitudes & longitudes to start from the other side
        start_lat, start_long, end_lat, end_long = end_lat, end_long, start_lat, start_long

    return flight_path

if __name__ == "__main__":
    pprint(
        generate_flight_plan(
            Point(49.09935094275363, 12.180929417801106, 496.0389585290104),
            Point(49.09934680865197, 12.18092950731804, 495.8597035156563),
            Point(49.09934817409882, 12.180937450325327, 495.46850503236055),
            Point(49.0993516569836, 12.180937365722043, 495.60829266440123),
            Point(49.0993516569836, 12.180937365722043, 495.60829266440123),
        )
    )