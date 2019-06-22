from global_imports import *;


def random_color():
    """ returns a random color """
    return randint(0, 255), randint(0, 255), randint(0, 255);

def compress(x, desc=1.5, max_=255):
    """ compresses an x value according to a logistic function. see http://sambrunacini.com/algorithms.html for details """
    z = max_ / (1 + math.e ** ((-1 / desc) * (x - 4 * desc)));
    return z;


class Styles:
    """ Contains the constants indicating which type of coloring to use """
    SOLID = 0;
    CHECKERBOARD = 1;
    WORLD_LIGHTING = 2;
    SCREEN_LIGHTING = 3;
    GRADIENT = 4;
    VALUE_BASED = 5;
    VERTICAL_STRIPED = 6;
    HORIZONTAL_STRIPED = 7;


class Gradient():

    """ class for getting a gradient between two colors """

    def __init__(self, color1=(0, 0, 0), color2=(255, 255, 255), grad_const=1/4, alpha=255):
        self.color1, self.color2 = color1, color2;
        self.grad_const = grad_const;
        self.gradient = self.__generate_grad();
        self.alpha = alpha;

    def next_color(self):
        """ get the next color in the gradient """
        try:
            return next(self.gradient);
        except StopIteration:
            self.gradient = self.__generate_grad();
            return self.next_color();

    def __generate_grad(self):
        """ generates the iterator over the colors in the gradient """
        def approach():
            nonlocal r1, g1, b1, r2, g2, b2, rstep, gstep, bstep;
            while (r1, g1, b1) != (r2, g2, b2):
                if r1 != r2: r1 += rstep;
                if g1 != g2: g1 += gstep;
                if b1 != b2: b1 += bstep;
                yield (r1, g1, b1, self.alpha);
                
        r1, g1, b1 = self.color1;
        r2, g2, b2 = self.color2;
        rstep = sign(r1-r2) * -self.grad_const;
        gstep = sign(g1-g2) * -self.grad_const;
        bstep = sign(b1-b2) * -self.grad_const;

        yield from approach();
        rstep, gstep, bstep = -rstep, -gstep, -bstep;
        r2, g2, b2 = self.color1;
        yield from approach();


class ColorStyle():

    """ An object used by Plottable subclasses to color the plots """

    def __init__(self, style, **kwargs):
        self.style = style;
        self.settings = kwargs;
        if self.style == Styles.GRADIENT:
            self.settings["gradient"] = Gradient(color1=self.settings["color1"], color2=self.settings["color2"]);

    def checkerboard(self, kwargs):
        """ two colors in a checkerboard pattern """
        if (kwargs["i"] + kwargs["j"]) % 2:
            return self.settings["color1"];
        return self.settings["color2"];

    def world_lighting(self, kwargs):
        """ lighting from a source in world coordinates, i.e. one that moves with the graph """
        point = kwargs["point"];
        distance = distance3D(point, self.settings["light_source"]);
        value = (255 - compress(distance, 1.5)) / 255;
        color = self.settings["base_color"]() if callable(self.settings["base_color"]) else self.settings["base_color"];
        return (value * color[0], value * color[1], value * color[2]);

    def gradient(self, kwargs):
        """ lighting from a source in screen coordinates, i.e. stationary """
        m=lambda cc:int(cc*0.8);
        color = self.settings["gradient"].next_color();
        if (kwargs["i"] + kwargs["j"]) % 2:
            return color;
        return m(color[0]), m(color[1]), m(color[2]);

    def value_based(self, kwargs):
        """ color based on the value of the function """
        val_range = abs(kwargs["min_"] - kwargs["max_"]);
        if not val_range: return self.settings["base_color"];
        pct = abs(kwargs["value"] / val_range);
        r, g, b = self.settings["base_color"];
        return (r * pct, g * pct, b * pct);

    def vertical_striped(self, kwargs):
        """ stripes of color parallel to the y axis """
        if kwargs["i"] % 2: return self.settings["color1"];
        return self.settings["color2"];

    def horizontal_striped(self, kwargs):
        """ stripes of color parallel to the x axis """
        if kwargs["j"] % 2: return self.settings["color1"];
        return self.settings["color2"];

    def next_color(self, **kwargs):
        """ get the next color in the style """
        if self.style == Styles.SOLID:
            return self.settings["color"];
        elif self.style == Styles.CHECKERBOARD:
            return self.checkerboard(kwargs);
        elif self.style == Styles.WORLD_LIGHTING:
            return self.world_lighting(kwargs);
        elif self.style == Styles.SCREEN_LIGHTING:
            pass;
        elif self.style == Styles.GRADIENT:
            return self.gradient(kwargs);
        elif self.style == Styles.VALUE_BASED:
            return self.value_based(kwargs);
        elif self.style == Styles.VERTICAL_STRIPED:
            return self.vertical_striped(kwargs);
        elif self.style == Styles.HORIZONTAL_STRIPED:
            return self.horizontal_striped(kwargs);
        
    def reset(self):
        """ reset the style """
        if self.style == Styles.GRADIENT:
            self.settings["gradient"] = Gradient(color1=self.settings["color1"], color2=self.settings["color2"]);
        elif self.style == Styles.WORLD_LIGHTING and callable(self.settings["base_color"]):
            grad = Gradient(c1,c2, 1/4);
            self.settings["base_color"]=grad.next_color;


