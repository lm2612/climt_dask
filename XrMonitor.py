from sympl import Monitor
import xarray as xr
import numpy as np
class XrMonitor(Monitor):
    """A Monitor which saves stored states to an Xarray. Potential functionality for Iris
    cube and saving to file to be added later"""
    def __init__(self, init_state, store_names, time_units='seconds'):
        """
        Args
        ----
        init_state : xr dataarray
            Initial state of model of xarrays to which the states will be saved.
        store_names : iterable of str
            Names of quantities to store. 
        time_units : str, optional
            The units in which time will be
            stored in the NetCDF file. Time is stored as an integer
            number of these units. Default is seconds.
        
        """
        self._cached_state_dict = {}
        self._time_units = time_units        
        if store_names is None:
            self._store_names = init_state.keys()
        else:
            self._store_names = list(store_names)

        dataset = {}
        for variable_name in self._store_names:  
            dataset_var = init_state[variable_name].expand_dims('time',0)
            dataset[variable_name] = dataset_var

        # Coordinates
        self.x = init_state['longitude'][0,:]
        self.y = init_state['latitude'][:,0]
        self.t = [init_state['time']]
        # Get mid-level vertical sigma coordinates 
        sigma_interface = init_state['atmosphere_hybrid_sigma_pressure_b_coordinate_on_interface_levels']
        sigma_mid = sigma_interface.interp(interface_levels=np.arange(.5,len(sigma_interface)-0.5)
                                          ).rename({'interface_levels':'mid_levels'})
        self.z = sigma_mid
        
        # Create Xarray dataset
        self.dataset = xr.Dataset(dataset, 
                                  coords = {'time':self.t,
                                            'mid_levels':self.z,
                                            'lat':self.y,
                                            'lon':self.x
                                            })

    def store(self, state):
        """
        Stores the given state in dataset.

        Args
        ----
        state : dict
            A model state dictionary that comes out climt        
        """
        # Get variables of interest
        current_state = xr.Dataset(state, coords = {'mid_levels':self.z,
                                                    'lat':self.y,
                                                    'lon':self.x
                                                   })
        current_state = current_state[self._store_names]
        
        # add time dimension and concatenate onto dataset
        self.t.append(state['time'])
        current_state = current_state.expand_dims({'time':[state['time']]})
        self.dataset = xr.concat((self.dataset, current_state), dim='time')
        
    def get_full(self):
        """Returns full xr dataset"""
        return self.dataset
    
    def get_var(self, var_name):
        """Returns xarray for variable
        
        Args
        ----
        var_name : str
            Name of variable to return """
        return self.dataset[var_name]
    
    def cube(self):
        """ Returns iris cube of dataset"""
        pass
    
    def write(self):
        """ Writes to file """
        pass
        
        
        
        