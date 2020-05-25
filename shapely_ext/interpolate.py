import math
from typing import Tuple, List

from shapely.geometry import Polygon, Point, MultiPoint, LineString, LinearRing, MultiPolygon, MultiLineString, \
    GeometryCollection
from shapely.geometry.base import BaseGeometry


def interpolate_coords_by_len(coord1: Tuple[float, float],
                              coord2: Tuple[float, float],
                              gap: float,
                              result_include_coord2: bool = True) -> List[Tuple[float, float]]:
    vector = (coord2[0] - coord1[0], coord2[1] - coord1[1])
    vec_len = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    unit_vector = (vector[0] / vec_len, vector[1] / vec_len)

    result = [coord1]
    for i in range(1, round(vec_len / gap)):
        result.append((coord1[0] + unit_vector[0] * i * gap, coord1[1] + unit_vector[1] * i * gap))
    if result_include_coord2:
        result.append(coord2)
    return result


def interpolate(geometry: BaseGeometry, gap: float, simplify_distance: float = 1e-6) -> BaseGeometry:
    def interpolate_coords(coords):
        new_coords: List[Tuple[float, float]] = []
        for i in range(len(coords) - 2):
            new_coords.extend(interpolate_coords_by_len(coords[i], coords[i + 1], gap, result_include_coord2=False))
        new_coords.extend(interpolate_coords_by_len(coords[-2], coords[-1], gap, result_include_coord2=True))
        return new_coords

    if isinstance(geometry, (Point, MultiPoint)):
        return geometry
    elif isinstance(geometry, (Polygon, LineString, LinearRing)):
        geometry_simplified = geometry.simplify(simplify_distance)
        if isinstance(geometry, Polygon):
            exterior_coords = list(geometry_simplified.exterior.coords)
            interior_coords_list = [list(interior.coords) for interior in geometry_simplified.interiors]
            interpolated_exterior = interpolate_coords(exterior_coords)
            interpolated_interiors = [interpolate_coords(interior_coords) for interior_coords in interior_coords_list]
            return Polygon(shell=interpolated_exterior, holes=interpolated_interiors)
        else:  # LineString or LinearRing
            coords = list(geometry_simplified.coords)
            return type(geometry)(interpolate_coords(coords))
    elif isinstance(geometry, (MultiPolygon, MultiLineString, GeometryCollection)):
        geoms = list(geometry)
        interpolated_geoms = [interpolate(geom, gap) for geom in geoms]
        return type(geometry)(interpolated_geoms)

    return geometry  # return origin geometry if not match any type
