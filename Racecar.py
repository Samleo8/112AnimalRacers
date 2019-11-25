from Obj3D import *

class Racecar(Obj3D):
    nRacecars = 0 # this will serve as the unique ID for collision node

    def __init__(self, gameObj, model, passenger=None, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.id = Racecar.nRacecars
        Racecar.nRacecars += 1

        # Speed, positioning and sizing
        self.defaultRotationSpeed = 1
        self.maxSpeed = 5
        self.maxSpeedBackwards = -3.5

        self.maxRotationSpeed = 5

        # Will be multiplied by current speed to provide the stopping force
        self.friction = 0.03
        self.accInc = self.friction + 0.005
        self.defaultRotationAcceleration = -0.1

        self.drifting = False
        self.allowStaticTurning = False

        self.isCollidingWall = False

        self.currLap = 0
        self.passedCheckpoints = []

        self.setSpeed(0, 0)
        self.setAcceleration(0, 0)

        # NOTE: When you scale, whatever coordinates used also scales
        self.scaleAll(1)

        # general way of making sure vehicle is always on the ground, regardless of that vehicle's center
        self.repositionToCenter()
        self.move(dz=self.dimZ/2) 
        
        # Add passenger
        self.personName = "penguin" if passenger == None else passenger
        self.passenger = Passenger(
            self.gameObj,
            self.personName, self.model
        )

        # Passenger's positions need to be adjusted to the actual center of the object
        self.passenger.scaleAll(2.5)
        self.passenger.move(dx=self.offsetX, dy=self.offsetY, dz=self.offsetZ)

        # Init position on racetrack iff racetrack exists
        if hasattr(self.gameObj, "racetrack"):
            self.initOnRacetrack()

        self.initCollisions()

    def getColNodeName(self, extras):
        return f"car_{self.id}_{extras}"

    def initCollisions(self):
        # Initialise bounding box for wall
        self.initSurroundingCollisionObj(self.getColNodeName("wall"), "capsule")

        colNode = self.getCollisionNode(self.getColNodeName("wall"))
        colNode.node().setFromCollideMask(self.gameObj.colBitMask["wall"])
        
        '''
        Wall Handling
        '''
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

        # Collision Events
        # Make this dependent on the player ID to allow for individual event triggering
        colNodeName = self.getColNodeName("wall")

        self.gameObj.accept(f"{colNodeName}-in-wall", self.onCollideWall)
        self.gameObj.accept(f"{colNodeName}-again-wall", self.onCollideWall)
        self.gameObj.accept(f"{colNodeName}-out-wall", self.onExitWall)

        '''
        Floor Handling
        '''
        self.colLifter = CollisionHandlerFloor()
        self.colLifter.setMaxVelocity(10)

        # Create the ray pointing from the bottom
        floorRayNode = self.addCollisionNode("floorRay")
        floorRayNode.node().addSolid(CollisionRay(
            #self.offsetX, self.offsetY, self.passenger.offsetZ+self.passenger.dimZ, 
            0, 0, 2,
            0, 0, -1
        ))
        floorRayNode.node().setFromCollideMask(self.gameObj.colBitMask["floor"])
        floorRayNode.node().setIntoCollideMask(0)

        self.colLifter.addCollider(floorRayNode, self.model)

        base.cTrav.addCollider(floorRayNode, self.colLifter)

        '''
        Checkpoint Handling
        '''
        # Init Event
        self.colCheckpointEvent = CollisionHandlerEvent()
        self.colCheckpointEvent.addOutPattern('%fn-out-%in')

        # Initialise simple sphere just to check for checkpoint passing
        colSphere = CollisionSphere(0, 0, 0, 1)
        self.colCheckpointNode = Obj3D.createIsolatedCollisionObj(
            self.getColNodeName("checkpoint"), colSphere, parentNode=self.model,
            fromBitmask=self.gameObj.colBitMask["checkpoint"], intoBitmask=self.gameObj.colBitMask["off"],
            show=True
        )

        # Collision Events
        # Make this dependent on the player ID to allow for individual event triggering
        colNodeName = self.getColNodeName("checkpoint")

        base.cTrav.addCollider(self.colCheckpointNode, self.colCheckpointEvent)

        self.gameObj.accept(f"{colNodeName}-out-checkpoint", self.onPassCheckpoint)
    
    def initOnRacetrack(self):
        # Assumes that racetrack has already been generated
        trackPoints = self.gameObj.racetrack.leftTrackPoints
        yawFacing = trackPoints[0][1][0]

        # Rotate to face the closest checkpoint
        self.rotate(dh=yawFacing)

        # Init Passed Checkpoints array
        self.currLap =0

        self.passedCheckpoints = [0 for i in range(len(trackPoints))]
        self.passedCheckpoints[0] = 1 # the first checkpoint is always passed

        return

    def onPassCheckpoint(self, entry):
        # Get passed checkpoint ID
        checkpointID = entry.getIntoNodePath().getPythonTag("checkpointID")
        
        # Make sure that previous checkpoint was passed before update
        if self.passedCheckpoints[checkpointID-1] > self.passedCheckpoints[checkpointID]:
            print(f"Car {self.id} successfully passed checkpoint {checkpointID}")
            self.passedCheckpoints[checkpointID] += 1
        # New lap
        elif checkpointID == 0 and self.passedCheckpoints[0] == self.passedCheckpoints[-1]:
            self.currLap += 1
            self.passedCheckpoints[0] += 1 

            # Check win condition
            # TODO: Gameover function
            totalLaps = self.gameObj.totalLaps
            if self.currLap >= totalLaps:
                self.gameObj.gameOver(self)
            else:
                print(f"Car {self.id} starting new lap {self.currLap} of {totalLaps}!")
        else:
            N = len(self.passedCheckpoints)
            print(f"Car {self.id} needs to pass checkpoint {(checkpointID+N-1)%N} first")


    def onCollideWall(self, entry):
        #self.isCollidingWall = True
        self.setSpeed(0, 0)
        self.setAcceleration(0, 0)
        return
        
    def onExitWall(self, entry):
        #self.isCollidingWall = False
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
        useSpeedBasedFriction = self.acceleration > 1.5 * self.friction
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
        accInc = self.accInc
        if direction in [ "backward", "backwards", "back", "reverse" ]:
            self.incAcceleration(-1 * accInc)
        else:
            self.incAcceleration(+1 * accInc)

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
    
import random

class StupidCar(Racecar):
    def __init__(self, gameObj, model, passenger=None, renderParent=None, pos=None, hpr=None):
        super().__init__(gameObj, model, passenger, renderParent, pos, hpr)

    def artificialStupidity(self):
        r = random.random()
        if r < 0.25:
            self.doDrive("backwards")

        else:
            self.doDrive("forward")
        
        if r < 0.5:
            if random.random() < 0.5:
                self.doTurn("right")
            else:
                self.doTurn("left")

        return

    def updateMovement(self):
        self.artificialStupidity()
        super().updateMovement()
