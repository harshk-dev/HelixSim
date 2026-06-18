from ursina import Entity,color
class DroneViz:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.draw()
        
    def draw(self,scale=1):
        self.drone = Entity(
            model='drone',
            color=color.yellow,
            scale=(scale,1,scale),
            x=self.x,
            y=self.y,
            z=self.z
            )
        self.prop1 = Entity(
            model='propeller',
            parent=self.drone,
            color=color.black,
            x=159,
            y=55,
            z=159
            )
        self.prop2 = Entity(
            model='propeller',
            parent=self.drone,
            color=color.black,
            x=-159,
            y=55,
            z=159
            )
        self.prop3 = Entity(
            model='propeller',
            parent=self.drone,
            color=color.black,
            x=-159,
            y=55,
            z=-159
            )
        self.prop4 = Entity(
            model='propeller',
            parent=self.drone,
            color=color.black,
            x=159,
            y=55,
            z=-159
            )

    def move(self,velox,veloy,veloz,RPM,dt):
        # print(self.y)
        self.x += (velox * dt)
        self.drone.y += (veloy * dt)
        self.z += (veloz * dt)

        self.rotate_prop(RPM,dt)

    def rotate_prop(self,RPM,dt):
        rotation_per_sec = RPM / 60
        self.prop1.rotation_y += rotation_per_sec * dt
        self.prop2.rotation_y -= rotation_per_sec * dt
        self.prop3.rotation_y += rotation_per_sec * dt
        self.prop4.rotation_y -= rotation_per_sec * dt