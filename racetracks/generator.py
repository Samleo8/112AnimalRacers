import math
import random

class RacetrackGenerator():
    def __init__(self, fileName=None, center=None, minRad=100, maxRad=500, steps=10):
        center = (0, 0) if center == None else center
        
        self.generatePoints(center, minRad, maxRad, steps)

        RacetrackGenerator.writePointsToFile(self.points, fileName=fileName)

        return

    def generatePoints(self, center, minRad, maxRad, steps):
        self.points = []
        cx, cy = center

        dAngle = (2 * math.pi) / (steps)

        for i in range(steps):
            dist = random.uniform(minRad, maxRad)
            height = random.randint(0, 11)

            angle = dAngle * i 

            x = dist * math.cos(angle)
            y = dist * math.sin(angle)
            z = height if random.random() < 0.25 else 0

            self.points.append( (x, y, z) )

        return self.points

    @staticmethod
    def writePointsToFile(points, fileName=None):
        fileName = "random" if fileName == None else fileName

        f = open("racetracks/" + fileName + ".track", "w")
        content = ""
        for point in points:
            for i in point:
                content += f"{i} "
            content+="\n"

        f.write(content)
        f.close()

RacetrackGenerator()
