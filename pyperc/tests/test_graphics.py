from nose.tools import *
from os.path import abspath, dirname, join, isfile
import os
import pyperc

testdir = dirname(abspath(str(__file__)))
datadir = join(testdir, 'data')

def test_plot_3D_network():
    filename = abspath(join(testdir, 'plot_3D_network.html'))
    if isfile(filename):
        os.remove(filename)
    
    ip = pyperc.model.InvasionPercolation()
    Nx = 10
    Ny = 10
    Nz = 10
    cell_size = 0.0005 # 5 mm
    radius_mean = 0.0002 # radius defined using a truncated normal distribution
    radius_std = 0.00005
    radius_min = 0.00001  
    ip.setup_grid(Nx, Ny, Nz, cell_size, (radius_mean, radius_std, radius_min), 0)
    
    pyperc.graphics.plot_3d_network(ip.G, ip.pores.radius, filename=filename, auto_open=False)
    
    assert_true(isfile(filename))
    
if __name__ == '__main__':
    cmp = test_plot_3D_network()
    