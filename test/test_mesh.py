from unittest import TestCase

from shapely.geometry import box, Polygon, Point

from shapely_ext.mesh import generate_tri_mesh


class Test(TestCase):
    def test_generate_tri_mesh_of_polygon(self):
        rect = box(0, 0, 10, 10)
        faces = generate_tri_mesh(rect, interpolate_distance=11)  # non interpolation
        self.assertTrue(all(isinstance(face, Polygon) for face in faces))
        self.assertTrue(2, len(faces))

        faces = generate_tri_mesh(rect, interpolate_distance=5)
        self.assertTrue(all(isinstance(face, Polygon) for face in faces))
        self.assertTrue(8, len(faces))

    def test_generate_tri_mesh_of_non_polygon(self):
        point = Point(0, 0)
        with self.assertRaises(NotImplementedError):
            generate_tri_mesh(point, interpolate_distance=11)
