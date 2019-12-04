from Racetrack import *

# Minimap generation
# Note that all the positioning is to be handled 
# in the render2d portion if we are to render the 2D version
class Minimap():
    def __init__(self, points, renderer, scaleFactor=100, color=None, thickness=2):
        self.scaleFactor = scaleFactor

        self.lineThickness = thickness
        self.lineColor = (10, 10, 10, 1) if color == None else color
        self.startLineColor = (255, 127, 0, 1)

        self.renderer = renderer

        self.loadPoints(points)
        self.draw()

        return

    def loadPoints(self, points):
        # Ensure aliasing doesn't get into the way
        points = copy.deepcopy(points)

        self.bounds = Minimap.getBounds(points) 

        minVec = LVector3f(
            self.bounds["x"][0], self.bounds["y"][0], self.bounds["z"][0]
        )

        maxVec = LVector3f(
            self.bounds["x"][1], self.bounds["y"][1], self.bounds["z"][1]
        )

        self.midPoint = (minVec + maxVec) / 2 - minVec
        self.midPoint /= self.scaleFactor

        # Need to normalise points to the minimap
        for i in range(len(points)):
            point = LVector3f(points[i]) - minVec

            points[i] = point / self.scaleFactor
            
        self.points = points

        return

    def draw(self):
        # Setup
        lines = LineSegs("minimap")
        lines.setColor(self.lineColor)
        lines.setThickness(self.lineThickness)

        lines.moveTo(self.points[0])

        for point in self.points:            
            x, y, z = point

            lines.drawTo(x, y, z)

        lines.drawTo(self.points[0])

        self.lines = lines

        node = lines.create()
        self.renderNode = self.renderer.attachNewNode(node)

        return self.renderNode

    def clear(self):
        self.lines.reset()

    def reloadAndDraw(self, points, destroy=True):
        if destroy: self.destroy()

        self.loadPoints(points)
        self.clear()
        return self.draw()

    def destroy(self):
        self.renderNode.removeNode()

    @staticmethod
    def getBounds(points):
        trackBounds = {}

        x0, y0, z0 = points[0]

        trackBounds["x"] = (x0, x0)
        trackBounds["y"] = (y0, y0)
        trackBounds["z"] = (z0, z0)

        for x0, y0, z0 in points:
            trackBounds["x"] = (
                min(x0, trackBounds["x"][0]),
                max(x0, trackBounds["x"][1])
            )
            trackBounds["y"] = (
                min(y0, trackBounds["y"][0]),
                max(y0, trackBounds["y"][1])
            )
            trackBounds["z"] = (
                min(z0, trackBounds["z"][0]),
                max(z0, trackBounds["z"][1])
            )

        return trackBounds
