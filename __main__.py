from global_imports import *;
from Color import ColorStyle, Styles, Gradient, preset_styles, random_color;
from CartesianFunctions import Function2D, Function3D;
from ParametricFunctions import ParametricFunctionT, ParametricFunctionUV, RevolutionSurface;
from Plot import Plot;


WIDTH, HEIGHT = 682, 372;
HWIDTH, HHEIGHT = WIDTH // 2, HEIGHT // 2;

if __name__ == "__main__":
    pygame.init();
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE);
    pygame.display.set_caption("ThreeDE - V5");
    pygame.key.set_repeat(100, 50);

    clock = pygame.time.Clock();
    running = True;

    plot = Plot(screen, axes_on=True, angles_on=True, labels_on=False, tracker_on=False, alpha=0.5, beta=0.8,
                x_start=-4, x_stop=4, y_start=-4, y_stop=4, z_start=-4, z_stop=4);

##    Function2D(plot, lambda x: 2*sin(3*x/2), line_weight=2);
##    Function3D(plot, lambda x, y: cos(y), color_style=preset_styles["poison"]);
##    ParametricFunctionT(plot, lambda t: (1, t, cos(t)*t));
##    ParametricFunctionUV(plot, lambda u, v: (u + v, u - v, sin(u * v)), color_style=preset_styles["comic-checker"],
##                         u_start=-3, u_stop=3, v_start=-3, v_stop=3);
    RevolutionSurface(plot, lambda x: x**3/16, color_style=preset_styles["tmp"], surf_on=True);
    

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
        except Exception as e:
            pygame.quit();
            raise e;
    pygame.quit();
    
