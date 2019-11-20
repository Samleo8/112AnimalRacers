from direct.showbase.ShowBase import ShowBase

from panda3d.core import *

import random

class Application(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.cam.setPos(0, -50, 10)
        self.addSmiley()

    def addSmiley(self):
        self.car = loader.loadModel("smiley")
        self.car.reparentTo(render)
        self.car.setPos(0, 0, 10)

        col = self.car.attachNewNode(CollisionNode("car"))
        col.node().addSolid(CollisionSphere(0, 0, 0, 1.1))
        col.show()

        base.cTrav = CollisionTraverser()
        base.cTrav.showCollisions(render)
        pusher = CollisionHandlerPusher()

        pusher.addCollider(col, self.car, base.drive.node())
        #pusher.addCollider(colNode, base.camera , base.drive.node())

        # Unfortunately still does not fix it; fixes wall scaling part though?
        # TODO: Try http://www.panda3d.org/manual/?title=Rapidly-Moving_Objects
        pusher.setHorizontal(True)

        base.cTrav.addCollider(col, pusher)

    def initKeyEvents(self):
        self.accept("arrow_right-up", self.keyPress, ["right", 1])
        self.accept("arrow_left-up", self.keyPress, ["left", 1])

    

    def updateSmiley(self, task):
        return task.cont

app = Application()
app.run()
