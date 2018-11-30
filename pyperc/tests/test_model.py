from nose.tools import *
from os.path import abspath, dirname, join
import pandas as pd
import numpy as np
import pyperc

testdir = dirname(abspath(__file__))
datadir = join(testdir, 'data')

def test_setup_grid():
    ip = pyperc.model.InvasionPercolation()
    Nx = 2
    Ny = 3
    Nz = 4
    cell_size = 1 
    ip.setup_grid(Nx,Ny,Nz,cell_size, 0, 0)
    
    assert_set_equal(set(ip.A[5]), set([3,4,11]))
    assert_set_equal(set(ip.A[14]), set([12,16,15,20,8]))
    
    assert_equal(sum(ip.pores.loc[5,['x', 'y', 'z']].values == [1,2,0]),3)
    assert_equal(sum(ip.pores.loc[14,['x', 'y', 'z']].values == [0,1,2]),3)

def test_setup_network():
    ip = pyperc.model.InvasionPercolation()
    
    throat_file = join(datadir,'simple_throat.txt'  )  
    pore_file = join(datadir,'simple_pore.txt')
    ip.setup_network(pore_file, throat_file)  

def test_initialize_pores():
    ip = pyperc.model.InvasionPercolation()
    Nx = 2
    Ny = 3
    Nz = 4
    cell_size = 0.0005 # 5mm
    radius = 0.0002
    contact_angles = [65]
    invading_fluid_density = 1000
    defending_fluid_density = 800
    surface_tension = 0.05 # N/m
                    
    ip.setup_grid(Nx,Ny,Nz,cell_size,radius,0)
    ip.initialize_pores(contact_angles, invading_fluid_density, 
                    defending_fluid_density, surface_tension)
    
def test_run():
    ip = pyperc.model.InvasionPercolation()
    Nx = 2
    Ny = 3
    Nz = 4
    cell_size = 0.0005 # 5mm
    radius = (0.0002, 0.00005, 0.00001)
    contact_angles = [65]
    invading_fluid_density = 1000
    defending_fluid_density = 800
    surface_tension = 0.05 # N/m
                    
    ip.setup_grid(Nx,Ny,Nz,cell_size,radius,0,123)
    ip.initialize_pores(contact_angles, invading_fluid_density, 
                    defending_fluid_density, surface_tension)
    ip.run()
    
    assert_equal(sum(ip.results.node == [6,9,10,7,13,15,14,11,19]),9)