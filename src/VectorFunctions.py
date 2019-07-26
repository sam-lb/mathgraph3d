from global_imports import *;
from Color import preset_styles;
from Plottable import Plottable;


class VectorField(Plottable):

    """ 3D vector field """

    def __init__(self, plot, function, vecs_per_unit=2, color_style=preset_styles["default"], z_start=-4, z_stop=4):
        Plottable.__init__(self, plot, function, color_style);
        self.z_start, self.z_stop = z_start, z_stop;
        self.vecs_per_unit = vecs_per_unit;
        self.step = 1 / vecs_per_unit;

    def set_z_bounds(self, start, stop):
        """ set the z bounds """
        self.z_start, self.z_stop = start, stop;
        
    def draw_arrow(self, M, A, B, color, width=1):
        """ draw an arrow """
        dy, dx = A[1] - B[1], A[0] - B[0];
        angle = math.atan2(dy, dx);
        dist = hypot(dx, dy);
        vec1, vec2 = Vector.from_polar(dist / 5, angle + math.pi / 4), Vector.from_polar(dist / 5, angle - math.pi / 4);
        self.plot.add_shape(M, pygame.draw.line, self.plot.surface, color, A, B, width);
        self.plot.add_shape(M, pygame.draw.line, self.plot.surface, color, B, (B[0] + vec1.x, B[1] + vec1.y), width);
        self.plot.add_shape(M, pygame.draw.line, self.plot.surface, color, B, (B[0] + vec2.x, B[1] + vec2.y), width);

    def draw(self):
        """ add the vector field to the plot's drawing queue """
        i, j = 0, 0;
        self.color_style.reset();
        for x in drange(self.plot.x_start, self.plot.x_stop+2*self.step, 2*self.step):
            i += 1;
            for y in drange(self.plot.y_start, self.plot.y_stop+2*self.step, 2*self.step):
                j += 1;
                for z in drange(self.plot.z_start, self.plot.z_stop+2*self.step, 2*self.step):
                    try:
                        origin = self.plot.screen_point(x, y, z);
                        head = Vector(*self.function(x, y, z));
                        color = self.color_style.next_color(i=i, j=j, point=(x, y, z), min_=self.plot.z_start, max_=self.plot.z_stop, value=z);
                        
                        proj_head = self.plot.screen_point(x + self.step * head.x / head.magnitude,
                                                           y + self.step * head.y / head.magnitude,
                                                           z + self.step * head.z / head.magnitude);
                    except ZeroDivisionError:
                        continue;
                    except Exception as e:
                        pass;
                    else:
                        self.draw_arrow((x, y, z), origin, proj_head, color, 1);
            j = 0;
