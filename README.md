# ocean-parcels-dev
Ocean Parcels implementation for buoy tracking

<!-- GETTING STARTED -->
### Installation

_Below instructions build Conda environment to get Ocean Parcels up and running._

1. Install [Miniconda](https://https://conda.io/docs/user-guide/install/)

2. Clone the repo
   ```sh
   git clone https://github.com/rbucciarelli/ocean-parcels-dev.git
   ```
3. Create conda environment and activate it
   ```sh
   conda create -n parcels_dev
   conda install nb_conda_kernels
   conda activate parcels_dev
   ```
4. Install required libraries
   ```sh
   conda install -c conda-forge parcels jupyter matplotlib cartopy
   conda install -c conda-forge ffmpeg numpy xarray pandas
   conda install -c conda-forge geojson requests simplekml
   conda activate parcels_dev
   ```


### Running example

_Below is a sample workflow to download HYCOM data and advect sample points through time/space._

1. Set up input points to work with (Note: Longitudes need to be from 0-360 deg)
   ```sh
   $ ./input/south-pacific-points.txt
   ```
2. Download subset of HYCOM model using region of interest (ROI) derived from input points. Will output to /tmp/hycom\_latest.nc
   ```sh
   ##- Run the following shell script
   $ ./download_hycom.sh				##- Latest forecast + 7 days
   $ ./download_hycom.sh 2021-04-12		##- Hindcast start date + 7 days
   ```

3. Advect particles through time using Parcels by running python script (either from command line or notebook)
   ```sh
   $ python run_parcels.py
   $ jupyter notebook
   ```

3. View output point trajectories in kml or netcdf format

