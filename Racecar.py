from Obj3D import *
from Powerup import *
class Racecar(Obj3D):
    nRacecars = 0 # this will serve as the unique ID for collision node

    def __init__(self, gameObj, model, passenger=None, renderParent=None, pos=None, hpr=None):
        super().__init__("car_" + model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.initCarAndPassengerModels(model, passenger)

        if isinstance(self, DisplayCar):
            return 
        
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

        # Powerups
        self.activePowerup = None
        self.powerupSprite = None
        self.powerupActiveTime = None
        
        # Reset speeds and acceleration
        self.setSpeed(0, 0)
        self.setAcceleration(0, 0)

        # Init position on racetrack iff racetrack exists
        if hasattr(self.gameObj, "racetrack"):
            self.initOnRacetrack()

        self.initCollisions()

        self.initAudio()

    def initCarAndPassengerModels(self, carName=None, passengerName=None):
        # NOTE: When you scale, whatever coordinates used also scales
        # if carName == "racecar":
        #     self.scaleAll(2)

        # general way of making sure vehicle is always on the ground, regardless of that vehicle's center
        self.repositionToCenter()
        self.move(dz=self.dimZ/2)

        # Add passenger
        self.personName = "penguin" if passengerName == None else passengerName
        self.passenger = Passenger(
            self.gameObj,
            self.personName, self.model
        )

        # Passenger's positions need to be adjusted to the actual center of the object
        self.passenger.scaleAll(2.5)

        self.passenger.move(dx=self.relOffsetX,
                            dy=self.relOffsetY,
                            dz=self.relOffsetZ
                            )

    # Init 3D audio
    def initAudio(self):
        self.attachAudio("collision", loop=False,
                         volume=1.5, dropOffFactor=0.3)

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
            self.offsetX, self.offsetY, self.passenger.offsetZ + self.passenger.dimZ, 
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

        self.colCheckpointEvent.addInPattern('%fn-in-%in')
        self.colCheckpointEvent.addAgainPattern('%fn-again-%in')
        self.colCheckpointEvent.addOutPattern('%fn-out-%in')

        # Initialise simple sphere just to check for checkpoint and powerup passing
        fromBitmask = self.gameObj.colBitMask["checkpoint"] | self.gameObj.colBitMask["powerup"]

        colSphere = CollisionSphere(self.relOffsetX, self.relOffsetY, self.relOffsetZ, self.dimZ/2)

        self.colCheckpointNode = Obj3D.createIsolatedCollisionObj(
            self.getColNodeName("checkpoint"), colSphere, parentNode=self.model,
            fromBitmask=fromBitmask, intoBitmask=self.gameObj.colBitMask["off"],
            show=False
        )
        
        '''
        self.colCheckpointNode = self.initSurroundingCollisionObj(self.getColNodeName("checkpoint"), "capsule", show=True)
        self.colCheckpointNode.node().setFromCollideMask(fromBitmask)
        self.colCheckpointNode.node().setIntoCollideMask(self.gameObj.colBitMask["off"])
        '''

        # Collision Events
        # Make this dependent on the player ID to allow for individual event triggering
        colNodeName = self.getColNodeName("checkpoint")

        base.cTrav.addCollider(self.colCheckpointNode, self.colCheckpointEvent)

        self.gameObj.accept(f"{colNodeName}-in-checkpoint", self.onPassCheckpoint)
        self.gameObj.accept(f"{colNodeName}-out-powerup", self.onCollectPowerup)
    
    def initOnRacetrack(self, order=None):
        if order == None: 
            order = self.id

        # Assumes that racetrack has already been generated
        trackPoints = self.gameObj.racetrack.points

        startPos = LVector3f(trackPoints[0])
        dirVec = LVector3f(trackPoints[1]) - startPos
        dirVec.normalize()

        dist = (self.dimY + 2) * order

        pos = startPos + dirVec * dist 

        trackPoints = self.gameObj.racetrack.leftTrackPoints
        yawFacing = trackPoints[0][1][0]

        # Position setting
        x, y, z = pos
        self.setPos(x, y, z)

        # Rotate to face the closest checkpoint
        self.rotate(dh=yawFacing)

        # Init Passed Checkpoints array
        self.currLap = 0

        self.passedCheckpoints = [0 for i in range(len(trackPoints))]
        self.passedCheckpoints[0] = 1 # the first checkpoint is always passed

        return

    # POWERUPS
    def onCollectPowerup(self, entry):
        powerupType = entry.getIntoNodePath().getPythonTag("powerupType")

        if self.gameObj.printStatements: print(f"Car {self.id} has collected a {powerupType} powerup!")

        # Deactivate first (removes away the sprites)
        self.deactivatePowerup()

        # Now activate
        self.activatePowerup(powerupType)

        return

    def updatePowerup(self, taskTime):
        # Check if new powerup was updated
        if self.activePowerup != None:
            # New powerup
            if self.powerupActiveTime == None:
                self.powerupActiveTime = taskTime
            # Powerup needs to be deactivated
            elif taskTime - self.powerupActiveTime >= Powerup.lastTime:
                self.deactivatePowerup()

        return

    def activatePowerup(self, powerupType=None):
        if powerupType == None:
            powerupType = Powerup.pickRandom()

        self.activePowerup = powerupType
        self.powerupSprite = DisabledPowerup(
            self.gameObj, powerupType,
            renderParent=self.model,
            pos=self.offset
        )
        self.powerupSprite.move(dz=self.dimZ/2 + self.passenger.dimZ/2)

        if powerupType == "speed":
            self.incAcceleration(self.accInc * 12)

    def deactivatePowerup(self):
        self.powerupActiveTime = None
        self.activePowerup = None
        
        if self.powerupSprite != None:
            self.powerupSprite.destroy()
            #self.powerupSprite = None

    # CHECKPOINTS
    def onPassCheckpoint(self, entry):
        # Get passed checkpoint ID
        checkpointID = entry.getIntoNodePath().getPythonTag("checkpointID")

        # Make sure that previous checkpoint was passed before update
        if self.passedCheckpoints[checkpointID-1] > self.passedCheckpoints[checkpointID]:
            if self.gameObj.printStatements:
                print(f"Car {self.id}: Passed checkpoint {checkpointID}")
            self.passedCheckpoints[checkpointID] += 1
        # New lap
        elif checkpointID == 0 and self.passedCheckpoints[0] == self.passedCheckpoints[-1]:
            self.currLap += 1
            self.passedCheckpoints[0] += 1 

            # Check win condition
            totalLaps = self.gameObj.totalLaps

            # Player, so update on screen text
            if self.id == 0:
                self.gameObj.texts["lap"].setText(
                    f'Lap {self.currLap+1}/{totalLaps}')

            if self.currLap >= totalLaps:
                self.gameObj.gameOver(self)
            else:
                if self.gameObj.printStatements: print(f"Car {self.id}: Starting new lap {self.currLap} of {totalLaps}!")
        else:
            N = len(self.passedCheckpoints)
            if self.gameObj.printStatements: print(f"Car {self.id}: Need to pass checkpoint {(checkpointID+N-1)%N} first")

    def onCollideWall(self, entry):
        # Shield powerup negates all effects
        if self.activePowerup == "shield":
            return

        self.isCollidingWall = True
        self.setSpeed(0, 0)
        self.setAcceleration(0, 0)

        # 3D audio yay!
        if not self.gameObj.sfxMuted:
            self.audio["collision"].play()
        
    def onExitWall(self, entry):
        self.isCollidingWall = False
        return
        
    # Speeds and Acceleration handling
    # Note that speed/accel is singluar direction (where the car is facing)
    # There is also angular velocity

    # Set/get/change velocities and accelerations
    def setSpeed(self, spd=None, rotSpd=None):
        if isNumber(spd):
            if self.activePowerup == "speed":
                self.speed = spd
            else:
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

    # Calculations relative to points
    # NOTE: Euler system used
    def angleToPoint(self, point):
        # Calculate angle from current position (x, y) to next point
        x, y, _ = self.getPos()
        px, py, _ = point

        # Because it's in the euler coordinate system
        # swap [y|x] with [-x|y]
        return rad2Deg(math.atan2(x-px, py-y))

    def distanceToPoint(self, point, xyOnly=False):
        # Calculate distance from current position (x, y) to next point
        x, y, z = self.getPos()
        px, py, pz = point

        squared = (px - x) ** 2 + (py - y) ** 2

        if not xyOnly:
            squared += (pz - z) ** 2

        return math.sqrt(squared)

    # Update movement
    def updateMovement(self):
        # Friction
        useSpeedBasedFriction = (self.speed == 0) or (self.acceleration > 1.5 * self.friction)
        if useSpeedBasedFriction:
            friction = -self.friction * self.speed
        else:
            if self.speed > 0:
                friction = -self.friction
            elif self.speed < 0:
                friction = self.friction

        if self.activePowerup == "speed":
            friction *= 0.75

        self.incAcceleration(friction)

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

        # Reset
        if self.checkBelowGround():
            print(f"Oops, car {self.id} fell below ground")
            self.initOnRacetrack(0)
            return

    def updateMinimap(self, minimapPoint):
        x, y, z = self.getPos()
        minimapPoint.setScaledPos(x, y, z)

    # Check below ground
    def checkBelowGround(self):
        _, _, z = self.getPos()
        groundLevel = self.gameObj.racetrack.trackBounds["z"][0] - self.dimZ * 2

        return z < groundLevel

    # External Controls
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
        super().__init__("passenger_" + model, renderParent, pos, hpr)
        self.gameObj = gameObj

class DisplayCar(Racecar):
    '''
    def __init__(self, gameObj, model, passenger=None, renderParent=None, pos=None, hpr=None):
        super(Racecar, self).__init__("car_" + model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.initCarAndPassengerModels(model, passenger)
    '''
    pass
        
class StupidCar(Racecar):
    def __init__(self, gameObj, model, passenger=None, renderParent=None, pos=None, hpr=None):
        super().__init__(gameObj, model, passenger, renderParent, pos, hpr)
        
        # Stupid, but faster
        self.maxSpeed = 10
        self.friction = 0.01
        self.accInc = self.friction + 0.005

        self.allowStaticTurning = True 

    def artificialStupidity(self):
        r = random.random()
        if r < 0.2:
                self.doDrive("backwards")
        else:
            self.doDrive("forward")
        
        if r < 0.8:
            if random.random() < 0.5:
                self.doTurn("right")
            else:
                self.doTurn("left")

        return

    def updateMovement(self):
        self.artificialStupidity()
        super().updateMovement()

class NotSoStupidCar(StupidCar):
    def __init__(self, gameObj, model, passenger=None, renderParent=None, pos=None, hpr=None):
        super().__init__(gameObj, model, passenger, renderParent, pos, hpr)

    def artificialStupidity(self):
        if self.isCollidingWall:
            #self.doDrive("backwards")

            if random.random() > 0.5:
                self.doTurn("right")
            else:
                self.doTurn("left")
        else: 
            self.doDrive("forwards")

        return

class SmartCar(Racecar):
    def __init__(self, gameObj, model, passenger=None, renderParent=None, pos=None, hpr=None):
        super().__init__(gameObj, model, passenger, renderParent, pos, hpr)

        self.currentCheckpoint = 0
        self.allowStaticTurning = True

        self.maxSpeed *= 1.5
        self.defaultRotationSpeed *= 1.8
        self.maxRotationSpeed = 10

        self.isBeingStupid = False

    def onPassCheckpoint(self, entry):
        super().onPassCheckpoint(entry)

        # Update current checkpoint
        currCheckpoint = entry.getIntoNodePath().getPythonTag("checkpointID")

        # Went back the wrong way, reset to old checkpoint
        self.currentCheckpoint = currCheckpoint
        self.isBeingStupid = False

        return

    # Basically, the idea is to keep adjusting itself to the next checkpoint
    # This is done through the knowledge of the track's center point
    def artificialStupidity(self):
        # Get midpoint of next checkpoint
        trackPoints = self.gameObj.racetrack.points
        i = (self.currentCheckpoint+1) % len(trackPoints)
        gotoPoint = trackPoints[i]

        self.moveTowardsPoint(gotoPoint)

    # Is it trying to go forwards towards the checkpoint but constantly banging into a wall?
    # If so, readjust
    def checkStupidity(self, delta):
        if abs(delta) < 0.1 and self.isCollidingWall:
            self.doDrive("backwards")
            # Do not want to keep going back checkpoints
            if not self.isBeingStupid: 
                self.currentCheckpoint -= 1
            self.isBeingStupid = True
        return

    def moveTowardsPoint(self, point):
        angle = self.angleToPoint(point)

        yawFacing, _, _ = self.getHpr()
 
        # NOTE: Yaw facing should already be normalised in setHpr function
        delta = yawFacing - angle
        delta = normaliseEuler(delta)

        self.doDrive("forward")

        if abs(delta) < 0.01:
            self.doDrive("forward")
        elif delta < 0:
            self.doTurn("left")
        elif delta > 0:
            self.doTurn("right")

        self.checkStupidity(delta)
        
    def updateMovement(self):
        self.artificialStupidity()
        super().updateMovement()

# The smarter car will go for powerups
class SmartGreedyCar(SmartCar):
    def artificialStupidity(self):
        # Get midpoint of next checkpoint
        trackPoints = self.gameObj.racetrack.points
        i = (self.currentCheckpoint+1) % len(trackPoints)

        powerup = self.gameObj.racetrack.powerups[i-1]
        trackPoint = trackPoints[i]
        
        if self.isBeingStupid or powerup == None or self.activePowerup != None:
            gotoPoint = trackPoint
        else:
            powerupPoint = powerup.getPos()

            angle = self.angleToPoint(powerupPoint) - self.getHpr()[0]
            # Now check if the powerup point is behind or in front of the car
            if abs(angle) < 90:
                gotoPoint = powerupPoint
            else: 
                gotoPoint = trackPoint

        self.moveTowardsPoint(gotoPoint)
