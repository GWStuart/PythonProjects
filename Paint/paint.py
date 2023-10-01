from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter import filedialog
from PIL import ImageGrab
# todo shift for shape tools, fix bug, flood fill


class Paint:
    def __init__(self):
        self.shift = False
        self.colour = "black"
        self.current_shape_id = 0
        self.old_x = None
        self.old_y = None
        self.eraser_on = False
        self.load_img = None
        self.lines = list()

        self.root = Tk()
        self.popup = None
        # self.root.state('zoomed')
        self.root.title("Paint")
        # self.root.iconbitmap("icon.ico")

        # creates shape tools menu
        self.shape_tools_frame = Frame(self.root)
        options = ["line", "rectangle", "circle", "triangle"]
        self.var = StringVar(self.shape_tools_frame)
        self.var.set(options[0])
        self.shape_select_btn = OptionMenu(self.shape_tools_frame, self.var, *options)
        self.shape_select_btn.grid(row=0, column=0)
        self.select_btn = Button(self.shape_tools_frame, text="select", command=self.shape_tool)
        self.select_btn.grid(row=0, column=1)

        self.shape_tools_frame.grid(row=0, column=1)

        self.draw_btn = Button(self.root, text="Pen", command=self.draw_tool)
        self.draw_btn.grid(row=0, column=2)

        self.erase_btn = Button(self.root, text="Eraser", command=self.erase_tool)
        self.erase_btn.grid(row=0, column=3)

        self.erase_all_btn = Button(self.root, text="Erase All", command=self.erase_all)
        self.erase_all_btn.grid(row=0, column=4)

        self.colour_btn = Button(self.root, text="Colour", command=self.choose_colour)
        self.colour_btn.grid(row=0, column=5)

        self.size_slider = Scale(self.root, from_=1, to=50, orient=HORIZONTAL)
        self.size_slider.grid(row=0, column=6)

        self.colour_canvas = Canvas(self.root, width=100, height=35)
        self.colour_canvas.create_text(38, 18, text="Colour: ", font="none 12 bold")
        self.colour_canvas.create_rectangle(70, 5, 98, 33, fill=self.colour)
        self.colour_canvas.grid(row=0, column=0)

        self.save_btn = Button(self.root, text="save", command=self.save_drawing)
        self.save_btn.grid(row=0, column=7)

        self.undo_btn = Button(self.root, text="undo", command=self.undo_line)
        self.undo_btn.grid(row=0, column=8)

        self.c = Canvas(self.root, width=1250, height=580, bg="white", cursor="crosshair")
        self.c.grid(row=1, column=0, columnspan=9, padx=10)

        self.active_button = self.draw_btn
        self.active_button.config(relief=SUNKEN)

        self.coord = Label(self.root, text="Coords: " + str(self.c.winfo_pointerxy()))
        self.coord.grid(row=2, column=0, sticky=W)

        self.root.bind("<KeyPress-Shift_L>", self.shift_true)
        self.root.bind("<KeyRelease-Shift_L>", self.shift_false)
        self.c.bind("<B1-Motion>", self.paint)
        self.c.bind("<Motion>", self.motion)
        self.c.bind("<ButtonRelease-1>", self.reset)

        self.root.mainloop()

    def shift_true(self, _):
        self.shift = True

    def shift_false(self, _):
        self.shift = False

    def draw_tool(self):
        self.activate_button(self.draw_btn)

    def shape_tool(self):
        self.activate_button(self.select_btn)

    @staticmethod
    def save_drawing():
        file = filedialog.asksaveasfilename(initialdir="/", title="Choose a location",
                                            filetypes=(("png files", ".png"), ("all files", "*.*")))
        file += ".png"
        x1 = 18
        y1 = 101
        x2 = 18 + 1875
        y2 = 101 + 870
        ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(file)

    def erase_tool(self):
        self.activate_button(self.erase_btn, True)

    def choose_colour(self):
        self.colour = askcolor()[1]
        self.colour_canvas.create_rectangle(70, 5, 98, 33, fill=self.colour)

    def motion(self, event):
        self.coord.grid_forget()
        self.coord = Label(self.root, text="Coords: " + str(event.x) + ", " + str(event.y))
        self.coord.grid(row=2, column=0, sticky=W)

    def erase_all(self):
        self.popup = Tk()
        self.popup.title("")
        self.popup.resizable(False, False)
        self.popup.iconbitmap("icon.ico")

        Label(self.popup, text="Are you sure you want to erase all?").grid(row=0, column=0, columnspan=2)
        Button(self.popup, text="yes", command=lambda: self.erase(self.popup)).grid(row=1, column=0)
        Button(self.popup, text="no", command=self.popup.destroy).grid(row=1, column=1)

        self.popup.geometry("188x47+546+200")

    def activate_button(self, button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        button.config(relief=SUNKEN)
        self.active_button = button
        self.eraser_on = eraser_mode

    def erase(self, popup):
        popup.destroy()
        self.c.delete("all")

    def paint(self, event):
        self.motion(event)
        if self.active_button == self.select_btn:
            self.draw_shape(event)
        else:
            width = self.size_slider.get()
            if self.eraser_on:
                colour = "white"
            else:
                colour = self.colour

            if self.old_x and self.old_y:
                line_id = self.c.create_line(event.x, event.y, self.old_x, self.old_y, width=width, fill=colour,
                                             capstyle=ROUND, smooth=TRUE, splinesteps=36)
                self.lines.append(line_id)
            else:
                self.lines.append(0)

            self.old_x = event.x
            self.old_y = event.y

    def reset(self, _):
        self.old_x = None
        self.old_y = None
        if self.active_button == self.select_btn and self.current_shape_id != 0:
            self.lines.append(self.current_shape_id)
            self.current_shape_id = 0

    def undo_line(self):
        if len(self.lines) > 0:
            i = len(self.lines) - 1
            while self.lines[i] != 0:
                self.c.delete(self.lines[i])
                self.lines.pop(i)
                i -= 1
            self.lines.pop(i)

    def draw_shape(self, event):
        if self.current_shape_id != 0:
            self.c.delete(self.current_shape_id)
        if self.old_x and self.old_y:
            if self.shift:
                self.draw_shape_shift(event)
            else:
                if self.var.get() == "line":
                    self.current_shape_id = self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                                                               fill=self.colour, width=self.size_slider.get(),
                                                               capstyle=ROUND)
                elif self.var.get() == "rectangle":
                    self.current_shape_id = self.c.create_rectangle(self.old_x, self.old_y, event.x, event.y,
                                                                    outline=self.colour, width=self.size_slider.get())
                elif self.var.get() == "circle":
                    self.current_shape_id = self.c.create_oval(self.old_x, self.old_y, event.x, event.y,
                                                               outline=self.colour, width=self.size_slider.get())
                elif self.var.get() == "triangle":
                    self.current_shape_id = self.c.create_polygon(self.old_x, self.old_y, event.x, event.y,
                                                                  self.old_x - (event.x - self.old_x), event.y, fill="",
                                                                  outline=self.colour, width=self.size_slider.get())
        else:
            self.old_x = event.x
            self.old_y = event.y
            self.lines.append(0)

    def draw_shape_shift(self, event):
        if self.var.get() == "line":
            self.current_shape_id = self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                                                       fill=self.colour, width=self.size_slider.get(),
                                                       capstyle=ROUND)
        elif self.var.get() == "rectangle":
            self.current_shape_id = self.c.create_rectangle(self.old_x, self.old_y, event.x, event.y,
                                                            outline=self.colour, width=self.size_slider.get())
        elif self.var.get() == "circle":
            self.current_shape_id = self.c.create_oval(self.old_x, self.old_y, event.x, event.y,
                                                       outline=self.colour, width=self.size_slider.get())
        elif self.var.get() == "triangle":
            self.current_shape_id = self.c.create_polygon(self.old_x, self.old_y, event.x, event.y,
                                                          self.old_x - (event.x - self.old_x), event.y, fill="",
                                                          outline=self.colour, width=self.size_slider.get())


if __name__ == '__main__':
    Paint()
