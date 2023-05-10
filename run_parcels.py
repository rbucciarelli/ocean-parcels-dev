##- run_parcels.py
##exec(open("run_parcels.py").read())

from geo_utils import *

##- Define input data
fname_pts = './input/south-pacific-points.txt'

##- Read input points and create bounding region of interest (ROI)
buf = 15.0										##- Buffer to extend ROI
D = read_csv(fname_pts)							##- Function found in geo_utils.py
bbox = bounding_box(D['lat'],D['lon'],buf)		##- Function found in geo_utils.py


