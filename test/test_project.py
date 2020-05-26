from unittest import TestCase

from shapely.geometry import Polygon, LineString

from shapely_ext.project import Projector
from test.constant import MATH_EPS


class TestProject(TestCase):
    def test_polygon_project_onto_polygon(self):
        polygon1 = Polygon([(3.5, 1), (6, 1), (6, 3), (3.5, 3)])
        polygon2 = Polygon([(1, 1), (3, 1), (3, 4), (4, 4), (4, 5), (0, 5),
                            (0, 4), (1, 4), (1, 1)])
        line = Projector(polygon1).project_onto(polygon2)
        self.assertTrue(isinstance(line, LineString))
        print(line.length, polygon2.buffer(MATH_EPS).intersection(line).length)
        self.assertEqual(line.length, polygon2.buffer(MATH_EPS).intersection(line).length)
