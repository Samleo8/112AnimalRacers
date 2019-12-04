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
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from direct.gui.DirectGui import *

# Import External Classes
from Obj3D import *
from Racecar import *
from Racetrack import *
from Terrain import *
from Powerup import *

from RacetrackGenerator import *

# CameraController from https://discourse.panda3d.org/t/another-camera-controller-orbit-style/11545
from CameraController import *

class Game(ShowBase):
    fonts = {}
    selectedTrack = "random.track"
    selectedCar = "groundroamer"
    selectedPassenger = "penguin"
    level = "medium"

    currentState = None

    instructionsText = """\
Collect the powerups, and beat all the other cars to win! 
- Shield: You don't slow down when you hit the walls.
- Speed: Speed boost!

[WASD/Arrow Keys] Drive
[Hold Space] Drift

[1, 2] Change camera view
[Hold C] Look behind
[Hold V] Look around

[P] Pause and show help
[R] Restart Game
"""

    def __init__(self):
        ShowBase.__init__(self)
        
        Game.fonts["AmericanCaptain"] = loader.loadFont('AmericanCaptain.ttf')

        self.helpDialog = HelpDialog()

        self.nextState("start")

    def nextState(self, state):
        self.destroyInstance()

        state = state.lower().replace(" ", "")

        Game.currentState = state

        if state in [ "startscreen", "start" ]:
            StartScreen()
        elif state in [ "game", "racing", "racinggame", "main" ]:
            RacingGame()
        elif state in [ "racetrackselection", "racetrack", "track" ]:
            RacetrackSelection()
        elif state in ["racecarselection", "racecar", "car" ]:
            RacecarSelection()
        elif state in [ "instructions", "help" ]:
            InstructionsScreen()
        else:
            print(f"ERROR: State {state} not found")
            sys.exit()

    def destroyInstance(self):
        self.destroy()

class HelpDialog():
    def __init__(self):
        self.components = []
        self.hidden = False

        self.bg = OnscreenImage(
            image="img/startscreen.png",
            scale=(1.5, 1.5, 1)
        )
        self.components.append(self.bg)

        self.title = OnscreenText(
            text='Instructions', pos=(0, 0.7), scale=0.15,
            font=Game.fonts["AmericanCaptain"], bg=(255, 255, 255, 1),
            align=TextNode.ACenter, mayChange=False
        )
        self.components.append(self.title)

        self.instructions = OnscreenText(
            text=Game.instructionsText, pos=(0, 0.52), scale=0.08,
            font=Game.fonts["AmericanCaptain"], bg=(182, 182, 182, 0.5),
            align=TextNode.ACenter, mayChange=False,
            wordwrap=22
        )
        self.components.append(self.instructions)

        self.nextButton = DirectButton(
            text="Next", text_font=Game.fonts["AmericanCaptain"],
            scale=0.10, command=self.hide,
            pad=(0.3, 0.3),
            pos=(0, 0, -0.8),
            text_mayChange=True
        )
        self.components.append(self.nextButton)

        self.buttonHelperText = OnscreenText(
            text='[P]', pos=(0, -0.93), scale=0.07,
            font=Game.fonts["AmericanCaptain"],
            align=TextNode.ACenter, mayChange=True,
            bg=(182, 182, 182, 0.5),
        )
        self.components.append(self.buttonHelperText)

    def show(self):
        self.hidden = False
        for component in self.components:
            component.show()

    def hide(self):
        self.hidden = True
        for component in self.components:
            component.hide()

    def toggleVisible(self):
        if self.hidden:
            self.show()
        else:
            self.hide()

    def destroy(self):
        self.destroyed = True
        for component in self.components:
            component.destroy()

