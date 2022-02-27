#!/bin/bash
# ==============================================================================
# Author: Man-Yau (Joseph) Chan
# Date: 26 Feb 2022
# =============================================================================

# =============================================================================
# Description:
# -----------------------------------------------------------------------------
# Script to demonstrate the following two parallelization approaches
# 1) Run multiple concurrent copies of a single-process program via a Bash
#    for loop
# 2) Using a parallelized program without involving a Bash script
#
# For this demonstration, I will be using the Lorenz 1996 wave-on-a-ring model.
# The goal is to construct a 4000 member ensemble of forecast model outcomes.
# Both parallelization approaches will be demonstrated and compared against a
# single-process approach.
# =============================================================================

# =============================================================================
# IMPORTANT NOTES:
# -----------------------------------------------------------------------------
# 1) This Bash script (run_tests.sh) must be called within a compute node.
# 2) The parallelized program must be called with with some kind of MPI-running
#    utility. This utility can be specified using the variable "MPI_RUNNER" on
#    this Bash script. For SLURM HPCs, utility is typically either "ibrun",
#    "srun" or "mpirun".
#    I have set MPI_RUNNER=ibrun since I am using Stampede2 for this script.
# ===========================================================================

# Important variables:
# --------------------
MPI_RUNNER=ibrun
PYTHON_RUNNER=python3


# PART 1: Generating 4000-member ensemble using only a single process.
# -------------------------------------------------------------------
# Print current time and date out
echo `date`':' "Running single-process ensemble generation"

# Run the python code to generate a 4000-member ens
$PYTHON_RUNNER serial_run_lorenz96.py 4000 single_proc_L96_ens.nc

# Print current time and date to sceen
echo `date`':' "Finished running single-process ensemble generation"



# PART 2: Generate ensemble using the Bash for-loop parallelization approach
# ---------------------------------------------------------------------------
# Print current time and date out
echo `date`':' "Generating ensemble using Bash wrapper parallelization"

# Evoking 20 copies of the serial Python code
for iter in `seq -f "%02g" 1 20`; do
  $PYTHON_RUNNER serial_run_lorenz96.py 200 bash_L96_ens_"$iter".nc >& log.$iter &
done

# Wait for all 20 copies to finish running
wait

# Print current time and date out
echo `date`':' "Generated ensemble using Bash wrapper parallelization"



# PART 3: Generate ensemble using a parallelized Python code
# ----------------------------------------------------------
# Print current time and date out
echo `date`':' "Generating ensemble using explicit parallelization"

# Run parallelized Python code
$MPI_RUNNER -n 20 $PYTHON_RUNNER parallel_run_lorenz96.py 4000 mpi4py_L96_ens.nc

# Print current time and date out
echo `date`':' "Generated ensemble using explicit parallelization"
