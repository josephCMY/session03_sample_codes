# Additional Sample Codes for Session 3 of the PSU-EnKF Spring 2022 Workshop
Author: Man-Yau (Joseph) Chan
Date: 26 Feb 2022


## Description
Script to demonstrate the following two parallelization approaches
1) Run multiple concurrent copies of a single-process program via a Bash
   for loop
2) Using a parallelized program without involving a Bash script

For this demonstration, I will be using the Lorenz 1996 wave-on-a-ring model.
The goal is to construct a 4000 member ensemble of forecast model outcomes.
Both parallelization approaches will be demonstrated and compared against a
single-process approach.



## IMPORTANT NOTES
1) This Bash script (run_demonstrations.sh) must be called within a compute node.
2) The parallelized program must be called with with some kind of MPI-running
   utility. This utility can be specified using the variable "MPI_RUNNER" on
   this Bash script. For SLURM HPCs, utility is typically either "ibrun",
   "srun" or "mpirun".
   I have set MPI_RUNNER=ibrun since I am using Stampede2 for this script.

## Components
1) Main script: `run_demonstrations.sh` 
2) Python code containing Lorenz 1996 model code: `L96_model.py`
3) Python code to generate many Lorenz 1996 model runs without explicit parallelization: `serial_run_lorenz96.py`
4) Python code to generate many Lorenz 1996 model runs with explicit parallelization: `parallel_run_lorenz96.py`

To see how I explicitly parallelized the `parallel_run_lorenz96.py`, compare `parallel_run_lorenz96.py` and `serial_run_lorenz96.py`. 

