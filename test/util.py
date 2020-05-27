from shapely.geometry.base import BaseGeometry

from test.constant import MATH_EPS


def is_geom_equal(geom1: BaseGeometry, geom2: BaseGeometry):
    return geom1.symmetric_difference(geom2).area < MATH_EPS
