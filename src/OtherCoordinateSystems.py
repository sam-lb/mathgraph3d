from global_imports import *;
from Color import preset_styles;
from ParametricFunctions import ParametricFunctionUV;


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
