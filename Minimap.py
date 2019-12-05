from Obj3D import *
from Racetrack import *

# Minimap generation
# Note that all the positioning is to be handled 
# in the render2d portion if we are to render the 2D version
class Minimap():
    def __init__(self, points, renderer, scaleFactor=100, color=None, thickness=2):
        self.scaleFactor = scaleFactor

        self.lineThickness = thickness
        self.lineColor = (1, 1, 1, 1) if color == None else color
        self.startLineColor = (1, 127/255, 0, 1)

        self.renderer = renderer

        self.loadPoints(points)
        self.draw()

        return

    def loadPoints(self, points):
        # Ensure aliasing doesn't get into the way
        points = copy.deepcopy(points)

        self.bounds = Minimap.getBounds(points) 

        self.minVec = LVector3f(
            self.bounds["x"][0], self.bounds["y"][0], self.bounds["z"][0]
        )

        self.maxVec = LVector3f(
            self.bounds["x"][1], self.bounds["y"][1], self.bounds["z"][1]
        )

        self.midPoint = (self.minVec + self.maxVec) / 2 - self.minVec
        self.midPoint /= self.scaleFactor

        # Need to normalise points to the minimap
        for i in range(len(points)):
            point = LVector3f(points[i]) - self.minVec

            points[i] = point / self.scaleFactor
            
        self.points = points

        return

    def draw(self):
        print("Drawing minimap")
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

    # TODO: Allow for minimap orbit via mouse drags
    # Adapted from https://discourse.panda3d.org/t/another-camera-controller-orbit-style/11545/2
    def setOrbit(self, orbit):
        if(orbit == True):
            props = base.win.getProperties()
            winX = props.getXSize()
            winY = props.getYSize()
            if base.mouseWatcherNode.hasMouse():
                mX = base.mouseWatcherNode.getMouseX()
                mY = base.mouseWatcherNode.getMouseY()
                mPX = winX * ((mX+1)/2)
                mPY = winY * ((-mY+1)/2)
            self.orbit = [(mX, mY), [mPX, mPY]]
        else:
            self.orbit = None

class MinimapPoint(Obj3D):
    def __init__(self, gameObj, minimap, isPlayer=False, renderParent=None, pos=None, hpr=None):
        self.gameObj = gameObj
        self.minimap = minimap

        # Set model
        #model = "minimap_playerdot" if isPlayer else "minimap_dot"
        model = "minimap_dot"
        modelFile = f"models/{model}"

        super().__init__(model, renderParent, pos, hpr)

        self.scaleAll(0.01)

        if isPlayer:
            self.initTexture("yellow")
        else: 
            self.initTexture("orange")

    def setScaledPos(self, x, y, z, centered=True):
        pos = x, y, z
        minimap = self.minimap

        scaledPos = (LVector3f(pos) - minimap.minVec) / minimap.scaleFactor
        x,y,z = tuple(scaledPos)
        
        self.setPos(x, y, z, centered)

