from tkinter import *
from tkinter.ttk import Progressbar
import shapefile
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from descartes import PolygonPatch


class GeographicInformationSystem:

    root = Tk()

    fig1 = Figure(figsize=(6, 5), dpi=100)
    fig2 = Figure(figsize=(6, 5), dpi=100)

    a = fig2.add_subplot(111)
    ax = fig1.add_subplot(111)
    raster_file = None
    vector_loaded = False
    raster_loaded = False

    NavigationToolbar2Tk.toolitems = (
        ('Home', 'Reset view', 'home', 'home'),
        (None, None, None, None),
        ('Pan', 'Pan', 'move', 'pan'),
        ('Zoom', 'Zoom In/Out', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Subplots', 'Adjust subplot', 'subplots', 'configure_subplots'),
        ('Save', 'Save figure', 'filesave', 'save_figure'),
    )

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

        self.progress_raster = Progressbar(self.raster_side, orient=HORIZONTAL, length=250, mode='determinate')
        self.progress_raster.place(relx=0.25, rely=0.165)
        self.toolbar_vec.update()
        self.load_raster_btn = Button(self.raster_side, command=self.load_raster, text='Load a raster file',
                                      bg='lightgoldenrod2',
                                      activebackground='lightgoldenrod3')
        self.load_raster_btn.place(relx=0.10, rely=0.16)

        self.select_vector_btn = Button(self.vector_side, command=self.select_vector, text='Select a vector file',
                                        bg='lightgoldenrod2',
                                        activebackground='lightgoldenrod3')
        self.select_vector_btn.place(relx=0.10, rely=0.1)
        self.vector_path = Text(self.vector_side, state=DISABLED)
        self.vector_path.place(relx=0.25, rely=0.1, height=25, width=250)
        self.load_vector_btn = Button(self.vector_side, command=self.load_vector, text='Load a vector file',
                                      bg='lightgoldenrod2',
                                      activebackground='lightgoldenrod3')
        self.load_vector_btn.place(relx=0.10, rely=0.16)
        self.progress_vector = Progressbar(self.vector_side, orient=HORIZONTAL, length=250, mode='determinate')
        self.progress_vector.place(relx=0.25, rely=0.165)

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
        self.raster_loaded = False

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

    def load_raster(self):

        if self.raster_file is None:
            messagebox.showerror(title='Error!',
                                 message="No file for loading was selected!\nPlease select a file, then try again!")
        else:
            self.ax.cla()

            import rasterio as rio
            from rasterio.plot import show

            self.fig1.subplots_adjust(bottom=0, right=1, top=1, left=0, wspace=0, hspace=0)
            with rio.open(r'{}'.format(self.raster_file)) as src_plot:
                show(src_plot, ax=self.ax, cmap='gist_gray')
            plt.close()

            self.ax.set(title="", xticks=[], yticks=[])
            self.ax.spines["top"].set_visible(False)
            self.ax.spines["right"].set_visible(False)
            self.ax.spines["left"].set_visible(False)
            self.ax.spines["bottom"].set_visible(False)

            self.bar(self.progress_raster)

            self.raster_can.draw()

            self.reset_bar(self.progress_raster)

            self.raster_loaded = True

    def select_vector(self):
        self.vector_file = filedialog.askopenfilename(initialdir="C:/Users/Desktop",
                                                      filetypes=[('Vector files', '*.shp')],
                                                      title='Select a vector file')
        self.vector_path.config(state=NORMAL)
        self.vector_path.delete(1.0, END)

        self.vector_path.insert(END, self.vector_file)

        self.vector_path.config(state=DISABLED)
        self.vector_loaded = False

    def load_vector(self):
        if self.vector_file == '':
            messagebox.showerror(title='Error!',
                                 message="No file for loading was selected!\nPlease select a file, then try again!")
        else:
            self.a.cla()

            self.vector = gpd.read_file(self.vector_file, crs="EPSG:4326")
            self.vector.plot()
            sf = shapefile.Reader(self.vector_file)
            if all(row['geometry'].geom_type == 'Point' or row['geometry'].geom_type == 'MultiPoint' for index, row in
                   self.vector.iterrows()):
                points = [np.array((shape.shape.points[0][0], shape.shape.points[0][1])) for shape in sf.shapeRecords()]
                self.a.plot([point[0] for point in points], [point[1] for point in points], 'o', color='red',
                            markersize=4)
                self.vector_loaded = True
            elif all(row['geometry'].geom_type == 'LineString' or row['geometry'].geom_type == 'MultiLineString' for
                     index, row in self.vector.iterrows()):
                for line in self.vector['geometry']:
                    if line.geom_type == 'MultiLineString':
                        for li in line:
                            self.a.plot(*li.xy)
                    elif line.geom_type == 'LineString':
                        self.a.plot(*line.xy)
                self.vector_loaded = True
            elif all(
                    row['geometry'].geom_type == 'Polygon' or row['geometry'].geom_type == 'MultiPolygon' for index, row
                    in self.vector.iterrows()):
                for polygon in self.vector['geometry']:
                    if polygon.geom_type == 'MultiPolygon':
                        for pol in polygon:
                            self.a.plot(*pol.exterior.xy)
                            patch = PolygonPatch(pol, alpha=0.5)
                            self.a.add_patch(patch)
                    elif polygon.geom_type == 'Polygon':
                        self.a.plot(*polygon.exterior.xy)
                self.vector_loaded = True
            else:
                messagebox.showerror(title='Error!',
                                     message="Unsupported geometry detected...")
                return

            self.bar(self.progress_vector)

            self.vector_can.draw()
            self.reset_bar(self.progress_vector)


if __name__ == '__main__':
    start = GeographicInformationSystem()
