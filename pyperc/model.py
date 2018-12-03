import networkx as nx
import pandas as pd
import numpy as np
import itertools

class InvasionPercolation(object):
    """
    Invasion Percolation class
    """
  
    def __init__(self):
        
        self._g = 9.8
        self._g_angle = 180 # down
        
        self.pores = pd.DataFrame()
        self.G = nx.Graph()
        self.A = None
        self._nf = None
        
    def setup_network(self, pore_file, throat_file):
        """
		Setup a pore network model using a throat and pore file
        
        Parameters
        --------------
        pore_file : string
            Name of the pore file. The pore file has 8 header lines followed by 
            6 columns which store pore id, x (m), y (m), z (m), radius (m), and grain type.
            See examples/data/pore.txt for an example.
        throat_file : string
            Name of the throat file. The throat file has 5 header lines followed 
            by three columns which store throat id, start pore id, and end pore id.
            See examples/data/throat.txt for an example.
		
		"""
        throats = pd.read_csv(throat_file, delim_whitespace=True, skiprows=5, header=None)
        throats.columns = ['id', 'start', 'end']
        throats.set_index('id', inplace=True)
        pores = pd.read_csv(pore_file, delim_whitespace=True, skiprows=8, header=None)
        pores.columns = ['id', 'x', 'y', 'z', 'radius', 'grain']
        pores.set_index('id', inplace=True)
        pores['pos'] = list(zip(pores.x, pores.y, pores.z))
        G = nx.Graph()
        node_bunch = [tuple([node_id, {'pos': node}]) for node_id, node in pores['pos'].iteritems()]
        edge_bunch = [tuple([edge[0], edge[1]]) for edge_id, edge in throats.iterrows()]
        G.add_nodes_from(node_bunch)
        G.add_edges_from(edge_bunch)
        del pores['pos']
        
        self.pores = pores
        self.G = G
        self.A = pd.Series(dict([(n1,list(n2.keys())) for n1,n2 in G.adj.items()]))
        self._nf = self.A.str.len() # connectivity
        
    def setup_grid(self, Nx, Ny, Nz, cell_size, radius=0, grain=0, seed=0):
        """
		Setup a regular grid pore network model
        
        Parameters
        --------------
        Nx : int
            Number of pores in the x direction
        Ny : int
            Number of pores in the y direction
        Nz : int 
            Number of pores in the z direction
        cell_size : float
            Spacing between pores (m)
        radius : numpy array, float, or tuple
            Pore radius (m), default = 0.  If radius is a tuple, then the radius is 
            defined using a normal distribution with (mean, std, min).
        grian : numpy array or int
            Pore grain type (zero based index), default = 0
        seed : int
            Seed used to define the normal distribution if a tuple is used to define radius
        """
        if float(nx.__version__) >= 2:
            G=nx.grid_graph(dim=[Nz,Ny,Nx]) # not sure why
        else:
            G=nx.grid_graph(dim=[Nx,Ny,Nz]) 
        node_locations = list(G.nodes())
        pos = dict(zip(G,node_locations))
        nx.set_node_attributes(G, name='pos', values=pos)
        # relabel nodes to index values (sorted by z, then y, then x)
        # i + nx*(j+ny*k)
        relabel_map = dict([(key,key[0]+Nx*(key[1]+(Ny*key[2]))) for key in pos.keys()])
        G = nx.relabel_nodes(G, relabel_map)
        
        pos = nx.get_node_attributes(G, name='pos')
        pores = pd.DataFrame(index=pos.keys())
        pores.index.name = 'id'
        X, Y, Z = zip(*pos.values())
        pores['x'] = X
        pores['y'] = Y
        pores['z'] = Z
        pores['x'] = pores['x']*cell_size
        pores['y'] = pores['y']*cell_size
        pores['z'] = pores['z']*cell_size
        
        pores.sort_values(['z', 'y', 'x'], inplace=True)
             
        # Set grain type
        if isinstance(grain, np.ndarray):
            pores['grain'] = grain
        elif isinstance(grain, int):
            pores['grain'] = grain
        else:
            pores['grain'] = np.nan
        
        # Set radius
        if isinstance(radius, np.ndarray):
            pores['radius'] = radius
        elif isinstance(radius, float):
            pores['radius'] = radius
        elif isinstance(radius, tuple) and len(radius) == 3:
            r_mean = radius[0]
            r_std = radius[1]
            r_min = radius[2]
            np.random.seed(seed)
            R = np.random.normal(r_mean, r_std, len(X))
            R[R<r_min] = r_min
            pores['radius'] = R
        else:
            pores['radius'] = np.nan
        
        self.pores = pores
        self.G = G
        self.A = pd.Series(dict([(n1,list(n2.keys())) for n1,n2 in G.adj.items()]))
        self._nf = self.A.str.len() # connectivity
    
    def initialize_pores(self, contact_angles, invading_density, defending_density, tension):
        """
        Initialize pores
        
        Parameters
        -------------
        contact_angles : list of floats
            Contact angle (degrees) for the invading fluid, one value per grain type
        invading_density : float
            Invading fluid density (kg/m3)
        defending_density : float
            Defending fluid density (kg/m3)
        tension : float
            Surface tension (N/m)
        """
        self.pores['angle'] = np.NaN
        for i, n in enumerate(contact_angles):
            self.pores.loc[self.pores['grain'] == i, 'angle'] = n
    
        self.pores['pc']  = (-2.0*tension*np.cos(self.pores.angle*np.pi/180))/self.pores.radius # Capillary pressure, Pa
        self.pores['pg'] = (defending_density-invading_density)*self._g*np.cos(self._g_angle*np.pi/180)*self.pores.z # Bouyancy pressure, Pa
        self.pores['pt']= self.pores.pc + self.pores.pg                  
        
        self.pores['start'] = self.pores.z <= min(self.pores.z)
        self.pores['end'] = self.pores.z >= max(self.pores.z)
        self.pores['occupy'] = self.pores['start']
        self.pores['neighbor'] = False
        
        self.pores.start = self.pores.start.astype(int)
        self.pores.end = self.pores.end.astype(int)
        self.pores.occupy = self.pores.occupy.astype(int)
        self.pores.neighbor = self.pores.neighbor.astype(int)
        
        self.tension = tension
    
    def _update_facilitation(self):
        """
        BETA Update Pc and Pt for neighbor nodes by adjusting the radius based on 
        connectivity and filled pores
        """
        neighbor_pores = self.pores.index[self.pores.neighbor == 1]
        neighbor_A = self.A[neighbor_pores]
        
        n = [len(set(x) & set(neighbor_pores)) for x in neighbor_A]
        n = pd.Series(index=neighbor_pores, data=n)
        nf = self._nf[neighbor_pores]
        radius_multiplier = pd.Series(index=self.pores.index, data=1)
        radius_multiplier[neighbor_pores] = 2-((n/nf-1/nf)/(1-1/nf))
        
        self.pores.pc = (-2.0*self.tension*np.cos(self.pores.angle*np.pi/180))/(self.pores.radius*radius_multiplier)
        self.pores.pt = self.pores.pc + self.pores.pg

    def _set_stochastic_parameters(self, p=0):
        """ 
        Set stochastic parameters
        """  
        if p <= 0:
            #f = 1/(2*(p+1))
            c = np.Inf
        else:
            #f = 0.5
            c = 1/p
            
        #self._f = f
        self._c = c

    def update_neighbors(self, previous_filled_node=None):
        """
        Update neighbors of the occupied pores.

        If the previously filled node is handed to update_neighbor, then
        only a small section is updated. If the previously filled node is NOT 
        handed to update_neighbor, then the entire neighbor list is updated.
        """
        if previous_filled_node:
            self.pores.loc[previous_filled_node,'neighbor'] = 0
            neigh = self.A[previous_filled_node]
            #pore_idx = self.pores.index[self.pores.occupy > 0]
            #neighbor_idx = set(neigh) - set(pore_idx)
            neighbor_idx = (self.pores.loc[neigh,'occupy'] == 0)
            neighbor_idx = neighbor_idx.index[neighbor_idx]
        else:
            self.pores.neighbor = 0
            pore_idx = self.pores.index[self.pores.occupy > 0]
            neigh = self.A[pore_idx]
            neigh = list(itertools.chain.from_iterable(neigh.values))
            neighbor_idx = set(neigh) - set(pore_idx)
            #neighbor_idx = (self.pores.loc[neigh,'occupy'] == 0)
            #neighbor_idx = neighbor_idx.index[neighbor_idx]
        self.pores.loc[neighbor_idx,'neighbor'] = 1
    
    def _select_node(self):
        """
        Select the next node to fill
        """
        potential_fill = self.pores.pt[self.pores.neighbor == 1]
        if not np.isinf(self._c):
            potential_fill.sort_values(inplace=True) # smallest on top
            rc = pow(np.random.rand(),self._c)
            selection = int(np.ceil(rc*len(potential_fill)))
            if selection == len(potential_fill):
                selection = selection - 1 # zero based index
            fill_node = potential_fill.index[selection]
        else:
            fill_node = potential_fill.idxmin()
        self.pores.loc[fill_node,'occupy'] = 1
                      
        threshold = potential_fill[fill_node]
        filled_node = fill_node
        
        return (filled_node, threshold)

    def _stop_criteria(self, i, max_iterations):
        """
        Check stop criteria.  Stop if an occupied node reached the 'end' or 
        if max iterations has been exceeded.
        """
        stop = False
        
        reached_end = (self.pores.end + self.pores.occupy).max()
        if reached_end > 1:
            stop = True
        
        if max_iterations > 0:
            if i > max_iterations:
                stop = True
        
        return stop
                
    def run(self, max_iterations=-1, p=0, seed=0):
        """
		Run invasion percolation model
		
		Parameters
		--------------
		max_iterations : int
			Maximum number of iteration, -1 = run to completion
		p : float
			Stochastic process parameter, between 0 and 1
		seed : int
			Random seed used in the stochastic process
		"""
        if (p > 1) or (p < 0):
            print('p must be in [0,1]')
            return
        
        np.random.seed(seed)
        
        facilitation=False # BETA, not fully tested (and slow).
        
        thresh = []
        node = []
        
        self._set_stochastic_parameters(p)   
        self.update_neighbors()
        if facilitation: self._update_facilitation()
        
        i = 0
        while True:
            if self._stop_criteria(i, max_iterations):
                break
            
            (filled_node, threshold) = self._select_node()
            self.update_neighbors(filled_node)
            if facilitation: self._update_facilitation()
            
            # Gather results
            thresh.append(threshold)
            node.append(filled_node)
                            
            i = i+1
        
        self.results = pd.DataFrame({'threshold': thresh,'node': node})