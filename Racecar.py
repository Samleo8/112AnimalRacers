from Obj3D import *

class Racecar(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        # Speed, positioning and sizing
        self.defaultSpeed = 0.5
        self.defaultRotationSpeed = 2
        self.maxSpeed = 1
        self.maxSpeedBackwards = -0.8

        self.maxRotationSpeed = 5

        # Will be multiplied by current speed to provide the stopping force
        self.friction = 0.2
        self.incAcceleration = self.friction + 0.1

        self.setSpeed(0, 0)
        self.setAcceleration(0, 0)

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

        # Collision 
        self.gameObj.accept("car-in-crate", self.collideCrate)
        self.gameObj.accept("car-out-crate", self.exitCrate)

    def collideCrate(self, entry):
        self.setSpeed(self.defaultSpeed/3, self.rotationSpeed)
        
    def exitCrate(self, entry):
        self.setSpeed(self.defaultSpeed, self.rotationSpeed)
        
    # Speeds and Acceleration handling
    # Note that speed/accel is singluar direction (where the car is facing)
    # There is also angular velocity

    # Set/get/change velocities and accelerations
    def setSpeed(self, spd=0, rotSpd=0):
        self.speed = min(max(spd, self.maxSpeedBackwards), self.maxSpeed) 
        self.rotationSpeed = min(rotSpd, self.maxRotationSpeed)

    def setAcceleration(self, acc=0, rotAcc=0):
        self.acceleration = acc
        self.rotationAcceleration = rotAcc

    def getSpeed(self):
        return self.speed

    def getAcceleration(self):
        return self.acceleration

    def getRotationSpeed(self):
        return self.rotationSpeed

    def getRotationAcceleration(self):
        return self.rotationAcceleration

    def incSpeed(self, dv=0, dw=0):
        self.setSpeed(self.speed + dv, self.rotationSpeed + self.rotationAcceleration)

    def updateMovement(self):
        # First 
        self.acceleration -= self.friction * self.speed
        prevSpeed = self.speed

        # Update the car's speed based on its acceleration
        self.incSpeed(dv=self.acceleration, dw=self.rotationAcceleration)

        # Direction changed
        if not sameSign(prevSpeed, self.speed):
            self.setSpeed(0, self.rotationSpeed)
            self.setAcceleration(0, self.rotationAcceleration)
        
        if self.speed: print(prevSpeed, self.speed)

        # Get car's current forward facing direction based on its yaw angle
        # Then calculate dx and dy
        dirAngle, _, _ = self.getHpr()
        dirAngle *= -(math.pi/180)  # to rad

        # Note that sin and cos are switched because car is facing y by default
        dy = self.speed * math.cos(dirAngle)
        dx = self.speed * math.sin(dirAngle)

        self.move(dx=dx, dy=dy)


class Passenger(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj
    
