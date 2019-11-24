# -*- coding: utf-8 -*-
"""
Gravity - how to better jump and bump over an uneven surface.

by fabius astelix @2010-02-04

Level: INTERMEDIATE

We put here together some of the cool stuff seen so far such as CollisionHandlerPusher to bump into walls, the CollisionHandlerEvent to react as soon as we touch something of our interest, but also we add a new dude to the team: CollisionHandlerGravity or, to better put it, we substitute the previous floor handler with a cooler one.

NOTE If you won't find here some line of code explained, probably you missed it in the previous steps - if you don't find there as well though, or still isn't clear for you, browse at http://www.panda3d.org/phpbb2/viewtopic.php?t=7918 and post your issue to the thread.
"""
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import ActorNode, CollisionHandlerEvent, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay, NodePath
from direct.interval.IntervalGlobal import *

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", """sync-video 0
"""
)
import direct.directbase.DirectStart
#** snippet support routines - not concerning the tutorial part
import snipstuff

#=========================================================================
# Scenographic stuff
#=========================================================================

base.cam.setPos(40, -70, 35)

splash=snipstuff.splashCard()
snipstuff.info.append("Gravity handler")
snipstuff.info.append("an advanced sample to setup a scene with pseudo gravity simulation.")
snipstuff.info.append("Try to put the avatar over a diveboard and then make it fall down to see what happen\n\nwasd=move the avatar around\nSPACE=avatar hiccup\n1-2-3=avatar over a diveboard")
snipstuff.info_show()

#=========================================================================
# Main
"""
Starting off step2, this time we just change the floor collider using a better one: CollisionHandlerGravity. This will provide us a better collision simulation than the former and adds some other goods we'll see how to make good use. Note that since it gives us a fine tuning over the floor simulation it is a handler useful when applied to just one single object, we'll see why later.
"""
#=========================================================================

#** Collision system ignition
base.cTrav=CollisionTraverser()

#** This is the new collision handler we use this time in place of the former CollisionHandlerFloor - this guy will give us better control over the floor simulation and some fancy settings like to set a constant gravity fallout or an easier way to make our avatar jump or also at which speed it smash to the ground falling down from heights.
avatarFloorHandler = CollisionHandlerGravity()
# Now we specify the gravitational force to apply. I know the earth gravity force is 9.81m/s but this handler apply it as the owner was without weight, so I add 25 as an additional weight to avoid our fat smiley ball to ridiculously float like a leaf. This said, now we start to get why this handler is better used just for a single object and why we named it like this - in other words this means that if we need it again for another avatar in the same scene we should instance and settle another one.
avatarFloorHandler.setGravity(9.81+25)
# we may limit the maximum speed that a falling object can reach in this way:
avatarFloorHandler.setMaxVelocity(100)
#
wallHandler = CollisionHandlerPusher()

#** Collision masks
FLOOR_MASK=BitMask32.bit(1)
WALL_MASK=BitMask32.bit(2)

#** Our steering avatar
avatarNP=base.render.attachNewNode(ActorNode('smileyNP'))
avatarNP.reparentTo(base.render)
avatar = loader.loadModel('smiley')
avatar.reparentTo(avatarNP)
# since our avatar origin is centered in a model sized 2,2,2, we need to shift it 1 unit above the ground
avatar.setPos(0,0,1)
avatar.setCollideMask(BitMask32.allOff())
avatarNP.setPos(0,0,15)
# The smiley collision sphere used to detect when smiley hits walls
avatarCollider = avatar.attachNewNode(CollisionNode('smileycnode'))
avatarCollider.node().addSolid(CollisionSphere(0, 0, 0, 1))
avatarCollider.node().setFromCollideMask(WALL_MASK)
avatarCollider.node().setIntoCollideMask(BitMask32.allOff())

#** Here we make a sensor to stick to the avatar - its role here is to precisely detect when the avatar touch the ground - note that there were several other ways to do that but this is our preferred way, as is using events. This way we'll be bothered just ASA the floor contact occurs, avoiding us to constantly peek an eye if the avatar is on ground or not, when he jump etc. How to prepare an event handler should be not a surprise to you if you passed by beginner/step3 but here there is a little difference, as is this sphere is just a sensor so we apply below a little method to set this.
collisionHandler = CollisionHandlerEvent()
avatarSensor = avatarNP.attachNewNode(CollisionNode('smileysensor'))
cs=CollisionSphere(0, 0, 0, 1.2)
avatarSensor.node().addSolid(cs)
avatarSensor.node().setFromCollideMask(FLOOR_MASK)
avatarSensor.node().setIntoCollideMask(BitMask32.allOff())
# as said above, to act correctly we need to make clear to the system that this is just a sensor, with no solid parts
cs.setTangible(0)
# you wanna see the sensor ball? just uncomment the following line then.
#avatarSensor.show()
# no great news here - peek an eye into novice-beginner/step3 if sound new to you
collisionHandler.addInPattern('%fn-into')
collisionHandler.addOutPattern('%fn-out')

#** Stick and set the ray collider to the avatar for ground collision detection
raygeometry = CollisionRay(0, 0, 2, 0, 0, -1)
avatarRay = avatarNP.attachNewNode(CollisionNode('avatarRay'))
avatarRay.node().addSolid(raygeometry)
# let's mask our floor FROM collider
avatarRay.node().setFromCollideMask(FLOOR_MASK)
avatarRay.node().setIntoCollideMask(BitMask32.allOff())

#** This is the terrain map - the egg model loaded contains also the collider geometry for the terrain and for the walls as childs
terrain = loader.loadModel("scene1")
terrain.reparentTo(render)
terrain.setCollideMask(BitMask32.allOff())
terrain.setScale(10)
# Let's mask our collision surfaces
floorcollider=terrain.find("**/floor_collide")
floorcollider.node().setIntoCollideMask(FLOOR_MASK)
wallcollider=terrain.find("**/wall_collide")
wallcollider.node().setIntoCollideMask(WALL_MASK)

#** As usual the floor handler need to know what it got to handle: the ray coupled with the avatar node wrapping everything related to smiley avatar
avatarFloorHandler.addCollider(avatarRay, avatarNP)
# ...and for the walls the avatar sphere collider together with - again - the avatar nodepath
wallHandler.addCollider(avatarCollider, avatarNP)

#** This flag is just for the show, to avoid the impact detection while unwanted moments like at startup or placing smiley above a diveboard
dont_care_ground_impact=True

#** Let's start the 3 collision handlers
base.cTrav.addCollider(avatarRay, avatarFloorHandler)
base.cTrav.addCollider(avatarCollider, wallHandler)
base.cTrav.addCollider(avatarSensor, collisionHandler)

#** Make the smiley roll on the the floor
def avatarwalk(dt, vel):
  if vel[0]: avatar.setR(avatar.getR()+(40*vel[0]))
  if vel[1]: avatar.setP(avatar.getP()+(-38*vel[1]))

#** Look here how simple is to make smiley jump: it is enough to set the floorhandler addVelocity member - not only this but we may easily know when let it jump testing if it is on the ground or not with isOnGround(). You also see then that since this velocity is applied to the whole handler, everything under its control (everything we applied addCollider()) will start to jump.
# Note: this function below is of course summoned outside this script file
def avatarjump(dt):
  if avatarFloorHandler.isOnGround():
    avatarFloorHandler.addVelocity(20)

#** Now we're ready to activate the avatar steering and go
steering=snipstuff.avatar_steer(avatarNP, avatarwalk, avatarjump, fwspeed=12.)
steering.start()

def avatar_on_diveboard(pos): avatarNP.setPos(pos)
snipstuff.DO.accept('1', avatar_on_diveboard, [(.83, -17.18, 10)])
snipstuff.DO.accept('2', avatar_on_diveboard, [(.83, -22.06, 20)])
snipstuff.DO.accept('3', avatar_on_diveboard, [(.83, -25.31, 30)])

#** The following stuff looks a bit complicated and maybe it is partially outside the snippet purposes, but there is something very important to see: all af this detect when the avatar touch the ground and, more important, at which speed, allowing us to make cute nifty things that give life to our games as, i.e., to making act smiley differently depending on the speed it smashes to the ground.
def smileySensorIn(e):
  # hope this don't add confusion: this is a task I made to see when the avatar effectively touch the ground and this happens just when the floor handler method isOnGround() returns true.
  def smileyHitTheGround(task):
    global dont_care_ground_impact

    if avatarFloorHandler.isOnGround():
      if dont_care_ground_impact: dont_care_ground_impact=False
      else:
        # Here is how to get the impact speed. To have a reliable value we got first to wait that the gravity collision routines sets isOnGround() to return True, otherwise if we grab the value returned just after the collision hit between the smiley sensor and the ground, we'll have a very inaccurate value.
        iv=abs(avatarFloorHandler.getImpactVelocity())
        t=""
        if iv > 42:
          t+="\nOh No, I guess is dead!"
          Sequence(
            Func(avatar.setHpr, (0,0,0)),
            Func(avatar.setScale, (3,3,.1)),
            Wait(3), Func(avatar.setScale, (1,1,1)),
            Func(snipstuff.infotext['message'].setText, ""),
          ).start()
        elif iv > 32:
          t+="\nCall an ambulance, quick!"
          Sequence(
            Func(avatar.setHpr, (0,0,0)),
            Func(avatar.setScale, (2,2,.5)),
            Func(avatar.setColor, (1,0,0,1)),
            Wait(.3), Func(avatar.setScale, (1,1,1)),
            Func(avatarNP.setZ, avatarNP.getZ()+5),
            Wait(3), Func(avatar.setColor, (1,1,1,1)),
            Func(snipstuff.infotext['message'].setText, ""),
          ).start()
        elif iv > 22:
          t+="\nOuch, it hurts!"
          Sequence(
            Func(avatar.setHpr, (0,0,0)),
            Func(avatar.setScale, (2,2,.5)),
            Wait(.3), Func(avatar.setScale, (1,1,1)),
            Func(avatarNP.setZ, avatarNP.getZ()+3),
            Wait(3), Func(snipstuff.infotext['message'].setText, ""),
          ).start()
        if t: snipstuff.infotext['message'].setText(t)
      task.remove()
    else: return task.cont
  tsk=taskMgr.add(smileyHitTheGround, "smiley_hit_g")

#** Here is where we tell the panda3D event managr to test when our sensor events occur. That snipstuff.DO is just to reuse the DirectObject defined in another module, don't worry about it. it's OK.
snipstuff.DO.accept('smileysensor-into', smileySensorIn)
# Note: in this snippet we don't need to do nothing when the smiley start to jump but, just in case, we always may use this line
#snipstuff.DO.accept('smileysensor-out', smileysensorout, ['out'])

splash.destroy()
run()
