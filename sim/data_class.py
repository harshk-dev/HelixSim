from ctypes import Structure, c_float, c_double, c_int, c_char
from multiprocessing import Value
from typing import Sequence, Dict, Any
from yaml import safe_load
from numpy.ctypeslib import as_array

class StructParam(Structure):
    mass: float
    arm_length: float
    prop_length: float
    
    _fields_=[
        ("mass", c_float),
        ("arm_length", c_float),
        ("prop_length", c_float)
    ]
    
class EnvParam(Structure):
    wind_velocity_x: float
    wind_velocity_y: float
    wind_velocity_z: float
    turbulence_intensity: float
    gust_frequency: float
    gravity: float
    atmospheric_pressure: float

    _fields_ = [
        ("wind_velocity_x", c_float),
        ("wind_velocity_y", c_float),
        ("wind_velocity_z", c_float),
        ("turbulence_intensity", c_float),
        ("gust_frequency", c_float),
        ("gravity", c_float),
        ("atmospheric_pressure", c_float)
    ]

class ControlParam(Structure):
    base_rpm: int
    min_rpm: int
    max_rpm: int
    windup_limit: float
    esc_latency: float
    imu_sensor_noise: float

    _fields_ = [
        ("base_rpm", c_int),
        ("min_rpm", c_int),
        ("max_rpm", c_int),
        ("windup_limit", c_float),
        ("esc_latency", c_float),
        ("imu_sensor_noise", c_float)
    ]

class SimPresets(Structure):
    STRING_SIZE = 16
    structural_preset: bytes
    trajectory_preset: bytes

    _fields_ = [
        ("structural_preset", c_char * STRING_SIZE),
        ("trajectory_preset", c_char * STRING_SIZE)
    ]

class DroneState(Structure):
    pos: Sequence[float]
    velocity: Sequence[float]
    orientation: Sequence[float]
    angular_velocity: Sequence[float]
    motor_rpm: Sequence[int]

    _fields_ = [
        ('pos' , c_double * 3),
        ('velocity' , c_double * 3),
        ('orientation' , c_float * 3),
        ('angular_velocity' , c_float * 3),
        ('motor_rpm' , c_int * 4)
    ]

class ThrustPIDParam(Structure):
    pos_kp: float
    pos_ki: float
    pos_kd: float
    velo_kp: float
    velo_ki: float
    velo_kd: float

    _fields_ = [
        ("pos_kp", c_float),
        ("pos_ki", c_float),
        ("pos_kd", c_float),
        ("velo_kp", c_float),
        ("velo_ki", c_float),
        ("velo_kd", c_float)
    ]

class RollPIDParam(Structure):
    pos_kp: float
    pos_ki: float
    pos_kd: float
    angle_kp: float
    angle_ki: float
    angle_kd: float

    _fields_ = [
        ("pos_kp", c_float),
        ("pos_ki", c_float),
        ("pos_kd", c_float),
        ("angle_kp", c_float),
        ("angle_ki", c_float),
        ("angle_kd", c_float)
    ]

class PitchPIDParam(Structure):
    pos_kp: float
    pos_ki: float
    pos_kd: float
    angle_kp: float
    angle_ki: float
    angle_kd: float

    _fields_ = [
        ("pos_kp", c_float),
        ("pos_ki", c_float),
        ("pos_kd", c_float),
        ("angle_kp", c_float),
        ("angle_ki", c_float),
        ("angle_kd", c_float)
    ]
 
class YawPIDParam(Structure):
    angle_kp: float
    angle_ki: float
    angle_kd: float

    _fields_ = [
        ("angle_kp", c_float),
        ("angle_ki", c_float),
        ("angle_kd", c_float)
    ]

