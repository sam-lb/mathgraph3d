from mathgraph3D.core.global_imports import *;
from math import *;


def random_color():
    """ returns a random color """
    return randint(0, 255), randint(0, 255), randint(0, 255);

def compress(x, desc=1.5, max_=255):
    """ compresses an x value according to a logistic function. see http://sambrunacini.com/algorithms.html#grapher/ for details """
    z = max_ / (1 + math.e ** ((-1 / desc) * (x - 4 * desc)));
    return z;

def vector_between_points(P, Q):
    """ vector between initial point P and terminal point Q """
    return vector_subtract(Q, P);

def cross_product(u, v):
    """ return the cross product of u and v """
    return u[1] * v[2] - u[2] * v[1], -(u[0] * v[2] - u[2] * v[0]), u[0] * v[1] - u[1] * v[0];

def scalar_multiply(c, u):
    """ return the vector u scaled by the scalar c """
    return tuple((c * a for a in u));

def angle_between_vectors(u, v):
    """ compute the angle between two vectors u and v """
    return acos(dot_product(u, v) / (magnitude(u) * magnitude(v)));

def dot_product(u, v):
    """ compute the dot product of u and v """
    return sum((a*b for a, b in zip(u, v)));

def magnitude(u):
    """ compute the magnitude of a vector u """
    result = sum(a*a for a in u);
    return sqrt(result);

def normalize(u):
    """ normalize a vector """
    mag = magnitude(u);
    return u[0] / mag, u[1] / mag, u[2] / mag;

def project(u, v):
    """ find the projection vector of u onto v """
    return scalar_multiply(dot_product(u, v) / (magnitude(v) ** 2), v);

def vector_subtract(u, v):
    """ return u - v """
    return tuple((a - b) for a, b in zip(u, v));

def color_average(a, b):
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2;

def scalar_multiply(c, u):
    """ return the vector u scaled by the scalar c """
    return tuple((c * a for a in u));


I = (1, 0, 0);
J = (0, 1, 0);
K = (0, 0, 1);

convert = lambda n: min(255, n / pi * 255 + 32);


class Styles:
    """ Contains the constants indicating which type of coloring to use """
    SOLID = 0;
    CHECKERBOARD = 1;
    SCREEN_LIGHTING = 2;
    GRADIENT = 3;
    VERTICAL_STRIPED = 4;
    HORIZONTAL_STRIPED = 5;
    COLOR_SET = 6;
    NORMAL_VECTOR = 7;
    FULL_EXPERIMENTAL = 8;
    INVNORM = 9;
    PICTURE = 10;
    NORM2 = 11;


class LightSource():

    def __init__(self, intensity=2, position=(1, 1, 6), color=(255, 255, 255)):
        self.intensity = intensity;
        self.position = position;
        self.color = color;

    def apply_lighting(self, position, color, surface_reflectivity):
        # surface reflectivity should be between 0 and 1 (inclusive)
        distance = distance3D(self.position, position);
        #L = self.intensity / (distance * distance);
        L = self.intensity / distance;
        factor = surface_reflectivity * L;
        return tuple(map(lambda color_component: constrain(color_component * factor), color));

    def specular_apply_lighting(self, color, surface_reflectivity, kwargs):
        # I = Ip * (Norm dot (normalized direction to light source)) + Ip * cos^n(a)
        A, B, C, *_ = kwargs["shape"];
        u = vector_between_points(A, B);
        v = vector_between_points(B, C);
        norm = cross_product(u, v);

        distance = distance3D(self.position, kwargs["point"]);
        factor = surface_reflectivity * self.intensity / (distance * distance);
        Ip = self.intensity;
        I = Ip * dot_product(norm, normalize(vector_between_points(A, self.position)));
        return tuple(map(lambda color_component: constrain(color_component * I + factor * color_component), color));

    def new_apply_lighting(self, color, surface_reflectivity, kwargs):
        r, g, b = color;
        dist = distance3D(kwargs["point"], self.position);
        inv_sq_dist = (self.intensity * surface_reflectivity) / (dist * dist + 1);
        nlf = lambda x: min(255, inv_sq_dist * x);
        return nlf(r), nlf(g), nlf(b);
        


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
        elif self.style == Styles.FULL_EXPERIMENTAL:
            self.settings["last mag"] = 0;
            self.settings["last color"] = (0, 128, 255);
        elif self.style == Styles.PICTURE:
            self.image = self.settings["picture"];
            self.sampling_interval = self.image.get_width() // self.settings["anchors"];
            print(self.sampling_interval, "si");

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

