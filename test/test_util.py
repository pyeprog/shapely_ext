from unittest import TestCase

from shapely.geometry import box, Polygon, MultiPolygon, GeometryCollection, Point

from shapely_ext.util import is_similar, flatten


class UtilTest(TestCase):
    def test_is_similar(self):
        geom1 = box(0, 0, 1, 1)
        geom2 = Polygon([(1, 1), (1, 0), (0, 0), (0, 1)])
        self.assertTrue(is_similar(geom1, geom2))
        self.assertTrue(is_similar(geom2, geom1))

        multi_geom2 = MultiPolygon([geom2])
        self.assertFalse(is_similar(geom1, multi_geom2))
        self.assertFalse(is_similar(multi_geom2, geom1))

        geom_col1 = GeometryCollection([geom1, geom2, Point(0, 1)])
        geom_col2 = GeometryCollection([geom1, geom2])
        self.assertFalse(is_similar(geom_col1, geom_col2))
        self.assertFalse(is_similar(geom_col2, geom_col1))

    def test_flatten(self):
        polygon = box(0, 0, 1, 1)
        result1 = flatten(polygon)
        self.assertTrue(isinstance(result1, list))
        self.assertEqual(1, len(result1))

        geoms = GeometryCollection([MultiPolygon([box(0, 0, 1, 1)]), box(0, 0, 1, 1)])
        result2 = flatten(geoms)
        self.assertTrue(isinstance(result2, list))
        self.assertEqual(2, len(result2))