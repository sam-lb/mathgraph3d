from mathgraph3D.core.global_imports import *;
from mathgraph3D.core.Plottable import Plottable;
from mathgraph3D.core.Color import Styles, ColorStyle, preset_styles;
from mathgraph3D.core.Shapes import SubPolygon


# A good explanation of marching squares can be found here:
# https://www.mattkeeter.com/projects/contours/



A, B, C, D = (0, 1), (1, 2), (2, 3), (0, 3);

LOOKUP_TABLE_2D = {
    0:  (),
    1:  ((A, D),),
    2:  ((A, B),),
    3:  ((D, B),),
    4:  ((B, C),),
    5:  ((A, B), (C, D)),
    6:  ((A, C),),
    7:  ((C, D),),
    8:  ((C, D),),
    9:  ((A, C),),
    10: ((A, D), (B, C)),
    11: ((B, C),),
    12: ((B, D),),
    13: ((A, B),),
    14: ((A, D),),
    15: (),
};


class Segment:

    """
    A segment shape. Really this belongs in the Shapes module but since it's only
    used here I'll let it slide
    """

    def __init__(self, A, B, color):
        self.A, self.B, self.color = A, B, color;
        self.M = midpoint(A, B);

    def draw(self, plot, weight):
        """ add the shape to the plot's drawing queue """
        plot.add_shape(self.M, pygame.draw.line, plot.surface, self.color, plot.screen_point(*self.A), plot.screen_point(*self.B), weight);



class ImplicitPlot2D(Plottable):

    """
    An implicit plot of the form f(x,y)=0. If you have a relation that is not of
    this form use CAS.Manipulator.move_all_terms_to_left to convert a string
    implicit function to the correct form. Then pass the resulting parse tree's
    evaluate() method as the function parameter.
    """

    def __init__(self, plot, function, color_style=preset_styles["default"], line_weight=1, squares_x=100, squares_y=100):
        Plottable.__init__(self, plot, function, color_style);
        self.color, self.line_weight, = color_style.settings["color"], line_weight;
        self.squares_x, self.squares_y = squares_x, squares_y;
        self.x_step, self.y_step = self.plot.units_x / squares_x, self.plot.units_y / squares_y;
        self.segments = [];
        self.march_squares();

    def calculate_lookup_code(self, cell):
        """ calculate and the lookup code of the given cell """
        return int("".join(map(str, cell)), 2);

    def generate_scalar_field(self):
        """ sample output values from self.function to create a grid of values """
        field = [];
        for x in drange(self.plot.x_start, self.plot.x_stop + self.x_step, self.x_step):
            row = [];
            for y in drange(self.plot.y_start, self.plot.y_stop + self.y_step, self.y_step):
                try:
                    z = self.function(x, y);
                    row.append(int(z > 0));
                    #row.append((x, y, z));
                except Exception:
                    #row.append((x, y, 0));
                    row.append(0);
            field.append(row);
##        print(len(field[0]));
        return field;

    def midpoint(self, A, B):
        """ Return the midpoint of 2D points A and B """
        return (A[0] + B[0]) / 2, (A[1] + B[1]) / 2;

    def interpolate(self, A, B):
        pct_z = abs(min(A[2], B[2]) / (A[2] - B[2]));
        return (min(A[0], B[0]) + pct_z * (A[0] - B[0]),
                min(A[1], B[1]) + pct_z * (A[1] - B[1]), 0);

    def march_squares(self):
        """ run the marching squares algorithm on the function's scalar field """
        half_x, half_y = self.plot.units_x / 2, self.plot.units_y / 2;
        pos_func = lambda i, j: (i * self.x_step - half_x, j * self.y_step - half_y);
        field = self.generate_scalar_field();
        
        for i, row in enumerate(field[1:], start=1):
            for j in range(1, len(row)):
                cell = field[i-1][j-1], field[i][j-1], field[i][j], field[i-1][j];
                code = self.calculate_lookup_code(cell);
##                code = self.calculate_lookup_code((int(z[2] > 0) for z in cell));
                cell = pos_func(i-1, j), pos_func(i, j), pos_func(i, j-1), pos_func(i-1, j-1);
                for line in LOOKUP_TABLE_2D[code]:
##                    try:
##                        m1 = self.interpolate(cell[line[0][0]], cell[line[0][1]]);
##                        m2 = self.interpolate(cell[line[1][0]], cell[line[1][1]]);
##                    except ZeroDivisionError:
##                        continue;
                    try:
                        m1 = self.midpoint(cell[line[0][0]], cell[line[0][1]]);
                        m2 = self.midpoint(cell[line[1][0]], cell[line[1][1]]);
                        self.segments.append(Segment((m1[0], m1[1], 0), (m2[0], m2[1], 0), self.color));
                    except IndexError:
                        print(cell[line[0][0]], cell[line[0][1]], cell[line[1][0]], cell[line[1][1]]);
                        raise;
