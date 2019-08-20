import tkinter as tk;
from tkinter.colorchooser import askcolor;
from tkinter.messagebox import showinfo;
from Color import preset_styles;
from CAS import Parser;
from pygame import Color;
# we don't need any of the global imports here.



def set_text(entry, text, clear=True):
    if clear: entry.delete(0, tk.END);
    entry.insert(0, text);


class PlotCreator(tk.Frame):

    """ A tkinter GUI for the grapher. allows user to create plots within the application """

    def __init__(self, master, *args, x_start=-4, x_stop=4, y_start=-4, y_stop=4, z_start=-4, z_stop=4, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs);
        self.master = master;
        self.master.title("3D Plotter");
        #self.master.iconbitmap("img/torus2.ico");
        self.update_pending_msg = "NONE";
        self.extra_data = {};

        self.x_start, self.x_stop = x_start, x_stop;
        self.y_start, self.y_stop = y_start, y_stop;
        self.z_start, self.z_stop = z_start, z_stop;

        self.create_widgets();

    def broadcast_to_plotter(self, msg):
        """ tell the plotter it needs to update """
        self.update_pending_msg = msg;

    def show_message(self, msg, error=False):
        """ show a message to the user """
        showinfo("", "Error: " * error + msg);

    def create_widgets(self):
        """ Create widgets for plot bounds, toggles for axes, angles, tracker, spin, and buttons to draw new plots """
        tk.Button(self.master, text="Plot settings", command=lambda: PlotSettingsWindow(self)).grid(row=4,column=2);
        self.create_function_frame();
        self.create_plot_btns();

    def create_function_frame(self):
        """ create the frame where the functions on the plot are displayed """
        self.function_frame = tk.Frame(self.master, borderwidth=3, relief="groove", background="#FFFFFF", height=400);
        tk.Label(self.function_frame, text="Functions currently on the graph: ").grid(row=0, column=0);
        self.function_frame_row = 1;
        self.function_frame.grid(row=0, column=2, rowspan=6, sticky=tk.N);

    def reset_function_frame(self):
        """ reset the function frame """
        self.function_frame.destroy();
        self.create_function_frame();

    def add_to_function_frame(self, function):
        """ add another line to the function display frame """
        tk.Label(self.function_frame, text=function).grid(row=self.function_frame_row, column=0, sticky=tk.W);
        self.function_frame_row += 1;

    def create_plot_btns(self):
        """ create buttons to add functions to the plot """
        frame = tk.Frame(self.master, borderwidth=3, relief="groove");
        frame.grid(row=3, column=2);

        i = 0;
        for text, plot_type in [("New 2D plot", "2D plot"), ("New 3D plot", "3D plot"), ("New parametric function (1 parameter)", "parametric: 1 param"),
                                ("New parametric function (2 parameters)", "parametric: 2 params"), ("New revolution surface", "revolution surface"),
                                ("New function of cylindrical coordinates", "cylindrical function"), ("New function of spherical coordinates", "spherical function"),
                                ("New vector field", "vector field")]:
            tk.Button(frame, text=text, command=lambda plot_type=plot_type: NewPlotWindow(self, plot_type)).grid(row=i, column=0, padx=10, pady=5);
            i += 1;
        tk.Button(frame, text="Compile new function", command=lambda: DefineFunctionWindow(self)).grid(row=i, column=0, pady=5);


class PlotSettingsWindow(tk.Toplevel):

    """ Window to input the settings for the plot view """

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent);
        self.parent = parent;
        self.title("Plot settings");
        #self.iconbitmap("img/torus2.ico");
        self.create_widgets();

    def create_widgets(self):
        """ create all the window's widgets """
        self.create_plot_bounds();
        self.create_toggles();
        tk.Button(self, text="Close", command=self.destroy).grid(row=2, column=0);

    def create_plot_bounds(self):
        """ create the widgets for plot bounds """
        def onchange(event, name):
            setattr(self.parent, name, int(event));
            self.parent.broadcast_to_plotter("UPDATE_PLOT_SETTINGS");

        frame = tk.Frame(self, borderwidth=3, relief="groove");
        frame.grid(row=0, column=0, padx=10, pady=10);

        widget_data = (
            ("x_start", True,  "x start value: ", 0, 0),
            ("x_stop",  False, "x stop value: ",  0, 2),
            ("y_start", True,  "y start value: ", 1, 0),
            ("y_stop",  False, "y stop value: ",  1, 2),
            ("z_start", True,  "z start value: ", 2, 0),
            ("z_stop",  False, "z stop value: ",  2, 2)
        );

        for name, start, text, row, col in widget_data:
            from_, to = (-10, -1) if start else (1, 10);
            widget = tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, command=lambda event, name=name: onchange(event, name));
            label = tk.Label(frame, text=text);

            label.grid(row=row, column=col);
            widget.grid(row=row, column=col+1);

            widget.set(getattr(self.parent, name));

    def create_toggles(self):
        """ create toggle buttons for axes, angles, tracker, and spin """
        frame = tk.Frame(self, borderwidth=3, relief="groove");
        i = 0;
        for text, broadcast in [("Toggle axes", "TOGGLE_AXES"), ("Toggle angles", "TOGGLE_ANGLES"),
                                ("Toggle tracker", "TOGGLE_TRACKER"), ("Toggle spin", "TOGGLE_SPIN"),
                                ("Toggle frame", "TOGGLE_CUBE"), ("Reset plots", "RESET_PLOTS")]:
            tk.Button(frame, text=text, command=lambda broadcast=broadcast: self.parent.broadcast_to_plotter(broadcast)).grid(row=0, column=i, padx=2);
            i += 1;
        frame.grid(row=1, column=0, pady=10, padx=10);


