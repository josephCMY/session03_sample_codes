''' 
Sensitivity experiments for various ensemble filters 

Outer bash script will control numpy seeding, cycling interval and obs interval

This Python script will perform both the extended and unextended state ensemble filters, with and without inflation 
'''

# Standard libraries
import numpy as np
import math as m
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys

# Experiment libraries
from model import multistep, dxdt
from ens_filters import BiGauss_EnF, EnKF
from setup_ens import setup_ens
from obs_operator import pseudo_ch8 as obs_op
from obs_operator import observe

''' User controls '''
# Outer controls
cyc_int = int(sys.argv[1])
obs_int = int(sys.argv[2])    # Spacing between observations
expt_num = int(sys.argv[3])

# Inner controls 
n_ens = 800
obs_sigma = 1.0
xpos = np.arange(40)[::obs_int]
n_obs = len(xpos)
totsteps = 800
n_cyc = int(totsteps/cyc_int)
flag_examples=True
infl_list = [True]
sp_list = ['non']
algo_list = ['EnKF', 'BGEnF_DDR', 'BGEnF_EnS']
''' Setting up expt '''
# Seeding for reproducibility of experimental conditions
np.random.seed(expt_num)

# Set up ensemble
ens = setup_ens( n_ens+1 )


''' Initialize results container '''
results = {}
results['NoDA'] = np.zeros([ n_cyc, n_ens, 40], dtype=np.float)
results['NoDA'][0] = ens[1:]*1.0
results['dxdt'] = np.zeros([n_cyc, n_ens], dtype=np.float )
results['dxdt'][0,:] = np.sqrt( np.mean( np.power( dxdt( ens[1:]*1.0 ),2), axis=-1 ))
results['xt'] = np.zeros([n_cyc, 40], dtype=np.float)
results['xt'][0] = ens[0]*1.0
for sp in sp_list:
  results[sp] = {}
  for infl in infl_list:
    results[sp][infl] = {}
    for algo in algo_list:
      results[sp][infl][algo] = {}
      results[sp][infl][algo]['xf'] = np.zeros([n_cyc, n_ens, 40], dtype=np.float)
      results[sp][infl][algo]['xf'][0] = ens[1:,:] * 1.0
      results[sp][infl][algo]['xa'] = np.zeros([n_cyc, n_ens, 40], dtype=np.float )
      results[sp][infl][algo]['dxdt'] = np.zeros([n_cyc, n_ens], dtype=np.float )


''' Now perform many cycle experiment '''
cyc = 0
while cyc <= n_cyc:

  ''' Generate observations with obs interval '''
  print('\nCycle #: %d' %cyc)

  obs, flags = observe( results['xt'][cyc], obs_op, obs_sigma )
  obs = obs[xpos]

  ''' Non-extended state space DA'''
  sp = 'non'
  # Whether or not to inflate prior perturbations
  for infl in infl_list:
    # Various algorithms
    for algo in algo_list:
    
      # Calling the prior ens
      xf = results['non'][infl][algo]['xf'][cyc, :,:] * 1.0
  
      # Adaptive inflation scheme for BiGauss EnF
      if infl:
        yf, flags= obs_op(xf)
        yf = yf[:,xpos]
        d = np.mean(np.power( np.mean(yf, axis=0) - obs, 2))
        sprd = np.mean(np.var( yf, axis=0, ddof=1) + obs_sigma*obs_sigma)
        fac = np.sqrt( d/sprd )
        if fac < 1.0:
          fac = 1.0  
        # Inflate!
        xf_avg = np.mean(xf, axis=0)
        xf_perts = (xf - xf_avg) * fac
        xf = xf_perts + xf_avg
  
      # Serial filter in state space
      for oo in range(n_obs):
        # Generating local observation
        yf, flags = obs_op( xf )
        yf = yf[:,xpos[oo]]
        flags = flags[:,xpos[oo]]
