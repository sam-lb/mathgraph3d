from global_imports import *;
from Color import preset_styles, ColorStyle, Styles;
from csv import reader;
from collections import defaultdict;
from Shapes import SubPolygon;
from Errors import GrapherError;


def load_csv(file_name, desperation=False):
    """ safely loads in a csv file; returns a csv.reader object """
    if not file_name.endswith(".csv"):
        if "." in file_name:
            raise GrapherError("Only .csv files can be loaded");
        else:
            return load_csv("{}.csv".format(file_name), desperation=True);
    try:
        return reader(open(file_name));
    except IOError:
        addendum = " The grapher attempted to open this file because a file type was not specified." if desperation else "";
        raise GrapherError("The file {} cannot be found!{}".format(file_name, addendum));


class _StatPlot():

    """ Base class for plots created from statistical data in a csv file """

    def __init__(self, plot, file, color_style=preset_styles["default"]):
        self.plot = plot;
        self.file_name = file;
        self.file = load_csv(file);
        self.color_style = color_style;
        self.get_data();
        self.plot.add_function(self);

    def get_data(self):
        """ read the data from the csv file """
        pass;

    def create_point(self, point):
        """ create a point from a list """
        return tuple(map(lambda p: round(float(p), 2), point));

    def draw(self):
        """ add the shapes to the plot's drawing queue """
        pass;


class StatPlot2D(_StatPlot):

    """ class for 2D plots created from statistical data """

    def __init__(self, plot, file, color_style=preset_styles["default"], point_color=(0, 0, 0), line_weight=1, points_on=True, lines_on=True):
        _StatPlot.__init__(self, plot, file, color_style);
        self.line_weight = line_weight;
        self.point_color = point_color;
        self.points_on, self.lines_on = points_on, lines_on;

    def get_data(self):
        """ read the data in from the csv file """
        data = [];
        for point in self.file:
            p = self.create_point(point);
            data.append((p[0], p[1], 0.0));
        self.data = sorted(data, key=lambda value: value[0]);

    def draw(self):
        """ add the shapes to the plot's drawing queue """
        last_point = None;
        for point in self.data:
            new_point = self.plot.screen_point(*point);
            if self.points_on:
                self.plot.add_shape(point, pygame.draw.circle, self.plot.surface, self.point_color, (int(new_point[0]), int(new_point[1])), 3);
            if (last_point is not None) and self.lines_on:
                self.plot.add_shape(point, pygame.draw.line, self.plot.surface, self.color_style.next_color(), last_point, new_point, self.line_weight);
            last_point = new_point;


class StatPlot3D(_StatPlot):

    """ class for 3D plots created from statistical data """

    def __init__(self, plot, file, color_style=preset_styles["default"], surf_on=True, mesh_on=True, mesh_color=(0, 0, 0), mesh_weight=1):
        _StatPlot.__init__(self, plot, file, color_style);
        self.surf_on, self.mesh_on = surf_on, mesh_on;
        self.mesh_color, self.mesh_weight = mesh_color, mesh_weight;
        self.anchorize();

    def get_data(self):
        """ read the data from the csv file """
        data = defaultdict(lambda: []);
        self.min_value, self.max_value = None, None;
        for point in self.file:
            p = self.create_point(point);
            if self.min_value is None:
                self.min_value = p[2];
                self.max_value = p[2];
            else:
                if p[2] < self.min_value:
                    self.min_value = p[2];
                elif p[2] > self.max_value:
                    self.max_value = p[2];
            data[p[0]].append(p);
        self.data = sorted((sorted((x_value), key=lambda value: value[1]) for x_value in data.values()), key=lambda l: l[0]);

    def anchorize(self):
        """ create the point mesh """
        polys = [];
        for i, row in enumerate(self.data[1:], start=1):
            for j, point in enumerate(row[1:], start=1):
                try:
                    points = (self.data[i][j-1], point, self.data[i-1][j], self.data[i-1][j-1]);
                    M = quad_midpoint(*points);
                    color = self.color_style.next_color(i=i, j=j, point=point, min_=self.min_value, max_=self.max_value, value=point[2]);
                    polys.append(SubPolygon(color, points, M, i, j));
                except IndexError as e:
                    pass;
        self.anchors = polys;

    def draw(self):
        """ add the shapes to the plot's drawing queue """
        for poly in self.anchors:
            points = tuple(map(lambda p: self.plot.screen_point(*p), poly.points));
            if self.surf_on: self.plot.add_shape(poly.M, pygame.draw.polygon, self.plot.surface, poly.color, points);
            if self.mesh_on: self.plot.add_shape(poly.M, pygame.draw.polygon, self.plot.surface, self.mesh_color, points, self.mesh_weight);
            
