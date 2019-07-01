import tkinter as tk;
from Color import preset_styles;
from pygame import Color;
# don't need any of the global imports here.



def set_text(entry, text, clear=True):
    if clear: entry.delete(0, tk.END);
    entry.insert(0, text);


class PlotCreator(tk.Frame):

    """ A tkinter GUI for the grapher. allows user to create plots within the application """

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs);
        self.master = master;
        self.master.title("3D Plotter");
        self.master.iconbitmap("torus2.ico");
        self.update_pending_msg = "NONE";
        self.extra_data = {};

        self.create_widgets();

    def broadcast_to_plotter(self, msg):
        self.update_pending_msg = msg;

    def create_widgets(self):
        """ Create widgets for plot bounds, toggles for axes, angles, tracker, spin, and buttons to draw new plots """
        self.create_plot_bounds();
        self.create_toggles();
        self.create_plot_btns();

    def create_plot_bounds(self):
        """ create the widgets for plot bounds """
        frame = tk.Frame(self.master, borderwidth=3, relief="groove");
        frame.grid(row=0, column=2);
        
        self.x_start = tk.Scale(frame, from_=-10, to=-1, orient=tk.HORIZONTAL, command=lambda event: self.broadcast_to_plotter("UPDATE_PLOT_SETTINGS"));
        self.x_stop = tk.Scale(frame, from_=1, to=10, orient=tk.HORIZONTAL, command=lambda event: self.broadcast_to_plotter("UPDATE_PLOT_SETTINGS"));
        self.y_start = tk.Scale(frame, from_=-10, to=-1, orient=tk.HORIZONTAL, command=lambda event: self.broadcast_to_plotter("UPDATE_PLOT_SETTINGS"));
        self.y_stop = tk.Scale(frame, from_=1, to=10, orient=tk.HORIZONTAL, command=lambda event: self.broadcast_to_plotter("UPDATE_PLOT_SETTINGS"));
        self.z_start = tk.Scale(frame, from_=-10, to=-1, orient=tk.HORIZONTAL, command=lambda event: self.broadcast_to_plotter("UPDATE_PLOT_SETTINGS"));
        self.z_stop = tk.Scale(frame, from_=1, to=10, orient=tk.HORIZONTAL, command=lambda event: self.broadcast_to_plotter("UPDATE_PLOT_SETTINGS"));

        x_start_l = tk.Label(frame, text="x start value: ");
        y_start_l = tk.Label(frame, text="y start value: ");
        z_start_l = tk.Label(frame, text="z start value: ");
        x_stop_l = tk.Label(frame, text="x stop value: ");
        y_stop_l = tk.Label(frame, text="y stop value: ");
        z_stop_l = tk.Label(frame, text="z stop value: ");

        self.x_start.set(-4); self.y_start.set(-4); self.z_start.set(-4);
        self.x_stop.set(4); self.y_stop.set(4); self.z_stop.set(4);

        x_start_l.grid(row=0, column=0);
        x_stop_l.grid(row=0, column=2);
        y_start_l.grid(row=1, column=0);
        y_stop_l.grid(row=1, column=2);
        z_start_l.grid(row=2, column=0);
        z_stop_l.grid(row=2, column=2);
        
        self.x_start.grid(row=0, column=1);
        self.x_stop.grid(row=0, column=3);
        self.y_start.grid(row=1, column=1);
        self.y_stop.grid(row=1, column=3);
        self.z_start.grid(row=2, column=1);
        self.z_stop.grid(row=2, column=3);

    def create_toggles(self):
        """ create toggle buttons for axes, angles, tracker, and spin """
        frame = tk.Frame(self.master, borderwidth=3, relief="groove");
        i = 0;
        for text, broadcast in [("Toggle axes", "TOGGLE_AXES"), ("Toggle angles", "TOGGLE_ANGLES"),
                                ("Toggle tracker", "TOGGLE_TRACKER"), ("Toggle spin", "TOGGLE_SPIN"),
                                ("Reset plots", "RESET_PLOTS")]:
            tk.Button(frame, text=text, command=lambda broadcast=broadcast: self.broadcast_to_plotter(broadcast)).grid(row=0, column=i, padx=2);
            i += 1;
        frame.grid(row=1, column=2);

    def create_plot_btns(self):
        """ create buttons to add functions to the plot """
        frame = tk.Frame(self.master, borderwidth=3, relief="groove");
        frame.grid(row=2, column=2);

        i = 0;
        for text, plot_type in [("New 2D plot", "2D plot"), ("New 3D plot", "3D plot"), ("New parametric function (1 parameter)", "parametric: 1 param"),
                                ("New parametric function (2 parameters)", "parametric: 2 params"), ("New revolution surface", "revolution surface")]:
            tk.Button(frame, text=text, command=lambda plot_type=plot_type: NewPlotWindow(self, plot_type)).grid(row=i, column=0, padx=10, pady=10);
            i += 1;
        

