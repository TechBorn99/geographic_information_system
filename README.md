# Geographic-Information-System

This repository contains a Geographic Information System (GIS) developed in Python. It's an educational project showcasing various functionalities such as working with raster, vector, and .csv data, generating Delaunay's triangulation, creating Convex Hull Polygons, calculating distances, and performing Nearest Neighbor Searches.

## Project Status

This project is a reflection of my early career development in Python programming and GIS technology. As my focus has shifted away from Python (for now), this repository has been archived. It remains a testament to my learning journey and might be useful for those interested in basic GIS functionalities.

## Features

- **Raster, Vector, and CSV Data Handling:** Ability to work with various data formats crucial in GIS.
- **Delaunay's Triangulation:** Generating triangulations, a fundamental technique in geospatial analysis.
- **Convex Hull Polygon Generation:** Creating the smallest polygon that contains all the points in a dataset.
- **Distance Calculation:** Functionality to calculate the distance between two selected points on the Earth's surface.
- **Nearest Neighbor Search:** Implementing efficient search algorithms to find the closest points in a dataset.
- **Data Visualization:** Tools for visualizing spatial data, enhancing understanding and analysis.
- **Spatial Data Storage and Retrieval:** Efficient methods for storing and accessing geospatial information.
- **Interactive Map Interface:** Providing a user-friendly interface for interacting with geospatial data.
- **Geospatial Analysis Tools:** A suite of tools for analyzing spatial relationships and patterns.

This project serves as an early exploration into the field of GIS and offers a glimpse into the various aspects of geospatial data handling and analysis.

## Requirements & How to start

Firstly, download and install Python from: https://www.python.org/downloads/

**Note:** Python version of 3.x is required.

**Note:** The commands that follow are different if you are installing them from Anaconda terminal.

From the terminal or CMD do:
1. Install **numpy** (in an environment or globally) with the command: `pip install numpy`
2. Install **matplotlib** with the command: `pip install matplotlib`
3. Install **rasterio**:
    1. Download appropriate version of GDAL and Fiona, based on your system and Python version from: **https://www.lfd.uci.edu/~gohlke/pythonlibs/**
    2. Change the directory to the folder in which you have downloaded the above-mentioned files
    3. Run command: `pip install [full name of the GDAL file that you have downloaded]`
    4. Run command: `pip install [full name of the Fiona file that you have downloaded]`
    
4. Install **shapefile** with the command: `pip install pyshp`
5. If you previously installed GDAL and Fiona, install **geopandas** with the command: `pip install geopandas`
6. If previously mentioned packages are installed, install **descartes** with the command: `pip install descartes`
7. Install **scipy** with the command: `pip install scipy`
8. Install **sklearn** with the command: `pip install sklearn`
9. Install **geopy** with the command: `pip install geopy`

## License

This project is licensed under the Apache-2.0 License. See the LICENSE file for more details.