#        print(flags[:10])
#        flags = yf>250
#        print("")
#        print(flags[:10])
#        quit()
        if algo == 'EnKF':
          output = EnKF( xf*1.0, yf*1.0, obs[oo], obs_sigma, xpos[oo])
        elif algo == 'BGEnF_DDR':
          output = BiGauss_EnF( xf*1.0, yf*1.0, obs[oo], obs_sigma, flags, xpos[oo], shift_algo='ddr2011')
        elif algo == 'BGEnF_EnS':
          output = BiGauss_EnF( xf*1.0, yf*1.0, obs[oo], obs_sigma, flags, xpos[oo], shift_algo='LineComb') 

        # Update quantities before going to the next observation
        xf = output['xa'][:] * 1.0
    
      # Storing final analysis 
      results[sp][infl][algo]['xa'][cyc,:] = output['xa'][:]
      results[sp][infl][algo]['dxdt'][cyc,:] = np.sqrt( np.mean( np.power( dxdt( output['xa']*1.0 ),2), axis=-1 ))

#  ''' Extended state space DA'''
#  sp = 'ext'
#  # Whether or not to inflate prior perturbations
#  for infl in [True]:
#    # Various algorithms
#    for algo in ['EnKF','BiGauss_EnF']:
#    
#      # Calling the prior ens
#      xf = results['non'][infl][algo]['xf'][cyc, :,:] * 1.0
#      
#      # Adaptive inflation scheme for BiGauss EnF
#      if infl:
#        yf = obs_op(xf)[:,xpos]
#        d = np.mean(np.power( np.mean(yf, axis=0) - obs, 2))
#        sprd = np.mean( np.var( yf, axis=0, ddof=1)) + obs_sigma*obs_sigma
#        fac = m.sqrt( d/sprd )
#        if fac < 1.0:
#          fac = 1.0  
#        # Inflate!
#        xf_avg = np.mean(xf, axis=0)
#        xf_perts = (xf - xf_avg) * fac
#        xf = xf_perts + xf_avg
#
#      # Generating the simulated obs and extending the state space
#      yf = obs_op(xf)[:,xpos]
#      psif = np.zeros( [n_ens, 40 + len(xpos)], dtype=np.float) 
#      psif[:,:40] = xf*1.0
#      psif[:,40:] = yf*1.0
#
#      # Serial filter
#      for oo in range(n_obs):
#        # Generating local observation
#        yf = psif[:,40+oo]
#  
#        if algo == 'EnKF':
#          output = EnKF( psif*1.0, yf*1.0, obs[oo], obs_sigma, xpos[oo])
#        elif algo == 'BiGauss_EnF':
#          flags = yf[:] > 260.      # Clustering flag
#          output = BiGauss_EnF( psif*1.0, yf*1.0, obs[oo], obs_sigma, flags, xpos[oo], shift_algo='eigenstate' )  
#        # Update quantities before going to the next observation
#        psif = output['xa'][:] * 1.0
#    
#      # Storing final analysis 
#      results[sp][infl][algo]['xa'][cyc,:] = output['xa'][:,:40]

  # Stop if cycle = n_cyc
  if cyc == n_cyc-1:
    break

  # Run forward integration
  ens[0] = results['xt'][cyc,:]
  ens[1:] = results['NoDA'][cyc,:]
  ens = multistep( ens*1.0, cyc_int )
  results['xt'][cyc+1,:] = ens[0]
  results['NoDA'][cyc+1,:] = ens[1:]
  results['dxdt'][cyc+1,:] = np.sqrt( np.mean( np.power( dxdt( ens[1:]*1.0 ),2), axis=-1 ))

  for algo in algo_list:
    for infl in infl_list:
      for sp in sp_list:
        results[sp][infl][algo]['xf'][cyc+1,:] = multistep( results[sp][infl][algo]['xa'][cyc,:]*1.0, cyc_int)
        if np.sum( np.isnan( results[sp][infl][algo]['xf'][cyc+1])):
          print( 'Algo %s %s has NaN' % (algo, sp) )
