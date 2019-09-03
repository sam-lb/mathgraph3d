import tkinter as tk;
import os, sys, time;
from global_imports import *;
from Color import ColorStyle, Styles, Gradient, preset_styles, random_color;
from CartesianFunctions import Function2D, Function3D;
from ParametricFunctions import ParametricFunctionT, ParametricFunctionUV, RevolutionSurface;
from VectorFunctions import VectorField;
from StatisticalPlots import StatPlot2D, StatPlot3D;
from OtherCoordinateSystems import CylindricalFunction, SphericalFunction;
from Plot import Plot;
from GUI import PlotCreator;

ALPHA_INCREMENT, BETA_INCREMENT = 0.1, 0.1;
INITIAL_ALPHA, INITIAL_BETA = 0.5, 0.8;
ZOOM_FACTOR = 20;
debug_dict = {};


def on_close():
    global running;
    running = False;
    root.destroy();

def main():
    WIDTH, HEIGHT = 630, 500;
    GUI = False;
    TESTING = False;

    def on_close():
        nonlocal running;
        running = False;
        root.destroy();

    if GUI:
        root = tk.Tk();
        embed = PlotCreator(root, width=WIDTH, height=HEIGHT);
        embed.grid(row=0, column=0, rowspan=6, padx=10);
        os.environ["SDL_WINDOWID"] = str(embed.winfo_id());
        root.protocol("WM_DELETE_WINDOW", on_close);
        root.update();

    loops, total_time = 0, 0;

    pygame.init();
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE);
    pygame.display.set_caption("ThreeDE - V5");
    pygame.key.set_repeat(100, 50);

    clock = pygame.time.Clock();
    running = True;

    if GUI:
        plot = Plot(screen, gui=embed);
    else:
        plot = Plot(screen, axes_on=True, angles_on=False, labels_on=False, tracker_on=False, spin=False, alpha=0.5, beta=0.8,
                    x_start=-4, x_stop=4, y_start=-4, y_stop=4, z_start=-4, z_stop=4);

##    f_x = lambda u, v: (3+sin(v)+cos(u))*cos(2*v);
##    f_y = lambda u, v: (3+sin(v)+cos(u))*sin(2*v);
##    f_z = lambda u, v: sin(u)+2*cos(v);
##    ParametricFunctionUV(plot, lambda u, v: (f_x(u, v), f_y(u, v), f_z(u, v)), u_start=-math.pi, u_stop=math.pi, v_start=-math.pi, v_stop=math.pi, mesh_on=False, color_style=ColorStyle(Styles.SOLID, color=(255, 0, 0), apply_lighting=True, light_source=(0,0,6)), u_anchors=150, v_anchors=150);
##    CylindricalFunction(plot, lambda z, t: t/z, color_style=ColorStyle(Styles.GRADIENT, color1=(200, 100, 100), color2=(100, 100, 200)), z_anchors=70, mesh_on=False);
##    Function3D(plot, lambda x, y: 2*(sin(x)+sin(y)), color_style=ColorStyle(Styles.CHECKERBOARD, color1=(200, 0, 50), color2=(255, 0, 255)), mesh_on=False);
##    Function3D(plot, lambda x, y: sin(math.sqrt(x**2+y**2))-1, color_style=ColorStyle(Styles.SOLID, color=(255, 255, 255), apply_lighting=True, light_source=(0, 0, 4)), x_anchors=220, y_anchors=220, mesh_on=False);
##    RevolutionSurface(plot, lambda x: x, surf_on=True);
##    Function3D(plot, lambda x, y: math.sqrt(4-x**2-y**2), color_style=ColorStyle(Styles.SOLID, color=(255, 255, 255), apply_lighting=True, light_source=(0,0,6)), x_anchors=100, y_anchors=10000, mesh_on=False);

    while running:
        initial_time = time.time();
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False;
                    break;
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        plot.set_alpha(INITIAL_ALPHA);
                        plot.set_beta(INITIAL_BETA);
                    elif event.key == pygame.K_LEFT:
                        plot.increment_alpha(-ALPHA_INCREMENT);
                    elif event.key == pygame.K_RIGHT:
                        plot.increment_alpha(ALPHA_INCREMENT);
                    elif event.key == pygame.K_UP:
                        plot.increment_beta(-BETA_INCREMENT);
                    elif event.key == pygame.K_DOWN:
                        plot.increment_beta(BETA_INCREMENT);
                    elif event.key == pygame.K_i:
                        plot.zoom(ZOOM_FACTOR);
                    elif event.key == pygame.K_o:
                        plot.zoom(-ZOOM_FACTOR);
                        plot.needs_update = True;
                    elif not GUI and event.key == pygame.K_RETURN:
                        pygame.image.save(screen, "C:\\Users\\sam\\Desktop\\3D Plots\\{}.png".format(input("name (no extension) > ")));
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:
                        plot.increment_alpha(event.rel[0] / 160);
                        plot.increment_beta(event.rel[1] / 320);
                elif event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.w, event.h;
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE);
                    plot.surface = screen;
                    plot.s_width, plot.s_height = screen.get_width()//2, screen.get_height()//2;
                    plot.needs_update = True;

            plot.update();
            clock.tick(50);
            if running and GUI: root.update();
        except Exception as e:
            pygame.quit();
            raise e;
        total_time += time.time() - initial_time;
        loops += 1;
    pygame.quit();


    if TESTING:
        msg = "In __main__: without using DOUBLEBUF";
        from performance_test import record;

        record(
            {
                "description": msg,
                "total time": plot.time,
                "total updates": plot.updates,
                "average update time": plot.get_average_update_time(),
                "average event loop time": loops / total_time
            }
        );

if __name__ == "__main__":
    main();