##                    print(m1, m2);
##                    self.segments.append(Segment((m1[0] - half_x, m1[1] - half_y, 0), (m2[0] - half_x, m2[1] - half_y, 0), self.color));
        del field;
##        print(len(self.segments));
        self.segments = tuple(self.segments);

    def draw(self):
        for segment in self.segments:
            segment.draw(self.plot, self.line_weight);

    @classmethod
    def make_function_string(cls, funcs):
        """ return a callable function from a string specific to the type of Plottable. to be overridden """
        func = funcs[0];
        return lambda x, y: func.evaluate(x=x, y=y);



class ImplicitSurface():

    """ An implicit surface of the form f(x,y,z) = g(x,y,z) """

    def __init__(self, plot, f1, f2, color_style=preset_styles["default"], cubes_per_axis=10, mesh_on=True, surf_on=True,
                 mesh_weight=1, mesh_color=(0, 0, 0)):
        self.plot = plot
        self.color_style = color_style
        self.mesh_on, self.surf_on = mesh_on, surf_on
        self.mesh_weight, self.mesh_color = mesh_weight, mesh_color
        self.plot.add_function(self);
        self.cubes_per_axis = cubes_per_axis
        self.f1, self.f2 = f1, f2
        self.generate_polygons()

    def f(self, x, y, z):
        return self.f1(x,y,z)-self.f2(x,y,z)

    def generate_scalar_field(self, x_step, y_step, z_step):
        self.field = []
        row, col = [], []
        for z in drange(self.plot.z_start, self.plot.z_stop, z_step):
            for y in drange(self.plot.y_start, self.plot.y_stop, y_step):
                for x in drange(self.plot.x_start, self.plot.x_stop, x_step):
                    row.append([(x, y, z), self.f(x, y, z)])
                col.append(row[:])
                row = []
            self.field.append(col[:])
            col = []

    def cube_edges(self, top_front_right, top_front_left, top_back_left, top_back_right,
                   bottom_front_right, bottom_front_left, bottom_back_left, bottom_back_right):
        return [
            [top_front_right, top_front_left],
            [top_front_right, top_back_right],
            [top_front_right, bottom_front_right],
            [top_front_left, top_back_left],
            [top_front_left, bottom_front_left],
            [top_back_right, top_back_left],
            [top_back_right, bottom_back_right],
            [top_back_left, bottom_back_left],
            [bottom_front_right, bottom_front_left],
            [bottom_front_right, bottom_back_right],
            [bottom_front_left, bottom_back_left],
            [bottom_back_left, bottom_back_right]
        ]

    def generate_polygons(self):
        self.generate_scalar_field(self.plot.units_x / self.cubes_per_axis,
                                   self.plot.units_y / self.cubes_per_axis,
                                   self.plot.units_z / self.cubes_per_axis)
        self.polygons = []

        for i in range(1, len(self.field)):
            col = self.field[i]
            last_col = self.field[i-1]
            for j in range(1, len(col)):
                row = col[j]
                for k in range(1, len(row)):
                    points = []
                    edges = self.cube_edges(row[k], row[k-1], col[j-1][k-1], col[j-1][k],
                                            last_col[j][k], last_col[j][k-1], last_col[j-1][k-1], last_col[j-1][k])
                    for edge in edges:
                        if sign(edge[0][1]) != sign(edge[1][1]):
                            points.append(lerp_vector(edge[0][0], edge[1][0], edge[0][1]/(edge[0][1]-edge[1][1])))
                    if len(points) != 0:
                        points = sort_clockwise(*points)
                        color = self.color_style.next_color(i=i, j=j, point=points[0], min_=self.plot.z_start, max_=self.plot.z_stop, value=points[0][2], shape=points)
                        self.polygons.append(SubPolygon(color, points, points[0], i, j))
        self.field = []

    def draw(self):
        for poly in self.polygons:
            points = tuple(map(lambda p: self.plot.screen_point(*p), poly.points))
            if self.surf_on: self.plot.add_shape(poly.M, pygame.draw.polygon, self.plot.surface, poly.color, points)
            if self.mesh_on: self.plot.add_shape(poly.M, pygame.draw.polygon, self.plot.surface, self.mesh_color, points, self.mesh_weight)

    def anchorize3D(self, *args, **kwargs):
        self.generate_polygons()




    
