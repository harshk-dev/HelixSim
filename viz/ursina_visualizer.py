from ursina import *
from ursina.shaders import lit_with_shadows_shader
from pathlib import Path
from viz import DroneViz, VizBase
from sim import SimDataManager
from math import degrees

class UrsinaVisualizer(VizBase):
    def __init__(self,data_manager: SimDataManager):
        application.asset_folder = Path(__file__).resolve().parent.parent / 'assets'
        self.app = Ursina()
        self.app.render.setShaderAuto()
        self.drone = None
        self.updater = Entity()
        self.data_manager = data_manager

    def run(self):
        self.app.run()

    def initialize(self):
        Entity.default_shader = lit_with_shadows_shader
        self.ground = Entity(
            model='plane',
            scale=200,
            texture='grass',
            texture_scale=(20,20)
            )
        AmbientLight(color=color.rgba(180, 180, 180, 255))
        self.sun = DirectionalLight(shadows=True)
        self.sun.look_at(Vec3(-5, -2, 1))
        Sky()

        with self.data_manager.get_lock():
            drone_pos = self.data_manager.get_drone_pos

        self.drone = DroneViz(x=drone_pos[0],y=drone_pos[2],z=drone_pos[1])

        camera.position = (10,40,-100)
        camera.look_at(self.drone.drone)
        # EditorCamera()

    def update(self,pos,orientation): 
        # print(time.dt) 
        self.drone.move(
            posx=pos[0],
            posy=pos[2],
            posz=pos[1],
            rotx=-degrees(orientation[0]),
            roty=-degrees(orientation[2]),
            rotz=-degrees(orientation[1]),
            RPM=10000,
            dt=time.dt
        )
        # print(self.drone.drone.x,self.drone.drone.y,self.drone.drone.z)
        camera.look_at(self.drone.drone)

    def update_param(self, new_param):
        pass
    
    def exit(self):
        self.app.quit()
