from Obj3D import *

class Racecar(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        # Speed, positioning and sizing
        self.defaultRotationSpeed = 2
        self.maxSpeed = 2
        self.maxSpeedBackwards = -2

        self.maxRotationSpeed = 5

        # Will be multiplied by current speed to provide the stopping force
        self.friction = 0.03
        self.accInc = self.friction + 0.005
        self.defaultRotationAcceleration = -0.1

        self.drifting = False
        self.allowStaticTurning = False

        self.setSpeed(0, 0)
        self.setAcceleration(0, 0)

        # NOTE: When you scale, whatever coordinates used also scales
        self.scaleAll(1)

        # general way of making sure vehicle is always on the ground, regardless of that vehicle's center
        self.repositionToCenter()
        self.move(dz=self.dimZ/2) 
        
        # Add passenger
        self.personName = "penguin"
        self.passenger = Passenger(
            self.gameObj,
            self.personName, self.model
        )

        # Passenger's positions need to be adjusted to the actual center of the object
        self.passenger.scaleAll(2.5)
        self.passenger.move(dx=self.offsetX, dy=self.offsetY, dz=self.offsetZ)

        self.initCollisions()

    def initCollisions(self):
        # Initialise bounding box
        self.initSurroundingCollisionObj("car", "capsule")

        colNode = self.getCollisionNode("car")
        
        # Wall Handling
        # NOTE: The way that pusher works is that it updates the NodePath model position on the collision
        # This means that the positions used to update the positions must be constantly updated from the 
        # __NodePath__ positions, not internal x,y,z positions stored in the class.
        # https://discourse.panda3d.org/t/player-goes-straight-through-walls-despite-collisionpusher/25368/7

        # Initialise pusher collision handling
        self.colPusher = CollisionHandlerPusher()

        # Credits to https://discourse.panda3d.org/t/collisions/58/7
        self.colPusher.addCollider(colNode, self.model, base.drive.node())
        #self.colPusher.addCollider(colNode, base.camera , base.drive.node())

        self.colPusher.addInPattern('%fn-in-%in')
        self.colPusher.addInPattern('%fn-again-%in')
        self.colPusher.addOutPattern('%fn-out-%in')
        
        # Problem is the racecar will attempt to scale the wall
        # TODO: Possible improvement: http://www.panda3d.org/manual/?title=Rapidly-Moving_Objects
        self.colPusher.setHorizontal(True)

        base.cTrav.addCollider(colNode, self.colPusher)

        # Floor Handling
        self.colLifter = CollisionHandlerGravity()

        # Create the ray pointing from the bottom
        colNode.node().addSolid(CollisionRay(
            #self.offsetX, self.offsetY, self.passenger.offsetZ+self.passenger.dimZ, 
            0, 0, 0,
            0, 0, -1
        ))
        self.colLifter.addCollider(colNode, self.model)

        # Note the cTrav scene will be under a different collider system
        #base.cTrav.addCollider(colNode, self.colLifter)


        # Collision Events
        self.gameObj.accept("car-in-wall", self.onCollideCrate)
        self.gameObj.accept("car-again-wall", self.onCollideCrate)
        self.gameObj.accept("car-out-wall", self.onExitCrate)

    def onCollideCrate(self, entry):
        self.setSpeed(0, 0)
        self.setAcceleration(0, 0)
        return
        
    def onExitCrate(self, entry):
        return
        
    # Speeds and Acceleration handling
    # Note that speed/accel is singluar direction (where the car is facing)
    # There is also angular velocity

    # Set/get/change velocities and accelerations
    def setSpeed(self, spd=None, rotSpd=None):
        if isNumber(spd):
            self.speed = min(max(spd, self.maxSpeedBackwards), self.maxSpeed) 

        if isNumber(rotSpd):
            self.rotationSpeed = min(rotSpd, self.maxRotationSpeed)

    def setAcceleration(self, acc=None, rotAcc=None):
        if isNumber(acc):
            self.acceleration = acc

        if isNumber(rotAcc):
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
        self.setSpeed(self.speed + dv, self.rotationSpeed + dw)

    def incAcceleration(self, da=0, dalpha=0):
        self.setAcceleration(self.acceleration + da, self.rotationAcceleration + dalpha)

    # Update movement
    def updateMovement(self):
        # Friction
        useSpeedBasedFriction = self.acceleration > self.friction
        if useSpeedBasedFriction:
            self.incAcceleration(-self.friction * self.speed)
        else:
            if self.speed > 0:
                self.incAcceleration(-self.friction)
            elif self.speed < 0:
                self.incAcceleration(self.friction)

        
        # Update the car's speed based on its acceleration
        prevSpeed = self.speed
        prevRotSpeed = self.rotationSpeed
        self.incSpeed(dv=self.acceleration, dw=self.rotationAcceleration)

        # Direction changed
        if not sameSign(prevSpeed, self.speed):
            self.setSpeed(spd=0)
            self.setAcceleration(acc=0)

        # Direction changed
        if not sameSign(prevRotSpeed, self.rotationSpeed):
            self.setSpeed(rotSpd=0)
            self.setAcceleration(acc=0, rotAcc=0)
        
        # Get car's current forward facing direction based on its yaw angle
        # Then calculate dx and dy
        dirAngle, _, _ = self.getHpr()
        dirAngle *= -(math.pi/180)  # to rad

        # Note that sin and cos are switched because car is facing y by default
        dy = self.speed * math.cos(dirAngle)
        dx = self.speed * math.sin(dirAngle)

        self.move(dx=dx, dy=dy)
        self.rotate(dh=self.rotationSpeed)

    # External Controls
    # TODO: Try https://www.panda3d.org/manual/?title=Bullet_Vehicles
    def doDrive(self, direction="forwards"):
        if direction in [ "backward", "backwards", "back", "reverse" ]:
            self.incAcceleration(-1 * self.accInc)
        else:
            self.incAcceleration(+1 * self.accInc)

    def doTurn(self, direction="left"):
        # Prevent static turning unless specified
        if self.speed == 0 and not self.allowStaticTurning:
            return

        # Direction changes depending on speed of the car
        if direction in [ "right", "clockwise", "cw" ]:
            _dir = -1 if self.speed >= 0 else +1 
        else: 
            _dir = +1 if self.speed >= 0 else -1

        rotSpd = _dir * self.defaultRotationSpeed
        rotAcc = _dir * self.defaultRotationAcceleration

        # Drifting!
        acc = 0 if self.drifting else None

        self.setSpeed(rotSpd=rotSpd)
        self.setAcceleration(acc=acc, rotAcc=rotAcc)

class Passenger(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj
    
