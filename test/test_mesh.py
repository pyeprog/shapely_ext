from unittest import TestCase

from shapely.geometry import box, Polygon, Point

from shapely_ext.mesh import TriMesher


class Test(TestCase):
    def setUp(self) -> None:
        self.mesher_11 = TriMesher(interpolate_distance=11)
        self.mesher_5 = TriMesher(interpolate_distance=5)

    def test_generate_tri_mesh_of_polygon(self):
        rect = box(0, 0, 10, 10)
        faces = self.mesher_11.mesh(rect)  # non interpolation
        self.assertTrue(all(isinstance(face, Polygon) for face in faces))
        self.assertTrue(2, len(faces))

        faces = self.mesher_5.mesh(rect)
        self.assertTrue(all(isinstance(face, Polygon) for face in faces))
        self.assertTrue(8, len(faces))

    def test_generate_tri_mesh_of_non_polygon(self):
        point = Point(0, 0)
        with self.assertRaises(NotImplementedError):
            self.mesher_11.mesh(point)
