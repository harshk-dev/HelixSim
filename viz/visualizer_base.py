from abc import ABC,abstractmethod

class VizBase(ABC):
    '''
    Irrespective of the Visualizer, this class will be followed by visualizer class.
    Visualizer class will inherit this class for making uniformity in the code.
    Only the the methods of this class will be called in main.py
    '''

    @abstractmethod
    def run(self):
        '''
        This method will be used to run the Visualization.
        It will be called when we want visualization to start.
        '''

    @abstractmethod
    def initialize(self,param):
        '''
        This method will be used for initialising the scene.
        It will draw intial drone, ground, set lightings etc.
        It will use param to know the initial structure of the drone.
        '''

    @abstractmethod
    def update(self,state):
        '''
        This method will be called in each frame for updation of scene.
        It will update the position of the required 3D models.
        It will take state as an argument to get a snapshot of the drone's current metrics.
        '''

    @abstractmethod
    def update_param(self,new_param):
        '''
        This method will be called when user varies any param.
        It will update existing param with new one.
        It uses new_param as an argument to know what has been updated.
        '''

    @abstractmethod
    def exit(self):
        '''
        This method will be called when user wants to kill the visualization.
        It will free all CPU and GPU resources.
        '''