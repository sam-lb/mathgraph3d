class Point:

    """ A 3D point """
    
    def __init__(self, plot, point, color):
        plot.add_point(self);
        self.plot = plot;
        self.point = point;
        self.color = color;
