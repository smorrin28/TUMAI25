from libxmp.utils import file_to_dict
from dataclasses import dataclass
from decimal import Decimal, getcontext

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
    latitude: float
    longitude: float

DJI_KEY = "http://www.dji.com/drone-dji/1.0/"
DJI_PREFIX = "drone-dji:"

RELATIVE_ALTITUDE = f"{DJI_PREFIX}RelativeAltitude"
ABSOLUTE_ALTITUDE = f"{DJI_PREFIX}AbsoluteAltitude"
YAW = f"{DJI_PREFIX}GimbalYawDegree"
PITCH = f"{DJI_PREFIX}GimbalPitchDegree"
ROLL = f"{DJI_PREFIX}GimbalRollDegree"
LATITUDE = f"{DJI_PREFIX}GpsLatitude"
LONGITUDE = f"{DJI_PREFIX}GpsLongitude"

PRECISION = 12

getcontext().prec = PRECISION

def _metadata_to_dict(metadata: list[tuple]) -> dict[str, str]:
    """
    Parses the DJI metadata into a dictionary
    """
    return {
        entry[0] : entry[1] for entry in metadata
    }

def read_metadata(file: str) -> DJIMetadata:
    """
    Reads the relevant metadata from `file`
    """
    xmp_data = file_to_dict(file)
    metadata = _metadata_to_dict(xmp_data[DJI_KEY])
    return DJIMetadata(
        relative_altitude=float(metadata[RELATIVE_ALTITUDE]),
        absolute_altitude=float(metadata[ABSOLUTE_ALTITUDE]),
        yaw=float(metadata[YAW]),
        pitch=float(metadata[PITCH]),
        roll=float(metadata[ROLL]),
        latitude=Decimal(metadata[LATITUDE]),
        longitude=Decimal(metadata[LONGITUDE]),
    )