##        if (kwargs["i"] + kwargs["j"]) % 2:
##            return m(r), m(g), m(b);
        return constrain(r), constrain(g), constrain(b);

#################################        Experimental Color Styles           ###############################################
    def normal_vector(self, kwargs):
        """ color based on the x and y slopes """
        A, B, C, *_ = kwargs["shape"];
        u = vector_between_points(A, B);
        v = vector_between_points(B, C);
        norm = cross_product(u, v);
        
        if magnitude(norm) == 0:
            angle_1 = angle_2 = angle_3 = pi;
        else:
            angle_1 = angle_between_vectors(norm, I);
            angle_2 = angle_between_vectors(norm, J);
            angle_3 = angle_between_vectors(norm, K);
        return (convert(angle_1), convert(angle_2), convert(angle_3));

    def normal_vector_2(self, kwargs):
        A, B, C, *_ = kwargs["shape"];
        u = vector_between_points(A, B);
        v = vector_between_points(B, C);
        norm = cross_product(u, v);

        X = self.settings["plot"].sortbox
        prod = dot_product(vector_subtract(A, X), norm)
        if prod >= 0:
            return self.settings["color1"]
        return self.settings["color2"]

    def full_experimental(self, kwargs):
        A, B, C, *_ = kwargs["shape"];
        u = vector_between_points(A, B);
        v = vector_between_points(B, C);
        q = magnitude(cross_product(u, v));
        
        if q > self.settings["last mag"]:
            color = color_average(self.settings["last color"],  (123, 12, 31));
        else:
            color = color_average(self.settings["last color"],  (31, 132, 233));
        self.settings["last mag"] = q;
        self.settings["last color"] = color;
        return color;

    def invnorm(self, kwargs):
        """ color revese of normal vector """
##        c = self.normal_vector(kwargs);
##        return 255 - c[0], 255 - c[1], 255 - c[2];
        A, B, C, *_ = kwargs["shape"];
        u = vector_between_points(A, B);
        v = vector_between_points(B, C);
        norm = scalar_multiply(-1, cross_product(u, v));
        
        if magnitude(norm) == 0:
            angle_1 = angle_2 = angle_3 = pi;
        else:
            angle_1 = angle_between_vectors(norm, I);
            angle_2 = angle_between_vectors(norm, J);
            angle_3 = angle_between_vectors(norm, K);
        return (convert(angle_1), convert(angle_2), convert(angle_3));

    def picture(self, kwargs):
        """ style the plot like a picture """
        #print(kwargs["i"] * self.sampling_interval, kwargs["j"] * self.sampling_interval);
        return self.image.get_at((kwargs["i"] * self.sampling_interval - 1, kwargs["j"] * self.sampling_interval - 1));
        
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

        elif self.style == Styles.VERTICAL_STRIPED:
            color = self.vertical_striped(kwargs);
        elif self.style == Styles.HORIZONTAL_STRIPED:
            color = self.horizontal_striped(kwargs);
        elif self.style == Styles.COLOR_SET:
            color = self.color_set(kwargs);
        elif self.style == Styles.NORMAL_VECTOR:
            color = self.normal_vector(kwargs);
        elif self.style == Styles.FULL_EXPERIMENTAL:
            color = self.full_experimental(kwargs);
        elif self.style == Styles.INVNORM:
            color = self.invnorm(kwargs);
        elif self.style == Styles.PICTURE:
            color = self.picture(kwargs);
        elif self.style == Styles.NORM2:
            color = self.normal_vector_2(kwargs)

        if not self.settings.get("apply_lighting"): # accounts for both cases: False/not provided
            return color;
        if self.settings.get("surface_reflectivity"):
            #return self.settings["light_source"].apply_lighting(kwargs["point"], color, self.settings["surface_reflectivity"]);
            #return self.settings["light_source"].specular_apply_lighting(color, self.settings["surface_reflectivity"], kwargs);
            return self.settings["light_source"].new_apply_lighting(color, self.settings["surface_reflectivity"], kwargs);
    
        #return self.apply_lighting(color, kwargs);
        return color;
        
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
    "wavy": ColorStyle(Styles.COLOR_SET, color_set={0: (164, 37, 64), -100: (240, 247, 75), 50: (220, 43, 59), 100: (116, 17, 130), -50: (69, 212, 78)}, step=50),
}
