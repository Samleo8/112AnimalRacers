# Lego Racers: Remake++
An attempt to remake my childhood favourite Lego Racers, with added features, including intelligent enemies, powerups and obstacles.

## Competitive Analysis
The first racing game to analyse will of course be **Lego Racers** itself. This will naturally be a hard game to beat in terms of playability, mechanics and features. However, this remake++ version will not only incorporate the good features of Lego Racers, but also add on some features:
 
Similarities | Differences
--- | ---
Powerups | Intelligent enemies and obstacles
\- | Different camera views
Tracks, racecar & character selection | Will not be able to customise fully
*Customisable racecars (KIV)* | 
*Enemy cars (KIV)* | Single player mode
Supports Windows | Coded in Python, so **multiplatform**!
 | 


When we compare against other racing games, the key difference we see is that first of all, it is in full 3D (not 2.5D). Moreover, it includes obstacles and roaming enemies - a feature not common in many racing games. If time permits, there will also be bonus features of customisable racecars, characters and tracks.

## Structural Plan
```
|-- Lego Racers Remake
    |-- Obj3D.py
        Object 3D Class: Super class for all more complicated 3D objects (virtually everything tbh)
        Handles models and textures, calculations of dimensions, offset from center, positioning, collision box drawing etc.
    |
    |-- Racecar.py
        Racecar Class: Subclass of Obj3D.
        Handles racecar with calculations/functions for positioning, rotations, speeds and acceleration. Also handles friction and collision with Racetrack/walls and floors. 
        Handles the passenger too. Purposely made to be scalable for future customisability 
    |
    |-- Racetrack.py (TODO)
        Racetrack Class: Subclass of Obj3D.
        Handles racetrack by housing collision solids, and is made through generation of bricks/walls and a floor
    |
    |-- Enemy.py (TODO)
        Enemy Class: Subclass of Obj3D. Contains subclasses of enemy types. Note that enemies here are more like obstacles and are different from enemy cars.
        Handles enemy movement, collision detection, AI etc.
    |
    |-- Powerups.py (TODO)
        Powerup Class: Subclass of Obj3D. Contains subclasses of powerup types
        Handles positioning, collision detection etc.
    |
    |-- Game.py
        Main game file that runs the game. Handles timers, collisions, camera, keyboard events, GUI, audio etc
    |
    |-- audio
    |   |-- backgroundMusic.mp3
    |   |-- collisionSFX.mp3
    |   |-- engineSFX.mp3
    |   |-- menuSFX.mp3
    |   
    |-- models
        |-- crate.egg
                Brick for racetrack
        |
        |-- forest.egg
                Backgrounds
        |
        |-- groundroamer.egg
        |-- racecar.egg
                Racecars
        |
        |-- penguin.egg
        |-- person.egg
                Passengers
        |
        |-- tex
            |-- personTexture.png
```

The full file structure of the project can be see in the Git repository.

Project structure with sub-projects can be seen under [Github Projects](https://github.com/Samleo8/112LegoRacers/projects), and is dynamically updated.

## Algorithmic Plan
A detailed algorithmic plan for how you will approach the trickiest part of the project.

## Timeline Plan
A timeline for when you intend to complete the major features of the project.

## Version Control Plan
This [Github repository](https://github.com/Samleo8/112LegoRacers) controls both the code versions, as well as the structure and timeline of the project *(see [Projects](https://github.com/Samleo8/112LegoRacers/projects) and [Issues](https://github.com/Samleo8/112LegoRacers/issues))*. 

Commits automatically reference and close their associated issues.

## Modules Used
[Panda3D Engine](https://www.panda3d.org)

Checkout `requirements.txt` to see the external Python libraries used in the repository.