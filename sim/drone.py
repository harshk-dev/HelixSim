from dataclasses import dataclass
import numpy as np

@dataclass
class droneparam:
    mass: float = 1.0
    arm_len: float = 0.5
    prop_radius: float = 0.25
    no_arm: int = 4
    
@dataclass
class dronestate:
    pos: np.ndarray
    velocity: np.ndarray
    orientation: np.ndarray
    angularvelocity: np.ndarray
    motor_rpm: np.ndarray