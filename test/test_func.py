from unittest import TestCase

from shapely.geometry import box

from shapely_ext.func import group


class TestGroup(TestCase):
    def test_group_num(self):
        items = [0, 0.1, 0.2, 0.3, 2, 2.1, 2.12, 10, 10.1]
        groups = group(items, grouping_func=lambda x1, x2: abs(x1 - x2) < 0.15)
        self.assertEqual(3, len(groups))
        groups.sort(key=len)
        self.assertListEqual([10, 10.1], sorted(groups[0]))
        self.assertListEqual([2, 2.1, 2.12], sorted(groups[1]))
        self.assertListEqual([0, 0.1, 0.2, 0.3], sorted(groups[2]))

    def test_group_polygon(self):
        boxes = [
            box(0, 0, 1, 1),
            box(1.1, 1, 2, 2),
            box(-10, 0, -9, 1),
        ]
        groups = group(boxes, grouping_func=lambda b1, b2: b1.distance(b2) < 0.5)
        self.assertEqual(2, len(groups))
        groups.sort(key=len)
        self.assertListEqual([boxes[2]], groups[0])
        self.assertListEqual(boxes[:2], groups[1])
