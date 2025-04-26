from libxmp.utils import file_to_dict
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path

__all__ = [
    "read_metadata"
]

@dataclass
class DJIMetadata:
    relative_altitude: float
    absolute_altitude: float
    yaw: float
    pitch: float
    roll: float
    latitude: Decimal
    longitude: Decimal
    focal_length: float
    image_width: int
    image_height: int


DJI_KEY = "http://www.dji.com/drone-dji/1.0/"
DJI_KEY_ALTERNATIVE = "http://www.uav.com/drone-dji/1.0/" # sometimes this key is used
EXIF_KEY = "http://ns.adobe.com/exif/1.0/"
DJI_PREFIX = "drone-dji:"
EXIF_PREFIX = "exif:"

RELATIVE_ALTITUDE = f"{DJI_PREFIX}RelativeAltitude"
ABSOLUTE_ALTITUDE = f"{DJI_PREFIX}AbsoluteAltitude"
YAW = f"{DJI_PREFIX}GimbalYawDegree"
PITCH = f"{DJI_PREFIX}GimbalPitchDegree"
ROLL = f"{DJI_PREFIX}GimbalRollDegree"
LATITUDE = f"{DJI_PREFIX}GpsLatitude"
LONGITUDE = f"{DJI_PREFIX}GpsLongitude"
FOCAL_LENGTH = f"{EXIF_PREFIX}FocalLength"
IMAGE_WIDTH = f"{EXIF_PREFIX}PixelXDimension"
IMAGE_HEIGHT = f"{EXIF_PREFIX}PixelYDimension"
PRECISION = 12

getcontext().prec = PRECISION

def _metadata_to_dict(metadata: list[tuple]) -> dict[str, str]:
    """
    Parses the DJI metadata into a dictionary
    """
    return {
        entry[0] : entry[1] for entry in metadata
    }

def read_metadata(file_path: str | Path) -> DJIMetadata:
    """
    Reads the relevant metadata from `file`
    """
    xmp_data = file_to_dict(str(file_path))
    # two different keys may be used to identify the data
    if DJI_KEY in xmp_data:
        dji_metadata = _metadata_to_dict(xmp_data[DJI_KEY])
    else:
        dji_metadata = _metadata_to_dict(xmp_data[DJI_KEY_ALTERNATIVE])
    exif_metadata = _metadata_to_dict(xmp_data[EXIF_KEY])
    return DJIMetadata(
        relative_altitude=float(dji_metadata[RELATIVE_ALTITUDE]),
        absolute_altitude=float(dji_metadata[ABSOLUTE_ALTITUDE]),
        yaw=float(dji_metadata[YAW]),
        pitch=float(dji_metadata[PITCH]),
        roll=float(dji_metadata[ROLL]),
        latitude=Decimal(dji_metadata[LATITUDE]),
        longitude=Decimal(dji_metadata[LONGITUDE]),
        focal_length=float(eval(exif_metadata[FOCAL_LENGTH])),
        image_width=int(exif_metadata[IMAGE_WIDTH]),
        image_height=int(exif_metadata[IMAGE_HEIGHT])
    )
