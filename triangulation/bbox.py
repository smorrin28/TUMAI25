from .triangulate import triangulate
from .metadata   import read_metadata
from more_itertools import chunked as batched
import numpy as np

image_bbox = tuple[str, any]

def _triangulate_two_images(img1: image_bbox, img2: image_bbox):
    img1_path, img1_bbox = img1
    img2_path, img2_bbox = img2
    print(f"Triangulating {img1_path} and {img2_path}")
    img1_metadata, img2_metadata = read_metadata(img1_path), read_metadata(img2_path)
    points = []
    for p1, p2 in zip(batched(img1_bbox, n=2), batched(img2_bbox, n=2)):
        p = triangulate(img1_metadata,
                        img2_metadata,
                        (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])))
        points.append(p)
    return np.array(points)

def get_bbox_positions(images: list[tuple[image_bbox, image_bbox]]):
    """
    Returns the averaged, triangulated bbox positions from a list of pairs of images.
    """
    bbox = []
    for img1, img2 in images:
        print(img1, img2)
        bbox.append(_triangulate_two_images(img1, img2))
    # return np.mean(bbox, axis=0)
    return bbox[0]
