import tkinter as tk
import os, sys, time, ctypes
from scipy.special import gamma
from mathgraph3D.global_imports import *
from mathgraph3D.Color import ColorStyle, Styles, Gradient, preset_styles, random_color
from mathgraph3D.CartesianFunctions import Function2D, Function3D
from mathgraph3D.ParametricFunctions import ParametricFunctionT, ParametricFunctionUV, RevolutionSurface
from mathgraph3D.VectorFunctions import VectorField
from mathgraph3D.StatisticalPlots import StatPlot2D, StatPlot3D
from mathgraph3D.OtherCoordinateSystems import CylindricalFunction, SphericalFunction, PolarFunction
from mathgraph3D.ImplicitPlots import ImplicitPlot2D, ImplicitSurface
from mathgraph3D.ComplexFunctions import ComplexFunction
from mathgraph3D.RecurrenceRelation import RecurrenceRelation
from mathgraph3D.ClippingPlane import ClippingPlane
from mathgraph3D.Plot import Plot
from mathgraph3D.GUI import Interface

ALPHA_INCREMENT, BETA_INCREMENT = 0.1, 0.1;
INITIAL_ALPHA, INITIAL_BETA = 0.5, 0.8;
ZOOM_FACTOR = 20;
debug_dict = {};

#print(ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1));


def on_close():
    global running;
    running = False;
    root.destroy();

def main():
    WIDTH, HEIGHT = 683, 600
    GUI = True
    TESTING = False

    def on_close():
        nonlocal running
        running = False
        root.destroy()

    if GUI:
        WIDTH = ctypes.windll.user32.GetSystemMetrics(0) // 2;
        HEIGHT = ctypes.windll.user32.GetSystemMetrics(1);
        root = tk.Tk();
        root.config(background="#ddddff");
        root.state("zoomed");
        embed = Interface(root, width=WIDTH, height=HEIGHT);
        embed.grid(row=0, column=0, rowspan=6, padx=10);
        os.environ["SDL_WINDOWID"] = str(embed.winfo_id());
        root.protocol("WM_DELETE_WINDOW", on_close);
        root.update();
    else:
        os.environ["SDL_VIDEO_WINDOW_POS"] = "600,50"

    loops, total_time = 0, 0;
    
    pygame.init();
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE);
    pygame.display.set_caption("MathGraph 3D");
    pygame.key.set_repeat(100, 50);

    clock = pygame.time.Clock();
    running = True;

    if GUI:
        plot = Plot(screen, gui=embed);
        embed.set_plot(plot);
    else:
        plot = Plot(screen, axes_on=False, angles_on=False, labels_on=False, tracker_on=False, spin=False, line_numbers=True,
                    x_start=-16, x_stop=16, y_start=-16, y_stop=16, z_start=-16, z_stop=16, ticks=True, alpha=2.75, beta=0.35);

    debug_dict["plot"] = plot;

