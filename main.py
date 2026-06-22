import multiprocessing
import numpy as np
from sys import argv, exit
from PyQt6.QtWidgets import QApplication
from viz import VizBase, UrsinaVisualizer
from sim import StructParam, EnvParam, ControlParam, SimPresets, DroneState
from ui import ControlPanel

def run_ui(shared):
    app = QApplication(argv)
    panel = ControlPanel(shared)
    panel.show()
    exit(app.exec())

def run_engine(shared):
    drone_param = StructParam()
    visualizer: VizBase = UrsinaVisualizer()

    new_state = DroneState(
            # pos=np.array([0,150,0]),
            # velocity=np.array([0,2.5,0]),
            # orientation=np.array([0,0,0]),
            # angular_velocity=np.array([0,0,0]),
            # motor_rpm=np.array([40000,40000,40000,40000])
        )
    visualizer.initialize(drone_param)
    def update_engine():
        if shared['run_sim'] == 1:
            visualizer.update(new_state)

    visualizer.updater.update = update_engine
    visualizer.run()

def main():
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn",force=True)

    manager = multiprocessing.Manager()
    shared = manager.dict({
        "run_sim" : 0,
        "struct_param" : StructParam().to_dict(),
        "env_param" : EnvParam().to_dict(),
        "control_param" : ControlParam().to_dict(),
        "sim_presets" : SimPresets().to_dict(),
        "drone_state" : DroneState().to_numpy()
        })

    p_engine = multiprocessing.Process(target=run_engine,args=(shared,))
    p_ui = multiprocessing.Process(target=run_ui,args=(shared,))

    p_ui.start()
    p_engine.start()

    p_ui.join()
    p_engine.terminate()
    # p_engine.join()

if __name__ == "__main__":
    main()