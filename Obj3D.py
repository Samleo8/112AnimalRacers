'''
3D Object Class used by Racing Game

Allows for setting of positions, hpr,
model and parenting, and more.

Meant to be used as a super class 
for more complicated objects
'''

# Panda 3D imports
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase

# Audio managers
from direct.showbase import Audio3DManager

# Other libraries
import os
import math
import random
import re

# Angle Conversions
def degToRad(deg):
    return deg * (math.pi / 180.0)

def radToDeg(rad):
    return rad * (180.0 / math.pi)

def add2Tuples(tuple1, tuple2):
    tup = tuple()
    for i in range(len(tuple1)):
        tup += (tuple1[i] + tuple2[i],)
    return tup

def sub2Tuples(tuple1, tuple2):
    tup = tuple()
    for i in range(len(tuple1)):
        tup += (tuple1[i] - tuple2[i],)
    return tup

def isNumber(n):
    return isinstance(n, float) or isinstance(n, int)

def sameSign(n1, n2):
    return n1 * n2 >= 0

def getVectorMagnitude(vec):
    sm = 0
    for i in vec:
        sm += i ** 2
    return math.sqrt(sm)

def multiplyVectorByScalar(vec, scal):
    newVector = tuple()
    for i in vec:
        newVector += (i * scal,)

    return newVector

def normaliseVector(vec):
    mag = getVectorMagnitude(vec)
    if mag == 0:
        return vec
    else:
        return multiplyVectorByScalar(vec, 1/mag)

def intersectionOfLines(line1, line2):
    start1, dir1 = line1
    start2, dir2 = line2

    start1 = LVector3f(start1)
    start2 = LVector3f(start2)
    p = start2 - start1

    dir1 = LVector3f(dir1)
    dir2 = LVector3f(dir2)

    try:
        a = p.cross(dir2).length() / dir1.cross(dir2).length()
    except:
        a = 0

    intersectionPoint = start1 + dir1 * a

    return tuple(intersectionPoint)

def normaliseEuler(n):
    if n > 180:
        n -= 360
    elif n < -180:
        n += 360

    return n

