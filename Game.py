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

# Audio managers
from direct.showbase import Audio3DManager

# GUI
from direct.gui.OnscreenText import OnscreenText

# Import External Classes
from Obj3D import *
from Racecar import *
from Racetrack import *
from Terrain import *
class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Get other stuff ready
        self.paused = False
        self.isGameOver = False
        self.gameOverTime = 0 # for camera rotation

        self.totalLaps = 3

        Obj3D.worldRenderer = self.render

        # Generate texts
        self.texts = {}
        self.texts["lap"] = OnscreenText(
            text=f'Lap 0/{self.totalLaps}', pos=(-1.25, 0.9), scale=0.08,
            bg=(255,255,255,0.7),
            align=TextNode.ALeft, mayChange=True
        )

        # Load collision handlers
        self.collisionSetup(showCollisions=False)

        # Load lights and the fancy background
        self.loadBackground()
        self.loadLights()

        # Load Music
        # NOTE: Do before models so that cars can have audio3d object preinitialised
        self.loadAudio()

        # Load the various models
        self.loadModels()

        # Key movement
        self.isKeyDown = {}
        self.createKeyControls()

        # Init camera
        self.camConfigDefault = "perspective"
        self.camConfig = self.camConfigDefault
        self.taskMgr.add(self.setCameraToPlayer, "SetCameraToPlayer")

        # Check for key presses 
        # And do corresponding action
        self.taskMgr.add(self.keyPressHandler, "KeyPressHandler")

        # Start a game timer
        self.taskMgr.add(self.gameTimer, "GameTimer")

    def setCameraToPlayer(self, task):
        # Focus on winning car when gameover
        player = self.player \
            if not self.isGameOver else self.winningCar
        
        x, y, z = player.getPos()
        h, p, r = player.getHpr()

        # Offset centers
        x += player.offsetX
        y += player.offsetY
        z += player.offsetZ

        # Math to make camera always facing player
        # And at a constant distance camDistance away
        # Note that cam distance is in the
        camDistance = player.dimY * 1.5

        # Allow for variable camera configuration
        thetha = degToRad(h)

        if "_rotate" in self.camConfig:
            if self.isGameOver and self.gameOverTime == 0:
                    self.gameOverTime = task.time
            
            thetha = (task.time - self.gameOverTime + degToRad(h)) * 2.5

            # Stop rotation after n rotations
            nRotations = 1
            if self.isGameOver and thetha >= nRotations * 2 * math.pi:
                self.setCameraView("perspective_behind_win")
                self.pauseAudio()

        if "_behind" in self.camConfig:
            thetha = degToRad(h - 180)

        xOffset = camDistance * math.sin(thetha)
        yOffset = -camDistance * math.cos(thetha)

        # Top-down view
        if self.camConfig == "birdsEye":
            xOffset = 0
            yOffset = 0
            camHeight = camDistance * 3

            phi = -90

            self.camera.setHpr(radToDeg(thetha), phi, 0)
        # Camera has a slight tilt
        else:
            camHeight = player.dimZ * 2

        self.camera.setPos(x + xOffset, y + yOffset, z + camHeight)
        
        # Look forward a bit
        # Remember to calculate the perspective offset accordingly
        if "perspective" in self.camConfig:
            perspectiveOffset = 10
            xOffset = perspectiveOffset * math.sin(-thetha)
            yOffset = perspectiveOffset * math.cos(-thetha)
            self.camera.lookAt(x + xOffset, y + yOffset, z)

        # Look at center of car
        if "_rotate" in self.camConfig:
            self.camera.lookAt(x, y, z)

        return Task.cont

    # Game over handling
    def gameOver(self, car):
        self.isGameOver = True
        self.winningCar = car  # self.cars[1]
        
        if car.id == 0: # player
            winMsg = f"Yay! You have won the game, beating {Racecar.nRacecars-1} other cars!"
        else:
            winMsg = f"Oh no! You have been beaten by car {car.id+1}!"

        print(winMsg)

        # Make camera move and have the audio stop after
        self.setCameraView("perspective_rotate_win")
        return

    # Game Timer
    def gameTimer(self, task):
        if self.paused or self.isGameOver:
            return Task.cont

        for car in self.cars:
            car.updateMovement()

        return Task.cont

    # Load Audio
    def loadAudio(self):
        audio3d = Audio3DManager.Audio3DManager(
            base.sfxManagerList[0], base.camera
        )
        Obj3D.audio3d = audio3d

        self.audio = {}

        # Bg audio
        bgAudio = base.loader.loadSfx("audio/purple_passion.mp3")
        bgAudio.setLoop(True)
        bgAudio.setVolume(0.05)

        bgAudio.play()
        
        self.audio["bg"] = bgAudio

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
        self.terrain = Terrain(self)

    def loadModels(self):
        self.cars = []
        self.racetrack = Racetrack(self, "hexagon")

        # Only the positions are updated here because we want to space them out
        # But car facing and checkpoint handling are handled inside the init function
        pos = self.racetrack.points[0]
        self.player = Racecar(self, "groundroamer", "penguin", self.render, pos=pos)
        car1 = StupidCar(self, "groundroamer", "bunny", self.render)
        car2 = NotSoStupidCar(self, "racecar", "chicken", self.render)

        self.cars.append(self.player)
        self.cars.append(car1)
        self.cars.append(car2)

    # Key Events
    def createKeyControls(self):
        # Create a function to key maps
        # "<function>": [ <list of key ids> ]   
        functionToKeys = {
            "forward": [ "arrow_up", "w" ],
            "backward": [ "arrow_down", "s" ],
            "turnLeft": [ "arrow_left", "a" ],
            "turnRight": [ "arrow_right", "d" ],
            "camConfigRotate": ["enter"],
            "camConfigBehind": ["space"],
            "drifting": [ "z" ]
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

        # Only need the key-release events
        # (fn, key list, args)
        keyReleaseMap = [
            (self.setCameraView, ["1"], ["perspective"]),
            (self.setCameraView, ["2"], ["birdsEye"]),
            (self.setCameraView, ["3"], ["firstPerson"]),
            (self.oobe, ["="], None),
            (self.togglePause, ["p", "Esc"], None)
        ]

        for fn, keys, args in keyReleaseMap:
            for key in keys:
                if isinstance(args, list) and len(args) > 0:
                    self.accept(key+"-up", fn, args)
                else:
                    self.accept(key+"-up", fn)

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

    def setCameraView(self, view):
        # Once win, only allow for win camera view
        if self.isGameOver and "_win" not in view:
            return

        self.camConfig = view
        print("Camera view set to: " + self.camConfig)

    def keyPressHandler(self, task):
        # NOTE: In order to allow for diagonal movement
        #       we cannot use elif

        if self.paused or self.isGameOver:
            return Task.cont    

        player = self.player

        if self.isKeyDown["drifting"] > 0:
            player.drifting = True
        else:
            player.drifting = False

        if self.isKeyDown["forward"] > 0:
            player.doDrive("forward")
            
        if self.isKeyDown["backward"] > 0:
            player.doDrive("backward")

        if self.isKeyDown["turnLeft"] > 0:
            player.doTurn("left")

        if self.isKeyDown["turnRight"] > 0:
            player.doTurn("right")

        if self.isKeyDown["camConfigRotate"] > 0:
            self.camConfig += "_rotate"
        else: 
            self.camConfig = self.camConfig.replace("_rotate", "")

        if self.isKeyDown["camConfigBehind"] > 0:
            self.camConfig += "_behind"
        else:
            self.camConfig = self.camConfig.replace("_behind", "")

        return Task.cont

    # https://hub.packtpub.com/collision-detection-and-physics-panda3d-game-development/
    # Collision Events
    def collisionSetup(self, showCollisions=False):
        base.cTrav = CollisionTraverser()

        if showCollisions:
            base.cTrav.showCollisions(render)

        # Set bitmasks
        # Reference: https://www.panda3d.org/manual/?title=Bitmask_Example
        self.colBitMask = {
            "off": BitMask32.allOff(),
            "wall": BitMask32.bit(0x04),
            "floor": BitMask32.bit(0x02),
            "checkpoint": BitMask32.bit(0x01)
        }

    def togglePause(self):
        self.paused ^= True
        self.pauseAudio()

    def pauseAudio(self):
        # We need to pause music too
        for nm in self.audio:
            sound = self.audio[nm]

            playRate = 0 if self.paused or self.isGameOver else 1
            sound.setPlayRate(playRate)

game = Game()
game.run()
