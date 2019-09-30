from global_imports import *;
from Plottable import Plottable;
from Color import preset_styles;
from Shapes import SubPolygon;
from math import isnan, isinf;
from warnings import filterwarnings;

filterwarnings("error");


class ComplexFunction(Plottable):

    """ A 4D plot of a complex function. 3 spatial dimensions and 1 color dimension """

    def __init__(self, plot, function, real_anchors=32, imag_anchors=32, surf_on=True, mesh_on=True, mesh_weight=1, detection=False, detection_level=0.7, color_style=None):
        Plottable.__init__(self, plot, function, preset_styles["rainbow"]);
        self.real_anchors, self.imag_anchors = real_anchors, imag_anchors;
        self.surf_on, self.mesh_on = surf_on, mesh_on;
        self.mesh_color = (0, 0, 0);
        self.mesh_weight = mesh_weight;
        self.detection, self.detection_level = detection, detection_level;
        self.anchorize3D();

    def anchorize3D(self):
        """ precalculate the set of 3D polygons """
        anchors = self.get_point_mesh();
        self.anchors = self.get_polygons(anchors);

    def get_point_mesh(self):
        """ create the point mesh """
        pn = (self.plot.x_stop - self.plot.x_start) / self.real_anchors;
        pm = (self.plot.y_stop - self.plot.y_start) / self.imag_anchors;
        anchors = [];
        
        for real in drange(self.plot.x_start, self.plot.x_stop + pm, pm):
            row = [];
            for imag in drange(self.plot.y_start, self.plot.y_stop + pn, pn):
                try:
                    result = self.function(complex(real, imag));
                    if isinf(result.real) or isnan(result.real): continue;
                    
                    point = (real, imag, result.real, result.imag);

                    if self.min_value is None:
                        self.min_value = self.max_value = result.imag;
                    else:
                        if result.imag > self.max_value: self.max_value = result.imag;
                        elif result.imag < self.min_value: self.min_value = result.imag;
                    
                    row.append(point);
                except ZeroDivisionError as e:
                    pass;
                except Exception as e:
                    raise;
            if row: anchors.append(row);
        return anchors;

    def get_polygons(self, anchors):
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

                    points = self.super_sub_clip([A, B, C, D], self.plot.z_stop, self.plot.z_start);
                    if len(points) == 0: continue;

                    if self.detection:
                        AB, AC = distance3D(A, B), distance3D(A, C);
                        if last_AB is None:
                            last_AB, last_AC = AB, AC;
                        else:
                            if abs(last_AB-AB) > self.detection_level or abs(last_AC-AC) > self.detection_level:
                                continue;

                    color = self.color_style.next_color(i=i, j=j, point=M, min_=self.min_value, max_=self.max_value, value=A[3]);
                    polys.append(SubPolygon(color, tuple((point[0], point[1], point[2]) for point in points), M, i, j));
                except RuntimeWarning:
                    continue;
                except IndexError as e:
                    pass;
                
        polys = tuple(polys);
        return polys;

    def draw(self):
        """ add the function's shapes to the plot's drawing queue """
        self.draw3D();

    @classmethod
    def make_function_string(cls, funcs):
        """ return a callable function from a string specific to the type of Plottable. to be overridden """
        func = funcs[0];
        return lambda z: func.complex_evaluate(z=z);
