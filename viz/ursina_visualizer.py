from ursina import *
from pathlib import Path
from viz import drone_viz

app = Ursina()

ground = Entity(model='plane', scale=2000, color=rgb(255,0,0))


asset_dir_path = Path(__file__).resolve().parent.parent / 'assets'

application.asset_folder = asset_dir_path

drone = drone_viz(x=0,y=150,z=0)

def update():
    drone.move(dt=time.dt,roty=750)

EditorCamera()
app.run()
