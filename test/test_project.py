from unittest import TestCase

from shapely.geometry import Polygon, LineString, Point

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

        Projector._insert_into_coords(coords, (5, 0))
        self.assertEqual(6, len(coords))
        self.assertListEqual([(0.0, 0.0), (5.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0), (0.0, 0.0)], coords)

    def test_insert_other_geom_projections_into_geom(self):
        polygon1 = Polygon([(3.5, 1), (6, 1), (6, 3), (3.5, 3)])
        polygon2 = Polygon([(1, 1), (3, 1), (3, 4), (4, 4), (4, 5), (0, 5),
                            (0, 4), (1, 4), (1, 1)])
        projector = Projector(polygon2, Vector2D(1, 0))
        new_polygon2 = projector._insert_other_geom_projections_into_geom(
            other_geom=polygon1, projecting_vector=Vector2D(-1, 0), geom=polygon2)
        self.assertEqual(len(polygon2.exterior.coords) + len(polygon1.exterior.coords),
                         len(new_polygon2.exterior.coords))

    def test_construct_by_coords_according_to(self):
        projector = object.__new__(Projector)
        ref_polygon = Polygon([(0, 0), (1, 0), (1, 1)], [[(0, 0), (0.5, 0), (0.5, 0.5)]])
        new_polygon = projector._construct_by_coords_according_to(ref_polygon, [(3.5, 1), (6, 1), (6, 3), (3.5, 3)])
        self.assertListEqual([(3.5, 1), (6, 1), (6, 3), (3.5, 3), (3.5, 1)], list(new_polygon.exterior.coords))
        self.assertEqual(list(ref_polygon.interiors), list(new_polygon.interiors))

        ref_lineString = LineString([(0, 0), (1, 0)])
        new_lineString = projector._construct_by_coords_according_to(ref_lineString, [(0, 0), (0, 1)])
        self.assertListEqual([(0, 0), (0, 1)], list(new_lineString.coords))

        ref_point = Point(0, 1)
        new_point = projector._construct_by_coords_according_to(ref_point, [(1, 0)])
        self.assertListEqual([(1, 0)], list(new_point.coords))
