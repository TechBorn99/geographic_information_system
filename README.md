# Geographic-Information-System

## Features
A desktop application that supports the following functionalities:
1. Selection and loading of raster and vector data (shapefiles)
2. Basic functionalities of desktop applications:
   1. Zoom In/Out,
   2. Zoom Extents,
   3. Pan, etc.
3. Displaying attributes (of vector data)
4. Loading coordinates from .csv files and generating spatial data based on those coordinates
5. Generating Delaunay's Triangulation based on points from .csv or vector files
6. Generating Convex Hull Polygon from points from .csv or vector files
7. Nearest Neighbor Search for selected coordinates
8. Calculating the distance between two selected points of a selected raster or vector file
9. Completely commented code, for easier understanding of implementation

## Requirements & How to start

Firstly, download and install Python from: https://www.python.org/downloads/

**Note:** *Python version of 3.x is required.

**Note:** The commands that follow are different if you are installing them from Anaconda terminal.

From terminal or CMD do:
1. Install **numpy** (in an environment or globally) with command: `pip install numpy`
2. Install **matplotlib** with command: `pip install matplotlib`
3. Install **rasterio**:
    1. Download appropriate version of GDAL and Fiona, based on your system and Python version from: **https://www.lfd.uci.edu/~gohlke/pythonlibs/**
    2. Change the directory to the folder in which you have downloaded the above-mentioned files
    3. Run command: `pip install [full name of the GDAL file that you have downloaded]`
    4. Run command: `pip install [full name of the Fiona file that you have downloaded]`
    
4. Install **shapefile** with command: `pip install pyshp`
5. If you previously installed GDAL and Fiona, install **geopandas** with the command: `pip install geopandas`
6. If previously mentioned packages are installed, install **descartes** with command: `pip install descartes`
7. Install **scipy** with the command: `pip install scipy`
8. Install **sklearn** with the command: `pip install sklearn`
9. Install **geopy** with the command: `pip install geopy`

