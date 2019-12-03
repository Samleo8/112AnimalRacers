# Adapted from https://discourse.panda3d.org/t/another-camera-controller-orbit-style/11545/2

# Core imports
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject

class CameraController(DirectObject):
    def	__init__(self, initZoom=5, camPos=None, anchorPos=None, zoomInLimit=1, zoomOutLimit=1000, moveSpeed=0.5):
        self.enabled = True

        base.disableMouse()
        
        self.setupVars(initZoom, camPos, anchorPos, zoomInLimit, zoomOutLimit, moveSpeed)
        self.setupCamera()
        self.setupInput()
        self.setupTasks()
        
    def setupVars(self, initZoom, camPos, anchorPos, zoomInLimit, zoomOutLimit, moveSpeed):
        self.initZoom = initZoom            # Camera's initial distance from anchor
        self.anchorPos = anchorPos if anchorPos != None else (0, -self.initZoom, 0)
        self.camPos = anchorPos if camPos == None else camPos

        self.zoomInLimit = zoomInLimit      # Camera's minimum distance from anchor
        self.zoomOutLimit = zoomOutLimit    # Camera's maximum distance from anchor
        self.moveSpeed = moveSpeed          # Rate of movement for the anchor
        self.zoom = None
        self.orbit = None
        self.move = None

    def setupCamera(self):
        self.camAnchor = render.attachNewNode("CameraAnchor")
        self.camAnchor.setPos(self.anchorPos)
        
        base.camera.reparentTo(self.camAnchor)
        base.camera.setPos(self.camPos)
        base.camera.lookAt(self.camAnchor)
        
    def setupInput(self):
        #self.accept("mouse1", self.setMove, [True])
        #self.accept("mouse1-up", self.setMove, [False])
        #self.accept("mouse2", self.setZoom, [True])
        #self.accept("mouse2-up", self.setZoom, [False])
        self.accept("mouse1", self.setOrbit, [True])
        self.accept("mouse1-up", self.setOrbit, [False])

    def setupTasks(self):
        taskMgr.add(self.cameraOrbit, "Camera Orbit")
        taskMgr.add(self.cameraZoom, "Camera Zoom")
        taskMgr.add(self.cameraMove, "Camera Move")
        
    def setOrbit(self, orbit):
        if not self.enabled: return
        
        if(orbit == True):
            props = base.win.getProperties()
            winX = props.getXSize()
            winY = props.getYSize()
            if base.mouseWatcherNode.hasMouse():
                mX = base.mouseWatcherNode.getMouseX()
                mY = base.mouseWatcherNode.getMouseY()
                mPX = winX * ((mX+1)/2)
                mPY = winY * ((-mY+1)/2)
            self.orbit = [[mX, mY], [mPX, mPY]]
        else:
            self.orbit = None

    def cameraOrbit(self, task):
        if(self.orbit != None):
            if base.mouseWatcherNode.hasMouse():
                
                mpos = base.mouseWatcherNode.getMouse()
                
                base.win.movePointer(0, int(self.orbit[1][0]), int(self.orbit[1][1]))
                
                deltaH = 90 * (mpos[0] - self.orbit[0][0])
                deltaP = 90 * (mpos[1] - self.orbit[0][1])
                
                limit = .5
                
                if(-limit < deltaH and deltaH < limit):
                    deltaH = 0
                elif(deltaH > 0):
                    deltaH - limit
                elif(deltaH < 0):
                    deltaH + limit
                    
                if(-limit < deltaP and deltaP < limit):
                    deltaP = 0
                elif(deltaP > 0):
                    deltaP - limit
                elif(deltaP < 0):
                    deltaP + limit

                newH = (self.camAnchor.getH() + -deltaH)
                newP = (self.camAnchor.getP() + deltaP)
                if(newP < -90): newP = -90
                if(newP > 90): newP = 90
            
                self.camAnchor.setHpr(newH, newP, 0)				
            
        return task.cont

    def setZoom(self, zoom):
        if(zoom == True):
            props = base.win.getProperties()
            winX = props.getXSize()
            winY = props.getYSize()
            if base.mouseWatcherNode.hasMouse():
                mX = base.mouseWatcherNode.getMouseX()
                mY = base.mouseWatcherNode.getMouseY()
                mPX = winX * ((mX+1)/2)
                mPY = winY * ((-mY+1)/2)
            self.zoom = [[mX, mY], [mPX, mPY]]
        else:
            self.zoom = None
        
    def cameraZoom(self, task):
        if(self.zoom != None):
            if base.mouseWatcherNode.hasMouse():
                
                mpos = base.mouseWatcherNode.getMouse()
                
                base.win.movePointer(0, int(self.zoom[1][0]), int(self.zoom[1][1]))
                
                deltaY = (mpos[1] - self.zoom[0][1]) * base.camera.getY()
                
                limit = .5
                
                if(-limit < deltaY and deltaY < limit):
                    deltaY = 0
                elif(deltaY > 0):
                    deltaY - limit
                elif(deltaY < 0):
                    deltaY + limit

                newY = (base.camera.getY() - deltaY)
                if(newY > -self.zoomInLimit): newY = -self.zoomInLimit
                if(newY < -self.zoomOutLimit): newY = -self.zoomOutLimit
            
                base.camera.setY(newY)				
            
        return task.cont
        
    def setMove(self, value):
        self.move = value
        
    def cameraMove(self, task):
        if(self.move == True):
            self.camAnchor.setY(self.camAnchor, self.moveSpeed)
            
        return task.cont
