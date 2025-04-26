import math
import cv2

from metadata import read_metadata

def calculate_object_angle(
    object_pixel_y,
    image_height,
    vertical_fov_deg,
    gimbal_pitch_deg
):

    # Center of the image
    center_y = image_height / 2

    # Pixels per degree
    pixels_per_degree_y = image_height / vertical_fov_deg

    # Pixel offset from center
    delta_y_pixels = object_pixel_y - center_y

    # Angle offsets
    delta_y_angle = delta_y_pixels / pixels_per_degree_y

    # Total pitch angle (camera pitch + offset from object position)
    total_pitch_deg = gimbal_pitch_deg + delta_y_angle

    return total_pitch_deg

def calculate_distance_to_object(
        drone_pitch: float,
        drone_relative_height: float,
        image_y: int,
        image_height: int,
        vertical_fov_deg: float,
        MAXIMUM_OBJECT_HEIGHT=2.6,
) -> tuple[float, float]:
    """
    Calculates the distance to the object relative to the horizon based on the drone pitch and relative height.
    MAXIMUM_OBJECT_HEIGHT defines the maximum possible height.
    Returns the minimum and maximum possible distance to the object relative to the horizon.
    """
    object_pitch = calculate_object_angle(
        object_pixel_y=image_y,
        image_height=image_height,
        vertical_fov_deg=vertical_fov_deg,
        gimbal_pitch_deg=drone_pitch,
    )
    return (
        drone_relative_height / math.tan(math.radians(object_pitch)),
        (drone_relative_height - MAXIMUM_OBJECT_HEIGHT) / math.tan(math.radians(object_pitch)),
    )

def select_pixel_and_calculate_distance(image_path: str) -> tuple[float, float]:
    """
    Opens an image, lets the user select a pixel, reads the metadata,
    and calculates the distance to the object.
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at path '{image_path}' could not be loaded.")

    # Read metadata
    metadata = read_metadata(image_path)

    # Resize for display if needed (optional)
    display_image = image.copy()

    # Variable to store selected point
    selected_point = []

    # Mouse callback function
    def select_point(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            selected_point.append((x, y))
            cv2.circle(display_image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Select Object", display_image)

    # Create window and set callback
    cv2.namedWindow("Select Object")
    cv2.setMouseCallback("Select Object", select_point)

    print("Click on the object in the image window. Press any key after selecting.")
    cv2.imshow("Select Object", display_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Check if a point was selected
    if not selected_point:
        raise ValueError("No point was selected.")

    x_pixel, y_pixel = selected_point[0]

    # Call your existing distance calculation function
    min_distance, max_distance = calculate_distance_to_object(
        drone_pitch=metadata.pitch,
        drone_relative_height=metadata.relative_altitude,
        image_y=y_pixel,
        image_height=metadata.image_height,
        vertical_fov_deg=67,
        MAXIMUM_OBJECT_HEIGHT=2.6,
    )

    return min_distance, max_distance

def move_point(lat, lon, yaw, distance_m):
    """
    Returns the coordinates of the object of interest,
    given the coordinates of the drone and the calculated distance
    and yaw.
    """
    # Earth radius in meters
    R = 6371000

    # Convert inputs to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    heading_rad = math.radians(yaw)

    # Calculate new latitude
    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(distance_m / R) +
                            math.cos(lat_rad) * math.sin(distance_m / R) * math.cos(heading_rad))

    # Calculate new longitude
    new_lon_rad = lon_rad + math.atan2(
        math.sin(heading_rad) * math.sin(distance_m / R) * math.cos(lat_rad),
        math.cos(distance_m / R) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )

    # Convert back to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon
