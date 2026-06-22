from ursina import *
from ursina.shaders import lit_with_shadows_shader
from pathlib import Path
from viz import DroneViz, VizBase

class UrsinaVisualizer(VizBase):
    def __init__(self):
        application.asset_folder = Path(__file__).resolve().parent.parent / 'assets'
        self.app = Ursina()
        self.app.render.setShaderAuto()
        self.drone = None
        self.updater = Entity()

    def run(self):
        self.app.run()

    def initialize(self, param):
        Entity.default_shader = lit_with_shadows_shader
        self.ground = Entity(
            model='plane',
            scale=2000,
            texture='grass',
            texture_scale=(20,20)
            )
        AmbientLight(color=color.rgba(180, 180, 180, 255))
        self.sun = DirectionalLight(shadows=True)
        self.sun.look_at(Vec3(-5, -2, 1))
        Sky()
        self.drone = DroneViz(x=0,y=150,z=0)


        camera.position = (500,400,-2000)
        camera.look_at(self.drone.drone)
        # EditorCamera()

    def update(self,state):   
        self.drone.move(
            velox=0,
            veloy=0,
            veloz=0,
            RPM=10000,
            dt=time.dt
        )
    
    def update_param(self, new_param):
        pass
    
    def exit(self):
        self.app.quit()
