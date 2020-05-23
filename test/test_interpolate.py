from unittest import TestCase

from shapely.geometry import box, Polygon, LineString, MultiPoint, Point, GeometryCollection

from shapely_ext.interpolate import interpolate


class TestInterpolate(TestCase):
    def test_interpolate(self):
        rect = box(0, 0, 10, 10)
        interpolated_rect = interpolate(rect, 5)
        self.assertTrue(type(rect) is type(interpolated_rect))
        self.assertTrue(len(list(rect.exterior.coords)) < len(list(interpolated_rect.exterior.coords)))
        self.assertEqual(9, len(list(interpolated_rect.exterior.coords)))

        polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)], [[(4, 4), (4, 6), (6, 6), (6, 4)]])
        interpolated_polygon = interpolate(polygon, 1)
        self.assertTrue(type(polygon) is type(interpolated_polygon))
        self.assertTrue(len(list(polygon.exterior.coords)) < len(list(interpolated_polygon.exterior.coords)))
        self.assertTrue(
            len(list(polygon.interiors[0].coords)) < len(list(interpolated_polygon.interiors[0].coords)))
        self.assertEqual(41, len(list(interpolated_polygon.exterior.coords)))
        self.assertEqual(9, len(list(interpolated_polygon.interiors[0].coords)))

        line = LineString([(0, 0), (10, 0)])
        interpolated_line = interpolate(line, 1)
        self.assertTrue(type(line) is type(interpolated_line))
        self.assertTrue(len(line.coords) < len(interpolated_line.coords))
        self.assertEqual(11, len(interpolated_line.coords))

        point = Point(0, 0)
        interpolated_point = interpolate(point, 1)
        self.assertTrue(type(point) is type(interpolated_point))
        self.assertEqual(point, interpolated_point)

        mp = MultiPoint([point, point])
        interpolated_mp = interpolate(mp, 1)
        self.assertTrue(type(mp) is type(interpolated_mp))
        self.assertEqual(mp, interpolated_mp)

        collection = GeometryCollection([mp, point, line, polygon])
        interpolated_collection = interpolate(collection, 1)
        self.assertTrue(type(collection) is type(interpolated_collection))
        self.assertEqual(len(collection), len(list(interpolated_collection)))
        processed_polygon = list(filter(lambda geom: isinstance(geom, Polygon), list(interpolated_collection)))[0]
        self.assertEqual(41, len(list(processed_polygon.exterior.coords)))
        self.assertEqual(9, len(list(processed_polygon.interiors[0].coords)))
        processed_line = list(filter(lambda geom: isinstance(geom, LineString), list(interpolated_collection)))[0]
        self.assertEqual(11, len(processed_line.coords))
