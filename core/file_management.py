import os, pickle;


CURRENT_PATH = os.getcwd();
DATA_PATH = os.path.join(CURRENT_PATH, "..");
USER_WARNING = "WARNING: editing this file may cause saved MathGraph3D plots to be lost!";


class Notebook:

    """ Contains plot data so it can be saved """

    def __init__(self, plottables, stat_plots, name):
        self.plottables, self.stat_plots = [], [];
        for plottable in plottables:
            self.add_plottable(plottable);
        for stat_plot in stat_plots:
            self.add_stat_plot(stat_plot);

    def add_plottable(self, plottable):
        self.plottables.append(
            [plottable.function, plottable.color_style, type(plottable)]
        );

    def add_stat_plot(self, stat_plot):
        self.stat_plots.append(
            [stat_plot.file_name, stat_plot.color_style, type(stat_plot)]
        );
