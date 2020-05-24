from itertools import chain
from typing import List

from shapely.geometry import Polygon, LineString, LinearRing, MultiPolygon, MultiLineString, GeometryCollection
from shapely.geometry.base import BaseGeometry

from shapely_ext.geometry.vector_2d import Vector2D


class Decompose:
    @staticmethod
    def decompose_to_line(
            geometry: BaseGeometry,
            min_corner_angle_degree: float = 0,
            simplify_radius: float = 1e-6) -> List[BaseGeometry]:
        geometry = geometry.simplify(simplify_radius)
        if isinstance(geometry, Polygon):
            return Decompose.decompose_polygon_to_line(
                polygon=geometry,
                min_corner_angle_degree=min_corner_angle_degree)
        elif isinstance(geometry, MultiPolygon):
            lines_list: List[List[LineString]] = [
                Decompose.decompose_polygon_to_line(
                    polygon=sub_polygon,
                    min_corner_angle_degree=min_corner_angle_degree)
                for sub_polygon in list(geometry)]
            return list(chain.from_iterable(lines_list))
        elif isinstance(geometry, LinearRing):
            return Decompose.decompose_linearRing_to_line(
                ring=geometry,
                min_corner_angle_degree=min_corner_angle_degree)
        elif isinstance(geometry, LineString):
            return Decompose.decompose_lineString_to_line(
                lineString=geometry,
                min_corner_angle_degree=min_corner_angle_degree)
        elif isinstance(geometry, MultiLineString):
            lines_list: List[List[LineString]] = [
                Decompose.decompose_lineString_to_line(
                    lineString=sub_lineString,
                    min_corner_angle_degree=min_corner_angle_degree)
                for sub_lineString in list(geometry)]
            return list(chain.from_iterable(lines_list))
        elif isinstance(geometry, GeometryCollection):
            lines_list: List[List[LineString]] =[
                Decompose.decompose_to_line(
                    geometry=sub_geometry,
                    min_corner_angle_degree=min_corner_angle_degree)
                for sub_geometry in list(geometry)]
            return list(chain.from_iterable(lines_list))
        else:
            return []

    @staticmethod
    def decompose_lineString_to_line(lineString: LineString, min_corner_angle_degree: float):
        coords = list(lineString.coords)
        lines: List[LineString] = []
        cur_line_coords = []
        for i in range(len(coords)):
            cur_line_coords.append(coords[i])
            if i - 1 < 0 or i + 1 >= len(coords):
                continue

            if Decompose._is_corner(coords[i], coords[i - 1], coords[i + 1],
                                    min_corner_angle_degree=min_corner_angle_degree):
                lines.append(LineString(cur_line_coords))
                cur_line_coords = [coords[i]]
        if cur_line_coords:
            lines.append(LineString(cur_line_coords))
        return lines

    @staticmethod
    def decompose_polygon_to_line(
            polygon: Polygon, min_corner_angle_degree: float) -> List[LineString]:
        exterior_lines: List[LineString] = Decompose.decompose_linearRing_to_line(
            ring=polygon.exterior,
            min_corner_angle_degree=min_corner_angle_degree)
        interior_lines_list: List[List[LineString]] = [
            Decompose.decompose_linearRing_to_line(
                ring=interior,
                min_corner_angle_degree=min_corner_angle_degree)
            for interior in polygon.interiors
        ]
        return exterior_lines + list(chain.from_iterable(interior_lines_list))

    @staticmethod
    def decompose_linearRing_to_line(
            ring: LinearRing,
            min_corner_angle_degree: float = 0) -> List[LineString]:
        coords = list(ring.coords)[:-1]
        corner_i = Decompose._find_first_corner_index(coords, min_corner_angle_degree)
        lines: List[LineString] = []
        cur_line = [coords[corner_i]]
        for j in range(1, len(coords) + 1):
            cur_i = (corner_i + j) % len(coords)
            cur_line.append(coords[cur_i])
            if Decompose._is_corner(coords[cur_i], coords[cur_i - 1],
                                    coords[(cur_i + 1) % len(coords)],
                                    min_corner_angle_degree=min_corner_angle_degree):
                lines.append(LineString(cur_line))
                cur_line = [coords[cur_i]]
        return lines

    @staticmethod
    def _find_first_corner_index(coords, min_corner_angle_degree):
        corner_i = None
        for i in range(len(coords)):
            last_last_coord = coords[i - 2]
            last_coord = coords[i - 1]
            cur_coord = coords[i]
            if Decompose._is_corner(last_coord,
                                    last_last_coord,
                                    cur_coord,
                                    min_corner_angle_degree=min_corner_angle_degree):
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
