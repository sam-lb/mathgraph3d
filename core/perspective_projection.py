import pygame;
import numpy as np;
from math import sin, cos;
pygame.init();

width, height, depth = 640, 480, 800;
camera = [width // 2, height // 2, depth];
units_x, units_y, units_z = 8, 8, 8;
scale_x, scale_y, scale_z = width / units_x, height / units_y, depth / units_z;

screen = pygame.display.set_mode((width, height));
pygame.display.set_caption("3D perspective projection test");
pygame.key.set_repeat(100, 50);

def scale(p):
  """ scale a point by the number of pixels per unit in each direction """
  return p[0] * scale_x, p[1] * scale_y, p[2] * scale_z;

def translate_to_screen(p):
  """ convert from projected cartesian coordinates to canvas coordinates """
  return p[0] + width // 2, height // 2 - p[1];

def project(p):
  """ project a point onto the 2D plane """
  proj_x = (camera[2] * (p[0] - camera[0])) / (camera[2] + p[2]) + camera[0];
  proj_y = (camera[2] * (p[1] - camera[1])) / (camera[2] + p[2]) + camera[1];
  return proj_x, proj_y;

def rproj(a, tx, ty, tz):
    rotation = rot_mat_x(tx).dot(rot_mat_y(ty)).dot(rot_mat_z(tz));
    sub = np.array([a]) - np.array([camera]);
    d = list(sub.dot(rotation)[0]);
    e = width, height, depth;
    return e[2] / d[2] * d[0] + e[0], e[2] / d[2] * d[1] + e[1];

def screen_point(p):
  """ convert a point in 3D cartesian space to a point in 2D canvas space """
  return translate_to_screen(project(scale(p)));

def project_triangle(tri):
    """ return the screen coordinates of a triangle """
    angs = (tx, ty, tz);
    return rproj(tri[0], *angs), rproj(tri[1], *angs), rproj(tri[2], *angs);
##    return screen_point(tri[0]), screen_point(tri[1]), screen_point(tri[2]);

def project_line(line):
    """ return the screen coordinates of a line """
    return screen_point(line[0]), screen_point(line[1]);

def rot_mat_x(theta):
    return np.array([
        [1, 0, 0],
        [0, cos(theta), -sin(theta)],
        [0, sin(theta), cos(theta)],
    ]);

def rot_mat_y(theta):
    return np.array([
        [cos(theta), 0, sin(theta)],
        [0, 1, 0],
        [-sin(theta), 0, cos(theta)],
    ]);

def rot_mat_z(theta):
    return np.array([
        [cos(theta), -sin(theta), 0],
        [sin(theta), cos(theta), 0],
        [0, 0, 1],
    ]);

triangle = ((1, 1, 1), (2, 2, 2), (1, 2, 1));

x_axis = ((-2, 0, 0), (2, 0, 0));
y_axis = ((0, -2, 0), (0, 2, 0));
z_axis = ((0, 0, -2), (0, 0, 2));
tx, ty, tz = 0, 0, 0;

clock = pygame.time.Clock();
running = True;
while running:

    screen.fill((255, 255, 200));
    proj_triangle = project_triangle(triangle);
    pygame.draw.polygon(screen, (255, 0, 200), proj_triangle);
    pygame.draw.polygon(screen, (0, 0, 0), proj_triangle, 1);
    pygame.draw.rect(screen, (255, 0, 0), (*proj_triangle[0], 10, 10));
    pygame.draw.rect(screen, (0, 255, 0), (*proj_triangle[1], 10, 10));
    pygame.draw.rect(screen, (0, 0, 255), (*proj_triangle[2], 10, 10));
##    proj_ax, proj_ay, proj_az = project_line(x_axis), project_line(y_axis), project_line(z_axis);
##    pygame.draw.line(screen, (255, 0, 0), proj_ax[0], proj_ax[1], 1);
##    pygame.draw.line(screen, (0, 255, 0), proj_ay[0], proj_ay[1], 1);
##    pygame.draw.line(screen, (0, 0, 255), proj_az[0], proj_az[1], 1);
    pygame.display.flip();
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False;
            break;
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                #camera[0] -= 25;
##                camera = list(np.array([camera]).dot(rot_mat_y(0.2).dot(rot_mat_z(0.1)))[0]);
                tx += 0.1;
            elif event.key == pygame.K_RIGHT:
                #camera[0] += 25;
##                camera = list(np.array([camera]).dot(rot_mat_z(-0.1))[0]);
                tx -= 0.1;
            elif event.key == pygame.K_UP:
                ty += 0.1;
            elif event.key == pygame.K_DOWN:
                ty -= 0.1;
            elif event.key == pygame.K_SPACE:
                print(camera);
            elif event.key == pygame.K_ESCAPE:
                running = False;
                break;
    clock.tick(30);
    
pygame.quit();
