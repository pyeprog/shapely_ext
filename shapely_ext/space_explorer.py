from copy import deepcopy
from enum import Enum
from functools import partial
from typing import List, Callable

from shapely.affinity import scale, rotate
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree

from shapely_ext.angle import get_polygon_angle_by_bounding_box


class SpaceExplorer:
    """ explore in 2D space and find the biggest shape not intsects with any obstacles """

    class Direction(Enum):
        LEFT = 1
        RIGHT = 2
        UP = 3
        DOWN = 4
        LEFT_AND_RIGHT_TOGETHER = 5  # exploring in left and right at the same time
        UP_AND_DOWN_TOGETHER = 6  # exploring in up and down at the same time
        ALL_TOGETHER = 7  # exploring in all directions at the same time

        ALL_RESPECTIVELY = 8  # exploring in all directions one by one
        LEFT_AND_RIGHT_RESPECTIVELY = 9  # exploring in left, then right
        UP_AND_DOWN_RESPECTIVELY = 10  # exploring in up, then down

    def __init__(self, obstacles: List[BaseGeometry], available_area: Polygon = None, eps: float = 1e-6,
                 max_explore_distance: float = 1e10):
        """
        :param obstacles: obstacle geometry objects that explorer should not touch
        """
        self._available_area = deepcopy(available_area)
        self._obstacles = deepcopy(obstacles) + self.get_global_obstacle(self._available_area)
        self._rtree = STRtree(self._obstacles)
        self._eps = eps
        self._max_explore_distance = max_explore_distance

    def get_global_obstacle(self, available_area: Polygon) -> List[Polygon]:
        if available_area is None:
            return []
        return [self._available_area.buffer(self._max_explore_distance).difference(self._available_area)]

    def explore_largest_polygon(self, polygon: Polygon,
                                exploring_direct: Direction = Direction.ALL_TOGETHER,
                                max_iter: int = 10) -> Polygon:
        if self._available_area is not None and not self._available_area.contains(polygon):
            raise ValueError("polygon doesn't start inside of available_area")

        polygon_angle_degree = get_polygon_angle_by_bounding_box(polygon, in_degree=True)
        composite_exploring_directions = [self.Direction.ALL_RESPECTIVELY,
                                          self.Direction.LEFT_AND_RIGHT_RESPECTIVELY,
                                          self.Direction.UP_AND_DOWN_RESPECTIVELY]
        if exploring_direct not in composite_exploring_directions:
            return self._explore_largest_polygon_single_round(polygon=polygon,
                                                              polygon_angle_degree=polygon_angle_degree,
                                                              exploring_direct_in_one_round=exploring_direct,
                                                              max_iter=max_iter)
        exploring_dir_queue = []
        if exploring_direct == self.Direction.LEFT_AND_RIGHT_RESPECTIVELY:
            exploring_dir_queue.append(self.Direction.LEFT)
            exploring_dir_queue.append(self.Direction.RIGHT)
        elif exploring_direct == self.Direction.UP_AND_DOWN_RESPECTIVELY:
            exploring_dir_queue.append(self.Direction.UP)
            exploring_dir_queue.append(self.Direction.DOWN)
        else:
            exploring_dir_queue.append(self.Direction.UP)
            exploring_dir_queue.append(self.Direction.DOWN)
            exploring_dir_queue.append(self.Direction.LEFT)
            exploring_dir_queue.append(self.Direction.RIGHT)

        for exploring_dir in exploring_dir_queue:
            polygon = self._explore_largest_polygon_single_round(polygon=polygon,
                                                                 polygon_angle_degree=polygon_angle_degree,
                                                                 exploring_direct_in_one_round=exploring_dir,
                                                                 max_iter=max_iter)
        return polygon

    def _explore_largest_polygon_single_round(self, polygon: Polygon,
                                              polygon_angle_degree: float,
                                              exploring_direct_in_one_round: Direction = Direction.ALL_TOGETHER,
                                              max_iter: int = 10):
        if len(self.get_intersected(polygon)) > 0:
            return polygon

        scale_func = partial(self.rotate_scale_rotate_back,
                             ccw_rotate_angle_degree=-polygon_angle_degree,
                             direct=exploring_direct_in_one_round)
        # noinspection PyTypeChecker
        return self._explore_scaling(origin_geometry=polygon,
                                     scale_func=scale_func,
                                     max_iter=max_iter)

    def _explore_scaling(self, origin_geometry: BaseGeometry,
                         scale_func: Callable[[BaseGeometry, float], BaseGeometry],
                         max_iter: int = 10) -> BaseGeometry:
        """

        :rtype: shapely geometry
        :param origin_geometry:
        :param scale_func:
        :param max_iter:
        :return:
        """
        lower_scale = 1
        upper_scale = 2
        last_failed_upper = None
        for _ in range(max_iter):
            # noinspection PyArgumentList
            geometry = scale_func(geometry=origin_geometry, fact=upper_scale)
            if len(self.get_intersected(geometry)) == 0:
                lower_scale = upper_scale
                if last_failed_upper is None:
                    upper_scale *= 2
                else:
                    upper_scale = last_failed_upper
            else:
                last_failed_upper = upper_scale
                upper_scale = (lower_scale + upper_scale) / 2

        # noinspection PyArgumentList
        return scale_func(geometry=origin_geometry, fact=lower_scale)

    @staticmethod
    def rotate_scale_rotate_back(geometry: BaseGeometry,
                                 ccw_rotate_angle_degree: float,
                                 direct: Direction,
                                 fact: float = 1):
        """

        :param geometry:
        :param ccw_rotate_angle_degree:
        :param direct:
        :param fact:
        :return:
        """
        if fact == 1:
            return geometry
        if ccw_rotate_angle_degree == 0:
            return SpaceExplorer.scale(geometry=geometry, direct=direct, fact=fact)

        origin = geometry.envelope.centroid
        rotated_geometry = rotate(geometry, ccw_rotate_angle_degree)
        scaled_geometry = SpaceExplorer.scale(geometry=rotated_geometry, direct=direct, fact=fact)
        return rotate(scaled_geometry, -ccw_rotate_angle_degree, origin=origin)

    @staticmethod
    def scale(geometry: BaseGeometry,
              direct: Direction = Direction.ALL_TOGETHER,
              fact: float = 1):
        """

        :param geometry:
        :param direct:
        :param fact:
        :return:
        """
        x_min, y_min, x_max, y_max = geometry.bounds
        if direct == SpaceExplorer.Direction.LEFT_AND_RIGHT_TOGETHER:
            origin = "center"
            x_fact = fact
            y_fact = 1
        elif direct == SpaceExplorer.Direction.UP_AND_DOWN_TOGETHER:
            origin = "center"
            x_fact = 1
            y_fact = fact
        elif direct == SpaceExplorer.Direction.LEFT:
            origin = (x_max, (y_min + y_max) / 2)
            x_fact = fact
            y_fact = 1
        elif direct == SpaceExplorer.Direction.RIGHT:
            origin = (x_min, (y_min + y_max) / 2)
            x_fact = fact
            y_fact = 1
        elif direct == SpaceExplorer.Direction.UP:
            origin = ((x_min + x_max) / 2, y_min)
            x_fact = 1
            y_fact = fact
        elif direct == SpaceExplorer.Direction.DOWN:
            origin = ((x_min + x_max) / 2, y_max)
            x_fact = 1
            y_fact = fact
        else:
            origin = "center"
            x_fact = y_fact = fact
        return scale(geometry, xfact=x_fact, yfact=y_fact, origin=origin)

    def get_intersected(self, geometry):
        """

        :param geometry:
        :return:
        """
        possible_intersections = self._rtree.query(geometry.buffer(self._eps))

        # since rtree search nearby geometries using envelope, result may include false positive case
        return [g for g in possible_intersections if g and geometry.distance(g) < self._eps]