class SimData(Structure):
    run_sim: int
    struct_param: StructParam
    env_param: EnvParam
    control_param: ControlParam
    sim_presets: SimPresets
    drone_state: DroneState
    thrust_pid_param: ThrustPIDParam
    roll_pid_param: RollPIDParam
    pitch_pid_param: PitchPIDParam
    yaw_pid_param: YawPIDParam

    _fields_ = [
        ("run_sim", c_int),
        ("struct_param", StructParam),
        ("env_param", EnvParam),
        ("control_param", ControlParam),
        ("sim_presets", SimPresets),
        ("drone_state", DroneState),
        ("thrust_pid_param", ThrustPIDParam),
        ("roll_pid_param", RollPIDParam),
        ("pitch_pid_param", PitchPIDParam),
        ("yaw_pid_param", YawPIDParam)
    ]

class SimDataManager:
    config_dict: Dict[str, Any]
    def __init__(self,config_path: str):
        self.memory: SimData = Value(SimData)
        self.config_path = config_path
        self._set_default()

    def get_lock(self):
        return self.memory.get_lock()

    @property
    def data(self) -> SimData:
        return self.memory
    
    def _load_config(self):
        with open(self.config_path,'r') as file:
            self.config_dict = safe_load(file)

    def _set_default(self):
        self._load_config()
        self._load_global_param()
        self._load_struct_param()
        self._load_env_param()
        self._load_control_param()
        self._load_sim_presets()
        self._load_drone_state()
        self._load_thrust_pid_param()
        self._load_roll_pid_param()
        self._load_pitch_pid_param()
        self._load_yaw_pid_param()

    def _load_global_param(self):
        self.memory.run_sim = self.config_dict["run_sim"]

    def _load_struct_param(self):
        self.memory.struct_param.mass = self.config_dict["struct_param"]["mass"]
        self.memory.struct_param.arm_length = self.config_dict["struct_param"]["arm_length"]
        self.memory.struct_param.prop_length = self.config_dict["struct_param"]["prop_length"]

    def _load_env_param(self):
        self.memory.env_param.wind_velocity_x = self.config_dict["env_param"]["wind_velocity_x"]
        self.memory.env_param.wind_velocity_y = self.config_dict["env_param"]["wind_velocity_y"]
        self.memory.env_param.wind_velocity_z = self.config_dict["env_param"]["wind_velocity_z"]
        self.memory.env_param.turbulence_intensity = self.config_dict["env_param"]["turbulence_intensity"]
        self.memory.env_param.gust_frequency = self.config_dict["env_param"]["gust_frequency"]
        self.memory.env_param.gravity = self.config_dict["env_param"]["gravity"]
        self.memory.env_param.atmospheric_pressure = self.config_dict["env_param"]["atmospheric_pressure"]

    def _load_control_param(self):
        self.memory.control_param.base_rpm = self.config_dict["control_param"]["base_rpm"]
        self.memory.control_param.min_rpm = self.config_dict["control_param"]["min_rpm"]
        self.memory.control_param.max_rpm = self.config_dict["control_param"]["max_rpm"]
        self.memory.control_param.windup_limit = self.config_dict["control_param"]["windup_limit"]
        self.memory.control_param.esc_latency = self.config_dict["control_param"]["esc_latency"]
        self.memory.control_param.imu_sensor_noise = self.config_dict["control_param"]["imu_sensor_noise"]

    def _load_sim_presets(self):
        self.set_structural_preset(self.config_dict["sim_presets"]["structural_preset"])
        self.set_trajectory_preset(self.config_dict["sim_presets"]["trajectory_preset"])

    def _load_drone_state(self):
        self.memory.drone_state.pos[:] = self.config_dict["drone_state"]["pos"]
        self.memory.drone_state.velocity[:] = self.config_dict["drone_state"]["velocity"]
        self.memory.drone_state.orientation[:] = self.config_dict["drone_state"]["orientation"]
        self.memory.drone_state.angular_velocity[:] = self.config_dict["drone_state"]["angular_velocity"]
        self.memory.drone_state.motor_rpm[:] = self.config_dict["drone_state"]["motor_rpm"]

    def _load_thrust_pid_param(self):
        self.memory.thrust_pid_param.pos_kp = self.config_dict["thrust_pid_param"]["pos_kp"]
        self.memory.thrust_pid_param.pos_ki = self.config_dict["thrust_pid_param"]["pos_ki"]
        self.memory.thrust_pid_param.pos_kd = self.config_dict["thrust_pid_param"]["pos_kd"]
        self.memory.thrust_pid_param.velo_kp = self.config_dict["thrust_pid_param"]["velo_kp"]
        self.memory.thrust_pid_param.velo_ki = self.config_dict["thrust_pid_param"]["velo_ki"]
        self.memory.thrust_pid_param.velo_kd = self.config_dict["thrust_pid_param"]["velo_kd"]

    def _load_roll_pid_param(self):
        self.memory.roll_pid_param.pos_kp = self.config_dict["roll_pid_param"]["pos_kp"]
        self.memory.roll_pid_param.pos_ki = self.config_dict["roll_pid_param"]["pos_ki"]
        self.memory.roll_pid_param.pos_kd = self.config_dict["roll_pid_param"]["pos_kd"]
        self.memory.roll_pid_param.angle_kp = self.config_dict["roll_pid_param"]["angle_kp"]
        self.memory.roll_pid_param.angle_ki = self.config_dict["roll_pid_param"]["angle_ki"]
        self.memory.roll_pid_param.angle_kd = self.config_dict["roll_pid_param"]["angle_kd"]

    def _load_pitch_pid_param(self):
        self.memory.pitch_pid_param.pos_kp = self.config_dict["pitch_pid_param"]["pos_kp"]
        self.memory.pitch_pid_param.pos_ki = self.config_dict["pitch_pid_param"]["pos_ki"]
        self.memory.pitch_pid_param.pos_kd = self.config_dict["pitch_pid_param"]["pos_kd"]
        self.memory.pitch_pid_param.angle_kp = self.config_dict["pitch_pid_param"]["angle_kp"]
        self.memory.pitch_pid_param.angle_ki = self.config_dict["pitch_pid_param"]["angle_ki"]
        self.memory.pitch_pid_param.angle_kd = self.config_dict["pitch_pid_param"]["angle_kd"]

    def _load_yaw_pid_param(self):
        self.memory.yaw_pid_param.angle_kp = self.config_dict["yaw_pid_param"]["angle_kp"]
        self.memory.yaw_pid_param.angle_ki = self.config_dict["yaw_pid_param"]["angle_ki"]
        self.memory.yaw_pid_param.angle_kd = self.config_dict["yaw_pid_param"]["angle_kd"]

    def set_structural_preset(self,text: str):
        self.memory.sim_presets.structural_preset = text.encode('utf-8')

    @property
    def get_structural_preset(self):
        return self.memory.sim_presets.structural_preset.decode('utf-8')
    
    def set_trajectory_preset(self,text: str):
        self.memory.sim_presets.trajectory_preset = text.encode('utf-8')

    @property
    def get_trajectory_preset(self):
        return self.memory.sim_presets.trajectory_preset.decode('utf-8')
    
    @property
    def get_drone_pos(self):
        return as_array(self.memory.drone_state.pos)

    @property
    def get_drone_velocity(self):
        return as_array(self.memory.drone_state.velocity)

    @property
    def get_drone_orientation(self):
        return as_array(self.memory.drone_state.orientation)

    @property
    def get_drone_angular_velocity(self):
        return as_array(self.memory.drone_state.angular_velocity)

    @property
    def get_drone_motor_rpm(self):
        return as_array(self.memory.drone_state.motor_rpm)

if __name__ == "__main__":
    sim_data_manager = SimDataManager("/home/harsh/HelixSim/config/defaults.yaml")
    print(sim_data_manager.config_dict)

    print("yes" if sim_data_manager.get_trajectory_preset() == "hover" else "no")
    import numpy as np
    print(sim_data_manager.get_drone_pos())
    sim_data_manager.get_drone_pos()[:] = np.array([1,2,3])
    print(sim_data_manager.get_drone_pos())
    target_attr = getattr(sim_data_manager.data,"run_sim")
    print(target_attr)
    setattr(target_attr,"run_sim",1)
    print(sim_data_manager.data.run_sim)