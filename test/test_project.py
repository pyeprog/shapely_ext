from unittest import TestCase

from shapely.geometry import Polygon, LineString, box

from shapely_ext.geometry.vector_2d import Vector2D
from shapely_ext.project import Projector
from test.constant import MATH_EPS


class TestProject(TestCase):
    def test_small_polygon_project_onto_large_polygon(self):
        polygon1 = Polygon([(3.5, 1), (6, 1), (6, 3), (3.5, 3)])
        polygon2 = Polygon([(1, 1), (3, 1), (3, 4), (4, 4), (4, 5), (0, 5),
                            (0, 4), (1, 4), (1, 1)])
        line = Projector(polygon1, projecting_vector=Vector2D(-1, 0)).project_onto(polygon2)
        self.assertTrue(isinstance(line, LineString))
        self.assertEqual(line.length, polygon2.buffer(MATH_EPS).intersection(line).length)

    def test_large_polygon_project_onto_small_polygon(self):
        polygon1 = Polygon([(3.5, 1), (6, 1), (6, 3), (3.5, 3)])
        polygon2 = Polygon([(1, 1), (3, 1), (3, 4), (4, 4), (4, 5), (0, 5),
                            (0, 4), (1, 4), (1, 1)])
        line = Projector(polygon2, projecting_vector=Vector2D(1, 0)).project_onto(polygon1)
        self.assertTrue(isinstance(line, LineString))
        self.assertEqual(line.length, polygon1.buffer(MATH_EPS).intersection(line).length)

    def test_insert_coord(self):
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        coords = list(rect.exterior.coords)

        new_coords = Projector._insert_into_coords(coords, (5, 0))
        self.assertEqual(6, len(new_coords))

