from math import sin,cos,atan2

class PIDController:

    def __init__(self, kp, ki, kd, windup_limit,angle_error=False):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.windup_limit = windup_limit
        self.target = 0
        self.error = 0
        self.prev_actual = 0
        self.integral = 0
        if angle_error:
            self.calc_error = self.angle_error
        else:
            self.calc_error = self.normal_error
        

    def update_target(self,value):
        self.target = value 

    def normal_error(self,target,actual):
        return target - actual
    
    def angle_error(self,target,actual):
        normal_error = self.normal_error(target,actual)
        return atan2(sin(normal_error),cos(normal_error))

    def p_term(self):
        return self.kp * self.error

    def i_term(self, dt):
        self.integral += self.error * dt
        clamped_i = max(-self.windup_limit, min(self.ki * self.integral, self.windup_limit))
        if self.ki != 0:
            self.integral = clamped_i / self.ki
        return clamped_i

    def d_term(self, actual, dt):
        if dt <= 0.0001:
            return 0
        
        return -self.kd * (self.calc_error(actual,self.prev_actual)) / dt
    
    def calc_cv(self, actual, dt):
        self.error = self.calc_error(self.target,actual)

        control_variable = self.p_term() + self.i_term(dt) + self.d_term(actual,dt)
        self.prev_actual = actual
        return control_variable
    
def main():
    import matplotlib.pyplot as plt
    import numpy as np
 
    kp = 0.400
    ki = 0.100
    kd = 0.800
    pid = PIDController(kp,ki,kd,50,angle_error=True)
    dt = 1
    data_cv = []
    data_velo = []
    data_x = []
    velo = 0
    x = 0

    plt.plot(50*np.ones(100),c="red")

    for _ in range(100):
        x += velo
        data_velo.append(velo)
        data_x.append(x)

        pid.update_target(50)
        cv = pid.calc_cv(x,dt)
        velo += cv
        data_cv.append(cv)
        print(cv)
        
    
    plt.plot(data_cv,c="green")
    plt.plot(data_velo,c="blue")
    plt.plot(data_x,c="black")
    plt.show()

if __name__ == "__main__":
    main()