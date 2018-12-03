import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import pyperc

plt.close('all')

# Invading and defending fluid density
invading_fluid_density = 1061 # kg/m3, Brine
defending_fluid_density = 797 # kg/m3, Kerosene
# Contact angles, one per grain type
contact_angles = [65, 165] # degrees, for the invading fluid
# Surface tension
surface_tension = 0.05 # N/m
# Iterations
max_iterations = -1 # Run to completion
# Stochastic selection
p = 0.1


# Get an IP model instance
ip = pyperc.model.InvasionPercolation()
 
# Setup an irregular pore network and convert units
throat_file = 'data/throat.txt'    
pore_file = 'data/pore.txt'
ip.setup_network(pore_file, throat_file)
ip.pores['grain'] = ip.pores['grain'] - 1 # zero based index
ip.pores[['x', 'y', 'z', 'radius']] = ip.pores[['x', 'y', 'z', 'radius']]*0.01 # convert to m
min_r = 0.0001
ip.pores.loc[ip.pores['radius'] < min_r, 'radius'] = min_r # truncate R

# Initialize pores
ip.initialize_pores(contact_angles, invading_fluid_density, 
                    defending_fluid_density, surface_tension)

# Run invasion percolation
ip.run(max_iterations, p)


# Generate figures
N_all = len(ip.pores.radius)
x_all = np.sort(ip.pores.radius)
f_all = np.array(range(N_all))/float(N_all)
filled_radius = ip.pores.radius.loc[ip.pores.occupy == 1]
N_filled = len(filled_radius)                               
x_filled = np.sort(filled_radius)
f_filled = np.array(range(N_filled))/float(N_filled)
plt.figure()
plt.plot(x_all, f_all, label='All radii')
plt.plot(x_filled, f_filled, label='Filled radii')
plt.xlabel('Radius (m)')
plt.ylabel('Empirical CDF')
plt.legend()

pyperc.graphics.plot_3d_network(ip.G, filename='Graph.html')
pyperc.graphics.plot_3d_network(ip.G, ip.pores.radius, filename='Radius.html')
pyperc.graphics.plot_3d_network(ip.G, ip.pores.occupy[ip.pores.occupy ==1], filename='Occupy.html')

iteration = pd.Series(index = ip.results.node, data = ip.results.index)
pyperc.graphics.plot_3d_network(ip.G, iteration, filename='Iteration.html')
         
threshold = pd.Series(index = ip.results.node, data = ip.results.threshold.values)
pyperc.graphics.plot_3d_network(ip.G, threshold, filename='Threshold.html')