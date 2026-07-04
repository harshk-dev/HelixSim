from numpy import array, ndarray, radians


class TrajectoryManager:
    def __init__(self,dt):
        self.dt = dt
        self.time = 0
        self.trajectory_func = self.hover
        self.hover_pos = array([0,0,5])
        self.yaw = 0

    def update_time(self):
        self.time += self.dt

    def config_reach_target(self,target_pos: ndarray = array([0,0,5]), yaw=0):
        self.target_pos = target_pos
        self.yaw = radians(yaw)

    def config_hover(self,hover_pos = array([0,0,5]), yaw=0):
        self.hover_pos = hover_pos
        self.yaw = radians(yaw)

    def config_straight_line(self,slope: ndarray = array([1,1,0]), intercept: ndarray = array([0,0,10]), yaw=0):
        self.slope = slope
        self.intercept = intercept
        self.yaw = radians(yaw)

    def config_circular_loop(self,radius=5,height=5,yaw=0):
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
        pass

    def reach_target(self):
        return self.target_pos,self.yaw

    def set_trajectory(self,type):
        if type == "hover":
            self.trajectory_func = self.hover
        elif type == "straight":
            self.trajectory_func = self.straight_line
        elif type == "circular":
            self.trajectory_func = self.circular_loop
        elif type == "target":
            self.trajectory_func = self.reach_target
