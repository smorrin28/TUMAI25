import numpy as np

from dataclasses import dataclass
from pyproj import Transformer
from export import write_file

Point = np.typing.NDArray

@dataclass
class Position:
    latitude: float
    longitude: float
    altitude: float

def generate_flight_plan(
    top_left: Point,
    bottom_right: Point,
    drone_position: Position,
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

    x1, y1, z1 = top_left
    x2, y2, z2 = bottom_right

    # Define the 4 plane points (in ECEF):
    # Top-left, Top-right, Bottom-left, Bottom-right
    plane_points_ecef = [
        np.array([x1, y1, z1]),  # Top-left
        np.array([x2, y1, z1]),  # Top-right (same y as top-left, x from bottom-right)
        np.array([x1, y2, z2]),  # Bottom-left (same x as top-left, y from bottom-right)
        np.array([x2, y2, z2]),  # Bottom-right
    ]
    plane_points_ecef = np.array(plane_points_ecef)

    wgs84_to_ecef = Transformer.from_crs("EPSG:4326", "EPSG:4978", always_xy=True)
    ecef_to_wgs84 = Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)

    v1 = plane_points_ecef[1] - plane_points_ecef[0]
    v2 = plane_points_ecef[2] - plane_points_ecef[0]
    normal = np.cross(v1, v2)
    normal /= np.linalg.norm(normal)

    drone_ecef = np.array(wgs84_to_ecef.transform(drone_position.longitude, drone_position.latitude, drone_position.altitude))


    inverted_normal = -normal
    # check which direction the normal vector should face
    if np.linalg.norm(inverted_normal - drone_ecef) < np.linalg.norm(normal - drone_ecef):
        normal = inverted_normal

    # Displacement amount
    d = PLANE_DISTANCE

    # Displace points
    displaced_ecef_points = plane_points_ecef + d * normal

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
        # fly from left to right, then back
        first_point = [start_lat, start_long, current_altitude]
        second_point = [end_lat, end_long, current_altitude]
        flight_path.append(first_point)
        flight_path.append(second_point)
        current_altitude -= DESCEND
        # switch the latitudes & longitudes to start from the other side
        start_lat, start_long, end_lat, end_long = end_lat, end_long, start_lat, start_long

    return flight_path
