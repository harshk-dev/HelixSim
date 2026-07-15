from ursina import *
from pathlib import Path
from viz import DroneViz, VizBase
from sim import SimDataManager
from math import degrees
from numpy import clip, array, asarray, ndarray

custom_fog_shader = Shader(language=Shader.GLSL, vertex='''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform vec2 tex_scale; // <-- ADD THIS: The scale variable from Python

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;
out vec3 world_pos;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    
    // MATH: Multiply the default texture coordinates by our custom scale!
    texcoord = p3d_MultiTexCoord0 * tex_scale; 
    
    // Calculate the real-world 3D position of the floor
    world_pos = (p3d_ModelMatrix * p3d_Vertex).xyz;
}
''', fragment='''
#version 140
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
in vec3 world_pos;
out vec4 fragColor;

// Variables we send from Python
uniform vec3 camera_pos;
uniform vec4 fog_color;
uniform float fog_start;
uniform float fog_end;

void main() {
    vec4 tex_color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;
    float dist = distance(camera_pos, world_pos);
    float fog_factor = clamp((dist - fog_start) / (fog_end - fog_start), 0.0, 1.0);
    fragColor = mix(tex_color, fog_color, fog_factor);
}
''')

class UrsinaVisualizer(VizBase):
    def __init__(self, data_manager: SimDataManager):
        application.asset_folder = Path(__file__).resolve().parent.parent / 'assets'
        self.app = Ursina()
        self.drone = None
        self.updater = Entity()
        self.data_manager = data_manager
        self.cam_pos = array([0, 50, -40])

    def run(self):
        self.app.run()

    def initialize(self):
        sky_color = Vec4(0.7, 0.75, 0.8, 1.0)
        
        window.color = sky_color
        camera.background_color = sky_color 
        
        camera.clip_plane_far = 650

        self.floor = Entity(
            model='plane',
            scale=1000,               
            texture='tile',
            collider='box',
            shader=custom_fog_shader
        )
        
        self.floor.set_shader_input('tex_scale', Vec2(50, 50))
        self.floor.set_shader_input('fog_color', sky_color)
        self.floor.set_shader_input('fog_start', 400)
        self.floor.set_shader_input('fog_end', 650)
        self.floor.set_shader_input('camera_pos', camera.world_position)

        AmbientLight(color=color.rgba(180, 180, 180, 255))
        self.sun = DirectionalLight(shadows=False)
        self.sun.look_at(Vec3(-5, -2, 1))
        
        with self.data_manager.get_lock():
            drone_pos = self.data_manager.get_drone_pos

        self.drone = DroneViz(x=drone_pos[0], y=drone_pos[2], z=drone_pos[1])

        camera.position = self.cam_pos
        camera.look_at(self.drone.drone)

    def update(self, pos, orientation, rpm): 
        self.drone.move(
            posx=pos[0],
            posy=pos[2],
            posz=pos[1],
            rotx=-degrees(orientation[0]),
            roty=degrees(orientation[2]),
            rotz=degrees(orientation[1]),
            RPM=rpm,
            dt=time.dt
        )
        cam_mode = self.data_manager.get_cam_mode
        if cam_mode == "follow":
            self.follow_cam(pos)
        elif cam_mode == "fixed":
            self.fixed_cam(pos)
        elif cam_mode == "origin":
            self.origin_cam(pos)
        
        self.floor.set_shader_input('camera_pos', camera.world_position)
        
    def update_param(self, new_param):
        pass

    def follow_cam(self, pos):
        self.cam_pos = self.vector_lerp(self.cam_pos,pos,array([0.025,0.025,0.1]))
        camera.position = (self.cam_pos[0], self.cam_pos[2], self.cam_pos[1]+20)
        camera.look_at(self.drone.drone)
        camera.rotation_z = 0

    def fixed_cam(self, pos):
        camera.position = (pos[0]+20, pos[2]+20, pos[1]-20)
        camera.look_at(self.drone.drone)
        camera.rotation_z = 0
        self.cam_pos = pos

    def origin_cam(self, pos):
        camera.position = (200, 200,-200)
        camera.rotation = (30,-45,0)
        self.cam_pos = array([200,200,-200])

    def vector_lerp(self,current, target, interpolation:ndarray):
        a = asarray(current, dtype=float)
        b = asarray(target, dtype=float)
        t = asarray(interpolation, dtype=float)
        t = clip(t, 0.0, 1.0)
        return a + t * (b - a)
    
    def exit(self):
        self.app.quit()