##    plot.add_clipping_plane(ClippingPlane(2, 3, 1, 0, 0, 0))
##    f_x = lambda u, v: (3+sin(v)+cos(u))*cos(2*v)
##    f_y = lambda u, v: (3+sin(v)+cos(u))*sin(2*v)
##    f_z = lambda u, v: sin(u)+2*cos(v)
##    ParametricFunctionUV(plot, lambda u, v: (f_x(u, v), f_y(u, v), f_z(u, v)), u_start=-math.pi, u_stop=math.pi, v_start=-math.pi, v_stop=math.pi, mesh_on=True, color_style=ColorStyle(Styles.INVNORM), u_anchors=120, v_anchors=30);
##    CylindricalFunction(plot, lambda z, t: t/z, color_style=ColorStyle(Styles.GRADIENT, color1=(200, 100, 100), color2=(100, 100, 200)), z_anchors=70, mesh_on=False);
##    Function3D(plot, lambda x, y: 2*(sin(x)+sin(y)), color_style=ColorStyle(Styles.CHECKERBOARD, color1=(200, 0, 50), color2=(255, 0, 255)));
##    Function3D(plot, lambda x, y: sin(math.sqrt(x**2+y**2))-1, color_style=ColorStyle(Styles.SOLID, color=(255, 255, 255), apply_lighting=True, light_source=(0, 0, 4)), x_anchors=220, y_anchors=220, mesh_on=False);
##    RevolutionSurface(plot, lambda x: x, surf_on=True);
##    RecurrenceRelation(plot, lambda last: 2*last*(1-last), seed_value=0.75, unit_scale=1);
##    PolarFunction(plot, lambda theta: 4);
##    Function3D(plot, lambda x, y: (y*sin(x) + x*cos(y))/2, color_style=ColorStyle(Styles.CHECKERBOARD, color1=(100, 100, 255), color2=(150, 255, 150), apply_lighting=True, light_source=(0, 0, 6)));
##    ImplicitPlot2D(plot, lambda x, y: y*sin(x) + x*cos(y) - 1, color=(0, 128, 255));
##    ImplicitPlot2D(plot, lambda x, y: -(y*sin(x) + x*cos(y)) - 1, color=(255, 128, 0));
##    ImplicitPlot2D(plot, lambda x, y: sqrt(sin(x**2+y**2))+1, line_weight=2, squares_x=10, squares_y=10);
##    function = lambda x, y: sin(sin(x)+sin(y));
##    Function3D(plot, function, color_style=ColorStyle(Styles.SOLID, color=(228, 228, 255), apply_lighting=True, light_source=(0, 0, 6)));
##    VectorField.slope_field_of(plot, function, vecs_per_unit=2);
##    ComplexFunction(plot, lambda z: complex(cmath.sqrt(z).imag, cmath.sqrt(z).real));
##    ComplexFunction(plot, cmath.atan);
##    ComplexFunction(plot, lambda z: cmath.sin(z)+cmath.cos(z));
##    function = plot.plane_from_3_points((2, 7, -3), (1, -1, 0), (6, -2, 4));
##    Function3D(plot, function, color_style=ColorStyle(Styles.SOLID, color=(200, 200, 255)));
##    VectorField.slope_field_of(plot, function, vecs_per_unit=2);
##    ComplexFunction(plot, cmath.exp, mesh_on=False, real_anchors=64, imag_anchors=64);
##    ComplexFunction(plot, cmath.asin, mesh_on=True, real_anchors=32, imag_anchors=32, detection=True);
##    ComplexFunction(plot, cmath.sin);

##    func = lambda x, y: cos(x**2+y);
##    tangent = plot.tangent_plane(func, 0, 1);
##    plot.add_point((0, 1, func(0, 1)));
##    Function3D(plot, func, color_style=preset_styles["cool-blue"]);
##    Function3D(plot, tangent, color_style=ColorStyle(Styles.SOLID, color=(225, 225, 255)));
##    Function3D(plot, lambda x, y: x**2-y**2, color_style=ColorStyle(Styles.VERTICAL_STRIPED, color1=(0, 0, 0), color2=(255, 255, 255), apply_lighting=True, light_source=(0, 0, 6)));
##    Function3D(plot, lambda x, y: (x*x+y*y)/4);
##    Function3D(plot, lambda x, y: cos(2*pi*(1.1*x-y))+cos(2*pi*(1.2*x-y))+cos(2*pi*(1.3*x-y))+cos(2*pi*(1.4*x-y))+cos(2*pi*(1.5*x-y))+cos(2*pi*(1.6*x-y))+cos(2*pi*(1.7*x-y))+cos(2*pi*(1.8*x-y))+cos(2*pi*(1.9*x-y))+cos(2*pi*(2*x-y)),
##               x_anchors=100, y_anchors=100, color_style=ColorStyle(Styles.INVNORM), mesh_on=False)
##    ImplicitSurface(plot, lambda x, y, z: x*y*z, lambda x, y, z: 0, color_style=ColorStyle(Styles.INVNORM), cubes_per_axis=30)
    Function3D(plot, lambda x, y: x+y*y/10 + 15*(sin(x)*sin(y))**4, color_style=ColorStyle(Styles.NORMAL_VECTOR), x_anchors=50, y_anchors=50, mesh_on=False)


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
            raise;
            pygame.quit();
            
        total_time += time.time() - initial_time;
        loops += 1;
    pygame.quit();


    if TESTING:
        msg = "In __main__: old projection (scaling done for every point)";
        from performance_testing import record;

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
