import numpy as np
import cv2
from pyproj import Transformer
from metadata import DJIMetadata, read_metadata
from scipy.spatial.transform import Rotation as R

# Camera calibration parameters (optimized values)
OPTIMIZED_FOCAL_LENGTH: np.float64 = 2804.051
OPTIMIZED_CX: np.float64 = 2010.41
OPTIMIZED_CY: np.float64 = 1512.734
DIST_COEFFS = np.array([
    0.116413456,
   -0.202624237,
    0.136982457,
    0.000004293,
   -0.000216595
], dtype=np.float64)


def compute_camera_matrix(metadata: DJIMetadata):
    # 1) Intrinsics
    K = np.array([
        [OPTIMIZED_FOCAL_LENGTH, 0.0,                   OPTIMIZED_CX],
        [0.0,                    OPTIMIZED_FOCAL_LENGTH, OPTIMIZED_CY],
        [0.0,                    0.0,                     1.0]
    ], dtype=np.float64)

    # 2) Camera centre in ECEF
    transformer = Transformer.from_crs("epsg:4326", "epsg:4978", always_xy=True)
    x, y, z = transformer.transform(
        metadata.longitude,
        metadata.latitude,
        metadata.absolute_altitude
    )
    cam_position = np.array([x, y, z], dtype=np.float64)

    # 3) Build D_ecef2ned (maps ECEF vectors into NED)
    φ = np.deg2rad(metadata.latitude)
    λ = np.deg2rad(metadata.longitude)
    D_ecef2ned = np.array([
        [-np.sin(φ)*np.cos(λ), -np.sin(φ)*np.sin(λ),  np.cos(φ)],
        [-np.sin(λ),            np.cos(λ),            0.0     ],
        [-np.cos(φ)*np.cos(λ), -np.cos(φ)*np.sin(λ), -np.sin(φ)]
    ], dtype=np.float64)

    # 4) Build NED→camera rotation from yaw, pitch, roll
    #    Using intrinsic rotations about z (yaw), y (pitch), x (roll)
    r = R.from_euler('zyx',
                     [metadata.yaw, metadata.pitch, metadata.roll],
                     degrees=True)
    R_ned2cam = r.as_matrix()

    # 5) Combine to get ECEF→camera rotation
    R_cam = R_ned2cam @ D_ecef2ned

    # 6) Translation in camera frame
    t = -R_cam @ cam_position

    # 7) Projection matrix
    Rt = np.hstack((R_cam, t.reshape(3, 1)))
    P = K @ Rt

    return P, K


def triangulate(img1_metadata: DJIMetadata,
                img2_metadata: DJIMetadata,
                label_pos1: tuple[int, int],
                label_pos2: tuple[int, int]):
    P1, K1 = compute_camera_matrix(img1_metadata)
    P2, K2 = compute_camera_matrix(img2_metadata)

    # Points in (1,1,2) shape
    pt1 = np.array(label_pos1, dtype=np.float64).reshape(1, 1, 2)
    pt2 = np.array(label_pos2, dtype=np.float64).reshape(1, 1, 2)

    # Undistort back into pixel coords
    und1 = cv2.undistortPoints(pt1, K1, DIST_COEFFS, P=K1).reshape(2, 1)
    und2 = cv2.undistortPoints(pt2, K2, DIST_COEFFS, P=K2).reshape(2, 1)

    # Triangulate
    pts4D = cv2.triangulatePoints(P1, P2, und1, und2)
    pts3D = (pts4D[:3] / pts4D[3]).reshape(3,)

    return pts3D