preset_styles = {
    "tmp": ColorStyle(Styles.GRADIENT, color1=(255, 0, 0), color2=(150, 150, 255)),
    "comic-gradient": ColorStyle(Styles.GRADIENT, color1=(128, 0, 0), color2=(155, 155, 155)),
    "mermaid": ColorStyle(Styles.GRADIENT, color1=(186, 45, 97), color2=(90, 217, 159)),
    "website": ColorStyle(Styles.GRADIENT, color1=(255, 150, 0), color2=(0, 0, 255)),
    "golf": ColorStyle(Styles.GRADIENT, color1=(180, 160, 165), color2=(15, 180, 30)),
    "salamence": ColorStyle(Styles.GRADIENT, color1=(68, 171, 178), color2=(235, 90, 5)),

    "standard-lighting": ColorStyle(Styles.WORLD_LIGHTING, light_source=(0, 0, 7), base_color=(255, 255, 255)),
    "incandescent-lighting": ColorStyle(Styles.WORLD_LIGHTING, light_source=(0, 0, 6), base_color=(244, 200, 66)),
    "overhead-lighting": ColorStyle(Styles.WORLD_LIGHTING, light_source=(2, 2, 4), base_color=(255, 0, 255)),
    
    "cool-blue": ColorStyle(Styles.CHECKERBOARD, color1=(0, 100, 100), color2=(0, 200, 200)),
    "comic-checker": ColorStyle(Styles.CHECKERBOARD, color1=(128, 0, 0), color2=(155, 155, 155)),
    "3blue1brown": ColorStyle(Styles.CHECKERBOARD, color1=(50, 50, 255), color2=(100, 100, 255)),
    "reds": ColorStyle(Styles.CHECKERBOARD, color1=(255, 50, 50), color2=(255, 100, 100)),

    "poison": ColorStyle(Styles.HORIZONTAL_STRIPED, color1=(132, 22, 164), color2=(10, 252, 119)),
    "circus": ColorStyle(Styles.HORIZONTAL_STRIPED, color1=(230, 206, 52), color2=(245, 42, 148)),
    "zebra": ColorStyle(Styles.HORIZONTAL_STRIPED, color1=(41, 65, 66), color2=(198, 181, 250)),

    "cushion": ColorStyle(Styles.VALUE_BASED, base_color=(255, 100, 100)),
    
    "default": ColorStyle(Styles.SOLID, color=(255, 0, 0)),
}
