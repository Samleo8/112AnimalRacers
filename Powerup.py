from Obj3D import *

class Powerup(Obj3D):
    nPowerups = 0

    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        if "keg" in model:
            self.scaleAll(0.1)

        self.repositionToCenter()
        self.move(dz=self.dimZ/2)

        # Floating off the ground
        self.move(dz=-10)

        self.initCollisions()

        self.initAudio()

    def initCollisions(self):
        # Initialise bounding box for wall
        self.initSurroundingCollisionObj("powerup", "sphere")

        colNode = self.getCollisionNode("powerup")
        colNode.node().setIntoCollideMask(self.gameObj.colBitMask["powerup"])

    def initAudio(self):
        return