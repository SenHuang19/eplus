# -*- coding: utf-8 -*-
"""
This module implements the REST API used to interact with the test case.  
The API is implemented using the ``flask`` package.  

"""

# GENERAL PACKAGE IMPORT
# ----------------------
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import json
from testcase import EmulatorSetup
import requests

url = 'http://jmodelica:5000'

u_modelica = {}

def cosim_data(u, dic):
    y = {}
#    print(u)
#    print(dic)    
    for key in dic:
        arry = dic[key]     
        temp1 = 0  
#        print(arry)        
        for i in range(len(arry[0])):        
            temp2 = 1     
            for j in range(len(arry)):        
                   if isinstance(arry[j][i], str):                  
                               temp2 = temp2 * float(u[arry[j][i]])                   
                   else:                   
                               temp2 = temp2 * float(arry[j][i])                                      
            temp1 = temp1 + temp2                              
        y.update({key:temp1})
#    print(y)        
    return y                

# ----------------------
# DEFINE REST REQUESTS
# ----------------------




class Advance(Resource):
    """Interface to advance the test case simulation."""

    def __init__(self, **kwargs):   
        self.case = kwargs["case"]        
        self.model_config = kwargs["model_config"]

    def post(self):
        """
        POST request with input data to advance the simulation one step 
        and receive current measurements.
        """
        u = json.loads(request.get_json(force=True)) 
        print(u)        
        global u_modelica
        
        if not bool(u_modelica) :        
            y = self.case.advance({})            
        else:

            if self.case.step/60>0:
            
                y = self.case.advance(u_modelica)
            
#        print(self.case.y)
#        print(y)
        u_eplus = cosim_data(y,self.model_config['outputs'])
#        print(u_eplus)        
        u.update(u_eplus) 
        y_modelica = requests.post('{0}/advance'.format(url), data=u).json()
#        print(self.model_config['inputs'])        
        u_modelica = cosim_data(y_modelica,self.model_config['inputs'])   
#        print(u_modelica)  
        y_eplus = {}        
        y_eplus.update(y_modelica)
#        y_eplus.update(y)         
        return y_eplus

class Reset(Resource):
    """
    Interface to test case simulation step size.
    """
    
    def __init__(self, **kwargs):
        self.case = kwargs["case"]
        self.model_config = kwargs["model_config"]
        self.parser_reset = kwargs["parser_reset"]

    def put(self):
        """PUT request to reset the test."""
        u = self.parser_reset.parse_args()
        self.model_config['start_time'] = u['start_time']
        self.model_config['end_time'] = u['end_time']
        requests.put('{0}/reset'.format(url), data={'start_time':float(u['start_time']),'end_time':u['start_time']})
        self.case.reset(self.model_config)
        return 

                
class Step(Resource):
    """Interface to test case simulation step size."""

    def __init__(self, **kwargs):
        self.case = kwargs["case"]
        self.parser_step = kwargs["parser_step"]

    def get(self):
        """GET request to receive current simulation step in seconds."""
        return self.case.get_step()

    def put(self):
        """PUT request to set simulation step in seconds."""
        args = self.parser_step.parse_args()
        step = args['step']
        self.case.set_step(max(60,float(step)))            
        requests.put('{0}/step'.format(url), data={'step':step})
        return step, 201                

class Results(Resource):
    """Interface to test case result data."""

    def __init__(self, **kwargs):       
        self.case = kwargs["case"]

    def get(self):
        """GET request to receive measurement data."""        
        Y = self.case.get_results()
        return Y

class Inputs(Resource):
    """Interface to test case inputs."""

    def __init__(self, **kwargs):   
        self.case = kwargs["case"]
        self.model_config = kwargs["model_config"]        
        
    def get(self):
        """GET request to receive list of available inputs."""
        u_list = requests.get('{0}/inputs'.format(url)).json()
        u = []
        for key in u_list:
            if not (key in self.model_config['outputs']):
                u.append(key)        
        return list(u)
                
class Measurements(Resource):
    """Interface to test case measurements."""

    def __init__(self, **kwargs):
        self.case = kwargs["case"]
        self.model_config = kwargs["model_config"]
        
    def get(self):
        """GET request to receive list of available measurements."""
        y_list = requests.get('{0}/measurements'.format(url)).json()
        y = []
        for key in y_list:
            if not (key in self.model_config['inputs']):
               y.append(key)            
        return list(y)

def main(config):
    
    # FLASK REQUIREMENTS
    # ------------------
    app = Flask(__name__)
    api = Api(app)
    # ------------------

    # INSTANTIATE TEST CASE
    # ---------------------

    with open(config) as json_file:
        model_config = json.load(json_file)

    case = EmulatorSetup(model_config)
    # ---------------------

    # DEFINE ARGUMENT PARSERS
    # -----------------------
    # ``step`` interface
    parser_step = reqparse.RequestParser()
    parser_step.add_argument('step')
    # ``reset`` interface
    reset_step = reqparse.RequestParser()
    reset_step.add_argument('start_time')
    reset_step.add_argument('end_time')
    reset_step.add_argument('name')


    # --------------------------------------
    # ADD REQUESTS TO API WITH URL EXTENSION
    # --------------------------------------
    api.add_resource(Advance, '/advance', resource_class_kwargs = {"case": case, "model_config":model_config})
    api.add_resource(Reset, '/reset', resource_class_kwargs = {"case": case, "parser_reset": reset_step, "model_config":model_config})
    api.add_resource(Step, '/step', resource_class_kwargs = {"case": case, "parser_step": parser_step})
    api.add_resource(Results, '/results', resource_class_kwargs = {"case": case})
    api.add_resource(Inputs, '/inputs', resource_class_kwargs = {"case": case, "model_config":model_config})
    api.add_resource(Measurements, '/measurements', resource_class_kwargs = {"case": case, "model_config":model_config})
    # --------------------------------------
    app.run(debug=True, host='0.0.0.0',port=5500)        
    # --------------------------------------

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
