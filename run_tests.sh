#!/bin/bash
#####header for stampede######
#SBATCH -J L96_tests
#SBATCH -N 1
#SBATCH -n 48
#SBATCH -p skx-dev
#SBATCH -t 00:30:00
#SBATCH -o test.log
#SBATCH -e test.err

# Script to run many iterations of testing to get statistically significant results
# Parallelization control



ntid=40
tid=0
intlist="8" #"4 6 8 10 12 14 16"
ointlist="1 2 4"

# Run many iterations
for oint in $ointlist; do
  for nint in $intlist; do
    echo Running cyc_int $nint obs_int $oint
    for ii in `seq -f "%04g" 1 40`; do
      python3 sensitivity_runs.py $nint $oint $ii >& log.$nint'_'$oint'_'$ii &
      tid=$(($tid+1))
      if [[ $tid == $ntid ]]; then
        wait
        tid=0
      fi
    done
  done
done
# Wait for parallel threads to complete
wait


mkdir all_sensitivities
mv log* all_sensitivities
mv *npy all_sensitivities

exit
