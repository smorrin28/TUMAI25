from triangulate import triangulate
from metadata import read_metadata
from pathlib import Path

base_path = Path.cwd()
img_path1 = base_path / "DJI_20250424192954_0007_V.jpeg"
img_path2 = base_path / "DJI_20250424193048_0052_V.jpeg"
img_pos1 = (1248, 458)
img_pos2 = (2132, 1961)

img_1_metadata = read_metadata(img_path1)
img_2_metadata = read_metadata(img_path2)

result = triangulate(img_1_metadata, img_2_metadata, img_pos1, img_pos2)
print(result)