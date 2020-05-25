import math
from unittest import TestCase

from shapely.geometry import LineString, Polygon

from shapely_ext.angle import AngleMeasurer


class Test(TestCase):
    def setUp(self) -> None:
        self.angle_measurer = AngleMeasurer()

    def test_get_straight_line_angle(self):
        line1 = LineString([(0, 0), (1, 1)])
        self.assertAlmostEqual(45, self.angle_measurer.get_straight_line_angle(line1, in_degree=True), delta=1e-6)

        line2 = LineString([(0, 0), (1, 0)])
        self.assertAlmostEqual(0, self.angle_measurer.get_straight_line_angle(line2, in_degree=True), delta=1e-6)

    def test_get_angle_by_coords(self):
        self.assertAlmostEqual(45, self.angle_measurer.get_angle_by_coords((0, 0), (1, 1), in_degree=True), delta=1e-6)
        self.assertAlmostEqual(0, self.angle_measurer.get_angle_by_coords((0, 0), (1, 0), in_degree=True), delta=1e-6)

    def test_get_polygon_angle_in_degree(self):
        polygon1 = Polygon([(0, 0), (100, 0), (100, 10), (0, 10)])
        polygon2 = Polygon([(0, 0), (10, 0), (10, 100), (0, 100)])
        polygon3 = Polygon([(1, 0), (11, 10), (10, 11), (0, 1)])
        polygon4 = Polygon([(1, 0), (11, -10), (10, -11), (0, -1)])

        self.assertEqual(0, self.angle_measurer.get_polygon_angle_by_bounding_box(polygon1))
        self.assertEqual(90, self.angle_measurer.get_polygon_angle_by_bounding_box(polygon2, in_degree=True))
        self.assertAlmostEqual(math.pi / 2,
                               self.angle_measurer.get_polygon_angle_by_bounding_box(polygon2, in_degree=False),
                               delta=1e-6)
        self.assertAlmostEqual(45, self.angle_measurer.get_polygon_angle_by_bounding_box(polygon3, in_degree=True),
                               delta=1e-6)
        self.assertAlmostEqual(45, self.angle_measurer.get_polygon_angle_by_bounding_box(polygon3, in_degree=True))
        self.assertAlmostEqual(math.pi / 4,
                               self.angle_measurer.get_polygon_angle_by_bounding_box(polygon3, in_degree=False))
        self.assertAlmostEqual(-45, self.angle_measurer.get_polygon_angle_by_bounding_box(polygon4), delta=1e-6)
        self.assertAlmostEqual(-math.pi / 4,
                               self.angle_measurer.get_polygon_angle_by_bounding_box(polygon4, in_degree=False),
                               delta=1e-6)
