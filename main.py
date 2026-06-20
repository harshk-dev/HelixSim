import multiprocessing
import numpy as np
from sys import argv, exit
from PyQt6.QtWidgets import QApplication
from viz import VizBase, UrsinaVisualizer
from sim import DroneParam, DroneState
from ui import ControlPanel

def run_ui():
    app = QApplication(argv)
    panel = ControlPanel()
    panel.show()
    exit(app.exec())

def run_engine():
    drone_param = DroneParam()
    visualizer: VizBase = UrsinaVisualizer()

    new_state = DroneState(
            pos=np.array([0,150,0]),
            velocity=np.array([0,2.5,0]),
            orientation=np.array([0,0,0]),
            angularvelocity=np.array([0,0,0]),
            motor_rpm=np.array([40000,40000,40000,40000])
        )
    visualizer.initialize(drone_param)
    visualizer.update(new_state)
    visualizer.run()

def main():
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn",force=True)

    p_engine = multiprocessing.Process(target=run_engine)
    p_ui = multiprocessing.Process(target=run_ui)

    p_ui.start()
    p_engine.start()

    p_ui.join()
    p_engine.terminate()
    # p_engine.join()

if __name__ == "__main__":
    main()