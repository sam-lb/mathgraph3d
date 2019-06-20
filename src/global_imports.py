import math, random, pygame;
from math import sin, cos, tan, sqrt, hypot, pi;
from random import randint;

pygame.font.init();
font = pygame.font.SysFont("arial", 32);

def drange(start, stop, step=1):
    """
    generator that returns an iterator between start and stop with any step value
    (not just an int). Similar in functionality to np.linspace(start, stop, num=(stop-start)/step)
    except it's an iterator so it doesn't return an np.array and it saves memory.
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

def sign(n):
    """ returns the sign of a number """
    if n: return n/abs(n);
    return 1;

def text(text, x, y, surface, color=(255, 255, 255)):
    """ draws text to a surface """
    surf = font.render(text, 1, color);
    surface.blit(surf, (x, y));

def distance3D(A, B):
    """ calculates the distance between 2 3D points """
    return math.sqrt((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2 + (A[2] - B[2]) ** 2);

def midpoint(A, B):
    """ calculates the midpoint between 2 points"""
    return (A[0]+B[0])/2, (A[1]+B[1])/2, (A[2]+B[2])/2;

def tri_midpoint(A, B, C):
    """ calculates the center of a triangle """
    return midpoint(C, midpoint(A, B));

def quad_midpoint(A, B, C, D):
    """ calculate the center of a quadrilateral """
    return midpoint(midpoint(A, B), midpoint(C, D));


class Vector():

    """ A class for representing vectors """

    def __init__(self, x, y, z=0):
        self.x, self.y, self.z = x, y, z;
        self.magnitude = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2);

    def __mul__(self, other):
        return Vector(other * self.x, other * self.y)

    def __rmul__(self, other):
        return self * other;

    def __repr__(self):
        return "Vector({}, {})".format(round(self.x, 2), round(self.y, 2));

    def normalize(self):
        """ normalize the vector i.e. make it's magnitude 1; ||v|| """
        self.x = self.x / self.magnitude;
        self.y = self.y / self.magnitude;
        self.z = self.z / self.magnitude;

    @staticmethod
    def from_polar(r, theta):
        """ create a vector from magnitude and angle (IN RADIANS) """
        return Vector(r * math.cos(theta), r * math.sin(theta));
