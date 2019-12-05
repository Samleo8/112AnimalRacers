# CMU 15-112 Term Project: Animal Racers

Creation of a 3D racing game for my CMU 15-112 Term Project!

Collect the powerups, and beat all the other cars to win! 

Trailer Video: https://youtu.be/lcON0dgbxwg

## Running and Installation
First clone the git repository: `git clone git@github.com:Samleo8/112AnimalRacers.git`

Then install all requirements by running the command `pip install -r requirements.txt`. The crucial library used for this game is the [Panda3D Engine](https://www.panda3d.org).

Then, from **within the main/root repository folder**, run the game with `python Game.py`. Note that only Python 3 is supported.

## Game instructions
Powerups:
 - Shield: You don't slow down when you hit the walls.
 - Speed: Speed boost!

[WASD/Arrow Keys] Drive
[Hold Space] Drift

[1, 2] Change camera view
[Hold C] Look behind
[Hold V] Look around

[P] Pause and show help
[R] Restart Game

### Special (Debugging) Commands
 - [=] Activates "god mode": 
    Changes the camera view to mouse-controlled. 
    Left-click and drag to move; alt-drag to rotate; ctrl-drag to zoom
 - [Backspace] Pause the game without showing the help screen. 
    This allows for debugging when you want to pause the game and use "god mode" to see items on the screen
 - [\ (Backslash)] Toggle the printing of debugging statements
 - [Space] In the start screens, press space to skip to the next screen (this is hinted in the GUI)

## Credits

### 3D Models
[Jeep Model](https://free3d.com/3d-model/1987-camel-trophy-range-rover-x3d-25052.html) by *bigcrazycarboy*

[Lightning Bolt](https://opengameart.org/content/bolt) by *Savino*

All other models from the [Alice Gallery](http://alice.org/pandagallery/index.html)

### Audio
Main music adapted from [Purple Passion](https://www.youtube.com/watch?v=ERbmI4_x1Xc) by *Diana Boncheva*

### Fonts
[American Captain](https://www.fontspace.com/the-fontry/american-captain) by *The Fontry*

### Code Reference

#### General
[Panda 3D Manual](https://www.panda3d.org/manual/)

[Panda 3D API Reference](https://www.panda3d.org/reference/python/index.html)

### Specific (adapted code)
[TabbedFrame for instructions screen](https://github.com/ArsThaumaturgis/TabbedFrame)

[Camera control for 3D racetrack selection](https://discourse.panda3d.org/t/another-camera-controller-orbit-style/11545/2)

## Project Details
Elaborated in document [here](ProjectProposal.md).
