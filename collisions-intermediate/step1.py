# -*- coding: utf-8 -*-
"""
CollisionHandlerFloor - how to steer an avatar on a uneven terrain keeping it grounded.

by fabius astelix @2010-01-25

Level: INTERMEDIATE

We'll see how to settle up a scene to have a movable avatar following the Z-height of an uneven the terrain. All of this is drived by the panda3D CollisionHandlerFloor collision handler.

NOTE If you won't find here some line of code explained, probably you missed it in the previous steps - if you don't find there as well though, or still isn't clear for you, browse at http://www.panda3d.org/phpbb2/viewtopic.php?t=7918 and post your issue to the thread.
"""
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import CollisionHandlerFloor, CollisionNode, CollisionTraverser, BitMask32, CollisionRay

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

base.cam.setPos(40, -70, 20)

splash=snipstuff.splashCard()
snipstuff.info.append("CollisionFloor in action")
snipstuff.info.append("a minimal sample to show how to keep an avatar grounded into an uneven terrain")
snipstuff.info.append("WASD=move the avatar around\nSPACE=avatar hiccup")
snipstuff.info_show()

#=========================================================================
# Main
"""
What we'll going to do is to load a model and stick a ray collider to it, to interact with the CollisionHandlerFloor and keep the model right over the uneven floor. The terrain is modelled in blender in a way to have 2 geometries: 1 for the terrain we see and one low poly copy that will act as a collider, precisely as we have seen in previous steps.
"""
#=========================================================================

#** Collision system ignition
base.cTrav=CollisionTraverser()
 # This time we use a special collision handler: the CollisionHandlerFloor object that will keep a steering avatar grounded against the terrain floor geometry, that is not quite flat but very uneven.
floorHandler = CollisionHandlerFloor()
# this parameter sets how fast the avatar will fall when floating above the terrain. Actually is settled to mimic the Earth gravity but naturally is not mathematically perfect - if i.e. you prefer the moon gravity, try to lower that value to 3.
floorHandler.setMaxVelocity(14)

#** This mask will be used later to mark the geometries for the floor collisions. Since we got just one INTO collision mesh (the floor collider - see below) there was no need of it but in a real application with different kind of collision geometries that would be essential. You'll got this better in the following step2.py using walls pushers
FLOOR_MASK=BitMask32.bit(1)

#** This is our steering avatar - note that we exclude it off the collision system and that we do not provide a collision solid
avatar = loader.loadModel('smiley')
avatar.reparentTo(base.render)
avatar.setCollideMask(BitMask32.allOff())
# We set the avatar initial position well above the terrain geometry, so will be dropped from middle air - you'll then see it falling down there and as soon as it will reach the floor geometry, you'll see it stop falling down. All of this is driven by the CollisionHandlerFloor handler.
avatar.setPos(0,0,15)

#** Here we stick and set the ray collider to the avatar - the first 3 parameters are the ray origin position were is stuck starting off the avatar origin and the last 3 the hpr direction toward it will shoots.
raygeometry = CollisionRay(0, 0, 0, 0, 0, -1)
avatarRay = avatar.attachNewNode(CollisionNode('avatarRay'))
avatarRay.node().addSolid(raygeometry)
# this is how we tell the collision system that this ray would collide just with the floor acting as a FROM collider.
avatarRay.node().setFromCollideMask(FLOOR_MASK)
# we then exclude the ray from acting as an INTO collider
avatarRay.node().setIntoCollideMask(BitMask32.allOff())

#** This is the terrain - the egg model we load contains also the collider geometry as child
terrain = loader.loadModel("scene1")
terrain.reparentTo(render)
terrain.setCollideMask(BitMask32.allOff())
terrain.setScale(10)
# here how we tell the collision system that the terrain collider geometry is allowed to collide with the avatar ray as INTO collider
floorcollider=terrain.find("**/floor_collide")
floorcollider.node().setIntoCollideMask(FLOOR_MASK)

#** We set here the collison handler to use our avatar ray as into collider to detect the contact point along the Z axis and also which is the avatar nodepath to take control - this means to say that while we steer horizontally our avatar, changing its X and Y position from here to there, the handler will take care to set its Z position automatically, eventually simulating when falling down if we drop the avatar in middle air.
floorHandler.addCollider(avatarRay, avatar)
# the following setup will shift the floor contact hit position detection a little up. This is cause the CollisionHandlerFloor uses the avatar origin as reference to drive it and don't care to detect when it touch the floor surface with its  outer geometry. It's up to you to settle things to keep the avatar staying up the floor relative to the avatar's origin. Note though that this is not the recommended way to proceed in real applications, cause if we got different models with different shapes and origins roaming around, we'd see them not touching the floor correctly but or half-submerged into the terrain or not toching it at all, looking floating into the air. The correct way to go will be to interpose another nodepath to the avatar, shifting off this one instead. We'll see this better in step2.py snippet.
floorHandler.setOffset(1.0)

#** Now we're ready to start the collisions using the floorHandler and the ray to fire collisions
base.cTrav.addCollider(avatarRay, floorHandler)

#** Activating avatar steering function - now we're ready to go
steering=snipstuff.avatar_steer(avatar)
steering.start()

splash.destroy()
run()
