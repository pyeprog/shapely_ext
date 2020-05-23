import math
from unittest import TestCase

from shapely.geometry import box
from shapely.geometry.base import BaseGeometry

from shapely_ext.geometry.vector_2d import Vector2D
from test.constant import MATH_EPS


class TestVector2D(TestCase):
    def test_is_valid_2d_coordinate(self):
        self.assertTrue(Vector2D.is_valid_2d_coordinate((0, 1)))
        self.assertTrue(Vector2D.is_valid_2d_coordinate((0., 1)))
        self.assertTrue(Vector2D.is_valid_2d_coordinate((0., 1, 2)))
        self.assertTrue(Vector2D.is_valid_2d_coordinate((0., 1, '2')))
        self.assertFalse(Vector2D.is_valid_2d_coordinate(0))
        self.assertFalse(Vector2D.is_valid_2d_coordinate([9]))
        self.assertFalse(Vector2D.is_valid_2d_coordinate(['a']))
        self.assertFalse(Vector2D.is_valid_2d_coordinate(['a', 1]))

    def test_from_coordinate(self):
        vector1 = Vector2D.from_coordinate([0, 1])
        self.assertTrue(isinstance(vector1, Vector2D))
        self.assertEqual(0, vector1.x)
        self.assertEqual(1, vector1.y)

        vector2 = Vector2D.from_coordinate((1, 2, 1))
        self.assertTrue(isinstance(vector2, Vector2D))
        self.assertEqual(1, vector2.x)
        self.assertEqual(2, vector2.y)

        with self.assertRaises(ValueError):
            Vector2D.from_coordinate([1])
        with self.assertRaises(ValueError):
            Vector2D.from_coordinate(['a', 1, 1])

    def test_from_coordinates(self):
        vector1 = Vector2D.from_coordinates((0, 0), (1, 1))
        self.assertTrue(isinstance(vector1, Vector2D))
        self.assertEqual(1, vector1.x)
        self.assertEqual(1, vector1.y)

        with self.assertRaises(ValueError):
            Vector2D.from_coordinates(('a', 1), [1, 1])
        with self.assertRaises(ValueError):
            Vector2D.from_coordinates((0, 1), [1])

    def test_get_angle_with(self):
        vector1 = Vector2D(1, 0)
        other1 = Vector2D(1, 1)
        self.assertAlmostEqual(45, vector1.angle_ccw_rotating_to(other1), delta=MATH_EPS)

        other2 = Vector2D(1, -1)
        self.assertAlmostEqual(315, vector1.angle_ccw_rotating_to(other2), delta=MATH_EPS)

        vector2 = Vector2D(1, 0)
        other3 = Vector2D(1, math.sqrt(3))
        self.assertAlmostEqual(60, vector2.angle_ccw_rotating_to(other3), delta=MATH_EPS)
        self.assertAlmostEqual(300, other3.angle_ccw_rotating_to(vector2), delta=MATH_EPS)

    def test_rotate_to(self):
        vector1 = Vector2D(1, 0)
        other1 = Vector2D(1, -1)
        self.assertAlmostEqual(45, vector1.angle_to(other1), delta=MATH_EPS)
        other2 = Vector2D(1, 1)
        self.assertAlmostEqual(45, vector1.angle_to(other2), delta=MATH_EPS)

    def test_len(self):
        vector1 = Vector2D(1, 0)
        self.assertAlmostEqual(1.0, vector1.length)

        vector2 = Vector2D(2, 0)
        self.assertAlmostEqual(2.0, vector2.length)

        vector3 = Vector2D(1, 1)
        self.assertAlmostEqual(2 ** 0.5, vector3.length)

    def test_dot(self):
        vector1 = Vector2D(1, 1)
        vector2 = Vector2D(-1, -1)
        self.assertAlmostEqual(-2, vector1.dot(vector2), delta=0)
        self.assertAlmostEqual(-2, vector2.dot(vector1), delta=0)

        vector3 = Vector2D(1, 1)
        vector4 = Vector2D(-1, 1)
        self.assertEqual(0, vector3.dot(vector4))
        self.assertEqual(0, vector4.dot(vector1))

    @staticmethod
    def _is_geom_equal(geom1: BaseGeometry, geom2: BaseGeometry):
        return geom1.symmetric_difference(geom2).area < MATH_EPS

    def test_apply(self):
        polygon = box(0, 0, 1, 1)
        vector = Vector2D(1, 1)
        expected = box(1, 1, 2, 2)
        self.assertTrue(self._is_geom_equal(expected, vector.apply(polygon)))

    def test_plus(self):
        vector1 = Vector2D(1, 3.14)
        vector2 = Vector2D(-1, -2)
        expected = Vector2D(0, 1.14)
        self.assertTrue(expected, vector1.plus(vector2))
        self.assertTrue(expected, vector2.plus(vector1))
        self.assertEqual(1, vector1.x)
        self.assertEqual(3.14, vector1.y)
        self.assertEqual(-1, vector2.x)
        self.assertEqual(-2, vector2.y)

    def test_eq(self):
        vector1 = Vector2D(1, 3.14)
        vector2 = Vector2D(-1, -2)
        vector3 = Vector2D(1, 3.14)

        self.assertEqual(vector1, vector3)
        self.assertNotEqual(vector1, vector2)
