import numpy as np

'''
Motor Config
- Quad-copter

M1(CCW)    M2(CW)
  


M3(CW)     M4(CCW)

* Up Thrust
M1 += thrust
M2 += thrust
M3 += thrust
M4 += thrust

* Right Roll
M1 += roll
M2 -= roll
M3 += roll
M4 -= roll

* Forward Pitch
M1 -= pitch
M2 -= pitch
M3 += pitch
M4 += pitch

* Right Yaw
M1 -= yaw
M2 += yaw
M3 += yaw
M4 -= yaw

    | Thrust | Roll | Pitch | Yaw |
M1  |    1   |   1  |  -1   | -1  |
M2  |    1   |  -1  |  -1   |  1  |
M3  |    1   |   1  |   1   |  1  |
M4  |    1   |  -1  |   1   | -1  |


'''

class MotorMixing:
    def __init__(self,motor_num,base_rpm,min_rpm,max_rpm):
        self.motor_num = motor_num
        self.base_rpm = base_rpm
        self.min_rpm = min_rpm
        self.max_rpm = max_rpm
        self.mix_matrix = self.mixing_matrix()

    def mixing_matrix(self):
        quad_motor_mix_mat = np.array([
            [ 1,  1, -1, -1],
            [ 1, -1, -1,  1],
            [ 1,  1,  1,  1],
            [ 1, -1,  1, -1]
        ])

        octa_motor_mix_mat = np.array([[]])

        if self.motor_num == 4:
            return quad_motor_mix_mat
        elif self.motor_num == 8:
            return octa_motor_mix_mat
        else:
            raise ValueError(f"Motor mixing matrix is not available for {self.motor_num} motor(s)")
        
    def mix(self,control_mat) -> np.ndarray:
        new_motor_rpm = self.mix_matrix @ control_mat
        final_motor_rpm = self.base_rpm + new_motor_rpm
        return np.clip(final_motor_rpm,self.min_rpm,self.max_rpm)
