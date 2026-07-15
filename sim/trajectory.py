from numpy import array, ndarray, radians
from sim import SimDataManager
from math import sin, cos

class TrajectoryManager:
    def __init__(self,data_manager: SimDataManager,dt):
        self.dt = dt
        self.time = 0
        self.data_manager = data_manager
        self.trajectory_func = self.hover
        self.hover_pos = array([0,0,5])
        self.yaw = 0

    def update_time(self):
        self.time += self.dt

    def config_hover(self):
        with self.data_manager.get_lock():
            hover_pos = [
                self.data_manager.data.hover_param.pos_x,
                self.data_manager.data.hover_param.pos_y,
                self.data_manager.data.hover_param.pos_z
            ]
            yaw = self.data_manager.data.hover_param.yaw
            
        self.hover_pos = array(hover_pos)
        self.yaw = radians(yaw)

    def config_straight_line(self):
        with self.data_manager.get_lock():
            slope = [
                self.data_manager.data.straight_param.slope_x,
                self.data_manager.data.straight_param.slope_y,
                self.data_manager.data.straight_param.slope_z
            ]
            intercept = [
                self.data_manager.data.straight_param.intercept_x,
                self.data_manager.data.straight_param.intercept_y,
                self.data_manager.data.straight_param.intercept_z
            ]
            yaw = self.data_manager.data.straight_param.yaw
            
        self.slope = array(slope)
        self.intercept = array(intercept)
        self.yaw = radians(yaw)

    def config_circular_loop(self):
        with self.data_manager.get_lock():
            radius = self.data_manager.data.circular_param.radius
            height = self.data_manager.data.circular_param.height
            yaw = self.data_manager.data.circular_param.yaw
            
        self.radius = radius
        self.height = height
        self.yaw = radians(yaw)

    def hover(self):
        return self.hover_pos,self.yaw

    def straight_line(self):
        self.update_time()
        pos = self.slope * self.time + self.intercept
        return pos,self.yaw

    def circular_loop(self):
        self.update_time()
        target_speed = 20
        omega = target_speed / self.radius
        angle = omega * self.time
        x = self.radius * cos(angle)
        y = self.radius * sin(angle)
        z = self.height
        
        pos = array([x, y, z])
        return pos, self.yaw
        

    def set_trajectory(self):
        with self.data_manager.get_lock():
            type = self.data_manager.get_trajectory_preset
            print(type)
        if type == "hover":
            self.config_hover()
            self.trajectory_func = self.hover
        elif type == "straight line":
            self.config_straight_line()
            self.trajectory_func = self.straight_line
        elif type == "circular loop":
            self.config_circular_loop()
            self.trajectory_func = self.circular_loop
