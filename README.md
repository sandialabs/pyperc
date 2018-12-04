pyperc
=======================================

pyperc is a Python package for invasion percolation which models multiphase 
fluid migration in porous media.  Invasion percolation and  
modified invasion percolation account for capillary pressure 
and buoyancy to sequentially fill pores along an interface between
an invading and defending fluid [e.g. 1,2,3,4].  A tuning parameter can be 
set to adjust the stochastic nature of the process [3]. 

To use pyperc, a pore network model is defined and each pore is initially 
filled with an invading or defending fluid. The desired terminal pores for the 
invading fluid are also defined, along with fluid-rock properties, including fluid 
densities, surface tension, and contact angles. Contact angles can vary 
throughout the pore network model to reflect spatial heterogeneity.
pyperc then advances the invading fluid by filling a pore along the 
invading/defending fluid interface where the total invading pressure is lowest. 
A stochastic selection parameter (p, between 0 and 1) adds a random selection 
process to the model [3]. When p = 0, the process is deterministic and the pore
with the lowest total invading pressure is filled at each iteration. As p increases, 
pores along the interface with higher total invading pressure can be filled. 
When p = 1, the selection process along the interface is completely random.
Note that p < 0, for multi-finger stochastic selection, is not implemented at this time.
The invasion percolation process continues until the invading fluid reaches 
a terminal pore or the maximum number of iterations are completed.

Total invading pressure (P<sub>t</sub>) at each pore is defined as follows:

P<sub>c</sub> = 2&gamma;cos(&theta;)/r  
P<sub>g</sub> = (&rho;<sub>d</sub>-&rho;<sub>i</sub>)gz  
P<sub>t</sub> = P<sub>c</sub> + P<sub>g</sub>  

where
* P<sub>c</sub> = capillary pressure (Pa)
* P<sub>g</sub> = buoyancy (gravity) pressure (Pa)
* &gamma; = surface tension (N/m)
* &theta; = invading fluid contact angle (degrees)
* r = pore radius (m)
* &rho;<sub>d</sub> = defending fluid density (kg/m3)
* &rho;<sub>i</sub> = invading fluid density (kg/m3)
* g = acceleration due to gravity (-9.8 m/s2)
* z = distance between the pore and a reference elevation (m)

The software contains a single class, `pyperc.model.InvasionPercolation`, which
is used to complete the following steps:

1. Define the regular or irregularly structured pore network including the 
   x,y,z location of pores, connectivity between pores, and pore radius. 
   The pore network can be defined using a regularly spaced grid 
   (see [3D regular grid example](examples/grid_example.py)) or using pore and 
   throat files (see [3D irregular grid example](examples/network_example.py)).
   pyperc stores pore properties using a pandas DataFrame (`InvasionPercolation.pores`).
   and stores network connectivity using a networkx graph (`InvasionPercolation.G`).
2. Initialize the pore network with contact angles, invading fluid density, 
   defending fluid density, and surface tension. The user can also specify 
   the initial condition (invading or defending fluid) for each pore and the 
   desired terminal pores for the invading fluid.  These properties update the pandas 
   DataFrame to include P<sub>c</sub>, P<sub>g</sub>, P<sub>t</sub>, start and end locations for the invading fluid, 
   current occupied pores, and current pores along the invading/defending interface (called neighbors).
3. Run invasion percolation and specify the maximum number of iterations and
   stochastic selection parameter.  At each iteration, the occupied and 
   neighboring pores are updated in the `InvasionPercolation.pores` pandas DataFrame.  
   pyperc also stores results as a pandas
   Dataframe (`InvasionPercolation.results`), which contains the pressure threshold 
   and pore number that was filled at each iteration.
   
Additionally, the software contains a graphics module, `pyperc.graphics`, which 
contains a function to plot 3D pore network models using plotly. matplotlib can 
be used to create simple 2D graphics using imshow.

Examples
-----------
The software contains several examples. In the examples, the user can modify input 
parameters, including the stochastic selection process and density 
difference, to explore a range percolation processes:

* [2D random porous media example](examples/random_porous_media_example.py), based on [3]. 
  Graphic below shows pore radius and occupied pores (yellow) based on invasion percolation using p = 0 and p = 0.2.

![Random field example](figures/random_ex.png)

* [2D sand pack example](examples/sand_pack_example.py), based on [4].
  Graphic below shows grain type, pore radius, and occupied pores (yellow) based on invasion percolation.
  
![Sand pack example](figures/sand_pack_ex.png)

* [3D regular grid example](examples/grid_example.py).
  Graphic below shows occupied pores, colored by iteration number, based on invasion percolation.

![Grid example](figures/grid_ex.png)

* [3D irregular grid example](examples/network_example.py).
  Graphic below shows occupied pores, colored by iteration number, based on invasion percolation.

![Network example](figures/network_ex.png)

Units
---------
All units are SI:

* Length = m
* Time = s
* Mass = kg
* Pressure = Pa
* Force = N

Installation
-----------------
pyperc requires Python (3.5, 3.6, or 3.7) along with several Python package dependencies.
Information on installing and using Python can be found at 
https://www.python.org.
Python distributions, such as Anaconda, are recommended to manage the Python interface.  

The pyperc source files can be obtained by downloading a zip file or using git.
The zip file is located at https://github.com/sandialabs/pyperc/archive/master.zip
To use git, run:

	git clone https://github.com/sandialabs/pyperc
	
Once the source files have been obtained (and uncompressed if using the zip file), 
run the following command from within the main pyperc folder:

	python setup.py install
	
Python package dependencies include:

* numpy
* networkx
* pandas
* matplotlib
* plotly

Testing
------------
Automated testing is run using TravisCI at https://travis-ci.org/sandialabs/pyperc.
Tests can also be run locally using nosetests.

Copyright
------------
Copyright 2018 National Technology & Engineering Solutions of Sandia, 
LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. 
Government retains certain rights in this software.

License
-------------------------
[Revised BSD](LICENSE.txt)

References
------------

[1] Chandler, R., Koplik, J., Lerman, K. and Willemsen, J.F., 1982. Capillary displacement and percolation in porous media. J. Fluid Mech., 119, 249-267

[2] Blunt, M.J. and Scher, H., 1995. Pore-level modeling of wetting. Phys. Rev. E 52, 6387-6403

[3] Ewing, R.P. and Berkowitz, B., 1998. A generalized growth model for simulating initial migration of dense non-aqueous phase liquids. Water Resour. Res., 34(4), 611-622

[4] Glass, R. and Yarrington, L., 2003. Mechanistic modeling of fingering, nonmonotonicity, fragmentation, and pulsation within gravity/buoyant destabilized two-phase/unsaturated flow. Water Resour. Res., 39(3), 1058
___
Sandia National Laboratories is a multimission laboratory managed and operated by National Technology and 
Engineering Solutions of Sandia, LLC., a wholly owned subsidiary of Honeywell International, Inc., for the 
U.S. Department of Energy's National Nuclear Security Administration under contract DE-NA-0003525.
