from tkinter import *
from tkinter.ttk import Progressbar
import shapefile
from geopandas import GeoDataFrame, points_from_xy
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from descartes import PolygonPatch
from shapely.geometry import Point
import pandas as pd
from scipy.spatial.qhull import Delaunay, ConvexHull
from sklearn.neighbors import BallTree
import math
import geopy.distance


class GeographicInformationSystem:

    root = Tk()

    fig1 = Figure(figsize=(6, 5), dpi=100)
    fig2 = Figure(figsize=(6, 5), dpi=100)

    a = fig2.add_subplot(111)
    ax = fig1.add_subplot(111)
    raster_file = None
    vector_file = None
    vector_loaded = False
    raster_loaded = False
    vector = None
    csv_destination = ''
    num_of_clicks_raster = 0
    connection_raster = None
    distance_ras = 0
    point1_ras = point2_ras = None

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
        self.vector_attributes_text = Text(self.vector_side, state=DISABLED, width=72, height=3)
        self.vector_attributes_text.place(relx=0.11, rely=0.22)
        self.display_vector_data = Button(self.vector_side, command=self.show_vector_data,
                                          text='Display\nvector\ndata',
                                          bg='lightgoldenrod2',
                                          activebackground='lightgoldenrod3')
        self.display_vector_data.place(relx=0.02, rely=0.22)
        self.clear_vector_data = Button(self.vector_side, command=self.clear_vector_data,
                                        text='Clear\nvector\ndata',
                                        bg='lightgoldenrod2',
                                        activebackground='lightgoldenrod3')
        self.clear_vector_data.place(relx=0.89, rely=0.22)
        load_csv_image = PhotoImage(file=r'.\resources\load_csv.gif')
        self.load_csv_btn = Button(self.raster_side, image=load_csv_image, command=self.load_csv_data)
        self.load_csv_btn.place(relx=0.0, rely=0.0, width=32, height=32)
        delaunay_triangulation_image = PhotoImage(file=r'.\resources\delaunay_triangulation_icon.gif')
        self.delaunay_triangulation_btn = Button(self.raster_side, image=delaunay_triangulation_image,
                                                 command=self.delaunay_triangulation)
        self.delaunay_triangulation_btn.place(relx=0.045, rely=0.0, width=32, height=32)
        polygon_image = PhotoImage(file=r'.\resources\polygon.gif')
        self.convex_hull_polygon_btn = Button(self.raster_side, image=polygon_image,
                                              command=self.convex_hull_polygon)
        self.convex_hull_polygon_btn.place(relx=0.09, rely=0.0, width=32, height=32)
        nearest_neighbor_search_image = PhotoImage(file=r'.\resources\nearest_neighbor.gif')
        self.nearest_neighbor_search_btn = Button(self.raster_side, image=nearest_neighbor_search_image,
                                                  command=self.nearest_neighbor_input)
        self.nearest_neighbor_search_btn.place(relx=0.135, rely=0.0, width=32, height=32)

        ruler_image = PhotoImage(file=r'.\resources\ruler.gif')
        self.calculate_distance_btn = Button(self.raster_side, image=ruler_image,
                                             command=self.calculate_distance_raster)
        self.calculate_distance_btn.place(relx=0.03, rely=0.25, width=32, height=32)

        self.raster_distance_lbl = Label(self.raster_side, text='', bg='lightgoldenrod1')
        self.raster_distance_lbl.place(relx=0.1, rely=0.255)

        self.root.mainloop()

    def calculate_distance_raster(self):
        if self.raster_file is not None:
            if self.raster_loaded:
                self.raster_distance_lbl.config(text='Enter the first point by clicking on the canvas...')
                self.raster_distance_lbl.update()
                self.connection_raster = self.raster_can.mpl_connect('button_press_event',
                                                                     self.get_click_coordinates_raster)
            else:
                messagebox.showerror(title='Error!',
                                     message="Raster file was not loaded!")

        else:
            messagebox.showerror(title='Error!',
                                 message="Raster file was not selected!")

    def get_click_coordinates_raster(self, event):
        self.num_of_clicks_raster += 1
        if self.num_of_clicks_raster == 1:
            self.point1_ras = (event.ydata, event.xdata)
            self.raster_distance_lbl.config(text='Enter the second point by clicking on the canvas...')
            self.raster_distance_lbl.update()
        elif self.num_of_clicks_raster == 2:
            self.point2_ras = (event.ydata, event.xdata)
            self.raster_can.mpl_disconnect(self.connection_raster)
            try:
                self.distance_ras = geopy.distance.distance(self.point1_ras,
                                                            self.point2_ras).m
            except:
                self.distance_ras = math.sqrt(
                    ((self.point1_ras[0] - self.point2_ras[0]) ** 2) + (
                            (self.point1_ras[1] - self.point2_ras[1]) ** 2))
            self.raster_distance_lbl.config(
                text='Distance between the two entered points in meters is:\n{}'.format(self.distance_ras))
            self.raster_distance_lbl.update()
            point1 = [self.point1_ras[0], event.xdata]
            point2 = [self.point1_ras[1], event.ydata]
            x_values = [point2[0], point1[1]]
            y_values = [point1[0], point2[1]]

            self.ax.plot(x_values, y_values, markersize=4)
            self.raster_can.draw()
            self.num_of_clicks_raster = 0

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

    def show_vector_data(self):
        if self.vector is not None:
            self.vector_attributes_text.config(state=NORMAL)
            self.vector_attributes_text.delete(1.0, END)
            self.vector_attributes_text.insert(END, self.vector)
            self.vector_attributes_text.config(state=DISABLED)
        else:
            messagebox.showerror(title='Error!',
                                 message="No data for displaying!")

    def clear_vector_data(self):
        if self.vector_attributes_text.get(1.0, END) != '':
            self.vector_attributes_text.config(state=NORMAL)
            self.vector_attributes_text.delete(1.0, END)
            self.vector_attributes_text.config(state=DISABLED)
        else:
            messagebox.showerror(title='Error!',
                                 message="No data for clearing!")

    def load_csv_data(self):
        self.csv_destination = filedialog.askopenfilename(initialdir="C:/Users/Desktop",
                                                          filetypes=[('CSV files', '*.csv')],
                                                          title='Select a CSV file')
        if self.csv_destination != '':
            try:
                self.a.cla()
                self.vector_file = None
                df = pd.read_csv(self.csv_destination)
                self.geometry = [Point(xyz) for xyz in zip(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2])]
                plotted_points = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in self.geometry]
                self.a.plot([point[0] for point in plotted_points], [point[1] for point in plotted_points], 'o',
                            color='red', markersize=4)
                self.vector_can.draw()
            except:
                messagebox.showerror(title='Error!',
                                     message="Selected file or it's data are not supported!")
        else:
            messagebox.showwarning(title='Warning!',
                                   message="No file was selected!")

    def delaunay_triangulation(self):
        if self.vector_file is not None or self.csv_destination != '':
            display_triangulation = Toplevel(self.root)
            display_triangulation.title('Delaunay\'s triangulation')
            display_triangulation.iconbitmap(r".\resources\flaticon.ico")
            display_triangulation.geometry('600x500')
            display_triangulation.resizable(0, 0)
            fig = Figure(figsize=(6, 5), dpi=100)
            canvas = FigureCanvasTkAgg(figure=fig, master=display_triangulation)
            canvas.get_tk_widget().place(relx=0, rely=0, height=500, width=600)
            tb = NavigationToolbar2Tk(canvas, display_triangulation)
            tb.update()
            axe = fig.add_subplot(111)
            points = []
            if self.vector_file is not None:
                if self.vector_loaded:
                    if all(row['geometry'].geom_type == 'Point' or row['geometry'].geom_type == 'MultiPoint' for
                           index, row
                           in self.vector.iterrows()):
                        sf = shapefile.Reader(self.vector_file)
                        points = [np.array((shape.shape.points[0][0], shape.shape.points[0][1])) for shape in
                                  sf.shapeRecords()]
                    else:
                        display_triangulation.destroy()
                        messagebox.showerror(title='Error!',
                                             message="Selected file contains geometry other than Point/MultiPoint!")
                        return
                else:
                    display_triangulation.destroy()
                    messagebox.showerror(title='Error!',
                                         message="Selected vector file is not loaded!")
                    return
            elif self.csv_destination != '':
                points = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in self.geometry]
            delaunay_points = Delaunay(points)
            axe.triplot([point[0] for point in points], [point[1] for point in points], delaunay_points.simplices)
            axe.plot([point[0] for point in points], [point[1] for point in points], 'o', color='red', markersize=3)
            canvas.draw()

    def convex_hull_polygon(self):
        if self.vector_file is not None or self.csv_destination != '':
            display_conhull = Toplevel(self.root)
            display_conhull.title('Convex Hull Polygon')
            display_conhull.iconbitmap(r".\resources\flaticon.ico")
            display_conhull.geometry('600x500')
            display_conhull.resizable(0, 0)
            fig = Figure(figsize=(6, 5), dpi=100)
            canvas = FigureCanvasTkAgg(figure=fig, master=display_conhull)
            canvas.get_tk_widget().place(relx=0, rely=0, height=500, width=600)
            tb = NavigationToolbar2Tk(canvas, display_conhull)
            tb.update()
            axe = fig.add_subplot(111)
            points = []
            if self.vector_file is not None:
                if self.vector_loaded:
                    if all(row['geometry'].geom_type == 'Point' or row['geometry'].geom_type == 'MultiPoint' for
                           index, row in self.vector.iterrows()):
                        sf = shapefile.Reader(self.vector_file)
                        points = np.array(
                            [[shape.shape.points[0][0], shape.shape.points[0][1]] for shape in sf.shapeRecords()])
                    else:
                        display_conhull.destroy()
                        messagebox.showerror(title='Error!',
                                             message="Selected file contains geometry other than Point/MultiPoint!")
                        return
                else:
                    display_conhull.destroy()
                    messagebox.showerror(title='Error!',
                                         message="Selected vector file is not loaded!")
                    return
            elif self.csv_destination != '':
                points = np.array([[geom.xy[0][0], geom.xy[1][0]] for geom in self.geometry])
            hull = ConvexHull(points)
            for simplex in hull.simplices:
                axe.plot(points[simplex, 0], points[simplex, 1], color='k')
            axe.plot([point[0] for point in points], [point[1] for point in points], 'o', color='red', markersize=3)
            canvas.draw()

    def nearest_neighbor_input(self):
        if self.vector_file is not None or self.csv_destination != '':

            entry = Toplevel(self.root)
            entry.geometry('220x70')
            entry.title('Insert coordinates')
            entry.iconbitmap(r".\resources\flaticon.ico")

            entry.resizable(0, 0)

            Label(entry, text="X coordinate:").grid(row=0)
            Label(entry, text="Y coordinate:").grid(row=1)

            global x_coordinate_txt, y_coordinate_txt

            x_coordinate_txt = StringVar(entry)
            y_coordinate_txt = StringVar(entry)

            x_entry = Entry(entry, textvariable=x_coordinate_txt)
            y_entry = Entry(entry, textvariable=y_coordinate_txt)
            x_entry.grid(row=0, column=1)
            y_entry.grid(row=1, column=1)
            Button(entry, text='OK', command=lambda: self.check_data(entry)).grid(row=3, column=1, sticky=W,
                                                                                  pady=4, padx=20)
            Button(entry, text='Cancel', command=entry.destroy).grid(row=3, column=0, sticky=W, pady=4, padx=20)

        else:
            messagebox.showerror(title='Error!',
                                 message="No file was selected!")

    def check_data(self, window):
        if x_coordinate_txt.get() == '' or y_coordinate_txt.get() == '':
            messagebox.showerror(title='Error!',
                                 message="One or more fields have not been filled!")
        else:
            try:
                nearest_neighbor_dataframe = pd.DataFrame(
                    {'x': list([float(x_coordinate_txt.get())]), 'y': list([float(y_coordinate_txt.get())])})
                window.destroy()
                self.nearest_neighbor_search(nearest_neighbor_dataframe)
            except:
                messagebox.showerror(title='Error!',
                                     message="Unsupported data type entered in one or more fields!")

    def nearest_neighbor_search(self, nn_df):
        nn_search = Toplevel(self.root)
        nn_search.title('Nearest Neighbor Search')
        nn_search.iconbitmap(r".\resources\flaticon.ico")
        nn_search.geometry('600x500')
        nn_search.resizable(0, 0)
        fig = Figure(figsize=(6, 5), dpi=100)
        canvas = FigureCanvasTkAgg(figure=fig, master=nn_search)
        canvas.get_tk_widget().place(relx=0, rely=0, height=500, width=600)
        tb = NavigationToolbar2Tk(canvas, nn_search)
        tb.update()
        axe = fig.add_subplot(111)
        input_point = GeoDataFrame(nn_df, geometry=points_from_xy(nn_df.x, nn_df.y))
        gdf = None
        if self.vector_file is not None:
            if self.vector_loaded:
                if all(row['geometry'].geom_type == 'Point' or row['geometry'].geom_type == 'MultiPoint' for index, row
                       in
                       self.vector.iterrows()):
                    gdf = gpd.read_file(self.vector_file)
                else:
                    nn_search.destroy()
                    messagebox.showerror(title='Error!',
                                         message="Selected file contains geometry other than Point/MultiPoint!")
                    return
            else:
                nn_search.destroy()
                messagebox.showerror(title='Error!',
                                     message="Selected vector file is not loaded!")
                return
        elif self.csv_destination != '':
            df = pd.read_csv(self.csv_destination)
            geometry = [Point(xy) for xy in zip(df.iloc[:, 0], df.iloc[:, 1])]
            gdf = GeoDataFrame(df, geometry=geometry)
        closest_point = self.nearest_neighbor(input_point, gdf, return_dist=True)
        for row in gdf['geometry']:
            if closest_point['geometry'][0] == row:

                axe.plot(row.x, row.y, 'o', color='green', markersize=6)
            else:
                axe.plot(row.x, row.y, 'o', color='red', markersize=3)
        canvas.draw()
        messagebox.showinfo(title='Result',
                            message="Distance between the entered point and it's closest neighbor is: {} meters.".format(
                                closest_point['distance'][0]))

    def get_nearest(self, src_points, candidates, k_neighbors=1):
        tree = BallTree(candidates, leaf_size=15, metric='haversine')
        distances, indices = tree.query(src_points, k=k_neighbors)
        distances = distances.transpose()
        indices = indices.transpose()
        closest = indices[0]
        closest_dist = distances[0]
        return (closest, closest_dist)

    def nearest_neighbor(self, left_gdf, right_gdf, return_dist=False):
        left_geom_col = left_gdf.geometry.name
        right_geom_col = right_gdf.geometry.name
        right = right_gdf.copy().reset_index(drop=True)
        left_radians = np.array(
            left_gdf[left_geom_col].apply(lambda geom: (geom.x * np.pi / 180, geom.y * np.pi / 180)).to_list())
        right_radians = np.array(
            right[right_geom_col].apply(lambda geom: (geom.x * np.pi / 180, geom.y * np.pi / 180)).to_list())
        closest, dist = self.get_nearest(src_points=left_radians, candidates=right_radians)
        closest_points = right.loc[closest]
        closest_points = closest_points.reset_index(drop=True)
        if return_dist:
            earth_radius = 6371000
            closest_points['distance'] = dist * earth_radius

        return closest_points


if __name__ == '__main__':
    start = GeographicInformationSystem()
