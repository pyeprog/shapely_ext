from copy import deepcopy
from typing import Union, Optional, List, Tuple

from shapely.geometry import Polygon, LineString, LinearRing, Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import nearest_points

from shapely_ext.geometry.vector_2d import Vector2D


class Projector:
    def __init__(
            self,
            geom: Union[Polygon, LineString, LinearRing, Point],
            projecting_vector: Vector2D,
            max_projecting_length: float = 1e6,
            eps: float = 1e-6,
    ):
        self._geom = geom
        self._projecting_vector = projecting_vector
        self._max_projecting_length = max_projecting_length
        self._eps = eps

    def _get_coords(self, geom: BaseGeometry):
        if isinstance(geom, Polygon):
            return list(geom.exterior.coords)
        return list(geom.coords)

    def is_facing_point(self, point: Point, other_geom: BaseGeometry):
        return (
                self._geom.intersection(
                    LineString(nearest_points(point, other_geom))
                ).length
                < self._eps
        )

    def project_onto(self, other_geom: BaseGeometry):
        if isinstance(self._geom, Point):
            return self.get_projection_point(self._geom, other_geom, self._projecting_vector)

        geom = self._insert_other_geom_projections_into_geom(other_geom, self._projecting_vector.reverse(), self._geom)

        points = [Point(coord) for coord in self._get_coords(geom)]
        optional_projecting_points: List[Optional[Point]] = []
        for point in points:
            if self.is_facing_point(point, other_geom):
                projecting_point = self.get_projection_point(point, other_geom, self._projecting_vector)
                optional_projecting_points.append(projecting_point)
            else:
                optional_projecting_points.append(None)

        # find consecutive projecting points
        projecting_points = self.find_consecutive_projecting_points(
            optional_projecting_points
        )
        if len(projecting_points) > 1:
            return LineString(projecting_points)
        elif len(projecting_points) == 1:
            return projecting_points[0]
        return None

    def _insert_other_geom_projections_into_geom(self, other_geom, projecting_vector, geom):
        other_geom_coords = self._get_coords(other_geom)
        geom_coords = self._get_coords(geom)
        geom_coords_copy = deepcopy(geom_coords)
        for coord_of_other in other_geom_coords:
            projection_point = self.get_projection_point(Point(coord_of_other), geom, projecting_vector)
            if projection_point:
                self._insert_into_coords(geom_coords_copy, projection_point)
        return self._construct_by_coords_according_to(geom, geom_coords_copy)

    def _construct_by_coords_according_to(self, ref_geom, coords):
        if isinstance(ref_geom, Polygon):
            return Polygon(shell=coords, holes=ref_geom.interiors)
        return type(ref_geom)(coords)

    def get_projection_point(self, start_point: Point, other_geom: BaseGeometry, projecting_vector: Vector2D):
        ray_reaching_point = projecting_vector.multiply(self._max_projecting_length).apply(start_point)
        ray = LineString([start_point, ray_reaching_point])
        ray_intersection = ray.intersection(other_geom)
        if ray_intersection.is_empty:
            return None
        projection_point = nearest_points(ray_intersection, start_point)[0]
        return projection_point

    def find_consecutive_projecting_points(self, facing_points):
        double_facing_points = facing_points + facing_points
        projecting_points: List[Point] = []
        start_taking: bool = False
        reaching_none: bool = False
        for optional_point in double_facing_points:
            if not reaching_none and optional_point is None:
                reaching_none = True
            if reaching_none and not start_taking and optional_point is not None:
                start_taking = True
            if start_taking:
                if optional_point is None:
                    break
                projecting_points.append(optional_point)
        return projecting_points

    @staticmethod
    def _insert_into_coords(coords: List[Tuple[float, float]], coord: Tuple[float, float]) -> None:
        polygon = Polygon(coords)
        if not polygon.is_valid:
            raise ValueError("coords is not valid")
        point = Point(coord)
        for i in range(len(coords)):
            buffered_line = LineString([coords[i - 1], coords[i]]).buffer(1e-6)
            if buffered_line.intersects(point):
                coords.insert(i, coord)
                break
