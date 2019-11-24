# -*- coding: utf-8 -*-
"""
CollisionHandlerFloor and CollisionHandlerPusher - how to steer an avatar on uneven terrain and bashing against walls.

by fabius astelix @2010-01-26

Level: INTERMEDIATE

We'll see how to settle up a scene to have a movable avatar follow the Z-height of an uneven the terrain and blocked by walls or other obstacles. All of this is drove in concert by the panda3D's CollisionHandlerFloor and CollisionHandlerPusher collision handlers.

NOTE If you won't find here some line of code explained, probably you missed it in the previous steps - if you don't find there as well though, or still isn't clear for you, browse at http://www.panda3d.org/phpbb2/viewtopic.php?t=7918 and post your issue to the thread.
"""
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import CollisionHandlerFloor, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay, NodePath

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
snipstuff.info.append("Collisions With Floor and Walls in action")
snipstuff.info.append("a minimal sample to show how to keep an avatar grounded and blocked by invisible walls")
snipstuff.info.append("WASD=move the avatar around\nSPACE=avatar hiccup")
snipstuff.info_show()

#=========================================================================
# Main
"""
Starting from step1, we just put an additional collision handler to take care to keep the avatar grounded. This will PUSH the avatar back as soon as hit geometry we settled to be a wall: in blender we modelled polygons to wrap around the little house and all around the terrain area so that this time the avatar, differently from step1, won't pass through the house and won't be able to leave the terrain perimeter anymore. I suggest you to open the blender source to find out what I'm talking about here.
"""
#=========================================================================

#** Collision system ignition
base.cTrav=CollisionTraverser()
# did you saw this stuff in step1?
floorHandler = CollisionHandlerFloor()
floorHandler.setMaxVelocity(14)
# here it is the new fella - this will take care to push the avatar off the walls
wallHandler = CollisionHandlerPusher()

#** As you know this mask is used to mark the geometries for the floor collisions...
FLOOR_MASK=BitMask32.bit(1)
#... and this time we need another one to mark the walls as well.
WALL_MASK=BitMask32.bit(2)

#** This is our steering avatar - this time we use a little different setup, more close to real applications: we wrap either the avatar and its collision ray into another nodepath. This way we add lotta flexibility allowing us to make fancy things like you'll see below, to make the avatar rolling while steering, a thing not possible before and also to get rid of the global floorHandler.setOffset(1.0) shift, to set our avatar precisly placed above the surface.
avatarNP=NodePath('smileyNP')
avatarNP.reparentTo(base.render)
avatar = loader.loadModel('smiley')
avatar.reparentTo(avatarNP)
# since our avatar origin is centered in a model sized 2,2,2, we need to shift it 1 unit above the ground and this time we make this happen shifting it off its own root node (avatarNP)
avatar.setPos(0,0,1)
avatar.setCollideMask(BitMask32.allOff())
avatarNP.setPos(0,0,15)
# we reintroduced in this snippet the renowned smiley collision sphere - we need it as low-poly collision geometry for the wall collision handler to know when the smiley hit a wall.
avatarCollider = avatar.attachNewNode(CollisionNode('smileycnode'))
avatarCollider.node().addSolid(CollisionSphere(0, 0, 0, 1))
# of course we mark it with the wall mask
avatarCollider.node().setFromCollideMask(WALL_MASK)
avatarCollider.node().setIntoCollideMask(BitMask32.allOff())

#** Here we stick and set the ray collider to the avatar - note that we set it well above the avatar position because like this we are sure to always find a floor surface higher than the avatar top - try to change the third value i.e. to 0 and see what happen steering the avatar to get what I mean
raygeometry = CollisionRay(0, 0, 2, 0, 0, -1)
avatarRay = avatarNP.attachNewNode(CollisionNode('avatarRay'))
avatarRay.node().addSolid(raygeometry)
# this is how we tell the collision system that this ray would collide just with the floor acting as a FROM collider.
avatarRay.node().setFromCollideMask(FLOOR_MASK)
# we then exclude the ray from acting as an INTO collider
avatarRay.node().setIntoCollideMask(BitMask32.allOff())

#** This is the terrain map - the egg model loaded contains also the collider geometry for the terrain and for the walls as childs
terrain = loader.loadModel("scene1")
terrain.reparentTo(render)
terrain.setCollideMask(BitMask32.allOff())
terrain.setScale(10)
# here how we tell the collision system that the terrain collider geometry is allowed to collide with the avatar ray as INTO collider...
floorcollider=terrain.find("**/floor_collide")
floorcollider.node().setIntoCollideMask(FLOOR_MASK)
#...and the same goes for the walls
wallcollider=terrain.find("**/wall_collide")
wallcollider.node().setIntoCollideMask(WALL_MASK)

#** as said in step1 we tells to our collision handlers who take part to the respective tasks: for the floor the avatar ray and the avatar nodepath...
floorHandler.addCollider(avatarRay, avatarNP)
# ...and for the walls the avatar sphere collider together with - again - the avatar nodepath
wallHandler.addCollider(avatarCollider, avatarNP)

#** Now we're ready to start the collisions using the avatar ray to use to fire collisions for the floorHandler...
base.cTrav.addCollider(avatarRay, floorHandler)
# ... and the sphere for the wallHandler
base.cTrav.addCollider(avatarCollider, wallHandler)

#** just for fun this time I made the smiley avatar rolling on the the floor (laughing of course) - this function is called by the steering function defined somewhere else but never mind this cos is off the purposes of this snippet.
def avatarwalk(dt, vel):
  if vel[0]: avatar.setR(avatar.getR()+(40*vel[0]))
  if vel[1]: avatar.setP(avatar.getP()+(-38*vel[1]))

#** Activating avatar steering function - now we're ready to go
steering=snipstuff.avatar_steer(avatarNP, avatarwalk, fwspeed=12.)
steering.start()

splash.destroy()
run()
