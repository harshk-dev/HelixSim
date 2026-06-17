from ursina import Entity,color
class drone_viz:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.draw()
        
    def draw(self,scale=1):
        self.drone = Entity(model='drone',color=color.white,scale=(scale,1,scale),x=self.x,y=self.y,z=self.z)
        self.prop1 = Entity(model='propeller',parent=self.drone,color=color.black,x=159,y=55,z=159)
        self.prop2 = Entity(model='propeller',parent=self.drone,color=color.black,x=-159,y=55,z=159)
        self.prop3 = Entity(model='propeller',parent=self.drone,color=color.black,x=-159,y=55,z=-159)
        self.prop4 = Entity(model='propeller',parent=self.drone,color=color.black,x=159,y=55,z=-159)

    def move(self,dt,roty):
        self.prop1.rotation_y += roty * dt
        self.prop2.rotation_y -= roty * dt
        self.prop3.rotation_y += roty * dt
        self.prop4.rotation_y -= roty * dt