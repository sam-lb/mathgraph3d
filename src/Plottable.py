from global_imports import *;
from Color import preset_styles;
from Shapes import SubPolygon;


class Plottable():

    """ Base class for any plot that is drawn to the screen """

    def __init__(self, plot, function, color_style=preset_styles["default"]):
        self.plot = plot;
        self.function = function;
        self.color_style = color_style;
        self.plot.add_function(self);
        self.min_value, self.max_value = None, None;
        self.anchors = [];

    def anchorize3D(self, h_anchors, v_anchors, h_start, h_stop, v_start, v_stop):
        """ precalculate the mesh of 3d points """
        pn, pm = (h_stop - h_start) / h_anchors, (v_stop - v_start) / v_anchors;
        anchors, polys = [], [];
        for x in drange(v_start, v_stop + pm, pm):
            row = [];
            for y in drange(h_start, h_stop + pn, pn):
                try:
                    value = self.function(x, y);
                    if isinstance(value, complex):
                        continue;
                    elif isinstance(value, float):
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
                except ZeroDivisionError:
                    pass;
                except Exception as e:
                    pass;
            if row: anchors.append(row);
        
        for i, row in enumerate(anchors):
            for j, pt in enumerate(row):
                if i and j:
                    try:
                        A = anchors[i][j-1];
                        B = pt;
                        C = anchors[i-1][j];
                        D = anchors[i-1][j-1];
                        M = quad_midpoint(A, B, C, D);

                        polys.append(SubPolygon(self.color_style.next_color(i=i, j=j, point=pt, min_=self.min_value, max_=self.max_value, value=pt[2]), A, B, C, D, M, i, j));
                    except IndexError as e:
                        pass;
        self.anchors = polys;

    def draw3D(self):
        """ add the function to the plot's drawing queue """
        for poly in self.anchors:
            A, B, C, D = map(lambda p: self.plot.screen_point(*p), poly.points);
            if self.surf_on: self.plot.add_shape(poly.M, pygame.draw.polygon, self.plot.surface, poly.color, (A, B, C, D));
            if self.mesh_on: self.plot.connect(poly.M, A, B, C, D, A, color=self.mesh_color, weight=self.mesh_weight);
            
