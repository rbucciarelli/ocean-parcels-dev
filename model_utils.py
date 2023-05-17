import numpy as np
from datetime import timedelta,datetime
import xarray as xr

##- Function to convert zarr file to netcdf
def zarr_to_nc(fname_zarr,fname_nc):
    try:
        dset = xr.open_dataset(fname_zarr,engine='zarr')
        dset.to_netcdf(fname_nc)
        print("Created NetCDF file: "+fname_nc)
    except:
        print("model_utils.py: Could not convert zarr file: "+fname_zarr)

##- Function to compute total time duration in days from model
def get_model_runtime(times):
     duration = times[-1] - times[0]
     total_days = duration/np.timedelta64(1,'D')
     return total_days

##- Create a list of datetime objects for FMRC forecast time steps
def hycom_fix_times(dset):
    tinfo = dset.time.attrs
    attrs = tinfo['units']  #- 'hours since 2022-03-19 12:00:00.000 UTC'
    units, reference_date = attrs.split(' since ')
    dt0= datetime.strptime(reference_date,'%Y-%m-%d %H:%M:%S.%f UTC')
    hours = dset.time.data
    hours = np.array([timedelta(hours=i) for i in hours])
    ctime = dt0 + hours
    return ctime
    
##- Clip model to bounding box lats=[min_lat,max_lat]
def hycom_subset(dset,lons,lats):
    ##- Clip dset to ROI bounds
    D = dset.sel( lat=slice(lats[0],lats[1]), lon=slice(lons[0],lons[1]),depth=slice(0,0))
    D = D.squeeze()
    return D

##- Subset aggregated HYCOM data from their OPeNDAP server
def get_hycom_data(fname=None):
    ##- Open dataset using xarray - need to skip decoding times for now
    dset = xr.open_dataset(fname)
    return dset

##- Subset aggregated HYCOM data from their OPeNDAP server
def get_hycom_opendap(fname=None):
    ##- If no fname provided, then get data from OPeNDAP server, which takes forever
    if(not fname):
        fname = 'https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/FMRC/GLBy0.08_930_FMRC_best.ncd'
    ##- Open dataset using xarray - need to skip decoding times for now
    dset = xr.open_dataset(fname,decode_times=False)
    
    ##-Fix times 
    ctime = hycom_fix_times(dset)

    ##- Cleanup dataset removing vars not needed and add time
    D = dset.drop(['tau','time_offset','water_u_bottom','water_v_bottom','water_temp_bottom','salinity','salinity_bottom'])
    D['time'] = ctime
    return D
