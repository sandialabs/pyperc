import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import pyperc

plt.close('all')

# Invading and defending fluid density
invading_fluid_density = 1061 # kg/m3, Brine
defending_fluid_density = 797 # kg/m3, Kerosene
# Contact angles, one per grain type
contact_angles = [65] # degrees, for the invading fluid
# Surface tension
surface_tension = 0.05 # N/m
# Iterations
max_iterations = -1 # Run to completion
# Growth model
p= 0
seed= 340995

# Get an IP model instance
ip = pyperc.model.InvasionPercolation()
 
# Setup regular grid pore network
Nx = 10
Ny = 10
Nz = 10
cell_size = 0.0005 # 5 mm
radius_mean = 0.0002 # radius defined using a truncated normal distribution
radius_std = 0.00005
radius_min = 0.00001  
ip.setup_grid(Nx, Ny, Nz, cell_size, (radius_mean, radius_std, radius_min), 0)

# Initialize pores
ip.initialize_pores(contact_angles, invading_fluid_density, 
                    defending_fluid_density, surface_tension)

# Run invasion percolation
ip.run(max_iterations,p,seed)

# Plot results
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
