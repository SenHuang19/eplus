from pyfmi import load_fmu
import copy


class EmulatorSetup(object):
    '''Class that implements the test case.
    
    '''
    
    def __init__(self,con):
        '''
        
           Constructor.
        
        '''       
        # Load fmu
        fmupath = con['fmupath']
        self.fmu = load_fmu(fmupath) 
#        self.inputs = con['inputs']        
        self.fmu.set_log_level(7)
       
        # Get available control inputs and outputs
        self.inputs = self.fmu.get_model_variables(causality = 0)     
        self.output_names = self.fmu.get_model_variables(causality = 1)

        # Define outputs data
        self.y = {'time':[]}
        for key in self.output_names:
            self.y[key] = []
        self.y_store = copy.deepcopy(self.y)
        # Define inputs data
        self.u = {'time':[]}
        for key in self.inputs:
            self.u[key] = []
        self.u_store = copy.deepcopy(self.u)

        # Define inputs data
        self.init_time = eval(con['start_time'])       
        self.start_time = self.init_time       
        self.end_time = eval(con['end_time'])                
        self.step = float(con['step'])        
        self.fmu.instantiate_slave(con['name'])
        self.fmu.initialize(tStart=self.start_time,tStop=self.end_time)
        
    def reset(self,config):
    
        config['step'] = self.step
    
        self.__init__(config)
        
                
    def advance(self,u):
        '''Advances the test case model simulation forward one step.
        
        Parameters
        ----------
        u : dict
            Defines the control input data to be used for the step.
            {<input_name> : <input_value>}
            
        Returns
        -------
        y : dict
            Contains the measurement data at the end of the step.
            {<measurement_name> : <measurement_value>}
            
        '''
        
        # Set control inputs if they exist and are written
        # Check if possible to overwrite

        if u.keys():
        
            for key in u.keys():
            
                if key !='time' and u[key] is not None and (key in self.inputs.keys()):                      
                      
                      self.inputs[key] = u[key]
                      
            for key in self.inputs.keys():
        
                self.fmu.set(key,self.inputs[key])
                
                
        for i in range(max(int(self.step/60),1)):
        
            self.fmu.do_step(current_t=self.start_time, step_size=60)
            
            self.start_time = self.start_time + 60

        # Get result and store measurement
        for key in self.y:
        
                if key == 'time':
          
                      self.y[key] = self.start_time
                      
                else:
        
                      self.y[key] = self.fmu.get(key)[0]
            
                self.y_store[key] = self.y_store[key] + [self.y[key]]
            
        # Store control inputs
        
        for key in self.inputs:
                    
                self.u_store[key] = self.u_store[key] + [self.inputs[key]]
                                                   
        self.u_store['time'] = self.u_store['time'] + [max(self.start_time-self.step,self.init_time+60)]   
        
        return self.y


    def get_step(self):
        '''Returns the current simulation step in seconds.'''

        return self.step

    def set_step(self,step):
        '''Sets the simulation step in seconds.
        
        Parameters
        ----------
        step : int
            Simulation step in seconds.
            
        Returns
        -------
        None
        
        '''
        
        self.step = float(step)
        
        return None
        
        
    def get_results(self):
        '''Returns measurement and control input trajectories.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        Y : dict
            Dictionary of measurement and control input names and their 
            trajectories as lists.
            {'y':{<measurement_name>:<measurement_trajectory>},
             'u':{<input_name>:<input_trajectory>}
            }
        
        '''
        
        Y = {'y':self.y_store, 'u':self.u_store}
        
        return Y
