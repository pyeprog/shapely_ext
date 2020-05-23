from typing import List

import numpy as np
from scipy.spatial import Delaunay
from shapely.geometry import Polygon

from shapely_ext.interpolate import interpolate


def generate_tri_mesh(
        polygon: Polygon,
        interpolate_distance: float) -> List[Polygon]:
    if not isinstance(polygon, Polygon):
        raise NotImplementedError("only polygon can be meshed")
    interpolated_polygon = interpolate(polygon, gap=interpolate_distance)
    exterior_coords = np.array(list(interpolated_polygon.exterior.coords))
    delaunay = Delaunay(exterior_coords)
    mesh_faces: List[Polygon] = list(map(lambda tri_coords: Polygon(tri_coords), exterior_coords[delaunay.simplices]))
    return mesh_faces
