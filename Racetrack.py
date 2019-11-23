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

        self.generateRacetrackFromFile("test")
        
    # Parse the special race track file
    # Ignore comments which start with #
    # Returns a list of tuples of points
    # Includes the end point as the start point if necessary (need to close the loop)
    @staticmethod
    def parseTrackFile(name):
        points = []

        f = open(f"{name}.track", "r")
        
        lineNo = 0
        for line in f:
            lineNo += 1
            # Remove away comments
            line = re.sub(r"\#(.+)", "", line).strip()

            # Ignore empty lines
            if len(line) == 0: 
                continue
            
            point = line.split(" ")
            # z-coordinate missing
            # default to 0
            if len(point) == 2:
                point.append(0)
            elif len(point) != 3:
                raise Exception(f"Invalid format in line {lineNo} of {name}.track")

            for i, coord in enumerate(point):
                try:
                    point[i] = float(coord)
                except:
                    raise Exception(f"Invalid format in line {lineNo} of {name}.track")

            points.append(tuple(point))

        # Handle closing
        if points[0] != points[-1]:
            points.append(points[0])

        f.close()
        return points

    # Generate racetrack given name of track
    def generateRacetrackFromFile(self, fileName):
        self.trackPoints = Racetrack.parseTrackFile(fileName)

        points = self.trackPoints

        for i in range(len(points)-1):
            self.genTrackFromPoint2Point(points[i], points[i+1])

        return

    # Generate a track from point to point
    def genTrackFromPoint2Point(self, point1, point2):
        directionVector = sub2Tuples(point2, point1)
        distance = getVectorMagnitude(directionVector)

        if distance == 0: return

        # Walls needed to fill in the gap
        wallSize = self.wallDim[1]
        nWallsNeeded = math.ceil(distance / wallSize)
        print("N Walls", nWallsNeeded, "Distance", distance)

        for i in range(nWallsNeeded):
            startPos = add2Tuples(
                point1, multiplyVectorByScalar(directionVector, i * wallSize/distance)
            )  
            self.createWallPair(startPos, directionVector)

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
