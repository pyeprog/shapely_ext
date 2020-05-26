from typing import Union, Optional, List

from shapely.geometry import Polygon, LineString, LinearRing, Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import nearest_points

from shapely_ext.geometry.vector_2d import Vector2D


class Projector:
    def __init__(self, geom: Union[Polygon, LineString, LinearRing, Point],
                 projecting_vector: Vector2D,
                 eps: float = 1e-6):
        self._geom = geom
        self._projecting_vector = projecting_vector
        self._eps = eps

    def _get_coords(self, geom: BaseGeometry):
        if isinstance(geom, Polygon):
            return list(geom.exterior.coords)
        return list(geom.coords)

    def is_facing_point(self, point: Point, other_geom: BaseGeometry):
        return self._geom.intersection(LineString(nearest_points(point, other_geom))).length < self._eps

    def project_onto(self, other_geom: BaseGeometry):
        if isinstance(self._geom, Point):
            return nearest_points(other_geom, self._geom)[0]

        points = [Point(coord) for coord in self._get_coords(self._geom)]
        optional_projecting_points: List[Optional[Point]] = []
        for point in points:
            if self.is_facing_point(point, other_geom):
                optional_projecting_points.append(nearest_points(point, other_geom)[1])
            else:
                optional_projecting_points.append(None)

        # find consecutive projecting points
        project_points = self.find_consecutive_projecting_points(optional_projecting_points)
        return LineString(project_points)

    def get_projecting_point(self, start_point: Point, other_geom: BaseGeometry):


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
