from global_imports import *;


class SubPolygon():

    """ Stored in anchor lists. Contains all the necessary data for each polygon """

    def __init__(self, color, A, B, C, D, M, i, j):
        self.color = color;
        self.points = [A, B, C, D];
        self.M = M;
        self.i, self.j = i, j;


class Shape():

    """ A shape that can be sorted and drawn to the screen by the plot """

    def __init__(self, M, shape, *args, **kwargs):
        self.shape, self.M = shape, M;
        self.args, self.kwargs = args, kwargs;

    def draw(self):
        """ draw the shape to the screen """
        return self.shape(*self.args, **self.kwargs);