class DefineFunctionWindow(tk.Toplevel):

    """ Window for defining a new function """

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent);
        self.parent = parent;
        self.title("Define a function");
        #self.iconbitmap("img/torus2.ico")

        self.geometry("400x400");
        self.deiconify();
        self.radio_btn_state = tk.IntVar();
        self.radio_btn_state.initialize(1);
        self.function_entry_state = tk.StringVar();
        self.function_label_text = tk.StringVar(value="f(x)=");
        self.function_name_state = tk.StringVar();
        self.create_widgets();

    def create_widgets(self):
        """ add all widgets needed for the window """
        self.msg = tk.StringVar(self, value="Define a new function");
        tk.Label(self, textvariable=self.msg).grid(row=0, column=0);
        tk.Radiobutton(self, text="one variable", variable=self.radio_btn_state, value=1, command=lambda: self.function_label_text.set("f(x)=")).grid(row=1, column=0);
        tk.Radiobutton(self, text="two variables", variable=self.radio_btn_state, value=2, command=lambda: self.function_label_text.set("f(x,y)=")).grid(row=1, column=1);
        tk.Radiobutton(self, text="three variables", variable=self.radio_btn_state, value=3, command=lambda: self.function_label_text.set("f(x,y,z)=")).grid(row=1, column=2);
        tk.Label(self, text="Name: ").grid(row=2, column=0, sticky=tk.W);
        tk.Entry(self, textvariable=self.function_name_state).grid(row=2, column=1, sticky=tk.W);
        tk.Label(self, textvariable=self.function_label_text).grid(row=3, column=0, sticky=tk.W);
        tk.Entry(self, textvariable=self.function_entry_state).grid(row=3, column=1, sticky=tk.W);
        tk.Button(self, text="Add", command=self.on_close).grid(row=4, column=0, sticky=tk.W);

    def on_close(self):
        """ send data to the plotter and tell it a new function should be created. then destroy the window """
        function = self.function_entry_state.get();
        function_name = self.function_name_state.get();
        rbtn_state = self.radio_btn_state.get();

        if function and function_name:
            self.add_data("function", function);
            self.add_data("num vars", rbtn_state);
            self.add_data("function name", function_name);
            self.parent.broadcast_to_plotter("NEW_COMPILED_FUNCTION");
            self.destroy();
        else:
            self.show_message("function box and name box cannot be blank", True);
            return;

    def add_data(self, name, data):
        """ add data to be broadcast to the plotter """
        self.parent.extra_data[name] = data;

    def show_message(self, msg, error=False):
        """ display a message to the user """
        self.msg.set("Error: " * error + msg);