#          quit()          
          
  cyc+=1

if flag_examples:
  print('Looking at ensemble at end of cycles')
  for algo in algo_list:
    for ss in ['xa','xf']:
      fig = plt.figure(figsize=(3,3))
      ens = results['non'][True][algo][ss][n_cyc-1,:,:] 
      extreme_flags = (ens > 15) + (ens < -8 )
      extreme_flags = np.sum( extreme_flags, axis=-1) > 0
      plt.plot( np.arange(40)+1, results['xt'][n_cyc-1], color='k', zorder=5000, label = 'Truth')
      plt.plot( np.arange(40)+1, np.mean( ens, axis=0), color = 'r', zorder=4000, label='Ens mean')
      for ee in range( n_ens):
        plt.plot( np.arange( 40)+1, ens[ee,:], color='lightgray', linewidth=0.5)
        if ee == 0:
          plt.plot( np.arange( 40)+1, ens[ee,:], color='lightgray', linewidth=0.5, label='Ens members')

      plt.title( algo ) 
      print('%s %s with extreme values: %5.2f %%' % (algo,ss, np.sum(extreme_flags)*100.0/n_ens))
      fig.subplots_adjust(left=0.2,right=0.9,top=0.85,bottom=0.35)
      if algo == 'BGEnF_EnS':
        plt.legend( loc = 'upper center', bbox_to_anchor = (0.4,-0.3), ncol=2)
      plt.ylabel('L96 variable')
      plt.xlabel('Position')
      plt.ylim([-20,20])
      plt.savefig( '%s_%s_ensemble_cycint%02d_obsint%02d_%04d.png' %(algo, ss, cyc_int, obs_int, expt_num), dpi=300)
      plt.close()
  quit()

   
    
print('Storing RMS outputs of the experiment')
# Now compute the RMSE, RMSS and storing outcome in numpy files
algo_list2 = [ val for val in algo_list]
algo_list2.append('NoDA')
for algo in algo_list2:
  # Special handling for NoDA
  if algo == 'NoDA':
    rmse = np.mean( results[algo], axis=1) - results['xt']
    rmse = np.sqrt( np.mean( np.power( rmse,2), axis=-1 ) )
    rmss = np.var( results[algo], axis=1, ddof=1)
    rmss = np.sqrt( np.mean( rmss, axis=-1 ) )
    out = np.array( [ [rmse, rmss], [rmse, rmss]])
    np.save('NoDA_stats_cycint%02d_obsint%02d_%04d.npy' % (cyc_int, obs_int, expt_num), out )
    np.save('NoDA_dxdt_cycint%02d_obsint%02d_%04d.npy' % (cyc_int, obs_int, expt_num), results['dxdt'])

    continue

  # For all other expts, need to contend with inflation and extended/unextended formulations
  for infl in infl_list:
    for sp in sp_list:
      out = []
      for ss in ['xf','xa']:
        ens = results[sp][infl][algo][ss]
        rmse = np.mean( ens, axis=1) - results['xt']
        rmse = np.sqrt( np.mean( np.power( rmse,2), axis=-1 ) )
        rmss = np.var( ens, axis=1, ddof=1)
        rmss = np.sqrt( np.mean( rmss, axis=-1))
        out.append( [rmse, rmss] )
      out = np.array(out)
      if infl:
        infl_str = 'InflateT'
      else:
        infl_str = 'InflateF'
      np.save( '%s_%s_%s_stats_cycint%02d_obsint%02d_%04d.npy' % (algo, infl_str, sp, cyc_int, obs_int, expt_num), out)
      np.save( '%s_%s_%s_dxdt_cycint%02d_obsint%02d_%04d.npy' % (algo, infl_str, sp, cyc_int, obs_int, expt_num), results[sp][infl][algo]['dxdt'])