class StartScreen(Game):
    def __init__(self):
        ShowBase.__init__(self)

        concreteBg = OnscreenImage(
            image="img/startscreen.png",
            scale=(1.5, 1.5, 1)
        )

        title = OnscreenText(
            text='Animal Racers', pos=(0, 0.3), scale=0.32,
            font=Game.fonts["AmericanCaptain"],
            align=TextNode.ACenter, mayChange=False
        )

        text = OnscreenText(
            text='Difficulty:', pos=(-0.1, 0), scale=0.1,
            font=Game.fonts["AmericanCaptain"], bg=(255, 255, 255, 0.1),
            align=TextNode.ARight, mayChange=False
        )

        menu = DirectOptionMenu(
            scale=0.12,
            items=[ "Easy", "Medium", "Hard" ], initialitem=1,
            highlightColor=(10, 10, 10, 1),
            pad=(10, 10),
            pos=(0, 0, 0),
            popupMenu_pos=(-0.5, 0, 0),
            command=self.changeLevel,
            text_scale=0.8
        )

        startGameButton = DirectButton(
            text="Start  Game", text_font=Game.fonts["AmericanCaptain"],
            scale=0.15, command=self.startGame,
            pad=(0.3, 0.3),
            pos=(0, 0, -0.32)
        )

        spaceShortcut = OnscreenText(
            text='[Space]', pos=(0, -0.49), scale=0.08,
            font=Game.fonts["AmericanCaptain"],
            align=TextNode.ACenter, mayChange=False,
            bg=(182, 182, 182, 0.5)
        )

        '''
        helpButton = DirectButton(
            text="Help", text_font=Game.fonts["AmericanCaptain"],
            scale=0.15, command=self.showHelp,
            pad=(0.3, 0.3),
            pos=(0, 0, -0.45)
        )
        '''

        # Instructions
        helpText = """\
WASD/Arrow Keys to Drive | Hold Space to drift
1, 2 to change camera | Hold C to look behind
Hold V to look around | R to Restart
"""
        OnscreenText(
            text=helpText, pos=(0, -0.7), scale=0.1,
            bg=(255,255,255,0.7), wordwrap=18,
            font=Game.fonts["AmericanCaptain"],
            align=TextNode.ACenter, mayChange=False
        )

        # Next frame without clicking
        self.accept("space-up", self.startGame)

    def startGame(self):
        self.nextState("RacetrackSelection")

    def changeLevel(self, level):
        Game.level = level.lower()

class RacetrackSelection(Game):
    def __init__(self):
        ShowBase.__init__(self)

        '''
        concreteBg = OnscreenImage(
            image="img/startscreen.png",
            scale=(1.5, 1.5, 1)
        )
        '''

        title = OnscreenText(
            text='Select your Racetrack!', pos=(0, 0.65), scale=0.18,
            font=Game.fonts["AmericanCaptain"], bg=(255, 255, 255, 1),
            align=TextNode.ACenter, mayChange=False
        )

        nextButton = DirectButton(
            text="Next", text_font=Game.fonts["AmericanCaptain"],
            scale=0.10, command=self.selectCar,
            pad=(0.3, 0.3),
            pos=(0, 0, -0.8)
        )

        spaceShortcut = OnscreenText(
            text='[Space]', pos=(0, -0.93), scale=0.07,
            font=Game.fonts["AmericanCaptain"],
            align=TextNode.ACenter, mayChange=False,
            bg=(182, 182, 182, 0.5),
        )

        # Get List of tracks
        self.tracks = self.findTracks("racetracks")

        initialItem = self.tracks.index(Game.selectedTrack)

        # Minimap!        
        points = Racetrack.parseTrackFile(Game.selectedTrack)
        self.minimap = Minimap(points)
        self.minimapNode = render.attachNewNode(self.minimap.node)

        self.selectTrack(self.tracks[initialItem])

        self.menu = DirectOptionMenu(
            scale=0.15,
            items=self.tracks, initialitem=initialItem,
            highlightColor=(10, 10, 10, 1), 
            pad=(10, 10),
            pos=(-0.5, 0, 0.35),
            popupMenu_pos=(-0.5, 0, 0.2),
            command=self.selectTrack
        )

        randomiseButton = DirectButton(
            text="New Random Track", text_font=Game.fonts["AmericanCaptain"],
            scale=0.10, command=self.randomiseTrack,
            pad=(0.3, 0.3),
            pos=(-0.9, 0, 0.35)
        )

        self.randomText = OnscreenText(
            text='', pos=(-0.9, 0.20), scale=0.07,
            font=Game.fonts["AmericanCaptain"],
            align=TextNode.ACenter, mayChange=True,
            bg=(182, 182, 182, 0.5),
        )

        # Next frame without clicking
        self.accept("space-up", self.selectCar)
        
        # Add task to spin camera
        #self.taskMgr.add(self.trackShowcase, "TrackShowcase")

    # Define a procedure to move the camera.
    def trackShowcase(self, task):
        rotateTime = 3.0
        angle = task.time * rotateTime

        rad = 100
        camHeight = 100

        self.camera.setPos(
            rad * math.sin(angle), -rad * math.cos(angle), camHeight
        )
        self.camera.lookAt(0,0,0)
        return Task.cont

    def randomiseTrack(self):
        RacetrackGenerator()

        self.randomText.setText("Random track created!")

        self.menu.set(index=self.tracks.index("random.track"))

        self.selectTrack("random.track")

    def selectTrack(self, track):
        Game.selectedTrack = track

        points = Racetrack.parseTrackFile(track)
        self.minimapNode.removeNode()
        self.minimap.reloadAndDraw(points)
        self.minimapNode = render.attachNewNode(self.minimap.node)

        # Camera Control
        baseVec = LVector3f(0, 20, -3)
        # base.trackball.node().setPos(baseVec + self.minimap.midPoint)

        self.camControl = CameraController(
            camPos=baseVec - self.minimap.midPoint,
            anchorPos= self.minimap.midPoint
        )

    def selectCar(self):
        self.camControl.enabled = False
        self.nextState("racecar")

    def findTracks(self, path):
        if os.path.isfile(path):
            if path.endswith(".track"):
                return [path.replace("racetracks/", "", 1) ]
            else:
                return []
        elif os.path.isdir(path):
            tracks = []

            for f in os.listdir(path):
                tracks += self.findTracks(path + "/" + f)
            
            return tracks
        else:
            return []

