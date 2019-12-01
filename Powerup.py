from Obj3D import *

class Powerup(Obj3D):
    nPowerups = 0
    types = {
        "shield": "shield",
        "speed": "bolt"
    }
    lastTime = 5 # seconds because task.time returns seconds

    @staticmethod
    def pickRandom(weights=None):
        if isinstance(weights, list):
            return random.choices(list(Powerup.types.keys()), weights)
        else:
            return random.choice(list(Powerup.types.keys()))

    def __init__(self, gameObj, powerupType=None, renderParent=None, pos=None, hpr=None):
        self.powerupType = Powerup.pickRandom() \
            if powerupType == None or powerupType == "random" else powerupType
        model = Powerup.types.get(self.powerupType, "speed")

        # Render
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        if "keg" == model:
            self.scaleAll(2)
        elif "bottle" == model:
            self.scaleAll(6)
        elif "shield" == model:
            self.scaleAll(1.5)
        elif "bolt" == model:
            self.scaleAll(1.2)

        self.repositionToCenter()
        self.move(dz=self.dimZ/2)

    def spin(self, amt=5):
        self.rotate(dh=amt)

# Active powerup with collisions
class ActivePowerup(Powerup):
    def __init__(self, gameObj, powerupType=None, renderParent=None, pos=None, hpr=None):
        super().__init__(gameObj, powerupType, renderParent, pos, hpr)

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

# Disabled powerup that's put on the top of the car
# Cannot have collisions otherwise issue for car
class DisabledPowerup(Powerup):
    def __init__(self, gameObj, powerupType, renderParent=None, pos=None, hpr=None):
        super().__init__(gameObj, powerupType, renderParent, pos, hpr)

        model = self.modelName
        if "keg" == model:
            self.scaleAll(0.6)
        elif "bottle" == model:
            self.scaleAll(1.5)
        elif "shield" == model:
            self.scaleAll(0.4)
        elif "bolt" == model:
            self.scaleAll(0.4)

        self.move(dz=1)


