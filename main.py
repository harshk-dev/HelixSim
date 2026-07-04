import multiprocessing
import queue
import numpy as np
from sys import argv, exit
from PyQt6.QtWidgets import QApplication
from viz import VizBase, UrsinaVisualizer
from sim import SimDataManager, MotorMixing, TrajectoryManager
from control import TrajectoryFlightController
from physics import PhysicsEngine
from ui import ControlPanel
from time import sleep
from functools import partial

CONFIG_PATH = 'config/defaults.yaml'

def run_ui(data_manager: SimDataManager):
    app = QApplication(argv)
    panel = ControlPanel(data_manager)
    panel.show()
    exit(app.exec())

def run_engine(state_queue,data_manager: SimDataManager):
    visualizer: VizBase = UrsinaVisualizer(data_manager)

    visualizer.initialize()
    def update_engine(state_queue):
        if data_manager.data.run_sim == 1:
            try:
                data_dict = state_queue.get_nowait()
                visualizer.update(
                    pos=data_dict["pos"],
                    orientation=data_dict["orientation"]
                )
            except queue.Empty:
                pass

    visualizer.updater.update = partial(update_engine,state_queue)
    visualizer.run()

def run_physics_engine(ui_drone_state_queue,visualizer_drone_state_queue,data_manager: SimDataManager):
    # settings_change_flag = True
    while True:
        if data_manager.data.run_sim == 1:
            if data_manager.get_structural_preset == "quad":
                motor_num = 4
            elif data_manager.get_structural_preset == "octa":
                motor_num = 8
            
            with data_manager.get_lock():
                base_rpm = data_manager.data.control_param.base_rpm
                min_rpm = data_manager.data.control_param.min_rpm
                max_rpm = data_manager.data.control_param.max_rpm
                thrust_param = data_manager.data.thrust_pid_param
                roll_param = data_manager.data.roll_pid_param
                pitch_param = data_manager.data.pitch_pid_param
                yaw_param = data_manager.data.yaw_pid_param

            motor_mixing = MotorMixing(
                motor_num=motor_num,
                base_rpm=base_rpm,
                min_rpm=min_rpm,
                max_rpm=max_rpm
            )
            
            trajectory_manager = TrajectoryManager(dt=1/240)
            trajectory_manager.hover_pos = np.array([14,-20,30])
            trajectory_manager.yaw = 0

            flight_controller = TrajectoryFlightController(
                motor_mix=motor_mixing.mix,
                trajectory_func=trajectory_manager.trajectory_func,
                thrust_pid_param=thrust_param,
                roll_pid_param=roll_param,
                pitch_pid_param=pitch_param,
                yaw_pid_param=yaw_param,
                windup_limit=500
            )

            phy_engine = PhysicsEngine(
                ui_drone_state_queue,visualizer_drone_state_queue,data_manager,
                rpm_func=flight_controller.calculate_rpm
            )

            phy_engine.initialize_engine()
            phy_engine.run()
            phy_engine.exit()

        sleep(1/10)

def main():
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn",force=True)

    data_manager = SimDataManager(CONFIG_PATH)
    ui_drone_state_queue = multiprocessing.Queue(maxsize=10)
    visualizer_drone_state_queue = multiprocessing.Queue(maxsize=10)

    p_engine = multiprocessing.Process(target=run_engine,args=(visualizer_drone_state_queue,data_manager))
    p_ui = multiprocessing.Process(target=run_ui,args=(data_manager,))
    p_phy_engine = multiprocessing.Process(target=run_physics_engine,args=(ui_drone_state_queue,visualizer_drone_state_queue,data_manager))

    p_ui.start()
    p_engine.start()
    p_phy_engine.start()

    p_ui.join()
    # p_engine.join()
    p_engine.terminate()
    # p_phy_engine.join()
    p_phy_engine.terminate()

if __name__ == "__main__":
    main()