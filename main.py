from viz import VizBase, UrsinaVisualizer
from sim import DroneParam, DroneState
import numpy as np

visualizer: VizBase = UrsinaVisualizer()

def update():
        new_state = DroneState(
            pos=np.array([0,150,0]),
            velocity=np.array([0,2.5,0]),
            orientation=np.array([0,0,0]),
            angularvelocity=np.array([0,0,0]),
            motor_rpm=np.array([40000,40000,40000,40000])
        )
        visualizer.update(new_state)

def main():
    drone_param = DroneParam()
    visualizer.initialize(drone_param)
    visualizer.run()


if __name__ == "__main__":
    main()