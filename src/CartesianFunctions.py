from global_imports import *;
from Plottable import Plottable;
from Color import preset_styles, ColorStyle, Styles;


class CartesianFunction(Plottable):

    """ A function with Cartesian coordinates (directed distance x, y, z) """

    def __init__(self, plot, function, color_style=preset_styles["default"], x_start=-4, x_stop=4, y_start=-4, y_stop=4):
        Plottable.__init__(self, plot, function, color_style);

        self.x_start, self.x_stop = x_start, x_stop;
        self.y_start, self.y_stop = y_start, y_stop;


class Function2D(CartesianFunction):

    """ A 2D function of a single variable x """

    def __init__(self, plot, function, x_start=-4, x_stop=4, y_start=-4, y_stop=4, points_per_unit=100,
                 line_color_style=ColorStyle(Styles.SOLID, color=(0, 0, 0)), line_weight=1, detect_poles=True):
        CartesianFunction.__init__(self, plot, function, line_color_style, x_start, x_stop, y_start, y_stop);

        self.step = (self.x_stop - self.x_start) / points_per_unit;
        self.line_weight = line_weight;
        self.detect_poles = detect_poles;

    def draw(self):
        """ add the function to the plot's drawing queue """
        prev_point = None;
        for x in drange(self.x_start, self.x_stop + self.step, self.step):
            try:
                y = complex(self.function(x));
                if not self.y_start <= y.real <= self.y_stop:
                    prev_point = None;
                    continue;
                point = x, y.real, y.imag;
            except ZeroDivisionError:
                pass;
            except Exception as e:
                print(e);
            else:
                new_point = self.plot.screen_point(*point);
                if prev_point is not None and ((self.detect_poles and abs(new_point[1]-prev_point[1]) < 40) or not self.detect_poles):
                    self.plot.connect(point, prev_point, new_point, color=self.color_style.next_color(), weight=self.line_weight);
                prev_point = new_point;


class Function3D(CartesianFunction):

    """ A 3D function of two variables x and y """

    def __init__(self, plot, function, color_style=preset_styles["default"], x_start=-4, x_stop=4,
                 y_start=-4, y_stop=4, x_anchors=32, y_anchors=32, mesh_on=True, surf_on=True,
                 mesh_weight=1, mesh_color=(0, 0, 0), prism_plot=False, area_surface=lambda x, y: True):
        
        CartesianFunction.__init__(self, plot, function, color_style, x_start, x_stop, y_start, y_stop);

        self.mesh_on, self.surf_on = mesh_on, surf_on;
        self.mesh_weight, self.mesh_color = mesh_weight, mesh_color;
        self.anchorize3D(x_anchors, y_anchors, x_start, x_stop, y_start, y_stop);
        self.prism_plot = prism_plot;
        self.area_surface = area_surface;

    def plot_prisms(self):
        """ Add the prisms of a volume approximation to the plot's drawing queue """
        volume = 0;
        for poly in self.anchors:
            try:
                if self.area_surface(poly.points[0][0], poly.points[0][1]):
                    volume += self.make_prism(poly.color, *poly.points);
            except ValueError:
                pass;
        text("Volume: {}".format(round(volume, 2)), 10, 140, self.plot.surface, (0, 0, 0));

    def make_prism(self, color, A, B, C, D):
        """ add a single prism to the drawing queue """
        A2 = (A[0], A[1], 0); B2 = (B[0], B[1], 0);
        C2 = (C[0], C[1], 0); D2 = (D[0], D[1], 0);
        z = quad_midpoint(A, B, C, D)[2];
        A = (A[0], A[1], z); B = (B[0], B[1], z);
        C = (C[0], C[1], z); D = (D[0], D[1], z);
        volume = z * abs(A[0] - C[0]) * abs(A[1] - B[1]);
        
        self.make_face(color, A, B, B2, A2);
        self.make_face(color, B, C, C2, B2);
        self.make_face(color, C, D, D2, C2);
        self.make_face(color, D, A, A2, D2);
        self.make_face(color, A, B, C, D);
        self.make_face(color, A2, B2, C2, D2);
        return volume;

    def make_face(self, color, A, B, C, D, mesh=False):
        """ make one of the prism's faces """
        M = quad_midpoint(A, B, C, D);
        A, B, C, D = map(lambda p: self.plot.screen_point(*p), (A,B,C,D));
        self.plot.add_shape(M, pygame.draw.polygon, self.plot.surface, color, (A, B, C, D));
        if mesh: self.plot.connect(M, A, B, C, D, A, color=self.mesh_color, weight=self.mesh_weight);

    def draw(self):
        """ add the function to the plot's drawing queue """
        if self.prism_plot: self.plot_prisms();
        self.draw3D()
