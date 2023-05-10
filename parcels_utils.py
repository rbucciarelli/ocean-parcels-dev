import netCDF4
import numpy as np
from datetime import datetime, timedelta
import csv
import simplekml
import json
from geojson import Feature, Point, FeatureCollection, LineString, dump
## exec(open("parcels_utils.py").read())


##- Try opening up remote opendap resource, from CDIPPY
def get_nc(url):
    try:
        nc = netCDF4.Dataset(url)
    except:
        nc = None
    return nc

def get_var(nc,var_name):
    if (nc is None) or (var_name not in nc.variables):
        return None
    else:
        return nc.variables[var_name]

##- Calculate distance based on Haversine formula.  
##- If performance issue, consider vector implementation instead of scalar input
def calc_dist(lon1,lat1,lon2,lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    dist = 6371 * c
    bearing =np.arctan2(np.cos(lat1)*np.sin(lat2)-np.sin(lat1)*np.cos(lat2)*np.cos(lon2-lon1), np.sin(lon2-lon1)*np.cos(lat2)) 
    data={'distance':dist,'bearing':np.degrees(bearing)}
    return data

def calc_bearing(lon1,lat1,lon2,lat2):
    bearing =np.arctan2(cos(lat1)*np.sin(lat2)-np.sin(lat1)*np.cos(lat2)*np.cos(lon2-lon1), np.sin(lon2-lon1)*np.cos(lat2)) 
    bearing = np.degrees(bearing)

##- Passed vectors of lon,lat,time compute metrics: distance, speed, & bearing
def calc_metrics(lon,lat,time):
    data = {}
    data['lon'] = list(lon)
    data['lat'] = list(lat)
    data['time'] = time
    data['time_str'] = [x.strftime("%Y-%m-%dT%H:%M:%SZ") for x in time]
    data['distance'] = [0.0]
    data['bearing'] = [0.0]
    data['speed'] = [0.0]
    for i in range(len(lon)):
        if (i > 0):
            dist_data = calc_dist(lon[i-1],lat[i-1],lon[i],lat[i])
            data['distance'].append(dist_data['distance']*1000)
            data['bearing'].append(dist_data['bearing'])
            dt = time[i] - time[i-1]
            data['speed'].append(dist_data['distance']*1000/dt.total_seconds())
    return data

##- Get a string of line coordinates
def line_coords(D):
    coords = []
    for i in range(len(D['lon'])):
        coords.append((D['lon'][i],D['lat'][i],0.0))
    return coords

def write_schema(kml,shape):
# Create a schema for extended data: heart rate, cadence and power
    schema = kml.newschema()
    schema.newgxsimplearrayfield(name='longitude', type=simplekml.Types.float, displayname='Longitude')
    schema.newgxsimplearrayfield(name='latitude', type=simplekml.Types.float, displayname='Latitude')
    schema.newgxsimplearrayfield(name='time', type=simplekml.Types.string, displayname='Time')
    schema.newgxsimplearrayfield(name='distance', type=simplekml.Types.float, displayname='Distance (m)')
    schema.newgxsimplearrayfield(name='speed', type=simplekml.Types.float, displayname='Speed (m/s)')
    schema.newgxsimplearrayfield(name='bearing', type=simplekml.Types.float, displayname='Bearing')
     

def write_kml(data):
    kml = simplekml.Kml()
    ##- Initialize
    now = datetime.utcnow()
    datestr = now.strftime("%Y-%m-%d %H:%M:%SZ")
    start_time = data[0]['time'][0]
    end_time = data[0]['time'][-1]
    N = len(data[0]['lon'])
    look_lon = data[0]['lon'][round(N/2)]
    look_lat = data[0]['lat'][round(N/2)]

    doc = kml.newdocument(name='Parcels Output', snippet=simplekml.Snippet('Created '+datestr))
    doc.lookat.gxtimespan.begin = start_time.strftime() #'2010-05-28T02:02:09Z'
    doc.lookat.gxtimespan.end = end_time.strftime() #'2010-05-28T02:02:56Z'
    doc.lookat.longitude = look_lon
    doc.lookat.latitude = look_lat
    ##- Set scale to encompass all of the particles
    doc.lookat.range = np.sum(data[0]['distance']) * len(data)

    fol = doc.newfolder(name='Particle Tracks')
    ##- Create a multitrack object
    #multitrack = kml.newgxmultitrack(name="HYCOMM Parcels Output")
    multitrack = fol.newgxmultitrack()
    #data = [data[0]]
    for i in range(len(data)):
        #fol = doc.newfolder(name='Particle Track: '+str(i))

        D = data[i]

        ##- Format data for use in google earth
        coords = line_coords(D)
        when = [x.strftime("%Y-%m-%dT%H:%M:%SZ") for x in D['time']]
        ge_lat = ["%.6f" % x for x in  D['lat']]
        ge_lon = ["%.6f" % x for x in  D['lon']]
        ge_distance = ["%.1f" % x for x in  D['distance']]
        ge_bearing = ["%.1f" % x for x in  D['bearing']]
        ge_speed = ["%.1f" % x for x in  D['speed']]

        #fol = doc.newfolder(name='Particle Track: '+str(i))

        ##- Create a schema for extended data: lon,lat,distance,speed,bearing 
        schema = kml.newschema()
        schema.newgxsimplearrayfield(name='longitude', type=simplekml.Types.float, displayname='Longitude')
        schema.newgxsimplearrayfield(name='latitude', type=simplekml.Types.float, displayname='Latitude')
        schema.newgxsimplearrayfield(name='distance', type=simplekml.Types.float, displayname='Distance (m)')
        schema.newgxsimplearrayfield(name='speed', type=simplekml.Types.float, displayname='Speed (m/s)')
        schema.newgxsimplearrayfield(name='bearing', type=simplekml.Types.float, displayname='Bearing')

        #- Add start/end points
        start_name = "Start Particle-"+str(i)
        pnt = fol.newpoint(name=start_name,coords=[(D['lon'][0],D['lat'][0])])
        pnt.style.scale = 1
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/grn-circle-lv.png'
        pnt.style.labelstyle.color = '9958d68d '
        pnt.style.labelstyle.scale = 0.25
        end_name = "End Particle-"+str(i)
        pnt = fol.newpoint(name=end_name,coords=[(D['lon'][-1],D['lat'][-1])])
        pnt.style.scale = 0.75 
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-diamond-lv.png'
        pnt.style.labelstyle.color = 'ff0000ff' 
        pnt.style.labelstyle.scale = 0.25

        # Create a new track in the folder
        #trk = fol.newgxtrack(name='Particle '+str(i))
        trk = multitrack.newgxtrack(name='Particle '+str(i)) 

        # Apply the above schema to this track
        trk.extendeddata.schemadata.schemaurl = schema.id

        # Add all the information to the track
        trk.newwhen(when) # Each item in the give nlist will become a new <when> tag
        trk.newgxcoord(coords) # Ditto
        trk.extendeddata.schemadata.newgxsimplearraydata('longitude', ge_lon)
        trk.extendeddata.schemadata.newgxsimplearraydata('latitude', ge_lat)
        trk.extendeddata.schemadata.newgxsimplearraydata('distance', ge_distance)
        trk.extendeddata.schemadata.newgxsimplearraydata('speed', ge_speed)
        trk.extendeddata.schemadata.newgxsimplearraydata('bearing', ge_bearing)

        # Styling
        trk.stylemap.normalstyle.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
        trk.stylemap.normalstyle.linestyle.color = '99ffac59'
        trk.stylemap.normalstyle.linestyle.width = 4
        trk.stylemap.highlightstyle.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
        trk.stylemap.highlightstyle.iconstyle.scale = 1.2
        trk.stylemap.highlightstyle.linestyle.color = '99ffac59'
        trk.stylemap.highlightstyle.linestyle.width = 8
        
    multitrack.stylemap.normalstyle.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
    multitrack.stylemap.normalstyle.linestyle.color = '99ffac59'
    multitrack.stylemap.normalstyle.linestyle.width = 4
    multitrack.stylemap.highlightstyle.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'

     
 
    return kml

def parcels_to_kml(particle_nc,out_kml):
    pfile=get_nc(particle_nc)
    ##- Get the identifier for each unique particle trajectory
    traj= np.ma.filled(pfile.variables['trajectory'], np.nan)
    lon = np.ma.filled(pfile.variables['lon'], np.nan)
    lon = (lon + 180)%360 - 180   ##- Format longitudes -180 to +180
    lat = np.ma.filled(pfile.variables['lat'], np.nan)
    time_var = pfile.variables['time']
    dtime = netCDF4.num2date(time_var[:],time_var.units)
    time = np.ma.filled(dtime, np.nan)
    pfile.close()

    ##- Iterate over diff trajectories and create Dict object
    D = []
    for i in range(len(traj)):
        data = calc_metrics(lon[i,:],lat[i,:],time[i,:])
        D.append(data)

    ##- Call function to write kml for each trajectory
    print("Creating KML: "+out_kml)
    kml = write_kml(D) 
    kml.save(out_kml)
    return D 

##- Function to format values from dictionary to json format
def format_json(D):
    J = {}
    time = [x.isoformat() + "Z" for x in D['time']]
    lat = [float(x) for x in D['lat']]
    lon = [float(x) for x in D['lon']]
    dist = [float(x) for x in D['distance']]
    speed = [float(x) for x in D['speed']]
    bearing = [float(x) for x in D['bearing']]
    J={'time':time,'lon':lon,'lat':lat,'distance':dist,'speed':speed,'bearing':bearing}
    return J

def create_geojson(D):
    coords = line_coords(D)
    line_feature = Feature(geometry=LineString(coords)) 
    line_feature['properties'] = {"popupContent":'HYCOMM particle track starting: '+D['time'][0]+
                                 ' and ending: '+D['time'][-1]}
    feat_list = [line_feature]
    for i in range(len(D['lat'])):
        props = {"Time":D['time'][i],"Distance":D['distance'][i],"Speed":D['speed'][i],"Bearing":D['bearing'][i]}
        pt = Feature(geometry=Point((D['lon'][i],D['lat'][i])),properties=props)
        feat_list.append(pt)
    features = FeatureCollection(feat_list)
    return features

'''
if __name__ == '__main__':
    fname="./output/parcels_hycom.nc"
    fname="/tmp/parcels_2022-05-18T042550.321134.nc"
    ofname=fname.replace('.nc','.kml')
    ##- Call script to output kml and return data
    D = parcels_to_kml(fname,ofname)

    ##- Output to JSON for web viewing 
    J = format_json(D[0])
    json_fname = ofname.replace(".kml",".json")
    geojson_obj = create_geojson(J)
    
    json_fname = ofname.replace(".kml",".geojson")
    with open(json_fname,"w") as outfile:
        dump(geojson_obj, outfile) 
'''
