from .pid import PIDController
from numpy import array

class TrajectoryFlightController():
    def __init__(self,motor_mix,trajectory_func,thrust_pid_param,roll_pid_param,pitch_pid_param,yaw_pid_param,windup_limit):
        self.motor_mix = motor_mix
        self.trajectory_func = trajectory_func
        self.thrust_pid_param = thrust_pid_param
        self.roll_pid_param = roll_pid_param
        self.pitch_pid_param = pitch_pid_param
        self.yaw_pid_param = yaw_pid_param
        self.windup_limit = windup_limit
        self.target_angle_limit = 0.78
        self.max_yaw_rpm = 800
        self.initialize_pid_controllers()
               

    def initialize_pid_controllers(self):
        self.x_pid = PIDController(
            kp=self.roll_pid_param.pos_kp,
            ki=self.roll_pid_param.pos_ki,
            kd=self.roll_pid_param.pos_kd,
            windup_limit=self.windup_limit
        )
        self.y_pid = PIDController(
            kp=self.pitch_pid_param.pos_kp,
            ki=self.pitch_pid_param.pos_ki,
            kd=self.pitch_pid_param.pos_kd,
            windup_limit=self.windup_limit
        )
        self.z_pid = PIDController(
            kp=self.thrust_pid_param.pos_kp,
            ki=self.thrust_pid_param.pos_ki,
            kd=self.thrust_pid_param.pos_kd,
            windup_limit=self.windup_limit
        )
        
        self.thrust_pid = PIDController(
            kp=self.thrust_pid_param.velo_kp,
            ki=self.thrust_pid_param.velo_ki,
            kd=self.thrust_pid_param.velo_kd,
            windup_limit=self.windup_limit
        )
        self.roll_pid = PIDController(
            kp=self.roll_pid_param.angle_kp,
            ki=self.roll_pid_param.angle_ki,
            kd=self.roll_pid_param.angle_kd,
            windup_limit=self.windup_limit,
            angle_error=True
        )
        self.pitch_pid = PIDController(
            kp=self.pitch_pid_param.angle_kp,
            ki=self.pitch_pid_param.angle_ki,
            kd=self.pitch_pid_param.angle_kd,
            windup_limit=self.windup_limit,
            angle_error=True
        )
        self.yaw_pid = PIDController(
            kp=self.yaw_pid_param.angle_kp,
            ki=self.yaw_pid_param.angle_ki,
            kd=self.yaw_pid_param.angle_kd,
            windup_limit=self.windup_limit,
            angle_error=True
        )

    def calculate_thrust(self,drone_pos,drone_velocity,new_z_coor,dt):
        self.z_pid.update_target(new_z_coor)
        z_target_velo = self.z_pid.calc_cv(drone_pos[2],dt)

        self.thrust_pid.update_target(z_target_velo)
        thrust = self.thrust_pid.calc_cv(drone_velocity[2],dt)
        return thrust

    def calculate_pitch(self, drone_pos, drone_orientation, new_x_coor, dt):
        self.x_pid.update_target(new_x_coor)
        target_angle = self.x_pid.calc_cv(drone_pos[0], dt)
        target_angle = max(-self.target_angle_limit, min(target_angle, self.target_angle_limit))

        self.pitch_pid.update_target(target_angle)
        pitch = self.pitch_pid.calc_cv(drone_orientation[1], dt)
        return pitch

    def calculate_roll(self, drone_pos, drone_orientation, new_y_coor, dt):
        self.y_pid.update_target(new_y_coor)
        target_angle = -self.y_pid.calc_cv(drone_pos[1], dt) 
        target_angle = max(-self.target_angle_limit, min(target_angle, self.target_angle_limit))

        self.roll_pid.update_target(target_angle)
        roll = self.roll_pid.calc_cv(drone_orientation[0], dt)
        return roll

    def calculate_yaw(self,drone_orientation,target_angle,dt):
        self.yaw_pid.update_target(target_angle)
        yaw = self.yaw_pid.calc_cv(drone_orientation[2],dt)
        return max(-self.max_yaw_rpm,min(yaw,self.max_yaw_rpm))

    def calculate_control_cmd(self,drone_pos,drone_velocity,drone_orientation,target_pos,target_yaw_angle,dt):
        thrust = self.calculate_thrust(drone_pos,drone_velocity,target_pos[2],dt)
        pitch = self.calculate_pitch(drone_pos,drone_orientation,target_pos[0],dt) # Pass X to Pitch
        roll = self.calculate_roll(drone_pos,drone_orientation,target_pos[1],dt)   # Pass Y to Roll
        yaw = self.calculate_yaw(drone_orientation,target_yaw_angle,dt)

        return array([thrust,roll,pitch,yaw])

    def calculate_rpm(self,drone_pos,drone_velocity,drone_orientation,dt):
        target_pos,target_yaw_angle = self.trajectory_func()
        control_cmd = self.calculate_control_cmd(drone_pos,drone_velocity,drone_orientation,target_pos,target_yaw_angle,dt)
        return self.motor_mix(control_cmd)