class RacecarSelection(Game):
    def __init__(self):
        ShowBase.__init__(self)

        '''
        concreteBg = OnscreenImage(
            image="img/startscreen.png",
            scale=(1.5, 1.5, 1)
        )
        '''

        title = OnscreenText(
            text='Select your Racecar and Passenger!', pos=(0, 0.7), scale=0.18,
            font=Game.fonts["AmericanCaptain"], bg=(255, 255, 255, 1),
            align=TextNode.ACenter, mayChange=False
        )

        nextButton = DirectButton(
            text="Next", text_font=Game.fonts["AmericanCaptain"],
            scale=0.10, command=self.startGame,
            pad=(0.3, 0.3),
            pos=(0, 0, -0.8)
        )

        spaceShortcut = OnscreenText(
            text='[Space]', pos=(0, -0.93), scale=0.07,
            font=Game.fonts["AmericanCaptain"],
            align=TextNode.ACenter, mayChange=False,
            bg=(182, 182, 182, 0.5),
        )

        # Get List of cars
        self.cars = self.findCarsOrPassengers("models", "car_")

        initialCar = self.cars.index(Game.selectedCar)

        text = OnscreenText(
            text='Racecar:', pos=(-0.55, 0.4), scale=0.1,
            font=Game.fonts["AmericanCaptain"], bg=(255, 255, 255, 1),
            align=TextNode.ARight, mayChange=False
        )

        menu = DirectOptionMenu(
            scale=0.15,
            items=self.cars, initialitem=initialCar,
            highlightColor=(10, 10, 10, 1),
            pad=(10, 10),
            pos=(-0.5, 0, 0.4),
            command=self.selectCar
        )

        # Get List of passengers
        self.passengers = self.findCarsOrPassengers("models", "passenger_")

        initialPassenger = self.passengers.index(Game.selectedPassenger)
    
        text = OnscreenText(
            text='Passenger:', pos=(-0.55, 0.2), scale=0.1,
            font=Game.fonts["AmericanCaptain"], bg=(255, 255, 255, 1),
            align=TextNode.ARight, mayChange=False
        )

        menu = DirectOptionMenu(
            scale=0.15,
            items=self.passengers, initialitem=initialPassenger,
            highlightColor=(10, 10, 10, 1),
            pad=(10, 10),
            pos=(-0.5, 0, 0.2),
            command=self.selectPassenger
        )

        # If drawing is needed, passenger needs to be selected first
        self.displayedCar = None

        self.selectPassenger(self.passengers[initialPassenger])
        self.selectCar(self.cars[initialCar])

        # Next frame without clicking
        self.accept("space-up", self.startGame)

        # Add task to spin camera
        self.taskMgr.add(self.carShowcase, "CarShowcase")

    # Define a procedure to move the camera.
    def carShowcase(self, task):
        rotateTime = 3.0
        angle = task.time * rotateTime

        rad = 80
        camHeight = 10

        self.camera.setPos(
            rad * math.sin(angle), -rad * math.cos(angle), camHeight
        )
        self.camera.setHpr(radToDeg(angle), 0, 0)
        return Task.cont

    def selectCar(self, car):
        Game.selectedCar = car

        if self.displayedCar != None:
            self.displayedCar.destroy()

        pos = (0, 0, 0)
        self.displayedCar = DisplayCar(
            self, Game.selectedCar, Game.selectedPassenger, self.render, pos=pos
        )

        self.camera.setPos(10, 10, 10)
        self.camera.lookAt(pos)

    def selectPassenger(self, passenger):
        Game.selectedPassenger = passenger

        self.selectCar(Game.selectedCar)

    def findCarsOrPassengers(self, path, prefix=""):
        items = []

        for f in os.listdir(path):
            if f.startswith(prefix):
                f = f.replace(prefix, "", 1)
                for ext in Obj3D.modelTypes:
                    f = f.replace(f".{ext}", "", 1)
                items.append(f)

        return items

    def startGame(self):
        self.nextState("instructions")

