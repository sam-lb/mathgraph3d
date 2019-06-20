from global_imports import *;
from Shapes import Shape;


class Plot():

    """ The environment to which all graphs are drawn and handled """

    def __init__(self, surface, x_start=-4, x_stop=4, y_start=-4, y_stop=4, z_start=-4, z_stop=4, background=(255, 255, 255), axis_length=200,
                 axes_on=True, angles_on=True, labels_on=True, cube_on=False, tracker_on=False, alpha=0.5, beta=0.8):
        self.surface = surface;
        self.s_width, self.s_height = self.surface.get_width()//2, self.surface.get_height()//2;
        self.axis_length = axis_length;
        self.background = background;
        self.axes_on, self.angles_on = axes_on, angles_on;
        self.labels_on, self.cube_on = labels_on, cube_on;
        self.tracker_on = tracker_on;
        self.set_bounds(x_start, x_stop, y_start, y_stop, z_start, z_stop);
        self.functions, self.shapes = [], [];
        self.alpha, self.beta = alpha, beta;
        self.get_unit_vectors();
        self.get_sortbox();
        self.updates = 0;
        self.needs_update = True;

    def set_bounds(self, x_start, x_stop, y_start, y_stop, z_start, z_stop):
        """ set the bounds of the Plot and calculate the pixel scales """
        scaler = lambda u: 2 * self.axis_length / u;
        self.x_start, self.x_stop = x_start, x_stop;
        self.y_start, self.y_stop = y_start, y_stop;
        self.z_start, self.z_stop = z_start, z_stop;
        self.units_x, self.units_y, self.units_z = x_stop - x_start, y_stop - y_start, z_stop - z_start;
        self.x_scale, self.y_scale, self.z_scale = map(scaler, (self.units_x, self.units_y, self.units_z));
        self.needs_update = True;

    def add_function(self, function):
        """ Add a function to be plotted """
        self.functions.append(function);

    def scale(self, x, y, z):
        """ Scale a cartesian 3D point by the pixel scales """
        return x * self.x_scale, y * self.y_scale, z * self.z_scale;

    def apply(self, x, y):
        """ cartesian coordinates to pygame screen coordinates """
        return x + self.s_width, self.s_height - y;

    def get_point_coordinates(self, x, y, z):
        """ multiply the UNSCALED 3D coordinates by the projected unit vectors """
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
        """ project the 3D unit vectors to the 2D plane. for an explanation visit http://sambrunacini.com/algorithms.html#grapher """
        self.x = Vector(cos(self.alpha), sin(self.alpha) * sin(self.beta));
        self.y = Vector(-sin(self.alpha), cos(self.alpha) * sin(self.beta));
        self.z = Vector(0, cos(self.beta));

    def get_sortbox(self):
        """ gets the corner closest to the viewer to sort the polygons with """
        if self.beta < 0: z = self.z_start;
        else: z = self.z_stop;

        if 0 <= self.alpha < math.pi: x = self.x_start;
        else: x = self.x_stop;

        if math.pi / 2 <= self.alpha < 1.5 * math.pi: y = self.y_stop;
        else: y = self.y_start;

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

    def __dcube(self, a, b, c, d, e, f, g, h, filled=False):
        """ draw a cube with verticies a, b, ..., g, h """
        A, B, C, D, E, F, G, H = map(lambda p: self.screen_point(*p), (a, b, c, d, e, f, g, h));
        color = (0, 0, 0); weight = 1;
        
        self.connect(quad_midpoint(a, b, c, d), A, B, C, D, A);
        self.connect(quad_midpoint(e, f, g, h), E, F, G, H, E);
        self.add_shape(midpoint(a, e), pygame.draw.line, self.surface, color, A, E, weight);
        self.add_shape(midpoint(b, f), pygame.draw.line, self.surface, color, B, F, weight);
        self.add_shape(midpoint(c, g), pygame.draw.line, self.surface, color, C, G, weight);
        self.add_shape(midpoint(d, h), pygame.draw.line, self.surface, color, D, H, weight);

        if filled:
            self.add_shape(quad_midpoint(a, b, c, d), pygame.draw.polygon, self.surface, (255, 0, 0), (A, B, C, D));
            self.add_shape(quad_midpoint(e, f, g, h), pygame.draw.polygon, self.surface, (0, 255, 0), (E, F, G, H));
            self.add_shape(quad_midpoint(a, b, f, e), pygame.draw.polygon, self.surface, (0, 0, 255), (A, B, F, E));
            self.add_shape(quad_midpoint(c, g, h, d), pygame.draw.polygon, self.surface, (255, 255, 0), (C, G, H, D));
            self.add_shape(quad_midpoint(b, f, g, c), pygame.draw.polygon, self.surface, (0, 255, 255), (B, F, G, C));
            self.add_shape(quad_midpoint(a, e, h, d), pygame.draw.polygon, self.surface, (255, 0, 255), (A, E, H, D));

    def cube(self, back_bottom_left, side, filled=True):
        """ draw a cube """
        e = back_bottom_left;
        f = (e[0] + side, e[1], e[2]);
        g = (e[0] + side, e[1] + side, e[2]);
        h = (e[0], e[1] + side, e[2]);
        
        a = (e[0], e[1], e[2] + side);
        b = (e[0] + side, e[1], e[2] + side);
        c = (e[0] + side, e[1] + side, e[2] + side);
        d = (e[0], e[1] + side, e[2] + side);
        self.__dcube(a, b, c, d, e, f, g, h, filled);

    def draw_axes(self):
        """ draw the 3D axes """
        p = 0.1;

        for x in drange(self.x_start, self.x_stop, p):
            self.connect((x, 0, 0), self.screen_point(x, 0, 0), self.screen_point(x+p, 0, 0), color=(255, 0, 0), weight=3);
        for y in drange(self.y_start, self.y_stop, p):
            self.connect((0, y, 0), self.screen_point(0, y, 0), self.screen_point(0, y+p, 0), color=(0, 255, 0), weight=3);
        for z in drange(self.z_start, self.z_stop, p):
            self.connect((0, 0, z), self.screen_point(0, 0, z), self.screen_point(0, 0, z+p), color=(0, 0, 255), weight=3);

        if self.labels_on:
            text("x", *self.screen_point(self.x_stop, 0, 0), self.surface, color=(255, 0, 0));
            text("y", *self.screen_point(0, self.y_stop, 0), self.surface, color=(0, 255, 0));
            text("z", *self.screen_point(0, 0, self.z_stop), self.surface, color=(0, 0, 255));

    def draw_angles(self):
        """ show the angle values on the screen """
        text("alpha: {}".format(self.alpha), 10, 10,self.surface,color=(0,0,0));
        text("beta: {}".format(self.beta), 10, 50,self.surface,color=(0,0,0));

    def add_shape(self, M, shape, *args, **kwargs):
        """ add a shape to the drawing queue """
        self.shapes.append(Shape(M, shape, *args, **kwargs));

    def draw_shapes(self):
        """ draw the shapes in the drawing queue """
        self.shapes.sort(key=lambda s: distance3D(s.M, self.sortbox), reverse=True);
        
        for shape in self.shapes:
            try:
                shape.draw();
            except TypeError as e:
                pass;
            except IndexError:
                pass;

    def zoom(self, f):
        """ zoom in or out by an amount f """
        self.axis_length = max(0, self.axis_length+f);
        self.needs_update = True;
        self.set_bounds(self.x_start, self.x_stop, self.y_start, self.y_stop, self.z_start, self.z_stop);

    def update(self):
        """ update all the graphs and everything in the plot """
        if self.needs_update:
            self.surface.fill(self.background);
            self.get_unit_vectors();
            self.get_sortbox();

            if self.axes_on: self.draw_axes();
            if self.angles_on: self.draw_angles();
            for f in self.functions:
                f.draw();
            self.draw_shapes();
            self.shapes = [];

            self.needs_update = False;
            self.updates += 1;
        pygame.display.flip();

