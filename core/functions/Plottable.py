from mathgraph3D.core.global_imports import *;
from mathgraph3D.core.Color import preset_styles, random_color;
from mathgraph3D.core.plot.Shapes import SubPolygon;
import warnings;
warnings.filterwarnings("error");

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
        self.anchors = self.get_polygons(anchors, True);

    def get_point_mesh(self, h_anchors, v_anchors, h_start, h_stop, v_start, v_stop):
        """ create the point mesh """
        pn, pm = (h_stop - h_start) / h_anchors, (v_stop - v_start) / v_anchors;
        anchors = [];
        needs_detection = False;
        last_defined_point = None;
        
        for x in drange(v_start, v_stop + pm, pm):
            row = [];
            for y in drange(h_start, h_stop + pn, pn):
                try:

##                    x0, y0 = x, y;
##                    define = True;
##                    if last_defined_point is not None: dx, dy = generate_approach_amount(last_defined_point, (x0, y0), 12);
##                    for i in range(10):
##                        try:
##                            value = self.function(x0, y0)
##                        except ValueError:
##                            if last_defined_point is not None:
##                                x0, y0 = approach((x0, y0), dx, dy);
##                                p = self.plot.screen_point(x0, y0, 0);
##                                pygame.draw.rect(self.plot.surface, random_color(), (p[0], p[1], 2, 2));
##                                pygame.display.flip();
##                                pygame.time.delay(50);
##                            define = False;
##                            last_defined_point = None;
##                        else:
##                            p = self.plot.screen_point(x0, y0, 0);
##                            pygame.draw.rect(self.plot.surface, (255, 0, 0), (p[0], p[1], 2, 2));
##                            pygame.display.flip();
##                            pygame.time.delay(10);
##                            break;
##                    else:
##                        continue;
##                    if define:
##                        last_defined_point = (x0, y0);
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
                    else:
                        print(type(value));
                    row.append(point);
                except ValueError as e:
                    pass;
                except ZeroDivisionError as e:
                    needs_detection = True;
                except NameError as e:
                    raise e;
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
                    points = [];
                    for a, b in ((i, j-1), (i, j), (i-1, j), (i-1, j-1)):
                        try:
                                points.append(anchors[a][b]);
                        except IndexError:
                            continue;

                    if len(points) <= 2: continue;
                    M = polygon_midpoint(points);
                    if self.max_value > self.plot.z_stop or self.min_value < self.plot.z_start:
                        points = self.super_sub_clip(points, self.plot.z_stop, self.plot.z_start);
                        if len(points) == 0: continue;
                    color = self.color_style.next_color(i=i, j=j, point=M, min_=self.min_value, max_=self.max_value, value=M[2], shape=points);
                    polys.append(SubPolygon(color, points, M, i, j));
                except RuntimeWarning:
                    pass;
        polys = tuple(self.plot.clip(polys));
        return polys;
                    
##                    A = anchors[i][j-1];
##                    B = pt;
##                    C = anchors[i-1][j];
##                    D = anchors[i-1][j-1];
##                    
##                    M = quad_midpoint(A, B, C, D);
##
##                    if self.max_value > self.plot.z_stop or self.min_value < self.plot.z_start:
##                        points = self.super_sub_clip([A, B, C, D], self.plot.z_stop, self.plot.z_start);
##                        if len(points) == 0: continue;
##                    else:
##                        points = [A, B, C, D];
##                                
##
##                    if needs_detection:
##                        AB, AC = distance3D(A, B), distance3D(A, C);
##                        if last_AB is None:
##                            last_AB, last_AC = AB, AC;
##                        else:
##                            if abs(last_AB-AB) > 1.7 or abs(last_AC-AC) > 1.7:
##                                continue;
##
##                    color = self.color_style.next_color(i=i, j=j, point=M, min_=self.min_value, max_=self.max_value, value=M[2]);
##                    polys.append(SubPolygon(color, points, M, i, j));
##                    #pygame.display.update(pygame.draw.polygon(self.plot.surface, (255, 255, 255), list(map(lambda p: self.plot.screen_point(*p), points)), 1));
##                    #pygame.time.delay(50);
##                except IndexError as e:
##                    pass;
##                
##        polys = tuple(polys);
##        return polys;

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

    def sort_by_closest(self, point, points):
        return sorted(points, key=lambda p: self.plot.proportion_distance3D_2(p, point));

    def line_constant_intersection(self, in_point, out_point, constant=None):
        return self.point_constant_intersection(in_point, out_point, constant);
    
    def super_sub_clip(self, points, z_top, z_bottom):
        violation_points_a, violation_points_b = [], [];
        valid_points, vertices = [], [];

        for point in points:
            if point[2] > z_top:
                violation_points_a.append(point);
            elif point[2] < z_bottom:
                violation_points_b.append(point);
            else:
                valid_points.append(point);

        if len(valid_points) == 0:
            return [];
        elif len(violation_points_a) + len(violation_points_b) == 0:
            return sort_clockwise(*valid_points);

        for point in violation_points_a:
            closest_points = self.sort_by_closest(point, valid_points);
            vertices.append(self.line_constant_intersection(closest_points[0], point, z_top));
            if len(violation_points_a) == 1 and len(closest_points) > 1: vertices.append(self.line_constant_intersection(closest_points[1], point, z_top));

        for point in violation_points_b:
            closest_points = self.sort_by_closest(point, valid_points);
            vertices.append(self.line_constant_intersection(closest_points[0], point, z_bottom));
            if len(violation_points_b) == 1 and len(closest_points) > 1: vertices.append(self.line_constant_intersection(closest_points[1], point, z_bottom));

        return sort_clockwise(*(vertices + valid_points));

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

    @classmethod
    def make_function_string(cls, funcs):
        """ return a callable function from a string specific to the type of Plottable. to be overridden """
        pass;
