import pybullet as p
import pybullet_data
import time 
import numpy as np
import queue
from sim import SimDataManager

class PhysicsEngine:
    def __init__(self,ui_drone_state_queue,visualizer_drone_state_queue,data_manager:SimDataManager,rpm_func,kt=4.0e-6,km=1.5e-7,dt=1/240):
        self.data_manager = data_manager
        self.ui_queue = ui_drone_state_queue
        self.visualizer_queue = visualizer_drone_state_queue
        self.rpm_func = rpm_func
        self.KT = kt
        self.KM = km
        self.dt = dt
        self.j = 0
        self.running = False
        self.tick_count = 0
        with self.data_manager.get_lock():
            self.drone_pos = self.data_manager.get_drone_pos
            self.drone_velocity = self.data_manager.get_drone_velocity
            self.drone_orientation = self.data_manager.get_drone_orientation
            self.gravity = self.data_manager.data.env_param.gravity
        
        self.drone_orientation = p.getQuaternionFromEuler(self.drone_orientation)

    def initialize_engine(self):
        p.connect(p.DIRECT)
        p.setGravity(0,0,-9.81)
        p.setTimeStep(self.dt)
        self.load_assets()
        self.running = True

    def load_assets(self):
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        self.plane = p.loadURDF("plane.urdf")
        p.setAdditionalSearchPath("assets/")
        self.drone_id = p.loadURDF("drone.urdf",basePosition=self.drone_pos,baseOrientation=self.drone_orientation)

    def get_state(self,obj):
        pos, qat = p.getBasePositionAndOrientation(obj)
        euler = p.getEulerFromQuaternion(qat)
        velo, angular_velo = p.getBaseVelocity(obj)
        self.drone_pos = pos
        self.drone_orientation = euler
        self.drone_velocity = velo
    
    def broadcast_data(self,data_queue, dict):
        try:
            data_queue.put_nowait(dict)
        except queue.Full:
            pass
    
    def get_joint_index(self,obj):
        num_joints = p.getNumJoints(obj)
        for i in range(num_joints):
            joint_info = p.getJointInfo(obj,i)
            joint_index = joint_info[0]
            joint_name = joint_info[1]
            print(f"{joint_index} - {joint_name}")

    def run(self):
        while self.running:
            self.get_state(self.drone_id)
            if self.tick_count % 4 == 0:
                self.broadcast_data(
                    data_queue=self.visualizer_queue,
                    dict={
                        "pos" : self.drone_pos,
                        "orientation" : self.drone_orientation
                    })
                # self.broadcast_data(
                #     data_queue=self.ui_queue,
                #     dict={
                #         "height" : self.drone_pos[2]
                #     }
                # )

            # motorRPM = flight_controller.calculate_rpm(self.dt)
            # if self.j % 40 == 0 :
            #     print(self.drone_pos)
                # print(motorRPM)
            # print(f"pos {self.drone_orientation}")

            rpm = self.rpm_func(
                drone_pos=self.drone_pos,
                drone_velocity=self.drone_velocity,
                drone_orientation=self.drone_orientation,
                dt=1/240
            )

            omega = rpm * (2 * np.pi) / 60
            force = self.KT * (omega ** 2)
            torque = self.KM * (omega ** 2)
            torque[0] = -torque[0]
            torque[3] = -torque[3]

            for i in range(4):
                p.applyExternalForce(
                    objectUniqueId=self.drone_id,
                    linkIndex=4+(2*i),
                    forceObj=[0,0,force[i]],
                    posObj=[0,0,0],
                    flags=p.LINK_FRAME
                )
                p.applyExternalTorque(
                    objectUniqueId=self.drone_id,
                    linkIndex=4+(2*i),
                    torqueObj=[0,0,torque[i]],
                    flags=p.WORLD_FRAME
                )
            
            self.tick_count += 1
            self.j += 1
            self.follow_camera(look_at_pos=self.drone_pos)
            p.stepSimulation()
            time.sleep(self.dt)

    def follow_camera(self,look_at_pos,distance=2,yaw=0,pitch=0):
        p.resetDebugVisualizerCamera(
                cameraDistance=distance,
                cameraYaw=yaw,
                cameraPitch=pitch,
                cameraTargetPosition=look_at_pos
            )

    def exit(self):
        p.disconnect()


import multiprocessing
import numpy as np
from sim import SimDataManager, MotorMixing, TrajectoryManager
from control import TrajectoryFlightController
from time import sleep
from functools import partial
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
            
            # trajectory_manager = TrajectoryManager(dt=1/240)
            # trajectory_manager.hover_pos = np.array([1,0,4])
            # trajectory_manager.yaw = 0
            def path():
                return np.array([4,10,4]),0

            flight_controller = TrajectoryFlightController(
                motor_mix=motor_mixing.mix,
                trajectory_func=path,
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
        break

data_manager = SimDataManager('config/defaults.yaml')
ui_drone_state_queue = multiprocessing.Queue(maxsize=10)
visualizer_drone_state_queue = multiprocessing.Queue(maxsize=10)

run_physics_engine(ui_drone_state_queue,visualizer_drone_state_queue,data_manager)