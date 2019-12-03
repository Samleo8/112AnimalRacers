import math
import random

class RacetrackGenerator():
    def __init__(self, fileName=None, center=None, minRad=200, maxRad=400, steps=10):
        center = (0, 0) if center == None else center
        
        self.generatePoints(center, minRad, maxRad, steps)

        RacetrackGenerator.writePointsToFile(self.points, fileName=fileName)

    def generatePoints(self, center, minRad, maxRad, steps):
        self.points = []
        cx, cy = center

        dAngle = (2 * math.pi) / (steps)

        # Clockwise is working but anticlockwise isn't
        for i in range(steps):
            dist = random.uniform(minRad, maxRad)
            height = random.randint(0, 11) * 2

            angle = dAngle * i * -1

            x = dist * math.cos(angle)
            y = dist * math.sin(angle)
            z = height if random.random() < 0.25 else 0

            self.points.append( (x, y, z) )

        print(f"Successfully generated {len(self.points)} points")

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

        print(f"Points successfully written to racetracks/{fileName}.track")
