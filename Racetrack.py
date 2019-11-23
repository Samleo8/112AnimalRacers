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
    def parseTrackFile(fileName):
        points = []

        f = open(f"{fileName}.track", "r")
        
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
                raise Exception(f"Invalid format in line {lineNo} of {fileName}.track")

            for i, coord in enumerate(point):
                try:
                    point[i] = float(coord)
                except:
                    raise Exception(f"Invalid format in line {lineNo} of {fileName}.track")

            points.append(tuple(point))

        # Handle closing
        if points[0] != points[-1]:
            points.append(points[0])

        if len(points) <= 3:
            raise Exception(f"{fileName}.track: Not enough points to make a racetrack!")

        f.close()
        return points

    # Generate racetrack given fileName of track
    def generateRacetrackFromFile(self, fileName):
        points = Racetrack.parseTrackFile(fileName)

        # line: startPoint, dirVector
        lines = []
        sideTrackPoints = []
        N = len(points)
        for i in range(N-1):
            p0 = points[i]
            p1 = points[(i+1) % N]

            startPoint = p0
            directionVector = sub2Tuples(p1, p0)

            if directionVector == (0, 0, 0): continue

            line = (startPoint, directionVector)
            lines.append(line)
            sideTrackPoints.append(self.calculateSideTracks(line))

        N = len(lines)
        for i in range(N):
            self.genTrackFromLineToLine(
                sideTrackPoints[i], sideTrackPoints[(i+1) % N]
            )

        self.points = points
        self.lines = lines
        self.sideTrackPoints = sideTrackPoints

        return

    # Generate a track from spaced position to spaced position
    def genTrackFromLineToLine(self, sideTrack1, sideTrack2):
        p1a, p1b, angles = sideTrack1
        p2a, p2b, _ = sideTrack2

        print(p1a, p1b, "|", p2a, p2b)

        # First side track
        self.genWallsFromPointToPoint(p1a, p2a, angles)

        # Second side track
        self.genWallsFromPointToPoint(p1b, p2b, angles)

        return 

    def genWallsFromPointToPoint(self, startPoint, endPoint, angles=None):
        if angles == None: angles = (0, 0)
        thetha, phi = angles

        directionVector = sub2Tuples(endPoint, startPoint)
        distance = getVectorMagnitude(directionVector)

        if distance == 0: return

        # Walls needed to fill in the gap
        wallSize = self.wallDim[1]
        nWallsNeeded = math.ceil(distance / wallSize)

        for i in range(nWallsNeeded):
            pos = add2Tuples(
                startPoint, 
                multiplyVectorByScalar(directionVector, i * wallSize/distance)
            )
            wall1 = Wall(self.gameObj, "crate", pos=pos)
            wall1.rotate(dh=thetha, dp=phi)

    # Given a start pos, calculate positions of side track points with defined spacing from the center position
    # and with the correct facing (yaw) 
    # Returns pos1, pos2, (thetha, phi) 
    def calculateSideTracks(self, line, spacing=None):
        startPos, directionVector = line

        spacing = self.defaultWallSpacing if spacing == None else spacing

        directionVector = normaliseVector(directionVector)
        if directionVector == (0, 0, 0): return

        x, y, z = startPos
        directionVector = multiplyVectorByScalar(directionVector, spacing/2)
        a, b, c = directionVector

        pos1 = x - b, y + a, z
        pos2 = x + b, y - a, z

        try:
            thetha = -radToDeg(math.atan(a/b))
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

        return pos1, pos2, (thetha, phi)
