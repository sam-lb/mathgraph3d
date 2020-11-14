from mathgraph3D.core.global_imports import *;
from mathgraph3D.core.Color import preset_styles;
from mathgraph3D.core.functions.Plottable import Plottable;


class RecurrenceRelation(Plottable):

    """ Plot of a 2D recurrence relation """

    def __init__(self, plot, function, seed_value, color_style=preset_styles["default"], unit_scale=1, line_weight=1):
        Plottable.__init__(self, plot, function, color_style);
        self.seed_value = seed_value;
        self.step = unit_scale;
        self.color = self.color_style.settings["color"];
        self.line_weight = line_weight;

    def draw(self):
        """ add the plot's shapes to the drawing queue """
        last_value, last_point = None, None;
        for x in drange(0, self.plot.x_stop + self.step, self.step):
            if last_value is None:
                last_value = self.seed_value;
                last_point = self.plot.screen_point(0, self.seed_value, 0);
                continue;
            else:
                try:
                    point = (x, self.function(last_value), 0);
                    new_point = self.plot.screen_point(*point);
                    if last_point is not None:
                        self.plot.add_shape(point, pygame.draw.line, self.plot.surface, self.color, last_point, new_point, self.line_weight);
                    last_point = new_point;
                    last_value = point[1];
                except:
                    last_point = None;

    @classmethod
    def make_function_string(cls, funcs):
        """ return a callable function from a string specific to the type of Plottable. to be overridden """
        func = funcs[0];
        return lambda n: func.evaluate(n=n);