class Obj3D(object):
    # Set worldRenderer in app loadModels
    worldRenderer = None
    audio3d = None

    modelTypes = ["bam", "egg", "gltf", "glb"]  # in order of priority

    def __init__(self, model, renderParent=None, pos=None, hpr=None):
        # Set model
        # Also check if we can load this model type
        self.modelName = model
        modelTypes = Obj3D.modelTypes
        modelFile = f"models/{model}"

        for modelType in modelTypes:
            tempModelFile = modelFile + "." + modelType

            if os.path.exists(tempModelFile):
                modelFile = tempModelFile
                break
        
        try:
            self.model = loader.loadModel(modelFile)
        except:
            raise Exception(f"Model {model} cannot be loaded")

        # Set rendering parent
        self.renderParent = renderParent \
            if renderParent != None else Obj3D.worldRenderer

        self.setRenderParent(self.renderParent)

        # Set positions/rotations
        self.pos = pos \
            if pos != None else (0, 0, 0)

        self.hpr = hpr \
            if hpr != None else (0, 0, 0)

        x, y, z = self.pos
        h, p, r = self.hpr

        self.setPos(x, y, z, centered=False)
        self.setHpr(h, p, r)

        # Set dimensions
        # Note that when the object is scaled, the coordinate systems are scaled as well.
        # Hence, the relative dimensions stay the same, and are used for anything which is a child of the object (such as collision boxes).
        # However, for movement and positioning etc, this is done in absolute coordinates
        self.relativeDim, self.relativeOffset = self.calculateDimensionsAndOffset()
        self.relDimX, self.relDimY, self.relDimZ = self.relativeDim
        self.relOffsetX, self.relOffsetY, self.relOffsetZ = self.relativeOffset

        # Collisions
        self.collisionNodes = { }

        # 3D Audio
        self.audio = { }

    # Collision Handling
    # Initialise a an object surrounding the whole player
    def initSurroundingCollisionObj(self, name=None, shape="box", show=False, args=None):
        name = name if name != None else self.modelName
        colNode = self.addCollisionNode(name)

        # Dynamically create a collision solid surrounding the object:
        # Shape:
        #   Box (default)
        #   Sphere 
        #   Capsule/Cylinder - requires args["axis"] to be set
        # Args:
        #   Axis: for capsule/cylinder
        #   Padding
        obj = self.genCollisionSolid(shape, args)

        colNode.node().addSolid(obj)

        if show: 
            colNode.show()

        return colNode

    # Create a collision solid dynamically based on 
    # offset center, dimensions and specified arguments
    def genCollisionSolid(self, shape="box", args=None):
        # Defaults
        padding = (0, 0, 0)
        axis = "y"
        
        # Load args if exists; else load defaults
        if isinstance(args, dict):
            axis = args.get("axis", axis)
            padding = args.get("padding", padding)

        padX, padY, padZ = padding

        if shape in [ "box", "rect", "square", "rectangle" ]:
            return CollisionBox(
                # calculated true center
                self.relativeOffset,  
                # dx, dy, dz
                self.relDimX/2 + padX, self.relDimY/2 + padY, self.relDimZ/2 + padZ
            )
        elif shape in [ "sphere" ]:
            return CollisionSphere(
                # calculated true center
                self.relOffsetX, self.relOffsetY, self.relOffsetZ, 
                # radius will be max of component of relative dimension
                max(add2Tuples(self.relativeDim, padding))/2
            )
        elif shape in [ "cylinder", "capsule" ]:
            # Get calcutated true center first
            sx, sy, sz = self.relativeOffset
            ex, ey, ez = self.relativeOffset

            if axis == "x":
                radMax = max(self.dimY + padY, self.dimZ + padZ)/2
                radMin = min(self.dimY + padY, self.dimZ + padZ)/2
                sx += self.dimX/2 - (radMin + padX)
                ex -= self.dimX/2 - (radMin + padX)
            elif axis == "y":
                radMax = max(self.dimX + padX, self.dimZ + padZ)/2
                radMin = min(self.dimX + padX, self.dimZ + padZ)/2

                sy += self.dimY/2 - (radMin + padY)
                ey -= self.dimY/2 - (radMin + padY)
            elif axis == "z":
                radMax = max(self.dimX, self.dimY)/2
                radMin = min(self.dimX, self.dimY)/2
                sz += self.dimZ/2 - (radMin + padZ)
                ez -= self.dimZ/2 - (radMin + padZ)
            else: 
                raise Exception("Invalid axis {axis} used!")
                return
            
            return CollisionCapsule(
                sx, sy, sz, # start point
                ex, ey, ez, # end point
                radMax
            )

        return None

    # Isolated collision node
    @staticmethod
    def createIsolatedCollisionObj(name, colSolid, parentNode=None, fromBitmask=None, intoBitmask=None, show=False):
        parentNode = Obj3D.worldRenderer if parentNode == None else parentNode
        
        colNode = parentNode.attachNewNode(
            CollisionNode(name)
        )
        colNode.node().addSolid(colSolid)

        if fromBitmask != None:
            colNode.node().setFromCollideMask(fromBitmask)

        if intoBitmask != None: 
            colNode.node().setIntoCollideMask(intoBitmask)

        if show:
            colNode.show()

        return colNode

    # Set texture
    def initTexture(self, textureName, override=1):
        texture = loader.loadTexture(f"models/tex/{textureName}.png")
        
        '''
        self.model.setTexGen(
            TextureStage.getDefault(), TexGenAttrib.MWorldPosition
        )
        '''
        self.model.setTexture(texture, override)

    # 3D Audio
    # NOTE: Stereo audio will not work; must convert to mono
    def attachAudio(self, audioName, loop=False, volume=1, dropOffFactor=1):
        audioTypes = ["wav", "ogg", "mp3"]  # in order of priority
        audioFile = f"audio/{audioName}"

        for audioType in audioTypes:
            tempaudioFile = audioFile + "." + audioType

            if os.path.exists(tempaudioFile):
                audioFile = tempaudioFile
                break

        audio3d = Audio3DManager.Audio3DManager(
            base.sfxManagerList[0], base.camera
        ) if Obj3D.audio3d == None else Obj3D.audio3d

        try:
            audio = audio3d.loadSfx(audioFile)
        except:
            raise Exception(f"Audio {audio} cannot be loaded")
        
        audio.setLoop(loop)
        audio.setVolume(volume)

        audio3d.attachSoundToObject(audio, self.model)
        audio3d.setDropOffFactor(dropOffFactor)

        self.audio[audioName] = audio
        
    # Relative movement and rotations
    def move(self, dx=0, dy=0, dz=0):
        x, y, z = self.getPos()
        self.setPos(x + dx, y + dy, z + dz, centered=False)
    
    def rotate(self, dh=0, dp=0, dr=0):
        h, p, r = self.getHpr()
        self.setHpr(h + dh, p + dp, r + dr)

    # Set and get positions and roll pitch yaw (hpr)
    def setPos(self, x, y, z, centered=True):
        self.x = x
        self.y = y
        self.z = z
        self.pos = (x, y, z)
        self.model.setPos(x, y, z)
        
        if centered: 
            self.repositionToCenter()

    def setHpr(self, h, p, r):
        h = normaliseEuler(h)
        self.hpr = (h, p, r)
        self.model.setHpr(h, p, r)

    def repositionToCenter(self):
        self.move(dx=-self.offsetX, dy=-self.offsetY, dz=-self.offsetZ)

    def lookAt(self, point):
        x, y, z = point
        self.model.lookAt(x, y, z)

    def getPos(self):
        self.pos = self.model.getPos()
        return self.pos

    def getHpr(self):
        self.hpr = self.model.getHpr()
        return self.hpr

    '''
    # Set/get/change velocities and accelerations
    def setSpeed(self, vx, vy, vz):
        self.speed = vx, vy, vz
        self.vx, self.vy, self.vz = self.speed

    def setAcceleration(self, ax, ay, az):
        self.acceleration = ax, ay, az
        self.ax, self.ay, self.az = self.acceleration

    def getSpeed(self):
        return self.speed

    def getAcceleration(self):
        return self.acceleration

    def incSpeed(self, vx=0, vy=0, vz=0):
        vx, vy, vz = add2Tuples(self.getSpeed(), (vx, vy, vz))
        self.setSpeed(vx, vy, vz)

    def updateMovement(self):
        self.incSpeed(self.ax, self.ay, self.az)
    '''

    # Set scale
    # Note that dimesions will change when scale changes
    # Hence, get dimensions must be updated in scale
    # However, note that get dimensions is slow.

    def setScale(self, scaleX=1, scaleY=1, scaleZ=1, getDim=False):
        self.model.setScale(scaleX, scaleY, scaleZ)

        if getDim: 
            self.calculateDimensionsAndOffset()

    def scaleAll(self, scaleXYZ=1, getDim=True):
        self.setScale(scaleXYZ, scaleXYZ, scaleXYZ, getDim)

    # Get dimensions
    # NOTE: These dimensions are absolute to the rendering parent
    # NOTE: Slow
    # https://discourse.panda3d.org/t/how-to-get-width-and-height-of-an-object/1490
    def calculateDimensionsAndOffset(self):
        pt1, pt2 = self.model.getTightBounds()

        x1, y1, z1 = pt1.getX(), pt1.getY(), pt1.getZ()
        x2, y2, z2 = pt2.getX(), pt2.getY(), pt2.getZ()

        # Calculate dimensions
        self.dimX = x2 - x1
        self.dimY = y2 - y1
        self.dimZ = z2 - z1

        # Calcuate offset from center
        self.offsetX = (x2 + x1)/2 - self.x
        self.offsetY = (y2 + y1)/2 - self.y
        self.offsetZ = (z2 + z1)/2 - self.z
        
        self.offset = (self.offsetX, self.offsetY, self.offsetZ)
        self.dim = (self.dimX, self.dimY, self.dimZ)
    
        return self.dim, self.offset

    def getDimensions(self):
        return self.dim

    def getOffset(self):
        return self.offset

    # Set parent to render to
    def setRenderParent(self, renderParent):
        self.model.reparentTo(renderParent)

    def destroy(self):
        self.model.removeNode()
    
    # Collisions
    def addCollisionNode(self, nodeName):
        colNode = self.model.attachNewNode(CollisionNode(nodeName))
        self.collisionNodes[nodeName] = colNode

        return self.collisionNodes[nodeName]

    def getCollisionNode(self, nodeName):
        obj = self.collisionNodes.get(nodeName)

        return obj
