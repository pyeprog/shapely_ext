from typing import List

from shapely.geometry import MultiLineString, LineString, Point, MultiPoint, Polygon, MultiPolygon, GeometryCollection, \
    LinearRing
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from shapely_ext.func import separate


def is_similar(geom1: BaseGeometry, geom2: BaseGeometry, eps: float = 1e-6) -> bool:
    if type(geom1) is not type(geom2):
        return False

    if isinstance(geom1, (LineString, MultiLineString, Point, MultiPoint)):
        return (geom1.buffer(eps).contains(geom2)
                and geom2.buffer(eps).contains(geom1))

    if isinstance(geom1, (Polygon, MultiPolygon)):
        return geom1.symmetric_difference(geom2).area < eps

    if isinstance(geom1, GeometryCollection):
        polygons1, non_polygons1 = separate(geom1, lambda geom: isinstance(geom, Polygon))
        polygons2, non_polygons2 = separate(geom2, lambda geom: isinstance(geom, Polygon))
        polygon_union1 = unary_union(polygons1)
        non_polygon_union1 = unary_union(non_polygons1)
        polygon_union2 = unary_union(polygons2)
        non_polygon_union2 = unary_union(non_polygons2)
        return (polygon_union1.symmetric_difference(polygon_union2).area < eps
                and non_polygon_union1.buffer(eps).contains(non_polygon_union2)
                and non_polygon_union2.buffer(eps).contains(non_polygon_union1))


def flatten(geom: BaseGeometry) -> List[BaseGeometry]:
    if isinstance(geom, (Polygon, LineString, LinearRing, Point)):
        return [geom]
    elif isinstance(geom, (MultiPolygon, MultiLineString, MultiPoint, GeometryCollection)):
        flattened: List[BaseGeometry] = []
        for sub_geom in list(geom):
            flattened.extend(flatten(sub_geom))
        return flattened
    return []
