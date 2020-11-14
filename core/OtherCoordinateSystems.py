from mathgraph3D.core.global_imports import *;
from mathgraph3D.core.Color import preset_styles, Styles, ColorStyle;
from mathgraph3D.core.Plottable import Plottable;
from mathgraph3D.core.ParametricFunctions import ParametricFunctionUV;


class CylindricalFunction(ParametricFunctionUV):

    """
    A function of cylindrical coordinates.
    For an explanation of how the function of z and theta is converted to a parametric function, visit http://sambrunacini.com/algorithms.html
    """

    def __init__(self, plot, function, color_style=preset_styles["default"], theta_start=-pi, theta_stop=pi, z_start=-4,
                 z_stop=4, theta_anchors=32, z_anchors=32, mesh_on=True, surf_on=True, mesh_weight=1, mesh_color=(0, 0, 0)):
        parametric_function = lambda u, v: (function(u, v) * cos(v), function(u, v) * sin(v), u);
        ParametricFunctionUV.__init__(self, plot, parametric_function, color_style, u_start=z_start, u_stop=z_stop, v_start=theta_start, v_stop=theta_stop,
                                      u_anchors=z_anchors, v_anchors=theta_anchors, mesh_on=mesh_on, surf_on=surf_on, mesh_weight=mesh_weight, mesh_color=mesh_color);

    @classmethod
    def make_function_string(cls, funcs):
        """ return a callable function from a string specific to the type of Plottable. to be overridden """
        func = funcs[0];
        return lambda z, t: func.evaluate(z=z, t=t);


class SphericalFunction(ParametricFunctionUV):

    """
    A function of spherical coordinates.
    For an explanation of how the function of theta and phi is converted to a parametric function, see http://sambrunacini.com/algorithms.html
    """

    def __init__(self, plot, function, color_style=preset_styles["default"], theta_start=-pi, theta_stop=pi, phi_start=-pi, phi_stop=pi,
                 theta_anchors=32, phi_anchors=32, mesh_on=True, surf_on=True, mesh_weight=1, mesh_color=(0, 0, 0)):
        parametric_function = lambda u, v: (function(u, v) * sin(u) * cos(v), function(u, v) * sin(u) * sin(v), function(u, v) * cos(u));
        ParametricFunctionUV.__init__(self, plot, parametric_function, color_style, u_start=theta_start, u_stop=theta_stop, v_start=phi_start, v_stop=phi_stop,
                                      u_anchors=theta_anchors, v_anchors=phi_anchors, mesh_on=mesh_on, surf_on=surf_on, mesh_weight=mesh_weight, mesh_color=mesh_color);

    @classmethod
    def make_function_string(cls, funcs):
        """ return a callable function from a string specific to the type of Plottable. to be overridden """
        func = funcs[0];
        return lambda t, p: func.evaluate(t=t, p=p);


class PolarFunction(Plottable):

    """ A function of polar coordinates """

    def __init__(self, plot, function, color_style=preset_styles["default"], theta_start=-pi, theta_stop=pi, step=0.1, line_weight=1):
        Plottable.__init__(self, plot, function, color_style);
        self.color = color_style.settings["color"];
        self.theta_start, self.theta_stop = theta_start, theta_stop;
        self.step = 0.1;
        self.line_weight = line_weight;

    def draw(self):
        """ add the function to the plot's drawing queue """
        last_point = None;
        for theta in drange(self.theta_start, self.theta_stop + self.step, self.step):
            try:
                r = self.function(theta);
                point = r * cos(theta), r * sin(theta), 0;
                new_point = self.plot.screen_point(*point);
                if last_point is not None:
                    self.plot.add_shape(point, pygame.draw.line, self.plot.surface, self.color, last_point, new_point, self.line_weight);
                last_point = new_point;
            except:
                last_point = None;

    @classmethod
    def make_function_string(cls, funcs):
        """ return a callable function from a string specific to the type of Plottable. to be overridden """
        func = funcs[0];
        return lambda t: func.evaluate(t=t);
