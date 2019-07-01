import tkinter as tk;
import os, sys;
from global_imports import *;
from Color import ColorStyle, Styles, Gradient, preset_styles, random_color;
from CartesianFunctions import Function2D, Function3D;
from ParametricFunctions import ParametricFunctionT, ParametricFunctionUV, RevolutionSurface;
from Plot import Plot;
from GUI import PlotCreator;


WIDTH, HEIGHT = 800, 768;#682, 372;
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
        embed.grid(row=0, column=0, rowspan=4, padx=10);
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

##    Function2D(plot, lambda x: 2*sin(3*x/2), line_weight=2);
##    Function3D(plot, lambda x, y: 2*sin(y), color_style=preset_styles["standard-lighting"]);
##    ParametricFunctionT(plot, lambda t: (1, t, cos(t)*t));
##    ParametricFunctionUV(plot, lambda u, v: (u + v, u - v, sin(u * v)), color_style=preset_styles["rainbow"],
##                         u_start=-3, u_stop=3, v_start=-3, v_stop=3);
##    RevolutionSurface(plot, lambda x: x**3/16, color_style=preset_styles["tmp"], surf_on=True);
##    Function3D(plot, lambda x, y: 2 * sin(2 * math.exp(-(x+2)**2/2) * math.exp(-(y+2)**2/2)) + 2 * cos(3 * math.exp(-(x-2)**2) * math.exp(-(y-2)**2)) + 0.5 * sin(x) * cos(y),
##               color_style=preset_styles["rainbow"], x_anchors=50, y_anchors=50, mesh_on=True, surf_on=True);
##    Function3D(plot, lambda x, y: 2*sin(y)*cos(x+y), color_style=preset_styles["rainbow"]);
##    Function3D(plot, lambda x, y: -(x**6+y**6)/1024+4,
##               color_style=preset_styles["coral"]);
##    ParametricFunctionUV(plot, lambda u, v: (4*cos(math.pi*u)*cos(math.pi/2*v),
##                                         4*sin(math.pi*u)*cos(math.pi/2*v),
##                                         4*sin(math.pi/2*v)),
##                         color_style=preset_styles["rainbow"], mesh_on=True);


    
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
                        plot.increment_alpha(event.rel[0] / 10);
                        plot.increment_beta(event.rel[1] / 20);
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