class NewPlotWindow(tk.Toplevel):

    """ Window to input the settings for a new plot """

    def __init__(self, parent, type_):
        tk.Toplevel.__init__(self, parent);
        self.parent = parent;
        self.title(type_);
        self.iconbitmap("torus2.ico");
        self.type = type_;

        self.geometry("400x400+200+200");
        self.deiconify();

        if self.type == "2D plot":
            self.plot2d();
        elif self.type == "3D plot":
            self.plot3d();
        elif self.type == "parametric: 1 param":
            self.para1param();
        elif self.type == "parametric: 2 params":
            self.para2params();
        elif self.type == "revolution surface":
            self.revsurf();

    def add_data(self, name, data):
        """ add data to be broadcast to the plotter """
        self.parent.extra_data[name] = data;

    def color_style(self, row=0, solid_only=False):
        """ Draw the widgets for ColorStyle configuring """
        cs_frame = tk.Frame(self, borderwidth=3, relief="groove");
        dframe = tk.Frame(cs_frame);
        dframe.grid(row=2);
        tk.Label(cs_frame, text="Color Style").grid(row=0, sticky=tk.W);
        cs_frame.grid(row=row, sticky=tk.W);
        
        self.style = tk.StringVar(dframe, value="select...");
        if solid_only:
            self.style.set("solid");
            self.color_style_set(dframe, row+1);
        else:
            tk.OptionMenu(cs_frame, self.style, "solid", "checkerboard", "world lighting", "gradient", "value based",
                          "vertical striped", "horizontal striped", "color set", "preset",
                          command=lambda event: self.color_style_set(dframe, row+1)).grid(row=1, sticky=tk.W);

    def color_box(self, frame, row, text="Color: ", data_name="fill color"):
        """ create widgets for a color picker """
        def on_color_select(cbox, canv):
            nonlocal self;
            color = tk.colorchooser.askcolor(initialcolor="red",  parent=self)[1];
            cbox.configure(text=color);
            canv.configure(background=color);
            self.add_data(data_name, Color(color)[0:3]);
            
        color_box = tk.Label(frame, text="#ff0000", borderwidth=3, relief="flat");
        color_box.grid(row=row, column=1);
        tk.Label(frame, text=text).grid(row=row);
        color_preview = tk.Canvas(frame, width=20, height=20);
        color_preview.grid(row=row, column=3);
        tk.Button(frame, text="select color", command=lambda: on_color_select(color_box, color_preview)).grid(row=row, column=2);

    def color_style_set(self, frame, row):
        """ Set the widgets for a specific ColorStyle """
        value = self.style.get();
        self.add_data("plot type", value);
        for child in frame.winfo_children():
            child.destroy();

        if value == "solid":
            self.color_box(frame, row);
        elif value in ("checkerboard", "gradient", "vertical striped", "horizontal striped"):
            cbox1 = self.color_box(frame, row, text="Color 1: ", data_name="color 1");
            cbox2 = self.color_box(frame, row+1, text="Color 2: ", data_name="color 2");
        elif value in ("world lighting", "value based"):
            self.color_box(frame, row, text="Base color: ", data_name="base color");
        elif value == "color set":
            self.color_box(frame, row, text="Color 1: ", data_name="color 1");
            self.color_box(frame, row+1, text="Color 2: ", data_name="color 2");
            self.color_box(frame, row+2, text="Color 3: ", data_name="color 3");
            self.color_box(frame, row+3, text="Color 4: ", data_name="color 4");
            self.color_box(frame, row+4, text="Color 5: ", data_name="color 5");
        elif value == "preset":
            tk.Label(frame, text="select preset: ").grid(row=row);
            preset = tk.StringVar(frame, value="tmp");
            tk.OptionMenu(frame, preset, *sorted(preset_styles.keys()), command=lambda event: self.add_data("plot type", preset.get())).grid(row=row, column=1);

    def on_complete(self, data, broadcast):
        """ Send the neccesary data to the plotter and notify it that a new plot should be created. Then destroy the window """
        for name, data in data.items():
            self.add_data(name, data);
        self.parent.broadcast_to_plotter(broadcast);
        self.destroy();

    def create_function_boxes(self, labels, row=0):
        """ create the input boxes for the functions """
        frame = tk.Frame(self, borderwidth=3, relief="groove");
        functions = [];
        for i, label in enumerate(labels):
            tk.Label(frame, text=label).grid(row=i, column=0);
            func = tk.Entry(frame);
            func.grid(row=i, column=1);
            functions.append(func);
        frame.grid(row=0, sticky=tk.W);
        return functions;

    def plot2d(self):
        """ Add a new 2D function """
        self.color_style(row=1, solid_only=True);
        strings = self.create_function_boxes(["f(x)="]);
        tk.Button(self, text="Add to plot", command=lambda: self.on_complete({"function {}".format(i+1): strings[i].get() for i in range(len(strings))}, "NEW_2D_FUNCTION")).grid(row=2);

    def plot3d(self):
        """ Add a new 3D function """
        self.color_style(row=1);
        strings = self.create_function_boxes(["f(x,y)="]);
        tk.Button(self, text="Add to plot", command=lambda: self.on_complete({"function {}".format(i+1): strings[i].get() for i in range(len(strings))}, "NEW_3D_FUNCTION")).grid(row=2);
        
    def para1param(self):
        """ Add a new 1 parameter parametric function """
        self.color_style(row=1, solid_only=True);
        strings= self.create_function_boxes(["x(t)=", "y(t)=", "z(t)="]);
        tk.Button(self, text="Add to plot", command=lambda: self.on_complete({"function {}".format(i+1): strings[i].get() for i in range(len(strings))}, "NEW_PARAM1_FUNCTION")).grid(row=2);

    def para2params(self):
        """ Add a new 2 parameter parametric function """
        self.color_style(row=1);
        strings = self.create_function_boxes(["x(u,v)=", "y(u,v)=", "z(u,v)="]);
        tk.Button(self, text="Add to plot", command=lambda: self.on_complete({"function {}".format(i+1): strings[i].get() for i in range(len(strings))}, "NEW_PARAM2_FUNCTION")).grid(row=2);

    def revsurf(self):
        """ Add a new surface of revolution """
        self.color_style(row=1);
        strings = self.create_function_boxes(["f(x)="]);
        tk.Button(self, text="Add to plot", command=lambda: self.on_complete({"function {}".format(i+1): strings[i].get() for i in range(len(strings))}, "NEW_REVOLUTION_SURFACE")).grid(row=2);