class InstructionsScreen(Game):
    def __init__(self):
        ShowBase.__init__(self)

        self.helpDialog = HelpDialog()
        self.helpDialog.nextButton["command"] = self.startGame
        self.helpDialog.buttonHelperText.setText("[Space]")

        # Next frame without clicking
        self.accept("space-up", self.startGame)

    def startGame(self):
        self.nextState("game")

class RacingGame(Game):
    def __init__(self):
        ShowBase.__init__(self)

        # Get other stuff ready
        self.paused = False
        self.isGameOver = False
        self.gameOverTime = 0 # for camera rotation

        self.helpDialog = HelpDialog()
        self.helpDialog.hide()
        self.helpDialog.nextButton["command"] = self.togglePause

        self.totalLaps = 3

        Obj3D.worldRenderer = self.render

        # Generate texts
        self.texts = {}

        self.texts["lap"] = OnscreenText(
            text=f'Lap 1/{self.totalLaps}', pos=(-1.25, 0.8), scale=0.15,
            bg=(255, 255, 255, 0.7), font=Game.fonts["AmericanCaptain"],
            align=TextNode.ALeft, mayChange=True
        )

        # Load collision handlers
        self.collisionSetup(showCollisions=False)

        # Load Music
        # NOTE: Do before models so that cars can have audio3d object preinitialised
        self.loadAudio()

        # Load the various models
        self.loadModels()
        self.loadMinimap()

        # Load lights and the fancy background
        # NOTE: Racetrack needs to be generated first to properly generate the terrain
        self.loadBackground()
        self.loadLights()

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
        theta = degToRad(h)

        if "_rotate" in self.camConfig:
            if self.isGameOver and self.gameOverTime == 0:
                self.gameOverTime = task.time
            
            theta = (task.time - self.gameOverTime) * 2.5 + degToRad(h)

            # Stop rotation after n rotations
            nRotations = 3
            if self.isGameOver and theta - degToRad(h) >= ( (nRotations-1) * 2 * math.pi + math.pi):
                self.setCameraView("perspective_behind_win")
                self.pauseAudio()

        if "_behind" in self.camConfig:
            theta = degToRad(h - 180)

        xOffset = camDistance * math.sin(theta)
        yOffset = -camDistance * math.cos(theta)

        # Top-down view
        if self.camConfig == "birdsEye":
            xOffset = 0
            yOffset = 0
            camHeight = camDistance * 3

            phi = -90

            self.camera.setHpr(radToDeg(theta), phi, 0)
        # Camera has a slight tilt
        else:
            camHeight = player.dimZ * 2

        self.camera.setPos(x + xOffset, y + yOffset, z + camHeight)
        
        # Look forward a bit
        # Remember to calculate the perspective offset accordingly
        if "perspective" in self.camConfig:
            perspectiveOffset = 10
            xOffset = perspectiveOffset * math.sin(-theta)
            yOffset = perspectiveOffset * math.cos(-theta)
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

        self.texts["lap"].destroy()

        self.texts["gameOver"] = OnscreenText(
            text=winMsg, pos=(0, 0.8), scale=0.15,
            bg=(255, 255, 255, 0.7), wordwrap=20, 
            font=Game.fonts["AmericanCaptain"],
            align=TextNode.ACenter, mayChange=False
        )

        startGameButton = DirectButton(
            text="Restart Game", text_font=Game.fonts["AmericanCaptain"],
            scale=0.15, command=self.restartGame,
            pad=(0.3, 0.3),
            pos=(0, 0, -0.75)
        )

        # Make camera move and have the audio stop after
        self.setCameraView("perspective_rotate_win")
        return

    # Game Timer
    def gameTimer(self, task):
        if self.paused or self.isGameOver:
            return Task.cont

        for car in self.cars:
            car.updatePowerup(task.time)
            car.updateMovement()

        for powerup in self.racetrack.powerups:
            if powerup != None:
                powerup.spin()

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
        Racecar.nRacecars = 0
        Powerup.nPowerups = 0

        self.racetrack = Racetrack(self, Game.selectedTrack)

        # Only the positions are updated here because we want to space them out
        # But car facing and checkpoint handling are handled inside the init function
        self.player = Racecar(self, Game.selectedCar, Game.selectedPassenger, self.render)
        self.cars.append(self.player)

        # Basic levels
        # TODO: Maybe more cars (easy to add)?
        if Game.level == "easy":
            car1 = NotSoStupidCar(self, "racecar", 'bunny', self.render)
            car2 = NotSoStupidCar(self, "jeep", "chicken", self.render)
        elif Game.level == "hard":
            car1 = SmartGreedyCar(self, "groundroamer", "bunny", self.render)
            car2 = SmartGreedyCar(self, "jeep", "chicken", self.render)
        else: # normal level
            car1 = SmartCar(self, "groundroamer", 'bunny', self.render)
            car2 = SmartGreedyCar(self, "jeep", "chicken", self.render)

        self.cars.append(car1)
        self.cars.append(car2)

        print(f"Opponent cars generated with difficulty {Game.level}")

    def loadMinimap(self):
        return

    # Key Events
    def createKeyControls(self):
        # Create a function to key maps
        # "<function>": [ <list of key ids> ]   
        functionToKeys = {
            "forward": [ "arrow_up", "w" ],
            "backward": [ "arrow_down", "s" ],
            "turnLeft": [ "arrow_left", "a" ],
            "turnRight": [ "arrow_right", "d" ],
            "camConfigRotate": [ "v" ],
            "camConfigBehind": [ "c" ],
            "drifting": [ "space", "z" ]
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
            (self.restartGame, ["r"], None),
            (self.oobe, ["="], None),
            (self.togglePause, ["backspace"], [False]),
            (self.togglePause, ["p", "escape"], None)
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
            "wall": BitMask32.bit(0),
            "floor": BitMask32.bit(1),
            "checkpoint": BitMask32.bit(2),
            "powerup": BitMask32.bit(3),
            "offworld": BitMask32.bit(4)
        }

    def togglePause(self, showHelp=True):
        self.paused ^= True
        self.pauseAudio()

        print(showHelp)

        if showHelp:
            self.helpDialog.toggleVisible()

    def pauseAudio(self):
        # We need to pause music too
        for nm in self.audio:
            sound = self.audio[nm]

            playRate = 0 if self.paused or self.isGameOver else 1
            sound.setPlayRate(playRate)

    def restartGame(self):
        self.nextState("start")

game = Game()
game.run()
