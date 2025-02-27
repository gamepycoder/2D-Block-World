2d block world:
===============

Inspired by minecraft, terraria, lay of the land, vintage story and mine blocks.

Blocks are 1/4 of a meter and the player is 8 blocks tall.

You can:
--------

Place blocks and change what block you place.

Mine/delete blocks.

Fly or walk/run/sneak.

Explore caves.

Defult keys:
------------

NUMBER_KEYS = [K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0]

JUMP = K_w

LEFT = K_a

RIGHT = K_d

FAST = K_LSHIFT

SLOW = K_s

PAUSE = K_p

CAM_LEFT = K_LEFT

CAM_RIGHT = K_RIGHT

CAM_UP = K_UP

CAM_DOWN = K_DOWN

CAMERA_TOGGLE = K_c

TELEPORT = K_t

CLONE = K_i

SAVE = K_k

FLY = K_SPACE

EXIT = K_ESCAPE

Code description:
=================

inputs.py:
----------

Defines key to variable mapping and a function to detect them.

ui.py:
----------

Defines UI elements.

Image, Text, Button, and Slider

textures.py:
------------

Defines a class for loading and storing textures.

constants.py:
-------------

Defines constants that multiple files need to know.

entity.py:
----------

Defines a base entity class that has physics and a player class for the player type of entity.

world.py:
---------

Defines the chunk and entity handling and world generation with the World and Chunk_loader classes. The world of this project is infinite and the chunks are loaded slowly to allow for a better playing performance.

game.py:
--------

Defines a game class that runs and renders the game.

create_game.py:
---------------

Defines a class for the main menu. 

When ran, runs the main menu then exits or runs the game class depending on main menu finished state.

TODO:
=====

 - Improve performance
 - Add structures to world gen
 - Add inventory and proper mining
 - Add more entitys

