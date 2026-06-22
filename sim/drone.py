from dataclasses import dataclass, asdict
from numpy import array, ndarray

@dataclass
class StructParam:
    mass: float = 1.0
    arm_length: float = 0.5
    prop_length: float = 0.25

    @classmethod
    def from_dict(cls,d: dict) -> StructParam:
        return cls(**d)

    def to_dict(self) -> dict:
        return asdict(self)
    
@dataclass
class EnvParam:
    wind_velocity_x: float = 0
    wind_velocity_y: float = 0
    wind_velocity_z: float = 0
    turbulence_intensity: float = 0
    gust_frequency: float = 0
    gravity: float = 9.81
    atmospheric_pressure: float = 1

    @classmethod
    def from_dict(cls,d: dict) -> StructParam:
        return cls(**d)

    def to_dict(self) -> dict:
        return asdict(self)
    
@dataclass
class ControlParam:
    pid_kp: float = 0
    pid_ki: float = 0
    pid_kd: float = 0
    esc_latency: float = 0
    imu_sensor_noise: float = 0

    @classmethod
    def from_dict(cls,d: dict) -> StructParam:
        return cls(**d)

    def to_dict(self) -> dict:
        return asdict(self)
    
@dataclass
class SimPresets:
    structural_preset: str = 'quad'
    trajectory_preset: str = 'hover'

    @classmethod
    def from_dict(cls,d: dict) -> StructParam:
        return cls(**d)

    def to_dict(self) -> dict:
        return asdict(self)
    
@dataclass
class DroneState:
    pos: list = None
    velocity: ndarray = None
    orientation: list = None
    angular_velocity: list = None
    motor_rpm: list = None

    def __post_init_(self):
        if self.pos is None:
            self.pos = [0, 0, 0]

        if self.velocity is None:
            self.velocity = [0, 0, 0]

        if self.orientation is None:
            self.orientation = [0, 0, 0, 0]

        if self.angular_velocity is None:
            self.angular_velocity = [0, 0, 0]
        
        if self.motor_rpm is None:
            self.motor_rpm = [0, 0, 0, 0]

    @classmethod
    def from_dict(cls,d: dict) -> StructParam:
        return cls(**d)

    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_numpy(self) -> dict:
        return {
            'pos' : array(self.pos),
            'velocity' : array(self.velocity),
            'orientation' : array(self.orientation),
            'angular_velocity' : array(self.angular_velocity),
            'motor_rpm' : array(self.motor_rpm)
        }
