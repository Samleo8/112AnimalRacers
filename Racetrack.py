from Obj3D import *

import re

class Wall(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.scaleAll(0.01)

        self.repositionToCenter()
        self.move(dz=self.dimZ/2)

        args = {
            "padding": (0, 0, 0)
        }

        self.initSurroundingCollisionObj("wall", args=args)

'''
Class holds all walls and floors
'''
class Racetrack(Obj3D):
    def __init__(self, gameObj, id=0):
        self.gameObj = gameObj

        # Get wall dimensions through a temporary wall
        tempWall = Wall(self.gameObj, "crate")
        self.wallDim = tempWall.getDimensions()
        self.wallOffset = tempWall.getOffset()
        tempWall.destroy()

        # Set wall spacing
        self.defaultWallSpacing = max(self.wallDim) + self.gameObj.player.dimX * 5 

        self.trackPoints = self.parseRacetrackFile("test")

    # Parse the special race track file
    # Ignore comments which start with #
    # Returns a list of tuples of points
    # Includes the end point as the start point if necessary (need to close the loop)
    def parseRacetrackFile(self, name):
        startPoint = None
        points = []

        f = open(f"{name}.track", "r")
        
        for line in f:
            line = re.sub(r"\#(.+)", "", line).strip()
            print(line)

        f.close()
        return

    # Generate a track from point to point
    def genTrackFromPoint2Point(self, point1, point2):
        return

    # Given a start pos, position two walls with defined spacing from the center position
    # and with the correct facing (yaw) 
    def createWallPair(self, startPos, directionVector, spacing=None):
        spacing = self.defaultWallSpacing if spacing == None else spacing

        directionVector = normaliseVector(directionVector)
        if directionVector == 0: return

        x, y, z = startPos
        directionVector= multiplyVectorByScalar(directionVector, spacing/2)
        a, b, c = directionVector

        pos1 = x - b, y + a, z
        pos2 = x + b, y - a, z

        try:
            thetha = radToDeg(math.atan(a/b))
        except:
            thetha = 0 

        # TODO: Fix the z angle component
        try:
            phi = -radToDeg(math.atan(c/b))
        except:
            try:
                phi = -radToDeg(math.atan(c/a))
            except:
                phi = 0

        print(pos1, pos2)

        wall1 = Wall(self.gameObj, "crate", pos=pos1)
        wall2 = Wall(self.gameObj, "crate", pos=pos2)

        wall1.rotate(dh=thetha, dp=phi)
        wall2.rotate(dh=thetha, dp=phi)

        return
