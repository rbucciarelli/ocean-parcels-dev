#!/bin/sh

base=`date -u "+%Y-%m-%d"`

##- Get latest model run available from Hycom server  (i.e. "2022-05-18T12")
src_url="https://tds.hycom.org/thredds/catalog/GLBy0.08/expt_93.0/FMRC/runs/catalog.html"
latest=`curl -s $src_url | grep "GLBy0.08_930_FMRC_RUN" | head -1 | awk -v FS=RUN_ '{print $2}' | cut -c -13`

##- Get a date in the future plus 4 days
run=$latest":00:00Z"	#- '2022-05-18T12:00:00Z'

echo $run

#start='2022-05-18T12'
##- Get a date in the future plus 4 days
end=`date -u "+%Y-%m-%d" -d "+ 4 days"`
end=$end"T12"
echo $end
#end='2022-05-22T12'


region='north=35&west=182&east=222&south=5'		#- HI
region='north=50&west=230&east=300&south=15'	#- CONUS
region='north=40&west=110&east=170&south=1'	#- SOUTH PAC: GUAM/PALAU
url='https://ncss.hycom.org/thredds/ncss/GLBy0.08/expt_93.0/FMRC/runs/'
url=$url'GLBy0.08_930_FMRC_RUN_'$run'?var=water_u&var=water_v&'$region'&disableProjSubset=on&horizStride=1&'
url=$url'time_start='$latest'%3A00%3A00Z&time_end='$end'%3A00%3A00Z&timeStride=1&vertCoord=0&addLatLon=true&accept=netcdf4'

echo $url
wget -4 -O "/tmp/hycom_latest.nc" $url
