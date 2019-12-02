from Obj3D import *

class Ground(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        if model == "ground":
            self.setScale(scaleX=0.1, scaleY=0.02)

        self.move(dz=self.dimZ/2)

        args = {
            "padding": (0, 0, 0.01)
        }

        self.initSurroundingCollisionObj("floor", args=args, show=False)

        colNode = self.getCollisionNode("floor")
        colNode.node().setIntoCollideMask(self.gameObj.colBitMask["floor"])
        colNode.node().setFromCollideMask(self.gameObj.colBitMask["off"])

        # Make bottom extra big
        padZ = 10
        '''
        colBox = CollisionBox(
            # center is padZ below the floor
            (self.relOffsetX, self.relOffsetY, self.relOffsetZ - padZ),
            # dx, dy, dz
            self.relDimX/2, self.relDimY/2, self.relDimZ/2 + padZ
        )
        colPlane = CollisionPlane(
            Plane(Vec3(0, 0, 1), Point3(self.relativeOffset))
        )

        colNode = self.createIsolatedCollisionObj(
            "floor", colPlane, 
            fromBitmask=self.gameObj.colBitMask["off"], intoBitmask=self.gameObj.colBitMask["floor"],
            show = True
        )
        '''

class Terrain():
    def __init__(self, gameObj):
        self.gameObj = gameObj

        racetrack = self.gameObj.racetrack

        # Load infinitely extending floor
        '''
        planeSolid = CollisionPlane(
            Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
        )

        floorPlane = Obj3D.createIsolatedCollisionObj(
            "floor", planeSolid, intoBitmask=self.gameObj.colBitMask["floor"]
        )
        '''

        # Load ground
        #self.ground = Ground(self.gameObj, "ground")
        #self.ground.setScale(scaleX=1.5, scaleY=1.5)

        _, angles = racetrack.leftTrackPoints[0]
        pos = racetrack.points[0]

        self.startLine = Ground(self.gameObj, "cornfield", pos=pos)
        self.startLine.rotate(
            dh=angles[0], dp=angles[1])

        # Sky
        #self.sky = Obj3D("FarmSky")
