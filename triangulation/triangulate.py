import numpy as np
import cv2
from pyproj import Transformer
from metadata import DJIMetadata, read_metadata
from scipy.spatial.transform import Rotation as R

# Camera calibration parameters (optimized values)
OPTIMIZED_FOCAL_LENGTH: np.float64 = 2804.051
OPTIMIZED_CX: np.float64 = 2010.41
OPTIMIZED_CY: np.float64 = 1512.734
DIST_COEFFS = np.array([0.116413456, -0.202624237, 0.136982457, 0.000004293, -0.000216595], dtype=np.float64)


def compute_camera_matrix(metadata: DJIMetadata):
    # Build K matrix using optimized intrinsics
    K = np.array([
        [OPTIMIZED_FOCAL_LENGTH, 0.0, OPTIMIZED_CX],
        [0.0, OPTIMIZED_FOCAL_LENGTH, OPTIMIZED_CY],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)
    # Convert GPS to ECEF (x, y, z)
    transformer = Transformer.from_crs("epsg:4326", "epsg:4978", always_xy=True)    
    x, y, z = transformer.transform(
        metadata.longitude,
        metadata.latitude,
        metadata.absolute_altitude
    )

    # Use gimbal yaw, pitch, roll for rotation
    r = R.from_euler('zyx', [metadata.yaw, metadata.pitch, metadata.roll], degrees=True)
    R_cam = r.as_matrix()

    # Compute translation vector
    cam_position = np.array([x, y, z], dtype=np.float64)
    t = -R_cam @ cam_position

    # Combine into extrinsics
    Rt = np.hstack((R_cam, t.reshape(3, 1)))

    # Full projection matrix
    P = K @ Rt

    return P, K


def triangulate(img1_metadata: DJIMetadata, img2_metadata: DJIMetadata, label_pos1: tuple[int, int], label_pos2: tuple[int, int]):
    P1, K1 = compute_camera_matrix(img1_metadata)
    P2, K2 = compute_camera_matrix(img2_metadata)

    # Convert label positions into (N, 1, 2) shape arrays
    pt1 = np.array(label_pos1, dtype=np.float64).reshape(1, 1, 2)
    pt2 = np.array(label_pos2, dtype=np.float64).reshape(1, 1, 2)

    # Undistort points based on calibration
    undist_pt1 = cv2.undistortPoints(pt1, K1, DIST_COEFFS, P=K1).reshape(2, 1)
    undist_pt2 = cv2.undistortPoints(pt2, K2, DIST_COEFFS, P=K2).reshape(2, 1)

    # Triangulate
    pts4D_hom = cv2.triangulatePoints(P1, P2, undist_pt1, undist_pt2)

    # Convert from homogeneous to Euclidean coordinates
    pts3D = (pts4D_hom[:3] / pts4D_hom[3]).reshape(3,)

    return pts3D
