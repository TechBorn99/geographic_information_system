import math
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.font import Font
from tkinter.ttk import Progressbar
import geopandas as gpd
import numpy as np
import shapefile
from descartes import PolygonPatch
from geopandas import GeoDataFrame, points_from_xy
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from scipy.spatial.qhull import Delaunay, ConvexHull
from sklearn.neighbors._ball_tree import BallTree
import pandas as pd
from shapely.geometry import Point
import geopy.distance


class GeographicInformationSystem:
    """
    Main class of the application. It contains variables and methods that enables the functionalities:
    1. Selecting and loading vector and raster files from the computer
    2. Zooming in, zooming out, pan, zoom extent, saving the figure inside the canvas etc.
    3. Selecting and loading CSV file that contains coordinates for Points
    4. Delaunay's triangulation for the selected CSV file or the shapefile that contains only points or multipoints
    5. Convex Hull Polygon generating for the selected CSV file or the shapefile that contains only points or multipoints
    6. Nearest Neighbor search for the points inside of the CSV file or the shapefile for the entered coordinates
    7. Measuring distance between points entered via mouse click, both on raster or the vector file.
    """

    # Initialization of the main Tkinter window
    root = Tk()

    # Variables that store the links to the selected raster and vector file
    raster_file = None
    vector_file = None

    # Variables used for checking if the raster file or shapefile is loaded onto the canvas
    vector_loaded = False
    raster_loaded = False

    # Figures added to the FigureCanvasTk of the vector and raster Frame
    fig1 = Figure(figsize=(6, 5), dpi=100)
    fig2 = Figure(figsize=(6, 5), dpi=100)

    # Variables that store figures to which the subplot was added
    a = fig2.add_subplot(111)
    ax = fig1.add_subplot(111)

    # Variable that stores the uploaded shapefile
    vector = None

    # Variable that stores the link to the selected CSV file
    csv_destination = ''

    # Variables that store the number of clicks inside the canvases when the measuring distance has started
    num_of_clicks_raster = 0
    num_of_clicks_vector = 0

    # Variables that store bindings of the click event to the raster_can and vector_can
    connection_raster = None
    connection_vector = None

    # Variables that store the distance between two points selected on the raster_can or vector_can
    distance_vec = distance_ras = 0

    # Variables that store data of the click on the vector and raster canvas during the measurement between two points
    point1_vec = point2_vec = point1_ras = point2_ras = None

    # Font added to some widgets
    helv12 = Font(family='Helvetica', size=12, weight='bold')

    # Customization of the buttons inside the NavigationToolbar2Tk
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
        """
        Initialization method that is called when the class is instantiated. It creates and adds all the necessary
        widgets to the main (root) window.
        """

        # Setting the title and the favicon for the application
        self.root.title('Geographic information system')
        self.root.iconbitmap(r".\resources\flaticon.ico")

        # Setting up the size of the main window
        self.root.geometry("1536x764+0+0")

        # Making the main window not resizable
        self.root.resizable(0, 0)

        # Configuring the grid layout for the main window
        self.root.columnconfigure(0, weight=4)
        self.root.columnconfigure(1, weight=4)
        self.root.rowconfigure(0, weight=1)

        # Creating two frames inside the main window (one for the raster files, and the other for the vector files)
        self.raster_side = Frame(self.root, bg='lightgoldenrod1')
        self.vector_side = Frame(self.root, bg='lightgoldenrod1')

        # Adding the two frames to the grid layout of the main window
        self.raster_side.grid(row=0, column=0, sticky="nsew")
        self.vector_side.grid(row=0, column=1, sticky="nsew")

        # Adding the label that marks the Frame that is meant for the vector files
        self.vector_lab = Label(self.vector_side, text='Shapefile', bg='lightgoldenrod1')
        self.vector_lab.place(relx=0.1, rely=0.05)

        # Adding the label that marks the Frame that is meant for the raster files
        self.raster_lab = Label(self.raster_side, text='Raster', bg='lightgoldenrod1')
        self.raster_lab.place(relx=0.1, rely=0.05)

        # Creating and adding the button that enables the 'Load CSV' functionality
        load_csv_image = PhotoImage(file=r'.\resources\load_csv.gif')
        self.load_csv_btn = Button(self.raster_side, image=load_csv_image, command=self.load_csv_data)
        self.load_csv_btn.place(relx=0.0, rely=0.0, width=32, height=32)

        # Creating and adding the button that enables the 'Delaunay's Triangulation' functionality
        delaunay_triangulation_image = PhotoImage(file=r'.\resources\delaunay_triangulation_icon.gif')
        self.delaunay_triangulation_btn = Button(self.raster_side, image=delaunay_triangulation_image,
                                                 command=self.delaunay_triangulation)
        self.delaunay_triangulation_btn.place(relx=0.045, rely=0.0, width=32, height=32)

        # Creating and adding the button that enables the 'Convex Hull Polygon' functionality
        polygon_image = PhotoImage(file=r'.\resources\polygon.gif')
        self.convex_hull_polygon_btn = Button(self.raster_side, image=polygon_image,
                                              command=self.convex_hull_polygon)
        self.convex_hull_polygon_btn.place(relx=0.09, rely=0.0, width=32, height=32)

        # Creating and adding the button that enables the 'Nearest neighbor search' functionality
        nearest_neighbor_search_image = PhotoImage(file=r'.\resources\nearest_neighbor.gif')
        self.nearest_neighbor_search_btn = Button(self.raster_side, image=nearest_neighbor_search_image,
                                                  command=self.nearest_neighbor_input)
        self.nearest_neighbor_search_btn.place(relx=0.135, rely=0.0, width=32, height=32)

        # Creating and adding of the 'About' button
        about_image = PhotoImage(file=r'.\resources\about.gif')
        self.about_btn = Button(self.raster_side, image=about_image, command=self.about)
        self.about_btn.place(relx=0.18, rely=0.0, width=32, height=32)

        # Creating and adding of the 'Exit' button
        exit_image = PhotoImage(file=r'.\resources\exit.gif')
        self.exit_btn = Button(self.raster_side, image=exit_image, command=self.exit)
        self.exit_btn.place(relx=0.225, rely=0.0, width=32, height=32)

        # Creating and adding the button that enables 'Measure distance between two points'
        # functionality for the raster canvas
        ruler_image = PhotoImage(file=r'.\resources\ruler.gif')
        self.calculate_distance_btn = Button(self.raster_side, image=ruler_image,
                                             command=self.calculate_distance_raster)
        self.calculate_distance_btn.place(relx=0.03, rely=0.25, width=32, height=32)

        # Creating and adding the button that enables 'Measure distance between two points'
        # functionality for the vector canvas (vector_can)
        self.calculate_distance_vector_btn = Button(self.vector_side, image=ruler_image,
                                                    command=self.calculate_distance_vector)
        self.calculate_distance_vector_btn.place(relx=0.6, rely=0.093, width=32, height=32)

        # Creating and adding the label in which the information regarding the measuring distance are shown
        # (for the raster canvas)
        self.raster_distance_lbl = Label(self.raster_side, text='', bg='lightgoldenrod1')
        self.raster_distance_lbl.place(relx=0.1, rely=0.255)

        # Creating and adding the label in which the information regarding the measuring distance are shown
        # (for the vector canvas (vector_can))
        self.vector_distance_lbl = Label(self.vector_side, text='', bg='lightgoldenrod1')
        self.vector_distance_lbl.place(relx=0.6, rely=0.15)

        # Creating and adding the button that enables raster file upload to the application
        self.select_raster_btn = Button(self.raster_side, command=self.select_raster, text='Select a raster file',
                                        bg='lightgoldenrod2',
                                        activebackground='lightgoldenrod3')
        self.select_raster_btn.place(relx=0.10, rely=0.1)

        # Creating and adding the button that enables shapefile upload to the application
        self.select_vector_btn = Button(self.vector_side, command=self.select_vector, text='Select a vector file',
                                        bg='lightgoldenrod2',
                                        activebackground='lightgoldenrod3')
        self.select_vector_btn.place(relx=0.10, rely=0.1)

        # Creating and adding the button that enables the loading od the raster file to the canvas
        self.load_raster_btn = Button(self.raster_side, command=self.load_raster, text='Load a raster file',
                                      bg='lightgoldenrod2',
                                      activebackground='lightgoldenrod3')
        self.load_raster_btn.place(relx=0.10, rely=0.16)

        # Creating and adding the button that enables the loading of the vector file to the canvas
        self.load_vector_btn = Button(self.vector_side, command=self.load_vector, text='Load a vector file',
                                      bg='lightgoldenrod2',
                                      activebackground='lightgoldenrod3')
        self.load_vector_btn.place(relx=0.10, rely=0.16)

        # Creating and adding the text field in which the link to the selected raster file will be shown
        self.raster_path = Text(self.raster_side, state=DISABLED)
        self.raster_path.place(relx=0.25, rely=0.1, height=25, width=250)

        # Creating and adding the text field in which the link to the selected vector file will be shown
        self.vector_path = Text(self.vector_side, state=DISABLED)
        self.vector_path.place(relx=0.25, rely=0.1, height=25, width=250)

        # Creating and adding the matplotlib canvas in which the raster files will be displayed
        self.raster_can = FigureCanvasTkAgg(self.fig1, master=self.raster_side)
        self.raster_can.get_tk_widget().place(relx=0.1, rely=0.22, height=500, width=600)

        # Creating and adding the matplotlib canvas in which the raster files will be displayed
        self.vector_can = FigureCanvasTkAgg(self.fig2, master=self.vector_side)
        self.vector_can.get_tk_widget().place(relx=0.005, rely=0.3, height=535, width=740)

        # Creating and adding of the progressbar of the uploading of the file to the canvas for displaying the raster files
        self.progress_raster = Progressbar(self.raster_side, orient=HORIZONTAL, length=250, mode='determinate')
        self.progress_raster.place(relx=0.25, rely=0.165)

        # Creating and adding of the progressbar of the uploading of the file to the canvas for displaying the shapefiles
        self.progress_vector = Progressbar(self.vector_side, orient=HORIZONTAL, length=250, mode='determinate')
        self.progress_vector.place(relx=0.25, rely=0.165)

        # Creating and adding the navigation toolbar for the canvas in which the raster files are displayed
        # It contains elements within the NavigationToolbar2Tk.toolitems
        self.toolbar = NavigationToolbar2Tk(self.raster_can, self.raster_side)
        self.raster_can._tkcanvas.pack(expand=False, side=BOTTOM, fill=BOTH)
        self.toolbar.update()

        # Creating and adding the navigation toolbar for the canvas in which the vector files are displayed
        # It contains elements within the NavigationToolbar2Tk.toolitems
        self.toolbar_vec = NavigationToolbar2Tk(self.vector_can, self.vector_side)
        self.vector_can._tkcanvas.pack(padx=2, expand=False, side=BOTTOM, fill='x')
        self.toolbar_vec.update()

        # Creating and adding the text box in which the attributes of the uploaded shapefile will
        # be shown on the click of a button
        self.vector_attributes_text = Text(self.vector_side, state=DISABLED, width=72, height=3)
        self.vector_attributes_text.place(relx=0.11, rely=0.22)

        # Creating and adding the button that enables the functionality of displaying vector data in the above-mentioned
        # text box
        self.display_vector_data = Button(self.vector_side, command=self.show_vector_data,
                                          text='Display\nvector\ndata',
                                          bg='lightgoldenrod2',
                                          activebackground='lightgoldenrod3')
        self.display_vector_data.place(relx=0.02, rely=0.22)

        # Creating and adding the button that enables the clearing the content of the above-mentioned text box
        self.clear_vector_data = Button(self.vector_side, command=self.clear_vector_data,
                                        text='Clear\nvector\ndata',
                                        bg='lightgoldenrod2',
                                        activebackground='lightgoldenrod3')
        self.clear_vector_data.place(relx=0.89, rely=0.22)

        # Mainloop of the main window of the app
        self.root.mainloop()

    def bar(self, progress):

        """
        Method that moves the progress bar when the load_raster_btn or load_vector_btn is clicked.
        :param progress: The progress bar for the selected side where the loading is needed
        """

        # Import the necessary module
        import time

        # Change the value of the progress bar to  20
        progress['value'] = 20

        # Finish all the tasks that are being done in the background
        self.root.update_idletasks()

        # Wait for 0.2 seconds
        time.sleep(0.2)

        # Change the value of the progress bar to  40, then finish all idle tasks, then wait 0.1 seconds
        progress['value'] = 40
        self.root.update_idletasks()
        time.sleep(0.1)

        # Change the value of the progress bar to  80, finish all idle tasks, then wait 0.2 seconds
        progress['value'] = 80
        self.root.update_idletasks()
        time.sleep(0.2)

        # Change the value of the progress bar to  100
        progress['value'] = 100

    def reset_bar(self, progress_bar):

        """ Method that resets the specified progress bar, by setting it's value to 0. """

        # Set the value of the progress bar to 0
        progress_bar['value'] = 0

    def select_raster(self):
        """
        Method that is called when the select_raster_btn is clicked.
        It opens the filedialog in which the user can selected a raster file with the supported extensions, and then
        displays the path to the selected file in the raster_path text box.
        """

        # Let the user choose the file, if it's extension is supported
        self.raster_file = filedialog.askopenfilename(initialdir="C:/Users/Desktop",
                                                      filetypes=[('Raster files', '*.tif'),
                                                                 ('Raster files', '*.jpg'),
                                                                 ('Raster files', '*.jfif'),
                                                                 ('Raster files', '*.gif'),
                                                                 ('Raster files', '*.bmp'),
                                                                 ('Raster files', '*.png'),
                                                                 ('Raster files', '*.bat')],
                                                      title='Select a raster file')

        # Change the state of the raster_path text box so it's content can be altered
        self.raster_path.config(state=NORMAL)

        # Delete the content of the raster_path text box if it contains any text
        self.raster_path.delete(1.0, END)

        # Insert the path to the selected raster file in the raster_path text box
        self.raster_path.insert(END, self.raster_file)

        # Disable the raster_path text box so new text cannot be manually added to it
        self.raster_path.config(state=DISABLED)

        # Set the loaded status to False
        self.raster_loaded = False

    def load_raster(self):
        """
        Method that is called when the load_raster_btn is clicked.
        It is used to display the the raster file selected in the select_raster method.
        """

        # Check whether the raster file is selected
        if self.raster_file is None:

            # If it is not, show the error to the user
            messagebox.showerror(title='Error!',
                                 message="No file for loading was selected!\nPlease select a file, then try again!")
        else:

            # If it is, clear the previous plot
            self.ax.cla()

            # Import necessary modules
            import rasterio as rio
            from rasterio.plot import show

            # Adjust the subplot
            self.fig1.subplots_adjust(bottom=0, right=1, top=1, left=0, wspace=0, hspace=0)
            with rio.open(r'{}'.format(self.raster_file)) as src_plot:
                show(src_plot, ax=self.ax, cmap='gist_gray')
            plt.close()

            # Hide the axes
            self.ax.set(title="", xticks=[], yticks=[])
            self.ax.spines["top"].set_visible(False)
            self.ax.spines["right"].set_visible(False)
            self.ax.spines["left"].set_visible(False)
            self.ax.spines["bottom"].set_visible(False)

            # Start the progress bar loading
            self.bar(self.progress_raster)

            # Draw the plotted raster file in the specified canvas
            self.raster_can.draw()

            # Reset the progress bar
            self.reset_bar(self.progress_raster)

            # Set the status of the raster to loaded
            self.raster_loaded = True

    def select_vector(self):
        """
        Method that is called when the select_vector_btn button is clicked.
        It opens the filedialog for the user to select the shapefile with the .shp extension, than inserts the link to
        that file in the vector_path text box.
        """

        # Open the filedialog for the user and store the result in the specified variable
        self.vector_file = filedialog.askopenfilename(initialdir="C:/Users/Desktop",
                                                      filetypes=[('Vector files', '*.shp')],
                                                      title='Select a vector file')

        # Set the state of the specified text box to NORMAL, so it can be altered
        self.vector_path.config(state=NORMAL)

        # Delete the content of the specified text box if there is any
        self.vector_path.delete(1.0, END)

        # Insert the link to the selected shapefile in specified text box
        self.vector_path.insert(END, self.vector_file)

        # Disable the specified text box, so it cannot be altered afterwards
        self.vector_path.config(state=DISABLED)

        # Set the status of the vector loading to False, so some operations cannot be done until the shapefile is loaded
        # onto the vector_can
        self.vector_loaded = False

    def load_vector(self):
        """
        Method that is called when the load_vector_btn button is clicked.
        It displays the plotted version of the shapefile on the vector_can, using method that depends on the type of the
        shapes in the shapefile.
        """

        # First check whether the shapefile is selected
        # If it is not, display an error message
        if self.vector_file is None:
            messagebox.showerror(title='Error!',
                                 message="No file for loading was selected!\nPlease select a file, then try again!")
        # If it is
        else:
            # Delete the link ot the previously added CSV file, if present
            self.csv_destination = ''

            # Clear the current plot
            self.a.cla()

            # Read the selected shapefile with geopandas and plot it
            self.vector = gpd.read_file(self.vector_file, crs="EPSG:4326")
            self.vector.plot()

            # Read the selected shapefile with shapefile Reader (it will be used for the conditions in the steps that follow)
            sf = shapefile.Reader(self.vector_file)

            # Check whether the shapefile geometry is made up of Points/MultiPoints, LineStrings/MultiLineStrings or
            # Polygons/MultiPolygons

            # If the shapefile geometry is made up of Points/MultiPoints
            if all(row['geometry'].geom_type == 'Point' or row['geometry'].geom_type == 'MultiPoint' for index, row in
                   self.vector.iterrows()):

                # Save every points that is inside the shapefile inside the variable
                points = [np.array((shape.shape.points[0][0], shape.shape.points[0][1])) for shape in sf.shapeRecords()]

                # Plot all the points from the points variable/shapefile
                self.a.plot([point[0] for point in points], [point[1] for point in points], 'o', color='red',
                            markersize=4)

                # Set the vector status to loaded
                self.vector_loaded = True

            # If the shapefile geometry is made up of LineStrings/MultiLineStrings
            elif all(row['geometry'].geom_type == 'LineString' or row['geometry'].geom_type == 'MultiLineString' for
                     index, row in self.vector.iterrows()):

                # For each LineString/MultiLineString in the geometry of the shapefile
                for line in self.vector['geometry']:

                    # Check whether it is a MultiLineString or a LineString
                    # If it is a MultiLineString
                    if line.geom_type == 'MultiLineString':

                        # Plot every line inside the MultiLineString
                        for li in line:
                            self.a.plot(*li.xy)

                    # If it is a LineString, just plot that line
                    elif line.geom_type == 'LineString':
                        self.a.plot(*line.xy)

                # Set the status of the vector to loaded
                self.vector_loaded = True

            # If the shapefile geometry is made up of Polygons/MultiPolygons
            elif all(
                    row['geometry'].geom_type == 'Polygon' or row['geometry'].geom_type == 'MultiPolygon' for index, row
                    in self.vector.iterrows()):

                # For each Polygons/MultiPolygons in the geometry of the shapefile
                for polygon in self.vector['geometry']:

                    # Check whether it is a MultiPolygon or a Polygon
                    # If it is a MultiLineString
                    if polygon.geom_type == 'MultiPolygon':
                        for pol in polygon:
                            # Plot every polygon inside the MultiLineString
                            self.a.plot(*pol.exterior.xy)

                            # For every Polygon inside the MultiPolygon add the PolygonPatch
                            patch = PolygonPatch(pol, alpha=0.5)

                            # Then plot every patch
                            self.a.add_patch(patch)

                    # If it is a Polygon, just plot that polygon
                    elif polygon.geom_type == 'Polygon':
                        self.a.plot(*polygon.exterior.xy)

                # Set the status of the vector to loaded
                self.vector_loaded = True

            # If the specified shapefile contains some geometry that is not supported, display an error message, then
            # exit the method
            else:
                messagebox.showerror(title='Error!',
                                     message="Unsupported geometry detected...")
                return

            # If the shapefile is plotted, start the progress bar
            self.bar(self.progress_vector)

            # When the bar finishes, display the plotted shapefile in the vector_can
            self.vector_can.draw()

            # When the plotted shapefile is displayed, reset the progress bar
            self.reset_bar(self.progress_vector)

    def show_vector_data(self):
        """
        Method that is called when the display_vector_data button is clicked.
        It is used to display the information contained inside the vector file (shapefile).
        """

        # Check whether the shapefile is selected
        # If it is
        if self.vector is not None:

            # Set the state of the vector_attributes_text text box to NORMAL, so it can be altered
            self.vector_attributes_text.config(state=NORMAL)

            # Then delete the current text inside the vector_attributes_text text box
            self.vector_attributes_text.delete(1.0, END)

            # Insert the information about the selected vector file in the vector_attributes_text text box
            self.vector_attributes_text.insert(END, self.vector)

            # Disable the vector_attributes_text text box, so it cannot be altered afterwards
            self.vector_attributes_text.config(state=DISABLED)

        # If it is not loaded, display an error message for the user
        else:
            messagebox.showerror(title='Error!',
                                 message="No data for displaying!")

    def clear_vector_data(self):
        """
        Method that is called when the clear_vector_data is clicked.
        It is used to clear the content of the vector_attributes_text text box.
        """
        # First check whether there is any data inside the vector_attributes_text text box
        # If there is
        if self.vector_attributes_text.get(1.0, END) != '':

            # Set the state of the vector_attributes_text text box to NORMAL, so it can be altered
            self.vector_attributes_text.config(state=NORMAL)

            # Delete the current text inside the vector_attributes_text text box
            self.vector_attributes_text.delete(1.0, END)

            # Disable the vector_attributes_text text box, so it cannot be altered afterwards
            self.vector_attributes_text.config(state=DISABLED)

        # If there is not, display an error message to the user
        else:
            messagebox.showerror(title='Error!',
                                 message="No data for clearing!")

    def load_csv_data(self):

        """
        Method that is called when the load_csv_btn is clicked.
        It is used for selecting and loading the content of the CSV file containing coordinates of points onto the
        vector_can.
        """

        # Open the filedialog, so the user can select the CSV file which will be dispalyed
        self.csv_destination = filedialog.askopenfilename(initialdir="C:/Users/Desktop",
                                                          filetypes=[('CSV files', '*.csv')],
                                                          title='Select a CSV file')
        # If the file is selected
        if self.csv_destination != '':
            # Encapsulate everything inside the try-except block, which will be triggered if there are any exceptions,
            # for example if the user selects the file which doesn't contain coordinates of the points which should
            # be plotted, etc.
            try:

                # Clear the previous plot, if there is any
                self.a.cla()

                # Set the vector file to None, so there won't be any ambiguous behaviour
                self.vector_file = None

                # Read the CSV file with the pandas module
                df = pd.read_csv(self.csv_destination)

                # If there are some unnecessary columns, they can be deleted (dropped) with the below-written method
                # df.drop(df.columns[[0]], axis=1, inplace=True)

                # Create the geometry, which will be used when creating a GeoDataFrame out of a pandas DataFrame
                self.geometry = [Point(xyz) for xyz in zip(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2])]

                # Create a GeoDataFrame out of a pandas DataFrame, using the made geometry and set the crs to "EPSG:4326"
                # points = GeoDataFrame(df, crs="EPSG:4326", geometry=self.geometry)
                # points.plot(color='red', marker='o', markersize=3)

                # Extract x and y coordinates from the GeoDataFrame geometry and store it as a numpy array
                # inside the specified variable
                plotted_points = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in self.geometry]

                # Plot every point from the plotted_points variable
                self.a.plot([point[0] for point in plotted_points], [point[1] for point in plotted_points], 'o',
                            color='red', markersize=4)

                # Display the new plot onto the vector_can
                self.vector_can.draw()

            # If any exception occurred, display an error message
            except:
                messagebox.showerror(title='Error!',
                                     message="Selected file or it's data are not supported!")

        # If the file was not selected, dispaly a warning
        else:
            messagebox.showwarning(title='Warning!',
                                   message="No file was selected!")

    def delaunay_triangulation(self):
        """
        Method that is called when the delaunay_triangulation_btn is clicked.
        It creates the Delaunay's triangulation for the shapefile that contains only points in it's geometry or
        the CSV file that contains coordinates for points.
        """
        # Check whether there is a selected vector or CSV file
        if self.vector_file is not None or self.csv_destination != '':

            # If there is, create the base Toplevel window in which the result will be presented
            display_triangulation = Toplevel(self.root)

            # Set the title, favicon and the size for the Toplevel window
            display_triangulation.title('Delaunay\'s triangulation')
            display_triangulation.iconbitmap(r".\resources\flaticon.ico")
            display_triangulation.geometry('600x500')

            # Make the Toplevel window not resizable
            display_triangulation.resizable(0, 0)

            # Store the Figure which will be added to the matplotlib canvas
            fig = Figure(figsize=(6, 5), dpi=100)

            # Create and add the canvas in which the result will be drawn
            canvas = FigureCanvasTkAgg(figure=fig, master=display_triangulation)
            canvas.get_tk_widget().place(relx=0, rely=0, height=500, width=600)

            # Add the navigation toolbar to the created canvas
            tb = NavigationToolbar2Tk(canvas, display_triangulation)
            tb.update()

            # Store the subplot of the above-created figure into a variable
            axe = fig.add_subplot(111)

            # Declare the points variable, which will be instantiated afterwards
            points = []

            # Check whether the triangulation should be done for the shapefile or the CSV file
            # If the vector file is not None, triangulation will be done for it
            if self.vector_file is not None:

                # Check whether the vector file is loaded
                # If it is, do the following
                if self.vector_loaded:

                    # Check whether the geometry for the selected and loaded vector file is made only of Points and
                    # MultiPoints
                    if all(row['geometry'].geom_type == 'Point' or row['geometry'].geom_type == 'MultiPoint' for
                           index, row
                           in self.vector.iterrows()):

                        # Read the file again with the shapefile reader, as it will be used during plotting and creating
                        # Delaunay triangulation
                        sf = shapefile.Reader(self.vector_file)

                        # Store coordinates of points in the shapefile as a numpy array in the variable points
                        points = [np.array((shape.shape.points[0][0], shape.shape.points[0][1])) for shape in
                                  sf.shapeRecords()]

                    # If it contains some other geometry, display an error message, close the Toplevel window
                    # and cancel the operation
                    else:
                        display_triangulation.destroy()
                        messagebox.showerror(title='Error!',
                                             message="Selected file contains geometry other than Point/MultiPoint!")
                        return

                # If it is not loaded, cancel the operation, close the newly created Toplevel window and display an error message
                else:
                    display_triangulation.destroy()
                    messagebox.showerror(title='Error!',
                                         message="Selected vector file is not loaded!")
                    return

            # If the CSV destination is not an empty string, triangulation will be done for it
            elif self.csv_destination != '':
                # Store the coordinates of all points into a variable as a numpy array
                points = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in self.geometry]

            # Create Delaunay triangulation
            delaunay_points = Delaunay(points)

            # Plot points and the triangulation lines on the subplot of a figure
            axe.triplot([point[0] for point in points], [point[1] for point in points], delaunay_points.simplices)
            axe.plot([point[0] for point in points], [point[1] for point in points], 'o', color='red', markersize=3)

            # If there were no exceptions, display the plotted and triangulated figure
            canvas.draw()

    def convex_hull_polygon(self):
        """
        Method that is called when clicked on convex_hull_polygon_btn button.
        It is used to create the convex hull polygon from the points from the CSV file or the shapefile.
        """
        # Check whether vector or CSV file has been selected
        if self.vector_file is not None or self.csv_destination != '':

            # If it is, create a new Toplevel window
            display_conhull = Toplevel(self.root)

            # Add the title, size and favicon to the new Toplevel window
            display_conhull.title('Convex Hull Polygon')
            display_conhull.iconbitmap(r".\resources\flaticon.ico")
            display_conhull.geometry('600x500')

            # Make the window not resizable
            display_conhull.resizable(0, 0)

            # Store the Figure which will be added to the matplotlib canvas
            fig = Figure(figsize=(6, 5), dpi=100)

            # Create and add the canvas in which the result will be drawn
            canvas = FigureCanvasTkAgg(figure=fig, master=display_conhull)
            canvas.get_tk_widget().place(relx=0, rely=0, height=500, width=600)

            # Add the navigation toolbar to the created canvas
            tb = NavigationToolbar2Tk(canvas, display_conhull)
            tb.update()

            # Store the subplot of the above-created figure into a variable
            axe = fig.add_subplot(111)

            # Declare a variable in which the points will be stored
            points = []

            # Check whether the triangulation should be done for the shapefile or the CSV file
            # If the vector file is not None, Convex Hull Polygon will be generated for it
            if self.vector_file is not None:

                # Check whether the vector file is loaded
                # If it is, do the following
                if self.vector_loaded:

                    # Check whether the geometry for the selected and loaded vector file is made only of Points and
                    # MultiPoints
                    if all(row['geometry'].geom_type == 'Point' or row['geometry'].geom_type == 'MultiPoint' for
                           index, row in self.vector.iterrows()):

                        # Read the file again with the shapefile reader, as it will be used during plotting and creating
                        # Convex Hull Polygon
                        sf = shapefile.Reader(self.vector_file)

                        # Store coordinates of points in the shapefile as a numpy array in the variable points
                        points = np.array(
                            [[shape.shape.points[0][0], shape.shape.points[0][1]] for shape in sf.shapeRecords()])

                    # If it contains some other geometry, display an error message, close the Toplevel window
                    # and cancel the operation
                    else:
                        display_conhull.destroy()
                        messagebox.showerror(title='Error!',
                                             message="Selected file contains geometry other than Point/MultiPoint!")
                        return
                # If it is not loaded, cancel the operation, close the newly created Toplevel window and display an error message
                else:
                    display_conhull.destroy()
                    messagebox.showerror(title='Error!',
                                         message="Selected vector file is not loaded!")
                    return

            # If the CSV destination is not an empty string, Convex Hull Polygon will be generated for it
            elif self.csv_destination != '':
                # Store the coordinates of all points into a variable as a numpy array
                points = np.array([[geom.xy[0][0], geom.xy[1][0]] for geom in self.geometry])

            # Create the Convex Hull
            hull = ConvexHull(points)
            # Plot the Polygon
            for simplex in hull.simplices:
                axe.plot(points[simplex, 0], points[simplex, 1], 'k-', color='blue')

            # Plot all the Points
            axe.plot([point[0] for point in points], [point[1] for point in points], 'o', color='red', markersize=3)

            # If there were no exceptions, display the Convex Hull Polygon, along with all the points
            canvas.draw()

    def nearest_neighbor_input(self):
        """
        Method that is called when clicked on nearest_neighbor_search_btn button.
        It initializes the window in which the coordinates for the point that will be searched for are entered.
        """
        # Check whether shapefile ot CSV file is selected
        if self.vector_file is not None or self.csv_destination != '':

            # Initialize the Toplevel window
            entry = Toplevel(self.root)

            # Set the size, title and flaticon for the Toplevel window
            entry.geometry('220x70')
            entry.title('Insert coordinates')
            entry.iconbitmap(r".\resources\flaticon.ico")

            # Make the window not resizable
            entry.resizable(0, 0)

            # Create and add two labels which indicate where to input x and y coordinates
            Label(entry, text="X coordinate:").grid(row=0)
            Label(entry, text="Y coordinate:").grid(row=1)

            # Make widgets x_coordinate_txt and y_coordinate_txt global, so they can be accessed from outside this method
            global x_coordinate_txt, y_coordinate_txt

            # Create StringVar-s which will store text entered into the text boxes
            x_coordinate_txt = StringVar(entry)
            y_coordinate_txt = StringVar(entry)

            # Create and add to the Toplevel window two Entry widgets in which the coordinates will be entered
            x_entry = Entry(entry, textvariable=x_coordinate_txt)
            y_entry = Entry(entry, textvariable=y_coordinate_txt)
            x_entry.grid(row=0, column=1)
            y_entry.grid(row=1, column=1)

            # Create and add the two buttons which close the Toplevel window or accept the entered text inside the two entries
            Button(entry, text='OK', command=lambda: self.check_data(entry)).grid(row=3, column=1, sticky=W,
                                                                                  pady=4, padx=20)
            Button(entry, text='Cancel', command=entry.destroy).grid(row=3, column=0, sticky=W, pady=4, padx=20)

        # If no file has been selected, display an error message for the user
        else:
            messagebox.showerror(title='Error!',
                                 message="No file was selected!")

    def check_data(self, window):

        """
        Method that is used to check whether the data entered into the window for nearest neighbor search is in correct
        format.
        :param window: Toplevel window which will be closed if data is not 'in order'.
        """

        # Check whether any of the text boxes is empty, if it is, display an error
        if x_coordinate_txt.get() == '' or y_coordinate_txt.get() == '':
            messagebox.showerror(title='Error!',
                                 message="One or more fields have not been filled!")
        else:
            # If it is not, proceed
            # The next few lines are wrapped with the try-except block which catches any exception that might show, and
            # displays an adequate error message
            try:
                # Create a pandas DataFrame out of the two entered numbers
                nearest_neighbor_dataframe = pd.DataFrame(
                    {'x': list([float(x_coordinate_txt.get())]), 'y': list([float(y_coordinate_txt.get())])})

                # When the Dataframe is created, close the window in which the coordinates are entered
                window.destroy()

                # Proceed to the next method
                self.nearest_neighbor_search(nearest_neighbor_dataframe)
            except:
                messagebox.showerror(title='Error!',
                                     message="Unsupported data type entered in one or more fields!")

    def nearest_neighbor_search(self, nn_df):
        """
        Method that is called when the entered data is valid.
        It is used for calling the method that finds the closest point and plots it and displays it inside of a new canvas.
        :param nn_df: DataFrame that contains only x and y coordinates
        """
        # Create the Toplevel window
        nn_search = Toplevel(self.root)

        # Set the title, favicon and size for the Toplevel window
        nn_search.title('Nearest Neighbor Search')
        nn_search.iconbitmap(r".\resources\flaticon.ico")
        nn_search.geometry('600x500')

        # Make the Toplevel not resizable
        nn_search.resizable(0, 0)

        # Store the Figure which will be added to the matplotlib canvas
        fig = Figure(figsize=(6, 5), dpi=100)

        # Create and add the canvas in which the result will be drawn
        canvas = FigureCanvasTkAgg(figure=fig, master=nn_search)
        canvas.get_tk_widget().place(relx=0, rely=0, height=500, width=600)

        # Add the navigation toolbar to the created canvas
        tb = NavigationToolbar2Tk(canvas, nn_search)
        tb.update()

        # Store the subplot of the above-created figure into a variable
        axe = fig.add_subplot(111)

        # Make a GeoDataFrame out of the pandas DataFrame that was passed to this method
        input_point = GeoDataFrame(nn_df, geometry=points_from_xy(nn_df.x, nn_df.y))

        # Declare the variable that will store the GeoDataFrame made out of the points inside the shapefile geometry or
        # the coordinates inside the CSV file
        gdf = None

        # Check whether the triangulation should be done for the shapefile or the CSV file
        # If the vector file is not None, GeoDataFrame will be created from it
        if self.vector_file is not None:

            # Check whether the vector file is loaded
            # If it is, do the following
            if self.vector_loaded:
                # Check whether the geometry for the selected and loaded vector file is made only of Points and
                # MultiPoints
                if all(row['geometry'].geom_type == 'Point' or row['geometry'].geom_type == 'MultiPoint' for index, row
                       in
                       self.vector.iterrows()):

                    # Read the file with geopandas, as it will make it into GeoDataFrame immediately
                    gdf = gpd.read_file(self.vector_file)

                # If it contains some other geometry, display an error message, close the Toplevel window
                # and cancel the operation
                else:
                    nn_search.destroy()
                    messagebox.showerror(title='Error!',
                                         message="Selected file contains geometry other than Point/MultiPoint!")
                    return

            # If it is not loaded, cancel the operation, close the newly created Toplevel window and display an error message
            else:
                nn_search.destroy()
                messagebox.showerror(title='Error!',
                                     message="Selected vector file is not loaded!")
                return

        # If the CSV destination is not an empty string, Nearest Neighbor Search will be done for it's points
        elif self.csv_destination != '':

            # Read that CSV as pandas DataFrame
            df = pd.read_csv(self.csv_destination)

            # Create the geometry variable (list of shapely Points)
            geometry = [Point(xy) for xy in zip(df.iloc[:, 0], df.iloc[:, 1])]

            # Create the GeoDataFrame out of the above-read pandas DataFrame and with the created geometry
            gdf = GeoDataFrame(df, geometry=geometry)

        # Find the Point closest to the entered coordinates
        closest_point = self.nearest_neighbor(input_point, gdf, return_dist=True)

        # Iterate through all of the rows of the GeoDataFrame geometry and plot every point
        # If the Point of the current iteration is the same as the closest point,
        # plot in different color and size
        for row in gdf['geometry']:
            if closest_point['geometry'][0] == row:

                axe.plot(row.x, row.y, 'o', color='green', markersize=6)
            else:
                axe.plot(row.x, row.y, 'o', color='red', markersize=3)

        # Draw the new plot onto the new Toplevel window canvas
        canvas.draw()

        # Display a message with the distance of the Point with entered coordinates and it's closest 'neighbor'
        messagebox.showinfo(title='Result',
                            message="Distance between the entered point and it's closest neighbor is: {} meters.".format(
                                closest_point['distance'][0]))

    def get_nearest(self, src_points, candidates, k_neighbors=1):

        """ Find nearest neighbors for all source points from a set of candidate points. """

        # Create tree from the candidate points
        tree = BallTree(candidates, leaf_size=15, metric='haversine')

        # Find closest points and distances
        distances, indices = tree.query(src_points, k=k_neighbors)

        # Transpose to get distances and indices into arrays
        distances = distances.transpose()
        indices = indices.transpose()

        # Get closest indices and distances (i.e. array at index 0)
        # Note: for the second closest points, you would take index 1, etc.
        closest = indices[0]
        closest_dist = distances[0]

        # Return indices and distances
        return (closest, closest_dist)

    def nearest_neighbor(self, left_gdf, right_gdf, return_dist=False):
        """
        For each point in left_gdf, find closest point in right GeoDataFrame and return them.

        NOTICE: Assumes that the input Points are in WGS84 projection (lat/lon).

        :returns Point that is the closest to the specified coordinates
        """

        left_geom_col = left_gdf.geometry.name
        right_geom_col = right_gdf.geometry.name

        # Ensure that index in right gdf is formed of sequential numbers
        right = right_gdf.copy().reset_index(drop=True)

        # Parse coordinates from points and insert them into a numpy array as RADIANS
        left_radians = np.array(
            left_gdf[left_geom_col].apply(lambda geom: (geom.x * np.pi / 180, geom.y * np.pi / 180)).to_list())
        right_radians = np.array(
            right[right_geom_col].apply(lambda geom: (geom.x * np.pi / 180, geom.y * np.pi / 180)).to_list())

        # Find the nearest points
        # -----------------------
        # closest ==> index in right_gdf that corresponds to the closest point
        # dist ==> distance between the nearest neighbors (in meters)
        closest, dist = self.get_nearest(src_points=left_radians, candidates=right_radians)

        # Return points from right GeoDataFrame that are closest to points in left GeoDataFrame
        closest_points = right.loc[closest]

        # Ensure that the index corresponds the one in left_gdf
        closest_points = closest_points.reset_index(drop=True)

        # Add distance if requested
        if return_dist:
            # Convert to meters from radians
            earth_radius = 6371000
            closest_points['distance'] = dist * earth_radius

        return closest_points

    def calculate_distance_raster(self):
        """
        Method that is called when the calculate_distance_btn button is clicked.
        It initializes the measuring process by binding the mouse click event with the
        get_click_coordinates_raster method and updating the text inside the raster_distance_lbl label.
        """

        # Check whether the raster file is selected
        if self.raster_file is not None:

            # If it is selected, check whether the raster file is loaded onto the raster_can
            if self.raster_loaded:

                # If the raster file is selected and loaded, do the following:
                # Update the text of the specified label
                self.raster_distance_lbl.config(text='Enter the first point by clicking on the canvas...')

                # Update the label, so the new text shows immediately
                self.raster_distance_lbl.update()

                # Bind the raster_can to the mouse click (button_press_event) event, and store it in a variable
                self.connection_raster = self.raster_can.mpl_connect('button_press_event',
                                                                     self.get_click_coordinates_raster)

            # If the raster file is not loaded, display an error message
            else:
                messagebox.showerror(title='Error!',
                                     message="Raster file was not loaded!")

        # If the raster file is not selected, display an error message
        else:
            messagebox.showerror(title='Error!',
                                 message="Raster file was not selected!")

    def get_click_coordinates_raster(self, event):

        """
        Method that is called when clicked inside the raster_can when the calculate_distance_btn button is already clicked.
        It is used to update labels and bindings regarding the distance measurement.
        :param event: Represents the click event, holding information regarding it
        """
        # Increase the number of clicks inside the raster canvas by one
        self.num_of_clicks_raster += 1

        # Check if the current number of clicks is 1 or 2
        # If it is 1
        if self.num_of_clicks_raster == 1:

            # Store the longitude and latitude as a tuple inside a variable
            # ydata == latitude
            # xdata == longitude
            self.point1_ras = (event.ydata, event.xdata)

            # Update the text inside the raster_distance_lbl, in which the distance will be displayed
            self.raster_distance_lbl.config(text='Enter the second point by clicking on the canvas...')
            self.raster_distance_lbl.update()

        # If it is 2
        elif self.num_of_clicks_raster == 2:

            # Store the longitude and latitude as a tuple inside a variable
            self.point2_ras = (event.ydata, event.xdata)

            # Unbind the button_press_event from the raster canvas
            self.raster_can.mpl_disconnect(self.connection_raster)

            # Calculate the distance between the two points
            # It is wrapped inside the try-except clause so if the first method doesn't works, distance will be
            # calculated
            # using the Euclidean distance
            try:
                self.distance_ras = geopy.distance.distance(self.point1_ras,
                                                            self.point2_ras).m
            except:
                self.distance_ras = math.sqrt(
                    ((self.point1_ras[0] - self.point2_ras[0]) ** 2) + (
                            (self.point1_ras[1] - self.point2_ras[1]) ** 2))

            # Update the label and display distance in meters
            self.raster_distance_lbl.config(
                text='Distance between the two entered points in meters is:\n{}'.format(self.distance_ras))
            self.raster_distance_lbl.update()

            # Used for drawing (plotting) the line when two clicks are made
            point1 = [self.point1_ras[0], event.xdata]
            point2 = [self.point1_ras[1], event.ydata]
            x_values = [point2[0], point1[1]]
            y_values = [point1[0], point2[1]]

            self.ax.plot(x_values, y_values, markersize=4)
            self.raster_can.draw()

            # Reset number of clicks inside the raster_can to 0
            self.num_of_clicks_raster = 0

    def calculate_distance_vector(self):
        """
        Method that is called when the calculate_distance_vector_btn is clicked.
        It initializes the measuring process by binding the mouse click event with the
        get_click_coordinates_vector method and updating the text inside the vector_distance_lbl label.
        """

        # Check whether the shapefile is selected
        if self.vector_file is not None:
            # If it is selected, check whether the shapefile is loaded onto the vector_can
            if self.vector_loaded:

                # If the shapefile is selected and loaded, do the following:
                # Update the text of the specified label
                self.vector_distance_lbl.config(text='Enter the first point by clicking on the canvas...')

                # Update the label, so the new text shows immediately
                self.vector_distance_lbl.update()

                # Bind the vector_can to the mouse click (button_press_event) event, and store it in a variable
                self.connection_vector = self.vector_can.mpl_connect('button_press_event',
                                                                     self.get_click_coordinates_vector)

                # Disable the load_csv_btn button until the measuring is finished
                self.load_csv_btn.config(state=DISABLED)

            # If the shapefile is not loaded, display an error message
            else:
                messagebox.showerror(title='Error!',
                                     message="Vector file is not loaded!")

        # If the vector file is not selected, display an error message
        else:
            messagebox.showerror(title='Error!',
                                 message="No vector file was selected!")

    def get_click_coordinates_vector(self, event):

        """
        Method that is called when clicked inside the vector_can when the calculate_distance_vector_btn button is already clicked.
        It is used to update labels and bindings regarding the distance measurement.
        :param event: Represents the click event, holding information regarding it
        """

        # Increase the number of clicks inside the raster canvas by one
        self.num_of_clicks_vector += 1

        # Check if the current number of clicks is 1 or 2
        # If it is 1
        if self.num_of_clicks_vector == 1:

            # Store the longitude and latitude as a tuple inside a variable
            # ydata == latitude
            # xdata == longitude
            self.point1_vec = (event.ydata, event.xdata)

            # Update the text inside the raster_distance_lbl, in which the distance will be displayed
            self.vector_distance_lbl.config(text='Enter the second point by clicking on the canvas...')
            self.vector_distance_lbl.update()

        # If it is 2
        elif self.num_of_clicks_vector == 2:

            # Store the longitude and latitude as a tuple inside a variable
            self.point2_vec = (event.ydata, event.xdata)

            # Unbind the button_press_event from the vector canvas
            self.vector_can.mpl_disconnect(self.connection_vector)

            # Calculate the distance between the two points
            # It is wrapped inside the try-except clause so if the first method doesn't works, distance will be
            # calculated
            # using the Euclidean distance
            try:
                self.distance_vec = geopy.distance.distance(self.point1_vec, self.point2_vec).m
            except:
                self.distance_vec = math.sqrt(
                    ((self.point1_vec[0] - self.point2_vec[0]) ** 2) + ((self.point1_vec[1] - self.point2_vec[1]) ** 2))

            # Update the label and display distance in meters
            self.vector_distance_lbl.config(
                text='Distance between the two entered points in meters is:\n{}'.format(self.distance_vec))
            self.vector_distance_lbl.update()

            # Used for drawing (plotting) the line when two clicks are made
            point1 = [self.point1_vec[0], event.xdata]
            point2 = [self.point1_vec[1], event.ydata]
            x_values = [point2[0], point1[1]]
            y_values = [point1[0], point2[1]]
            self.a.plot(x_values, y_values, markersize=4)
            self.vector_can.draw()

            # Reset number of clicks inside the raster_can to 0
            self.num_of_clicks_vector = 0

            # Enable the load_csv_btn, since the operation of measuring is now finished
            self.load_csv_btn.config(state=NORMAL)

    def about(self):
        """
        Method that is called when the about_btn is clicked.
        It displays basic information about the application.
        """
        messagebox.showinfo(title='About the program',
                            message="This program is a geographic information system created by Stefan Radojević.")

    def exit(self):
        """
        Method that is called when the exit_btn is clicked.
        It closes the application.
        """
        # Close the window
        self.root.destroy()


# Main 'function'
if __name__ == '__main__':
    # Start the program
    start = GeographicInformationSystem()
