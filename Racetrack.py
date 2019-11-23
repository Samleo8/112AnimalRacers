from Obj3D import *

class Wall(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.scaleAll(0.01)
        self.move(dz=self.dimZ/2-self.offsetZ)

        args = {
            "padding": (0, 0, 0)
        }

        self.initSurroundingCollisionObj("wall", args=args)


'''
Class holds all walls and floors
'''
class Racetrack(Obj3D):
    def __init__(self, id=0):
        for i in range(10):
            center = (0, 0, 0)
            facingAngle = (0, 0, 0) # hpr
            self.createWallPair(center, facingAngle)

    def createWallPair(self, centerPos, facingAngle, spacing=None):
        spacing = self.defaultWallSpacing if spacing != None else spacing 

        positiveSpacing = (spacing, 0, 0)
        negativeSpacing = (spacing, 0, 0)

        h, p, r = facingAngle

        wall1 = Wall(self, "crate")
        wall2 = Wall(self, "crate")

        return
