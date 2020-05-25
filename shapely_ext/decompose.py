from itertools import chain
from typing import List

from shapely.geometry import Polygon, LineString, LinearRing, MultiPolygon, MultiLineString, GeometryCollection
from shapely.geometry.base import BaseGeometry

from shapely_ext.geometry.vector_2d import Vector2D


class Decomposer:
    def __init__(self, min_corner_angle_degree: float = 0, simplify_distance: float = 1e-6):
        self._min_corner_angle_degree = min_corner_angle_degree
        self._simplify_distance = simplify_distance

    def decompose(self, geometry: BaseGeometry) -> List[LineString]:
        geometry = geometry.simplify(self._simplify_distance)
        if isinstance(geometry, Polygon):
            return self.decompose_polygon(polygon=geometry)
        elif isinstance(geometry, MultiPolygon):
            lines_list: List[List[LineString]] = [
                self.decompose_polygon(polygon=sub_polygon)
                for sub_polygon in list(geometry)]
            return list(chain.from_iterable(lines_list))
        elif isinstance(geometry, LinearRing):
            return self.decompose_linearRing(ring=geometry)
        elif isinstance(geometry, LineString):
            return self.decompose_lineString(lineString=geometry)
        elif isinstance(geometry, MultiLineString):
            lines_list: List[List[LineString]] = [
                self.decompose_lineString(lineString=sub_lineString)
                for sub_lineString in list(geometry)]
            return list(chain.from_iterable(lines_list))
        elif isinstance(geometry, GeometryCollection):
            lines_list: List[List[LineString]] = [
                self.decompose(geometry=sub_geometry) for sub_geometry in list(geometry)]
            return list(chain.from_iterable(lines_list))
        else:
            return []

    def decompose_lineString(self, lineString: LineString):
        coords = list(lineString.coords)
        lines: List[LineString] = []
        cur_line_coords = []
        for i in range(len(coords)):
            cur_line_coords.append(coords[i])
            if i - 1 < 0 or i + 1 >= len(coords):
                continue

            if self._is_corner(coords[i], coords[i - 1], coords[i + 1],
                               min_corner_angle_degree=self._min_corner_angle_degree):
                lines.append(LineString(cur_line_coords))
                cur_line_coords = [coords[i]]
        if cur_line_coords:
            lines.append(LineString(cur_line_coords))
        return lines

    def decompose_polygon(self, polygon: Polygon) -> List[LineString]:
        exterior_lines: List[LineString] = self.decompose_linearRing(ring=polygon.exterior)
        interior_lines_list: List[List[LineString]] = [
            self.decompose_linearRing(ring=interior)
            for interior in polygon.interiors
        ]
        return exterior_lines + list(chain.from_iterable(interior_lines_list))

    def decompose_linearRing(self, ring: LinearRing) -> List[LineString]:
        coords = list(ring.coords)[:-1]
        corner_i = self._find_first_corner_index(coords)
        lines: List[LineString] = []
        cur_line = [coords[corner_i]]
        for j in range(1, len(coords) + 1):
            cur_i = (corner_i + j) % len(coords)
            cur_line.append(coords[cur_i])
            if self._is_corner(coords[cur_i], coords[cur_i - 1],
                               coords[(cur_i + 1) % len(coords)],
                               min_corner_angle_degree=self._min_corner_angle_degree):
                lines.append(LineString(cur_line))
                cur_line = [coords[cur_i]]
        return lines

    def _find_first_corner_index(self, coords):
        corner_i = None
        for i in range(len(coords)):
            last_last_coord = coords[i - 2]
            last_coord = coords[i - 1]
            cur_coord = coords[i]
            if self._is_corner(last_coord,
                               last_last_coord,
                               cur_coord,
                               min_corner_angle_degree=self._min_corner_angle_degree):
                corner_i = i - 1
                break
        if corner_i is None:
            raise ValueError("Polygon has no corner")
        return corner_i

    @staticmethod
    def _is_corner(cur_coord, prev_coord, next_coord, min_corner_angle_degree: float) -> bool:
        prev_vec = Vector2D.from_coordinates(prev_coord, cur_coord)
        next_vec = Vector2D.from_coordinates(cur_coord, next_coord)
        angle_in_degree = prev_vec.angle_to(next_vec)
        return angle_in_degree >= min_corner_angle_degree
