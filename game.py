# Core imports
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import sys
import math
import os
import random

# Basic intervals
from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import *

# Task managers
from direct.task.Task import Task
import time

# 3D Object super class
from Obj3D import *

class Racecar(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        # Speed, positioning and sizing
        self.speed = 0.5
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

        print(self.offset)
        print(self.dimX, self.dimY, self.dimZ)

        self.initBasicCollisionBox("hittest", showBox=True)

class Passenger(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj
    
class Crate(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.scaleAll(0.01)
        self.move(dz=self.dimZ/2)

        self.initBasicCollisionBox("hittest", showBox=True)

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Get other stuff ready
        self.paused = False
        self.isGameOver = False

        Obj3D.worldRenderer = self.render

        # Load lights and the fancy background
        self.loadBackground()
        self.loadLights()

        # Load the various models
        self.loadModels()

        # Key movement
        self.isKeyDown = {}
        self.createKeyControls()

        # Init camera
        self.camConfigDefault = "fixed"
        self.camConfig = self.camConfigDefault
        self.taskMgr.add(self.setCameraToPlayer, "SetCameraToPlayer")

        # Check for key presses 
        # And do corresponding action
        self.taskMgr.add(self.keyPressHandler, "keyPressHandler")

        # Load collision handlers
        self.setupCollisionDetections()

    def setCameraToPlayer(self, task):
        car = self.car
        x, y, z = car.getPos()
        h, p, r = car.getHpr()

        # Math to make camera always facing player
        # And at a constant distance camDistance away
        # Note that cam distance is in the
        camDistance = car.dimY * 1.5

        # Allow for variable camera configuration
        if self.camConfig == "rotate":
            thetha = task.time * 2.5
        else:
            thetha = degToRad(h)

        xOffset = camDistance * math.sin(thetha)
        yOffset = -camDistance * math.cos(thetha)

        # Camera has a slight tilt
        phi = -45 # in degress
        camHeight = car.dimZ + 20

        self.camera.setPos(x + xOffset, y + yOffset, z + camHeight)
        self.camera.setHpr(radToDeg(thetha), phi, 0)

        return Task.cont

    # Load lights
    def loadLights(self):
        #add one light per face, so each face is nicely illuminated
        plight1 = PointLight('plight')
        plight1.setColor(VBase4(1, 1, 1, 1))
        plight1NodePath = render.attachNewNode(plight1)
        plight1NodePath.setPos(0, 0, 500)
        render.setLight(plight1NodePath)

        plight2 = PointLight('plight')
        plight2.setColor(VBase4(1, 1, 1, 1))
        plight2NodePath = render.attachNewNode(plight2)
        plight2NodePath.setPos(0, 0, -500)
        render.setLight(plight2NodePath)

        plight3 = PointLight('plight')
        plight3.setColor(VBase4(1, 1, 1, 1))
        plight3NodePath = render.attachNewNode(plight3)
        plight3NodePath.setPos(0, -500, 0)
        render.setLight(plight3NodePath)

        plight4 = PointLight('plight')
        plight4.setColor(VBase4(1, 1, 1, 1))
        plight4NodePath = render.attachNewNode(plight4)
        plight4NodePath.setPos(0, 500, 0)
        render.setLight(plight4NodePath)

        plight5 = PointLight('plight')
        plight5.setColor(VBase4(1, 1, 1, 1))
        plight5NodePath = render.attachNewNode(plight5)
        plight5NodePath.setPos(500, 0, 0)
        render.setLight(plight5NodePath)

        plight6 = PointLight('plight')
        plight6.setColor(VBase4(1, 1, 1, 1))
        plight6NodePath = render.attachNewNode(plight6)
        plight6NodePath.setPos(-500, 0, 0)
        render.setLight(plight6NodePath)

    def loadBackground(self):
        # Load the environment model.
        self.scene = Obj3D("environment")

        # Sky
        self.sky = Obj3D("FarmSky")

    def loadModels(self):
        self.car = Racecar(self, "groundroamer", self.render)

        self.crate = Crate(self, "crate", self.render)


    # Key Events
    def createKeyControls(self):
        # Create a function to key maps
        # "<function>": [ <list of key ids> ]
        functionToKeys = {
            "forward": [ "arrow_up" ],
            "backward": [ "arrow_down" ],
            "turnLeft": [ "arrow_left" ],
            "turnRight": [ "arrow_right" ],
            "camConfigRotate": ["space"]
        }

        for fn in functionToKeys:
            keys = functionToKeys[fn]

            # Initialise dictionary
            self.isKeyDown[fn] = 0

            for key in keys:
                # Key Down
                self.accept(key, self.setKeyDown, [fn, 1])

                # Key Up
                self.accept(key+"-up", self.setKeyDown, [fn, -1])

        self.accept("m-up", self.oobe)

    def setKeyDown(self, key, value):
        # In order to account for multiple keys
        # mapped to the same function
        # We increment isKeyDown by 1 if key down
        # and decrement if key up
        # This way even if another key is held down
        # the function still runs
        self.isKeyDown[key] += value

        # Make sure we don't go 
        # below 0 for any reason
        if self.isKeyDown[key] < 0:
            self.isKeyDown[key] = 0

    def keyPressHandler(self, task):
        # NOTE: In order to allow for diagonal movement
        #       we cannot use elif

        if self.paused or self.isGameOver:
            return

        # Get car's current forward facing direction based on its yaw angle
        # Then calculate dx and dy
        car = self.car
        dirAngle, _, _  = car.getHpr()
        dirAngle *= -(math.pi/180) # to rad

        # Note that max and cos are switched because car is facing y by default
        dy = car.speed * math.cos(dirAngle)
        dx = car.speed * math.sin(dirAngle)
        
        if self.isKeyDown["forward"] > 0:
            car.move(dx=dx, dy=dy)
        
        if self.isKeyDown["backward"] > 0:
            car.move(dx=-dx, dy=-dy)
        
        if self.isKeyDown["turnLeft"] > 0:
            dh = car.rotationSpeed
            car.rotate(dh=dh)

        if self.isKeyDown["turnRight"] > 0:
            dh = car.rotationSpeed * -1
            car.rotate(dh=dh)

        self.camConfig = self.camConfigDefault
        if self.isKeyDown["camConfigRotate"] > 0:
            self.camConfig = "rotate"

        return Task.cont
       
    # https://hub.packtpub.com/collision-detection-and-physics-panda3d-game-development/
    # Collision Events
    def setupCollisionDetections(self):
        self.colTrav = CollisionTraverser()
        self.colTrav.showCollisions(self.render)
        self.colNotifier = CollisionHandlerEvent()
        
game = Game()
base.run()
