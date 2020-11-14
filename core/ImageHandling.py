from mathgraph3D.core.global_imports import *;


class Segment():

    def __init__(self, point1, point2):
        self.point1, self.point2 = point1, point2;
        self.get_slope();
        self.get_b();
        self.start_x, self.stop_x = sorted((point1[0], point2[0]));
        self.start_y, self.stop_y = sorted((point1[1], point1[1]));

    def get_slope(self):
        try:
            self.slope = (self.point1[1] - self.point2[1]) / (self.point1[0] - self.point2[0]);
            self.vertical = False;
        except ZeroDivisionError:
            self.vertical = True;

    def get_b(self):
        if not self.vertical: self.b = self.point1[1] - self.slope * self.point1[0];

    def get_intersection(self, segment):
        if self.vertical or segment.vertical: return self.get_vertical_intersection(segment);
        
        x = (segment.b - self.b) / (self.slope - segment.slope);
        y = self.slope * x + self.b;
        if all((self.start_x <= x < self.stop_x,
                self.start_y <= y < self.stop_y,
                segment.start_x <= x < segment.stop_x,
                segment.start_y <= y < segment.stop_y)):
            return x, y;
        return None;

    def get_vertical_intersection(self, segment):
        if self.vertical and segment.vertical:
            return None;
        elif self.vertical:
            if segment.start_x <= self.start_x <= segment.stop_x:
                return self.start_x, segment.slope * self.start_x + segment.b;
            return None;
##        else:
##            if self.start_x <= segment.start_x <= self.stop_x:
##                return segment.start_x, self.slope * segment.start_x + self.b;
##            return None;


def segment_image(image, x_segments=32, y_segments=32):
    x_step = image.get_width() // x_segments;
    y_step = image.get_height() // y_segments;
    x_pos, y_pos = 0, 0;
    
    for x in range(x_segments):
        subl = [];
        for y in range(y_segments):
            surf = pygame.Surface((x_step, y_step));
            surf.blit(image, (0, 0), (x_pos, y_pos, x_step, y_step));
            yield surf;
            y_pos += y_step;
        x_pos += x_step;
        y_pos = 0;

def stretch_image_to_quadrilateral_and_draw(surface, image, A, B, C, D):
    width, height = image.get_width(), image.get_height();
    A, B, C, D = sorted((A, B, C, D), key=lambda p: p[1]);
    min_y, max_y = A[1], D[1];
    A, B, C, D = *sorted((A, B), key=lambda p: p[0]), *sorted((C, D), key=lambda p: p[0]);
    min_x, max_x = min(A[0], C[0]), max(B[0], D[0]);
    AB, CD, AC, BD = Segment(A, B), Segment(C, D), Segment(A, C), Segment(B, D);

    x_range = max_x - min_x;
    y_range = max_y - min_y;
    omin_x = min_x;

    constrain = lambda n, min_, max_: max(min_, min(max_, n));

    for x in drange(min_x, max_x, 1):
        scanline = Segment((min_x, min_y), (min_x, max_y));
        min_x += 1;

        inter = scanline.get_vertical_intersection(AB);
        if inter is None: inter = scanline.get_vertical_intersection(AC);
        if inter is None: inter = scanline.get_vertical_intersection(BD);
        start = inter[1];
        
        inter = scanline.get_vertical_intersection(CD);
        if inter is None: inter = scanline.get_vertical_intersection(BD);
        if inter is None: inter = scanline.get_vertical_intersection(AC);
        stop = inter[1];

        start, stop = sorted((start, stop));

        for y in drange(start, stop, 1):
            i, j = int((x - omin_x) / x_range * width), int((y - min_y) / y_range * height);
            i, j = constrain(i, 0, width-1), constrain(j, 0, height-1);
            color = image.get_at((i, j));
            pygame.draw.rect(surface, color, (x, y, 1, 1));
