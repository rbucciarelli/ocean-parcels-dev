#!/bin/sh
##--------------------------------------------------------------------------------------------------------- 
##- NAME: 	download_hycom.sh
##- DESC: 	Download HYCOM Forecast or Hindcast data from HYCOM THREDDS Server
##- USAGE:  Supply input date (YYYY-MM-DD) for hindcast plus X days 
##-         download_hycom.sh <YYYY-MM-DD>
##- NOTE: HYCOM data server can be flaky, not much error checking done
##-       You can also download manually from server here: https://tds.hycom.org/thredds/catalogs/GLBy0.08/expt_93.0.html
##--------------------------------------------------------------------------------------------------------- 
base=`date -u "+%Y-%m-%d"`

ofname="/tmp/hycom_latest.nc"

##- Check for YYYYMMDD as input, if not supplied then default to latest forecast
if [ $# -eq 0 ]; then
    ##- Get latest model run available from Hycom server  (i.e. "2022-05-18T12")
    src_url="https://tds.hycom.org/thredds/catalog/GLBy0.08/expt_93.0/FMRC/runs/catalog.html"
    latest=`curl -s $src_url | grep "GLBy0.08_930_FMRC_RUN" | head -1 | awk -v FS=RUN_ '{print $2}' | cut -c -13`
    #start=$latest":00:00Z"	#- '2022-05-18T12:00:00Z'
    start=$latest	#- 2022-05-18T12
    ##- Get a date in the future plus 6 days
    end=`date -u "+%Y-%m-%d" -d "+ 5 days"`
    end=$end"T12"
    data_url='https://ncss.hycom.org/thredds/ncss/GLBy0.08/expt_93.0/FMRC/runs/GLBy0.08_930_FMRC_RUN_'$start
else
    ##- Get hindcast model run plus 7 days from Hycom server  (i.e. "2022-05-18T12")
    start=$1			#- YYYY-MM-DD
    ##- Get a date in future from start plus 6 days
    end=`date '+%Y-%m-%d' -d "$start+7 days"`
    start=$1"T12"		#- YYYY-MM-DDT12
    end=$end"T12"
    echo $start
    echo $end
    data_url='https://ncss.hycom.org/thredds/ncss/GLBy0.08/expt_93.0/uv3z'
fi

echo "START: $start"
echo "END: $end"

##- Define region to extract from global grid (currently manually entered below)
#region='north=35&west=182&east=222&south=5'		#- HI
#region='north=50&west=230&east=300&south=15'	#- CONUS
region='north=40&west=110&east=170&south=-20'	#- SOUTH PAC: GUAM/PALAU

##- Assemble data url
data_url=$data_url'?var=water_u&var=water_v&'$region'&disableProjSubset=on&horizStride=1&'
data_url=$data_url'time_start='$start'%3A00%3A00Z&time_end='$end'%3A00%3A00Z&'
data_url=$data_url'timeStride=1&vertCoord=0&addLatLon=true&accept=netcdf4'

echo $data_url
wget -4 -O $ofname $data_url
