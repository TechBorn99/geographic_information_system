from tkinter import *
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt

NavigationToolbar2Tk.toolitems = (
        ('Home', 'Reset view', 'home', 'home'),
        (None, None, None, None),
        ('Pan', 'Pan', 'move', 'pan'),
        ('Zoom', 'Zoom In/Out', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Subplots', 'Adjust subplot', 'subplots', 'configure_subplots'),
        ('Save', 'Save figure', 'filesave', 'save_figure'),
    )

raster_file = None


class GeographicInformationSystem:

    root = Tk()

    fig1 = Figure(figsize=(6, 5), dpi=100)
    fig2 = Figure(figsize=(6, 5), dpi=100)

    a = fig2.add_subplot(111)
    ax = fig1.add_subplot(111)

    def __init__(self):

        self.root.title('Geographic information system')
        self.root.iconbitmap(r".\resources\flaticon.ico")

        self.root.geometry("1536x764+0+0")

        self.root.resizable(0, 0)

        self.root.columnconfigure(0, weight=4)
        self.root.columnconfigure(1, weight=4)
        self.root.rowconfigure(0, weight=1)

        self.raster_side = Frame(self.root, bg='lightgoldenrod1')
        self.vector_side = Frame(self.root, bg='lightgoldenrod1')

        self.raster_side.grid(row=0, column=0, sticky="nsew")
        self.vector_side.grid(row=0, column=1, sticky="nsew")

        self.vector_lab = Label(self.vector_side, text='Shapefile', bg='lightgoldenrod1')
        self.vector_lab.place(relx=0.1, rely=0.05)

        self.raster_lab = Label(self.raster_side, text='Raster', bg='lightgoldenrod1')
        self.raster_lab.place(relx=0.1, rely=0.05)

        self.raster_can = FigureCanvasTkAgg(self.fig1, master=self.raster_side)
        self.raster_can.get_tk_widget().place(relx=0.1, rely=0.22, height=500, width=600)

        self.vector_can = FigureCanvasTkAgg(self.fig2, master=self.vector_side)
        self.vector_can.get_tk_widget().place(relx=0.005, rely=0.3, height=535, width=740)

        self.toolbar = NavigationToolbar2Tk(self.raster_can, self.raster_side)
        self.raster_can._tkcanvas.pack(expand=False, side=BOTTOM, fill=BOTH)
        self.toolbar.update()

        self.raster_path = Text(self.raster_side, state=DISABLED)
        self.raster_path.place(relx=0.25, rely=0.1, height=25, width=250)

        self.select_raster_btn = Button(self.raster_side, command=self.select_raster, text='Select a raster file',
                                        bg='lightgoldenrod2',
                                        activebackground='lightgoldenrod3')
        self.select_raster_btn.place(relx=0.10, rely=0.1)

        self.toolbar_vec = NavigationToolbar2Tk(self.vector_can, self.vector_side)
        self.vector_can._tkcanvas.pack(padx=2, expand=False, side=BOTTOM, fill='x')
        self.toolbar_vec.update()

        self.root.mainloop()

    def select_raster(self):
        self.raster_file = filedialog.askopenfilename(initialdir="C:/Users/Desktop",
                                                      filetypes=[('Raster files', '*.tif'),
                                                                 ('Raster files', '*.jpg'),
                                                                 ('Raster files', '*.jfif'),
                                                                 ('Raster files', '*.gif'),
                                                                 ('Raster files', '*.bmp'),
                                                                 ('Raster files', '*.png'),
                                                                 ('Raster files', '*.bat')],
                                                      title='Select a raster file')

        self.raster_path.config(state=NORMAL)
        self.raster_path.delete(1.0, END)
        self.raster_path.insert(END, self.raster_file)
        self.raster_path.config(state=DISABLED)

    def bar(self, progress):
        import time
        progress['value'] = 20

        self.root.update_idletasks()
        time.sleep(0.2)

        progress['value'] = 40
        self.root.update_idletasks()
        time.sleep(0.1)
        progress['value'] = 80
        self.root.update_idletasks()
        time.sleep(0.2)
        progress['value'] = 100

    def reset_bar(self, progress_bar):
        progress_bar['value'] = 0


if __name__ == '__main__':
    start = GeographicInformationSystem()
