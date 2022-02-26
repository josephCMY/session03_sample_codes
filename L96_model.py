'''
Python functions to integrate Lorenz '96 model

Dimensions of x_ens: [ens, variable]

'''

import numpy as np
import math as m
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

''' User controls '''
# Model integration variables based on original paper
F=8.0
dt=0.025 # ~ 3 hours


''' Model forward stepping function '''
def multistep( x_ens, n_steps ):
  # Iterative counter
  ii = 0
  # Run while loop
  while ii < n_steps:
    x_ens[:] = rk4(x_ens)
    ii += 1
  return x_ens


''' Runge-Kutta 4th order integration function '''
def rk4(x_ens):
  k1 = dt * dxdt( x_ens)
  k2 = dt * dxdt( x_ens+k1/2.0)
  k3 = dt * dxdt( x_ens+k2/2.0)
  k4 = dt * dxdt( x_ens+k3)
  return x_ens + k1/6 + k2/3 + k3/3 + k4/6



''' Function to compute time derivative of state '''
def dxdt( x_ens ):
  # Find number of variables in system
  nx = x_ens.shape[1]
  # Number of ensemble members
  ne = x_ens.shape[0]
  # Initialize memory to hold rate of change
  rate = x_ens * 0.0
  # Compute advection term in interior points
  rate[:,2:-1] = (x_ens[:,3:] - x_ens[:,:-3]) * x_ens[:,1:-2]
  # Compute advection term in boundary points
  rate[:, 0] = (x_ens[:,1] - x_ens[:,-2])*x_ens[:,-1]
  rate[:, 1] = (x_ens[:,2] - x_ens[:,-1])*x_ens[:, 0]
  rate[:,-1] = (x_ens[:,0] - x_ens[:,-3])*x_ens[:,-2]
  # Add in self-decay term
  rate -= x_ens
  # Add in forcing term
  rate += F
  return rate


''' Function to spin up an ensemble '''
def setup_ens( n_ens ):
  x_ens = np.random.normal( loc=0, scale=1.0, size=[n_ens,40])
  # Spinup
  x_ens = multistep( x_ens * 1.0, 1000 )
  return x_ens


# Sanity check the model dynamics
if __name__ == '__main__':
  traj = np.zeros( [201, 1, 40] , dtype=np.float)
  traj[0,0,:] = np.random.normal(loc=0, scale=1.0, size=40)
  # Spin up
  traj[0,:,:] = multistep( traj[0,:,:] * 1.0, 1000)
  tt = 0
  while tt < 200:
    traj[tt+1,:,:] = multistep( traj[tt,:,:] * 1.0, 1)
    tt += 1
  fig = plt.figure(figsize=(4,6))
  cnf = plt.contourf( traj[:,0,:], cmap = plt.cm.RdBu_r )
  plt.colorbar()
  plt.savefig('sanity_check_model.png', bbox_to_inches='tight',dpi=100)
