from Obj3D import *

class Racecar(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        # Speed, positioning and sizing
        self.defaultSpeed = 0.5
        self.speed = self.defaultSpeed
        self.rotationSpeed = 2

        # NOTE: When you scale, whatever coordinates used also scales
        self.scaleAll(1)

        # general way of making sure vehicle is always on the ground, regardless of that vehicle's center
        self.move(dz=self.relDimZ/2-self.offsetZ) 
        
        # Add passenger
        self.personName = "penguin"
        self.passenger = Passenger(
            self.gameObj,
            self.personName, self.model,
            pos, hpr
        )

        # Passenger's positions need to be adjusted to the actual center of the object
        self.passenger.scaleAll(2.5)
        self.passenger.move(dx=self.offsetX, dy=self.offsetY, dz=self.offsetZ)

        self.initSurroundingCollisionObj("car", "capsule")

        colNode = self.getCollisionNode("car")
        
        # Initialise pusher collision handling
        self.colPusher = CollisionHandlerPusher()

        # Credits to https://discourse.panda3d.org/t/collisions/58/7
        self.colPusher.addCollider(colNode, self.model, base.drive.node())
        self.colPusher.addInPattern('%fn-in-%in')
        self.colPusher.addOutPattern('%fn-out-%in')
        
        base.cTrav.addCollider(colNode, self.colPusher)

class Passenger(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj
    
