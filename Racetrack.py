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
    def __init__(self, gameObj, id=0):
        self.gameObj = gameObj

        # Get wall dimensions through a temporary wall
        tempWall = Wall(self.gameObj, "crate")
        self.wallDim = tempWall.getDimensions()
        self.wallOffset = tempWall.getOffset()
        tempWall.destroy()

        # Set wall spacing
        self.defaultWallSpacing = max(self.wallDim) + self.gameObj.player.dimX * 5 

        for i in range(10):
            center = (0, i * self.wallDim[1], 0)
            facingAngle = (0, 0, 0) # hpr
            self.createWallPair(center, facingAngle)

    def createWallPair(self, centerPos, facingAngle, spacing=None):
        spacing = self.defaultWallSpacing if spacing == None else spacing 

        positiveSpacing = (spacing/2, 0, 0)
        negativeSpacing = (-spacing/2, 0, 0)

        h, p, r = facingAngle

        wall1 = Wall(self.gameObj, "crate", pos=add2Tuples(centerPos, positiveSpacing))
        wall2 = Wall(self.gameObj, "crate", pos=add2Tuples(centerPos, negativeSpacing))

        return
