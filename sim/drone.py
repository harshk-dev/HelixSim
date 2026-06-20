from dataclasses import dataclass, field
import numpy as np
from typing import Callable

@dataclass
class DroneParam:
    mass: float = 1.0
    arm_len: float = 0.5
    prop_radius: float = 0.25
    no_arm: int = 4
    on_change: Callable = field(default=lambda:None,repr=False)
    
@dataclass
class DroneState:
    pos: np.ndarray
    velocity: np.ndarray
    orientation: np.ndarray
    angularvelocity: np.ndarray
    motor_rpm: np.ndarray