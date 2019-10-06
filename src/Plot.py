from global_imports import *;
from CAS.Parser import Parser;
from CAS.Errors import UserError;
from Shapes import Shape;
from Color import ColorStyle, Styles, preset_styles;
from CartesianFunctions import Function2D, Function3D;
from ParametricFunctions import ParametricFunctionT, ParametricFunctionUV, RevolutionSurface;
from VectorFunctions import VectorField;
from OtherCoordinateSystems import CylindricalFunction, SphericalFunction;
##import numpy as np;

import time;

parser = Parser(ALLOWED_FUNCTIONS);


class Plot():

    """ The environment to which all graphs are drawn and handled """

    def __init__(self, surface, gui=None, x_start=-4, x_stop=4, y_start=-4, y_stop=4, z_start=-4, z_stop=4, background=(255, 255, 255), axis_length=200,
                 axes_on=True, angles_on=True, labels_on=True, cube_on=False, tracker_on=False, spin=False, line_numbers=False, ticks=False, alpha=0.5, beta=0.8,
                 axis_weight=2, line_number_freq=2, x_axis_color=(255, 0, 0), y_axis_color=(0, 255, 0), z_axis_color=(0, 0, 255)):
        self.surface = surface;
        self.gui = gui;
        self.s_width, self.s_height = self.surface.get_width()//2, self.surface.get_height()//2;
        self.axis_length = axis_length;
        self.background = background;
        self.axes_on, self.angles_on = axes_on, angles_on;
        self.labels_on, self.cube_on = labels_on, cube_on;
        self.tracker_on, self.spin = tracker_on, spin;
        self.line_numbers, self.line_number_freq = line_numbers, line_number_freq;
        self.ticks = ticks;
        self.functions, self.points, self.shapes = [], [], [];
        self.set_bounds(x_start, x_stop, y_start, y_stop, z_start, z_stop);
        self.alpha, self.beta = alpha, beta;
        self.get_unit_vectors();
        self.get_sortbox();
        
        self.updates, self.time = 0, 0;
        self.axis_weight = axis_weight;
        self.x_axis_color, self.y_axis_color, self.z_axis_color = x_axis_color, y_axis_color, z_axis_color;
        self.needs_update = True;

    def set_bounds(self, x_start, x_stop, y_start, y_stop, z_start, z_stop, anch=False):
        """ set the bounds of the Plot and calculate the pixel scales """
        if any(map(lambda o: o == 0, (x_start, x_stop, y_start, y_stop, z_start, z_stop))) and anch:
            return;
        
        scaler = lambda u: 2 * self.axis_length / u;
        self.x_start, self.x_stop = x_start, x_stop;
        self.y_start, self.y_stop = y_start, y_stop;
        self.z_start, self.z_stop = z_start, z_stop;
        self.units_x, self.units_y, self.units_z = x_stop - x_start, y_stop - y_start, z_stop - z_start;
        self.x_scale, self.y_scale, self.z_scale = map(scaler, (self.units_x, self.units_y, self.units_z));

        if anch:
            for function in self.functions:
                if isinstance(function, (Function3D)):
                    function.anchorize3D(function.x_anchors,
                                         function.y_anchors,
                                         self.x_start, self.x_stop,
                                         self.y_start, self.y_stop);
        self.needs_update = True;

    def toggle_axes(self):
        """ toggle the axes """
        self.axes_on = not self.axes_on;
        self.needs_update = True;

    def toggle_angles(self):
        """ toggle the angles text """
        self.angles_on = not self.angles_on;
        self.needs_update = True;

    def toggle_labels(self):
        """ toggle the axis labels """
        self.labels_on = not self.labels_on;
        self.needs_update = True;

    def toggle_cube(self):
        """ toggle the cube """
        self.cube_on = not self.cube_on;
        self.needs_update = True;

    def toggle_spin(self):
        """ toggle the spin """
        self.spin = not self.spin;
        self.needs_update = True;

    def toggle_line_numbers(self):
        """ toggle the line numbers """
        self.line_numbers = not self.line_numbers;
        self.needs_update = True;

    def toggle_ticks(self):
        """ toggle the axes """
        self.ticks = not self.ticks;
        self.needs_update = True;

    def add_function(self, function):
        """ Add a function to be plotted """
        self.functions.append(function);
        self.needs_update = True;

    def compile_function(self, name, function, num_vars):
        """ compile a function from a string and add it to the parser """
        parser.redefine_symbols(*["x", "y", "z"][0:num_vars]);
        tree = parser.parse(function);
        if num_vars == 1:
            parser.define_functions(**{name: lambda x: tree.evaluate(x=x)}); # had to break out some trickery here
        elif num_vars == 2:
            parser.define_functions(**{name: lambda x, y: tree.evaluate(x=x, y=y)});
        else:
            parser.define_functions(**{name: lambda x, y, z: tree.evaluate(x=x, y=y, z=z)});

    def scale(self, x, y, z):
        """ Scale a cartesian 3D point by the pixel scales """
        return x * self.x_scale, y * self.y_scale, z * self.z_scale;

    def apply(self, x, y):
        """ cartesian coordinates to pygame screen coordinates """
        return x + self.s_width, self.s_height - y;

    def get_point_coordinates(self, x, y, z):
        """ multiply the SCALED 3D coordinates by the projected unit vectors """
        return (x * self.x.x + y * self.y.x,
                x * self.x.y + y * self.y.y + z * self.z.y);

    def screen_point(self, x, y, z):
        """ 3D unscaled point -> pygame point """
        return self.apply(*self.get_point_coordinates(*self.scale(x, y, z)));

    def set_alpha(self, alpha):
        """ set the alpha angle """
        # all these setters should be switched to more pythonic @property decorated functions
        self.alpha = round(alpha % 6.3, 2);
        self.needs_update = True;

    def set_beta(self, beta):
        """ set the beta angle """
        self.beta = round(max(-1.57, min(1.57, beta)), 2);
        self.needs_update = True;

    def increment_alpha(self, inc):
        """ increment the alpha angle by an amount. for convenience """
        self.set_alpha(self.alpha + inc);

    def increment_beta(self, inc):
        """ increment beta angle by an amount """
        self.set_beta(self.beta + inc);

    def get_unit_vectors(self):
        """ project the 3D unit vectors to the 2D plane. for an explanation visit http://sambrunacini.com/algorithms.html#projection """
        self.x = Vector(cos(self.alpha), sin(self.alpha) * sin(self.beta));
        self.y = Vector(-sin(self.alpha), cos(self.alpha) * sin(self.beta));
        self.z = Vector(0, cos(self.beta));

    def get_sortbox(self):
        """ gets the corner closest to the viewer to sort the polygons with """
        if 0 <= self.alpha < math.pi: x = self.x_start;
        else: x = self.x_stop;

        if math.pi / 2 <= self.alpha < 1.5 * math.pi: y = self.y_stop;
        else: y = self.y_start;

        if self.beta < 0: z = self.z_start;
        else: z = self.z_stop;

        self.sortbox = (x, y, z);
        if self.tracker_on:
            closest_corner = self.screen_point(x, y, z);
            x_ax = self.screen_point(x, 0, 0);
            y_ax = self.screen_point(0, y, 0);
            z_ax = self.screen_point(0, 0, z);
            bot = self.screen_point(x, y, 0);

            self.connect(self.sortbox, closest_corner, bot);
            self.connect(self.sortbox, closest_corner, self.screen_point(0, y, z));
            self.connect(self.sortbox, closest_corner, self.screen_point(x, 0, z));
            self.connect(self.sortbox, bot, self.screen_point(x, 0, 0));
            self.connect(self.sortbox, bot, self.screen_point(0, y, 0));

            self.add_shape(self.sortbox, pygame.draw.circle, self.surface, (255, 0, 0), tuple(map(int, closest_corner)), 10);

    def connect(self, M, *points, color=(0, 0, 0), weight=1):
        """ connect a set of points with lines """
        for i in range(len(points) - 1):
            self.add_shape(M, pygame.draw.line, self.surface, color, points[i], points[i+1], weight);
        self.add_shape(M, pygame.draw.line, self.surface, color, points[-1], points[0], 1);

    def __dcube(self, a, b, c, d, e, f, g, h):
        """ draw a cube with verticies a, b, ..., g, h """
        A, B, C, D, E, F, G, H = map(lambda p: self.screen_point(*p), (a, b, c, d, e, f, g, h));
        color = (0, 0, 0); weight = 1;

        self.connect(quad_midpoint(a, b, c, d), A, B, C, D, A);
        self.connect(quad_midpoint(e, f, g, h), E, F, G, H, E);
        self.add_shape(midpoint(a, e), pygame.draw.line, self.surface, color, A, E, weight);
        self.add_shape(midpoint(b, f), pygame.draw.line, self.surface, color, B, F, weight);
        self.add_shape(midpoint(c, g), pygame.draw.line, self.surface, color, C, G, weight);
        self.add_shape(midpoint(d, h), pygame.draw.line, self.surface, color, D, H, weight);

    def cube(self, back_bottom_left, side):
        """ draw a cube """
        e = back_bottom_left;
        f = (e[0] + side, e[1], e[2]);
        g = (e[0] + side, e[1] + side, e[2]);
        h = (e[0], e[1] + side, e[2]);

        a = (e[0], e[1], e[2] + side);
        b = (e[0] + side, e[1], e[2] + side);
        c = (e[0] + side, e[1] + side, e[2] + side);
        d = (e[0], e[1] + side, e[2] + side);
        self.__dcube(a, b, c, d, e, f, g, h);

    def point(self, point):
        """ draw a point """
        p = self.screen_point(*point.point);
        self.add_shape(point.point, pygame.draw.circle, self.surface, point.color, (int(p[0]), int(p[1])), int(0.2 * self.x_scale));

    @classmethod
    def tangent_plane(cls, function, x0, y0):
        """ returns the function of the tangent plane to the given function at (x, y) """
        gradient = function_gradient(function)(x0, y0, 0);
        return lambda x, y: function(x0, y0) + gradient[0] * (x - x0) + gradient[1] * (y - y0);

    @classmethod
    def plane_from_3_points(cls, A, B, C):
        """ returns the function of the plane that contains A, B, and C unless they are colinear """
        AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2]);
        AC = (C[0] - A[0], C[1] - A[1], C[2] - A[2]);
        a = AB[1] * AC[2] - AB[2] * AC[1];
        b = -(AB[0] * AC[2] - AB[2] * AC[0]);
        c = AB[0] * AC[1] - AB[1] * AC[0];
        x1, y1, z1 = A;
