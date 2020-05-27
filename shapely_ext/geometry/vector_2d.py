import math
from typing import Sequence, TypeVar

from shapely.affinity import translate
from shapely.geometry.base import BaseGeometry

Num = TypeVar('Num', float, int)


class Vector2D:
    def __init__(self, x, y):
        if not isinstance(x, (float, int)) or not isinstance(y, (float, int)):
            raise TypeError("x, y should be number")
        self.x = x
        self.y = y

    @staticmethod
    def is_valid_2d_coordinate(coord: Sequence[Num]):
        return (isinstance(coord, Sequence)
                and len(coord) >= 2
                and isinstance(coord[0], (int, float))
                and isinstance(coord[1], (int, float)))

    @classmethod
    def from_coordinate(cls, coord: Sequence[Num]):
        if not cls.is_valid_2d_coordinate(coord):
            raise ValueError(f"{coord} is not valid coordinates")
        return cls(x=coord[0], y=coord[1])

    @classmethod
    def from_coordinates(cls, from_coord: Sequence[Num], to_coord: Sequence[Num]):
        if not cls.is_valid_2d_coordinate(from_coord):
            raise ValueError(f"{from_coord} is not valid from_coordinates")
        if not cls.is_valid_2d_coordinate(to_coord):
            raise ValueError(f"{to_coord} is not valid from_coordinates")
        return cls(x=to_coord[0] - from_coord[0], y=to_coord[1] - from_coord[1])

    @property
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    @classmethod
    def raise_if_not_vector(cls, possible_vector):
        if not isinstance(possible_vector, cls):
            raise TypeError(f"{possible_vector} is of type {type(possible_vector)}, expect Vector2D")

    def plus(self, vector):
        self.raise_if_not_vector(vector)
        return Vector2D(self.x + vector.x, self.y + vector.y)

    def dot(self, vector) -> Num:
        self.raise_if_not_vector(vector)
        return self.x * vector.x + self.y * vector.y

    def angle_ccw_rotating_to(self, vector_2d, in_degree: bool = True):
        """
        in range of [0, 360] degree
        """
        dot_prod = self.dot(vector_2d)
        cos_val = dot_prod / self.length / vector_2d.length
        angle_in_radian = math.acos(cos_val)
        cross_prod = self.x * vector_2d.y - self.y * vector_2d.x
        if cross_prod < 0:  # then vector_2d is on the cw side of self vector
            angle_in_radian = math.pi * 2 - angle_in_radian
        if in_degree:
            return math.degrees(angle_in_radian)
        return angle_in_radian

    def angle_to(self, vector_2d, in_degree: bool = True):
        """
        in range of [0, 180]
        """
        ccw_rotating_angle_degree = self.angle_ccw_rotating_to(vector_2d)
        if ccw_rotating_angle_degree > 180:
            ccw_rotating_angle_degree = 360 - ccw_rotating_angle_degree
        if not in_degree:
            return math.radians(ccw_rotating_angle_degree)
        return ccw_rotating_angle_degree

    def apply(self, geom: BaseGeometry) -> BaseGeometry:
        return translate(geom, xoff=self.x, yoff=self.y)

    def multiply(self, multiple: float):
        return Vector2D(self.x * multiple, self.y * multiple)

    def __mul__(self, other):
        return self.multiply(other)

    def unit(self):
        length = math.sqrt(self.x ** 2 + self.y ** 2)
        if length == 0:
            raise ValueError('x and y cannot be both 0')
        return Vector2D(self.x / length, self.y / length)

    def reverse(self):
        return Vector2D(-self.x, -self.y)
