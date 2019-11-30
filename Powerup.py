from Obj3D import *

class Powerup(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        if "keg" in model:
            self.scaleAll(0.1)

        self.repositionToCenter()
        self.move(dz=self.dimZ/2)

        # Floating off the ground
        self.move(dz=-10)

        # TODO: Collisions
        
