import math, random, pygame;
from math import sin, cos, tan, sqrt, hypot, pi, atan2;
import cmath;
from random import randint;
from decimal import Decimal;

pygame.font.init();
font = pygame.font.SysFont("arial", 32);

ALLOWED_FUNCTIONS = {
    "sin": sin, "cos": cos, "tan": tan, "sqrt": sqrt,
    "floor": math.floor, "ceil": math.ceil, "abs": abs,
    "arcsin": math.asin, "arccos": math.acos, "arctan": math.atan,
    "max": lambda a, b: max(a, b), "min": lambda a, b: min(a, b),
    "log": math.log, "exp": math.exp,
}

ALLOWED_COMPLEX_FUNCTIONS = {
    "sin": cmath.sin, "cos": cmath.cos, "tan": cmath.tan, "sqrt": cmath.sqrt,
    "abs": abs, "exp": cmath.exp,
};

TWO_PI = 2 * pi;
HALF_PI = pi / 2;
QUARTER_PI = pi / 4;

def drange(start, stop, step=1):
    """
    generator that returns an iterator between start and stop with any step value
    (not just an int). Similar in functionality to np.linspace(start, stop, num=(stop-start)/step)
    except it's an iterator so it doesn't return an np.array and it saves memory.

    should NOT be used for anything that requires a high degree of accuracy!
    """
    yield start;
    if stop >= start:
        while (start + step) < stop:
            start += step;
            yield round(start, 2);
    else:
        while (start + step) > stop:
            start += step;
            yield round(start, 2);

def safe_drange(start, stop, step=1, precision=2):
    """
    drange, but somewhat safer (i.e. less lossy)
    does not work if stop < start.
    """
    scaler = 10 ** precision;
    start, stop = start * scaler, stop * scaler;
    step = step * scaler;
    
    for i in range(int(start), int(stop), int(step)):
        yield i / scaler;


def sign(n):
    """ returns the sign of a number """
    if n: return n/abs(n);
    return 1;

def lerp_vector(v1, v2, pct):
    """ lerps pct percent between v1 and v2 """
    comp = 1 - pct
    return v1[0]*comp+v2[0]*pct,v1[1]*comp+v2[1]*pct,v1[2]*comp+v2[2]*pct

def text(text, x, y, surface, color=(255, 255, 255)):
    """ draws text to a surface """
    surf = font.render(text, 1, color);
    surface.blit(surf, (x, y));

def create_text_surface(text, size, color):
    """ creates a surface with text on it """
    return pygame.font.SysFont("arial", size).render(text, 1, color);

def distance2D(A, B):
    """ calculates the distance between 2 2D points """
    return math.hypot(A[0] - B[0], A[1] - B[1]);

def distance3D(A, B):
    """ calculates the distance between 2 3D points """
    return math.sqrt((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2 + (A[2] - B[2]) ** 2);

def relative_distance(A, B):
    """ Calculates a quantity proportional to 3D distance """
    dx, dy, dz = A[0] - B[0], A[1] - B[1], A[2] - B[2]
    return dx*dx+dy*dy+dz*dz

def midpoint(A, B):
    """ calculates the midpoint between 2 points"""
    return (A[0]+B[0])/2, (A[1]+B[1])/2, (A[2]+B[2])/2;

def tri_midpoint(A, B, C):
    """ calculates the center of a triangle """
    return midpoint(C, midpoint(A, B));

def quad_midpoint(A, B, C, D):
    """ calculate the center of a quadrilateral """
    return midpoint(midpoint(A, B), midpoint(C, D));

def polygon_midpoint(points):
    """ calculate the center of a polygon """
    z = len(points);
    return (sum((p[0] for p in points)) / z,
            sum((p[1] for p in points)) / z,
            sum((p[2] for p in points)) / z,);

def generate_approach_amount(A, B, nsteps=15):
    """ generate a dx and dy value between A and B with nsteps steps """
    x0, y0, x1, y1 = *A, *B;
    return (x0 - x1) / nsteps, (y0 - y1) / nsteps;

def approach(B, dx, dy):
    """ add dx and dy to point B's coordinates """
    return B[0] + dx, B[1] + dy;

def constrain(x, min_=0, max_=255):
    """ constrain a number between two values """
    return min(max_, max(min_, x));

def slope(A, B):
    """ calculate the slope between two points """
    return (A[1] - B[1]) / (A[0] - B[0]);

def sort_clockwise(*points):
    """ sort points clockwise around the center point """
    center = (sum((point[0] for point in points))/len(points), sum((point[1] for point in points))/len(points));
    return sorted(points, key=lambda p: math.atan2(p[1]-center[1], p[0]-center[0]));

def function_gradient(function, step=0.001):
    """ return a gradient estimation of the function """
    return lambda x, y, z: ((function(x + step, y) - function(x, y)) / step,
                            (function(x, y + step) - function(x, y)) / step,
                            0);

def partial_x(function, step=0.001):
    return lambda x, y: (function(x + step, y) - function(x, y)) / step;

def partial_y(function, step=0.001):
    return lambda x, y: (function(x, y + step) - function(x, y)) / step;

class Vector():

    """ A class for representing vectors """

    def __init__(self, x, y, z=0):
        self.x, self.y, self.z = x, y, z;
        self.magnitude = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2);

    def __mul__(self, other):
        return Vector(other * self.x, other * self.y)

    def __rmul__(self, other):
        return self * other;

    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self, other):
        return Vector(self.x-other.x, self.y-other.y, self.z-other.z)

    def __rsub__(self, other):
        return Vector(other.x-self.x, other.y-self.y, other.z-self.z)

    def __repr__(self):
        return "Vector({}, {})".format(round(self.x, 2), round(self.y, 2));

    def __getitem__(self, index):
        if index == 0: return self.x
        if index == 1: return self.y
        if index == 2: return self.z
        raise IndexError

    def normalize(self):
        """ normalize the vector i.e. make it's magnitude 1; 1/||v||*v """
        self.x = self.x / self.magnitude;
        self.y = self.y / self.magnitude;
        self.z = self.z / self.magnitude;

    def dot(self, other):
        """ compute the dot product """
        return self[0] * other[0] + self[1] * other[1] + self[2] * other[2]

    def to_tuple(self):
        """ convert to a 3-tuple """
        return self.x, self.y, self.z

    @staticmethod
    def from_polar(r, theta):
        """ create a vector from magnitude and angle (IN RADIANS) """
        return Vector(r * math.cos(theta), r * math.sin(theta));

    @staticmethod
    def scale(vec, k):
        return Vector(vec.x*k,vec.y*k,vec.z*k)
