import math
from typing import List
from unittest import TestCase

from shapely.geometry import box, LineString, Polygon, Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from shapely_ext.decompose import Decomposer
from test.constant import MATH_EPS


class TestDecompose(TestCase):
    def setUp(self):
        self.decomposer1 = Decomposer()
        self.decomposer_angle_tol = Decomposer(min_corner_angle_degree=15)

    def test_decompose_polygon(self):
        polygon1 = box(0, 0, 10, 5)
        lines1 = self.decomposer1.decompose(geometry=polygon1)
        self.assertEqual(4, len(lines1))
        self._test_objects_are_all_of_type(lines1, LineString)
        self._test_objects_are_of_lens(lines1, [10, 10, 5, 5])

        polygon2 = Polygon([(0, 0), (1, 1), (0, 1)])
        lines2 = self.decomposer1.decompose(geometry=polygon2)
        self.assertEqual(3, len(lines2))
        self._test_objects_are_all_of_type(lines2, LineString)
        self._test_objects_are_of_lens(lines2, [1, 1, 2 ** 0.5])

        circle = Point(0.5, 0.5).buffer(0.5)
        polygon3 = unary_union([circle, box(0.5, 0, 1.5, 1)])
        line3 = self.decomposer_angle_tol.decompose(polygon3)
        self.assertEqual(2, len(line3))
        self._test_objects_are_all_of_type(line3, LineString)
        self._test_objects_are_of_lens(line3, [1, math.pi / 2 + 2])

    def _test_objects_are_all_of_type(self, geoms: List[BaseGeometry], type_class):
        return self.assertTrue(all(isinstance(g, type_class) for g in geoms))

    def _test_objects_are_of_lens(self, geoms: List[BaseGeometry], lens: List[float], delta: float = MATH_EPS):
        geom_lens = sorted(map(lambda g: g.length, geoms))
        lens.sort()
        for geom_len, expected_len in zip(geom_lens, lens):
            self.assertAlmostEqual(expected_len, geom_len, delta=delta)
