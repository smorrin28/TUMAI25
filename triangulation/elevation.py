import math
import struct
from pathlib import Path

base_path = Path.cwd()

def get_elevation(latitude, longitude, hgt_file_path=str(base_path / "N49E012.hgt")):
    # Open file
    with open(hgt_file_path, 'rb') as f:
        # Determine file size to get sample count
        f.seek(0, 2)  # Seek to end
        file_size = f.tell()
        samples = int(math.sqrt(file_size / 2))  # Each sample is 2 bytes

        if samples not in (1201, 3601):
            raise ValueError(f"Unexpected sample size: {samples}")

        # Extract tile's lower-left coordinate from filename
        # Example filename: 'N37W122.hgt'
        import re
        m = re.search(r'([NS])(\d+)([EW])(\d+)', hgt_file_path)
        if not m:
            raise ValueError("Invalid filename format")

        lat_origin = int(m.group(2)) * (1 if m.group(1) == 'N' else -1)
        lon_origin = int(m.group(4)) * (1 if m.group(3) == 'E' else -1)

        # Calculate row and column
        lat_diff = latitude - lat_origin
        lon_diff = longitude - lon_origin

        # In HGT files, (0,0) is top-left (northwest corner)
        row = int((1 - lat_diff) * (samples - 1))
        col = int(lon_diff * (samples - 1))

        # Bounds checking
        if not (0 <= row < samples and 0 <= col < samples):
            raise ValueError("Requested point is outside the bounds of the HGT file")

        # Calculate file position
        position = (row * samples + col) * 2

        # Read the elevation value
        f.seek(position)
        data = f.read(2)
        elevation = struct.unpack('>h', data)[0]  # '>h' means big-endian 16-bit signed

        return elevation


if __name__ == "__main__":
    print(get_elevation(49.099376103, 12.180945684))
