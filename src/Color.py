from global_imports import *;


def random_color():
    """ returns a random color """
    return randint(0, 255), randint(0, 255), randint(0, 255);

def compress(x, desc=1.5, max_=255):
    """ compresses an x value according to a logistic function. see http://sambrunacini.com/algorithms.html#grapher/ for details """
    z = max_ / (1 + math.e ** ((-1 / desc) * (x - 4 * desc)));
    return z;


class Styles:
    """ Contains the constants indicating which type of coloring to use """
    SOLID = 0;
    CHECKERBOARD = 1;
    SCREEN_LIGHTING = 2;
    GRADIENT = 3;
    VERTICAL_STRIPED = 4;
    HORIZONTAL_STRIPED = 5;
    COLOR_SET = 6;


class Gradient():

    """ class for getting a gradient between two colors """

    def __init__(self, color1=(0, 0, 0), color2=(255, 255, 255), grad_const=1/4, alpha=255):
        self.color1, self.color2 = color1, color2;
        self.grad_const = grad_const;
        self.gradient = self.__generate_grad();
        self.alpha = alpha;

    def next_color(self):
        """ get the next color in the gradient """
        if self.color1 == self.color2: return self.color1;
        
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
        elif self.style == Styles.COLOR_SET:
            self.settings["step"] = self.settings["step"] / 100;

    def checkerboard(self, kwargs):
        """ two colors in a checkerboard pattern """
        if (kwargs["i"] + kwargs["j"]) % 2:
            return self.settings["color1"];
        return self.settings["color2"];

    def apply_lighting(self, color, kwargs):
        """ apply lighting from a source in world coordinates, i.e. one that moves with the graph """
        point = kwargs["point"];
        distance = distance3D(point, self.settings["light_source"]);
        value = (255 - compress(distance, 1.5)) / 255;
        return value * color[0], value * color[1], value * color[2];

    def gradient(self, kwargs):
        """ smooth gradient between two colors """
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
        return (constrain(r * pct), constrain(g * pct), constrain(b * pct));

    def vertical_striped(self, kwargs):
        """ stripes of color parallel to the y axis """
        if kwargs["i"] % 2: return self.settings["color1"];
        return self.settings["color2"];

    def horizontal_striped(self, kwargs):
        """ stripes of color parallel to the x axis """
        if kwargs["j"] % 2: return self.settings["color1"];
        return self.settings["color2"];

    def color_set(self, kwargs):
        """ A mapping of normalized function values to a set of colors in a dict """
        m=lambda cc:int(cc*0.8);
        if kwargs["max_"] == kwargs["min_"]:
            r, g, b = self.settings["color_set"][0];
        else:
            norm = kwargs["value"] / abs(kwargs["max_"]) if kwargs["value"] >= 0 else kwargs["value"] / abs(kwargs["min_"]);
            low_interval = max(-1, min(1-self.settings["step"], norm - norm % self.settings["step"], 1));
            high_interval = low_interval + self.settings["step"];
            r1, g1, b1, r2, g2, b2 = *self.settings["color_set"][int(low_interval * 100)], *self.settings["color_set"][int(high_interval * 100)];
            
            range_val = abs((norm - low_interval) / (high_interval - low_interval));
            r, g, b = r1 + (r2 - r1) * range_val, g1 + (g2 - g1) * range_val, b1 + (b2 - b1) * range_val;

        if (kwargs["i"] + kwargs["j"]) % 2:
            return m(r), m(g), m(b);
        return r, g, b;

    def next_color(self, **kwargs):
        """ get the next color in the style """
        if self.style == Styles.SOLID:
            color = self.settings["color"];
        elif self.style == Styles.CHECKERBOARD:
            color = self.checkerboard(kwargs);
        elif self.style == Styles.SCREEN_LIGHTING:
            pass;
        elif self.style == Styles.GRADIENT:
            color = self.gradient(kwargs);
        elif self.style == Styles.VALUE_BASED:
            color = self.value_based(kwargs);
        elif self.style == Styles.VERTICAL_STRIPED:
            color = self.vertical_striped(kwargs);
        elif self.style == Styles.HORIZONTAL_STRIPED:
            color = self.horizontal_striped(kwargs);
        elif self.style == Styles.COLOR_SET:
            color = self.color_set(kwargs);

        if not self.settings.get("apply_lighting"): # accounts for both cases: False/not provided
            return color;
        return self.apply_lighting(color, kwargs);
        
    def reset(self):
        """ reset the style """
        if self.style == Styles.GRADIENT:
            self.settings["gradient"] = Gradient(color1=self.settings["color1"], color2=self.settings["color2"]);


