from Obj3D import *
from Racecar import *

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

        # Get racecar dimensions through a temporary wall
        tempCar = Racecar(self.gameObj, "groundroamer")
        tempCarDim = tempCar.getDimensions()
        tempCar.destroy()

        # Set wall spacing
        self.defaultWallSpacing = max(self.wallDim) + tempCarDim[0] * 5

        # Generate racetrack
        self.points = []
        self.generateRacetrackFromFile("hexagon")
        
    # Parse the special race track file
    # Ignore comments which start with #
    # Returns a list of tuples of points
    # Includes the end point as the start point if necessary (need to close the loop)
    @staticmethod
    def parseTrackFile(fileName):
        points = []

        f = open(f"racetracks/{fileName}.track", "r")
        
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

        # TODO: Handle unless points
        if points[0] == points[-1]:
            points.pop()

        if len(points) <= 3:
            raise Exception(f"{fileName}.track: Not enough points to make a racetrack!")

        f.close()
        return points

    # Generate racetrack given fileName of track
    def generateRacetrackFromFile(self, fileName):
        points = Racetrack.parseTrackFile(fileName)

        # line: (startPoint, dirVector)
        # sideTrack: (sidetrackPoint1, sideTrack2, angles)
        N = len(points)

        leftTrackPoints = []
        rightTrackPoints = []

        # Find bounds of inner and outer tracks
        for i in range(N):
            point = points[i]

            dir1 = sub2Tuples(points[i-1], point)
            dir2 = sub2Tuples(points[(i+1) % N], point)

            # Remember to swap positions due to the way the points are calculated!
            p1a, p1b, _ = self.calculateSideTracks((point, dir1))
            p2b, p2a, angles = self.calculateSideTracks((point, dir2))

            # Left track
            sideLine1 = (p1a, dir1)
            sideLine2 = (p2a, dir2)
            pos = intersectionOfLines(sideLine1, sideLine2)
            leftTrackPoints.append((pos, angles))

            # Right track
            sideLine1 = (p1b, dir1)
            sideLine2 = (p2b, dir2)
            pos = intersectionOfLines(sideLine1, sideLine2)
            rightTrackPoints.append((pos, angles))
        
        # Now actually generate the tracks!
        for i in range(N):
            # Left Track
            p0, angles = leftTrackPoints[i]
            p1, _ = leftTrackPoints[(i+1) % N]

            self.genWallsFromPointToPoint(p0, p1, angles)

            # Right Track
            p0, angles = rightTrackPoints[i]
            p1, _ = rightTrackPoints[(i+1) % N]

            self.genWallsFromPointToPoint(p0, p1, angles)

        self.points = points

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
