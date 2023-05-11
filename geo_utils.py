import csv
from csv import DictReader
import numpy as np

##- Function to convert longitudes from -180:180 to 0:360
def lons_180_360(lon):
    return (lon + 180) % 360 - 180

##- Passed lists of lats/lons, compute bounding box + buffer in degrees
def bounding_box(lats,lons,buff=0):
    min_lat = np.min(lats) - buff
    min_lon = np.min(lons) - buff   
    max_lon = np.max(lons) + buff
    max_lat = np.max(lats) + buff
    return {'lat':[min_lat,max_lat],'lon':[min_lon,max_lon]}

##- Read csv into dictionary
def read_csv(input_csv):
    with open(input_csv,'r') as f:
        dict_reader = list(DictReader(f))
    D = {}
    for k in dict_reader[0].keys():
        #D[k] = list(float(D[k]) for D in dict_reader)
        D[k] = list(float(D[k]) for D in dict_reader)
    #return dict_reader
    return D
    
 

