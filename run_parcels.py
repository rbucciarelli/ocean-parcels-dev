##-------------------------------------------------------------------------------------------
##- NAME: run_parcels.py
##- DESC: Advect input points in HYCOM surface current model forecast
##-       Ensure there is 
##- exec(open("run_parcels.py").read())
##-------------------------------------------------------------------------------------------
from parcels import FieldSet, ParticleSet, Variable, JITParticle, AdvectionRK4, plotTrajectoriesFile
import numpy as np
import math
import xarray as xr
##- Custom functions
from model_utils import *
from geo_utils import *
from parcels_utils import *

##- Initialize parameters
run_days = None		##- Number of days to run simulation, if None then default to entire model time bounds
stime = None		##- Time to begin simulation, defaults to T0 in dataset '%Y-%m-%dT%H:%MZ'

##- Define input data
fname_pts = './input/south-pacific-points.txt'
fname_model = '/tmp/hycom_latest.nc'

##- Define output fname
ofname = '/tmp/hycom_parcels_output.zarr'

##- Read input points and create bounding region of interest (ROI)
buf = 15.0										##- Buffer to extend ROI
P = read_csv(fname_pts)							##- Function found in geo_utils.py
bbox = bounding_box(P['lat'],P['lon'],buf)		##- Function found in geo_utils.py

##- Particle coords
plat = P['lat']
plon = P['lon']

##- Get HYCOM model data from OPeNDAP server and subset to ROI - takes a while to run
#dset = get_hycom_opendap(bbox['lon'][0],bbox['lon'][1],bbox['lat'][0],bbox['lat'][1])
dset = get_hycom_data(fname_model)
dset = hycom_subset(dset,bbox['lon'],bbox['lat'])

##- Set up parameters for parcels to run
variables = { 'U':'water_u','V':'water_v'}
dimensions = { 'lat':'lat','lon':'lon','time':'time'}
start_dt = stime
if (not run_days):
    run_days = get_model_runtime(dset.time.data)

##- Create a Parcels FieldSet object using vars/dims
fieldset = FieldSet.from_xarray_dataset(dset,variables,dimensions)

##- Create Parcels ParticleSet
pset = ParticleSet.from_list(fieldset=fieldset, pclass=JITParticle, lon=plon, lat=plat, time=start_dt)

##- Advect the particles through fieldset time/space
##- Will create a .zarr file in /tmp, need to convert this to netcdf
output_file = pset.ParticleFile(name=ofname, outputdt=timedelta(hours=1))
pset.execute(AdvectionRK4,
             runtime=timedelta(days=run_days),            					##- total length of run in days
             dt=timedelta(minutes=10),                                      ##- Timestep of kernel in min
             output_file=output_file)

##- Export results to netcdf
nc_fname = ofname.replace('.zarr','.nc')
zarr_to_nc(ofname,nc_fname)


##- Write to KML
kml_fname = nc_fname.replace('.nc','.kml')
tt = parcels_to_kml(nc_fname,kml_fname)
print("Created KML file: "+kml_fname)


