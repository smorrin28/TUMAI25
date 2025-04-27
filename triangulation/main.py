from .bbox            import get_bbox_positions, image_bbox
from .flight_planning import generate_flight_plan, Position
from .metadata        import read_metadata
from .export          import write_file


def write_flight_plan(image_pairs: list[tuple[image_bbox, image_bbox]], output_file="output.kmz", plane_distance=2.0, descend=1.5):
    """
    Writes a flight plan from the image paris to ``output_file``.
    The drone will pass ``plane_distance``m (default=3) in front of the bbox
    and descend ``descend``m (default=1.5) after each row.
    """
    bbox_positions = get_bbox_positions(image_pairs)
    # required for the flight plan
    metadata = read_metadata(image_pairs[0][0][0])
    drone_position = Position(metadata.latitude, metadata.longitude, metadata.absolute_altitude)
    flight_plan = generate_flight_plan(bbox_positions[0], bbox_positions[1], drone_position, plane_distance=plane_distance, descend=descend)
    write_file(flight_plan, output_file)


'''if __name__ == "__main__":
    images = [(
        ("/Users/smorrin/Downloads/dev_data/DJI_20250424193049_0053_V.jpeg", [1860, 1984, 1866, 2143]),
        ("/Users/smorrin/Downloads/dev_data/DJI_20250424193048_0052_V.jpeg", [2031, 1944, 2025, 2101]),
    )]
    write_flight_plan(images)'''