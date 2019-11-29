from Obj3D import *

class Ground(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        if model == "ground":
            self.setScale(scaleX=0.1, scaleY=0.08)

        self.move(dz=self.dimZ/2)

        args = {
            "padding": (0, 0, 0)
        }

        self.initSurroundingCollisionObj("floor", args=args, show=False)

        colNode = self.getCollisionNode("floor")
        colNode.node().setIntoCollideMask(self.gameObj.colBitMask["floor"])

class Terrain():
    def __init__(self, gameObj):
        self.gameObj = gameObj

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

        # self.scene = Ground(self.gameObj, "cornfield")
        # self.scene.move(dz=0)

        # Sky
        #self.sky = Obj3D("FarmSky")
