'''
Python script to generate an ensemble of Lorenz '96 model runs
--------------------------------------------------------------
Author: Man-Yau (Joseph) Chan
Date: 26 Feb 2022

Description:
------------
This script will output an ensemble of Lorenz '96 model outcomes in
the form of a netCDF4 file.
White noise is used as the initial conditions.

To run this script, just call
>> python serial_run_lorenz96.py ENSEMBLE_SIZE output_filename


IMPORTANT NOTES:
1) This Python script has no parallelization. However, multiple
   instances of this Python code can be run at the same time.
2) Since the initial conditions are randomly drawn, reruns of the
   script may not produce the same ensemble every time.
'''

# Standard packages
import numpy as np
import math as m
import sys
import os
from time import time

# NetCDF file writing package
from netCDF4 import Dataset as ncopen

# Package to run the L96 model
import L96_model as L96


# ===================================================
# Section 1: Load inputs from the command line
# ===================================================
ens_size = int(sys.argv[1])   # Ensemble size
outfname = sys.argv[2]        # Output netCDF file name


# ===================================================
# Section 2: Generate the ensemble
# ===================================================
# Setup seed for NumPy's random number generator
np.random.seed( os.getpid() )

# Initialize timer to measure ens generation time
time_start = time()

# Generate a spun-up ensemble using function from L96_model.py
ens_outcomes = L96.setup_ens( ens_size )

# Compute time taken to generate ensemble
time_taken = time() - time_start
print("Code took %5.1f seconds to generate a %d-member ensemble"
      % (time_taken, ens_size))

# ===================================================
# Section 3: Save ensemble into a netCDF4 file
# ===================================================
# Initialize file handler and buffer for the new netCDF4 file
outfile = ncopen( outfname, 'w' )

# Save time taken to run ens generation
outfile.time_taken = 'Time to generate ensemble: %5.1f seconds' % time_taken

# Initialize array dimensions
outfile.createDimension('ens_mem_id', ens_size )
outfile.createDimension('L96_gridpt', 40)

# Setting up vector of ensemble member id's and adding to netCDF4 file
mem_id = outfile.createVariable('MEMBER ID', 'i4', ('ens_mem_id',) )
mem_id.description = 'Ensemble member IDs'
mem_id[:] = np.arange( ens_size )+1

# Setting up vector of Lorenz 96 grid point locations and adding to netCDF4 file
gridpt = outfile.createVariable('GRID POINTS', 'i4', ('L96_gridpt',) )
gridpt.description = 'Integer positions of Lorenz 1996 model grid points'
gridpt[:] = np.arange(40) + 1

# Adding ensemble outcomes to netCDF4 file
ens_store = outfile.createVariable('L96 ENSEMBLE','f4',
                                   ('ens_mem_id','L96_gridpt',) )
ens_store.description = 'Ensemble of Lorenz 1996 model outcomes'
ens_store[:] = ens_outcomes*1.

# Save and close the netCDF4 file
outfile.close()
