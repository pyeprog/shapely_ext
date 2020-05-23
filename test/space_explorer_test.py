from unittest import TestCase

from shapely.affinity import rotate
from shapely.geometry import Polygon, Point, box

from shapely_ext.angle import get_polygon_angle_by_bounding_box
from shapely_ext.space_explorer import SpaceExplorer


class TestSpaceExplorer(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        polygons = [
            Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
            Polygon([(90, 0), (100, 0), (100, 10), (90, 10)]),
            Polygon([(90, 90), (100, 90), (100, 100), (90, 100)]),
            Polygon([(0, 90), (10, 90), (10, 100), (0, 100)]),
            Polygon([(10, 50), (20, 50), (20, 60), (10, 60)]),
        ]
        cls.explorer = SpaceExplorer(polygons)

    def test_explore_largest_polygon(self):
        polygons1 = [
            box(0, 0, 10, 100),
            box(90, 0, 100, 100)
        ]
        explorer1 = SpaceExplorer(polygons1)
        result1 = explorer1.explore_largest_polygon(polygon=box(48, 49, 52, 51),
                                                    exploring_direct=SpaceExplorer.Direction.LEFT_AND_RIGHT_TOGETHER,
                                                    max_iter=20)
        min_x, min_y, max_x, max_y = result1.bounds
        self.assertAlmostEqual(80, max_x - min_x, delta=1)
        self.assertAlmostEqual(2, max_y - min_y, delta=1)

        result11 = explorer1.explore_largest_polygon(polygon=box(50, 10, 61, 20),
                                                     exploring_direct=SpaceExplorer.Direction.RIGHT,
                                                     max_iter=20)
        min_x, min_y, max_x, max_y = result11.bounds
        self.assertAlmostEqual(90, max_x, delta=1)
        self.assertAlmostEqual(50, min_x, delta=1e-6)
        self.assertAlmostEqual(10, max_y - min_y, delta=1e-6)

        polygons2 = [
            box(0, 0, 100, 5),
            box(0, 100, 100, 102),
        ]
        explorer2 = SpaceExplorer(polygons2)
        result2 = explorer2.explore_largest_polygon(box(40, 30, 45, 31),
                                                    exploring_direct=SpaceExplorer.Direction.UP_AND_DOWN_TOGETHER,
                                                    max_iter=20)
        min_x, min_y, max_x, max_y = result2.bounds
        self.assertAlmostEqual(50, max_y - min_y, delta=1)
        self.assertAlmostEqual(5, max_x - min_x, delta=1)

        result22 = explorer2.explore_largest_polygon(box(40, 30, 45, 31),
                                                     exploring_direct=SpaceExplorer.Direction.DOWN,
                                                     max_iter=20)
        min_x, min_y, max_x, max_y = result22.bounds
        self.assertAlmostEqual(5, min_y, delta=1)
        self.assertAlmostEqual(31, max_y, delta=1e-6)
        self.assertAlmostEqual(40, min_x, delta=1e-6)
        self.assertAlmostEqual(45, max_x, delta=1e-6)

        polygons3 = [
            box(0, 0, 10, 10),
            box(90, 90, 100, 100),
        ]
        explorer3 = SpaceExplorer(polygons3)
        result3 = explorer3.explore_largest_polygon(Polygon([(52, 46), (54, 48), (48, 54), (46, 52)]),
                                                    exploring_direct=SpaceExplorer.Direction.UP_AND_DOWN_TOGETHER,
                                                    max_iter=40)
        self.assertAlmostEqual(45, get_polygon_angle_by_bounding_box(result3, in_degree=True), delta=1e-6)
        self.assertAlmostEqual(960, result3.area, delta=1)

        coords = list(result3.exterior.coords)[:-1]
        for i in range(len(coords)):
            prev = coords[i - 2]
            cur = coords[i - 1]
            post = coords[i]
            vec1 = (cur[0] - prev[0], cur[1] - prev[1])
            vec2 = (post[0] - cur[0], post[1] - cur[1])
            self.assertAlmostEqual(0, vec1[0] * vec2[0] + vec1[1] * vec2[1], delta=1e-6)

    def test_rotate_scale_rotate_back(self):
        rectangle = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        rotated_rect = rotate(rectangle, 45)
        scale_rotate_rect = SpaceExplorer.rotate_scale_rotate_back(geometry=rotated_rect,
                                                                   ccw_rotate_angle_degree=-45,
                                                                   direct=SpaceExplorer.Direction.LEFT_AND_RIGHT_TOGETHER,
                                                                   fact=2)
        self.assertAlmostEqual(100, scale_rotate_rect.area, delta=1e-6)
        self.assertAlmostEqual(rotated_rect.centroid.x, scale_rotate_rect.centroid.x, delta=1e-6)
        self.assertAlmostEqual(rotated_rect.centroid.y, scale_rotate_rect.centroid.y, delta=1e-6)
        coords = list(scale_rotate_rect.exterior.coords)[:-1]
        for i in range(len(coords)):
            prev = coords[i - 2]
            cur = coords[i - 1]
            post = coords[i]
            vec1 = (cur[0] - prev[0], cur[1] - prev[1])
            vec2 = (post[0] - cur[0], post[1] - cur[1])
            self.assertAlmostEqual(0, vec1[0] * vec2[0] + vec1[1] * vec2[1], delta=1e-6)

    def test_get_intersected(self):
        result1 = self.explorer.get_intersected(Point(25, 55).buffer(3))
        self.assertEqual(0, len(result1))

        result2 = self.explorer.get_intersected(Point(25, 55).buffer(5))
        self.assertEqual(1, len(result2))

        result3 = self.explorer.get_intersected(Point(25, 55).buffer(10))
        self.assertEqual(1, len(result3))

        result4 = self.explorer.get_intersected(box(5, 5, 15, 95))
        self.assertEqual(3, len(result4))

        result5 = self.explorer.get_intersected(box(80, -20, 91, 101))
        self.assertEqual(2, len(result5))

        result6 = self.explorer.get_intersected(box(0, 0, 100, 100))
        self.assertEqual(5, len(result6))
