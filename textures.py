from entity import ENTITY_TEXTURE_NAMES, ENTITY_SIZES
from constants import *
import pygame

BLOCK_TEXTURE_NAMES = [
    ["textures/void.png"],
    ["textures/air.png"],
    ["textures/grass_block_1.png", "textures/grass_block_2.png"],
    [
        "textures/dirt_1.png",
        "textures/dirt_2.png",
        "textures/dirt_3.png",
        "textures/dirt_4.png",
    ],
    [
        "textures/stone_1.png",
        "textures/stone_2.png",
        "textures/stone_3.png",
        "textures/stone_4.png",
    ],
    [
        "textures/planks_1.png",
        "textures/planks_2.png",
        "textures/planks_3.png",
        "textures/planks_4.png",
    ],
    [
        "textures/glass_1.png",
    ],
    [
        "textures/leaves_1.png",
        "textures/leaves_2.png",
        "textures/leaves_3.png",
        "textures/leaves_4.png",
    ],
    [
        "textures/wood_1.png",
        "textures/wood_2.png",
        "textures/wood_3.png",
        "textures/wood_4.png",
    ],
    [
        "textures/branches_1.png",
        "textures/branches_2.png",
        "textures/branches_3.png",
        "textures/branches_4.png",
    ],
    [
        "textures/cobblestone_1.png",
        "textures/cobblestone_2.png",
        "textures/cobblestone_3.png",
        "textures/cobblestone_4.png",
    ],
    [
        "textures/rock_1.png",
    ],
]
BLOCK_TEXTURE_NAMES_LENS = [len(list_of_names) for list_of_names in BLOCK_TEXTURE_NAMES]

BLOCK_EDIT_NAME = "textures/edit_block.png"
BLOCK_PLACE_NAME = "textures/place_block.png"
HOTBAR_NAME = "textures/hotbar.png"
HOTBAR_COVER_NAME = "textures/hotbar_cover.png"
BACKGROUND_COLOR = (0, 200, 255)


def load_texture(texture, size):
    return pygame.transform.scale(pygame.image.load(texture).convert_alpha(), size)


class Textures:
    def __init__(self):
        self.block_textures = [
            [
                load_texture(texture_name, (BLOCK_SIZE, BLOCK_SIZE))
                for texture_name in list_of_names
            ]
            for list_of_names in BLOCK_TEXTURE_NAMES
        ]
        self.big_block_textures = [
            [
                load_texture(texture_name, (BLOCK_SIZE * 4, BLOCK_SIZE * 4))
                for texture_name in list_of_names
            ]
            for list_of_names in BLOCK_TEXTURE_NAMES
        ]
        self.empty_chunk_surface = pygame.Surface(
            (CHUNK_TOTAL_SIZE, CHUNK_TOTAL_SIZE)
        ).convert_alpha()
        self.background_block_surface = pygame.Surface(
            (BLOCK_SIZE, BLOCK_SIZE)
        ).convert_alpha()
        self.entity_textures = [
            load_texture(texture_name, ENTITY_SIZES[i])
            for i, texture_name in enumerate(ENTITY_TEXTURE_NAMES)
        ]
        self.edit_block = load_texture(BLOCK_EDIT_NAME, (BLOCK_SIZE, BLOCK_SIZE))
        self.place_block = load_texture(BLOCK_PLACE_NAME, (BLOCK_SIZE, BLOCK_SIZE))

        self.empty_chunk_surface.fill(BACKGROUND_COLOR)
        self.background_block_surface.fill(BACKGROUND_COLOR)

        self.hotbar = pygame.image.load(HOTBAR_NAME).convert_alpha()
        self.hotbar_cover = pygame.image.load(HOTBAR_COVER_NAME).convert_alpha()

    def get_block_texture(self, block_type, pos=pygame.Vector2(0)):
        x_odd = int(not (pos.x % 2 == 0))
        y_odd = int(not (pos.y % 2 == 0)) * 2
        if BLOCK_TEXTURE_NAMES_LENS[block_type] == 1:
            return self.block_textures[block_type][0]
        elif BLOCK_TEXTURE_NAMES_LENS[block_type] == 2:
            return self.block_textures[block_type][0 + x_odd]
        elif BLOCK_TEXTURE_NAMES_LENS[block_type] == 4:
            return self.block_textures[block_type][0 + x_odd + y_odd]

    def get_big_block_texture(self, block_type, pos=pygame.Vector2(0)):
        x_odd = int(not (pos.x % 2 == 0))
        y_odd = int(not (pos.y % 2 == 0)) * 2
        if BLOCK_TEXTURE_NAMES_LENS[block_type] == 1:
            return self.big_block_textures[block_type][0]
        elif BLOCK_TEXTURE_NAMES_LENS[block_type] == 2:
            return self.big_block_textures[block_type][0 + x_odd]
        elif BLOCK_TEXTURE_NAMES_LENS[block_type] == 4:
            return self.big_block_textures[block_type][0 + x_odd + y_odd]
