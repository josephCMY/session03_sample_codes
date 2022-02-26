'''
Parallelized Python script to generate an ensemble of Lorenz '96 model runs
----------------------------------------------------------------------------
Author: Man-Yau (Joseph) Chan
Date: 26 Feb 2022

Description:
------------
This script will output an ensemble of Lorenz '96 model outcomes in
the form of a netCDF4 file.
White noise is used as the initial conditions.
This parallelized script splits the ensemble generation among the processes.
If there are 20 processes, each process will generate ceil(ens_size/20) ensemble
members. The script will then combine the 20 processes' worth of members, and
output ens_size members into a single netCDF4 file.

To run this script, just call
>> python serial_run_lorenz96.py ENSEMBLE_SIZE output_filename


IMPORTANT NOTES:
1) Since the initial conditions are randomly drawn, reruns of the
   script may not produce the same ensemble every time.
'''

# Standard packages
import numpy as np
import math as m
import sys
import os
from time import time
from mpi4py import MPI

# NetCDF file writing package
from netCDF4 import Dataset as ncopen

# Package to run the L96 model
import L96_model as L96


# =============================================================
# Section 1: Load inputs from the command line
# =============================================================
ens_size = int(sys.argv[1])   # Ensemble size
outfname = sys.argv[2]        # Output netCDF file name


# ============================================================
# Section 2: Initialize inter-process communication interface
#            (aka, Message Passing Interface, or MPI)
# ============================================================
# Initialize global communicator ring
comm = MPI.COMM_WORLD

# Determine rank of process in the global communicator ring.
# This rank is unique to each process in the communicator ring.
# Will use this rank as the process id.
my_proc_id = comm.Get_rank()

# Determine total number of processes
nprocs = comm.Get_size()

# Determine how many members each process needs to generate
sub_ens_size = m.ceil( ens_size / nprocs )

# Note that sub_ens_size * nprocs is likely > ens_size.
# To handle this I will define the overflow ensemble size:
overflow_ens_size = sub_ens_size * nprocs



# ============================================================
# Section 3: Generate the ensemble
# ============================================================
# Setup seed for NumPy's random number generator
np.random.seed( my_proc_id )

# Waiting for all processes to reach this line
comm.Barrier()

# Initialize timer to measure ens generation time
time_start = time()

# Generate a spun-up ensemble using function from L96_model.py
ens_outcomes = L96.setup_ens( sub_ens_size )

# Wait for all processes to reach this line
comm.Barrier()

# Compute time taken to generate ensemble
time_taken = time() - time_start


# ============================================================
# Section 4: Gather all ensemble members from all processes
#            to root process (my_proc_id = 0)
# ============================================================
# Initialize array to hold all created members at root process
if my_proc_id == 0:
  overflow_ens = np.zeros( [overflow_ens_size, 40] ) *1.
else:
  overflow_ens = None

# Gather members to root process
comm.Gather( ens_outcomes, overflow_ens, root = 0)



# ===========================================================
# Section 5: Root process saves ensemble into a netCDF4 file
# ===========================================================
# Only root process does the file writing
if my_proc_id == 0:

  # Saving only the desired number of ensemble members
  ens_outcomes = overflow_ens[0:ens_size,:]

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


# Wait for all processes to clear before exiting
comm.Barrier()
