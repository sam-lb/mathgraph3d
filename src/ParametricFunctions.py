from global_imports import *;
from Color import preset_styles;
from Plottable import Plottable;


class ParametricFunctionT(Plottable):

    """ Parametric function of one parameter """

    def __init__(self, plot, function, t_start=-5, t_stop=5, line_color=(0, 0, 0), line_weight=1, t_step=0.1):
        Plottable.__init__(self, plot, function);

        self.t_start, self.t_stop, self.t_step = t_start, t_stop, t_step;
        self.line_color, self.line_weight = line_color, line_weight;

    def draw(self):
        """ place the function into the plot's drawing queue """
        prev_point = None;
        for t in drange(self.t_start, self.t_stop, self.t_step):
            try:
                point = self.function(t);
                new_point = self.plot.screen_point(*point);
            except Exception as e:
                prev_point = None;
            else:
                if prev_point is not None:
                    self.plot.connect(point, prev_point, new_point, color=self.line_color, weight=self.line_weight);
                prev_point = new_point;


class ParametricFunctionUV(Plottable):

    """ Parametric function of two parameters """

    def __init__(self, plot, function, color_style=preset_styles["default"], u_start=-1, u_stop=1, v_start=-1, v_stop=1,
                 u_anchors=32, v_anchors=32, mesh_on=True, surf_on=True, mesh_weight=1, mesh_color=(0, 0, 0)):
        Plottable.__init__(self, plot, function, color_style);


        self.u_start, self.u_stop = u_start, u_stop;
        self.v_start, self.v_stop = v_start, v_stop;
        self.mesh_on, self.surf_on = mesh_on, surf_on;
        self.mesh_weight, self.mesh_color = mesh_weight, mesh_color;
        self.anchorize3D(u_anchors, v_anchors, u_start, u_stop, v_start, v_stop);

    def draw(self):
        """ Place the funciton into the plot's drawing queue """
        self.draw3D();


class RevolutionSurface(ParametricFunctionUV):

    """ Plot a surface of revolution (surface obtained by rotating a 2D function about an axis """

    def __init__(self, plot, function, color_style=preset_styles["default"], x_start=-4, x_stop=4, x_anchors=32,
                 y_anchors=32, mesh_on=True, surf_on=False, mesh_weight=1, mesh_color=(0, 0, 0)):
        func = lambda u, v: (u, function(u) * cos(v), function(u) * sin(v));
        ParametricFunctionUV.__init__(self, plot, func, color_style, 0, 2 * pi, x_start, x_stop, x_anchors, y_anchors, mesh_on, surf_on, mesh_weight, mesh_color);