preset_styles = {
    "tmp": ColorStyle(Styles.GRADIENT, color1=(255, 0, 0), color2=(150, 150, 255)),
    "comic-gradient": ColorStyle(Styles.GRADIENT, color1=(128, 0, 0), color2=(155, 155, 155)),
    "mermaid": ColorStyle(Styles.GRADIENT, color1=(186, 45, 97), color2=(90, 217, 159)),
    "website": ColorStyle(Styles.GRADIENT, color1=(255, 150, 0), color2=(0, 0, 255)),
    "golf": ColorStyle(Styles.GRADIENT, color1=(180, 160, 165), color2=(15, 180, 30)),
    "salamence": ColorStyle(Styles.GRADIENT, color1=(68, 171, 178), color2=(235, 90, 5)),

    "standard-lighting": ColorStyle(Styles.SOLID, light_source=(0, 0, 7), apply_lighting=True, color=(255, 255, 255)),
    "incandescent-lighting": ColorStyle(Styles.SOLID, light_source=(0, 0, 6), apply_lighting=True, color=(244, 200, 66)),
    "overhead-lighting": ColorStyle(Styles.SOLID, light_source=(2, 2, 4), apply_lighting=True, color=(255, 0, 255)),
    
    "cool-blue": ColorStyle(Styles.CHECKERBOARD, color1=(0, 100, 100), color2=(0, 200, 200)),
    "comic-checker": ColorStyle(Styles.CHECKERBOARD, color1=(128, 0, 0), color2=(155, 155, 155)),
    "3blue1brown": ColorStyle(Styles.CHECKERBOARD, color1=(50, 50, 255), color2=(100, 100, 255)),
    "reds": ColorStyle(Styles.CHECKERBOARD, color1=(255, 50, 50), color2=(255, 100, 100)),

    "poison": ColorStyle(Styles.HORIZONTAL_STRIPED, color1=(132, 22, 164), color2=(10, 252, 119)),
    "circus": ColorStyle(Styles.HORIZONTAL_STRIPED, color1=(230, 206, 52), color2=(245, 42, 148)),
    "zebra": ColorStyle(Styles.HORIZONTAL_STRIPED, color1=(41, 65, 66), color2=(198, 181, 250)),
    
    "default": ColorStyle(Styles.SOLID, color=(255, 0, 0)),

    "rainbow": ColorStyle(Styles.COLOR_SET, color_set={100: (255, 0, 0), 50: (255, 128, 0), 0: (255, 255, 0), -50: (0, 255, 0), -100: (0, 0, 255)}, step=50),
    "america": ColorStyle(Styles.COLOR_SET, color_set={100: (255, 255, 255), 50: (0, 0, 255), 0: (150, 0, 150), -50: (255, 0, 0), -100: (128, 128, 128)}, step=50),
    "coral": ColorStyle(Styles.COLOR_SET, color_set={50: (126, 5, 180), 100: (8, 183, 165), -100: (54, 3, 125), 0: (217, 40, 220), -50: (216, 201, 227)}, step=50),
    "cs-mermaid": ColorStyle(Styles.COLOR_SET, color_set={50: (222, 70, 175), 100: (151, 119, 201), -100: (83, 167, 8), 0: (160, 204, 64), -50: (87, 252, 240)}, step=50),
    "random": ColorStyle(Styles.COLOR_SET, color_set={100: random_color(), 50: random_color(), 0: random_color(), -50: random_color(), -100: random_color()}, step=50),
}
