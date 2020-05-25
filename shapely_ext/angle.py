import math
from typing import Tuple, List

from shapely.geometry import LineString, Polygon


class AngleMeasurer:
    def __init__(self, simplify_distance: float = 1e-6):
        self._simplify_distance = simplify_distance

    def get_straight_line_angle(self, line: LineString, in_degree: bool = True) -> float:
        """
        return angle in range [-90, 90]
        """
        if not line.is_valid:
            raise ValueError("input line is not a valid lineString")
        coords = list(line.coords)
        endpoint1, endpoint2 = coords[0], coords[-1]

        angle_in_radian = (math.atan2(endpoint2[1] - endpoint1[1], endpoint2[0] - endpoint1[0])) % math.pi
        if angle_in_radian > math.pi / 2:
            angle_in_radian -= math.pi
        if in_degree:
            return math.degrees(angle_in_radian)
        return angle_in_radian

    def get_angle_by_coords(self, coord1: Tuple[float, float], coord2: Tuple[float, float],
                            in_degree: bool = True) -> float:
        if coord1 == coord2:
            raise ValueError("coord1 and coord2 should not be equal")
        line = LineString([coord1, coord2])
        return self.get_straight_line_angle(line, in_degree=in_degree)

    def get_polygon_angle_by_bounding_box(self, polygon: Polygon, in_degree: bool = True) -> float:
        """
        计算polygon的最小外接矩形的长边的角度, return angle in range [-90, 90]
        """
        rotated_box_coords = list(polygon.minimum_rotated_rectangle.simplify(self._simplify_distance).exterior.coords)
        edges = [(rotated_box_coords[i], rotated_box_coords[i + 1]) for i in range(2)]
        longest_edge = max(edges,
                           key=lambda coords: (coords[0][0] - coords[1][0]) ** 2 + (coords[0][1] - coords[1][1]) ** 2)
        return self.get_angle_by_coords(*longest_edge, in_degree=in_degree)
