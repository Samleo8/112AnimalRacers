from Obj3D import *

class Crate(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.scaleAll(0.01)
        self.move(dz=self.dimZ/2-self.offsetZ)

        args = {
            "padding": (0, 0, 0)
        }

        self.initSurroundingCollisionObj("crate", args=args)


'''
Class holds all walls and floors
'''
class Racetrack(Obj3D):
    def __init__(self, id=0):
        for i in range(10):
            crate = Crate(self, "crate")
            crate.move(dx=i*crate.dimX, dy=crate.dimY*5)
