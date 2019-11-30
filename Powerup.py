from Obj3D import *

class Powerup(Obj3D):
    nPowerups = 0
    types = {
        "speed": "bottle",
        "slow": "keg"
    }
    lastTime = 1000 # milliseconds

    def __init__(self, gameObj, powerupType=None, renderParent=None, pos=None, hpr=None):
        # Set powerup type
        if powerupType == None:
            types = list(Powerup.types.keys())
            powerupType = random.choice(types)

        self.powerupType = powerupType
        model = Powerup.types.get(self.powerupType, "speed")

        # Render
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        if "keg" == model:
            self.scaleAll(2)
        elif "bottle" == model:
            self.scaleAll(6)

        self.repositionToCenter()
        self.move(dz=self.dimZ/2)

        # Floating a little off the ground, and to the right and left a little
        dx = self.dimX * random.uniform(-5.0, 5.0)
        self.move(dx=dx, dz=self.dimZ/2)

        self.initCollisions()
        self.initAudio()

    def initCollisions(self):
        # Initialise bounding box for powerup
        self.initSurroundingCollisionObj("powerup", "sphere")

        colNode = self.getCollisionNode("powerup")
        colNode.node().setIntoCollideMask(self.gameObj.colBitMask["powerup"])

        colNode.setPythonTag("powerupType", self.powerupType)

    def initAudio(self):
        return
