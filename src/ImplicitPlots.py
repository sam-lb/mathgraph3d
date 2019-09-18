from global_imports import *;
from Plottable import Plottable;
from Color import Styles, ColorStyle;


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

    def __init__(self, plot, function, color=(255, 0, 0), line_weight=1, squares_x=300, squares_y=300):
        Plottable.__init__(self, plot, function, ColorStyle(Styles.SOLID, color=color));
        self.color, self.line_weight, = color, line_weight;
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
                    #row.append(int(z > 0));
                    row.append((x, y, z));
                except Exception:
                    row.append((x, y, 0));
            field.append(row);
        print(len(field[0]));
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
        #half_x, half_y = self.plot.units_x / 2, self.plot.units_y / 2;
        #pos_func = lambda i, j: (i * self.x_step, j * self.y_step);
        field = self.generate_scalar_field();
        
        for i, row in enumerate(field[1:], start=1):
            for j in range(1, len(row)):
                cell = field[i-1][j-1], field[i][j-1], field[i][j], field[i-1][j];
                #code = self.calculate_lookup_code(cell);
                code = self.calculate_lookup_code((int(z[2] > 0) for z in cell));
                #cell = pos_func(i-1, j), pos_func(i, j), pos_func(i, j-1), pos_func(i-1, j-1);
                for line in LOOKUP_TABLE_2D[code]:
                    try:
                        m1 = self.interpolate(cell[line[0][0]], cell[line[0][1]]);
                        m2 = self.interpolate(cell[line[1][0]], cell[line[1][1]]);
                    except ZeroDivisionError:
                        continue;
##                    m1 = self.midpoint(cell[line[0][0]], cell[line[0][1]]);
##                    m2 = self.midpoint(cell[line[1][0]], cell[line[1][1]]);
                    self.segments.append(Segment(m1, m2, self.color));
                    print(m1, m2);
##                    self.segments.append(Segment((m1[0] - half_x, m1[1] - half_y, 0), (m2[0] - half_x, m2[1] - half_y, 0), self.color));
        del field;
        print(len(self.segments));
        self.segments = tuple(self.segments);

    def draw(self):
        for segment in self.segments:
            segment.draw(self.plot, self.line_weight);
