import numpy as np
import cv2
from pyproj import Transformer
from metadata import DJIMetadata, read_metadata
from scipy.spatial.transform import Rotation as R
from pathlib import Path


def compute_camera_matrix(metadata: DJIMetadata):
    # calculate camera matrix first
    sensor_width = 9.6
    sensor_height = 7.2
    f_0 = metadata.focal_length * metadata.image_width / sensor_width
    f_1 = metadata.focal_length * metadata.image_height / sensor_height
    c_0 = metadata.image_width / 2.0
    c_1 = metadata.image_height / 2.0
    K = [[f_0, 0.0, c_0],
         [0.0, f_1, c_1],
         [0.0, 0, 1.0]]

    # convert gps into x, y, z
    transformer = Transformer.from_crs("epsg:4326", "epsg:4978")  # WGS84 to ECEF
    x, y, z = transformer.transform(
        metadata.latitude,
        metadata.longitude,
        metadata.absolute_altitude)

    r = R.from_euler('zyx', [metadata.yaw, metadata.pitch, metadata.roll], degrees=True)
    R_cam = r.as_matrix()  # 3x3 rotation matrix
    t = -R_cam @ [x, y, z]
    Rt = np.hstack((R_cam, t.reshape(3, 1)))
    P = K @ Rt
    return P

def triangulate(img1_metadata: DJIMetadata, img2_metadata: DJIMetadata, label_pos1: tuple[int, int], label_pos2: tuple[int, int]):
    P1 = compute_camera_matrix(img1_metadata)
    P2 = compute_camera_matrix(img2_metadata)
    
    pts4D_hom = cv2.triangulatePoints(P1, P2, label_pos1, label_pos2)
    pts3D = pts4D_hom[:3] / pts4D_hom[3]
    return pts3D.ravel()


base_path = Path.cwd()
img_path1 = base_path / "DJI_20250424192954_0007_V.jpeg"
img_path2 = base_path / "DJI_20250424193048_0052_V.jpeg"
img_pos1 = (1248, 458)
img_pos2 = (2132, 1961)

img_1_metadata = read_metadata(img_path1)
img_2_metadata = read_metadata(img_path2)

result = triangulate(img_1_metadata, img_2_metadata, img_pos1, img_pos2)
print(result)