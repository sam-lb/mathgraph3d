import tkinter as tk;
import os, sys;
from global_imports import *;
from Color import ColorStyle, Styles, Gradient, preset_styles, random_color;
from CartesianFunctions import Function2D, Function3D;
from ParametricFunctions import ParametricFunctionT, ParametricFunctionUV, RevolutionSurface;
from VectorFunctions import VectorField;
from StatisticalPlots import StatPlot2D, StatPlot3D;
from OtherCoordinateSystems import CylindricalFunction, SphericalFunction;
from Plot import Plot;
from GUI import PlotCreator;


WIDTH, HEIGHT = 800, 768;
HWIDTH, HHEIGHT = WIDTH // 2, HEIGHT // 2;
GUI = True;


def on_close():
    global running;
    running = False;
    root.destroy();


if __name__ == "__main__":
    if GUI:
        root = tk.Tk();
        embed = PlotCreator(root, width=WIDTH, height=HEIGHT);
        embed.grid(row=0, column=0, rowspan=6, padx=10);
        os.environ["SDL_WINDOWID"] = str(embed.winfo_id());
        root.protocol("WM_DELETE_WINDOW", on_close);
        root.update();
    
    pygame.init();
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE);
    pygame.display.set_caption("ThreeDE - V5");
    pygame.key.set_repeat(100, 50);

    clock = pygame.time.Clock();
    running = True;

    if GUI:
        plot = Plot(screen, gui=embed);
    else:
        plot = Plot(screen, axes_on=True, angles_on=True, labels_on=False, tracker_on=False, spin=False, alpha=0.5, beta=0.8,
                    x_start=-4, x_stop=4, y_start=-4, y_stop=4, z_start=-4, z_stop=4);

    
    while running:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False;
                    break;
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False;
                        break;
                    elif event.key == pygame.K_r:
                        plot.set_alpha(0.5);
                        plot.set_beta(0.8);
                    elif event.key == pygame.K_LEFT:
                        plot.increment_alpha(-0.1);
                    elif event.key == pygame.K_RIGHT:
                        plot.increment_alpha(0.1);
                    elif event.key == pygame.K_UP:
                        plot.increment_beta(-0.1);
                    elif event.key == pygame.K_DOWN:
                        plot.increment_beta(0.1);
                    elif event.key == pygame.K_i:
                        plot.zoom(20);
                    elif event.key == pygame.K_o:
                        plot.zoom(-20);
                        plot.needs_update = True;
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:
                        plot.increment_alpha(event.rel[0] / 160);
                        plot.increment_beta(event.rel[1] / 320);
                elif event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.w, event.h;
                    HWIDTH, HHEIGHT = WIDTH // 2, HEIGHT // 2;
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
    pygame.quit();