##        print("{}(x-{}) + {}(y-{}) + {}(z-{})".format(a, x1, b, y1, c, z1)); # print the standard form
        if c == 0: raise ValueError("Points are colinear");
        return lambda x, y: z1 - (1 / c) * (a * (x - x1) + b * (y - y1));

    def arrowhead(self, start_point, end_point, color):
        """ draw an arrowhead (under construction) """
        length = 1 / 4;
        start = self.screen_point(start_point[0], start_point[1]+length, start_point[2]+length);
        stop = self.screen_point(start_point[0], start_point[1]-length, start_point[2]-length);
        self.add_shape(start_point, pygame.draw.line, self.surface, color, start, stop, 1)
        start = self.screen_point(start_point[0], start_point[1]-length, start_point[2]+length);
        stop = self.screen_point(start_point[0], start_point[1]+length, start_point[2]-length);
        self.add_shape(start_point, pygame.draw.line, self.surface, color, start, stop, 1)

    def draw_axes(self):
        """ draw the 3D axes """
        p = 0.1;

        for x in drange(self.x_start, self.x_stop + p, p):
            new_point = self.screen_point(x + p, 0, 0);
            if x and x % self.line_number_freq == 0:
                if self.ticks:
                    self.add_shape((x, 0, 0), pygame.draw.line, self.surface, self.x_axis_color, self.screen_point(x, -0.1, 0), self.screen_point(x, 0.1, 0), self.axis_weight);
                if self.line_numbers:
                    self.add_shape((x, 0, 0), self.surface.blit, create_text_surface(str(x), 10, self.x_axis_color), (new_point[0], new_point[1] + 10));
            self.connect((x, 0, 0), self.screen_point(x, 0, 0), new_point, color=self.x_axis_color, weight=self.axis_weight);
            
        for y in drange(self.y_start, self.y_stop + p, p):
            new_point = self.screen_point(0, y + p, 0);
            if y and y % self.line_number_freq == 0:
                if self.ticks:
                    self.add_shape((x, 0, 0), pygame.draw.line, self.surface, self.y_axis_color, self.screen_point(-0.1, y, 0), self.screen_point(0.1, y, 0), self.axis_weight);
                if self.line_numbers:
                    self.add_shape((0, y, 0), self.surface.blit, create_text_surface(str(y), 10, self.y_axis_color), (new_point[0], new_point[1] + 10));
            self.connect((0, y, 0), self.screen_point(0, y, 0), new_point, color=self.y_axis_color, weight=self.axis_weight);
            
        for z in drange(self.z_start, self.z_stop + p, p):
            new_point = self.screen_point(0, 0, z + p);
            if z and z % self.line_number_freq == 0:
                if self.ticks:
                    self.add_shape((x, 0, 0), pygame.draw.line, self.surface, self.z_axis_color, self.screen_point(0, -0.1, z), self.screen_point(0, 0.1, z), self.axis_weight);
                if self.line_numbers:
                    self.add_shape((0, 0, z), self.surface.blit, create_text_surface(str(z), 10, self.z_axis_color), (new_point[0] + 10, new_point[1]));
            self.connect((0, 0, z), self.screen_point(0, 0, z), new_point, color=self.z_axis_color, weight=self.axis_weight);

        #self.arrowhead((self.x_stop-0.5, 0, 0), (self.x_stop, 0,0), (255, 0, 0));

    def draw_angles(self):
        """ show the angle values on the screen """
        text("alpha: {}".format(self.alpha), 10, 10,self.surface,color=(0,0,0));
        text("beta: {}".format(self.beta), 10, 50,self.surface,color=(0,0,0));

    def add_point(self, point):
        """ add a point to the plot """
        self.points.append(point);
        self.needs_update = True;

    def add_shape(self, M, shape, *args, **kwargs):
        """ add a shape to the drawing queue """
        self.shapes.append(Shape(M, shape, *args, **kwargs));

    def proportion_distance3D(self, point1, point2):
        """ dx^2 + dy^2 + dz^2. eliminates square root calculation, proportions are still correct """
        return (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]);

    def proportion_distance3D_2(self, point1, point2):
        """ proportion_distance3D but without exponentiation """
        x = (point1[0] - point2[0]);
        y = (point1[1] - point2[1]);
        z = (point1[2] - point2[2]);
        return x * x, y * y, z * z;

    def draw_shapes(self):
        """ draw the shapes in the drawing queue """
        #self.shapes.sort(key=lambda s: self.proportion_distance3D_2(s.M, self.sortbox), reverse=True);
        self.shapes.sort(key=lambda s: distance3D(s.M, self.sortbox), reverse=True);

        for shape in self.shapes:
            try:
                shape.draw();
            except TypeError:
                raise;
            except ValueError as e:
                raise;
            except IndexError:
                raise;

    def zoom(self, f):
        """ zoom in or out by an amount f """
        self.axis_length = max(0, self.axis_length+f);
        self.needs_update = True;
        self.set_bounds(self.x_start, self.x_stop, self.y_start, self.y_stop, self.z_start, self.z_stop);

    def get_average_update_time(self):
        """ get the average time the plot has taken to update """
        return self.time / self.updates;

    def update(self):
        """ update all the graphs and everything in the plot """
        if self.needs_update:
            initial_time = time.time()
            self.surface.fill(self.background);
            self.get_unit_vectors();
            self.get_sortbox();

            if self.axes_on: self.draw_axes();
            if self.angles_on: self.draw_angles();
            
            if self.cube_on: self.cube((self.x_start, self.y_start, self.z_start), self.units_x);
            for f in self.functions:
                f.draw();
            for p in self.points:
                self.point(p);

            self.draw_shapes();
            self.shapes = [];

            if self.labels_on and self.axes_on:
                text("x", *self.screen_point(self.x_stop, 0, 0), self.surface, color=(255, 0, 0));
                text("y", *self.screen_point(0, self.y_stop, 0), self.surface, color=(0, 255, 0));
                text("z", *self.screen_point(0, 0, self.z_stop), self.surface, color=(0, 0, 255));

            self.needs_update = False;
            self.updates += 1;
            self.time += time.time() - initial_time;
        pygame.display.flip();
        if self.spin: self.increment_alpha(0.01);
