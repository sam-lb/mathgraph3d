from mathgraph3D.global_imports import Vector, relative_distance, sort_clockwise
from mathgraph3D.Shapes import SubPolygon


class ClippingPlane:

    def __init__(self, a, b, c, x0, y0, z0):
        self.normal = Vector(a, b, c)
        self.normal.normalize()
        self.pos = Vector(x0, y0, z0)
        self.test_value = self.normal.dot(self.pos)

    def point_outside_clipping_region(self, P):
        return self.normal.dot(P) - self.test_value > 0

    def find_boundary_point(self, out_p, in_p):
        out_p = Vector(out_p[0], out_p[1], out_p[2])
        in_p = Vector(in_p[0], in_p[1], in_p[2])
        
        direction = out_p - in_p
        diff = self.pos - out_p
        t = self.normal.dot(diff) / self.normal.dot(direction)

        return (out_p + Vector.scale(direction, t)).to_tuple()

    def sort_by_closest(self, out_point, in_points):
        return sorted(in_points, key=lambda P: relative_distance(out_point, P))

    def clip_polygon(self, polygon):
        out_points, in_points, result = [], [], []
        for point in polygon.points:
            if self.point_outside_clipping_region(point):
                out_points.append(point)
            else:
                in_points.append(point)

        if ((len(in_points) >= 2) or ((len(in_points) == 1) and (len(out_points) > 1))):
            for out_p in out_points:
                for in_p in in_points:
                    result.append(self.find_boundary_point(out_p, in_p))
            polygon = SubPolygon(polygon.color, sort_clockwise(*(result + in_points)), in_points[0], polygon.i, polygon.j)
            return polygon
        return None