class NewPlotWindow(tk.Toplevel):

    """ Window to input the settings for a new plot """

    def __init__(self, parent, type_):
        tk.Toplevel.__init__(self, parent);
        self.parent = parent;
        self.title(type_);
        #self.iconbitmap("img/torus2.ico");
        self.type = type_;

        self.geometry("400x400+200+200");
        self.deiconify();

        if self.type == "2D plot":
            self.set_up_configurations(["f(x)="], "NEW_2D_FUNCTION", solid_only=True);
        elif self.type == "3D plot":
            self.set_up_configurations(["f(x,y)="], "NEW_3D_FUNCTION");
        elif self.type == "parametric: 1 param":
            self.set_up_configurations(["x(t)=", "y(t)=", "z(t)="], "NEW_PARAM1_FUNCTION", solid_only=True);
        elif self.type == "parametric: 2 params":
            self.set_up_configurations(["x(u,v)=", "y(u,v)=", "z(u,v)="], "NEW_PARAM2_FUNCTION");
        elif self.type == "revolution surface":
            self.set_up_configurations(["f(x)="], "NEW_REVOLUTION_SURFACE");
        elif self.type == "cylindrical function":
            self.set_up_configurations(["r(z,t)="], "NEW_CYL_FUNCTION");
        elif self.type == "spherical function":
            self.set_up_configurations(["r(t,p)="], "NEW_SPH_FUNCTION");
        elif self.type == "vector field":
            self.set_up_configurations(["x(x,y,z)=", "y(x,y,z)=", "z(x,y,z)="], "NEW_VECTOR_FIELD");

    def add_data(self, name, data):
        """ add data to be broadcast to the plotter """
        self.parent.extra_data[name] = data;

    def light_source(self, row=0):
        """ draw the widgets for light source configuring """
        data = (
            ("x", self.parent.x_start, self.parent.x_stop, "light_source_x", 0),
            ("y", self.parent.y_start, self.parent.y_stop, "light_source_y", 0),
            ("z", self.parent.z_start, self.parent.z_stop, "light_source_z", 6)
        );

        self.light_source_frame = tk.Frame(self, borderwidth=3, relief="groove");
        self.light_source_frame.grid(row=row, sticky=tk.W);

        tk.Label(self.light_source_frame, text="Light source position");
        row = 1;
        for text, from_, to, name, default in data:
            start = min(-8, from_);
            stop = max(8, to);

            widget = tk.Scale(self.light_source_frame, from_=start, to=stop, orient=tk.HORIZONTAL, command=lambda event, name=name: self.add_data(name, int(event)));
            label = tk.Label(self.light_source_frame, text=text);

            label.grid(row=row);
            widget.grid(row=row, column=1);
            widget.set(default);
            row += 1;

    def destroy_light_source(self):
        """ remove the widgets for light source configuring """
        if hasattr(self, "light_source_frame"):
            self.light_source_frame.destroy();

    def color_style(self, row=0, solid_only=False):
        """ Draw the widgets for ColorStyle configuring """
        def on_check(lighting):
            nonlocal row;
            value = lighting.get();
            self.add_data("apply_lighting", value);
            if value: self.light_source(row+1);
            else: self.destroy_light_source();

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
            tk.OptionMenu(cs_frame, self.style, "solid", "checkerboard", "gradient",
                          "vertical striped", "horizontal striped", "color set", "preset",
                          command=lambda event: self.color_style_set(dframe, row+1)).grid(row=1, sticky=tk.W);

            lighting = tk.IntVar();
            tk.Checkbutton(cs_frame, text="Apply lighting", var=lighting,
                           command=lambda lighting=lighting: on_check(lighting)).grid(row=3, sticky=tk.W);

    def color_box(self, frame, row, text="Color: ", data_name="fill color"):
        """ create widgets for a color picker """
        def on_color_select(cbox, canv, ask=True):
            nonlocal self;
            if ask: color = askcolor(initialcolor="red",  parent=self)[1];
            else: color="#ff0000";
            if not color: return;

            cbox.configure(text=color);
            canv.configure(background=color);
            self.add_data(data_name, Color(color)[0:3]);

        color_box = tk.Label(frame, text="#ff0000", borderwidth=3, relief="flat");
        color_box.grid(row=row, column=1);
        tk.Label(frame, text=text).grid(row=row);
        color_preview = tk.Canvas(frame, width=20, height=20);
        color_preview.grid(row=row, column=3);
        on_color_select(color_box, color_preview, ask=False);
        tk.Button(frame, text="select color", command=lambda: on_color_select(color_box, color_preview, ask=True)).grid(row=row, column=2);

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
        elif value == "color set":
            self.color_box(frame, row, text="Color 1: ", data_name="color 1");
            self.color_box(frame, row+1, text="Color 2: ", data_name="color 2");
            self.color_box(frame, row+2, text="Color 3: ", data_name="color 3");
            self.color_box(frame, row+3, text="Color 4: ", data_name="color 4");
            self.color_box(frame, row+4, text="Color 5: ", data_name="color 5");
        elif value == "preset":
            tk.Label(frame, text="select preset: ").grid(row=row);
            preset = tk.StringVar(frame, value="tmp");
            self.add_data("plot type", preset.get());
            tk.OptionMenu(frame, preset, *sorted(preset_styles.keys()), command=lambda event: self.add_data("plot type", preset.get())).grid(row=row, column=1);

    def on_complete(self, data, broadcast):
        """ Send the neccesary data to the plotter and notify it that a new plot should be created. Then destroy the window """
        for name, data_item in data.items():
            if name.startswith("function") and not len(data_item):
                self.show_message("Function box cannot be blank!", error=True);
                return;
            self.add_data(name, data_item);
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
        frame.grid(row=row, sticky=tk.W);
        return functions;

    def show_message(self, msg, error=False):
        """ display a message to the user """
        self.msg.set("Error: " * error + msg);

    def set_up_configurations(self, function_boxes, broadcast_msg, solid_only=False):
        """ Set up the widgets for adding a new function of any type """
        self.add_data("plot type", "solid");
        self.add_data("fill color", (255, 0, 0));

        frame = tk.Frame(self, borderwidth=3, relief="groove");
        frame.grid(row=0, column=0);
        self.msg = tk.StringVar(frame, value="Add a graph to the plot");
        tk.Label(frame, textvariable=self.msg).grid(row=0);

        strings = self.create_function_boxes(function_boxes, row=1);
        self.color_style(row=2, solid_only=solid_only);
        tk.Button(self, text="Add to plot", command=lambda: self.on_complete({"function {}".format(i+1): strings[i].get() for i in range(len(strings))}, broadcast_msg)).grid(row=4);
