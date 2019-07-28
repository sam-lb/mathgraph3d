from global_imports import *;
from Color import preset_styles;
from Shapes import SubPolygon;

class Plottable():

    """ Base class for any function plot that is drawn to the screen (not stat plot) """

    def __init__(self, plot, function, color_style=preset_styles["default"]):
        self.plot = plot;
        self.function = function;
        self.color_style = color_style;
        self.plot.add_function(self);
        self.min_value, self.max_value = None, None;
        self.anchors = [];

    def anchorize3D(self, h_anchors, v_anchors, h_start, h_stop, v_start, v_stop):
        """ precalculate the set of 3D polygons """
        self.color_style.reset();
        anchors, needs_detection = self.get_point_mesh(h_anchors, v_anchors, h_start, h_stop, v_start, v_stop);
        self.anchors = self.get_polygons(anchors, needs_detection);

    def get_point_mesh(self, h_anchors, v_anchors, h_start, h_stop, v_start, v_stop):
        """ create the point mesh """
        pn, pm = (h_stop - h_start) / h_anchors, (v_stop - v_start) / v_anchors;
        anchors = [];
        needs_detection = False;
        
        for x in drange(v_start, v_stop + pm, pm):
            row = [];
            for y in drange(h_start, h_stop + pn, pn):
                try:
                    value = self.function(x, y);
                    if isinstance(value, complex):
                        continue;
                    elif isinstance(value, float) or isinstance(value, int):
                        if self.min_value is None:
                            self.min_value = value;
                            self.max_value = value;
                        elif value > self.max_value:
                            self.max_value = value;
                        elif value < self.min_value:
                            self.min_value = value;
                        point = (x, y, value);
                    elif isinstance(value, tuple):
                        z = value[2];
                        if self.min_value is None:
                            self.min_value = z;
                            self.max_value = z;
                        elif z > self.max_value:
                            self.max_value = z;
                        elif z < self.min_value:
                            self.min_value = z;
                        point = value;
                    row.append(point);
                except ZeroDivisionError as e:
                    needs_detection = True;
                except Exception as e:
                    needs_detection = True;
            if row: anchors.append(row);
        return anchors, needs_detection;

    def get_polygons(self, anchors, needs_detection):
        """ create polygons from the point mesh """
        last_AB, last_AC, polys = None, None, [];
        for i, row in enumerate(anchors[1:], start=1):
            for j, pt in enumerate(row[1:], start=1):
                try:
                    A = anchors[i][j-1];
                    B = pt;
                    C = anchors[i-1][j];
                    D = anchors[i-1][j-1];
                    M = quad_midpoint(A, B, C, D);

                    if self.max_value > self.plot.z_stop or self.min_value < self.plot.z_start:
                        points = self.superclip((A, B, C, D));
                        if points is None:
                            continue;
                        elif points[1]:
                            points = points[0];
                        else:
                            points = self.subclip(points[0]);
                        if points is None: continue;
                        points = sort_clockwise(*points);
                    else:
                        points = [A, B, C, D];
                                

                    if needs_detection:
                        AB, AC = distance3D(A, B), distance3D(A, C);
                        if last_AB is None:
                            last_AB, last_AC = AB, AC;
                        else:
                            if abs(last_AB-AB) > 1.7 or abs(last_AC-AC) > 1.7:
                                continue;

                    color = self.color_style.next_color(i=i, j=j, point=M, min_=self.min_value, max_=self.max_value, value=M[2]);
                    polys.append(SubPolygon(color, points, M, i, j));
                except IndexError as e:
                    pass;
        return polys;

    def point_constant_intersection(self, in_point, out_point, constant=None):
        if constant is None: constant = self.plot.z_stop;

        try:
            xm = slope((in_point[0], in_point[2]), (out_point[0], out_point[2]));
            xb = in_point[2] - xm * in_point[0];
        except ZeroDivisionError:
            x = in_point[0];
        else:
            x = (constant - xb) / xm;

        try:
            ym = slope((in_point[1], in_point[2]), (out_point[1], out_point[2]));
            yb = in_point[2] - ym * in_point[1];
        except ZeroDivisionError:
            y = in_point[1];
        else:
            y = (constant - yb) / ym;

        return x, y, constant;

    def superclip(self, points):
        """ clip the top off a graph that goes over the max z value """
        points = sorted(points, key=lambda p: p[2]);
        A, B, C, D = (point[2] > self.plot.z_stop for point in points);
        
        if A:
            return None;
        elif not D:
            return points, False;
        else:
            if B:
                return [points[0], self.point_constant_intersection(points[0], points[1]),
                        self.point_constant_intersection(points[0], points[2])], True;
            elif C:
                return [points[0], points[1], self.point_constant_intersection(points[0], points[2]),
                        self.point_constant_intersection(points[1], points[3])], True;
            else:
                return [points[0], points[1], points[2], self.point_constant_intersection(points[1], points[3]),
                        self.point_constant_intersection(points[2], points[3])], True;

    def subclip(self, points):
        """ clip the bottom off a graph that goes under the min z value """
        if points is None or len(points) != 4: return None;
        A, B, C, D = (point[2] < self.plot.z_start for point in points);

        if D:
            return None;
        elif not A:
            return points;
        else:
            if C:
                return [points[3], self.point_constant_intersection(points[3], points[2], self.plot.z_start),
                        self.point_constant_intersection(points[3], points[1], self.plot.z_start)];
            elif B:
                return [points[3], points[2], self.point_constant_intersection(points[3], points[1], self.plot.z_start),
                        self.point_constant_intersection(points[2], points[0], self.plot.z_start)];
            else:
                return [points[3], points[2], points[1], self.point_constant_intersection(points[2], points[0], self.plot.z_start),
                        self.point_constant_intersection(points[1], points[0], self.plot.z_start)];

    def draw3D(self):
        """ add the function to the plot's drawing queue """
        for poly in self.anchors:
            points = tuple(map(lambda p: self.plot.screen_point(*p), poly.points));
            if self.surf_on: self.plot.add_shape(poly.M, pygame.draw.polygon, self.plot.surface, poly.color, points);
            if self.mesh_on: self.plot.add_shape(poly.M, pygame.draw.polygon, self.plot.surface, self.mesh_color, points, self.mesh_weight);
