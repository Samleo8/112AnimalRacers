from Obj3D import *

class Scene(Obj3D):
    def __init__(self, gameObj, model, renderParent=None, pos=None, hpr=None):
        super().__init__(model, renderParent, pos, hpr)
        self.gameObj = gameObj

        self.scaleAll(1)
        self.move(dz=self.dimZ/2)

        args = {
            "padding": (0, 0, 0)
        }

        # TODO: See https://www.panda3d.org/manual/?title=Bitmask_Example
        # TODO: Integrate https://discourse.panda3d.org/t/panda3d-collisions-made-simple/7441/12
        self.initSurroundingCollisionObj("floor", args=args, show=False)

        colNode = self.getCollisionNode("floor")
        colNode.node().setIntoCollideMask(self.gameObj.colBitMask["floor"])

class Terrain():
    def __init__(self, gameObj):
        self.gameObj = gameObj

        # Load floor/scene
        self.ground = Scene(self.gameObj, "ground")
        self.scene = Scene(self.gameObj, "cornfield")
        self.scene.move(dz=0)

        # Sky
        #self.sky = Obj3D("FarmSky")

