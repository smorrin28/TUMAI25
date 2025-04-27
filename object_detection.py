from ultralytics import YOLO
from typing import List, Tuple
from itertools import combinations
from ultralytics.engine.results import Results
from libxmp.utils import file_to_dict
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path
from pyproj import Transformer
import numpy as np
from torchvision.ops import box_area
import os
import torch

def predict_oois(folder_path: str, model_path: str) -> List[Results]:
    model = YOLO(model_path)
    
    # run inference and dump only .txt files
    results = model.predict(
        source=folder_path,
        imgsz=640,
        conf=0.25,
        iou=0.45,
        # save_txt=True,               # ← write out labels in YOLO format
        # project='.',                 # ← save into ./predictions/
        # name='predictions',          
        # exist_ok=True,               # ← overwrite if it already exists
        # save=False                   # ← do NOT save annotated images
    )
    return results

def filter_results_by_object_num(results: List[Results], min_num=0) -> List[Results]:
    results_with_objects = []
    for r in results:
        # Count detections
        count = len(r.boxes.data)

        if count > min_num:
            print(f"Detected {count} objects")
            results_with_objects.append(r)
        else:
            print("No objects detected")
    return results_with_objects

def pair_by_box_counts(results: List[Results], tol=0) -> List[Tuple[Results, Results]]:
    paired: List[Tuple[Results, Results]] = []
    for r1, r2 in combinations(results, 2):
        if abs(len(r1.boxes.data) - len(r2.boxes.data)) <= tol:
            print('---------------')
            print('r1 count:', len(r1.boxes.data))
            print('r2 count:', len(r2.boxes.data))
            print("is pair")
            paired.append((r1, r2))
    return paired

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
    
def latlong_in_geo(metadata: DJIMetadata):
     # convert gps into x, y, z
    transformer = Transformer.from_crs("epsg:4326", "epsg:4978")  # WGS84 to ECEF
    x, y, z = transformer.transform(
        metadata.latitude,
        metadata.longitude,
        metadata.absolute_altitude)
    return x, y, z

def calculate_distance_3d(x1, y1, z1, x2, y2, z2):
    point1 = np.array((x1, y1, z1))
    point2 = np.array((x2, y2, z2))
    
    # calculating Euclidean distance
    # using linalg.norm()
    return np.linalg.norm(point1 - point2)

def filter_pairs_by_distance(result_pairs: List[Tuple[Results, Results]], min=0, max=10) -> List[Tuple[Results, Results]]:
    filtered: List[Tuple[Results, Results]] = []
    for r1, r2 in result_pairs:
        meta1 = read_metadata(r1.path)
        meta2 = read_metadata(r2.path)

        p1 = latlong_in_geo(meta1)
        p2 = latlong_in_geo(meta2)

        dist = calculate_distance_3d(*p1, *p2)

        print('------------')
        print('Distance:', dist)

        if dist >= min and dist <= max:
            filtered.append((r1, r2))

    return filtered

def create_pairs(results: List[Results]) -> List[Tuple[Results, Results]]:
    count_pairs = pair_by_box_counts(results)
    print('================')
    print('Number of pairs by count:', len(count_pairs))
    print('================')
    filtered = filter_pairs_by_distance(count_pairs)
    print('================')
    return filtered 

def get_avg_pair_conf(pair: Tuple[Results, Results]):
    r1, r2 = pair
    avg1 = r1.boxes.conf.mean()
    avg2 = r2.boxes.conf.mean()
    return (avg1 + avg2)

def sort_by_conf(pairs: List[Tuple[Results, Results]]) -> List[Tuple[Results, Results]]:
    sorted_pairs = sorted(pairs, key=get_avg_pair_conf, reverse=True)
    return sorted_pairs

def get_avg_box_size(r: Results):
    areas = box_area(r.boxes.xyxy)
    return areas.mean()

def get_avg_pair_box_size(pair: Tuple[Results, Results]):
    r1, r2 = pair
    return get_avg_box_size(r1) + get_avg_box_size(r2)

def sort_by_box_size(pairs: List[Tuple[Results, Results]]) -> List[Tuple[Results, Results]]:
    sorted_pairs = sorted(pairs, key=get_avg_pair_box_size, reverse=True)
    return sorted_pairs

def combine_rankings_rrf(list1, list2, k: int = 60):
    """
    Combines two ranked lists using Reciprocal Rank Fusion (RRF).

    Assumes lower index means better rank. Items are ranked based on their
    position (index). The RRF score for an item is the sum of 1/(k + rank)
    over all lists it appears in. Items not present in a list contribute 0
    to the score from that list. The final ranking sorts items by RRF score
    (higher score is better).

    Args:
        list1: The first list of items, ordered by rank (best first).
        list2: The second list of items, ordered by rank (best first).
        k: RRF constant (default 60). Controls how much lower ranks
           are penalized relative to higher ranks.

    Returns:
        A new list of items, sorted by the combined RRF score (best first).
    """
    ranks1: Dict[Any, int] = {item: i for i, item in enumerate(list1)}
    ranks2: Dict[Any, int] = {item: i for i, item in enumerate(list2)}
    all_items: set = set(list1) | set(list2)

    rrf_scores: Dict[Any, float] = {}
    for item in all_items:
        score: float = 0.0
        # Get rank from list1 if item exists
        rank1: Optional[int] = ranks1.get(item)
        if rank1 is not None:
            score += 1.0 / (k + rank1)

        # Get rank from list2 if item exists
        rank2: Optional[int] = ranks2.get(item)
        if rank2 is not None:
            score += 1.0 / (k + rank2)
            

        rrf_scores[item] = score

    # Sort items based on the RRF score (descending order - higher is better)
    sorted_items: List[Any] = sorted(all_items, key=lambda item: rrf_scores[item], reverse=True)
    return sorted_items

def create_overall_bbox(boxes):
    x_min = boxes[:, 0].min()
    y_min = boxes[:, 1].min()
    x_max = boxes[:, 2].max()
    y_max = boxes[:, 3].max()
    overall_box = torch.stack([x_min, y_min, x_max, y_max])
    return overall_box

def get_image_pairs(folder_path, model_path):
    results = predict_oois(folder_path, model_path)
    results_with_objects = filter_results_by_object_num(results, min_num=1)
    paired_results = create_pairs(results_with_objects)
    print("Number of pairs:", len(paired_results))
    
    conf_sorted = sort_by_conf(paired_results)
    box_sorted = sort_by_box_size(paired_results)
    
    rankings_combined = combine_rankings_rrf(conf_sorted, box_sorted)
    for idx, pair in enumerate(rankings_combined):
        r1, r2 = pair
        print('====================')
        print('Rank:', idx)
        print('Image 1:', r1.path)
        print('Image 2:', r2.path)
    print('====================')
    
    final_list = []
    for pair in rankings_combined:
        r1, r2 = pair
        bbox1 = create_overall_bbox(r1.boxes.xyxy)
        bbox2 = create_overall_bbox(r2.boxes.xyxy)
        final_list.append(((r1.path, bbox1), (r2.path, bbox2)))
        
    return final_list
    