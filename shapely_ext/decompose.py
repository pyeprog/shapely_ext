from typing import List

from shapely.geometry import Polygon, LineString
from shapely.geometry.base import BaseGeometry

from shapely_ext.geometry.vector_2d import Vector2D


def _is_corner(cur_coord, prev_coord, next_coord, min_corner_angle_degree: float) -> bool:
    prev_vec = Vector2D.from_coordinates(prev_coord, cur_coord)
    next_vec = Vector2D.from_coordinates(cur_coord, next_coord)
    angle_in_degree = prev_vec.angle_to(next_vec)
    return angle_in_degree >= min_corner_angle_degree


def decompose(
        geometry: BaseGeometry,
        min_corner_angle_degree: float = 0,
        simplify_radius: float = 1e-6) -> List[BaseGeometry]:
    geometry = geometry.simplify(simplify_radius)
    if isinstance(geometry, Polygon):
        exterior_coords = list(geometry.exterior.coords)[:-1]
        corner_i = None
        for i in range(len(exterior_coords)):
            last_last_coord = exterior_coords[i - 2]
            last_coord = exterior_coords[i - 1]
            cur_coord = exterior_coords[i]
            if _is_corner(last_coord, last_last_coord, cur_coord, min_corner_angle_degree=min_corner_angle_degree):
                corner_i = i - 1
                break
        if corner_i is None:
            raise ValueError("Polygon has no corner")
        lines: List[LineString] = []
        cur_line = [exterior_coords[corner_i]]
        for j in range(1, len(exterior_coords) + 1):
            cur_i = (corner_i + j) % len(exterior_coords)
            cur_line.append(exterior_coords[cur_i])
            if _is_corner(exterior_coords[cur_i], exterior_coords[cur_i - 1],
                          exterior_coords[(cur_i + 1) % len(exterior_coords)],
                          min_corner_angle_degree=min_corner_angle_degree):
                lines.append(LineString(cur_line))
                cur_line = [exterior_coords[cur_i]]
        return lines
