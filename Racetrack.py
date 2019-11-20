from Obj3D import *

class Crate(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.scaleAll(0.01)
        self.move(dz=self.dimZ/2-self.offsetZ)

        args = {
            "padding": (self.relDimZ*5, self.relDimZ*5, 0)
        }

        self.initSurroundingCollisionObj("crate", args=args, show=True)
