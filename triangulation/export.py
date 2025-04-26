import chevron
import tempfile
from pathlib import Path
from dataclasses import dataclass
from zipfile import ZipFile

@dataclass
class Waypoint:
    latitude: float
    longitude: float
    absolute_height: float


def write_file(waypoints: list[Waypoint], output_filename="output.kmz"):
    waypoints = [
        {   
            "latitude": wp.latitude,
            "longitude": wp.longitude, 
            "absoluteHeight": wp.absolute_height, 
            "index": i 
        } 
        for i, wp in enumerate(waypoints)
    ]
    base_path = Path.cwd() / "templates"
    waylines_template = base_path / "waylines.wpml"
    template_template = base_path / "template.kml"
    with ZipFile(output_filename, "w") as zfile:
        # write the waylines file
        with tempfile.NamedTemporaryFile("w+") as waylines:
            with open(waylines_template, "r") as tmpl:
                waylines.write(chevron.render(tmpl, {
                    "waypoints": waypoints,
                }))
            zfile.write(waylines.name, arcname="wpmz/waylines.wpml")
        # write the template file
        with tempfile.NamedTemporaryFile("w+") as template_file:
            with open(template_template, "r") as tmpl:
                template_file.write(chevron.render(tmpl, {
                    "waypoints": waypoints
                }))
            zfile.write(template_file.name, arcname="wpmz/template.kml")


# for testing
if __name__ == "__main__":
    waypoints = [
        Waypoint(latitude=47.234, longitude=12.234, absolute_height=450.32),
        Waypoint(latitude=-43.23, longitude=-40.032, absolute_height=304.21),
    ]
    write_file(waypoints)